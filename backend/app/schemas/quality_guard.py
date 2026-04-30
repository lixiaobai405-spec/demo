from typing import Literal

from pydantic import BaseModel, Field

ConfidenceLevel = Literal["高", "中", "低"]
SourceType = Literal["规则引擎", "模板知识库", "LLM生成", "用户输入", "待补充"]
ValidationStatus = Literal["pass", "warn", "fail"]


class QualityFlag(BaseModel):
    code: str
    level: Literal["info", "warn", "error"]
    message: str


class SectionQualityReport(BaseModel):
    section_key: str
    section_title: str
    confidence: ConfidenceLevel = "中"
    source: SourceType = "规则引擎"
    flags: list[QualityFlag] = Field(default_factory=list)
    has_actionable_content: bool = True
    missing_aspects: list[str] = Field(default_factory=list)


class OverallQualityReport(BaseModel):
    overall_score: int = Field(default=50, ge=0, le=100)
    overall_confidence: ConfidenceLevel = "中"
    sections: list[SectionQualityReport] = Field(default_factory=list)
    critical_flags: list[QualityFlag] = Field(default_factory=list)
    summary: str = ""
    improvement_suggestions: list[str] = Field(default_factory=list)


QUALITY_RULES = {
    "company_profile": {
        "min_content_length": 40,
        "check_phrases": ["待补充", "数据不完整", "信息不足"],
        "required_aspects": ["企业名称", "行业定位"],
        "source": "规则引擎",
    },
    "canvas_diagnosis": {
        "min_content_length": 80,
        "check_phrases": ["待补充", "不清晰", "缺失关键数据", "无法完成诊断"],
        "required_aspects": ["overall_summary", "9 blocks"],
        "source": "规则引擎",
    },
    "breakthrough": {
        "min_content_length": 30,
        "check_phrases": ["待补充"],
        "required_aspects": [],
        "source": "规则引擎",
    },
    "direction_expansion": {
        "min_content_length": 20,
        "check_phrases": ["待补充"],
        "required_aspects": [],
        "source": "模板知识库",
    },
    "ai_readiness": {
        "min_content_length": 40,
        "check_phrases": ["待补充"],
        "required_aspects": [],
        "source": "规则引擎",
    },
    "priority_scenarios": {
        "min_content_length": 30,
        "check_phrases": ["待补充"],
        "required_aspects": ["场景名称", "场景分类"],
        "source": "规则引擎",
    },
    "scenario_planning": {
        "min_content_length": 30,
        "check_phrases": ["待补充"],
        "required_aspects": [],
        "source": "模板知识库",
    },
    "competitiveness": {
        "min_content_length": 50,
        "check_phrases": ["待补充"],
        "required_aspects": ["增强型价值主张", "串联竞争力线"],
        "source": "规则引擎",
    },
    "cases": {
        "min_content_length": 20,
        "check_phrases": ["待补充", "未匹配到", "暂无", "通用参考"],
        "required_aspects": ["案例数量", "来源标注"],
        "source": "模板知识库",
    },
    "roadmap": {
        "min_content_length": 30,
        "check_phrases": ["待补充"],
        "required_aspects": ["3个阶段"],
        "source": "规则引擎",
    },
    "action_plan": {
        "min_content_length": 20,
        "check_phrases": ["待补充"],
        "required_aspects": [],
        "source": "规则引擎",
    },
    "risks": {
        "min_content_length": 40,
        "check_phrases": ["待补充"],
        "required_aspects": ["风险项数"],
        "source": "规则引擎",
    },
    "instructor_comments": {
        "min_content_length": 30,
        "check_phrases": ["待补充", "人工点评"],
        "required_aspects": [],
        "source": "模板知识库",
    },
    "endgame": {
        "min_content_length": 50,
        "check_phrases": ["尚未生成", "待补充"],
        "required_aspects": ["私域", "生态", "OPC", "路径推演"],
        "source": "规则引擎",
    },
}
