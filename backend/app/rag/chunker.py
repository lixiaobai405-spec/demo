"""Chunker for splitting documents into RAG chunks."""
import hashlib
from pathlib import Path

from app.rag.schemas import RAGChunk


class DocumentChunker:
    """Split documents into chunks for RAG."""

    def chunk_case(self, case: dict) -> RAGChunk:
        """Convert a case dict to a RAG chunk."""
        case_id = case.get("id", "unknown")
        content_parts = [
            case.get("title", ""),
            case.get("summary", ""),
        ]

        if case.get("reference_points"):
            content_parts.append("参考做法：" + "；".join(case["reference_points"]))
        if case.get("data_foundation"):
            content_parts.append("数据基础：" + "；".join(case["data_foundation"]))
        if case.get("cautions"):
            content_parts.append("注意事项：" + "；".join(case["cautions"]))

        content = "\n".join(content_parts)

        return RAGChunk(
            chunk_id=f"case_{case_id}",
            doc_id=f"industry_cases#{case_id}",
            source_file="industry_cases.yaml",
            source_type="case",
            title=case.get("title", case_id),
            content=content,
            metadata={
                "industry": case.get("industry"),
                "applicable_industries": case.get("applicable_industries", []),
            },
            industry=case.get("industry"),
            canvas_tags=case.get("canvas_blocks", []),
            pain_points=case.get("pain_keywords", []),
            ai_scenarios=case.get("scenario_keywords", []),
        )

    def chunk_scenario(self, scenario: dict) -> RAGChunk:
        """Convert a scenario dict to a RAG chunk."""
        scenario_id = scenario.get("id", "unknown")
        content_parts = [
            scenario.get("name", ""),
            scenario.get("description", ""),
        ]

        if scenario.get("value_points"):
            content_parts.append("价值点：" + "；".join(scenario["value_points"]))
        if scenario.get("implementation_hints"):
            content_parts.append("实施建议：" + "；".join(scenario["implementation_hints"]))

        content = "\n".join(content_parts)

        return RAGChunk(
            chunk_id=f"scenario_{scenario_id}",
            doc_id=f"ai_scenarios#{scenario_id}",
            source_file="ai_scenarios.yaml",
            source_type="scenario",
            title=scenario.get("name", scenario_id),
            content=content,
            metadata={
                "category": scenario.get("category"),
                "priority": scenario.get("priority"),
            },
            industry=None,
            canvas_tags=scenario.get("canvas_blocks", []),
            pain_points=scenario.get("pain_points", []),
            ai_scenarios=[scenario.get("name", scenario_id)],
        )

    def chunk_markdown(
        self,
        content: str,
        source_file: str,
        source_type: str,
        max_chunk_size: int = 1000,
    ) -> list[RAGChunk]:
        """Split markdown content into chunks by sections."""
        chunks = []
        lines = content.split("\n")
        current_section = ""
        current_title = "Introduction"

        for line in lines:
            if line.startswith("## "):
                # Save previous section if substantial
                if len(current_section.strip()) >= 100:
                    chunk_id = hashlib.md5(current_section.encode()).hexdigest()[:8]
                    chunks.append(RAGChunk(
                        chunk_id=f"{source_type}_{chunk_id}",
                        doc_id=source_file,
                        source_file=source_file,
                        source_type=source_type,
                        title=current_title,
                        content=current_section.strip(),
                        metadata={"section": current_title},
                    ))
                current_title = line[3:].strip()
                current_section = line + "\n"
            else:
                current_section += line + "\n"

        # Save last section
        if len(current_section.strip()) >= 100:
            chunk_id = hashlib.md5(current_section.encode()).hexdigest()[:8]
            chunks.append(RAGChunk(
                chunk_id=f"{source_type}_{chunk_id}",
                doc_id=source_file,
                source_file=source_file,
                source_type=source_type,
                title=current_title,
                content=current_section.strip(),
                metadata={"section": current_title},
            ))

        return chunks

    def chunk_all(
        self,
        cases: list[dict],
        scenarios: list[dict],
        canvas_guide: str | None,
        report_templates: str | None,
        risk_playbook: str | None,
    ) -> list[RAGChunk]:
        """Chunk all documents."""
        chunks = []

        for case in cases:
            chunks.append(self.chunk_case(case))

        for scenario in scenarios:
            chunks.append(self.chunk_scenario(scenario))

        if canvas_guide:
            chunks.extend(self.chunk_markdown(
                canvas_guide,
                "business_canvas.md",
                "canvas",
            ))

        if report_templates:
            chunks.extend(self.chunk_markdown(
                report_templates,
                "report_templates.md",
                "template",
            ))

        if risk_playbook:
            chunks.extend(self.chunk_markdown(
                risk_playbook,
                "risk_playbook.md",
                "risk",
            ))

        return chunks