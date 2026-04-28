import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.assessment import Assessment
from app.models.canvas_diagnosis import CanvasDiagnosis
from app.models.case_recommendation import CaseRecommendation
from app.models.generated_report import GeneratedReport
from app.models.scenario_recommendation import ScenarioRecommendation
from app.schemas.assessment import (
    AssessmentCanvasResponse,
    AssessmentCaseResponse,
    AssessmentCreateRequest,
    AssessmentDetailResponse,
    AssessmentInputSnapshot,
    AssessmentProfileResponse,
    AssessmentProgress,
    AssessmentResponse,
    AssessmentScenarioRecommendationResponse,
    BusinessModelCanvasResult,
    CanvasDiagnosisResult,
    CaseMatchItem,
    CaseRecommendationResult,
    CompanyProfileResult,
    ReportContextResponse,
    ReportDocumentResponse,
    ScenarioRecommendationItem,
    ScenarioRecommendationResult,
)
from app.services.case_matcher import CaseMatcher
from app.services.llm_client import LLMClient
from app.services.report_builder import ReportBuilder
from app.services.report_service import ReportService
from app.services.scenario_recommender import ScenarioRecommender

router = APIRouter(prefix="/api/assessments", tags=["assessments"])

REPORT_OUTLINE = [
    "企业基本画像",
    "当前商业模式画布诊断",
    "AI 成熟度评估",
    "高优先级 AI 提效场景",
    "推荐场景详细规划",
    "差异化竞争力设计",
    "参考案例与启示",
    "三阶段 AI 创新路线图",
    "90 天行动计划",
    "风险与阻力",
    "讲师点评区",
]


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    assessment = Assessment(**payload.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return AssessmentResponse.model_validate(assessment, from_attributes=True)


@router.get(
    "/{assessment_id}",
    response_model=AssessmentDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_assessment_detail(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentDetailResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    report_service = ReportService()
    profile = _load_profile_from_assessment(assessment)
    canvas = _load_canvas_diagnosis(db, assessment_id)
    scenarios = _load_scenario_recommendation(db, assessment_id)
    cases = _load_case_recommendation(db, assessment_id)
    report_summary = report_service.get_report_summary_by_assessment(db, assessment_id)

    return AssessmentDetailResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        company_profile=profile,
        canvas_diagnosis=canvas,
        scenario_recommendation=scenarios,
        case_recommendation=cases,
        generated_report=report_summary,
        progress=_build_progress(profile, canvas, scenarios, cases, report_summary),
    )


@router.get(
    "/{assessment_id}/report-context",
    response_model=ReportContextResponse,
    status_code=status.HTTP_200_OK,
)
def get_report_context(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> ReportContextResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    profile, canvas, scenarios = _require_report_prerequisites(db, assessment)

    return ReportContextResponse(
        assessment_id=assessment.id,
        company_input=_build_assessment_input_snapshot(assessment),
        company_profile=profile,
        canvas_diagnosis=canvas,
        top_scenarios=scenarios.top_scenarios,
        report_outline=REPORT_OUTLINE,
    )


@router.post(
    "/{assessment_id}/profile",
    response_model=AssessmentProfileResponse,
    status_code=status.HTTP_200_OK,
)
def generate_profile(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentProfileResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    profile, generation_mode = _generate_and_store_profile(db, assessment)

    return AssessmentProfileResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        generation_mode=generation_mode,
        profile=profile,
    )


@router.post(
    "/{assessment_id}/canvas",
    response_model=AssessmentCanvasResponse,
    status_code=status.HTTP_200_OK,
)
def generate_canvas(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentCanvasResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    profile, _ = _ensure_profile(db, assessment)
    llm_client = LLMClient()
    canvas_result, generation_mode = llm_client.generate_business_model_canvas(
        assessment,
        profile,
    )
    stored_canvas = _upsert_canvas_diagnosis(
        db=db,
        assessment_id=assessment.id,
        canvas_result=canvas_result,
        generation_mode=generation_mode,
    )

    return AssessmentCanvasResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        canvas_diagnosis=stored_canvas,
    )


@router.post(
    "/{assessment_id}/scenarios",
    response_model=AssessmentScenarioRecommendationResponse,
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/{assessment_id}/scenario-recommendations",
    response_model=AssessmentScenarioRecommendationResponse,
    status_code=status.HTTP_200_OK,
    deprecated=True,
)
def recommend_scenarios(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentScenarioRecommendationResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    profile = _load_profile_from_assessment(assessment)
    recommender = ScenarioRecommender()
    top_recommendations, evaluated_count = recommender.recommend(assessment, profile)
    stored_scenarios = _upsert_scenario_recommendation(
        db=db,
        assessment_id=assessment.id,
        evaluated_count=evaluated_count,
        top_scenarios=top_recommendations,
    )

    return AssessmentScenarioRecommendationResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        scenario_recommendation=stored_scenarios,
    )


@router.post(
    "/{assessment_id}/cases",
    response_model=AssessmentCaseResponse,
    status_code=status.HTTP_200_OK,
)
def match_cases(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentCaseResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    profile = _require_profile(assessment)
    canvas = _require_canvas(db, assessment_id)
    scenarios = _require_scenarios(db, assessment_id)
    stored_cases = _match_and_store_cases(db, assessment, profile, canvas, scenarios)

    return AssessmentCaseResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        case_recommendation=stored_cases,
    )


@router.post(
    "/{assessment_id}/report",
    response_model=ReportDocumentResponse,
    status_code=status.HTTP_200_OK,
)
def generate_report(
    assessment_id: str,
    mode: str = "template",
    db: Session = Depends(get_db),
) -> ReportDocumentResponse:
    """Generate report with specified mode.

    Args:
        mode: "template" (default), "llm", or "template_fallback"
            - template: Always use template-based generation
            - llm: Use LLM deep writing, fallback to template if LLM unavailable
            - template_fallback: Prefer template with LLM enhancement when available
    """
    from app.services.llm_report_writer import LLMReportWriter

    assessment = _get_assessment_or_404(db, assessment_id)
    profile, canvas, scenarios = _require_report_prerequisites(db, assessment)

    cases = _load_case_recommendation(db, assessment_id)
    if cases is None:
        cases = _match_and_store_cases(db, assessment, profile, canvas, scenarios)

    # Validate mode
    valid_modes = ("template", "llm", "template_fallback")
    if mode not in valid_modes:
        mode = "template"

    # Use LLMReportWriter which handles fallback logic
    llm_writer = LLMReportWriter()
    report_data, metadata = llm_writer.build(
        assessment=assessment,
        profile=profile,
        canvas_diagnosis=canvas,
        scenario_recommendation=scenarios,
        case_recommendation=cases,
        mode=mode,
    )

    return ReportService().save_report(
        db=db,
        assessment_id=assessment.id,
        report_data=report_data,
        generation_mode=metadata.get("generation_mode", "template"),
        metadata=metadata,
    )


def _get_assessment_or_404(db: Session, assessment_id: str) -> Assessment:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )
    return assessment


def _build_assessment_input_snapshot(
    assessment: Assessment,
) -> AssessmentInputSnapshot:
    return AssessmentInputSnapshot(
        company_name=assessment.company_name,
        industry=assessment.industry,
        company_size=assessment.company_size,
        region=assessment.region,
        annual_revenue_range=assessment.annual_revenue_range,
        core_products=assessment.core_products,
        target_customers=assessment.target_customers,
        current_challenges=assessment.current_challenges,
        ai_goals=assessment.ai_goals,
        available_data=assessment.available_data,
        notes=assessment.notes,
    )


def _parse_json_payload(payload: str, model_class, detail_message: str):
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_message,
        ) from exc

    try:
        return model_class.model_validate(raw)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_message,
        ) from exc


def _parse_json_raw(payload: str, detail_message: str):
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_message,
        ) from exc


def _parse_json_string_list(payload: str, detail_message: str) -> list[str]:
    raw = _parse_json_raw(payload, detail_message)
    if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_message,
        )
    return raw


def _load_profile_from_assessment(
    assessment: Assessment,
) -> CompanyProfileResult | None:
    if not assessment.profile_payload:
        return None
    return _parse_json_payload(
        assessment.profile_payload,
        CompanyProfileResult,
        "Failed to parse stored company profile for this assessment.",
    )


def _load_canvas_diagnosis(
    db: Session,
    assessment_id: str,
) -> CanvasDiagnosisResult | None:
    record = db.scalar(
        select(CanvasDiagnosis).where(CanvasDiagnosis.assessment_id == assessment_id)
    )
    if record is None:
        return None

    return CanvasDiagnosisResult(
        generation_mode=record.generation_mode,
        overall_score=record.overall_score,
        weakest_blocks=_parse_json_string_list(
            record.weakest_blocks,
            "Failed to parse stored weakest canvas blocks for this assessment.",
        ),
        recommended_focus=_parse_json_string_list(
            record.recommended_focus,
            "Failed to parse stored recommended focus for this assessment.",
        ),
        canvas=_parse_json_payload(
            record.canvas_json,
            BusinessModelCanvasResult,
            "Failed to parse stored canvas diagnosis for this assessment.",
        ),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _load_scenario_recommendation(
    db: Session,
    assessment_id: str,
) -> ScenarioRecommendationResult | None:
    record = db.scalar(
        select(ScenarioRecommendation).where(
            ScenarioRecommendation.assessment_id == assessment_id
        )
    )
    if record is None:
        return None

    raw_top_scenarios = _parse_json_raw(
        record.scenario_json,
        "Failed to parse stored scenario recommendation for this assessment.",
    )
    _parse_json_string_list(
        record.top_scenarios,
        "Failed to parse stored top scenario names for this assessment.",
    )
    if not isinstance(raw_top_scenarios, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse stored scenario recommendation for this assessment.",
        )

    try:
        validated_scenarios = [
            ScenarioRecommendationItem.model_validate(item)
            for item in raw_top_scenarios
        ]
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse stored scenario recommendation for this assessment.",
        ) from exc

    return ScenarioRecommendationResult(
        scoring_method=record.scoring_method,
        evaluated_count=record.evaluated_count,
        top_scenarios=validated_scenarios,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _load_case_recommendation(
    db: Session,
    assessment_id: str,
) -> CaseRecommendationResult | None:
    record = db.scalar(
        select(CaseRecommendation).where(
            CaseRecommendation.assessment_id == assessment_id
        )
    )
    if record is None:
        return None

    raw_top_cases = _parse_json_raw(
        record.case_json,
        "Failed to parse stored case recommendation for this assessment.",
    )
    _parse_json_string_list(
        record.top_cases,
        "Failed to parse stored top case titles for this assessment.",
    )
    if not isinstance(raw_top_cases, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse stored case recommendation for this assessment.",
        )

    try:
        validated_cases = [CaseMatchItem.model_validate(item) for item in raw_top_cases]
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse stored case recommendation for this assessment.",
        ) from exc

    return CaseRecommendationResult(
        scoring_method=record.scoring_method,
        evaluated_count=record.evaluated_count,
        top_cases=validated_cases,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _require_profile(assessment: Assessment) -> CompanyProfileResult:
    profile = _load_profile_from_assessment(assessment)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile has not been generated for this assessment.",
        )
    return profile


def _require_canvas(db: Session, assessment_id: str) -> CanvasDiagnosisResult:
    canvas = _load_canvas_diagnosis(db, assessment_id)
    if canvas is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Canvas diagnosis has not been generated for this assessment.",
        )
    return canvas


def _require_scenarios(
    db: Session,
    assessment_id: str,
) -> ScenarioRecommendationResult:
    scenarios = _load_scenario_recommendation(db, assessment_id)
    if scenarios is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scenario recommendation has not been generated for this assessment.",
        )
    return scenarios


def _require_report_prerequisites(
    db: Session,
    assessment: Assessment,
) -> tuple[
    CompanyProfileResult,
    CanvasDiagnosisResult,
    ScenarioRecommendationResult,
]:
    profile = _load_profile_from_assessment(assessment)
    canvas = _load_canvas_diagnosis(db, assessment.id)
    scenarios = _load_scenario_recommendation(db, assessment.id)

    missing_steps: list[str] = []
    if profile is None:
        missing_steps.append("company profile")
    if canvas is None:
        missing_steps.append("canvas diagnosis")
    if scenarios is None:
        missing_steps.append("scenario recommendation")

    if missing_steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Report generation requires completed steps before continuing: "
                + ", ".join(missing_steps)
                + ". Generate them from the assessment workbench first."
            ),
        )

    return profile, canvas, scenarios


def _ensure_profile(
    db: Session,
    assessment: Assessment,
) -> tuple[CompanyProfileResult, str]:
    existing_profile = _load_profile_from_assessment(assessment)
    if existing_profile is not None:
        return existing_profile, assessment.profile_generation_mode or "mock"
    return _generate_and_store_profile(db, assessment)


def _generate_and_store_profile(
    db: Session,
    assessment: Assessment,
) -> tuple[CompanyProfileResult, str]:
    llm_client = LLMClient()
    profile, generation_mode = llm_client.generate_company_profile(assessment)

    assessment.profile_payload = json.dumps(profile.model_dump(), ensure_ascii=False)
    assessment.profile_generation_mode = generation_mode
    assessment.profile_generated_at = datetime.now(timezone.utc)

    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    _clear_canvas_and_below(db, assessment.id)

    return profile, generation_mode


def _calculate_canvas_metadata(
    canvas_result: BusinessModelCanvasResult,
) -> tuple[int, list[str], list[str]]:
    block_scores: list[tuple[str, int, str]] = []
    for block in canvas_result.blocks:
        score = 10
        for content in (
            block.current_state,
            block.diagnosis,
            block.ai_opportunity,
            block.missing_information,
        ):
            if "待补充" in content:
                score -= 2
            if "缺失" in content or "不完整" in content or "不足" in content:
                score -= 1
        block_scores.append((block.title, max(3, score), block.ai_opportunity))

    if not block_scores:
        return 0, [], []

    total_score = sum(item[1] for item in block_scores)
    overall_score = max(0, min(100, round(total_score / (len(block_scores) * 10) * 100)))
    weakest = sorted(block_scores, key=lambda item: item[1])[:3]
    weakest_blocks = [item[0] for item in weakest]
    recommended_focus = [f"{item[0]}：{item[2]}" for item in weakest]
    return overall_score, weakest_blocks, recommended_focus


def _upsert_canvas_diagnosis(
    db: Session,
    assessment_id: str,
    canvas_result: BusinessModelCanvasResult,
    generation_mode: str,
) -> CanvasDiagnosisResult:
    overall_score, weakest_blocks, recommended_focus = _calculate_canvas_metadata(
        canvas_result
    )
    record = db.scalar(
        select(CanvasDiagnosis).where(CanvasDiagnosis.assessment_id == assessment_id)
    )
    if record is None:
        record = CanvasDiagnosis(
            assessment_id=assessment_id,
            generation_mode=generation_mode,
            canvas_json="",
            overall_score=overall_score,
            weakest_blocks="[]",
            recommended_focus="[]",
        )

    record.generation_mode = generation_mode
    record.canvas_json = json.dumps(canvas_result.model_dump(), ensure_ascii=False)
    record.overall_score = overall_score
    record.weakest_blocks = json.dumps(weakest_blocks, ensure_ascii=False)
    record.recommended_focus = json.dumps(recommended_focus, ensure_ascii=False)

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_scenarios_and_below(db, assessment_id)

    return CanvasDiagnosisResult(
        generation_mode=record.generation_mode,  # type: ignore[arg-type]
        overall_score=record.overall_score,
        weakest_blocks=weakest_blocks,
        recommended_focus=recommended_focus,
        canvas=canvas_result,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _upsert_scenario_recommendation(
    db: Session,
    assessment_id: str,
    evaluated_count: int,
    top_scenarios: list[ScenarioRecommendationItem],
) -> ScenarioRecommendationResult:
    record = db.scalar(
        select(ScenarioRecommendation).where(
            ScenarioRecommendation.assessment_id == assessment_id
        )
    )
    if record is None:
        record = ScenarioRecommendation(
            assessment_id=assessment_id,
            scoring_method="rule_based_v1",
            evaluated_count=evaluated_count,
            scenario_json="[]",
            top_scenarios="[]",
        )

    record.scoring_method = "rule_based_v1"
    record.evaluated_count = evaluated_count
    record.scenario_json = json.dumps(
        [item.model_dump() for item in top_scenarios],
        ensure_ascii=False,
    )
    record.top_scenarios = json.dumps(
        [item.name for item in top_scenarios],
        ensure_ascii=False,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_cases_and_reports(db, assessment_id)

    return ScenarioRecommendationResult(
        scoring_method="rule_based_v1",
        evaluated_count=evaluated_count,
        top_scenarios=top_scenarios,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _match_and_store_cases(
    db: Session,
    assessment: Assessment,
    profile: CompanyProfileResult,
    canvas: CanvasDiagnosisResult,
    scenarios: ScenarioRecommendationResult,
) -> CaseRecommendationResult:
    matcher = CaseMatcher()
    top_cases, evaluated_count = matcher.match(
        assessment=assessment,
        profile=profile,
        canvas_diagnosis=canvas,
        scenario_recommendation=scenarios,
    )
    return _upsert_case_recommendation(
        db=db,
        assessment_id=assessment.id,
        evaluated_count=evaluated_count,
        top_cases=top_cases,
    )


def _upsert_case_recommendation(
    db: Session,
    assessment_id: str,
    evaluated_count: int,
    top_cases: list[CaseMatchItem],
) -> CaseRecommendationResult:
    record = db.scalar(
        select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)
    )
    if record is None:
        record = CaseRecommendation(
            assessment_id=assessment_id,
            scoring_method="rule_based_case_v1",
            evaluated_count=evaluated_count,
            case_json="[]",
            top_cases="[]",
        )

    record.scoring_method = "rule_based_case_v1"
    record.evaluated_count = evaluated_count
    record.case_json = json.dumps(
        [item.model_dump() for item in top_cases],
        ensure_ascii=False,
    )
    record.top_cases = json.dumps([item.title for item in top_cases], ensure_ascii=False)

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_reports_only(db, assessment_id)

    return CaseRecommendationResult(
        scoring_method="rule_based_case_v1",
        evaluated_count=evaluated_count,
        top_cases=top_cases,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _build_progress(
    profile: CompanyProfileResult | None,
    canvas: CanvasDiagnosisResult | None,
    scenarios: ScenarioRecommendationResult | None,
    cases: CaseRecommendationResult | None,
    report_summary,
) -> AssessmentProgress:
    has_profile = profile is not None
    has_canvas = canvas is not None
    has_scenarios = scenarios is not None
    has_cases = cases is not None
    has_report = report_summary is not None
    return AssessmentProgress(
        has_profile=has_profile,
        has_canvas=has_canvas,
        has_scenarios=has_scenarios,
        has_cases=has_cases,
        has_report=has_report,
        ready_for_report=has_profile and has_canvas and has_scenarios,
    )


def _clear_canvas_and_below(db: Session, assessment_id: str) -> None:
    _delete_records(
        db,
        [
            db.scalar(select(CanvasDiagnosis).where(CanvasDiagnosis.assessment_id == assessment_id)),
            db.scalar(
                select(ScenarioRecommendation).where(
                    ScenarioRecommendation.assessment_id == assessment_id
                )
            ),
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_scenarios_and_below(db: Session, assessment_id: str) -> None:
    _delete_records(
        db,
        [
            db.scalar(
                select(ScenarioRecommendation).where(
                    ScenarioRecommendation.assessment_id == assessment_id
                )
            ),
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_cases_and_reports(db: Session, assessment_id: str) -> None:
    _delete_records(
        db,
        [
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_reports_only(db: Session, assessment_id: str) -> None:
    _delete_records(
        db,
        [db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id))],
    )


def _delete_records(db: Session, records: list[object | None]) -> None:
    changed = False
    for record in records:
        if record is not None:
            db.delete(record)
            changed = True

    if changed:
        db.commit()
