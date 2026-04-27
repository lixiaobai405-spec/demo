from html import escape

from app.schemas.assessment import (
    ReportCardData,
    ReportData,
    ReportSectionData,
    ReportTableData,
)


class HtmlExporter:
    def render_fragment(self, report_data: ReportData) -> str:
        sections_html = "".join(
            self._render_section(index, section)
            for index, section in enumerate(report_data.sections, start=1)
        )

        return f"""
<div style="font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; color: #0f172a;">
  <section style="padding: 32px; border-radius: 28px; background: linear-gradient(135deg, #0f172a, #1e293b); color: #f8fafc; margin-bottom: 28px;">
    <div style="display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap;">
      <div style="max-width: 760px;">
        <div style="display: inline-block; padding: 6px 12px; border-radius: 999px; background: rgba(34,211,238,0.14); color: #a5f3fc; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;">
          Structured Business Report
        </div>
        <h1 style="margin: 18px 0 8px; font-size: 34px; line-height: 1.2;">{escape(report_data.title)}</h1>
        <p style="margin: 0; color: #cbd5e1; font-size: 15px;">{escape(report_data.subtitle)}</p>
      </div>
      <div style="min-width: 240px; padding: 18px 20px; border-radius: 20px; background: rgba(255,255,255,0.08);">
        <div style="font-size: 12px; color: #cbd5e1; letter-spacing: 0.08em; text-transform: uppercase;">AI 就绪度评分</div>
        <div style="margin-top: 10px; font-size: 38px; font-weight: 700;">{report_data.ai_readiness_score}</div>
        <p style="margin: 10px 0 0; color: #e2e8f0; font-size: 14px; line-height: 1.7;">{escape(report_data.ai_readiness_summary)}</p>
      </div>
    </div>
    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px;">
      {self._meta_tag(f"企业：{report_data.company_name}")}
      {self._meta_tag(f"行业：{report_data.industry}")}
      {self._meta_tag(f"规模：{report_data.company_size}")}
      {self._meta_tag(f"区域：{report_data.region}")}
      {self._meta_tag(f"营收范围：{report_data.annual_revenue_range}")}
    </div>
  </section>
  {sections_html}
</div>
""".strip()

    def render_print_document(
        self,
        report_data: ReportData,
        metadata: dict | None = None,
    ) -> str:
        fragment = self.render_fragment(report_data)
        metadata_html = self._render_metadata(metadata or {})
        return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(report_data.title)}</title>
  <style>
    body {{
      margin: 0;
      background: #f8fafc;
      color: #0f172a;
      font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }}
    .print-shell {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 24px 60px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 12px;
      vertical-align: top;
      text-align: left;
      font-size: 14px;
      line-height: 1.7;
    }}
    th {{
      background: #e2e8f0;
    }}
    @media print {{
      body {{
        background: #fff;
      }}
      .print-shell {{
        padding: 0;
      }}
    }}
  </style>
</head>
<body>
  <div class="print-shell">
    {metadata_html}
    {fragment}
  </div>
</body>
</html>
""".strip()

    def _render_section(self, index: int, section: ReportSectionData) -> str:
        bullets_html = ""
        if section.bullets:
            bullets_html = (
                "<ul style='margin: 16px 0 0 20px; color: #334155; line-height: 1.8;'>"
                + "".join(
                    f"<li style='margin-bottom: 8px;'>{escape(item)}</li>"
                    for item in section.bullets
                )
                + "</ul>"
            )

        cards_html = ""
        if section.cards:
            cards_html = (
                "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 20px;'>"
                + "".join(self._render_card(card) for card in section.cards)
                + "</div>"
            )

        table_html = ""
        if section.table:
            table_html = (
                "<div style='margin-top: 20px; overflow-x: auto;'>"
                + self._render_table(section.table)
                + "</div>"
            )

        note_html = ""
        if section.note:
            note_html = (
                f"<div style='margin-top: 18px; padding: 14px 16px; border-radius: 16px; background: #f8fafc; color: #475569; font-size: 14px; line-height: 1.8;'>"
                f"备注：{escape(section.note)}</div>"
            )

        return f"""
<section style="margin-bottom: 28px; padding: 28px; border-radius: 24px; border: 1px solid #e2e8f0; background: #ffffff;">
  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
    <div style="width: 36px; height: 36px; border-radius: 999px; background: #cffafe; color: #0f172a; display: flex; align-items: center; justify-content: center; font-weight: 700;">{index}</div>
    <h2 style="margin: 0; font-size: 24px; line-height: 1.3;">{escape(section.title)}</h2>
  </div>
  <p style="margin: 0; color: #334155; font-size: 15px; line-height: 1.9;">{escape(section.content)}</p>
  {bullets_html}
  {cards_html}
  {table_html}
  {note_html}
</section>
""".strip()

    def _render_card(self, card: ReportCardData) -> str:
        subtitle_html = (
            f"<div style='margin-top: 6px; color: #0891b2; font-size: 13px;'>{escape(card.subtitle)}</div>"
            if card.subtitle
            else ""
        )
        highlight_html = (
            f"<div style='margin-top: 10px; padding: 8px 10px; border-radius: 12px; background: #ecfeff; color: #155e75; font-size: 13px;'>{escape(card.highlight)}</div>"
            if card.highlight
            else ""
        )
        bullets_html = ""
        if card.bullets:
            bullets_html = (
                "<ul style='margin: 14px 0 0 18px; color: #334155; line-height: 1.75;'>"
                + "".join(
                    f"<li style='margin-bottom: 8px;'>{escape(item)}</li>"
                    for item in card.bullets
                )
                + "</ul>"
            )

        return f"""
<article style="padding: 20px; border-radius: 20px; background: #f8fafc; border: 1px solid #e2e8f0;">
  <h3 style="margin: 0; font-size: 18px; line-height: 1.35; color: #0f172a;">{escape(card.title)}</h3>
  {subtitle_html}
  {highlight_html}
  <p style="margin: 14px 0 0; color: #334155; font-size: 14px; line-height: 1.85;">{escape(card.content)}</p>
  {bullets_html}
</article>
""".strip()

    def _render_table(self, table: ReportTableData) -> str:
        header_html = "".join(f"<th>{escape(column)}</th>" for column in table.columns)
        body_html = "".join(
            "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
            for row in table.rows
        )
        return f"<table><thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>"

    def _meta_tag(self, text: str) -> str:
        return (
            "<span style='display: inline-flex; padding: 8px 12px; border-radius: 999px; "
            "background: rgba(255,255,255,0.08); color: #e2e8f0; font-size: 13px;'>"
            f"{escape(text)}</span>"
        )

    def _render_metadata(self, metadata: dict) -> str:
        generation_mode = str(metadata.get("generation_mode", "template"))
        used_llm = "true" if metadata.get("used_llm") else "false"
        used_rag = "true" if metadata.get("used_rag") else "false"
        warnings = metadata.get("warnings") or []
        warning_items = "".join(
            f"<li style='margin-bottom: 6px;'>{escape(str(item))}</li>"
            for item in warnings
        )
        warnings_html = (
            f"<ul style='margin: 12px 0 0 18px; color: #334155; line-height: 1.7;'>{warning_items}</ul>"
            if warning_items
            else "<p style='margin: 12px 0 0; color: #475569; font-size: 14px;'>无</p>"
        )

        return f"""
<section style="margin-bottom: 20px; padding: 20px 24px; border-radius: 20px; border: 1px solid #e2e8f0; background: #ffffff;">
  <h2 style="margin: 0 0 12px; font-size: 18px; color: #0f172a;">生成元信息</h2>
  <div style="display: flex; gap: 10px; flex-wrap: wrap;">
    <span style="display: inline-flex; padding: 8px 12px; border-radius: 999px; background: #e0f2fe; color: #075985; font-size: 13px;">generation_mode: {escape(generation_mode)}</span>
    <span style="display: inline-flex; padding: 8px 12px; border-radius: 999px; background: #ecfccb; color: #365314; font-size: 13px;">used_llm: {used_llm}</span>
    <span style="display: inline-flex; padding: 8px 12px; border-radius: 999px; background: #fae8ff; color: #86198f; font-size: 13px;">used_rag: {used_rag}</span>
  </div>
  <div style="margin-top: 16px;">
    <div style="font-size: 14px; font-weight: 600; color: #0f172a;">warnings</div>
    {warnings_html}
  </div>
</section>
""".strip()
