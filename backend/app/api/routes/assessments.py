import json
import logging
import threading
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.models.assessment import Assessment
from app.models.breakthrough_selection import BreakthroughSelection
from app.models.canvas_diagnosis import CanvasDiagnosis
from app.models.case_recommendation import CaseRecommendation
from app.models.competitiveness_analysis import CompetitivenessAnalysis
from app.models.direction_expansion import DirectionExpansion
from app.models.direction_selection import DirectionSelection
from app.models.endgame_analysis import EndgameAnalysis
from app.models.generated_report import GeneratedReport
from app.models.intake_session import AssessmentIntakeSession
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
    CanvasBlockResult,
    CanvasDiagnosisResult,
    CaseMatchItem,
    CaseRecommendationResult,
    CompanyProfileResult,
    ReportContextResponse,
    ReportDocumentResponse,
    ScenarioRecommendationItem,
    ScenarioRecommendationResult,
)
from app.schemas.breakthrough import (
    AssessmentBreakthroughResponse,
    BreakthroughRecommendationResult,
    BreakthroughSelectionRequest,
    BreakthroughSelectionResponse,
    BreakthroughElement,
    ELEMENT_KEY_TO_TITLE,
)
from app.schemas.direction import (
    AssessmentDirectionResponse,
    DirectionExpansionResult,
    DirectionSelectionRequest,
    DirectionSelectionResponse,
)
from app.schemas.competitiveness import (
    build_line_summary,
    CompetitivenessResponse,
    CompetitivenessResult,
)
from app.schemas.endgame import (
    EndgameResponse,
    EndgameResult,
)
from app.services.breakthrough_recommender import BreakthroughRecommender
from app.services.case_matcher import CaseMatcher
from app.services.competitiveness_analyzer import CompetitivenessAnalyzer
from app.services.direction_expansion_service import DirectionExpansionService
from app.services.endgame_analyzer import EndgameAnalyzer
from app.services.llm_client import LLMClient
from app.services.llm_enhancer import LLMEnhancer
from app.services.report_builder import ReportBuilder
from app.services.report_enrichment import ReportEnrichmentService
from app.services.report_service import ReportService
from app.services.scenario_recommender import ScenarioRecommender
from app.api.deps import get_current_user, require_instructor
from app.models.user import User
from app.schemas.assessment import AssessmentCardItem, AssessmentListResponse

router = APIRouter(prefix="/api/assessments", tags=["assessments"])

REPORT_OUTLINE = [
    "企业基本画像",
    "当前商业模式画布诊断",
    "突破要素",
    "创新方向延展",
    "AI 成熟度评估",
    "高优先级 AI 提效场景",
    "推荐场景详细规划",
    "差异化竞争力设计",
    "参考案例与启示",
    "三阶段 AI 创新路线图",
    "风险与阻力",
    "讲师点评区",
    "商业终局设计",
]


def _check_owner_or_instructor(
    assessment: Assessment, current_user: User
) -> None:
    if current_user.role == "instructor":
        return
    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此评估。",
        )


def _claim_orphaned_assessment_from_intake(
    db: Session,
    assessment: Assessment,
    current_user: User,
) -> Assessment:
    if current_user.role == "instructor" or assessment.user_id is not None:
        return assessment

    intake_session = (
        db.query(AssessmentIntakeSession)
        .filter(AssessmentIntakeSession.created_assessment_id == assessment.id)
        .order_by(AssessmentIntakeSession.created_at.desc())
        .first()
    )
    if intake_session is None:
        return assessment
    if intake_session.user_id not in (None, current_user.id):
        return assessment

    assessment.user_id = current_user.id
    db.add(assessment)
    if intake_session.user_id is None:
        intake_session.user_id = current_user.id
        db.add(intake_session)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResponse:
    assessment = Assessment(**payload.model_dump(), user_id=current_user.id)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return AssessmentResponse.model_validate(assessment, from_attributes=True)


@router.get("", response_model=AssessmentListResponse, status_code=status.HTTP_200_OK)
def list_assessments(
    search: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    industry: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentListResponse:
    query = db.query(Assessment)
    if current_user.role != "instructor":
        query = query.filter(Assessment.user_id == current_user.id)
    if search:
        query = query.filter(Assessment.company_name.ilike(f"%{search}%"))
    if date_from:
        query = query.filter(Assessment.created_at >= date_from)
    if date_to:
        query = query.filter(Assessment.created_at <= date_to)
    if industry:
        query = query.filter(Assessment.industry == industry)

    total = query.count()
    items = (
        query.order_by(Assessment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    card_items = []
    for a in items:
        has_report = db.query(GeneratedReport).filter(
            GeneratedReport.assessment_id == a.id
        ).count() > 0
        card_items.append(
            AssessmentCardItem(
                id=a.id,
                company_name=a.company_name,
                industry=a.industry,
                company_size=a.company_size,
                has_profile=a.has_profile,
                has_report=has_report,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
        )

    return AssessmentListResponse(
        items=card_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{assessment_id}",
    response_model=AssessmentDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_assessment_detail(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentDetailResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    assessment = _claim_orphaned_assessment_from_intake(db, assessment, current_user)
    _check_owner_or_instructor(assessment, current_user)
    report_service = ReportService()
    profile = _load_profile_from_assessment(assessment)
    canvas = _load_canvas_diagnosis(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id)
    scenarios = _load_scenario_recommendation(db, assessment_id)
    cases = _load_case_recommendation(db, assessment_id)
    report_summary = report_service.get_report_summary_by_assessment(db, assessment_id)
    direction_selection = _load_direction_selection(db, assessment_id)
    direction_expansion = _load_direction_expansion_result(db, assessment_id)
    competitiveness = _load_competitiveness_analysis(db, assessment_id)

    return AssessmentDetailResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        company_profile=profile,
        canvas_diagnosis=canvas,
        breakthrough_selection=breakthrough_keys,
        direction_expansion=direction_expansion,
        direction_selection=direction_selection,
        scenario_recommendation=scenarios,
        case_recommendation=cases,
        generated_report=report_summary,
        progress=_build_progress(
            profile, canvas, breakthrough_keys, scenarios, cases, report_summary,
            direction_selection, competitiveness,
        ),
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
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id) or []

    return ReportContextResponse(
        assessment_id=assessment.id,
        company_input=_build_assessment_input_snapshot(assessment),
        company_profile=profile,
        canvas_diagnosis=canvas,
        selected_breakthrough_elements=breakthrough_keys,
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


class UpdateCanvasBlockRequest(BaseModel):
    key: str
    title: str
    current_state: str
    diagnosis: str
    ai_opportunity: str


class UpdateCanvasRequest(BaseModel):
    overall_summary: str
    blocks: list[UpdateCanvasBlockRequest]


@router.put(
    "/{assessment_id}/canvas",
    response_model=AssessmentCanvasResponse,
    status_code=status.HTTP_200_OK,
)
def update_canvas(
    assessment_id: str,
    payload: UpdateCanvasRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentCanvasResponse:
    """手动更新画布诊断内容，并清除下游数据以便基于新画布重新生成。"""
    from app.models.breakthrough_selection import BreakthroughSelection
    from app.models.direction_expansion import DirectionExpansion
    from app.models.scenario_recommendation import ScenarioRecommendation

    assessment = _get_assessment_or_404(db, assessment_id)

    # Build updated canvas result from payload
    canvas_blocks = [
        CanvasBlockResult(
            key=b.key,
            title=b.title,
            current_state=b.current_state,
            diagnosis=b.diagnosis,
            ai_opportunity=b.ai_opportunity,
            missing_information="",
        )
        for b in payload.blocks
    ]
    canvas_result = BusinessModelCanvasResult(
        overall_summary=payload.overall_summary,
        blocks=canvas_blocks,
    )
    stored_canvas = _upsert_canvas_diagnosis(
        db=db,
        assessment_id=assessment.id,
        canvas_result=canvas_result,
        generation_mode="manual_edit",
    )

    # Clear downstream — breakthrough, directions, direction selection, scenarios
    from app.models.direction_selection import DirectionSelection as _DS
    for model_cls in [BreakthroughSelection, DirectionExpansion, _DS, ScenarioRecommendation]:
        record = db.scalar(
            select(model_cls).where(model_cls.assessment_id == assessment_id)
        )
        if record is not None:
            db.delete(record)
    db.commit()

    return AssessmentCanvasResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        canvas_diagnosis=stored_canvas,
    )


@router.post(
    "/{assessment_id}/breakthrough/recommend",
    response_model=AssessmentBreakthroughResponse,
    status_code=status.HTTP_200_OK,
)
def recommend_breakthrough(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentBreakthroughResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)

    recommendation = None
    enhancer = LLMEnhancer()
    llm_result = enhancer.enhance_breakthrough(canvas, assessment_id=assessment_id)
    if llm_result is not None:
        recommendation = llm_result
    else:
        recommender = BreakthroughRecommender()
        recommendation = recommender.recommend(canvas)

    existing = _load_breakthrough_selection(db, assessment_id)
    selection_response = None
    if existing is not None:
        selection_response = _build_breakthrough_selection_response(existing)

    return AssessmentBreakthroughResponse(
        assessment_id=assessment.id,
        breakthrough_recommendation=recommendation,
        breakthrough_selection=selection_response,
    )


@router.post(
    "/{assessment_id}/breakthrough/select",
    response_model=BreakthroughSelectionResponse,
    status_code=status.HTTP_200_OK,
)
def select_breakthrough(
    assessment_id: str,
    payload: BreakthroughSelectionRequest,
    db: Session = Depends(get_db),
) -> BreakthroughSelectionResponse:
    _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    recommender = BreakthroughRecommender()
    recommendation = recommender.recommend(canvas)

    selected_elements = _resolve_selected_elements(payload.selected_keys, recommendation)

    record = _upsert_breakthrough_selection(
        db=db,
        assessment_id=assessment_id,
        selection_mode=payload.selection_mode,
        recommended_elements=recommendation.elements,
        selected_elements=selected_elements,
    )

    # 清除下游：突破要素是分支结点，改变后方向、场景等需重新生成
    from app.models.direction_expansion import DirectionExpansion
    from app.models.direction_selection import DirectionSelection
    from app.models.scenario_recommendation import ScenarioRecommendation
    for model_cls in [DirectionExpansion, DirectionSelection, ScenarioRecommendation]:
        downstream = db.scalar(
            select(model_cls).where(model_cls.assessment_id == assessment_id)
        )
        if downstream is not None:
            db.delete(downstream)
    db.commit()

    return _build_breakthrough_selection_response(record)


@router.get(
    "/{assessment_id}/breakthrough",
    response_model=AssessmentBreakthroughResponse,
    status_code=status.HTTP_200_OK,
)
def get_breakthrough(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentBreakthroughResponse:
    _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    recommender = BreakthroughRecommender()
    recommendation = recommender.recommend(canvas)

    existing = _load_breakthrough_selection(db, assessment_id)
    selection_response = None
    if existing is not None:
        selection_response = _build_breakthrough_selection_response(existing)

    return AssessmentBreakthroughResponse(
        assessment_id=assessment_id,
        breakthrough_recommendation=recommendation,
        breakthrough_selection=selection_response,
    )


@router.post(
    "/{assessment_id}/directions/expand",
    response_model=AssessmentDirectionResponse,
    status_code=status.HTTP_200_OK,
)
def expand_directions(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentDirectionResponse:
    _get_assessment_or_404(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id)
    if not breakthrough_keys or len(breakthrough_keys) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先选择突破要素，再展开创新方向。",
        )

    canvas = _require_canvas(db, assessment_id)

    # Phase 1: Instant rule-based expansion
    service = DirectionExpansionService()
    expansion = service.expand(breakthrough_keys)

    # Persist with pending LLM status
    record = _upsert_direction_expansion(
        db=db,
        assessment_id=assessment_id,
        expansion=expansion,
    )
    db.commit()

    # Phase 2: Background LLM enhancement (daemon thread, non-blocking)
    enhancer = LLMEnhancer()
    if enhancer._is_live_mode():
        canvas_json = canvas.model_dump_json()
        thread = threading.Thread(
            target=_background_enhance_directions,
            args=(assessment_id, canvas_json, breakthrough_keys),
            daemon=True,
        )
        thread.start()
    else:
        record.llm_status = "completed"
        db.commit()
        db.refresh(record)

    # Set llm_status on the response expansion
    expansion.llm_status = record.llm_status

    selection_response = _load_direction_selection(db, assessment_id)

    return AssessmentDirectionResponse(
        assessment_id=assessment_id,
        direction_expansion=expansion,
        direction_selection=selection_response,
    )


@router.post(
    "/{assessment_id}/directions/select",
    response_model=DirectionSelectionResponse,
    status_code=status.HTTP_200_OK,
)
def select_directions(
    assessment_id: str,
    payload: DirectionSelectionRequest,
    db: Session = Depends(get_db),
) -> DirectionSelectionResponse:
    _get_assessment_or_404(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id)
    if not breakthrough_keys or len(breakthrough_keys) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先选择突破要素，再确认创新方向。",
        )

    service = DirectionExpansionService()
    selected_directions, _ = _resolve_selected_directions_for_assessment(
        db,
        assessment_id,
        payload.selected_direction_ids,
    )
    if not selected_directions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择当前创新方向列表中的有效方向。",
        )

    record = _upsert_direction_selection(
        db=db,
        assessment_id=assessment_id,
        direction_ids=[direction.direction_id for direction in selected_directions],
        selected_directions=selected_directions,
    )

    return service.build_selection_response(record, selected_directions)


@router.get(
    "/{assessment_id}/directions",
    response_model=AssessmentDirectionResponse,
    status_code=status.HTTP_200_OK,
)
def get_directions(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentDirectionResponse:
    _get_assessment_or_404(db, assessment_id)
    service = DirectionExpansionService()

    # Read from persisted expansion record
    record = _load_direction_expansion(db, assessment_id)
    if record is not None:
        expansion = DirectionExpansionResult.model_validate_json(record.expansion_json)
        expansion.generation_mode = record.generation_mode  # type: ignore[assignment]
        expansion.llm_status = record.llm_status  # type: ignore[assignment]
    else:
        # Fallback: re-run rule-based for backwards compatibility
        breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id) or []
        expansion = service.expand(breakthrough_keys) if breakthrough_keys else DirectionExpansionResult(
            generation_mode="rule_based",
            elements=[],
            total_suggestions=0,
        )

    selection_response = _load_direction_selection(db, assessment_id)

    return AssessmentDirectionResponse(
        assessment_id=assessment_id,
        direction_expansion=expansion,
        direction_selection=selection_response,
    )


@router.post(
    "/{assessment_id}/competitiveness/generate",
    response_model=CompetitivenessResponse,
    status_code=status.HTTP_200_OK,
)
def generate_competitiveness(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> CompetitivenessResponse:
    _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id)
    if not breakthrough_keys or len(breakthrough_keys) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先选择突破要素，再生成竞争力分析。",
        )

    selected_directions = _load_selected_directions(db, assessment_id)

    result = None
    enhancer = LLMEnhancer()
    llm_result = enhancer.enhance_competitiveness(canvas, breakthrough_keys, selected_directions)
    if llm_result is not None:
        result = llm_result
    else:
        analyzer = CompetitivenessAnalyzer()
        result = analyzer.analyze(canvas, breakthrough_keys, selected_directions)

    record = _upsert_competitiveness_analysis(
        db=db,
        assessment_id=assessment_id,
        result=result,
    )

    return CompetitivenessResponse(
        assessment_id=record.assessment_id,
        result=result,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get(
    "/{assessment_id}/competitiveness",
    response_model=CompetitivenessResponse,
    status_code=status.HTTP_200_OK,
)
def get_competitiveness(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> CompetitivenessResponse:
    _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id) or []
    selected_directions = _load_selected_directions(db, assessment_id)

    existing = _load_competitiveness_analysis(db, assessment_id)
    if existing is not None:
        result = _build_competitiveness_result_from_record(existing)
        return CompetitivenessResponse(
            assessment_id=existing.assessment_id,
            result=result,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )

    analyzer = CompetitivenessAnalyzer()
    result = analyzer.analyze(canvas, breakthrough_keys, selected_directions)
    return CompetitivenessResponse(
        assessment_id=assessment_id,
        result=result,
        created_at=None,
        updated_at=None,
    )


@router.post(
    "/{assessment_id}/endgame/generate",
    response_model=EndgameResponse,
    status_code=status.HTTP_200_OK,
)
def generate_endgame(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> EndgameResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id) or []
    selected_directions = _load_selected_directions(db, assessment_id)

    competitiveness_result = None
    comp_record = _load_competitiveness_analysis(db, assessment_id)
    if comp_record is not None:
        competitiveness_result = _build_competitiveness_result_from_record(comp_record)

    analyzer = EndgameAnalyzer()
    result = analyzer.analyze(
        industry=assessment.industry,
        canvas_diagnosis=canvas,
        breakthrough_keys=breakthrough_keys,
        selected_directions=selected_directions,
        competitiveness_result=competitiveness_result,
    )

    record = _upsert_endgame_analysis(db, assessment_id, result)

    return EndgameResponse(
        assessment_id=record.assessment_id,
        result=result,
        created_at=record.created_at.isoformat() if record.created_at else None,
        updated_at=record.updated_at.isoformat() if record.updated_at else None,
    )


@router.get(
    "/{assessment_id}/endgame",
    response_model=EndgameResponse,
    status_code=status.HTTP_200_OK,
)
def get_endgame(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> EndgameResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    canvas = _require_canvas(db, assessment_id)
    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id) or []
    selected_directions = _load_selected_directions(db, assessment_id)

    existing = _load_endgame_analysis(db, assessment_id)
    if existing is not None:
        result = _build_endgame_result_from_record(existing)
        return EndgameResponse(
            assessment_id=existing.assessment_id,
            result=result,
            created_at=existing.created_at.isoformat() if existing.created_at else None,
            updated_at=existing.updated_at.isoformat() if existing.updated_at else None,
        )

    competitiveness_result = None
    comp_record = _load_competitiveness_analysis(db, assessment_id)
    if comp_record is not None:
        competitiveness_result = _build_competitiveness_result_from_record(comp_record)

    analyzer = EndgameAnalyzer()
    result = analyzer.analyze(
        industry=assessment.industry,
        canvas_diagnosis=canvas,
        breakthrough_keys=breakthrough_keys,
        selected_directions=selected_directions,
        competitiveness_result=competitiveness_result,
    )
    return EndgameResponse(
        assessment_id=assessment_id,
        result=result,
        created_at=None,
        updated_at=None,
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
    mode: str | None = None,
    db: Session = Depends(get_db),
) -> AssessmentScenarioRecommendationResponse:
    """生成 Top 3 AI 场景推荐。

    默认使用四象限优先级评分算法（four_quadrant_v1）。
    可通过 ?mode=legacy 回退到旧关键词评分算法（rule_based_v1）。
    """
    assessment = _get_assessment_or_404(db, assessment_id)
    profile = _load_profile_from_assessment(assessment)
    direction_categories = _load_direction_categories(db, assessment_id)
    recommender = ScenarioRecommender()

    if mode == "legacy":
        top_recommendations, evaluated_count = recommender.recommend(
            assessment, profile, direction_categories
        )
        stored_scenarios = _upsert_scenario_recommendation(
            db=db,
            assessment_id=assessment.id,
            evaluated_count=evaluated_count,
            top_scenarios=top_recommendations,
            scoring_method="rule_based_v1",
        )
    else:
        priority_result = recommender.recommend_with_priority(
            assessment, profile, direction_categories
        )
        stored_scenarios = _upsert_scenario_recommendation(
            db=db,
            assessment_id=assessment.id,
            evaluated_count=priority_result.evaluated_count,
            top_scenarios=priority_result.top_scenarios,
            scoring_method=priority_result.scoring_method,
        )

    return AssessmentScenarioRecommendationResponse(
        assessment=AssessmentResponse.model_validate(assessment, from_attributes=True),
        scenario_recommendation=stored_scenarios,
    )


@router.post(
    "/{assessment_id}/scenarios/priority",
    response_model=AssessmentScenarioRecommendationResponse,
    status_code=status.HTTP_200_OK,
)
def recommend_scenarios_with_priority(
    assessment_id: str,
    db: Session = Depends(get_db),
) -> AssessmentScenarioRecommendationResponse:
    """使用四象限优先级评分引擎推荐 Top 3 AI 场景。

    先通过关键词评分从 24 个预定义场景中筛选候选，再使用
    ScenePriorityScorer 计算每个场景的 QS/LPS/LPS_display，
    最终按梯队+LPS_final 排序返回 Top 3。

    输出每个场景附带的 priority_* 字段：
    - priority_structuredness_x / priority_complexity_y: X/Y 评分
    - priority_qs: 象限定位得分
    - priority_lps / priority_lps_display: 落地优先级及展示分
    - priority_quadrant: 象限归属
    - priority_tier: 推荐梯队 (1=自动化主战场, 2=AI优先区, 3=人机协作区)
    - priority_recommendation: 推荐话术模板
    """
    assessment = _get_assessment_or_404(db, assessment_id)
    profile = _load_profile_from_assessment(assessment)
    direction_categories = _load_direction_categories(db, assessment_id)
    recommender = ScenarioRecommender()
    priority_result = recommender.recommend_with_priority(
        assessment, profile, direction_categories
    )
    stored_scenarios = _upsert_scenario_recommendation(
        db=db,
        assessment_id=assessment.id,
        evaluated_count=priority_result.evaluated_count,
        top_scenarios=priority_result.top_scenarios,
        scoring_method=priority_result.scoring_method,
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

    breakthrough_keys = _load_breakthrough_selection_keys(db, assessment_id) or []
    direction_labels = _load_direction_labels(db, assessment_id)
    competitiveness_record = _load_competitiveness_analysis(db, assessment_id)
    competitiveness_result = _build_competitiveness_result_from_record(competitiveness_record) if competitiveness_record else None

    enrichment_service = ReportEnrichmentService()
    enrichment = enrichment_service.enrich(
        assessment=assessment,
        profile=profile,
        canvas=canvas,
        scenarios=scenarios,
        breakthrough_keys=breakthrough_keys,
        direction_labels=direction_labels,
        competitiveness_result=competitiveness_result,
    )

    endgame_record = _load_endgame_analysis(db, assessment_id)
    endgame_result = _build_endgame_result_from_record(endgame_record) if endgame_record else None

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
        breakthrough_keys=breakthrough_keys,
        direction_labels=direction_labels,
        competitiveness_result=competitiveness_result,
        enrichment_result=enrichment,
        endgame_result=endgame_result,
        mode=mode,
    )

    report_service = ReportService()
    response = report_service.save_report(
        db=db,
        assessment_id=assessment.id,
        report_data=report_data,
        generation_mode=metadata.get("generation_mode", "template"),
        metadata=metadata,
    )

    record = report_service.get_report_or_404(db, response.report_id)
    report_service.save_enrichment(db, record, enrichment)

    return response


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


def _load_breakthrough_selection(
    db: Session,
    assessment_id: str,
) -> BreakthroughSelection | None:
    return db.scalar(
        select(BreakthroughSelection).where(
            BreakthroughSelection.assessment_id == assessment_id
        )
    )


def _load_breakthrough_selection_keys(
    db: Session,
    assessment_id: str,
) -> list[str] | None:
    record = _load_breakthrough_selection(db, assessment_id)
    if record is None:
        return None
    return _parse_json_string_list(
        record.selected_elements_json,
        "Failed to parse stored breakthrough selection.",
    )


def _resolve_selected_elements(
    selected_keys: list[str],
    recommendation: BreakthroughRecommendationResult,
) -> list[BreakthroughElement]:
    element_map = {e.key: e for e in recommendation.elements}
    resolved: list[BreakthroughElement] = []
    for key in selected_keys:
        if key in element_map:
            resolved.append(element_map[key])
        else:
            resolved.append(
                BreakthroughElement(
                    key=key,
                    title=ELEMENT_KEY_TO_TITLE.get(key, key),
                    score=0,
                    reason="",
                    ai_opportunity="",
                )
            )
    return resolved


def _upsert_breakthrough_selection(
    db: Session,
    assessment_id: str,
    selection_mode: str,
    recommended_elements: list[BreakthroughElement],
    selected_elements: list[BreakthroughElement],
) -> BreakthroughSelection:
    record = _load_breakthrough_selection(db, assessment_id)
    if record is None:
        record = BreakthroughSelection(
            assessment_id=assessment_id,
            selection_mode=selection_mode,
            recommended_elements_json="[]",
            selected_elements_json="[]",
        )

    record.selection_mode = selection_mode
    record.recommended_elements_json = json.dumps(
        [e.model_dump() for e in recommended_elements], ensure_ascii=False
    )
    record.selected_elements_json = json.dumps(
        [e.key for e in selected_elements], ensure_ascii=False
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_directions_and_below(db, assessment_id)

    return record


def _build_breakthrough_selection_response(
    record: BreakthroughSelection,
) -> BreakthroughSelectionResponse:
    recommended = [
        BreakthroughElement.model_validate(item)
        for item in _parse_json_raw(
            record.recommended_elements_json,
            "Failed to parse breakthrough recommendation.",
        )
    ]

    selected_keys = _parse_json_string_list(
        record.selected_elements_json,
        "Failed to parse breakthrough selection.",
    )
    selected = [e for e in recommended if e.key in selected_keys]

    return BreakthroughSelectionResponse(
        assessment_id=record.assessment_id,
        selection_mode=record.selection_mode,
        recommended_elements=recommended,
        selected_elements=selected,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _load_direction_selection_record(
    db: Session,
    assessment_id: str,
) -> DirectionSelection | None:
    return db.scalar(
        select(DirectionSelection).where(
            DirectionSelection.assessment_id == assessment_id
        )
    )


def _load_direction_selection(
    db: Session,
    assessment_id: str,
) -> DirectionSelectionResponse | None:
    record = _load_direction_selection_record(db, assessment_id)
    if record is None:
        return None
    return _build_direction_selection_response(record)


def _load_direction_expansion_result(
    db: Session,
    assessment_id: str,
) -> DirectionExpansionResult | None:
    from app.schemas.direction import DirectionExpansionResult

    record = _load_direction_expansion(db, assessment_id)
    if record is None or not record.expansion_json:
        return None
    try:
        raw = json.loads(record.expansion_json)
        return DirectionExpansionResult.model_validate(raw)
    except Exception:
        return None


def _resolve_selected_directions_for_assessment(
    db: Session,
    assessment_id: str,
    direction_ids: list[str],
) -> tuple[list, list[str]]:
    """优先按当前 assessment 已保存的方向扩展结果解析选择，兼容增强后的自定义方向 ID。"""
    from app.schemas.direction import DirectionSuggestion

    expansion = _load_direction_expansion_result(db, assessment_id)
    if expansion is not None:
        suggestion_map = {
            suggestion.direction_id: suggestion
            for element in expansion.elements
            for suggestion in element.suggestions
        }
        selected = [
            suggestion_map[direction_id]
            for direction_id in direction_ids
            if direction_id in suggestion_map
        ]
        categories = list(
            dict.fromkeys(
                category
                for direction in selected
                for category in direction.related_scenario_categories
            )
        )
        return selected, categories

    service = DirectionExpansionService()
    return service.resolve_selected_directions(direction_ids)


def _load_direction_categories(
    db: Session,
    assessment_id: str,
) -> list[str] | None:
    from app.schemas.direction import DirectionSuggestion

    record = _load_direction_selection_record(db, assessment_id)
    if record is None:
        return None

    raw_directions = _parse_json_raw(
        record.directions_json,
        "Failed to parse direction selection for categories.",
    )
    categories = list(
        dict.fromkeys(
            category
            for item in raw_directions
            for category in (item.get("related_scenario_categories", []) if isinstance(item, dict) else getattr(item, "related_scenario_categories", []))
        )
    )
    return categories if categories else None


def _load_direction_labels(
    db: Session,
    assessment_id: str,
) -> list[str] | None:
    from app.schemas.direction import DirectionSuggestion

    record = _load_direction_selection_record(db, assessment_id)
    if record is None:
        return None

    raw_directions = _parse_json_raw(
        record.directions_json,
        "Failed to parse direction selection for labels.",
    )
    labels = [
        item.get("title", "") if isinstance(item, dict) else getattr(item, "title", "")
        for item in raw_directions
    ]
    labels = [l for l in labels if l]
    return labels if labels else None


def _upsert_direction_selection(
    db: Session,
    assessment_id: str,
    direction_ids: list[str],
    selected_directions,
) -> DirectionSelection:
    from app.schemas.direction import DirectionSuggestion

    record = _load_direction_selection_record(db, assessment_id)
    if record is None:
        record = DirectionSelection(
            assessment_id=assessment_id,
            generation_mode="rule_based",
            direction_ids_json="[]",
            directions_json="[]",
        )

    record.generation_mode = "rule_based"
    record.direction_ids_json = json.dumps(direction_ids, ensure_ascii=False)
    record.directions_json = json.dumps(
        [d.model_dump() if isinstance(d, DirectionSuggestion) else d for d in selected_directions],
        ensure_ascii=False,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_competitiveness_and_below(db, assessment_id)

    return record


def _build_direction_selection_response(
    record: DirectionSelection,
) -> DirectionSelectionResponse:
    from app.schemas.direction import DirectionSuggestion

    raw_directions = _parse_json_raw(
        record.directions_json,
        "Failed to parse direction selection.",
    )
    selected = [DirectionSuggestion.model_validate(item) for item in raw_directions]

    return DirectionSelectionResponse(
        assessment_id=record.assessment_id,
        generation_mode=record.generation_mode,
        selected_directions=selected,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _load_selected_directions(
    db: Session,
    assessment_id: str,
) -> list:
    from app.schemas.direction import DirectionSuggestion

    record = _load_direction_selection_record(db, assessment_id)
    if record is None:
        return []

    raw_directions = _parse_json_raw(
        record.directions_json,
        "Failed to parse direction selection.",
    )
    return [DirectionSuggestion.model_validate(item) for item in raw_directions]


def _inject_llm_directions_into_expansion(
    expansion,
    llm_directions,
):
    from app.schemas.direction import (
        DirectionExpansionByElement,
        DirectionExpansionResult,
    )

    llm_by_key: dict[str, list] = {}
    for d in llm_directions:
        llm_by_key.setdefault(d.element_key, []).append(d)

    elements: list[DirectionExpansionByElement] = []
    for elem in expansion.elements:
        llm_suggestions = llm_by_key.get(elem.element_key, [])
        if llm_suggestions:
            elements.append(
                DirectionExpansionByElement(
                    element_key=elem.element_key,
                    element_title=elem.element_title,
                    suggestions=llm_suggestions,
                )
            )
        else:
            elements.append(elem)

    total = sum(len(e.suggestions) for e in elements)
    return DirectionExpansionResult(
        generation_mode="llm" if llm_directions else expansion.generation_mode,
        elements=elements,
        total_suggestions=total,
    )


def _upsert_direction_expansion(
    db: Session,
    assessment_id: str,
    expansion: DirectionExpansionResult,
) -> DirectionExpansion:
    record = db.scalar(
        select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)
    )
    if record is None:
        record = DirectionExpansion(
            assessment_id=assessment_id,
            generation_mode=expansion.generation_mode,
            llm_status="pending",
            expansion_json=expansion.model_dump_json(),
        )
        db.add(record)
    else:
        record.generation_mode = expansion.generation_mode
        record.llm_status = "pending"
        record.expansion_json = expansion.model_dump_json()
    db.flush()
    db.refresh(record)
    return record


def _load_direction_expansion(
    db: Session,
    assessment_id: str,
) -> DirectionExpansion | None:
    return db.scalar(
        select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)
    )


def _background_enhance_directions(
    assessment_id: str,
    canvas_json: str,
    breakthrough_keys: list[str],
) -> None:
    """Run LLM enhancement in a daemon thread with its own DB session."""
    from app.schemas.assessment import CanvasDiagnosisResult

    logger = logging.getLogger(__name__)
    db = SessionLocal()
    try:
        canvas = CanvasDiagnosisResult.model_validate_json(canvas_json)
        enhancer = LLMEnhancer()
        llm_directions = enhancer.enhance_directions(canvas, breakthrough_keys)

        record = db.scalar(
            select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)
        )
        if record is None:
            logger.warning("DirectionExpansion record vanished before background task completed")
            return

        if llm_directions:
            stored_expansion = DirectionExpansionResult.model_validate_json(record.expansion_json)
            merged = _inject_llm_directions_into_expansion(stored_expansion, llm_directions)
            record.generation_mode = merged.generation_mode
            record.llm_status = "completed"
            record.expansion_json = merged.model_dump_json()
        else:
            record.llm_status = "failed"

        record.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(
            "Background LLM enhancement %s for assessment %s",
            "completed" if llm_directions else "failed (no result)",
            assessment_id,
        )
    except Exception:
        logger.warning(
            "Background LLM enhancement failed for %s", assessment_id, exc_info=True
        )
        try:
            record = db.scalar(
                select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)
            )
            if record is not None:
                record.llm_status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def _load_competitiveness_analysis(
    db: Session,
    assessment_id: str,
) -> CompetitivenessAnalysis | None:
    return db.scalar(
        select(CompetitivenessAnalysis).where(
            CompetitivenessAnalysis.assessment_id == assessment_id
        )
    )


def _upsert_competitiveness_analysis(
    db: Session,
    assessment_id: str,
    result: CompetitivenessResult,
) -> CompetitivenessAnalysis:
    record = _load_competitiveness_analysis(db, assessment_id)
    if record is None:
        record = CompetitivenessAnalysis(
            assessment_id=assessment_id,
            generation_mode="rule_based",
            vp_json="{}",
            connections_json="[]",
            advantages_json="[]",
            strategy_json="{}",
        )

    record.generation_mode = "rule_based"
    record.vp_json = json.dumps(result.vp_reconstruction.model_dump(), ensure_ascii=False)
    record.connections_json = json.dumps(
        [c.model_dump() for c in result.connections], ensure_ascii=False
    )
    record.advantages_json = json.dumps(
        [a.model_dump() for a in result.advantages], ensure_ascii=False
    )
    record.strategy_json = json.dumps(result.delivery_strategy.model_dump(), ensure_ascii=False)

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_endgame_and_below(db, assessment_id)

    return record


def _build_competitiveness_result_from_record(
    record: CompetitivenessAnalysis,
) -> CompetitivenessResult:
    """Rehydrate a persisted competitiveness analysis into the API schema."""
    from app.schemas.competitiveness import (
        VPReconstruction,
        PointToLineConnection,
        CoreAdvantage,
        DeliveryStrategy,
    )

    vp_raw = _parse_json_raw(record.vp_json, "Failed to parse VP reconstruction.")
    connections_raw = _parse_json_raw(record.connections_json, "Failed to parse connections.")
    advantages_raw = _parse_json_raw(record.advantages_json, "Failed to parse advantages.")
    strategy_raw = _parse_json_raw(record.strategy_json, "Failed to parse delivery strategy.")
    normalized_connections = [_normalize_connection_summary(item) for item in connections_raw]

    return CompetitivenessResult(
        generation_mode=record.generation_mode,
        vp_reconstruction=VPReconstruction.model_validate(vp_raw),
        connections=[PointToLineConnection.model_validate(item) for item in normalized_connections],
        advantages=[CoreAdvantage.model_validate(item) for item in advantages_raw],
        delivery_strategy=DeliveryStrategy.model_validate(strategy_raw),
        overall_narrative=record.overall_narrative or "",
    )


def _normalize_connection_summary(item: dict) -> dict:
    """将旧版线路摘要兼容为只表达逻辑和预期效果的一句话。"""
    normalized = dict(item)
    line_name = str(normalized.get("line_name", "")).strip()
    competitive_impact = str(normalized.get("competitive_impact", "")).strip()
    normalized["strategic_narrative"] = build_line_summary(line_name, competitive_impact)
    normalized["competitive_moat"] = ""
    return normalized


def _load_endgame_analysis(
    db: Session,
    assessment_id: str,
) -> EndgameAnalysis | None:
    return db.scalar(
        select(EndgameAnalysis).where(
            EndgameAnalysis.assessment_id == assessment_id
        )
    )


def _upsert_endgame_analysis(
    db: Session,
    assessment_id: str,
    result: EndgameResult,
) -> EndgameAnalysis:
    record = _load_endgame_analysis(db, assessment_id)
    if record is None:
        record = EndgameAnalysis(
            assessment_id=assessment_id,
            generation_mode="rule_based",
            private_domain_json="{}",
            ecosystem_json="{}",
            opc_json="{}",
            three_stage_strategy_json="{}",
            strategic_paths_json="[]",
        )

    record.generation_mode = "rule_based"
    record.private_domain_json = json.dumps(result.private_domain.model_dump(), ensure_ascii=False)
    record.ecosystem_json = json.dumps(result.ecosystem.model_dump(), ensure_ascii=False)
    record.opc_json = json.dumps(result.opc.model_dump(), ensure_ascii=False)
    record.three_stage_strategy_json = json.dumps(
        result.three_stage_strategy.model_dump(), ensure_ascii=False
    )
    record.strategic_paths_json = json.dumps(
        [p.model_dump() for p in result.strategic_paths], ensure_ascii=False
    )
    record.overall_narrative = result.overall_narrative

    db.add(record)
    db.commit()
    db.refresh(record)
    _clear_cases_and_reports(db, assessment_id)

    return record


def _build_endgame_result_from_record(
    record: EndgameAnalysis,
) -> EndgameResult:
    from app.schemas.endgame import (
        PrivateDomainDesign,
        EcosystemDesign,
        OPCDesign,
        StrategicPath,
        ThreeStageStrategy,
    )

    pd_raw = _parse_json_raw(record.private_domain_json, "Failed to parse private domain.")
    eco_raw = _parse_json_raw(record.ecosystem_json, "Failed to parse ecosystem.")
    opc_raw = _parse_json_raw(record.opc_json, "Failed to parse OPC.")
    three_stage_raw = _parse_json_raw(
        getattr(record, "three_stage_strategy_json", "{}"),
        "Failed to parse three-stage strategy.",
    )
    paths_raw = _parse_json_raw(record.strategic_paths_json, "Failed to parse strategic paths.")

    return EndgameResult(
        generation_mode=record.generation_mode,
        private_domain=PrivateDomainDesign.model_validate(pd_raw),
        ecosystem=EcosystemDesign.model_validate(eco_raw),
        opc=OPCDesign.model_validate(opc_raw),
        three_stage_strategy=ThreeStageStrategy.model_validate(three_stage_raw),
        strategic_paths=[
            StrategicPath.model_validate(_normalize_endgame_strategic_path(item))
            for item in paths_raw
        ],
        overall_narrative=record.overall_narrative or "",
    )


def _normalize_endgame_strategic_path(item: dict) -> dict:
    """兼容历史终局路径结构，统一还原为当前定性字段。"""
    normalized = dict(item)
    if "execution_rhythm" not in normalized and "timeline" in normalized:
        normalized["execution_rhythm"] = normalized["timeline"]
    if "capability_requirements" not in normalized and "required_investments" in normalized:
        normalized["capability_requirements"] = normalized["required_investments"]
    return normalized


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
    block_scores: list[tuple[str, int, str, str]] = []
    for block in canvas_result.blocks:
        score = 10
        completeness_issues = 0
        for content in (
            block.current_state,
            block.diagnosis,
            block.ai_opportunity,
            block.missing_information,
        ):
            if "待补充" in content:
                score -= 2
                completeness_issues += 1
            if "缺失" in content or "不完整" in content or "不足" in content:
                score -= 1
        block_scores.append(
            (block.title, max(3, score), block.ai_opportunity, block.diagnosis)
        )

    if not block_scores:
        return 0, [], []

    total_score = sum(item[1] for item in block_scores)
    # Demo mode: score based on 9-block completeness (0-100)
    overall_score = max(0, min(100, round(total_score / (len(block_scores) * 10) * 100)))
    weakest = sorted(block_scores, key=lambda item: item[1])[:3]
    weakest_blocks = [item[0] for item in weakest]

    # Build concise, actionable recommended_focus (one sentence per element)
    recommended_focus: list[str] = []
    for title, _, _, diagnosis in weakest:
        # Extract the core diagnostic insight and make it actionable
        short_diag = diagnosis.split("。")[0] if "。" in diagnosis else diagnosis
        abbr = _block_title_to_abbr(title)
        recommended_focus.append(f"{title}（{abbr}）：{short_diag}。—— 建议优先完善该模块数据基础并启动 AI 试点。")

    return overall_score, weakest_blocks, recommended_focus


def _block_title_to_abbr(title: str) -> str:
    abbr_map = {
        "关键合作伙伴": "KP",
        "关键业务活动": "KA",
        "关键资源": "KR",
        "价值主张": "VP",
        "客户关系": "CR",
        "渠道通路": "CH",
        "客户细分": "CS",
        "成本结构": "C$",
        "收入来源": "R$",
    }
    return abbr_map.get(title, title[:2])


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
    _clear_breakthrough_and_below(db, assessment_id)

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
    scoring_method: Literal["rule_based_v1", "four_quadrant_v1"] = "rule_based_v1",
) -> ScenarioRecommendationResult:
    record = db.scalar(
        select(ScenarioRecommendation).where(
            ScenarioRecommendation.assessment_id == assessment_id
        )
    )
    if record is None:
        record = ScenarioRecommendation(
            assessment_id=assessment_id,
            scoring_method=scoring_method,
            evaluated_count=evaluated_count,
            scenario_json="[]",
            top_scenarios="[]",
        )

    record.scoring_method = scoring_method
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
        scoring_method=scoring_method,
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
            scoring_method="layered_v1",
            evaluated_count=evaluated_count,
            case_json="[]",
            top_cases="[]",
        )

    record.scoring_method = "layered_v1"
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
        scoring_method="layered_v1",
        evaluated_count=evaluated_count,
        top_cases=top_cases,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _build_progress(
    profile: CompanyProfileResult | None,
    canvas: CanvasDiagnosisResult | None,
    breakthrough_keys: list[str] | None,
    scenarios: ScenarioRecommendationResult | None,
    cases: CaseRecommendationResult | None,
    report_summary,
    direction_selection: object | None = None,
    competitiveness: object | None = None,
) -> AssessmentProgress:
    has_profile = profile is not None
    has_canvas = canvas is not None
    has_breakthrough = breakthrough_keys is not None and len(breakthrough_keys) >= 2
    has_directions = False
    if direction_selection is not None:
        has_directions = bool(
            getattr(direction_selection, "selected_directions", None)
            or getattr(direction_selection, "directions_json", None)
        )
    has_competitiveness = competitiveness is not None
    has_scenarios = scenarios is not None
    has_cases = cases is not None
    has_report = report_summary is not None
    return AssessmentProgress(
        has_profile=has_profile,
        has_canvas=has_canvas,
        has_breakthrough=has_breakthrough,
        has_directions=has_directions,
        has_competitiveness=has_competitiveness,
        has_scenarios=has_scenarios,
        has_cases=has_cases,
        has_report=has_report,
        ready_for_report=has_profile and has_canvas and has_breakthrough and has_scenarios,
    )


def _clear_canvas_and_below(db: Session, assessment_id: str) -> None:
    _delete_records(
        db,
        [
            db.scalar(select(CanvasDiagnosis).where(CanvasDiagnosis.assessment_id == assessment_id)),
            db.scalar(select(BreakthroughSelection).where(BreakthroughSelection.assessment_id == assessment_id)),
            db.scalar(select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)),
            db.scalar(select(CompetitivenessAnalysis).where(CompetitivenessAnalysis.assessment_id == assessment_id)),
            db.scalar(select(EndgameAnalysis).where(EndgameAnalysis.assessment_id == assessment_id)),
            db.scalar(
                select(ScenarioRecommendation).where(
                    ScenarioRecommendation.assessment_id == assessment_id
                )
            ),
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_competitiveness_and_below(db: Session, assessment_id: str) -> None:
    """Clear competitiveness analysis, endgame, and everything downstream (scenarios, cases, reports).

    Used after direction re-selection, which invalidates competitiveness and below.
    """
    _delete_records(
        db,
        [
            db.scalar(select(CompetitivenessAnalysis).where(CompetitivenessAnalysis.assessment_id == assessment_id)),
            db.scalar(select(EndgameAnalysis).where(EndgameAnalysis.assessment_id == assessment_id)),
            db.scalar(
                select(ScenarioRecommendation).where(
                    ScenarioRecommendation.assessment_id == assessment_id
                )
            ),
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_endgame_and_below(db: Session, assessment_id: str) -> None:
    """Clear endgame analysis and everything downstream (scenarios, cases, reports).

    Used after competitiveness re-generation, which invalidates endgame and below.
    Does NOT clear competitiveness itself.
    """
    _delete_records(
        db,
        [
            db.scalar(select(EndgameAnalysis).where(EndgameAnalysis.assessment_id == assessment_id)),
            db.scalar(
                select(ScenarioRecommendation).where(
                    ScenarioRecommendation.assessment_id == assessment_id
                )
            ),
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_directions_and_below(db: Session, assessment_id: str) -> None:
    """Clear direction expansion, direction selection, and everything downstream.

    Used after breakthrough re-selection, which invalidates all direction-related
    data plus competitiveness, endgame, scenarios, cases, and reports.
    """
    _delete_records(
        db,
        [
            db.scalar(select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)),
            db.scalar(select(DirectionSelection).where(DirectionSelection.assessment_id == assessment_id)),
            db.scalar(select(CompetitivenessAnalysis).where(CompetitivenessAnalysis.assessment_id == assessment_id)),
            db.scalar(select(EndgameAnalysis).where(EndgameAnalysis.assessment_id == assessment_id)),
            db.scalar(
                select(ScenarioRecommendation).where(
                    ScenarioRecommendation.assessment_id == assessment_id
                )
            ),
            db.scalar(select(CaseRecommendation).where(CaseRecommendation.assessment_id == assessment_id)),
            db.scalar(select(GeneratedReport).where(GeneratedReport.assessment_id == assessment_id)),
        ],
    )


def _clear_breakthrough_and_below(db: Session, assessment_id: str) -> None:
    _delete_records(
        db,
        [
            db.scalar(select(BreakthroughSelection).where(BreakthroughSelection.assessment_id == assessment_id)),
            db.scalar(select(DirectionExpansion).where(DirectionExpansion.assessment_id == assessment_id)),
            db.scalar(select(CompetitivenessAnalysis).where(CompetitivenessAnalysis.assessment_id == assessment_id)),
            db.scalar(select(EndgameAnalysis).where(EndgameAnalysis.assessment_id == assessment_id)),
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
