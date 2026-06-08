from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SCORE_SCHEMA_VERSION = "score.v1"
SCORE_RUBRIC_VERSION = "spec.v1.0"


class ScoreReportType(str, Enum):
    WEN_GU_ZHI_XIN = "温故知新"
    ACTION_LEARNING = "行动学习"


class ScoreMaterialSource(str, Enum):
    DOCUMENT = "文档"
    TRANSCRIPT = "录音转写"


class ScoreLevelLabel(str, Enum):
    OUTSTANDING = "卓越"
    EXCELLENT = "优秀"
    GOOD = "良好"
    PASS = "合格"
    FAIL = "不合格"
    NOT_SCORED = "未评分"


class ScoreExportFormat(str, Enum):
    MARKDOWN = "md"
    PDF = "pdf"


class ScoreDimensionDefinition(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int
    name: str
    level_name: str
    material_source: ScoreMaterialSource
    weight_pct: float = Field(ge=0, le=100)
    level_weight_pct: float = Field(ge=0, le=100)


class ScoreRubricDefinition(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    report_type: ScoreReportType
    version: str = SCORE_RUBRIC_VERSION
    dimensions: list[ScoreDimensionDefinition]


class ScoreSubmissionInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(min_length=1, max_length=100)
    org: str = Field(min_length=1, max_length=200)
    report_type: ScoreReportType
    date: date
    note: str | None = Field(default=None, max_length=1000)
    transcript: str = Field(default="")

    @field_validator("name", "org", "note", "transcript")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class ScoreLLMDimensionResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int
    name: str
    level: str
    material_source: ScoreMaterialSource
    score: float | None = Field(default=None, ge=0.0, le=10.0)
    level_label: ScoreLevelLabel
    evidence: str = Field(min_length=1, max_length=80)
    comment: str = Field(min_length=1, max_length=120)

    @field_validator("score")
    @classmethod
    def normalize_score_precision(cls, value: float | None) -> float | None:
        if value is None:
            return None
        return round(value, 1)


class ScoreLLMResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    report_type: ScoreReportType
    dimensions: list[ScoreLLMDimensionResult]
    overall_comment: str = Field(min_length=1, max_length=400)


class ScoreDimensionResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int
    name: str
    level_name: str
    material_source: ScoreMaterialSource
    weight_pct: float
    score: float | None = Field(default=None, ge=0.0, le=10.0)
    weighted_score: float = Field(ge=0.0, le=100.0)
    level_label: ScoreLevelLabel
    evidence: str = Field(min_length=1, max_length=80)
    comment: str = Field(min_length=1, max_length=120)

    @field_validator("score")
    @classmethod
    def normalize_dimension_score_precision(cls, value: float | None) -> float | None:
        if value is None:
            return None
        return round(value, 1)

    @field_validator("weighted_score")
    @classmethod
    def normalize_weighted_score_precision(cls, value: float) -> float:
        return round(value, 1)


class ScoreResultPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    schema_version: str = SCORE_SCHEMA_VERSION
    rubric_version: str = SCORE_RUBRIC_VERSION
    report_type: ScoreReportType
    total_score: float = Field(ge=0.0, le=100.0)
    dimensions: list[ScoreDimensionResult]
    overall_comment: str = Field(min_length=1, max_length=400)
    strengths: list[str]
    improvements: list[str]
    disclaimer: str
    transcript_provided: bool

    @field_validator("total_score")
    @classmethod
    def normalize_total_score_precision(cls, value: float) -> float:
        return round(value, 1)


class ScoreRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    score_id: str
    name: str
    org: str
    report_type: ScoreReportType
    date: date
    note: str | None = None
    total_score: float = Field(ge=0.0, le=100.0)
    dimensions: list[ScoreDimensionResult]
    overall_comment: str
    strengths: list[str]
    improvements: list[str]
    created_at: datetime


class ScoreDetailResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    score_id: str
    input: ScoreSubmissionInput
    result: ScoreResultPayload
    created_at: datetime
    updated_at: datetime
    export_markdown_path: str | None = None
    export_pdf_path: str | None = None


class ScoreCreateResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    score_id: str
    total_score: float = Field(ge=0.0, le=100.0)
    dimensions: list[ScoreDimensionResult]
    overall_comment: str
    created_at: datetime


class ScoreFileExtractionResult(BaseModel):
    file_name: str
    size_bytes: int
    extracted_text: str


class ScoreCreateServiceInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    submission: ScoreSubmissionInput
    pdf: ScoreFileExtractionResult


class ScoreExportMetadata(BaseModel):
    file_name: str
    media_type: str
    extension: Literal["md", "pdf"]


WEN_GU_ZHI_XIN_RUBRIC = ScoreRubricDefinition(
    report_type=ScoreReportType.WEN_GU_ZHI_XIN,
    dimensions=[
        ScoreDimensionDefinition(
            id=1,
            name="战略链接与价值认知",
            level_name="温故·实战复盘",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=10.0,
            level_weight_pct=55.0,
        ),
        ScoreDimensionDefinition(
            id=2,
            name="知识融合与框架应用",
            level_name="温故·实战复盘",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=15.0,
            level_weight_pct=55.0,
        ),
        ScoreDimensionDefinition(
            id=3,
            name="行为的具体性与可观察性",
            level_name="温故·实战复盘",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=10.0,
            level_weight_pct=55.0,
        ),
        ScoreDimensionDefinition(
            id=4,
            name="行动的有效性与结果导向",
            level_name="温故·实战复盘",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=10.0,
            level_weight_pct=55.0,
        ),
        ScoreDimensionDefinition(
            id=5,
            name="反思深刻性与真诚度",
            level_name="温故·实战复盘",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=10.0,
            level_weight_pct=55.0,
        ),
        ScoreDimensionDefinition(
            id=6,
            name="课题的战略价值",
            level_name="知新·课题立项",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=10.0,
            level_weight_pct=25.0,
        ),
        ScoreDimensionDefinition(
            id=7,
            name="目标与规划的前瞻性",
            level_name="知新·课题立项",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=10.0,
            level_weight_pct=25.0,
        ),
        ScoreDimensionDefinition(
            id=8,
            name="创新与突破性",
            level_name="知新·课题立项",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=5.0,
            level_weight_pct=25.0,
        ),
        ScoreDimensionDefinition(
            id=9,
            name="逻辑的严谨性和链条完整性",
            level_name="逻辑性与展现力",
            material_source=ScoreMaterialSource.TRANSCRIPT,
            weight_pct=10.0,
            level_weight_pct=20.0,
        ),
        ScoreDimensionDefinition(
            id=10,
            name="材料与汇报的展现力",
            level_name="逻辑性与展现力",
            material_source=ScoreMaterialSource.TRANSCRIPT,
            weight_pct=10.0,
            level_weight_pct=20.0,
        ),
    ],
)


ACTION_LEARNING_RUBRIC = ScoreRubricDefinition(
    report_type=ScoreReportType.ACTION_LEARNING,
    dimensions=[
        ScoreDimensionDefinition(
            id=1,
            name="直面问题",
            level_name="作业评价",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=20.0,
            level_weight_pct=80.0,
        ),
        ScoreDimensionDefinition(
            id=2,
            name="创新构想",
            level_name="作业评价",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=15.0,
            level_weight_pct=80.0,
        ),
        ScoreDimensionDefinition(
            id=3,
            name="结构性方法",
            level_name="作业评价",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=15.0,
            level_weight_pct=80.0,
        ),
        ScoreDimensionDefinition(
            id=4,
            name="可操作性",
            level_name="作业评价",
            material_source=ScoreMaterialSource.DOCUMENT,
            weight_pct=30.0,
            level_weight_pct=80.0,
        ),
        ScoreDimensionDefinition(
            id=5,
            name="表达清晰",
            level_name="呈现效果评价",
            material_source=ScoreMaterialSource.TRANSCRIPT,
            weight_pct=10.0,
            level_weight_pct=20.0,
        ),
        ScoreDimensionDefinition(
            id=6,
            name="回答问题",
            level_name="呈现效果评价",
            material_source=ScoreMaterialSource.TRANSCRIPT,
            weight_pct=5.0,
            level_weight_pct=20.0,
        ),
        ScoreDimensionDefinition(
            id=7,
            name="时间管理",
            level_name="呈现效果评价",
            material_source=ScoreMaterialSource.TRANSCRIPT,
            weight_pct=5.0,
            level_weight_pct=20.0,
        ),
    ],
)


SCORE_RUBRICS: dict[ScoreReportType, ScoreRubricDefinition] = {
    ScoreReportType.WEN_GU_ZHI_XIN: WEN_GU_ZHI_XIN_RUBRIC,
    ScoreReportType.ACTION_LEARNING: ACTION_LEARNING_RUBRIC,
}


def get_score_rubric(report_type: ScoreReportType) -> ScoreRubricDefinition:
    return SCORE_RUBRICS[report_type]


def infer_level_label(score: float | None) -> ScoreLevelLabel:
    if score is None:
        return ScoreLevelLabel.NOT_SCORED
    if score >= 9.0:
        return ScoreLevelLabel.OUTSTANDING
    if score >= 7.5:
        return ScoreLevelLabel.EXCELLENT
    if score >= 6.0:
        return ScoreLevelLabel.GOOD
    if score >= 4.0:
        return ScoreLevelLabel.PASS
    return ScoreLevelLabel.FAIL


def build_score_disclaimer() -> str:
    return "本报告由 AI 智能体自动生成，仅供参考，最终评定以培训导师意见为准。"


def ensure_llm_dimensions_match_rubric(
    report_type: ScoreReportType,
    dimensions: list[ScoreLLMDimensionResult],
) -> list[ScoreLLMDimensionResult]:
    rubric = get_score_rubric(report_type)
    expected = {item.id: item for item in rubric.dimensions}
    actual_ids = [item.id for item in dimensions]
    if actual_ids != [item.id for item in rubric.dimensions]:
        raise ValueError("LLM dimensions do not match the rubric order.")

    normalized: list[ScoreLLMDimensionResult] = []
    for item in dimensions:
        definition = expected[item.id]
        if item.name != definition.name:
            raise ValueError(f"LLM dimension name mismatch for id={item.id}.")
        if item.level != definition.level_name:
            raise ValueError(f"LLM dimension level mismatch for id={item.id}.")
        if item.material_source != definition.material_source:
            raise ValueError(f"LLM material source mismatch for id={item.id}.")
        normalized.append(item)
    return normalized


class ScoreRubricSnapshot(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    schema_version: str = SCORE_SCHEMA_VERSION
    rubric_version: str = SCORE_RUBRIC_VERSION
    report_type: ScoreReportType
    dimensions: list[ScoreDimensionDefinition]

    @classmethod
    def from_report_type(cls, report_type: ScoreReportType) -> "ScoreRubricSnapshot":
        rubric = get_score_rubric(report_type)
        return cls(
            report_type=report_type,
            dimensions=rubric.dimensions,
        )


class ScoreCreateRequestValidation(BaseModel):
    """Used in tests and service to validate multipart payload after parsing."""

    submission: ScoreSubmissionInput
    pdf_file_present: bool

    @model_validator(mode="after")
    def ensure_pdf_present(self) -> "ScoreCreateRequestValidation":
        if not self.pdf_file_present:
            raise ValueError("pdf_file is required.")
        return self
