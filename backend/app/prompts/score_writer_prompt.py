"""Prompt builders for the scoring domain."""

from __future__ import annotations

from app.schemas.score import ScoreReportType, ScoreRubricDefinition, get_score_rubric


class ScoreWriterPrompt:
    @staticmethod
    def build_system_prompt(report_type: ScoreReportType | str) -> str:
        report_type_text = (
            report_type.value if hasattr(report_type, "value") else str(report_type)
        )
        rubric = get_score_rubric(ScoreReportType(report_type_text))
        transcript_dimensions = [
            item.name
            for item in rubric.dimensions
            if item.material_source == "录音转写"
        ]
        document_dimensions = [
            item.name
            for item in rubric.dimensions
            if item.material_source == "文档"
        ]
        return f"""
你是专业培训评分助手，必须严格按照给定量化评分标准，对汇报材料进行逐维度评分。

评分对象：{report_type_text}

【评分标准】
{ScoreWriterPrompt._format_rubric(rubric)}

【材料说明】
- 文档材料：用于评判 {ScoreWriterPrompt._join(document_dimensions)}
- 录音转写文本：用于评判 {ScoreWriterPrompt._join(transcript_dimensions)}
- 若录音转写文本为空或标注未提供，对应维度 score 填 null，level_label 填“未评分”，evidence 填“录音材料未提供”，comment 说明无法完成该维度评分

【打分规则】
1. 各子维度独立评分，范围 0.0-10.0，保留 1 位小数，尽量避免整数
2. evidence 引用材料原文作为依据，1-2 句，不超过 80 字
3. comment 给出维度评价，2-3 句，不超过 120 字
4. 只允许输出 rubric 中已经出现的维度、一级维度名称和材料来源
5. 不得新增字段，不得输出代码块，不得输出任何解释性前言或结尾

【输出要求】
只输出合法 JSON，结构如下：
{{
  "report_type": "{report_type_text}",
  "dimensions": [
    {{
      "id": 1,
      "name": "示例维度名称",
      "level": "一级维度名称",
      "material_source": "文档",
      "score": 8.5,
      "level_label": "优秀",
      "evidence": "引用材料原文作为依据",
      "comment": "给出维度评价"
    }}
  ],
  "overall_comment": "3-5 句整体评价，涵盖亮点与主要改进方向"
}}
""".strip()

    @staticmethod
    def build_user_prompt(document_text: str, transcript_text: str) -> str:
        normalized_document = document_text.strip() or "未提供"
        normalized_transcript = transcript_text.strip() or "未提供"
        return f"""
---文档内容开始---
{normalized_document}
---文档内容结束---

---录音转写文本开始---
{normalized_transcript}
---录音转写文本结束---

请按评分标准对以上材料评分，只输出 JSON。
""".strip()

    @staticmethod
    def _format_rubric(rubric: ScoreRubricDefinition) -> str:
        lines: list[str] = []
        for item in rubric.dimensions:
            lines.append(
                f"- #{item.id} {item.level_name} / {item.name} / {item.material_source} / 权重 {item.weight_pct:.1f}%"
            )
        lines.extend(
            [
                "",
                "统一锚定规则：",
                "- 9.0-10.0：卓越",
                "- 7.5-8.9：优秀",
                "- 6.0-7.4：良好",
                "- 4.0-5.9：合格",
                "- 0.0-3.9：不合格",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _join(values: list[str]) -> str:
        return "、".join(values) if values else "无"
