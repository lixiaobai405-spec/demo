"""
BMC（三维）评分相关 API。

注意：该路由是为前端的 BMC 突破要素评分能力提供支撑，路径与前端约定为：
- GET  /api/assessments/{assessment_id}/bmc-scoring
- POST /api/assessments/{assessment_id}/bmc-scoring/calculate
- POST /api/assessments/{assessment_id}/bmc-scoring/save
- POST /api/assessments/{assessment_id}/bmc-scoring/auto-derive
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.assessment import Assessment
from app.models.bmc_scoring import BMCScoring
from app.schemas.bmc_scoring import (
    AutoDeriveResponse,
    BmcScoringResponse,
    BmcScoringResult,
    BmcScoringSaveRequest,
    ModuleScoreInput,
    ModuleScoringResult,
)

router = APIRouter(prefix="/api/assessments/{assessment_id}/bmc-scoring", tags=["bmc-scoring"])

# 与前端 BMC_MODULES 保持一致（用于渲染标题/缩写/分类）
_BMC_META: dict[str, dict[str, str]] = {
    "customer_segments": {"title": "客户细分", "abbr": "CS", "category": "market"},
    "value_propositions": {"title": "价值主张", "abbr": "VP", "category": "market"},
    "channels": {"title": "渠道通路", "abbr": "CH", "category": "market"},
    "customer_relationships": {"title": "客户关系", "abbr": "CR", "category": "market"},
    "revenue_streams": {"title": "收入来源", "abbr": "R$", "category": "market"},
    "key_resources": {"title": "核心资源", "abbr": "KR", "category": "efficiency"},
    "key_activities": {"title": "关键业务", "abbr": "KA", "category": "efficiency"},
    "key_partnerships": {"title": "重要合作", "abbr": "KP", "category": "efficiency"},
    "cost_structure": {"title": "成本结构", "abbr": "C$", "category": "efficiency"},
}


def _iso(dt: datetime | None) -> str | None:
    """将 datetime 安全序列化为 ISO 字符串。"""

    return dt.isoformat() if dt else None


def _compute_zone(pain: int, feasibility: int) -> tuple[str, str, str, str, str | None]:
    """
    根据痛点与可行性给出一个“可解释”的分区与推荐标签。

    返回：
    - zone: quickwin/strategic/longterm/hold/blocked
    - level: 用于前端展示的推荐等级（中文）
    - label: 推荐标签（中文）
    - stars: 星级字符串（如 ★★★）
    - veto_reason: 若阻塞则给出原因
    """

    if feasibility <= 1:
        return ("blocked", "阻塞", "暂不推进", "★", "可行性过低，建议先补齐资源/流程/数据")
    if pain >= 4 and feasibility >= 4:
        return ("quickwin", "立即启动", "高痛点高可行", "★★★", None)
    if pain >= 4 and feasibility >= 2:
        return ("strategic", "规划推进", "高痛点需规划", "★★☆", None)
    if pain >= 3:
        return ("longterm", "长期储备", "中痛点待时机", "★★", None)
    return ("hold", "观察", "优先级较低", "★☆", None)


def _normalize_score(raw_score: float) -> float:
    """将原始分（0-15）归一到 0-10，便于统一展示。"""

    return round((raw_score / 15.0) * 10.0, 2)


def _calculate_result(assessment_id: str, modules: list[ModuleScoreInput]) -> BmcScoringResult:
    """
    计算 BMC 三维评分结果（轻量算法，确保 Demo 可用）。

    规则（可后续迭代成更严谨的算法/知识库推导）：
    - raw_score = pain + data + feasibility（范围 0-15）
    - normalized_score = raw_score 映射到 0-10
    - zone 与推荐文案：由 (pain, feasibility) 组合决定（数据维度用于加权，但不进入分区）
    - Top3：按 normalized_score 倒序取 3 个
    - 互补性提示：若 Top3 全部来自同一 category，则给出提醒
    """

    results: list[ModuleScoringResult] = []
    for m in modules:
        meta = _BMC_META.get(m.key)
        if not meta:
            # 未知 key 仍可返回，但以 key 自身兜底，避免前端崩溃
            meta = {"title": m.key, "abbr": m.key[:2].upper(), "category": "unknown"}

        raw_score = float(m.pain + m.data + m.feasibility)
        normalized = _normalize_score(raw_score)
        zone, level, label, stars, veto_reason = _compute_zone(m.pain, m.feasibility)
        veto_status = "veto" if zone == "blocked" else "ok"

        results.append(
            ModuleScoringResult(
                key=m.key,
                title=meta["title"],
                abbr=meta["abbr"],
                category=meta["category"],
                pain=m.pain,
                data=m.data,
                feasibility=m.feasibility,
                raw_score=raw_score,
                normalized_score=normalized,
                zone=zone,  # type: ignore[arg-type]
                veto_status=veto_status,
                veto_reason=veto_reason,
                recommendation_level=level,
                recommendation_label=label,
                recommendation_stars=stars,
            )
        )

    sorted_results = sorted(results, key=lambda r: r.normalized_score, reverse=True)
    top3 = sorted_results[:3]
    top3_keys = [x.key for x in top3]

    # 互补性提醒：Top3 全部同类则提醒（market/efficiency）
    categories = {x.category for x in top3 if x.category}
    complementarity_warning = None
    if len(top3) == 3 and len(categories) == 1 and list(categories)[0] in {"market", "efficiency"}:
        complementarity_warning = "Top3 模块集中在同一类别，建议补充另一类要素以增强方案互补性。"

    return BmcScoringResult(
        assessment_id=assessment_id,
        module_results=results,
        top_3_keys=top3_keys,
        top_3_results=top3,
        complementarity_warning=complementarity_warning,
    )


def _ensure_assessment(db: Session, assessment_id: str) -> Assessment:
    """确保 assessment 存在，否则返回 404。"""

    stmt = select(Assessment).where(Assessment.id == assessment_id)
    obj = db.execute(stmt).scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="assessment not found")
    return obj


def _get_or_create_record(db: Session, assessment_id: str) -> BMCScoring:
    """获取或创建 BMCScoring 记录（assessment_id 唯一）。"""

    stmt = select(BMCScoring).where(BMCScoring.assessment_id == assessment_id)
    record = db.execute(stmt).scalar_one_or_none()
    if record:
        return record
    record = BMCScoring(assessment_id=assessment_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=BmcScoringResponse)
def get_bmc_scoring(assessment_id: str, db: Session = Depends(get_db)) -> BmcScoringResponse:
    """查询指定评估的 BMC 评分（若不存在返回空结构）。"""

    _ensure_assessment(db, assessment_id)
    stmt = select(BMCScoring).where(BMCScoring.assessment_id == assessment_id)
    record = db.execute(stmt).scalar_one_or_none()
    if not record:
        return BmcScoringResponse(
            assessment_id=assessment_id,
            scoring_result=None,
            selected_keys=[],
            created_at=None,
            updated_at=None,
        )

    scoring_result = json.loads(record.scoring_result_json) if record.scoring_result_json else None
    return BmcScoringResponse(
        assessment_id=assessment_id,
        scoring_result=BmcScoringResult.model_validate(scoring_result) if scoring_result else None,
        selected_keys=json.loads(record.selected_keys_json or "[]"),
        created_at=_iso(record.created_at),
        updated_at=_iso(record.updated_at),
    )


@router.post("/calculate", response_model=BmcScoringResult)
def calculate_bmc_scoring(
    assessment_id: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
) -> BmcScoringResult:
    """计算 BMC 三维评分（不落库，仅返回结果）。"""

    _ensure_assessment(db, assessment_id)
    modules_raw = payload.get("modules") or []
    modules = [ModuleScoreInput.model_validate(x) for x in modules_raw]
    if not modules:
        raise HTTPException(status_code=400, detail="modules is required")
    return _calculate_result(assessment_id, modules)


@router.post("/save", response_model=BmcScoringResponse)
def save_bmc_scoring(
    assessment_id: str,
    payload: BmcScoringSaveRequest,
    db: Session = Depends(get_db),
) -> BmcScoringResponse:
    """保存 BMC 评分选择结果（落库）。"""

    _ensure_assessment(db, assessment_id)
    record = _get_or_create_record(db, assessment_id)

    # 允许前端只传 selected_keys（manual），但推荐同时传 all_module_scores 以便审计/回放
    scoring_result = None
    if payload.all_module_scores:
        scoring_result = _calculate_result(assessment_id, payload.all_module_scores)

    record.selection_mode = payload.selection_mode
    record.selected_keys_json = json.dumps(payload.selected_keys, ensure_ascii=False)
    record.all_module_scores_json = json.dumps(
        [x.model_dump() for x in payload.all_module_scores],
        ensure_ascii=False,
    )
    record.scoring_result_json = json.dumps(
        scoring_result.model_dump() if scoring_result else None,
        ensure_ascii=False,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return BmcScoringResponse(
        assessment_id=assessment_id,
        scoring_result=scoring_result,
        selected_keys=payload.selected_keys,
        created_at=_iso(record.created_at),
        updated_at=_iso(record.updated_at),
    )


@router.post("/auto-derive", response_model=AutoDeriveResponse)
def auto_derive_bmc_scoring(assessment_id: str, db: Session = Depends(get_db)) -> AutoDeriveResponse:
    """
    从商业画布自动推导 BMC 分值（Demo 兜底实现）。

    说明：
    - 真实推导可基于 CanvasDiagnosis / Assessment.profile_payload 等字段做规则/LLM 推断
    - 当前先返回“中性默认值”，保证前端流程可跑通
    """

    _ensure_assessment(db, assessment_id)

    modules = [
        ModuleScoreInput(key=k, pain=3, data=3, feasibility=3) for k in _BMC_META.keys()
    ]
    return AutoDeriveResponse(modules=modules, derived_from_canvas=False)

