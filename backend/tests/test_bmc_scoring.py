"""BMC 三维突破要素评分 — 算法验证测试"""

from app.services.bmc_scoring_service import BMCScoringService
from app.schemas.bmc_scoring import ModuleScoreInput


def test_calculate_cr_case():
    """产品文档 4.3 节案例：CR pain=4.5, data=2.0, feasibility=3.5"""
    svc = BMCScoringService()
    raw, norm = svc.calculate_single(4.5, 2.0, 3.5)
    assert raw == 3.825
    assert norm == 53.4


def test_calculate_extremes():
    """边界值测试"""
    svc = BMCScoringService()
    # 最高分
    raw_max, norm_max = svc.calculate_single(5.0, 5.0, 5.0)
    assert raw_max == 6.25
    assert norm_max == 100.0

    # 最低分
    raw_min, norm_min = svc.calculate_single(1.0, 1.0, 1.0)
    assert raw_min == 1.05
    assert norm_min == 0.0


def test_zone_quickwin():
    svc = BMCScoringService()
    assert svc.get_zone(4.0, 4.0, 70.0) == "quickwin"
    assert svc.get_zone(5.0, 5.0, 90.0) == "quickwin"


def test_zone_strategic():
    svc = BMCScoringService()
    assert svc.get_zone(4.5, 2.0, 53.0) == "strategic"
    assert svc.get_zone(4.0, 3.0, 55.0) == "strategic"


def test_zone_longterm():
    svc = BMCScoringService()
    assert svc.get_zone(3.0, 4.0, 45.0) == "longterm"


def test_zone_hold():
    svc = BMCScoringService()
    assert svc.get_zone(2.5, 2.0, 30.0) == "hold"


def test_veto_feasibility():
    svc = BMCScoringService()
    veto, reason = svc.get_veto_status(4.0, 3.0, 1.0)
    assert veto == "blocked_feasibility"
    assert reason is not None


def test_veto_data_pain():
    svc = BMCScoringService()
    veto, reason = svc.get_veto_status(3.0, 1.0, 4.0)
    assert veto == "blocked_data_pain"


def test_veto_pain_low():
    svc = BMCScoringService()
    veto, reason = svc.get_veto_status(2.0, 3.0, 3.0)
    assert veto == "not_recommended"


def test_evaluate_all():
    svc = BMCScoringService()
    modules = [
        ModuleScoreInput(key="customer_relationships", pain=4.5, data=2.0, feasibility=3.5),
        ModuleScoreInput(key="key_activities", pain=4.5, data=3.5, feasibility=4.0),
        ModuleScoreInput(key="key_resources", pain=4.0, data=2.5, feasibility=3.0),
        ModuleScoreInput(key="value_propositions", pain=3.0, data=3.0, feasibility=3.0),
        ModuleScoreInput(key="channels", pain=3.0, data=3.5, feasibility=3.5),
        ModuleScoreInput(key="customer_segments", pain=3.5, data=3.0, feasibility=3.5),
        ModuleScoreInput(key="revenue_streams", pain=3.0, data=3.0, feasibility=2.5),
        ModuleScoreInput(key="key_partnerships", pain=2.5, data=2.0, feasibility=3.0),
        ModuleScoreInput(key="cost_structure", pain=3.5, data=3.0, feasibility=3.5),
    ]
    result = svc.evaluate_all(modules, "test-001")
    assert len(result.top_3_keys) >= 2
    assert len(result.module_results) == 9


def test_complementarity_warning():
    svc = BMCScoringService()
    # 全部为内部效率类
    warning = svc.check_complementarity(
        ["key_activities", "key_resources", "cost_structure"]
    )
    assert warning is not None
    assert "内部效率" in warning

    # 混合
    no_warning = svc.check_complementarity(
        ["key_activities", "customer_relationships", "cost_structure"]
    )
    assert no_warning is None
