from datetime import date
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.score import ScoreReportType, ScoreSubmissionInput
from app.services.score_service import ScoreService


def test_score_markdown_render_contains_required_sections() -> None:
    service = ScoreService()
    submission = ScoreSubmissionInput(
        name="王五",
        org="创新部",
        report_type=ScoreReportType.WEN_GU_ZHI_XIN,
        date=date(2026, 5, 23),
        note="备注信息",
        transcript="录音转写内容",
    )
    llm_result = service._build_mock_llm_result(
        submission,
        "一份完整的文档内容，包含目标、问题、行动与结果。",
    )
    result = service._build_result_payload(submission, llm_result)
    markdown = service.render_markdown(submission, result)

    assert "# 汇报评分报告" in markdown
    assert "## 总分" in markdown
    assert "## 总评" in markdown
    assert "## 各维度评分明细" in markdown
    assert "## 结论与建议" in markdown
    assert "本报告由 AI 智能体自动生成，仅供参考" in markdown
