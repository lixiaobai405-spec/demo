from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api.routes import chat as chat_route
from app.db import session as db_session
from app.main import create_app
from app.models.assessment import Assessment

TEST_DB_PATH = Path(__file__).resolve().parent / "test_chat_upload.db"


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
    db_session.init_db()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def create_assessment() -> str:
    session = db_session.SessionLocal()
    try:
        assessment = Assessment(
            company_name="测试企业",
            industry="零售",
            company_size="50-99人",
            region="上海",
            annual_revenue_range="1000万-5000万",
            core_products="门店零售",
            target_customers="企业客户",
            current_challenges="资料分散",
            ai_goals="提效",
            available_data="ERP、CRM",
            notes=None,
        )
        session.add(assessment)
        session.commit()
        session.refresh(assessment)
        return assessment.id
    finally:
        session.close()


def test_chat_accepts_uploaded_files(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    assessment_id = create_assessment()
    captured: Dict[str, object] = {}

    async def fake_stream_chat(
        incoming_assessment_id: str,
        user_message: str,
        attachments: Optional[List[Dict[str, object]]] = None,
    ):
        captured["assessment_id"] = incoming_assessment_id
        captured["message"] = user_message
        captured["attachments"] = attachments
        yield 'data: {"done": true}\n\n'

    monkeypatch.setattr(chat_route, "stream_chat", fake_stream_chat)

    response = client.post(
        f"/api/assessments/{assessment_id}/chat",
        data={"message": "请总结这份资料"},
        files=[("files", ("memo.txt", "第一行\n第二行".encode("utf-8"), "text/plain"))],
    )

    assert response.status_code == 200
    assert captured["assessment_id"] == assessment_id
    assert captured["message"] == "请总结这份资料"

    attachments = captured["attachments"]
    assert isinstance(attachments, list)
    assert len(attachments) == 1
    assert attachments[0]["name"] == "memo.txt"
    assert attachments[0]["kind"] == "txt"
    assert "第一行" in str(attachments[0]["content"])
