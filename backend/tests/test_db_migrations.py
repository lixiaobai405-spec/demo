import sys
from pathlib import Path
import json

from sqlalchemy import create_engine, inspect, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db import session as db_session


def test_migrate_bmc_scorings_table_from_legacy_schema(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "legacy_bmc.db"
    engine = create_engine(
        f"sqlite:///{db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )

    monkeypatch.setattr(db_session, "engine", engine)

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE assessments (
                    id VARCHAR(36) PRIMARY KEY
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE bmc_scorings (
                    id VARCHAR(36) PRIMARY KEY,
                    assessment_id VARCHAR(36) NOT NULL UNIQUE,
                    selection_mode VARCHAR(20) NOT NULL,
                    selected_keys_json TEXT NOT NULL DEFAULT '[]',
                    all_module_scores_json TEXT NOT NULL DEFAULT '[]',
                    scoring_result_json TEXT NOT NULL DEFAULT '{}',
                    created_at DATETIME,
                    updated_at DATETIME
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO assessments (id) VALUES ('assessment-1')
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO bmc_scorings
                (id, assessment_id, selection_mode, selected_keys_json, all_module_scores_json, scoring_result_json, created_at, updated_at)
                VALUES
                (:id, :assessment_id, :selection_mode, :selected_keys_json, :all_module_scores_json, :scoring_result_json, :created_at, :updated_at)
                """
            ),
            {
                "id": "bmc-1",
                "assessment_id": "assessment-1",
                "selection_mode": "bmc_scoring",
                "selected_keys_json": json.dumps(["customer_relationships"]),
                "all_module_scores_json": json.dumps(
                    [
                        {
                            "key": "customer_relationships",
                            "pain": 5,
                            "data": 4,
                            "feasibility": 4,
                        }
                    ]
                ),
                "scoring_result_json": json.dumps(
                    {
                        "assessment_id": "assessment-1",
                        "module_results": [],
                        "top_3_keys": ["customer_relationships"],
                        "top_3_results": [],
                        "complementarity_warning": None,
                    }
                ),
                "created_at": "2026-05-14 00:00:00",
                "updated_at": "2026-05-14 00:00:00",
            },
        )

    db_session._migrate_bmc_scorings_table()

    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("bmc_scorings")}

    assert "module_scores_json" in columns
    assert "selection_mode" not in columns
    assert "all_module_scores_json" not in columns

    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                SELECT assessment_id, module_scores_json, scoring_result_json, selected_keys_json
                FROM bmc_scorings
                WHERE id = 'bmc-1'
                """
            )
        ).mappings().one()

    assert row["assessment_id"] == "assessment-1"
    assert "customer_relationships" in row["module_scores_json"]
    assert "customer_relationships" in row["selected_keys_json"]
