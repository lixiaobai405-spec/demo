from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.prompts.score_writer_prompt import ScoreWriterPrompt
from app.schemas.score import ScoreReportType


def test_score_prompt_contains_rubric_and_json_contract() -> None:
    prompt = ScoreWriterPrompt.build_system_prompt(ScoreReportType.WEN_GU_ZHI_XIN)

    assert "温故知新" in prompt
    assert "战略链接与价值认知" in prompt
    assert "逻辑的严谨性和链条完整性" in prompt
    assert '"overall_comment"' in prompt
    assert '"dimensions"' in prompt
    assert "只输出合法 JSON" in prompt


def test_score_user_prompt_wraps_document_and_transcript() -> None:
    prompt = ScoreWriterPrompt.build_user_prompt(
        document_text="文档内容A",
        transcript_text="录音内容B",
    )

    assert "---文档内容开始---" in prompt
    assert "文档内容A" in prompt
    assert "---录音转写文本开始---" in prompt
    assert "录音内容B" in prompt
