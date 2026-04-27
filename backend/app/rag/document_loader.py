"""Document loader for RAG knowledge sources."""
from pathlib import Path

import yaml

from app.rag.schemas import RAGChunk


class DocumentLoader:
    """Load documents from knowledge/raw directory."""

    def __init__(self, knowledge_dir: Path | None = None):
        self.knowledge_dir = knowledge_dir or Path(__file__).parent.parent.parent.parent.parent / "knowledge" / "raw"

    def load_yaml_cases(self) -> list[dict]:
        """Load industry cases from YAML file."""
        cases_file = self.knowledge_dir / "industry_cases.yaml"
        if not cases_file.exists():
            return []

        with open(cases_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("cases", [])

    def load_yaml_scenarios(self) -> list[dict]:
        """Load AI scenarios from YAML file."""
        scenarios_file = self.knowledge_dir / "ai_scenarios.yaml"
        if not scenarios_file.exists():
            return []

        with open(scenarios_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("scenarios", [])

    def load_markdown_file(self, filename: str) -> str | None:
        """Load a markdown file from knowledge directory."""
        md_file = self.knowledge_dir / filename
        if not md_file.exists():
            return None

        with open(md_file, encoding="utf-8") as f:
            return f.read()

    def load_all_sources(self) -> dict[str, list[dict] | str | None]:
        """Load all knowledge sources."""
        return {
            "cases": self.load_yaml_cases(),
            "scenarios": self.load_yaml_scenarios(),
            "canvas_guide": self.load_markdown_file("business_canvas.md"),
            "report_templates": self.load_markdown_file("report_templates.md"),
            "risk_playbook": self.load_markdown_file("risk_playbook.md"),
        }