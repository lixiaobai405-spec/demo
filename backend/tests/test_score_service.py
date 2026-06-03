from datetime import date
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.score import ScoreReportType, ScoreSubmissionInput
from app.services.score_service import ScoreService


def test_score_service_marks_transcript_dimensions_unscored_when_missing() -> None:
    service = ScoreService()
    submission = ScoreSubmissionInput(
        name="张三",
        org="测试部门",
        report_type=ScoreReportType.ACTION_LEARNING,
        date=date(2026, 5, 23),
        note=None,
        transcript="",
    )

    llm_result = service._build_mock_llm_result(
        submission,
        "这是行动学习文档内容，包含问题、方法、行动与改进。",
    )
    transcript_dimensions = [
        item for item in llm_result.dimensions if item.material_source == "录音转写"
    ]

    assert transcript_dimensions
    assert all(item.score is None for item in transcript_dimensions)
    assert all(item.level_label == "未评分" for item in transcript_dimensions)


def test_score_service_aggregates_weighted_total_to_hundred_scale() -> None:
    service = ScoreService()
    submission = ScoreSubmissionInput(
        name="李四",
        org="测试组织",
        report_type=ScoreReportType.WEN_GU_ZHI_XIN,
        date=date(2026, 5, 23),
        note="",
        transcript="这里有录音转写文本，用于逻辑性和展现力评分。",
    )

    llm_result = service._build_mock_llm_result(
        submission,
        "这是一份温故知新文档，包含目标、问题、行动、结果与反思。",
    )
    result = service._build_result_payload(submission, llm_result)

    assert result.total_score > 0
    assert result.total_score <= 100
    assert len(result.dimensions) == 10
    assert sum(item.weight_pct for item in result.dimensions) == 100
