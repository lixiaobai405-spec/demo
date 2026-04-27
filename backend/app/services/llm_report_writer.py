"""LLM-based deep writing for AI Innovation Reports."""

import json
import logging
import re
from typing import Any

from app.core.config import settings
from app.models.assessment import Assessment
from app.prompts.report_writer_prompt import ReportWriterPrompt
from app.schemas.assessment import (
    CanvasDiagnosisResult,
    CaseRecommendationResult,
    CompanyProfileResult,
    ReportData,
    ReportSectionData,
    ReportTableData,
    ScenarioRecommendationResult,
)
from app.services.report_builder import ReportBuilder

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS: list[tuple[str, str]] = [
    ("company_profile", "企业基本画像"),
    ("canvas_diagnosis", "当前商业模式画布诊断"),
    ("ai_readiness", "AI 成熟度评估"),
    ("priority_scenarios", "高优先级 AI 提效场景"),
    ("scenario_planning", "推荐场景详细规划"),
    ("competitiveness", "差异化竞争力设计"),
    ("cases", "参考案例与启示"),
    ("roadmap", "三阶段 AI 创新路线图"),
    ("action_plan", "90 天行动计划"),
    ("risks", "风险与阻力"),
    ("instructor_comments", "讲师点评区"),
]

PLACEHOLDER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"待补充",
        r"待填写",
        r"未补充",
        r"tbd",
        r"placeholder",
        r"示例内容",
    )
]

ROI_SANITIZE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(ROI[^0-9\n，。,；;]{0,8})\d+(?:\.\d+)?%?", re.IGNORECASE),
        r"\1待验证",
    ),
    (
        re.compile(r"(投资回报[^0-9\n，。,；;]{0,8})\d+(?:\.\d+)?%?"),
        r"\1待验证",
    ),
    (
        re.compile(
            r"((?:提升|增长|下降|降低|减少|节省|缩短)[^0-9\n，。,；;]{0,8})\d+(?:\.\d+)?%"
        ),
        r"\1待验证",
    ),
]


class LLMReportWriter:
    """Generate AI Innovation Reports using optional LLM deep writing mode."""

    def __init__(self) -> None:
        self.report_builder = ReportBuilder()
        self.prompt_builder = ReportWriterPrompt()

    def build(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
        case_recommendation: CaseRecommendationResult | None,
        mode: str = "template",
    ) -> tuple[ReportData, dict[str, Any]]:
        metadata: dict[str, Any] = {
            "generation_mode": "template",
            "used_llm": False,
            "used_rag": False,
            "warnings": [],
        }

        actual_mode, resolve_warnings = self._resolve_mode(mode)
        metadata["generation_mode"] = actual_mode
        metadata["warnings"].extend(resolve_warnings)

        if actual_mode == "template":
            return self._build_template_report(
                assessment,
                profile,
                canvas_diagnosis,
                scenario_recommendation,
                case_recommendation,
                metadata,
            )

        llm_report, llm_metadata = self._try_llm_generation(
            assessment=assessment,
            profile=profile,
            canvas_diagnosis=canvas_diagnosis,
            scenario_recommendation=scenario_recommendation,
            case_recommendation=case_recommendation,
        )

        metadata["warnings"].extend(llm_metadata.get("warnings", []))
        metadata["used_rag"] = bool(llm_metadata.get("used_rag", False))

        if llm_report is not None:
            metadata["used_llm"] = True
            metadata["generation_mode"] = "llm"
            llm_report.generated_with = "llm"
            metadata["warnings"] = self._deduplicate_warnings(metadata["warnings"])
            return llm_report, metadata

        metadata["generation_mode"] = "template"
        metadata["used_llm"] = False
        metadata["warnings"].append("LLM report generation unavailable, fallback to template mode.")
        return self._build_template_report(
            assessment,
            profile,
            canvas_diagnosis,
            scenario_recommendation,
            case_recommendation,
            metadata,
        )

    def _build_template_report(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
        case_recommendation: CaseRecommendationResult | None,
        metadata: dict[str, Any],
    ) -> tuple[ReportData, dict[str, Any]]:
        report = self.report_builder.build(
            assessment=assessment,
            profile=profile,
            canvas_diagnosis=canvas_diagnosis,
            scenario_recommendation=scenario_recommendation,
            case_recommendation=case_recommendation,
        )
        report.generated_with = "template"
        metadata["warnings"] = self._deduplicate_warnings(metadata["warnings"])
        return report, metadata

    def _resolve_mode(self, requested_mode: str) -> tuple[str, list[str]]:
        warnings: list[str] = []
        valid_modes = {"template", "llm", "template_fallback"}
        if requested_mode not in valid_modes:
            warnings.append(
                f"Unknown report mode '{requested_mode}', switched to template mode."
            )
            return "template", warnings

        if requested_mode == "template":
            return "template", warnings

        if not getattr(settings, "llm_report_enabled", False):
            warnings.append(
                "LLM report generation is disabled by configuration, switched to template mode."
            )
            return "template", warnings

        if not settings.openai_api_key:
            warnings.append(
                "OPENAI_API_KEY is missing, switched to template mode."
            )
            return "template", warnings

        if not settings.openai_model:
            warnings.append(
                "OPENAI_MODEL is missing, switched to template mode."
            )
            return "template", warnings

        return requested_mode, warnings

    def _try_llm_generation(
        self,
        assessment: Assessment,
        profile: CompanyProfileResult,
        canvas_diagnosis: CanvasDiagnosisResult,
        scenario_recommendation: ScenarioRecommendationResult,
        case_recommendation: CaseRecommendationResult | None,
    ) -> tuple[ReportData | None, dict[str, Any]]:
        metadata: dict[str, Any] = {"used_rag": False, "warnings": []}

        try:
            system_prompt = self.prompt_builder.build_system_prompt()
            user_prompt = self.prompt_builder.build_user_prompt(
                company_input=self._assessment_to_dict(assessment),
                company_profile=self._profile_to_dict(profile),
                canvas_diagnosis=self._canvas_to_dict(canvas_diagnosis),
                top_scenarios=self._scenarios_to_list(scenario_recommendation),
                case_recommendation=self._cases_to_dict(case_recommendation),
            )

            llm_response, llm_warning = self._call_llm(system_prompt, user_prompt)
            if llm_warning:
                metadata["warnings"].append(llm_warning)
            if llm_response is None:
                return None, metadata

            parsed_sections, parse_warnings, fatal_error = self._parse_llm_response(
                llm_response
            )
            metadata["warnings"].extend(parse_warnings)
            if fatal_error or parsed_sections is None:
                return None, metadata

            ai_readiness_score = self.report_builder._calculate_ai_readiness_score(
                profile=profile,
                canvas_diagnosis=canvas_diagnosis,
                scenario_recommendation=scenario_recommendation,
            )

            report = ReportData(
                title=f"{assessment.company_name} AI 商业创新建议报告",
                subtitle=f"{assessment.industry} | {assessment.region} | LLM 增强版",
                company_name=assessment.company_name,
                industry=assessment.industry,
                company_size=assessment.company_size,
                region=assessment.region,
                annual_revenue_range=assessment.annual_revenue_range,
                ai_readiness_score=ai_readiness_score,
                ai_readiness_summary=self.report_builder._build_ai_readiness_summary(
                    ai_readiness_score,
                    profile,
                    canvas_diagnosis,
                ),
                generated_with="llm",
                sections=parsed_sections,
            )
            metadata["warnings"] = self._deduplicate_warnings(metadata["warnings"])
            return report, metadata
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("LLM report generation failed: %s", exc)
            metadata["warnings"].append(
                f"LLM report generation failed: {exc.__class__.__name__}."
            )
            return None, metadata

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> tuple[str | None, str | None]:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

            timeout = getattr(settings, "llm_report_timeout_seconds", 60)
            response = client.chat.completions.create(
                model=settings.openai_model,
                temperature=0.5,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                timeout=timeout,
            )
            return response.choices[0].message.content or "", None
        except Exception as exc:
            logger.error("OpenAI API call failed: %s", exc)
            return None, f"LLM API request failed: {exc.__class__.__name__}."

    def _parse_llm_response(
        self,
        raw_response: str,
    ) -> tuple[list[ReportSectionData] | None, list[str], bool]:
        warnings: list[str] = []
        fatal_error = False

        try:
            json_str = self._extract_json_object(raw_response)
            data = json.loads(json_str)
        except Exception as exc:
            logger.error("Failed to parse LLM response JSON: %s", exc)
            return None, ["LLM response is not valid JSON."], True

        sections_data = data.get("sections")
        if not isinstance(sections_data, list) or not sections_data:
            return None, ["LLM response did not include a valid sections array."], True

        raw_warnings = data.get("warnings") or []
        if isinstance(raw_warnings, list):
            warnings.extend(str(item) for item in raw_warnings if str(item).strip())

        sections_by_title: dict[str, ReportSectionData] = {}
        for raw_section in sections_data:
            if not isinstance(raw_section, dict):
                warnings.append("LLM response contained a non-object section and it was ignored.")
                continue

            title = str(raw_section.get("title", "")).strip()
            key = str(raw_section.get("key", "")).strip()
            matched_key = self._key_for_title(title) or key
            if not title or not matched_key:
                warnings.append("LLM response contained a section without a valid title/key and it was ignored.")
                continue

            if title in sections_by_title:
                warnings.append(f"Duplicate section '{title}' detected; only the first one was kept.")
                continue

            content, content_warnings = self._sanitize_text(
                str(raw_section.get("content", "")).strip(),
                title=title,
            )
            warnings.extend(content_warnings)
            if not content:
                warnings.append(f"Section '{title}' has empty content.")

            bullets = []
            raw_bullets = raw_section.get("bullets") or []
            if isinstance(raw_bullets, list):
                for item in raw_bullets:
                    sanitized_bullet, bullet_warnings = self._sanitize_text(
                        str(item).strip(),
                        title=title,
                    )
                    warnings.extend(bullet_warnings)
                    if sanitized_bullet:
                        bullets.append(sanitized_bullet)

            note = None
            if raw_section.get("note"):
                note, note_warnings = self._sanitize_text(
                    str(raw_section.get("note", "")).strip(),
                    title=title,
                )
                warnings.extend(note_warnings)
                if not note:
                    note = None

            table = self._parse_table(raw_section.get("table"), title, warnings)
            section = ReportSectionData(
                key=matched_key,
                title=title,
                content=content,
                bullets=bullets,
                table=table,
                note=note,
            )
            self._append_placeholder_warnings(section, warnings)
            sections_by_title[title] = section

        missing_titles = [
            title for _, title in REQUIRED_SECTIONS if title not in sections_by_title
        ]
        if missing_titles:
            warnings.append(
                "Missing required report sections: " + "、".join(missing_titles) + "."
            )
            fatal_error = True

        ordered_sections: list[ReportSectionData] = []
        for key, title in REQUIRED_SECTIONS:
            section = sections_by_title.get(title)
            if section is None:
                continue
            section.key = key
            if not section.content.strip():
                warnings.append(f"Section '{title}' is empty after validation.")
                fatal_error = True
            ordered_sections.append(section)

        if len(ordered_sections) != len(REQUIRED_SECTIONS):
            fatal_error = True

        return ordered_sections if ordered_sections else None, self._deduplicate_warnings(warnings), fatal_error

    def _parse_table(
        self,
        raw_table: Any,
        title: str,
        warnings: list[str],
    ) -> ReportTableData | None:
        if raw_table is None:
            return None
        if not isinstance(raw_table, dict):
            warnings.append(f"Section '{title}' contains an invalid table payload and it was ignored.")
            return None

        columns = raw_table.get("columns") or []
        rows = raw_table.get("rows") or []
        if not isinstance(columns, list) or not isinstance(rows, list):
            warnings.append(f"Section '{title}' contains an invalid table structure and it was ignored.")
            return None

        sanitized_columns = [str(item).strip() for item in columns if str(item).strip()]
        sanitized_rows: list[list[str]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            sanitized_row: list[str] = []
            for cell in row:
                sanitized_cell, cell_warnings = self._sanitize_text(str(cell).strip(), title=title)
                warnings.extend(cell_warnings)
                sanitized_row.append(sanitized_cell)
            if sanitized_row:
                sanitized_rows.append(sanitized_row)

        if not sanitized_columns or not sanitized_rows:
            return None

        return ReportTableData(columns=sanitized_columns, rows=sanitized_rows)

    def _sanitize_text(self, value: str, title: str) -> tuple[str, list[str]]:
        warnings: list[str] = []
        sanitized = value.strip()

        for pattern, replacement in ROI_SANITIZE_PATTERNS:
            updated = pattern.sub(replacement, sanitized)
            if updated != sanitized:
                warnings.append(
                    f"Section '{title}' contained suspicious ROI or percentage claims; numbers were replaced with '待验证'."
                )
                sanitized = updated

        return sanitized, warnings

    def _append_placeholder_warnings(
        self,
        section: ReportSectionData,
        warnings: list[str],
    ) -> None:
        values = [section.content, *(section.bullets or [])]
        if section.note:
            values.append(section.note)

        has_placeholder = any(
            pattern.search(value)
            for value in values
            for pattern in PLACEHOLDER_PATTERNS
        )
        if has_placeholder:
            warnings.append(
                f"Section '{section.title}' still contains placeholder-like content."
            )

    def _extract_json_object(self, text: str) -> str:
        start = text.find("{")
        if start == -1:
            return "{}"

        depth = 0
        in_string = False
        escape_next = False

        for index, char in enumerate(text[start:], start):
            if escape_next:
                escape_next = False
                continue
            if char == "\\":
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]

        return "{}"

    def _key_for_title(self, title: str) -> str | None:
        for key, expected_title in REQUIRED_SECTIONS:
            if expected_title == title:
                return key
        return None

    def _deduplicate_warnings(self, warnings: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for warning in warnings:
            cleaned = warning.strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            deduped.append(cleaned)
        return deduped

    def _assessment_to_dict(self, assessment: Assessment) -> dict[str, Any]:
        return {
            "company_name": assessment.company_name,
            "industry": assessment.industry,
            "company_size": assessment.company_size,
            "region": assessment.region,
            "annual_revenue_range": assessment.annual_revenue_range,
            "core_products": assessment.core_products,
            "target_customers": assessment.target_customers,
            "current_challenges": assessment.current_challenges,
            "ai_goals": assessment.ai_goals,
            "available_data": assessment.available_data,
        }

    def _profile_to_dict(self, profile: CompanyProfileResult) -> dict[str, Any]:
        return {
            "industry_position": profile.company_summary,
            "business_model": profile.value_proposition,
            "pain_points": "; ".join(profile.key_challenges),
            "data_readiness": profile.digital_and_ai_readiness,
            "ai_opportunities": "; ".join(profile.priority_ai_directions),
        }

    def _canvas_to_dict(self, canvas: CanvasDiagnosisResult) -> dict[str, Any]:
        return {
            "overall_score": canvas.overall_score,
            "weakest_blocks": canvas.weakest_blocks,
            "recommended_focus": canvas.recommended_focus,
            "canvas": {
                block.key: block.current_state
                for block in canvas.canvas.blocks
                if hasattr(block, "key") and hasattr(block, "current_state")
            },
        }

    def _scenarios_to_list(
        self,
        scenarios: ScenarioRecommendationResult,
    ) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "category": item.category,
                "score": item.score,
                "summary": item.summary,
                "reasons": list(item.reasons) if item.reasons else [],
                "data_requirements": list(item.data_requirements)
                if item.data_requirements
                else [],
            }
            for item in scenarios.top_scenarios
        ]

    def _cases_to_dict(
        self,
        cases: CaseRecommendationResult | None,
    ) -> dict[str, Any] | None:
        if cases is None:
            return None

        return {
            "top_cases": [
                {
                    "title": case.title,
                    "industry": case.industry,
                    "fit_score": case.fit_score,
                    "summary": case.summary,
                    "match_reasons": list(case.match_reasons) if case.match_reasons else [],
                    "cautions": list(case.cautions) if case.cautions else [],
                }
                for case in cases.top_cases
            ]
        }
