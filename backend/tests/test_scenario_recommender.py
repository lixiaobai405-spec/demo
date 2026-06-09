from app.models.assessment import Assessment
from app.models.user import User  # noqa: F401
from app.services.scenario_recommender import MAX_SCENARIO_POOL_SIZE, ScenarioRecommender


def _assessment() -> Assessment:
    return Assessment(
        company_name="测试零售企业",
        industry="零售",
        company_size="100-499人",
        region="华东",
        annual_revenue_range="5000万-1亿元",
        core_products="社区零售门店与会员服务",
        target_customers="周边社区会员",
        current_challenges="复购波动、回款风险、库存周转压力",
        ai_goals="提升复购、优化回款、提高门店补货效率",
        available_data="POS、会员交易、库存台账、回款记录",
        notes="希望优先选择可快速试点的 AI 场景",
    )


def test_priority_recommendation_populates_card_ready_fields() -> None:
    result = ScenarioRecommender().recommend_with_priority(
        assessment=_assessment(),
        direction_categories=["客户经营", "财务经营", "零售运营"],
        breakthrough_labels=["客户关系", "收入来源"],
        direction_titles=["智能会员运营", "现金流风险预警"],
    )

    assert len(result.top_scenarios) == 3
    for item in result.top_scenarios:
        assert item.positioning
        assert len(item.positioning) <= 15
        assert "围绕" not in item.positioning
        assert item.canvas_element
        assert item.canvas_key
        assert item.value_text
        assert "对应突破要素" not in item.value_text
        assert item.benefits
        assert all(benefit.text for benefit in item.benefits)
        assert all(benefit.canvas for benefit in item.benefits)
        assert item.resources
        assert all(resource.type for resource in item.resources)
        assert all(resource.label for resource in item.resources)
        assert all(resource.text for resource in item.resources)


def test_priority_recommendation_limits_scenario_pool_to_18() -> None:
    result = ScenarioRecommender().recommend_with_priority(
        assessment=_assessment(),
        direction_categories=["客户经营", "财务经营", "零售运营"],
        breakthrough_labels=["客户关系", "收入来源"],
        direction_titles=["智能会员运营", "现金流风险预警"],
    )

    assert result.evaluated_count == MAX_SCENARIO_POOL_SIZE
    assert result.all_scores is not None
    assert len(result.all_scores) == MAX_SCENARIO_POOL_SIZE
    assert {item.scenario_id for item in result.top_scenarios}.issubset(
        {item.scenario_id for item in result.all_scores},
    )


def test_build_template_summary_trims_repeated_direction_lead_in() -> None:
    recommender = ScenarioRecommender()
    summary = recommender._trim_summary_lead_in(
        "围绕“客户数据平台与智能分群推荐引擎、基于位置的个性化触达引擎、AI驱动的供应商发现与匹配引擎”，"
        "结合“关键资源、渠道通路、关键合作伙伴”，在财务经营环节布局“回款风险预警”，"
        "对账期异常、逾期概率和重点客户回款风险进行监控与预警。"
    )

    assert summary.startswith("在财务经营环节布局“回款风险预警”")
    assert "围绕“客户数据平台与智能分群推荐引擎" not in summary
