from app.schemas.assessment import (
    ReportCardData,
    ReportData,
    ReportSectionData,
    ReportTableData,
)


class MarkdownExporter:
    def render(self, report_data: ReportData) -> str:
        lines: list[str] = [
            f"# {report_data.title}",
            "",
            report_data.subtitle,
            "",
            f"- 企业：{report_data.company_name}",
            f"- 行业：{report_data.industry}",
            f"- 规模：{report_data.company_size}",
            f"- 区域：{report_data.region}",
            f"- 营收范围：{report_data.annual_revenue_range}",
            f"- AI 就绪度评分：{report_data.ai_readiness_score}",
            "",
            "> 本报告基于当前问卷、已生成的结构化诊断结果和模板规则生成，不使用自由写作式 LLM 深度生成。",
            "",
        ]

        for index, section in enumerate(report_data.sections, start=1):
            lines.extend(self._render_section(index, section))

        return "\n".join(lines).strip() + "\n"

    def _render_section(self, index: int, section: ReportSectionData) -> list[str]:
        lines = [f"## {index}. {section.title}", "", section.content, ""]

        if section.bullets:
            lines.extend(f"- {item}" for item in section.bullets)
            lines.append("")

        for card in section.cards:
            lines.extend(self._render_card(card))

        if section.table:
            lines.extend(self._render_table(section.table))

        if section.note:
            lines.extend(["", f"> 备注：{section.note}", ""])

        return lines

    def _render_card(self, card: ReportCardData) -> list[str]:
        lines = [f"### {card.title}"]
        if card.subtitle:
            lines.append(f"*{card.subtitle}*")
        if card.highlight:
            lines.append(f"**{card.highlight}**")
        lines.extend(["", card.content, ""])
        lines.extend(f"- {item}" for item in card.bullets)
        lines.append("")
        return lines

    def _render_table(self, table: ReportTableData) -> list[str]:
        if not table.columns:
            return []

        header = "| " + " | ".join(table.columns) + " |"
        divider = "| " + " | ".join(["---"] * len(table.columns)) + " |"
        rows = [header, divider]
        for row in table.rows:
            rows.append("| " + " | ".join(self._escape_cell(cell) for cell in row) + " |")
        rows.append("")
        return rows

    def _escape_cell(self, value: str) -> str:
        return value.replace("|", "\\|").replace("\n", "<br>")
