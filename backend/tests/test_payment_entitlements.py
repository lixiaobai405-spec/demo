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
from app.services.llm_client import LLMClient
from app.services.llm_enhancer import LLMEnhancer


TEST_DB_PATH = Path(__file__).resolve().parent / "test_payment_entitlements.db"


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
    monkeypatch.setattr(LLMClient, "_use_mock_mode", lambda self: True)
    monkeypatch.setattr(LLMEnhancer, "_is_live_mode", lambda self: False)

    app = create_app()
    with TestClient(app) as test_client:
        register_response = test_client.post(
            "/api/auth/register",
            json={
                "email": "payments@test.com",
                "password": "test123456",
                "display_name": "Payment Tester",
                "company_name": "Payment Co",
                "job_title": "Founder",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture()
def assessment_payload() -> dict[str, str | None]:
    return {
        "company_name": "Paid Flow Retail",
        "industry": "Retail",
        "company_size": "100-499",
        "region": "Shanghai",
        "annual_revenue_range": "50M-100M",
        "core_products": "Stores and member operations",
        "target_customers": "Community members",
        "current_challenges": "Retention and inventory volatility",
        "ai_goals": "Improve retention and inventory planning",
        "available_data": "POS, members, inventory",
        "notes": None,
    }


def _create_assessment(client: TestClient, payload: dict[str, str | None]) -> str:
    response = client.post("/api/assessments", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def _prepare_free_canvas(client: TestClient, assessment_id: str) -> None:
    assert client.post(f"/api/assessments/{assessment_id}/profile").status_code == 200
    assert client.post(f"/api/assessments/{assessment_id}/canvas").status_code == 200


def test_canvas_is_free_and_breakthrough_requires_paid_unlock(
    client: TestClient,
    assessment_payload: dict[str, str | None],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)
    _prepare_free_canvas(client, assessment_id)

    entitlement_response = client.get(f"/api/assessments/{assessment_id}/entitlement")
    assert entitlement_response.status_code == 200
    entitlement = entitlement_response.json()
    assert entitlement["is_unlocked"] is False
    assert entitlement["can_continue"] is False
    assert entitlement["locked_after_stage"] == "canvas"

    breakthrough_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    assert breakthrough_response.status_code == 402
    assert breakthrough_response.json()["detail"]["code"] == "PAYMENT_REQUIRED"


def test_mock_wechat_payment_unlocks_only_the_current_assessment(
    client: TestClient,
    assessment_payload: dict[str, str | None],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)
    other_assessment_id = _create_assessment(client, assessment_payload)
    _prepare_free_canvas(client, assessment_id)
    _prepare_free_canvas(client, other_assessment_id)

    order_response = client.post(
        f"/api/assessments/{assessment_id}/payments/orders",
        json={"provider": "wechat"},
    )
    assert order_response.status_code == 201
    order = order_response.json()
    assert order["provider"] == "wechat"
    assert order["status"] == "pending"
    assert order["qr_code_url"].startswith("mockpay://")

    notify_response = client.post(
        "/api/payments/wechat/notify",
        json={
            "out_trade_no": order["order_no"],
            "total_amount_cents": order["amount_cents"],
            "transaction_id": "wx-test-transaction",
            "trade_state": "SUCCESS",
        },
    )
    assert notify_response.status_code == 200
    assert notify_response.json()["status"] == "paid"

    duplicate_notify = client.post(
        "/api/payments/wechat/notify",
        json={
            "out_trade_no": order["order_no"],
            "total_amount_cents": order["amount_cents"],
            "transaction_id": "wx-test-transaction",
            "trade_state": "SUCCESS",
        },
    )
    assert duplicate_notify.status_code == 200
    assert duplicate_notify.json()["status"] == "paid"

    entitlement_response = client.get(f"/api/assessments/{assessment_id}/entitlement")
    assert entitlement_response.status_code == 200
    assert entitlement_response.json()["is_unlocked"] is True
    assert entitlement_response.json()["can_continue"] is True

    breakthrough_response = client.post(
        f"/api/assessments/{assessment_id}/breakthrough/recommend"
    )
    assert breakthrough_response.status_code == 200

    other_breakthrough_response = client.post(
        f"/api/assessments/{other_assessment_id}/breakthrough/recommend"
    )
    assert other_breakthrough_response.status_code == 402


def test_payment_notify_rejects_amount_mismatch(
    client: TestClient,
    assessment_payload: dict[str, str | None],
) -> None:
    assessment_id = _create_assessment(client, assessment_payload)
    _prepare_free_canvas(client, assessment_id)

    order = client.post(
        f"/api/assessments/{assessment_id}/payments/orders",
        json={"provider": "alipay"},
    ).json()

    notify_response = client.post(
        "/api/payments/alipay/notify",
        json={
            "out_trade_no": order["order_no"],
            "total_amount_cents": order["amount_cents"] + 1,
            "trade_no": "ali-test-transaction",
            "trade_status": "TRADE_SUCCESS",
        },
    )
    assert notify_response.status_code == 400

    entitlement_response = client.get(f"/api/assessments/{assessment_id}/entitlement")
    assert entitlement_response.json()["is_unlocked"] is False
