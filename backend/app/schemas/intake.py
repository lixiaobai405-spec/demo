from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.assessment import AssessmentCreateRequest, AssessmentResponse

IntakeSourceType = Literal["text", "markdown", "form", "file"]
FieldSourceType = Literal["raw", "inferred", "missing"]
FieldStatus = Literal["confirmed", "needs_user_confirmation", "needs_user_input"]
CandidateSource = Literal["原文", "推断"]
CandidateConfidence = Literal["high", "medium"]
IntakeSessionStatus = Literal["draft", "parsed", "confirmed", "discarded"]
IntakeUploadedFileKind = Literal["txt", "markdown", "pdf", "docx"]

ASSESSMENT_FIELD_NAMES = (
    "company_name",
    "industry",
    "company_size",
    "region",
    "annual_revenue_range",
    "core_products",
    "target_customers",
    "current_challenges",
    "ai_goals",
    "available_data",
    "notes",
)


class AssessmentPrefillDraft(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    company_size: str | None = None
    region: str | None = None
    annual_revenue_range: str | None = None
    core_products: str | None = None
    target_customers: str | None = None
    current_challenges: str | None = None
    ai_goals: str | None = None
    available_data: str | None = None
    notes: str | None = None


class IntakeFieldCandidate(BaseModel):
    value: str
    source: CandidateSource
    confidence: CandidateConfidence
    evidence: str


class IntakeFieldMeta(BaseModel):
    source_type: FieldSourceType
    status: FieldStatus


class IntakeSourceFile(BaseModel):
    name: str
    kind: IntakeUploadedFileKind
    size_bytes: int


class IntakeImportRequest(BaseModel):
    source_type: IntakeSourceType
    raw_content: str | None = None
    structured_fields: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_has_input(self) -> "IntakeImportRequest":
        cleaned_structured = {
            key: value.strip()
            for key, value in self.structured_fields.items()
            if isinstance(value, str) and value.strip()
        }
        raw_content = self.raw_content.strip() if self.raw_content and self.raw_content.strip() else None

        if raw_content is None and not cleaned_structured:
            raise ValueError("raw_content or structured_fields must provide at least one non-empty value.")

        self.raw_content = raw_content
        self.structured_fields = cleaned_structured
        return self


class IntakeImportResponse(BaseModel):
    import_session_id: str
    status: IntakeSessionStatus
    source_type: IntakeSourceType
    source_file: IntakeSourceFile | None = None
    assessment_prefill: AssessmentPrefillDraft
    field_meta: dict[str, IntakeFieldMeta] = Field(default_factory=dict)
    field_candidates: dict[str, IntakeFieldCandidate] = Field(default_factory=dict)
    unmapped_notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class IntakeSessionDetailResponse(IntakeImportResponse):
    raw_content: str | None = None
    structured_fields: dict[str, str] = Field(default_factory=dict)
    created_assessment_id: str | None = None
    created_at: str
    updated_at: str


class IntakeCreateAssessmentRequest(BaseModel):
    confirmed_assessment_input: AssessmentCreateRequest


class IntakeCreateAssessmentResponse(BaseModel):
    import_session_id: str
    status: IntakeSessionStatus
    assessment: AssessmentResponse
