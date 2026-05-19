from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db import session as db_session
from app.main import create_app
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
    assert profile_response.json()["generation_mode"] == "mock"

    canvas_response = client.post(f"/api/assessments/{assessment_id}/canvas")
    assert canvas_response.status_code == 200
    canvas_body = canvas_response.json()["canvas_diagnosis"]
    assert canvas_body["generation_mode"] == "mock"
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
    assert detail_body["progress"]["has_directions"] is False
    assert detail_body["progress"]["has_competitiveness"] is False
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
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/scenarios").status_code == 200

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
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/scenarios").status_code == 200

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

    select_response = client.post(
        f"/api/assessments/{assessment_id}/directions/select",
        json={"selected_direction_ids": selected_direction_ids},
    )
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

    assert client.post(f"/api/assessments/{assessment_id}/scenarios").status_code == 200
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
    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200

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

    assessment_id = _create_assessment(client, assessment_payload)

    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/scenarios").status_code == 200

    report_response = client.post(f"/api/assessments/{assessment_id}/report?mode=llm")

    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["generation_mode"] == "llm"
    assert report_body["used_llm"] is True
    assert report_body["content_json"]["generated_with"] == "llm"
    assert len(report_body["sections"]) == 13
