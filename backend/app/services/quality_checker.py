"""C3 Quality Checker: 章节级可信度评分 / 校验规则 / 无匹配内容规范 / 来源标注"""

from app.schemas.assessment import ReportData, ReportSectionData
from app.schemas.quality_guard import (
    QUALITY_RULES,
    ConfidenceLevel,
    OverallQualityReport,
    QualityFlag,
    SectionQualityReport,
    SourceType,
)


class QualityChecker:
    def audit(self, report: ReportData) -> OverallQualityReport:
        sections = []
        critical_flags = []
        total_score = 0
        section_count = max(len(report.sections), 1)

        for section in report.sections:
            qr = self._audit_section(section, report)
            sections.append(qr)
            for flag in qr.flags:
                if flag.level == "error":
                    critical_flags.append(flag)
            total_score += self._section_score(qr)

        overall_score = min(100, max(0, total_score // section_count))
        overall_confidence = self._infer_overall_confidence(overall_score, critical_flags)

        summary = self._build_summary(overall_score, overall_confidence, critical_flags, sections)
        suggestions = self._build_suggestions(sections)

        return OverallQualityReport(
            overall_score=overall_score,
            overall_confidence=overall_confidence,
            sections=sections,
            critical_flags=critical_flags,
            summary=summary,
            improvement_suggestions=suggestions,
        )

    def _audit_section(self, section: ReportSectionData, report: ReportData) -> SectionQualityReport:
        rules = QUALITY_RULES.get(section.key, {})
        flags: list[QualityFlag] = []
        missing: list[str] = []

        content = section.content or ""
        content_len = len(content)
        min_len = rules.get("min_content_length", 20)
        check_phrases = rules.get("check_phrases", ["待补充"])
        required_aspects = rules.get("required_aspects", [])

        # Rule 1: content length
        if content_len < min_len:
            flags.append(
                QualityFlag(
                    code="SHORT_CONTENT",
                    level="warn",
                    message=f"内容过短（{content_len}字符），建议补充至少{min_len}字符。",
                )
            )

        # Rule 2: placeholder phrases
        for phrase in check_phrases:
            if phrase in content:
                flags.append(
                    QualityFlag(
                        code="PLACEHOLDER_DETECTED",
                        level="warn",
                        message=f"检测到占位表述「{phrase}」，建议替换为实质性内容。",
                    )
                )
                break

        # Rule 3: required aspects
        for aspect in required_aspects:
            if aspect not in content and not any(aspect in b for b in section.bullets):
                missing.append(aspect)
                flags.append(
                    QualityFlag(
                        code="MISSING_ASPECT",
                        level="warn",
                        message=f"缺少关键信息要素「{aspect}」，建议补充。",
                    )
                )

        # Rule 4: card content quality
        for card in section.cards:
            if "待补充" in card.content or ("待补充" in (card.highlight or "")):
                flags.append(
                    QualityFlag(
                        code="PLACEHOLDER_CARD",
                        level="warn",
                        message=f"卡片「{card.title}」包含占位内容。",
                    )
                )

        # Rule 5: ROI / numeric claims validation
        if section.key in ("ai_readiness", "competitiveness", "roadmap", "endgame"):
            import re
            percent_claims = re.findall(r'(\d+\s*[-~]\s*\d+%|\d+%)', content)
            if percent_claims:
                has_caveat = any(kw in content for kw in ["预计", "预估", "可能", "参考", "视", "有待"])
                if not has_caveat:
                    flags.append(
                        QualityFlag(
                            code="UNQUALIFIED_CLAIM",
                            level="info",
                            message=f"发现量化表述（{percent_claims[0]}），建议添加「预计」「视情况」等限定词以提高可信度。",
                        )
                    )

        # Rule 6: case applicability
        if section.key == "cases":
            case_content = content + "".join(f"{c.title}{c.content}" for c in section.cards)
            if "待补充" in case_content or "未匹配" in case_content:
                flags.append(
                    QualityFlag(
                        code="INCOMPLETE_CASES",
                        level="info",
                        message="案例匹配不完整，建议后续扩充行业案例库以提高匹配精度。",
                    )
                )

        # Determine confidence
        error_count = sum(1 for f in flags if f.level == "error")
        warn_count = sum(1 for f in flags if f.level == "warn")
        has_actionable = content_len >= min_len and not any(p in content for p in check_phrases)

        if error_count > 0:
            confidence: ConfidenceLevel = "低"
        elif warn_count >= 2:
            confidence = "低"
        elif warn_count == 1:
            confidence = "中"
        else:
            confidence = "高"

        source: SourceType = rules.get("source", "模板知识库")
        if "llm" in report.generated_with.lower():
            source = "LLM生成"

        return SectionQualityReport(
            section_key=section.key,
            section_title=section.title,
            confidence=confidence,
            source=source,
            flags=flags,
            has_actionable_content=has_actionable,
            missing_aspects=missing,
        )

    @staticmethod
    def _section_score(qr: SectionQualityReport) -> int:
        base = 70
        for flag in qr.flags:
            if flag.level == "error":
                base -= 20
            elif flag.level == "warn":
                base -= 10
            elif flag.level == "info":
                base -= 3
        if not qr.has_actionable_content:
            base -= 20
        return max(0, min(100, base))

    @staticmethod
    def _infer_overall_confidence(score: int, critical_flags: list[QualityFlag]) -> ConfidenceLevel:
        if critical_flags:
            return "低"
        if score >= 80:
            return "高"
        if score >= 55:
            return "中"
        return "低"

    @staticmethod
    def _build_summary(
        score: int,
        confidence: ConfidenceLevel,
        critical_flags: list[QualityFlag],
        sections: list[SectionQualityReport],
    ) -> str:
        high_count = sum(1 for s in sections if s.confidence == "高")
        low_count = sum(1 for s in sections if s.confidence == "低")
        total = len(sections)

        parts = [
            f"整体质量评分 {score}/100，可信度「{confidence}」。",
            f"共 {total} 个章节：高可信度 {high_count} 个，中可信度 {total - high_count - low_count} 个，低可信度 {low_count} 个。",
        ]

        if critical_flags:
            parts.append(f"发现 {len(critical_flags)} 个关键问题需要关注。")
        else:
            parts.append("未发现关键错误，报告整体可用。")

        return "".join(parts)

    @staticmethod
    def _build_suggestions(sections: list[SectionQualityReport]) -> list[str]:
        suggestions: list[str] = []
        for s in sections:
            for flag in s.flags:
                if flag.level == "error":
                    suggestions.append(f"【{s.section_title}】{flag.message}")
        if not suggestions:
            for s in sections:
                if s.confidence == "低":
                    suggestions.append(f"建议重点优化「{s.section_title}」章节的内容质量。")
        if not suggestions:
            suggestions.append("当前报告质量良好，建议在人工审核后交付。")
        return suggestions[:5]
