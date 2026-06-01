from html import escape

from app.schemas.assessment import (
    ReportCardData,
    ReportData,
    ReportSectionData,
    ReportTableData,
)


class HtmlExporter:
    """Produces polished, print-ready HTML report fragment with warm design system."""

    # ── Design tokens ──
    COLORS = {
        "bg": "#FDFBF7",
        "surface": "#FFFDF9",
        "inset": "#F5F1E8",
        "text": "#2D2218",
        "text_secondary": "#5C4A3A",
        "text_muted": "#8B7355",
        "accent": "#B8752A",
        "accent_light": "#F5E6D0",
        "success": "#5d8a4a",
        "success_light": "#E8F0E0",
        "warn": "#c07020",
        "warn_light": "#FDF0E0",
        "border": "#E0D5C5",
        "border_light": "#EBE3D6",
        "shadow": "0 2px 12px rgba(44,30,16,0.06)",
        "shadow_card": "0 1px 4px rgba(44,30,16,0.04)",
    }

    def render_fragment(self, report_data: ReportData) -> str:
        c = self.COLORS
        sections_html = "".join(
            self._render_section(index, section)
            for index, section in enumerate(report_data.sections, start=1)
        )

        return f"""
<div style="font-family: 'PingFang SC','Noto Serif SC','Microsoft YaHei',sans-serif;color:{c['text']};background:{c['bg']};">
  <section style="padding:40px 36px;border-radius:24px;background:linear-gradient(135deg,#2D2218,#4A3728,#5C4A3A);color:#FDFBF7;margin-bottom:32px;box-shadow:0 4px 24px rgba(44,30,16,0.15);">
    <div style="display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;align-items:flex-start;">
      <div style="max-width:740px;">
        <div style="display:inline-flex;align-items:center;gap:8px;padding:6px 14px;border-radius:999px;background:rgba(245,230,208,0.15);color:{c['accent_light']};font-size:12px;letter-spacing:0.1em;text-transform:uppercase;">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{c['accent']};"></span>
          AI 商业创新报告
        </div>
        <h1 style="margin:20px 0 10px;font-family:'Noto Serif SC','PingFang SC',serif;font-size:36px;line-height:1.25;font-weight:700;">{escape(report_data.title)}</h1>
        <p style="margin:0;color:#D5C8B5;font-size:15px;line-height:1.6;">{escape(report_data.subtitle)}</p>
      </div>
      <div style="min-width:200px;padding:20px 22px;border-radius:18px;background:rgba(255,255,255,0.08);text-align:center;">
        <div style="font-size:11px;color:#C4B59D;letter-spacing:0.1em;text-transform:uppercase;">AI 就绪度</div>
        <div style="margin-top:6px;font-size:44px;font-weight:800;line-height:1;">{report_data.ai_readiness_score}</div>
        <p style="margin:10px 0 0;color:#C4B59D;font-size:13px;line-height:1.7;">{escape(report_data.ai_readiness_summary)}</p>
      </div>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:22px;">
      {self._meta_tag(f"企业：{report_data.company_name}")}
      {self._meta_tag(f"行业：{report_data.industry}")}
      {self._meta_tag(f"规模：{report_data.company_size}")}
      {self._meta_tag(f"区域：{report_data.region}")}
      {self._meta_tag(f"营收：{report_data.annual_revenue_range}")}
    </div>
  </section>
  {sections_html}
  <footer style="margin-top:40px;padding:24px;border-radius:18px;background:{c['inset']};text-align:center;color:{c['text_muted']};font-size:13px;line-height:1.8;">
    <p style="margin:0;">本报告由 AI 商业创新智能体自动生成 · 数据来源为企业自填问卷与规则引擎分析</p>
    <p style="margin:4px 0 0;">报告内容仅供管理层参考，不构成投资决策或财务承诺</p>
  </footer>
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
      background: #FDFBF7;
      color: #2D2218;
      font-family: 'PingFang SC','Noto Serif SC','Microsoft YaHei',sans-serif;
    }}
    .print-shell {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 24px 60px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      border: 1px solid #E0D5C5;
      padding: 12px 14px;
      vertical-align: top;
      text-align: left;
      line-height: 1.7;
    }}
    th {{
      background: #F5F1E8;
      font-weight: 600;
      color: #2D2218;
    }}
    @media print {{
      body {{ background: #fff; }}
      .print-shell {{ padding: 0; }}
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
        c = self.COLORS

        bullets_html = ""
        if section.bullets:
            bullets_html = (
                "<ul style='margin:16px 0 0 20px;color:" + c["text_secondary"] + ";line-height:1.9;font-size:14px;'>"
                + "".join(
                    f"<li style='margin-bottom:8px;padding-left:4px;'>{escape(item)}</li>"
                    for item in section.bullets
                )
                + "</ul>"
            )

        cards_html = ""
        if section.cards:
            cards_html = (
                "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:20px;'>"
                + "".join(self._render_card(card) for card in section.cards)
                + "</div>"
            )

        table_html = ""
        if section.table:
            table_html = (
                "<div style='margin-top:20px;overflow-x:auto;border-radius:14px;border:1px solid " + c["border"] + ";'>"
                + self._render_table(section.table, section.key)
                + "</div>"
            )

        note_html = ""
        if section.note:
            note_html = (
                f"<div style='margin-top:18px;padding:14px 18px;border-radius:14px;background:{c['accent_light']};color:{c['text_secondary']};font-size:13px;line-height:1.8;border-left:4px solid {c['accent']};'>"
                f"<strong>备注：</strong>{escape(section.note)}</div>"
            )

        return f"""
<section style="margin-bottom:28px;padding:32px 30px;border-radius:20px;border:1px solid {c['border_light']};background:{c['surface']};box-shadow:{c['shadow_card']};">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid {c['border_light']};">
    <div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,{c['accent']},{c['warn']});color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;flex-shrink:0;">{index}</div>
    <h2 style="margin:0;font-family:'Noto Serif SC','PingFang SC',serif;font-size:22px;line-height:1.3;color:{c['text']};">{escape(section.title)}</h2>
  </div>
  <p style="margin:0;color:{c['text_secondary']};font-size:15px;line-height:2;">{escape(section.content)}</p>
  {bullets_html}
  {cards_html}
  {table_html}
  {note_html}
</section>
""".strip()

    def _render_card(self, card: ReportCardData) -> str:
        c = self.COLORS

        subtitle_html = ""
        if card.subtitle:
            subtitle_html = (
                f"<div style='margin-top:4px;color:{c['accent']};font-size:12px;letter-spacing:0.04em;'>"
                f"{escape(card.subtitle)}</div>"
            )

        highlight_html = ""
        if card.highlight:
            highlight_html = (
                f"<div style='margin-top:10px;padding:8px 12px;border-radius:10px;background:{c['accent_light']};color:{c['accent']};font-size:13px;font-weight:500;'>"
                f"{escape(card.highlight)}</div>"
            )

        bullets_html = ""
        if card.bullets:
            bullets_html = (
                "<ul style='margin:12px 0 0 16px;color:" + c["text_secondary"] + ";line-height:1.8;font-size:13px;'>"
                + "".join(
                    f"<li style='margin-bottom:6px;'>{escape(item)}</li>"
                    for item in card.bullets
                )
                + "</ul>"
            )

        content_style = f"margin:12px 0 0;color:{c['text_secondary']};font-size:14px;line-height:1.85;"
        if card.title == "核心竞争力提升路径":
            content_style += "white-space:pre-line;"

        return f"""
<article style="padding:20px;border-radius:16px;background:{c['inset']};border:1px solid {c['border_light']};transition:box-shadow 0.2s;">
  <h3 style="margin:0;font-size:16px;line-height:1.4;color:{c['text']};font-weight:600;">{escape(card.title)}</h3>
  {subtitle_html}
  {highlight_html}
  <p style="{content_style}">{escape(card.content)}</p>
  {bullets_html}
</article>
""".strip()

    def _render_table(self, table: ReportTableData, section_key: str | None = None) -> str:
        if section_key == "competitiveness":
            header_style = (
                "padding:12px 14px;background:linear-gradient(135deg,#4A3728,#6A513A);color:#FFF8EE;"
                "font-weight:700;border-color:rgba(255,248,238,0.16);"
            )
            cell_style = "padding:14px;vertical-align:top;background:#FFFDF9;color:#2D2218;"
        else:
            header_style = "padding:10px 14px;"
            cell_style = "padding:10px 14px;"

        header_html = "".join(
            f"<th style='{header_style}'>{escape(col)}</th>"
            for col in table.columns
        )
        body_html = "".join(
            "<tr>"
            + "".join(
                f"<td style='{cell_style}'>{escape(cell).replace(chr(10), '<br />')}</td>"
                for cell in row
            )
            + "</tr>"
            for row in table.rows
        )
        return f"<table><thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>"

    def _meta_tag(self, text: str) -> str:
        c = self.COLORS
        return (
            "<span style='display:inline-flex;padding:7px 12px;border-radius:999px;"
            f"background:rgba(255,255,255,0.08);color:#D5C8B5;font-size:13px;'>"
            f"{escape(text)}</span>"
        )

    def _render_metadata(self, metadata: dict) -> str:
        c = self.COLORS
        generation_mode = str(metadata.get("generation_mode", "template"))
        used_llm = "true" if metadata.get("used_llm") else "false"
        used_rag = "true" if metadata.get("used_rag") else "false"
        warnings = metadata.get("warnings") or []
        warning_items = "".join(
            f"<li style='margin-bottom:6px;'>{escape(str(w))}</li>"
            for w in warnings
        )
        warnings_html = (
            f"<ul style='margin:12px 0 0 18px;color:{c['text_secondary']};line-height:1.7;'>{warning_items}</ul>"
            if warning_items
            else f"<p style='margin:12px 0 0;color:{c['text_muted']};font-size:14px;'>无</p>"
        )

        return f"""
<section style="margin-bottom:20px;padding:20px 24px;border-radius:18px;border:1px solid {c['border']};background:{c['surface']};">
  <h2 style="margin:0 0 12px;font-size:16px;color:{c['text']};">生成元信息</h2>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">
    <span style="display:inline-flex;padding:7px 12px;border-radius:999px;background:{c['accent_light']};color:{c['accent']};font-size:12px;">generation_mode: {escape(generation_mode)}</span>
    <span style="display:inline-flex;padding:7px 12px;border-radius:999px;background:{c['success_light']};color:{c['success']};font-size:12px;">used_llm: {used_llm}</span>
    <span style="display:inline-flex;padding:7px 12px;border-radius:999px;background:{c['warn_light']};color:{c['warn']};font-size:12px;">used_rag: {used_rag}</span>
  </div>
  <div style="margin-top:16px;">
    <div style="font-size:14px;font-weight:600;color:{c['text']};">warnings</div>
    {warnings_html}
  </div>
</section>
""".strip()
