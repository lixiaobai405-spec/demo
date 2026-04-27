from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AssessmentCreateRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    industry: str = Field(min_length=1, max_length=255)
    company_size: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=255)
    annual_revenue_range: str = Field(min_length=1, max_length=100)
    core_products: str = Field(min_length=1)
    target_customers: str = Field(min_length=1)
    current_challenges: str = Field(min_length=1)
    ai_goals: str = Field(min_length=1)
    available_data: str = Field(min_length=1)
    notes: str | None = None


class AssessmentInputSnapshot(BaseModel):
    company_name: str
    industry: str
    company_size: str
    region: str
    annual_revenue_range: str
    core_products: str
    target_customers: str
    current_challenges: str
    ai_goals: str
    available_data: str
    notes: str | None


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    industry: str
    company_size: str
    region: str
    annual_revenue_range: str
    core_products: str
    target_customers: str
    current_challenges: str
    ai_goals: str
    available_data: str
    notes: str | None
    has_profile: bool
    profile_generation_mode: str | None
    profile_generated_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CompanyProfileResult(BaseModel):
    company_name: str
    company_summary: str
    value_proposition: str
    customer_and_market: str
    operations_and_resources: str
    digital_and_ai_readiness: str
    key_challenges: list[str] = Field(default_factory=list)
    priority_ai_directions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class AssessmentProfileResponse(BaseModel):
    assessment: AssessmentResponse
    generation_mode: Literal["mock", "live"]
    profile: CompanyProfileResult


class CanvasBlockResult(BaseModel):
    key: str
    title: str
    current_state: str
    diagnosis: str
    ai_opportunity: str
    missing_information: str


class BusinessModelCanvasResult(BaseModel):
    overall_summary: str
    blocks: list[CanvasBlockResult] = Field(default_factory=list)


class CanvasDiagnosisResult(BaseModel):
    generation_mode: Literal["mock", "live"]
    overall_score: int
    weakest_blocks: list[str] = Field(default_factory=list)
    recommended_focus: list[str] = Field(default_factory=list)
    canvas: BusinessModelCanvasResult
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentCanvasResponse(BaseModel):
    assessment: AssessmentResponse
    canvas_diagnosis: CanvasDiagnosisResult


class ScenarioRecommendationItem(BaseModel):
    scenario_id: str
    name: str
    category: str
    summary: str
    score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)
    data_requirements: list[str] = Field(default_factory=list)


class ScenarioRecommendationResult(BaseModel):
    scoring_method: Literal["rule_based_v1"]
    evaluated_count: int
    top_scenarios: list[ScenarioRecommendationItem] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentScenarioRecommendationResponse(BaseModel):
    assessment: AssessmentResponse
    scenario_recommendation: ScenarioRecommendationResult


class CaseMatchItem(BaseModel):
    case_id: str
    title: str
    industry: str
    summary: str
    fit_score: int = Field(ge=0, le=100)
    matched_pain_points: list[str] = Field(default_factory=list)
    matched_canvas_blocks: list[str] = Field(default_factory=list)
    matched_scenarios: list[str] = Field(default_factory=list)
    match_reasons: list[str] = Field(default_factory=list)
    reference_points: list[str] = Field(default_factory=list)
    data_foundation: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)


class CaseRecommendationResult(BaseModel):
    scoring_method: Literal["rule_based_case_v1"]
    evaluated_count: int
    top_cases: list[CaseMatchItem] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentCaseResponse(BaseModel):
    assessment: AssessmentResponse
    case_recommendation: CaseRecommendationResult


class ReportRoadmapStage(BaseModel):
    stage_name: str
    time_horizon: str
    strategic_focus: str
    priority_actions: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)


class ReportActionItem(BaseModel):
    period: str
    action: str
    owner_suggestion: str
    deliverable: str


class ReportTableData(BaseModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class ReportCardData(BaseModel):
    title: str
    subtitle: str | None = None
    content: str
    bullets: list[str] = Field(default_factory=list)
    highlight: str | None = None


class ReportSectionData(BaseModel):
    key: str
    title: str
    content: str
    bullets: list[str] = Field(default_factory=list)
    table: ReportTableData | None = None
    cards: list[ReportCardData] = Field(default_factory=list)
    note: str | None = None


class ReportData(BaseModel):
    title: str
    subtitle: str
    company_name: str
    industry: str
    company_size: str
    region: str
    annual_revenue_range: str
    ai_readiness_score: int = Field(ge=0, le=100)
    ai_readiness_summary: str
    generated_with: Literal["template", "llm"]
    sections: list[ReportSectionData] = Field(default_factory=list)


class ReportSummaryResponse(BaseModel):
    report_id: str
    assessment_id: str
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReportDocumentResponse(BaseModel):
    report_id: str
    assessment_id: str
    title: str
    generation_mode: str
    used_llm: bool
    used_rag: bool
    warnings: list[str] = Field(default_factory=list)
    content_markdown: str
    content_html: str
    content_json: ReportData
    sections: list[ReportSectionData] = Field(default_factory=list)
    export_markdown_path: str | None = None
    export_docx_path: str | None = None
    export_pdf_path: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentProgress(BaseModel):
    has_profile: bool
    has_canvas: bool
    has_scenarios: bool
    has_cases: bool
    has_report: bool
    ready_for_report: bool


class AssessmentDetailResponse(BaseModel):
    assessment: AssessmentResponse
    company_profile: CompanyProfileResult | None
    canvas_diagnosis: CanvasDiagnosisResult | None
    scenario_recommendation: ScenarioRecommendationResult | None
    case_recommendation: CaseRecommendationResult | None
    generated_report: ReportSummaryResponse | None
    progress: AssessmentProgress


class ReportContextResponse(BaseModel):
    assessment_id: str
    company_input: AssessmentInputSnapshot
    company_profile: CompanyProfileResult
    canvas_diagnosis: CanvasDiagnosisResult
    top_scenarios: list[ScenarioRecommendationItem] = Field(default_factory=list)
    report_outline: list[str] = Field(default_factory=list)
