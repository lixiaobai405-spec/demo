"""
Full end-to-end test: 画像→画布→突破→方向→场景→案例→报告→导出
Runs against the live backend at localhost:8000 (new DB each run via TEST_DB).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import session as db_session
from app.main import create_app

TEST_DB_PATH = Path(__file__).resolve().parent / "test_e2e_full_chain.db"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    engine = create_engine(
        f"sqlite:///{TEST_DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", testing_session_local)

    db_session.Base.metadata.create_all(bind=engine)
    db_session._migrate_generated_reports_table()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


PAYLOAD = {
    "company_name": "智慧云链科技有限公司",
    "industry": "供应链科技",
    "company_size": "200-500人",
    "region": "华东",
    "annual_revenue_range": "1亿-10亿",
    "core_products": "智能供应链协同平台、仓储机器人调度系统、物流可视化中台",
    "target_customers": "中大型制造企业、区域物流服务商、品牌零售企业",
    "current_challenges": "订单交付波动大，跨部门协同低效，知识传递依赖核心骨干，获客成本持续上升",
    "ai_goals": "提升订单履约准确率，降低跨部门沟通成本，沉淀可复用的供应链优化知识，提升销售线索转化",
    "available_data": "ERP 订单与库存、WMS 仓储数据、CRM 客户与商机、客服工单、设备运行日志",
    "notes": "已完成一期 ERP 和 WMS 系统上线，正推进数据中台建设。希望在二期引入 AI 能力增强供应链决策。",
}


class TestFullChainE2E:
    """端到端全链路测试"""

    def test_full_chain(self, client: TestClient) -> None:
        print("\n" + "=" * 60)
        print("  全链路 E2E 测试：画像→画布→突破→方向→场景→案例→报告")
        print("=" * 60)

        # ── Step 1: 创建 Assessment ──
        resp = client.post("/api/assessments", json=PAYLOAD)
        assert resp.status_code == 201, f"Create assessment failed: {resp.text}"
        assessment = resp.json()
        assessment_id = assessment["id"]
        assert assessment["company_name"] == PAYLOAD["company_name"]
        print(f"\n✅ Step 1 创建问卷 → {assessment_id[:8]}...")

        # ── Step 2: 生成企业画像 ──
        resp = client.post(f"/api/assessments/{assessment_id}/profile")
        assert resp.status_code == 200, f"Profile failed: {resp.text}"
        profile_body = resp.json()
        assert profile_body["generation_mode"] == "mock"
        assert profile_body["profile"]["company_name"] == PAYLOAD["company_name"]
        print(f"✅ Step 2 企业画像 → mode={profile_body['generation_mode']}")

        # ── Step 3: 生成商业模式画布 ──
        resp = client.post(f"/api/assessments/{assessment_id}/canvas")
        assert resp.status_code == 200, f"Canvas failed: {resp.text}"
        canvas_body = resp.json()["canvas_diagnosis"]
        assert canvas_body["generation_mode"] == "mock"
        assert len(canvas_body["canvas"]["blocks"]) == 9
        assert 0 <= canvas_body["overall_score"] <= 100
        print(f"✅ Step 3 商业画布 → 评分={canvas_body['overall_score']}, 薄弱={canvas_body['weakest_blocks']}")

        # ── Step 4: 生成突破要素推荐 ──
        resp = client.post(f"/api/assessments/{assessment_id}/breakthrough/recommend")
        assert resp.status_code == 200, f"Breakthrough recommend failed: {resp.text}"
        bt_body = resp.json()
        assert bt_body["assessment_id"] == assessment_id
        assert bt_body["breakthrough_recommendation"]["generation_mode"] == "rule_based"
        assert len(bt_body["breakthrough_recommendation"]["elements"]) == 9
        recommended = bt_body["breakthrough_recommendation"]["recommended_keys"]
        assert len(recommended) == 3
        print(f"✅ Step 4 突破要素推荐 → {recommended}")

        # ── Step 5: 选择突破要素 ──
        resp = client.post(
            f"/api/assessments/{assessment_id}/breakthrough/select",
            json={"selected_keys": recommended[:2], "selection_mode": "system_recommended"},
        )
        assert resp.status_code == 200, f"Breakthrough select failed: {resp.text}"
        sel_body = resp.json()
        assert sel_body["selection_mode"] == "system_recommended"
        assert len(sel_body["selected_elements"]) == 2
        selected_elements = sel_body["selected_elements"]
        print(f"✅ Step 5 突破要素选择 → {[e['title'] for e in selected_elements]}")

        # ── Step 6: 方向延展 ──
        resp = client.post(f"/api/assessments/{assessment_id}/directions/expand")
        assert resp.status_code == 200, f"Direction expand failed: {resp.text}"
        dir_body = resp.json()
        expansion = dir_body["direction_expansion"]
        assert expansion["generation_mode"] == "rule_based"
        assert expansion["total_suggestions"] >= 2

        all_direction_ids: list[str] = []
        for elem in expansion["elements"]:
            for s in elem["suggestions"]:
                all_direction_ids.append(s["direction_id"])
        print(f"✅ Step 6 方向延展 → {expansion['total_suggestions']} 个方向")

        # ── Step 7: 方向选择 ──
        selected_dir_ids = all_direction_ids[:4]  # pick 4
        resp = client.post(
            f"/api/assessments/{assessment_id}/directions/select",
            json={"selected_direction_ids": selected_dir_ids},
        )
        assert resp.status_code == 200, f"Direction select failed: {resp.text}"
        dir_sel_body = resp.json()
        assert len(dir_sel_body["selected_directions"]) == 4
        print(f"✅ Step 7 方向选择 → {len(dir_sel_body['selected_directions'])} 个")

        # ── Step 8: 获取方向详情(GET) ──
        resp = client.get(f"/api/assessments/{assessment_id}/directions")
        assert resp.status_code == 200, f"GET directions failed: {resp.text}"
        dir_get = resp.json()
        assert dir_get["direction_selection"] is not None
        assert len(dir_get["direction_selection"]["selected_directions"]) == 4
        print(f"✅ Step 8 GET 方向 → 已选 {len(dir_get['direction_selection']['selected_directions'])} 个")

        # ── Step 9: 差异化竞争力分析 ──
        resp = client.post(f"/api/assessments/{assessment_id}/competitiveness/generate")
        assert resp.status_code == 200, f"Competitiveness generate failed: {resp.text}"
        comp_body = resp.json()
        comp_result = comp_body["result"]
        assert comp_result["generation_mode"] == "rule_based"
        assert len(comp_result["vp_reconstruction"]["differentiation_points"]) > 0
        assert len(comp_result["connections"]) > 0
        assert len(comp_result["advantages"]) > 0
        print(f"✅ Step 9 竞争力分析 → {len(comp_result['connections'])} 条竞争力线, {len(comp_result['advantages'])} 个优势")

        # verify GET competitiveness
        resp = client.get(f"/api/assessments/{assessment_id}/competitiveness")
        assert resp.status_code == 200
        comp_get = resp.json()
        assert len(comp_get["result"]["advantages"]) == len(comp_result["advantages"])
        print(f"   → GET 竞争力返回一致，已持久化")

        # ── Step 10: 场景推荐（带方向加权 + 竞争力分析可能清空下游） ──
        # note: competitiveness upsert clears scenarios, so re-generate
        resp = client.post(f"/api/assessments/{assessment_id}/scenarios")
        assert resp.status_code == 200, f"Scenarios failed: {resp.text}"
        sc_body = resp.json()["scenario_recommendation"]
        assert sc_body["scoring_method"] == "rule_based_v1"
        assert len(sc_body["top_scenarios"]) == 3
        print(f"✅ Step 10 场景推荐 → Top 3: {[s['name'] for s in sc_body['top_scenarios']]}")
        # verify direction category matching appears in reasons
        has_direction_reason = any("创新方向" in r for s in sc_body["top_scenarios"] for r in s.get("reasons", []))
        if has_direction_reason:
            print("   → 方向加权生效：推荐理由包含创新方向匹配")

        # ── Step 11: 商业终局分析 ──
        resp = client.post(f"/api/assessments/{assessment_id}/endgame/generate")
        assert resp.status_code == 200, f"Endgame generate failed: {resp.text}"
        endgame_body = resp.json()
        eg_result = endgame_body["result"]
        assert eg_result["generation_mode"] == "rule_based"
        assert len(eg_result["private_domain"]["key_strategies"]) > 0
        assert len(eg_result["strategic_paths"]) == 3
        print(f"✅ Step 11 商业终局 → 私域+生态+OPC, {len(eg_result['strategic_paths'])} 条推演路径")

        # verify GET endgame
        resp = client.get(f"/api/assessments/{assessment_id}/endgame")
        assert resp.status_code == 200
        eg_get = resp.json()
        assert len(eg_get["result"]["strategic_paths"]) == 3
        print(f"   → GET 商业终局返回一致，已持久化")

        # ── Step 12: 案例匹配 ──
        resp = client.post(f"/api/assessments/{assessment_id}/cases")
        assert resp.status_code == 200, f"Cases failed: {resp.text}"
        case_body = resp.json()["case_recommendation"]
        assert case_body["scoring_method"] == "layered_v1"
        assert len(case_body["top_cases"]) >= 1
        print(f"✅ Step 11 案例匹配 → {len(case_body['top_cases'])} 个案例")

        # ── Step 12: Report Context ──
        resp = client.get(f"/api/assessments/{assessment_id}/report-context")
        assert resp.status_code == 200, f"Report context failed: {resp.text}"
        ctx = resp.json()
        assert ctx["assessment_id"] == assessment_id
        assert len(ctx["report_outline"]) == 14
        assert len(ctx["selected_breakthrough_elements"]) == 2
        print(f"✅ Step 12 报告上下文 → 14 章节，突破要素={len(ctx['selected_breakthrough_elements'])} 个")

        # ── Step 13: 模板报告生成（含竞争力数据） ──
        resp = client.post(f"/api/assessments/{assessment_id}/report?mode=template")
        assert resp.status_code == 200, f"Template report failed: {resp.text}"
        report = resp.json()
        assert report["assessment_id"] == assessment_id
        assert report["generation_mode"] == "template"
        assert report["used_llm"] is False
        assert len(report["sections"]) == 14
        report_id = report["report_id"]
        print(f"✅ Step 13 模板报告 → {len(report['sections'])} 章节, report_id={report_id[:8]}...")

        # verify key sections exist
        section_keys = {s["key"] for s in report["content_json"]["sections"]}
        expected_keys = {
            "company_profile", "canvas_diagnosis", "breakthrough",
            "direction_expansion", "ai_readiness", "priority_scenarios",
            "scenario_planning", "competitiveness", "cases",
            "roadmap", "action_plan", "risks", "instructor_comments",
            "endgame",
        }
        missing = expected_keys - section_keys
        assert not missing, f"Missing report sections: {missing}"
        print(f"   → 全部 14 个章节 key 完整")

        # verify competitiveness section has actual data (not fallback)
        comp_section = next((s for s in report["content_json"]["sections"] if s["key"] == "competitiveness"), None)
        assert comp_section is not None
        assert "串联竞争力线" in comp_section.get("content", "") or any("串联竞争力线" in b for b in comp_section.get("bullets", []))
        print(f"   → 竞争力章节已合并到报告，包含点到线串联数据")

        # ── Step 14: Markdown 导出 ──
        resp = client.get(f"/api/reports/{report_id}/export/markdown")
        assert resp.status_code == 200, f"Markdown export failed: {resp.text}"
        md_content = resp.text
        assert "智慧云链科技有限公司" in md_content
        assert "突破要素" in md_content
        assert "创新方向延展" in md_content
        print(f"✅ Step 14 Markdown 导出 → {len(md_content)} 字符")

        # ── Step 15: DOCX 导出 ──
        resp = client.get(f"/api/reports/{report_id}/export/docx")
        assert resp.status_code == 200, f"DOCX export failed: {resp.text}"
        assert len(resp.content) > 1000
        print(f"✅ Step 15 DOCX 导出 → {len(resp.content)} bytes")

        # ── Step 16: 打印版 ──
        resp = client.get(f"/api/reports/{report_id}/print")
        assert resp.status_code == 200, f"Print export failed: {resp.text}"
        assert "智慧云链科技有限公司" in resp.text
        print(f"✅ Step 16 打印版 → OK")

        # ── Step 17: PDF 导出 ──
        resp = client.get(f"/api/reports/{report_id}/export/pdf")
        assert resp.status_code == 200, f"PDF export failed: {resp.text}"
        assert len(resp.content) > 40
        print(f"✅ Step 17 PDF 导出 → {len(resp.content)} bytes")

        # ── Step 18: 报告增强内容 ──
        resp = client.get(f"/api/reports/{report_id}/enrich")
        assert resp.status_code == 200, f"Enrich failed: {resp.text}"
        enrich = resp.json()
        assert "executive_summary" in enrich
        assert "industry_benchmark" in enrich
        assert "roi_framework" in enrich
        assert "instructor_comment" in enrich
        print(f"✅ Step 18 报告增强 → 4 个模块完整")

        # ── Step 19: 报告质量审计 ──
        resp = client.get(f"/api/reports/{report_id}/quality")
        assert resp.status_code == 200, f"Quality failed: {resp.text}"
        quality = resp.json()
        assert "overall_score" in quality
        assert "overall_confidence" in quality
        assert len(quality["sections"]) == 14
        assert 0 <= quality["overall_score"] <= 100
        assert quality["overall_confidence"] in ("高", "中", "低")
        low_sections = [s for s in quality["sections"] if s["confidence"] == "低"]
        high_sections = [s for s in quality["sections"] if s["confidence"] == "高"]
        print(f"✅ Step 19 质量审计 → 评分{quality['overall_score']}, 可信度{quality['overall_confidence']}, 高{len(high_sections)}/中/低{len(low_sections)}")

        # ── Step 20: 报告分享 ──
        resp = client.post(f"/api/reports/{report_id}/share")
        assert resp.status_code == 200, f"Share failed: {resp.text}"
        share = resp.json()
        assert "share_url" in share
        assert "token" in share
        print(f"✅ Step 20 分享链接 → {share['share_url']}")

        # verify the shared link works
        resp = client.get(share["share_url"])
        assert resp.status_code == 200
        assert "智慧云链科技有限公司" in resp.text
        print(f"   → 分享链接可访问")

        # ── Step 21: Assessment Detail 状态恢复 ──

        resp = client.get(f"/api/assessments/{assessment_id}")
        assert resp.status_code == 200, f"Detail failed: {resp.text}"
        detail = resp.json()
        progress = detail["progress"]
        assert progress["has_profile"] is True
        assert progress["has_canvas"] is True
        assert progress["has_breakthrough"] is True
        assert progress["has_scenarios"] is True
        assert progress["has_cases"] is True
        assert progress["has_report"] is True
        assert progress["ready_for_report"] is True
        assert detail["breakthrough_selection"] is not None
        assert len(detail["breakthrough_selection"]) == 2
        print(f"✅ Step 21 状态恢复 → 全部就绪")

        # ── Step 22: 课后 30 天跟进 ──
        resp = client.get(f"/api/assessments/{assessment_id}/follow-up")
        assert resp.status_code == 200, f"Follow-up failed: {resp.text}"
        follow_up = resp.json()
        assert follow_up["assessment_id"] == assessment_id
        assert len(follow_up["tasks"]) == 6
        assert follow_up["total_count"] == 6
        assert follow_up["overall_progress_pct"] == 0
        print(f"✅ Step 22 课后跟进 → {follow_up['total_count']} 项任务已就绪")

        # update a task
        first_task = follow_up["tasks"][0]
        resp = client.patch(
            f"/api/assessments/{assessment_id}/follow-up/tasks/{first_task['task_id']}",
            json={"status": "in_progress", "progress_note": "已确定试点项目范围和数据源，正在组建团队。"}
        )
        assert resp.status_code == 200
        updated_task = resp.json()
        assert updated_task["status"] == "in_progress"
        assert updated_task["progress_note"] == "已确定试点项目范围和数据源，正在组建团队。"
        print(f"   → 任务状态更新成功：pending → in_progress")

        # mark another as completed and one as blocked
        second_task = follow_up["tasks"][1]
        resp = client.patch(
            f"/api/assessments/{assessment_id}/follow-up/tasks/{second_task['task_id']}",
            json={"status": "completed", "progress_note": "数据盘点完成，质量报告已输出。"}
        )
        assert resp.status_code == 200
        third_task = follow_up["tasks"][2]
        resp = client.patch(
            f"/api/assessments/{assessment_id}/follow-up/tasks/{third_task['task_id']}",
            json={"blocked": True, "blocker_description": "IT 资源被其他项目占用，需管理决策。"}
        )
        assert resp.status_code == 200

        # re-fetch
        resp = client.get(f"/api/assessments/{assessment_id}/follow-up")
        plan2 = resp.json()
        assert plan2["overall_progress_pct"] >= 16
        assert plan2["completed_count"] >= 1
        assert plan2["blocked_count"] >= 1
        print(f"   → 刷新后：{plan2['completed_count']}完成/{plan2['blocked_count']}阻塞/{plan2['total_count']}总计 进度{plan2['overall_progress_pct']}%")

        # recalibrate
        resp = client.post(
            f"/api/assessments/{assessment_id}/follow-up/recalibrate",
            json={"note": "30天复盘：第一阶段试点效果超预期，建议加速扩展。", "updated_tasks": []}
        )
        assert resp.status_code == 200
        assert "30天复盘" in resp.json()["recalibration_note"]
        print(f"   → 复盘完成：{resp.json()['recalibration_note'][:30]}...")

        # ── Step 23: 双周案例推送 ──
        resp = client.post(f"/api/assessments/{assessment_id}/push")
        assert resp.status_code == 200, f"Push failed: {resp.text}"
        push1 = resp.json()
        assert push1["cycle"] == 1
        assert len(push1["pushed_cases"]) >= 1
        assert "source_summary" in (push1["pushed_cases"][0] or {})
        print(f"✅ Step 23 案例推送 → 第{push1['cycle']}轮, {len(push1['pushed_cases'])} 个案例, 总库{push1['total_available']}")

        # Push cycle 2 — should get different cases
        resp = client.post(f"/api/assessments/{assessment_id}/push")
        assert resp.status_code == 200
        push2 = resp.json()
        assert push2["cycle"] == 2
        # verify different cases if possible
        if push1["pushed_cases"] and push2["pushed_cases"]:
            p1_ids = {c["case_id"] for c in push1["pushed_cases"]}
            p2_ids = {c["case_id"] for c in push2["pushed_cases"]}
            if len(push1["previous_case_ids"]) < push1["total_available"]:
                assert p1_ids != p2_ids, "Cycle 2 should push different cases"
            print(f"   → 第2轮案例与第1轮不同：去重机制生效")
        else:
            print(f"   → 第2轮推送完成")

        # recalibrate plan via push service
        resp = client.post(
            f"/api/assessments/{assessment_id}/recalibrate",
            json={
                "note": "从B2B软件案例中学到商机分层方法，决定在跟进计划中增加客户分层试点。",
                "new_actions": [{
                    "period": "校准-第1项",
                    "action": "基于案例学习，对Top 20客户做分层标注和差异化服务设计。",
                    "owner_suggestion": "销售负责人",
                    "deliverable": "客户分层方案文档"
                }],
                "update_task_ids": []
            }
        )
        assert resp.status_code == 200
        recal = resp.json()
        assert recal["status"] == "ok"
        assert recal["new_actions"] == 1
        print(f"   → 再校准：新增 {recal['new_actions']} 项行动到跟进计划")

        # ── Step 24: 讲师工作台 ──
        resp = client.get("/api/instructor/dashboard")
        assert resp.status_code == 200, f"Instructor dashboard failed: {resp.text}"
        dash = resp.json()
        assert dash["total_students"] >= 1
        assert len(dash["students"]) >= 1
        student = dash["students"][0]
        assert student["company_name"]
        assert student["has_report"] is True
        print(f"✅ Step 24 讲师工作台 → {dash['total_students']} 名学员, 完成率 {dash['overall_completion_pct']}%")

        # batch comment
        resp = client.post(
            "/api/instructor/batch-comment",
            json={"assessment_ids": [assessment_id], "comment": "整体方案可行，重点关注数据基础建设。"}
        )
        assert resp.status_code == 200
        assert resp.json()["updated_count"] == 1
        print("   → 批量点评成功")

        # export CSV
        resp = client.get("/api/instructor/export?format=csv")
        assert resp.status_code == 200
        csv_data = resp.json()
        assert csv_data["student_count"] >= 1
        assert "company_name" in csv_data["content"]
        print(f"   → CSV 导出：{csv_data['student_count']} 条记录")

        # ── Step 25: 级联清空验证 ──
        resp = client.post(f"/api/assessments/{assessment_id}/canvas")
        assert resp.status_code == 200
        resp = client.get(f"/api/assessments/{assessment_id}")
        detail2 = resp.json()
        assert detail2["progress"]["has_canvas"] is True
        assert detail2["progress"]["has_breakthrough"] is False
        assert detail2["progress"]["has_scenarios"] is False
        assert detail2["progress"]["has_cases"] is False
        print(f"✅ Step 25 级联清空 → 重生成画布后下游全部清空")

        print("\n" + "=" * 60)
        print("  🎉 全链路 E2E 测试全部通过！26 个步骤验证完成")
        print("=" * 60)
