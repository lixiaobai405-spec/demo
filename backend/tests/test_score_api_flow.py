from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db import session as db_session
from app.main import create_app
from app.core.config import settings
from app.schemas.intake import IntakeSourceFile
from app.services.intake_service import IntakeService

TEST_DB_PATH = Path(__file__).resolve().parent / "test_score_flow.db"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    engine = create_engine(
        f"sqlite:///{TEST_DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", testing_session_local)

    async def fake_extract_upload_file(self, upload_file):
        return (
            IntakeSourceFile(
                name=upload_file.filename or "report.pdf",
                kind="pdf",
                size_bytes=2048,
            ),
            "这是 PDF 文档的解析文本，包含问题、行动、结果和改进计划。",
            [],
        )

    monkeypatch.setattr(IntakeService, "extract_upload_file", fake_extract_upload_file)
    previous_llm_mode = settings.llm_mode
    object.__setattr__(settings, "llm_mode", "mock")

    app = create_app()
    db_session.Base.metadata.create_all(bind=engine)
    db_session._migrate_generated_reports_table()
    db_session._migrate_users_table()
    db_session._migrate_score_records_table()

    with TestClient(app) as test_client:
        register_response = test_client.post(
            "/api/auth/register",
            json={
                "email": "score-user@example.com",
                "password": "password123",
                "display_name": "Score User",
                "company_name": "Test Company",
                "job_title": "Coach",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client
        object.__setattr__(settings, "llm_mode", previous_llm_mode)

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_score_api_create_detail_and_export_flow(client: TestClient) -> None:
    create_response = client.post(
        "/api/score",
        data={
            "name": "张三",
            "org": "测试事业部",
            "report_type": "温故知新",
            "date": "2026-05-23",
            "note": "体验期样例",
            "transcript": "这里是录音转写文本，包含表达和逻辑信息。",
        },
        files={
            "pdf_file": (
                "report.pdf",
                b"%PDF-1.4 fake pdf bytes",
                "application/pdf",
            )
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["score_id"]
    assert created["total_score"] > 0
    assert len(created["dimensions"]) == 10

    score_id = created["score_id"]
    detail_response = client.get(f"/api/score/{score_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["input"]["name"] == "张三"
    assert detail["result"]["report_type"] == "温故知新"
    assert detail["result"]["disclaimer"]

    markdown_response = client.get(
        f"/api/score/{score_id}/export",
        params={"format": "md"},
    )
    assert markdown_response.status_code == 200
    assert markdown_response.headers["content-type"].startswith("text/markdown")
    assert "汇报评分报告" in markdown_response.text

    pdf_response = client.get(
        f"/api/score/{score_id}/export",
        params={"format": "pdf"},
    )
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content[:5] == b"%PDF-"


def test_score_api_rejects_non_pdf_file(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_non_pdf_extract(self, upload_file):
        return (
            IntakeSourceFile(
                name=upload_file.filename or "report.docx",
                kind="docx",
                size_bytes=1024,
            ),
            "docx text",
            [],
        )

    monkeypatch.setattr(IntakeService, "extract_upload_file", fake_non_pdf_extract)

    response = client.post(
        "/api/score",
        data={
            "name": "李四",
            "org": "测试组织",
            "report_type": "行动学习",
            "date": "2026-05-23",
            "transcript": "",
        },
        files={
            "pdf_file": (
                "report.docx",
                b"fake docx bytes",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "pdf_file must be a PDF document."
