from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import ROOT_DIR, settings

Base = declarative_base()


def _build_engine():
    if settings.database_url.startswith("sqlite:///") and ":memory:" not in settings.database_url:
        raw_database_path = Path(settings.database_url.replace("sqlite:///", "", 1))
        database_path = (
            raw_database_path
            if raw_database_path.is_absolute()
            else (ROOT_DIR / raw_database_path).resolve()
        )
        database_path.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(
            f"sqlite:///{database_path.as_posix()}",
            connect_args={"check_same_thread": False},
        )

    return create_engine(settings.database_url)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    from app.models.assessment import Assessment  # noqa: F401
    from app.models.case_recommendation import CaseRecommendation  # noqa: F401
    from app.models.canvas_diagnosis import CanvasDiagnosis  # noqa: F401
    from app.models.generated_report import GeneratedReport  # noqa: F401
    from app.models.scenario_recommendation import ScenarioRecommendation  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_generated_reports_table()


def _migrate_generated_reports_table() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "generated_reports" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("generated_reports")}
    required_columns = {
        "title": "ALTER TABLE generated_reports ADD COLUMN title VARCHAR(255)",
        "used_llm": "ALTER TABLE generated_reports ADD COLUMN used_llm BOOLEAN NOT NULL DEFAULT 0",
        "used_rag": "ALTER TABLE generated_reports ADD COLUMN used_rag BOOLEAN NOT NULL DEFAULT 0",
        "warnings": "ALTER TABLE generated_reports ADD COLUMN warnings TEXT",
        "content_markdown": "ALTER TABLE generated_reports ADD COLUMN content_markdown TEXT",
        "content_html": "ALTER TABLE generated_reports ADD COLUMN content_html TEXT",
        "export_markdown_path": "ALTER TABLE generated_reports ADD COLUMN export_markdown_path VARCHAR(500)",
        "export_docx_path": "ALTER TABLE generated_reports ADD COLUMN export_docx_path VARCHAR(500)",
        "export_pdf_path": "ALTER TABLE generated_reports ADD COLUMN export_pdf_path VARCHAR(500)",
    }

    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
