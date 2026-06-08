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
    """Create tables and apply lightweight SQLite compatibility migrations."""
    from app.models.assessment import Assessment  # noqa: F401
    from app.models.bmc_scoring import BMCScoring  # noqa: F401
    from app.models.breakthrough_selection import BreakthroughSelection  # noqa: F401
    from app.models.case_recommendation import CaseRecommendation  # noqa: F401
    from app.models.canvas_diagnosis import CanvasDiagnosis  # noqa: F401
    from app.models.chat import Conversation, Message  # noqa: F401
    from app.models.competitiveness_analysis import CompetitivenessAnalysis  # noqa: F401
    from app.models.direction_expansion import DirectionExpansion  # noqa: F401
    from app.models.direction_selection import DirectionSelection  # noqa: F401
    from app.models.endgame_analysis import EndgameAnalysis  # noqa: F401
    from app.models.follow_up import FollowUpTask  # noqa: F401
    from app.models.generated_report import GeneratedReport  # noqa: F401
    from app.models.intake_session import AssessmentIntakeSession  # noqa: F401
    from app.models.payment import AssessmentEntitlement, PaymentOrder  # noqa: F401
    from app.models.push_record import PushRecord  # noqa: F401
    from app.models.scenario_recommendation import ScenarioRecommendation  # noqa: F401
    from app.models.score_record import ScoreRecord  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_bmc_scorings_table()
    _migrate_generated_reports_table()
    _migrate_competitiveness_analyses_table()
    _migrate_endgame_analyses_table()
    _migrate_users_table()
    _migrate_assessments_add_user_id()
    _migrate_assessment_intake_sessions_add_user_id()
    _migrate_scenario_recommendations_table()
    _migrate_score_records_table()
    _migrate_payment_tables()


def _migrate_bmc_scorings_table() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "bmc_scorings" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("bmc_scorings")}
    needs_rebuild = (
        "selection_mode" in existing_columns
        or "all_module_scores_json" in existing_columns
        or "module_scores_json" not in existing_columns
    )
    if not needs_rebuild:
        return

    module_scores_source = (
        "module_scores_json"
        if "module_scores_json" in existing_columns
        else "all_module_scores_json"
    )

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys=OFF"))
        connection.execute(text("DROP TABLE IF EXISTS bmc_scorings_new"))
        connection.execute(
            text(
                """
                CREATE TABLE bmc_scorings_new (
                    id VARCHAR(36) PRIMARY KEY,
                    assessment_id VARCHAR(36) NOT NULL UNIQUE,
                    module_scores_json TEXT NOT NULL DEFAULT '[]',
                    scoring_result_json TEXT NOT NULL DEFAULT '{}',
                    selected_keys_json TEXT NOT NULL DEFAULT '[]',
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY(assessment_id) REFERENCES assessments(id)
                )
                """
            )
        )
        connection.execute(
            text(
                f"""
                INSERT OR REPLACE INTO bmc_scorings_new
                (id, assessment_id, module_scores_json, scoring_result_json, selected_keys_json, created_at, updated_at)
                SELECT
                    id,
                    assessment_id,
                    COALESCE({module_scores_source}, '[]'),
                    COALESCE(scoring_result_json, '{{}}'),
                    COALESCE(selected_keys_json, '[]'),
                    created_at,
                    updated_at
                FROM bmc_scorings
                """
            )
        )
        connection.execute(text("DROP TABLE bmc_scorings"))
        connection.execute(text("ALTER TABLE bmc_scorings_new RENAME TO bmc_scorings"))
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_bmc_scorings_assessment_id "
                "ON bmc_scorings (assessment_id)"
            )
        )
        connection.execute(text("PRAGMA foreign_keys=ON"))


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


def _migrate_competitiveness_analyses_table() -> None:
    """Add newly required competitiveness columns for existing SQLite databases."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "competitiveness_analyses" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("competitiveness_analyses")
    }
    if "overall_narrative" in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE competitiveness_analyses "
                "ADD COLUMN overall_narrative TEXT"
            )
        )


def _migrate_endgame_analyses_table() -> None:
    """Add newly required endgame columns for existing SQLite databases."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "endgame_analyses" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("endgame_analyses")}

    with engine.begin() as connection:
        if "three_stage_strategy_json" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE endgame_analyses "
                    "ADD COLUMN three_stage_strategy_json TEXT NOT NULL DEFAULT '{}'"
                )
            )
        if "industry_essence" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE endgame_analyses "
                    "ADD COLUMN industry_essence TEXT"
                )
            )


def _migrate_users_table() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("users")}
    required_columns = {
        "company_name": "ALTER TABLE users ADD COLUMN company_name VARCHAR(255)",
        "job_title": "ALTER TABLE users ADD COLUMN job_title VARCHAR(100)",
        "recovery_question": "ALTER TABLE users ADD COLUMN recovery_question VARCHAR(255)",
        "recovery_answer_hash": "ALTER TABLE users ADD COLUMN recovery_answer_hash VARCHAR(255)",
        "reset_token": "ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)",
        "reset_token_expires_at": "ALTER TABLE users ADD COLUMN reset_token_expires_at TIMESTAMP",
    }

    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def _migrate_assessments_add_user_id() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "assessments" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("assessments")}
    if "user_id" not in existing_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE assessments ADD COLUMN user_id VARCHAR(36) REFERENCES users(id)")
            )


def _migrate_assessment_intake_sessions_add_user_id() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "assessment_intake_sessions" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("assessment_intake_sessions")}
    if "user_id" not in existing_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE assessment_intake_sessions "
                    "ADD COLUMN user_id VARCHAR(36) REFERENCES users(id)"
                )
            )


def _migrate_scenario_recommendations_table() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "scenario_recommendations" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("scenario_recommendations")}
    required_columns = {
        "all_scores_json": (
            "ALTER TABLE scenario_recommendations "
            "ADD COLUMN all_scores_json TEXT"
        ),
        "active_scenario_ids_json": (
            "ALTER TABLE scenario_recommendations "
            "ADD COLUMN active_scenario_ids_json TEXT"
        ),
    }

    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def _migrate_score_records_table() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "score_records" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("score_records")}
    required_columns = {
        "note": "ALTER TABLE score_records ADD COLUMN note TEXT",
        "export_markdown_path": (
            "ALTER TABLE score_records ADD COLUMN export_markdown_path VARCHAR(500)"
        ),
        "export_pdf_path": (
            "ALTER TABLE score_records ADD COLUMN export_pdf_path VARCHAR(500)"
        ),
    }

    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def _migrate_payment_tables() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "payment_orders" in table_names:
        order_columns = {c["name"] for c in inspector.get_columns("payment_orders")}
        required_columns = {
            "provider_payload": "ALTER TABLE payment_orders ADD COLUMN provider_payload TEXT",
            "provider_transaction_id": (
                "ALTER TABLE payment_orders ADD COLUMN provider_transaction_id VARCHAR(128)"
            ),
        }
        with engine.begin() as connection:
            for column_name, ddl in required_columns.items():
                if column_name not in order_columns:
                    connection.execute(text(ddl))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
