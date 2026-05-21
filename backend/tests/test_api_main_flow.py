from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db import session as db_session
from app.main import create_app
from app.services.llm_client import LLMClient
from app.services.llm_enhancer import LLMEnhancer
from app.services.llm_report_writer import LLMReportWriter


TEST_DB_PATH = Path(__file__).resolve().parent / "test_main_flow.db"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    engine = create_engine(
        f"sqlite:///{TEST_DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", testing_session_local)
    monkeypatch.setattr(LLMClient, "_use_mock_mode", lambda self: True)
    monkeypatch.setattr(LLMEnhancer, "_is_live_mode", lambda self: False)

    db_session.Base.metadata.create_all(bind=engine)
    db_session._migrate_generated_reports_table()

    app = create_app()
    with TestClient(app) as test_client:
        register_response = test_client.post(
            "/api/auth/register",
            json={
                "email": "mainflow@test.com",
                "password": "test123456",
                "display_name": "主流程测试用户",
                "company_name": "主流程测试企业",
                "job_title": "产品负责人",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture()
def assessment_payload() -> dict[str, str]:
    return {
        "company_name": "测试连锁零售企业",
        "industry": "零售",
        "company_size": "100-499人",
        "region": "华东",
        "annual_revenue_range": "5000万-1亿元",
        "core_products": "社区零售门店、会员运营与到家服务",
        "target_customers": "社区家庭用户、周边白领与会员客户",
        "current_challenges": "门店运营效率波动，会员复购不稳定，知识传递依赖店长经验",
        "ai_goals": "提升门店运营效率，增强会员复购，沉淀可复制的门店运营知识",
        "available_data": "POS、会员系统、商品主数据、巡店记录、客服反馈",
        "notes": "计划先从单区域试点推进",
    }


def _create_assessment(client: TestClient, payload: dict[str, str]) -> str:
    response = client.post("/api/assessments", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["company_name"] == payload["company_name"]
    return body["id"]


def _select_recommended_breakthroughs(client: TestClient, assessment_id: str) -> list[str]:
    breakthrough_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    assert breakthrough_response.status_code == 200
    recommended_keys = breakthrough_response.json()["breakthrough_recommendation"][
        "recommended_keys"
    ]
    select_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/select",
        json={
            "selected_keys": recommended_keys[:2],
            "selection_mode": "system_recommended",
        },
    )
    assert select_response.status_code == 200
    return recommended_keys


def _expand_and_select_directions(
    client: TestClient,
    assessment_id: str,
) -> list[str]:
    expand_response = client.post(f"/api/assessments/{assessment_id}/directions/expand")
    assert expand_response.status_code == 200
    expanded = expand_response.json()["direction_expansion"]["elements"]
    selected_direction_ids = [
        expanded[0]["suggestions"][0]["direction_id"],
        expanded[1]["suggestions"][0]["direction_id"],
    ]
    select_response = client.post(
        f"/api/assessments/{assessment_id}/directions/select",
        json={"selected_direction_ids": selected_direction_ids},
    )
    assert select_response.status_code == 200
    return selected_direction_ids


def _prepare_for_scenarios(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> str:
    assessment_id = _create_assessment(client, assessment_payload)
    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200
    _select_recommended_breakthroughs(client, assessment_id)
    _expand_and_select_directions(client, assessment_id)
    return assessment_id


def _prepare_for_report(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> str:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)
    assert client.post(f"/api/assessments/{assessment_id}/scenarios").status_code == 200
    assert (
        client.post(f"/api/assessments/{assessment_id}/competitiveness/generate").status_code
        == 200
    )
    assert client.post(f"/api/assessments/{assessment_id}/endgame/generate").status_code == 200
    return assessment_id


def _live_llm_report_test_enabled() -> bool:
    return (
        os.getenv("RUN_LIVE_LLM_TESTS", "").strip().lower() == "true"
        and os.getenv("LLM_REPORT_ENABLED", "").strip().lower() == "true"
        and bool(os.getenv("OPENAI_API_KEY", "").strip())
        and bool(os.getenv("OPENAI_MODEL", "").strip())
    )


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_report_requires_prerequisites(client: TestClient, assessment_payload: dict[str, str]) -> None:
    assessment_id = _create_assessment(client, assessment_payload)

    context_response = client.get(f"/api/assessments/{assessment_id}/report-context")
    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=template")

    assert context_response.status_code == 400
    assert "company profile" in context_response.json()["detail"]
    assert report_response.status_code == 400
    assert "company profile" in report_response.json()["detail"]


def test_main_flow_template_report_and_exports(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)

    profile_response = client.post(f"/api/assessments/{assessment_id}/profile")
    assert profile_response.status_code == 200
    assert profile_response.json()["generation_mode"] in ("mock", "live")

    canvas_response = client.post(f"/api/assessments/{assessment_id}/canvas")
    assert canvas_response.status_code == 200
    canvas_body = canvas_response.json()["canvas_diagnosis"]
    assert canvas_body["generation_mode"] in ("mock", "live")
    assert len(canvas_body["canvas"]["blocks"]) == 9

    breakthrough_recommend_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    assert breakthrough_recommend_response.status_code == 200
    breakthrough_recommend_body = breakthrough_recommend_response.json()
    assert breakthrough_recommend_body["assessment_id"] == assessment_id
    assert breakthrough_recommend_body["breakthrough_recommendation"]["generation_mode"] == "rule_based"
    assert len(breakthrough_recommend_body["breakthrough_recommendation"]["elements"]) == 9
    assert len(breakthrough_recommend_body["breakthrough_recommendation"]["recommended_keys"]) == 3

    recommended_keys = breakthrough_recommend_body["breakthrough_recommendation"]["recommended_keys"]
    breakthrough_select_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/select",
        json={
            "selected_keys": recommended_keys[:2],
            "selection_mode": "system_recommended",
        },
    )
    assert breakthrough_select_response.status_code == 200
    breakthrough_select_body = breakthrough_select_response.json()
    assert breakthrough_select_body["selection_mode"] == "system_recommended"
    assert len(breakthrough_select_body["selected_elements"]) == 2

    direction_ids = _expand_and_select_directions(client, assessment_id)
    assert len(direction_ids) == 2

    scenarios_response = client.post(f"/api/assessments/{assessment_id}/scenarios")
    assert scenarios_response.status_code == 200
    scenarios_body = scenarios_response.json()["scenario_recommendation"]
    assert scenarios_body["scoring_method"] == "four_quadrant_v1"
    assert len(scenarios_body["top_scenarios"]) >= 1
    # 验证每个 Top 场景都带有四象限评分字段
    for s in scenarios_body["top_scenarios"]:
        assert "priority_structuredness_x" in s
        assert "priority_complexity_y" in s
        assert "priority_qs" in s
        assert "priority_lps" in s
        assert "priority_lps_display" in s
        assert "priority_quadrant" in s
        assert s["priority_quadrant"] in ("自动化主战场", "AI优先区", "人机协作区", "人类保留区")
        assert "priority_tier" in s
        assert "priority_recommendation" in s

    cases_response = client.post(f"/api/assessments/{assessment_id}/cases")
    assert cases_response.status_code == 200
    cases_body = cases_response.json()["case_recommendation"]
    assert cases_body["scoring_method"] == "layered_v1"
    assert len(cases_body["top_cases"]) >= 1

    competitiveness_response = client.post(
        f"/api/assessments/{assessment_id}/competitiveness/generate"
    )
    assert competitiveness_response.status_code == 200

    endgame_response = client.post(f"/api/assessments/{assessment_id}/endgame/generate")
    assert endgame_response.status_code == 200

    context_response = client.get(f"/api/assessments/{assessment_id}/report-context")
    assert context_response.status_code == 200
    context_body = context_response.json()
    assert context_body["assessment_id"] == assessment_id
    assert len(context_body["top_scenarios"]) >= 1
    assert len(context_body["report_outline"]) == 13
    assert len(context_body["selected_breakthrough_elements"]) == 2

    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=template")
    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["assessment_id"] == assessment_id
    assert report_body["generation_mode"] == "template"
    assert report_body["used_llm"] is False
    assert report_body["content_json"]["generated_with"] == "template"
    assert len(report_body["sections"]) == 13

    detail_response = client.get(f"/api/assessments/{assessment_id}")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["progress"]["has_profile"] is True
    assert detail_body["progress"]["has_canvas"] is True
    assert detail_body["progress"]["has_breakthrough"] is True
    assert detail_body["progress"]["has_directions"] is True
    assert detail_body["progress"]["has_competitiveness"] is True
    assert detail_body["progress"]["has_endgame"] is True
    assert detail_body["progress"]["has_scenarios"] is True
    assert detail_body["progress"]["has_report"] is True
    assert detail_body["progress"]["ready_for_report"] is True
    assert detail_body["progress"].get("has_cases") is True
    assert detail_body["generated_report"]["report_id"] == report_body["report_id"]

    report_id = report_body["report_id"]

    markdown_response = client.get(f"/api/reports/{report_id}/export/markdown")
    assert markdown_response.status_code == 200
    assert "text/markdown" in markdown_response.headers["content-type"]
    assert "used_llm: false" in markdown_response.text

    docx_response = client.get(f"/api/reports/{report_id}/export/docx")
    assert docx_response.status_code == 200
    assert (
        docx_response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(docx_response.content) > 0

    print_response = client.get(f"/api/reports/{report_id}/print")
    assert print_response.status_code == 200
    assert "text/html" in print_response.headers["content-type"]
    assert "used_llm: false" in print_response.text

    report_detail_response = client.get(f"/api/reports/{report_id}")
    assert report_detail_response.status_code == 200
    assert report_detail_response.json()["report_id"] == report_id


def test_llm_mode_falls_back_to_template_when_llm_call_fails(
    client: TestClient,
    assessment_payload: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assessment_id = _prepare_for_report(client, assessment_payload)

    def _force_llm_mode(self, requested_mode: str) -> tuple[str, list[str]]:
        return "llm", []

    def _raise_llm_error(*args, **kwargs):
        raise RuntimeError("forced llm failure")

    monkeypatch.setattr(LLMReportWriter, "_resolve_mode", _force_llm_mode)
    monkeypatch.setattr(LLMReportWriter, "_call_llm", _raise_llm_error)

    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=llm")

    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["generation_mode"] == "template"
    assert report_body["used_llm"] is False
    assert report_body["content_json"]["generated_with"] == "template"
    assert any("template mode" in warning for warning in report_body["warnings"])
    assert any("RuntimeError" in warning for warning in report_body["warnings"])


def test_report_generation_auto_matches_cases_when_missing(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _prepare_for_report(client, assessment_payload)

    detail_before_report = client.get(f"/api/assessments/{assessment_id}")
    assert detail_before_report.status_code == 200
    assert detail_before_report.json()["progress"].get("has_cases") is False

    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=template")

    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["generation_mode"] == "template"
    assert report_body["used_llm"] is False

    detail_after_report = client.get(f"/api/assessments/{assessment_id}")
    assert detail_after_report.status_code == 200
    detail_body = detail_after_report.json()
    assert detail_body["progress"].get("has_cases") is True
    assert detail_body["case_recommendation"]["scoring_method"] == "layered_v1"
    assert len(detail_body["case_recommendation"]["top_cases"]) >= 1


def test_assessment_detail_serializes_direction_selection(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200

    _select_recommended_breakthroughs(client, assessment_id)
    selected_direction_ids = _expand_and_select_directions(client, assessment_id)

    select_response = client.get(f"/api/assessments/{assessment_id}/directions")
    assert select_response.status_code == 200

    detail_response = client.get(f"/api/assessments/{assessment_id}")

    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["direction_selection"] is not None
    assert {
        item["direction_id"]
        for item in detail_body["direction_selection"]["selected_directions"]
    } == set(selected_direction_ids)


def test_direction_selection_accepts_llm_enhanced_direction_ids(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200

    breakthrough_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    recommended_keys = breakthrough_response.json()["breakthrough_recommendation"][
        "recommended_keys"
    ]
    assert client.post(
        f"/api/assessments/{assessment_id}/breakthrough/select",
        json={
            "selected_keys": recommended_keys[:2],
            "selection_mode": "system_recommended",
        },
    ).status_code == 200

    expand_response = client.post(f"/api/assessments/{assessment_id}/directions/expand")
    assert expand_response.status_code == 200

    from sqlalchemy import select

    from app.models.direction_expansion import DirectionExpansion

    custom_ids = ["llm_direction_alpha", "llm_direction_beta"]
    enhanced_expansion = {
        "generation_mode": "llm",
        "llm_status": "completed",
        "total_suggestions": 2,
        "elements": [
            {
                "element_key": recommended_keys[0],
                "element_title": "收入来源",
                "suggestions": [
                    {
                        "direction_id": custom_ids[0],
                        "element_key": recommended_keys[0],
                        "title": "AI 驱动动态定价与个性化促销引擎",
                        "description": "根据会员行为实时调整活动策略。",
                        "expected_impact": "提升转化与复购。",
                        "data_needed": ["会员画像", "订单明细"],
                        "related_scenario_categories": ["销售增长"],
                    },
                    {
                        "direction_id": custom_ids[1],
                        "element_key": recommended_keys[0],
                        "title": "会员订阅付费计划",
                        "description": "围绕高频客户推出订阅权益。",
                        "expected_impact": "提升客单与留存。",
                        "data_needed": ["会员等级", "消费频次"],
                        "related_scenario_categories": ["销售增长"],
                    },
                ],
            }
        ],
    }

    with db_session.SessionLocal() as session:
        record = session.scalar(
            select(DirectionExpansion).where(
                DirectionExpansion.assessment_id == assessment_id
            )
        )
        assert record is not None
        record.generation_mode = "llm"
        record.llm_status = "completed"
        record.expansion_json = json.dumps(enhanced_expansion, ensure_ascii=False)
        session.add(record)
        session.commit()

    select_response = client.post(
        f"/api/assessments/{assessment_id}/directions/select",
        json={"selected_direction_ids": custom_ids},
    )

    assert select_response.status_code == 200
    assert {
        item["direction_id"] for item in select_response.json()["selected_directions"]
    } == set(custom_ids)

    detail_response = client.get(f"/api/assessments/{assessment_id}/directions")

    assert detail_response.status_code == 200
    assert {
        item["direction_id"]
        for item in detail_response.json()["direction_selection"]["selected_directions"]
    } == set(custom_ids)


def test_expand_directions_clears_existing_selection_and_downstream_outputs(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _prepare_for_report(client, assessment_payload)

    response = client.post(f"/api/assessments/{assessment_id}/directions/expand")

    assert response.status_code == 200
    body = response.json()
    assert body["direction_selection"] is None

    detail_response = client.get(f"/api/assessments/{assessment_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["direction_selection"] is None
    assert detail["scenario_recommendation"] is None
    assert detail["competitiveness"] is None
    assert detail["endgame"] is None
    assert detail["progress"]["has_directions"] is False
    assert detail["progress"]["has_scenarios"] is False
    assert detail["progress"]["has_competitiveness"] is False
    assert detail["progress"]["has_endgame"] is False


def test_get_directions_normalizes_duplicate_ids_and_total_count(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200

    breakthrough_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    recommended_keys = breakthrough_response.json()["breakthrough_recommendation"][
        "recommended_keys"
    ]
    assert client.post(
        f"/api/assessments/{assessment_id}/breakthrough/select",
        json={
            "selected_keys": recommended_keys[:2],
            "selection_mode": "system_recommended",
        },
    ).status_code == 200

    expand_response = client.post(f"/api/assessments/{assessment_id}/directions/expand")
    assert expand_response.status_code == 200

    from sqlalchemy import select

    from app.models.direction_expansion import DirectionExpansion

    duplicate_expansion = {
        "generation_mode": "llm",
        "llm_status": "completed",
        "total_suggestions": 7,
        "elements": [
            {
                "element_key": recommended_keys[0],
                "element_title": "收入来源",
                "suggestions": [
                    {
                        "direction_id": "direction-1",
                        "element_key": recommended_keys[0],
                        "title": "方向 1",
                        "description": "描述 1",
                        "expected_impact": "影响 1",
                        "data_needed": ["数据 1"],
                        "related_scenario_categories": ["销售增长"],
                    },
                    {
                        "direction_id": "direction-2",
                        "element_key": recommended_keys[0],
                        "title": "方向 2",
                        "description": "描述 2",
                        "expected_impact": "影响 2",
                        "data_needed": ["数据 2"],
                        "related_scenario_categories": ["销售增长"],
                    },
                    {
                        "direction_id": "direction-3",
                        "element_key": recommended_keys[0],
                        "title": "方向 3",
                        "description": "描述 3",
                        "expected_impact": "影响 3",
                        "data_needed": ["数据 3"],
                        "related_scenario_categories": ["销售增长"],
                    },
                    {
                        "direction_id": "direction-4",
                        "element_key": recommended_keys[0],
                        "title": "方向 4",
                        "description": "描述 4",
                        "expected_impact": "影响 4",
                        "data_needed": ["数据 4"],
                        "related_scenario_categories": ["销售增长"],
                    },
                ],
            },
            {
                "element_key": recommended_keys[1],
                "element_title": "客户关系",
                "suggestions": [
                    {
                        "direction_id": "direction-4",
                        "element_key": recommended_keys[1],
                        "title": "重复方向 4",
                        "description": "重复描述",
                        "expected_impact": "重复影响",
                        "data_needed": ["重复数据"],
                        "related_scenario_categories": ["客户服务"],
                    },
                    {
                        "direction_id": "direction-5",
                        "element_key": recommended_keys[1],
                        "title": "方向 5",
                        "description": "描述 5",
                        "expected_impact": "影响 5",
                        "data_needed": ["数据 5"],
                        "related_scenario_categories": ["客户服务"],
                    },
                    {
                        "direction_id": "direction-6",
                        "element_key": recommended_keys[1],
                        "title": "方向 6",
                        "description": "描述 6",
                        "expected_impact": "影响 6",
                        "data_needed": ["数据 6"],
                        "related_scenario_categories": ["客户服务"],
                    },
                ],
            },
        ],
    }

    with db_session.SessionLocal() as session:
        record = session.scalar(
            select(DirectionExpansion).where(
                DirectionExpansion.assessment_id == assessment_id
            )
        )
        assert record is not None
        record.generation_mode = "llm"
        record.llm_status = "completed"
        record.expansion_json = json.dumps(duplicate_expansion, ensure_ascii=False)
        session.add(record)
        session.commit()

    response = client.get(f"/api/assessments/{assessment_id}/directions")

    assert response.status_code == 200
    expansion = response.json()["direction_expansion"]
    all_ids = [
        suggestion["direction_id"]
        for element in expansion["elements"]
        for suggestion in element["suggestions"]
    ]
    assert expansion["total_suggestions"] == 6
    assert len(all_ids) == 6
    assert len(set(all_ids)) == 6


def test_main_flow_generates_competitiveness_endgame_and_report_without_old_labels(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    """确认主流程可生成点线面结果，并且报告中不再混入旧省略号与终局量化标签。"""
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200

    breakthrough_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    recommended_keys = breakthrough_response.json()["breakthrough_recommendation"][
        "recommended_keys"
    ]
    assert client.post(
        f"/api/assessments/{assessment_id}/breakthrough/select",
        json={
            "selected_keys": recommended_keys[:2],
            "selection_mode": "system_recommended",
        },
    ).status_code == 200

    expand_response = client.post(f"/api/assessments/{assessment_id}/directions/expand")
    assert expand_response.status_code == 200
    expanded = expand_response.json()["direction_expansion"]["elements"]
    selected_direction_ids = [
        expanded[0]["suggestions"][0]["direction_id"],
        expanded[1]["suggestions"][0]["direction_id"],
    ]
    assert client.post(
        f"/api/assessments/{assessment_id}/directions/select",
        json={"selected_direction_ids": selected_direction_ids},
    ).status_code == 200

    assert client.post(f"/api/assessments/{assessment_id}/scenarios").status_code == 200

    competitiveness_response = client.post(
        f"/api/assessments/{assessment_id}/competitiveness/generate"
    )
    assert competitiveness_response.status_code == 200
    competitiveness_payload = json.dumps(
        competitiveness_response.json(), ensure_ascii=False
    )
    assert "..." not in competitiveness_payload
    assert "…" not in competitiveness_payload

    endgame_response = client.post(f"/api/assessments/{assessment_id}/endgame/generate")
    assert endgame_response.status_code == 200
    endgame_body = endgame_response.json()["result"]
    assert endgame_body["three_stage_strategy"]["stage_1"]["focus"] == "快速验证"
    assert "execution_rhythm" in endgame_body["strategic_paths"][0]
    assert "timeline" not in endgame_body["strategic_paths"][0]

    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=template")
    assert report_response.status_code == 200
    report_payload = json.dumps(report_response.json(), ensure_ascii=False)
    assert "投资需求" not in report_payload
    assert "时间范围" not in report_payload

    detail_response = client.get(f"/api/assessments/{assessment_id}")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["progress"]["has_directions"] is True
    assert detail_body["progress"]["has_competitiveness"] is True


def test_scenario_recommendations_alias_is_backward_compatible(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)

    alias_response = client.post(
        f"/api/assessments/{assessment_id}/scenario-recommendations"
    )
    canonical_response = client.post(f"/api/assessments/{assessment_id}/scenarios")

    assert alias_response.status_code == 200
    alias_body = alias_response.json()["scenario_recommendation"]
    assert alias_body["scoring_method"] == "four_quadrant_v1"
    assert len(alias_body["top_scenarios"]) >= 1

    assert canonical_response.status_code == 200
    canonical_body = canonical_response.json()["scenario_recommendation"]
    assert canonical_body["scoring_method"] == "four_quadrant_v1"
    assert [item["name"] for item in canonical_body["top_scenarios"]] == [
        item["name"] for item in alias_body["top_scenarios"]
    ]

    # 验证 legacy mode 仍返回 rule_based_v1
    legacy_response = client.post(
        f"/api/assessments/{assessment_id}/scenarios?mode=legacy"
    )
    assert legacy_response.status_code == 200
    legacy_body = legacy_response.json()["scenario_recommendation"]
    assert legacy_body["scoring_method"] == "rule_based_v1"
    assert len(legacy_body["top_scenarios"]) == 3
    assert legacy_body.get("all_scores") is None

    # 验证四象限模式返回 all_scores
    assert canonical_body.get("all_scores") is not None
    assert len(canonical_body["all_scores"]) >= len(canonical_body["top_scenarios"])


def test_save_calibrations_persists_xy_and_reranks_top3(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)

    scenarios_resp = client.post(f"/api/assessments/{assessment_id}/scenarios")
    assert scenarios_resp.status_code == 200
    original = scenarios_resp.json()["scenario_recommendation"]
    all_scores = original.get("all_scores") or original["top_scenarios"]

    if len(all_scores) < 1:
        return

    first = all_scores[0]
    calibrations = [
        {
            "scenario_id": first["scenario_id"],
            "priority_structuredness_x": 5.0,
            "priority_complexity_y": 1.0,
        }
    ]

    cal_resp = client.post(
        f"/api/assessments/{assessment_id}/scenarios/calibrations",
        json={"calibrations": calibrations},
    )
    assert cal_resp.status_code == 200
    cal_body = cal_resp.json()["scenario_recommendation"]

    updated = next(
        (s for s in cal_body["all_scores"] if s["scenario_id"] == first["scenario_id"]),
        None,
    )
    assert updated is not None
    assert updated["priority_structuredness_x"] == 5.0
    assert updated["priority_complexity_y"] == 1.0
    assert updated["priority_qs"] == 5.0
    assert updated["priority_quadrant"] == "自动化主战场"
    assert updated["priority_tier"] == 1
    assert updated["recommendation_level"] == "立即启动"

    # 刷新后数据应持久化
    detail_resp = client.get(f"/api/assessments/{assessment_id}")
    assert detail_resp.status_code == 200
    detail_scenarios = detail_resp.json()["scenario_recommendation"]
    assert detail_scenarios is not None
    detail_updated = next(
        (s for s in detail_scenarios["all_scores"]
         if s["scenario_id"] == first["scenario_id"]),
        None,
    )
    assert detail_updated is not None
    assert detail_updated["priority_structuredness_x"] == 5.0


def test_update_scenario_pool_persists_active_and_excluded_buckets_and_clears_downstream_outputs(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _prepare_for_report(client, assessment_payload)
    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=template")
    assert report_response.status_code == 200

    detail_before = client.get(f"/api/assessments/{assessment_id}")
    assert detail_before.status_code == 200
    original_scenarios = detail_before.json()["scenario_recommendation"]
    all_scores = original_scenarios["all_scores"]
    assert all_scores is not None
    assert len(all_scores) >= 4

    removed_id = all_scores[3]["scenario_id"]
    original_ids = [item["scenario_id"] for item in all_scores]
    next_active_ids = [scenario_id for scenario_id in original_ids if scenario_id != removed_id]

    update_response = client.put(
        f"/api/assessments/{assessment_id}/scenarios/pool",
        json={"active_scenario_ids": next_active_ids},
    )
    assert update_response.status_code == 200
    updated_scenarios = update_response.json()["scenario_recommendation"]
    assert updated_scenarios["active_count"] == len(next_active_ids)
    assert all(
        item["scenario_id"] != removed_id for item in updated_scenarios["all_scores"]
    )
    assert any(
        item["scenario_id"] == removed_id
        for item in updated_scenarios["excluded_scores"]
    )

    detail_after_update = client.get(f"/api/assessments/{assessment_id}")
    assert detail_after_update.status_code == 200
    detail_body = detail_after_update.json()
    assert detail_body["progress"]["has_competitiveness"] is False
    assert detail_body["progress"]["has_endgame"] is False
    assert detail_body["progress"]["has_report"] is False
    assert detail_body["progress"].get("has_cases") is False
    assert detail_body["scenario_recommendation"]["active_count"] == len(next_active_ids)

    restore_response = client.put(
        f"/api/assessments/{assessment_id}/scenarios/pool",
        json={"active_scenario_ids": original_ids},
    )
    assert restore_response.status_code == 200
    restored_scenarios = restore_response.json()["scenario_recommendation"]
    assert restored_scenarios["active_count"] == len(original_ids)
    assert restored_scenarios["excluded_scores"] == []


def test_calibration_keeps_removed_scenarios_out_of_top3(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)

    scenarios_response = client.post(f"/api/assessments/{assessment_id}/scenarios")
    assert scenarios_response.status_code == 200
    scenario_body = scenarios_response.json()["scenario_recommendation"]
    all_scores = scenario_body["all_scores"]
    assert all_scores is not None
    assert len(all_scores) >= 4

    removed = all_scores[3]
    removed_id = removed["scenario_id"]
    active_ids = [
        item["scenario_id"]
        for item in all_scores
        if item["scenario_id"] != removed_id
    ]

    pool_response = client.put(
        f"/api/assessments/{assessment_id}/scenarios/pool",
        json={"active_scenario_ids": active_ids},
    )
    assert pool_response.status_code == 200

    calibration_response = client.post(
        f"/api/assessments/{assessment_id}/scenarios/calibrations",
        json={
            "calibrations": [
                {
                    "scenario_id": removed_id,
                    "priority_structuredness_x": 5.0,
                    "priority_complexity_y": 1.0,
                }
            ]
        },
    )
    assert calibration_response.status_code == 200
    calibrated = calibration_response.json()["scenario_recommendation"]

    assert all(
        item["scenario_id"] != removed_id for item in calibrated["top_scenarios"]
    )
    removed_after = next(
        item
        for item in calibrated["excluded_scores"]
        if item["scenario_id"] == removed_id
    )
    assert removed_after["priority_structuredness_x"] == 5.0
    assert removed_after["priority_complexity_y"] == 1.0

    detail_response = client.get(f"/api/assessments/{assessment_id}")
    assert detail_response.status_code == 200
    detail_scenarios = detail_response.json()["scenario_recommendation"]
    assert detail_scenarios["active_count"] == len(active_ids)
    assert all(
        item["scenario_id"] != removed_id
        for item in detail_scenarios["top_scenarios"]
    )


def test_calibration_requires_existing_scenarios(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)
    cal_resp = client.post(
        f"/api/assessments/{assessment_id}/scenarios/calibrations",
        json={"calibrations": [{"scenario_id": "test", "priority_structuredness_x": 3, "priority_complexity_y": 3}]},
    )
    assert cal_resp.status_code in (404, 400)


def test_live_scenario_packaging_rewrites_top3_and_syncs_all_scores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.routes import assessments as assessments_routes
    from app.schemas.assessment import (
        BusinessModelCanvasResult,
        CanvasBlockResult,
        CanvasDiagnosisResult,
        ScenarioRecommendationItem,
    )

    monkeypatch.setattr(
        LLMEnhancer,
        "enhance_scenario_descriptions",
        lambda self, assessment, profile, canvas_diagnosis, breakthrough_labels, selected_directions, scenarios: [
            scenario.model_copy(
                update={
                    "summary": f"改写场景摘要 {index}",
                    "canvas_elements": f"对应突破要素：突破{index}",
                    "expected_effects": f"预期收益：收益{index}",
                    "core_data_requirements": f"资源准备：准备{index}",
                }
            )
            for index, scenario in enumerate(scenarios, start=1)
        ],
    )

    canvas = CanvasDiagnosisResult(
        generation_mode="mock",
        overall_score=70,
        weakest_blocks=["客户关系"],
        recommended_focus=["客户关系"],
        canvas=BusinessModelCanvasResult(
            overall_summary="摘要",
            blocks=[
                CanvasBlockResult(
                    key="customer_relationships",
                    title="客户关系",
                    current_state="现状",
                    diagnosis="诊断",
                    ai_opportunity="机会",
                    missing_information="",
                )
            ],
        ),
    )
    top_scenarios = [
        ScenarioRecommendationItem(
            scenario_id="s-1",
            name="场景 1",
            category="客户经营",
            summary="旧摘要 1",
            canvas_elements="旧切入 1",
            expected_effects="旧收益 1",
            core_data_requirements="旧资源 1",
            priority_quadrant="AI优先区",
        ),
        ScenarioRecommendationItem(
            scenario_id="s-2",
            name="场景 2",
            category="客户经营",
            summary="旧摘要 2",
            canvas_elements="旧切入 2",
            expected_effects="旧收益 2",
            core_data_requirements="旧资源 2",
            priority_quadrant="自动化主战场",
        ),
    ]
    all_scores = top_scenarios + [
        ScenarioRecommendationItem(
            scenario_id="s-3",
            name="场景 3",
            category="客户经营",
            summary="旧摘要 3",
            canvas_elements="旧切入 3",
            expected_effects="旧收益 3",
            core_data_requirements="旧资源 3",
            priority_quadrant="人机协作区",
        )
    ]

    merged_top, merged_all = assessments_routes._enhance_scenario_description_fields(
        assessment=SimpleNamespace(
            company_name="测试企业",
            industry="零售",
            company_size="100-499人",
            region="华东",
            annual_revenue_range="5000万-1亿元",
            core_products="门店服务",
            target_customers="会员用户",
            current_challenges="复购波动",
            ai_goals="提升复购",
            available_data="POS、会员数据",
            notes="先试点",
        ),
        profile=None,
        canvas=canvas,
        breakthrough_labels=["客户关系"],
        selected_directions=[],
        top_scenarios=top_scenarios,
        all_scores=all_scores,
    )

    assert merged_top[0].summary == "改写场景摘要 1"
    assert merged_top[1].summary == "改写场景摘要 2"
    assert merged_all is not None
    assert merged_all[0].summary == "改写场景摘要 1"
    assert merged_all[1].summary == "改写场景摘要 2"
    assert merged_all[2].summary == "旧摘要 3"


@pytest.mark.skip(reason="manual scenario calibration no longer re-runs LLM packaging")
def test_calibration_repackages_promoted_top3_when_live_packaging_enabled(
    client: TestClient,
    assessment_payload: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)

    scenarios_response = client.post(f"/api/assessments/{assessment_id}/scenarios")
    assert scenarios_response.status_code == 200
    scenario_body = scenarios_response.json()["scenario_recommendation"]
    all_scores = scenario_body["all_scores"]
    assert all_scores is not None
    assert len(all_scores) >= 4

    target = scenario_body["top_scenarios"][0]
    rewrites = [
        {
            "scenario_id": item["scenario_id"],
            "summary": f"{item['name']} 的管理层改写摘要",
            "canvas_elements": f"{item['name']} 的突破要素与战略价值",
            "expected_effects": f"{item['name']} 的预期收益",
            "core_data_requirements": f"{item['name']} 的资源准备",
        }
        for item in scenario_body["top_scenarios"]
    ]

    monkeypatch.setattr(
        LLMEnhancer,
        "enhance_scenario_descriptions",
        lambda self, assessment, profile, canvas_diagnosis, breakthrough_labels, selected_directions, scenarios: [
            scenario.model_copy(
                update=next(
                    rewrite
                    for rewrite in rewrites
                    if rewrite["scenario_id"] == scenario.scenario_id
                )
            )
            if any(
                rewrite["scenario_id"] == scenario.scenario_id for rewrite in rewrites
            )
            else scenario
            for scenario in scenarios
        ],
    )

    calibration_response = client.post(
        f"/api/assessments/{assessment_id}/scenarios/calibrations",
        json={
            "calibrations": [
                {
                    "scenario_id": target["scenario_id"],
                    "priority_structuredness_x": 5.0,
                    "priority_complexity_y": 1.0,
                }
            ]
        },
    )
    assert calibration_response.status_code == 200
    calibrated = calibration_response.json()["scenario_recommendation"]

    promoted_top = next(
        (
            item
            for item in calibrated["top_scenarios"]
            if item["scenario_id"] == target["scenario_id"]
        ),
        None,
    )
    assert promoted_top is not None
    assert promoted_top["summary"] == f"{target['name']} 的管理层改写摘要"
    assert (
        promoted_top["expected_effects"]
        == f"{target['name']} 的预期收益"
    )

    promoted_all = next(
        item
        for item in calibrated["all_scores"]
        if item["scenario_id"] == target["scenario_id"]
    )
    assert promoted_all["summary"] == promoted_top["summary"]
    assert (
        promoted_all["core_data_requirements"]
        == f"{target['name']} 的资源准备"
    )


def test_calibration_keeps_text_without_repackaging(
    client: TestClient,
    assessment_payload: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)

    scenarios_response = client.post(f"/api/assessments/{assessment_id}/scenarios")
    assert scenarios_response.status_code == 200
    scenario_body = scenarios_response.json()["scenario_recommendation"]
    all_scores = scenario_body["all_scores"]
    assert all_scores is not None
    assert len(all_scores) >= 4

    target = scenario_body["top_scenarios"][0]
    monkeypatch.setattr(
        LLMEnhancer,
        "enhance_scenario_descriptions",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("manual calibration should not trigger scenario repackaging")
        ),
    )

    calibration_response = client.post(
        f"/api/assessments/{assessment_id}/scenarios/calibrations",
        json={
            "calibrations": [
                {
                    "scenario_id": target["scenario_id"],
                    "priority_structuredness_x": 5.0,
                    "priority_complexity_y": 1.0,
                }
            ]
        },
    )
    assert calibration_response.status_code == 200
    calibrated = calibration_response.json()["scenario_recommendation"]

    promoted_top = next(
        (
            item
            for item in calibrated["top_scenarios"]
            if item["scenario_id"] == target["scenario_id"]
        ),
        None,
    )
    assert promoted_top is not None
    assert promoted_top["summary"] == target["summary"]
    assert promoted_top["expected_effects"] == target["expected_effects"]

    promoted_all = next(
        item
        for item in calibrated["all_scores"]
        if item["scenario_id"] == target["scenario_id"]
    )
    assert promoted_all["summary"] == promoted_top["summary"]
    assert promoted_all["core_data_requirements"] == target["core_data_requirements"]


def test_pool_update_reorders_top3_without_repackaging_text(
    client: TestClient,
    assessment_payload: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assessment_id = _prepare_for_scenarios(client, assessment_payload)

    scenarios_response = client.post(f"/api/assessments/{assessment_id}/scenarios")
    assert scenarios_response.status_code == 200
    scenario_body = scenarios_response.json()["scenario_recommendation"]
    all_scores = scenario_body["all_scores"]
    assert all_scores is not None
    assert len(all_scores) >= 4

    removed_top_id = all_scores[0]["scenario_id"]
    promoted_candidate = all_scores[3]
    monkeypatch.setattr(
        LLMEnhancer,
        "enhance_scenario_descriptions",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("scenario pool update should not trigger scenario repackaging")
        ),
    )

    next_active_ids = [
        item["scenario_id"] for item in all_scores if item["scenario_id"] != removed_top_id
    ]
    pool_response = client.put(
        f"/api/assessments/{assessment_id}/scenarios/pool",
        json={"active_scenario_ids": next_active_ids},
    )
    assert pool_response.status_code == 200
    updated = pool_response.json()["scenario_recommendation"]

    promoted_top = next(
        (
            item
            for item in updated["top_scenarios"]
            if item["scenario_id"] == promoted_candidate["scenario_id"]
        ),
        None,
    )
    assert promoted_top is not None
    assert promoted_top["summary"] == promoted_candidate["summary"]
    assert promoted_top["canvas_elements"] == promoted_candidate["canvas_elements"]


def test_enhance_scenario_descriptions_only_overrides_text_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.schemas.assessment import (
        BusinessModelCanvasResult,
        CanvasBlockResult,
        CanvasDiagnosisResult,
        CompanyProfileResult,
        ScenarioRecommendationItem,
    )
    from app.schemas.direction import DirectionSuggestion

    enhancer = LLMEnhancer()
    monkeypatch.setattr(LLMEnhancer, "_is_live_mode", lambda self: True)
    monkeypatch.setattr(
        LLMEnhancer,
        "_call_llm",
        lambda self, system_prompt, user_prompt: {
            "scenarios": [
                {
                    "scenario_id": "scenario-1",
                    "summary": "新的管理层场景描述",
                    "canvas_elements": "对应突破要素与战略价值",
                    "expected_effects": "新的预期收益",
                    "core_data_requirements": "新的资源准备",
                }
            ]
        },
    )

    assessment = SimpleNamespace(
        company_name="测试零售企业",
        industry="零售",
        company_size="100-499人",
        region="华东",
        annual_revenue_range="5000万-1亿元",
        core_products="社区零售门店",
        target_customers="会员用户",
        current_challenges="复购波动",
        ai_goals="提升复购",
        available_data="POS、会员数据",
        notes="先试点",
    )
    profile = CompanyProfileResult(
        company_name="测试零售企业",
        company_summary="企业概览",
        value_proposition="价值主张",
        customer_and_market="客户与市场",
        operations_and_resources="运营与资源",
        digital_and_ai_readiness="准备度",
        key_challenges=["复购波动"],
        priority_ai_directions=["会员经营"],
    )
    canvas = CanvasDiagnosisResult(
        generation_mode="mock",
        overall_score=68,
        weakest_blocks=["客户关系"],
        recommended_focus=["客户关系"],
        canvas=BusinessModelCanvasResult(
            overall_summary="画布总体摘要",
            blocks=[
                CanvasBlockResult(
                    key="customer_relationships",
                    title="客户关系",
                    current_state="依赖门店经验",
                    diagnosis="复购运营缺少统一机制",
                    ai_opportunity="建立客户分层与召回",
                    missing_information="",
                )
            ],
        ),
    )
    directions = [
        DirectionSuggestion(
            direction_id="dir-1",
            element_key="customer_relationships",
            title="会员经营自动化",
            description="围绕复购做分层运营",
            expected_impact="提升复购稳定性",
            data_needed=["POS", "会员标签"],
            related_scenario_categories=["客户经营"],
        )
    ]
    source = ScenarioRecommendationItem(
        scenario_id="scenario-1",
        name="AI 流失预测与自动关怀",
        category="客户经营",
        summary="旧摘要",
        canvas_elements="旧切入点",
        expected_effects="旧收益",
        core_data_requirements="旧资源",
        priority_structuredness_x=4.0,
        priority_complexity_y=2.0,
        priority_qs=4.0,
        priority_lps=7.2,
        priority_lps_display=7.0,
        priority_quadrant="AI优先区",
        priority_tier=2,
        priority_recommendation="原推荐说明",
        recommendation_level="规划推进",
    )

    result = enhancer.enhance_scenario_descriptions(
        assessment=assessment,
        profile=profile,
        canvas_diagnosis=canvas,
        breakthrough_labels=["客户关系"],
        selected_directions=directions,
        scenarios=[source],
    )

    assert result is not None
    assert result[0].summary == "新的管理层场景描述"
    assert result[0].canvas_elements == "对应突破要素与战略价值"
    assert result[0].expected_effects == "新的预期收益"
    assert result[0].core_data_requirements == "新的资源准备"
    assert result[0].priority_qs == 4.0
    assert result[0].priority_quadrant == "AI优先区"
    assert result[0].priority_recommendation == "原推荐说明"


def test_report_endpoints_return_404_for_missing_report_id(client: TestClient) -> None:
    missing_report_id = "missing-report-id"

    report_response = client.get(f"/api/reports/{missing_report_id}")
    markdown_response = client.get(
        f"/api/reports/{missing_report_id}/export/markdown"
    )
    docx_response = client.get(f"/api/reports/{missing_report_id}/export/docx")
    print_response = client.get(f"/api/reports/{missing_report_id}/print")

    for response in (
        report_response,
        markdown_response,
        docx_response,
        print_response,
    ):
        assert response.status_code == 404
        assert response.json()["detail"] == "Report not found."


def test_live_llm_report_success_path_is_opt_in(
    client: TestClient,
    assessment_payload: dict[str, str],
) -> None:
    if not _live_llm_report_test_enabled():
        pytest.skip(
            "Set RUN_LIVE_LLM_TESTS=true together with LLM_REPORT_ENABLED=true, "
            "OPENAI_API_KEY, and OPENAI_MODEL to run the live LLM report test."
        )

    assessment_id = _prepare_for_report(client, assessment_payload)

    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=llm")

    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["generation_mode"] == "llm"
    assert report_body["used_llm"] is True
    assert report_body["content_json"]["generated_with"] == "llm"
    assert len(report_body["sections"]) == 13
