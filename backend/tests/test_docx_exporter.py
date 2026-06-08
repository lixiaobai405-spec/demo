from pathlib import Path
import sys

from docx import Document

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.exporters.docx_exporter import DocxExporter  # noqa: E402
from app.schemas.assessment import ReportData  # noqa: E402


def test_docx_exporter_omits_ai_readiness_score_from_header(tmp_path) -> None:
    report = ReportData(
        title="测试企业 AI 商业创新建议报告",
        subtitle="零售 | 华东 | 模板化管理层阅读版",
        company_name="测试企业",
        industry="零售",
        company_size="100-499人",
        region="华东",
        annual_revenue_range="5000万-1亿元",
        ai_readiness_score=89,
        ai_readiness_summary="企业已经具备相对明确的试点条件。",
        generated_with="template",
        sections=[],
    )

    target = tmp_path / "report.docx"
    DocxExporter().export(report, target)

    document = Document(target)
    paragraph_text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "AI 就绪度评分" not in paragraph_text
    assert "企业已经具备相对明确的试点条件。" not in paragraph_text
