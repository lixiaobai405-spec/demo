from __future__ import annotations

from io import BytesIO
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
from app.db.session import Base
from app.main import create_app

TEST_DB_PATH = Path(__file__).resolve().parent / "test_auth.db"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create an isolated auth test client backed by a disposable SQLite DB."""
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
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(db_session, "SessionLocal", testing_session_local)

    def _override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[db_session.get_db] = _override_get_db
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_teacher_login_returns_instructor_role(client: TestClient):
    """讲师硬编码账户登录应返回 role=instructor + 有效 token"""
    resp = client.post("/api/auth/login", json={
        "email": "teacher",
        "password": "meitai123456",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "teacher"
    assert data["user"]["role"] == "instructor"
    assert data["user"]["display_name"] == "讲师"


def test_teacher_login_wrong_password_fails(client: TestClient):
    """讲师错误密码应返回 401"""
    resp = client.post("/api/auth/login", json={
        "email": "teacher",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401, resp.text


def test_student_register_and_login(client: TestClient):
    """学员正常注册和登录流程不受影响"""
    # 注册
    resp = client.post("/api/auth/register", json={
        "email": "student@test.com",
        "password": "test123456",
        "display_name": "测试学员",
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["user"]["role"] == "student"
    assert data["user"]["email"] == "student@test.com"

    # 登录
    resp = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "test123456",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["user"]["role"] == "student"


def test_teacher_can_see_all_assessments(client: TestClient):
    """讲师登录后调用 /api/assessments 不过滤 user_id"""
    # 先创建两个不同用户的评估
    # 注册学生 A
    resp = client.post("/api/auth/register", json={
        "email": "a@test.com",
        "password": "test123456",
        "display_name": "学生A",
    })
    token_a = resp.json()["access_token"]

    # 注册学生 B
    resp = client.post("/api/auth/register", json={
        "email": "b@test.com",
        "password": "test123456",
        "display_name": "学生B",
    })
    token_b = resp.json()["access_token"]

    # 学生 A 创建评估
    client.post("/api/assessments", json={
        "company_name": "A公司",
        "industry": "教育",
        "company_size": "小型",
    }, headers={"Authorization": f"Bearer {token_a}"})

    # 学生 B 创建评估
    client.post("/api/assessments", json={
        "company_name": "B公司",
        "industry": "医疗",
        "company_size": "中型",
    }, headers={"Authorization": f"Bearer {token_b}"})

    # 讲师登录
    resp = client.post("/api/auth/login", json={
        "email": "teacher",
        "password": "meitai123456",
    })
    teacher_token = resp.json()["access_token"]

    # 讲师查看所有评估
    resp = client.get("/api/assessments", headers={
        "Authorization": f"Bearer {teacher_token}",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] >= 2, f"讲师应能看到所有评估，实际 total={data['total']}"


def test_student_can_only_see_own_assessments(client: TestClient):
    """学生只能看到自己的评估"""
    # 注册并登录学生
    resp = client.post("/api/auth/register", json={
        "email": "onlyme@test.com",
        "password": "test123456",
    })
    token = resp.json()["access_token"]

    client.post("/api/assessments", json={
        "company_name": "我的公司",
        "industry": "金融",
        "company_size": "小型",
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/assessments", headers={
        "Authorization": f"Bearer {token}",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 1


# ── A. 登录与账户系统 逐项测试 ──

class TestLoginCorrectCredentials:
    """正确账号密码登录"""

    def test_student_login_with_correct_credentials(self, client):
        client.post("/api/auth/register", json={
            "email": "correct@test.com", "password": "test123456",
        })
        resp = client.post("/api/auth/login", json={
            "email": "correct@test.com", "password": "test123456",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "correct@test.com"

    def test_login_returns_valid_token_usable_for_me(self, client):
        client.post("/api/auth/register", json={
            "email": "valid@test.com", "password": "test123456",
        })
        resp = client.post("/api/auth/login", json={
            "email": "valid@test.com", "password": "test123456",
        })
        token = resp.json()["access_token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["email"] == "valid@test.com"


class TestLoginWrongPassword:
    """错误密码登录"""

    def test_wrong_password_returns_401(self, client):
        client.post("/api/auth/register", json={
            "email": "wp@test.com", "password": "test123456",
        })
        resp = client.post("/api/auth/login", json={
            "email": "wp@test.com", "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_wrong_password_message_does_not_leak_info(self, client):
        """错误提示不泄露是否存在该用户"""
        client.post("/api/auth/register", json={
            "email": "leak@test.com", "password": "test123456",
        })
        # wrong password for existing user
        resp = client.post("/api/auth/login", json={
            "email": "leak@test.com", "password": "wrong",
        })
        msg_existing = resp.json()["detail"]

        # non-existent user
        resp2 = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com", "password": "test123456",
        })
        msg_nonexistent = resp2.json()["detail"]

        # Same error message — no user enumeration
        assert msg_existing == msg_nonexistent
        assert "邮箱或密码错误" in msg_existing


class TestLoginEmptyCredentials:
    """空账号/空密码"""

    def test_empty_email_rejected(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "", "password": "test123456",
        })
        # Backend LoginRequest uses str (not EmailStr), so empty string
        # passes through and fails authentication → 401.
        # This is correct security posture: no user-enumeration via validation.
        assert resp.status_code == 401

    def test_empty_password_rejected(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "test@test.com", "password": "",
        })
        assert resp.status_code == 401

    def test_both_empty_rejected(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "", "password": "",
        })
        assert resp.status_code == 401


class TestLoginEmailFormat:
    """邮箱格式错误 — 统一返回 401，不区分格式错误与凭据错误"""

    def test_no_at_sign_uniform_error(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "notanemail", "password": "test123456",
        })
        # LoginRequest.email is plain str, no EmailStr validation.
        # Returns 401 with generic message — prevents user enumeration.
        assert resp.status_code == 401
        assert "邮箱或密码错误" in resp.json()["detail"]

    def test_no_domain_uniform_error(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "user@", "password": "test123456",
        })
        assert resp.status_code == 401


class TestProtectedRoutes:
    """未登录访问受保护页面"""

    def test_me_without_token_returns_401(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
        assert "请先登录" in resp.json()["detail"]

    def test_me_with_malformed_header_returns_401(self, client):
        resp = client.get("/api/auth/me", headers={
            "Authorization": "not-bearer-format",
        })
        assert resp.status_code == 401
        assert "认证格式错误" in resp.json()["detail"]

    def test_me_with_empty_token_returns_401(self, client):
        resp = client.get("/api/auth/me", headers={
            "Authorization": "Bearer ",
        })
        assert resp.status_code == 401
        assert "认证格式错误" in resp.json()["detail"]

    def test_me_with_tampered_token_returns_401(self, client):
        resp = client.get("/api/auth/me", headers={
            "Authorization": "Bearer tampered.jwt.token",
        })
        assert resp.status_code == 401
        assert "认证信息无效" in resp.json()["detail"]

    def test_assessments_without_token_returns_401(self, client):
        resp = client.get("/api/assessments")
        assert resp.status_code == 401


class TestTokenExpiry:
    """会话过期处理"""

    def test_expired_token_returns_401(self, client, monkeypatch):
        """模拟过期 token 返回明确提示"""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from app.core.config import settings
        from app.models.user import User
        from app.db.session import SessionLocal

        # 创建一个真实用户
        db = next(client.app.dependency_overrides.get(
            db_session.get_db,
            lambda: SessionLocal(),
        )())
        try:
            user = User(
                email="expired@test.com",
                hashed_password="...",
                role="student",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id
        finally:
            db.close()

        # 用已在过去的 exp 生成 token
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {"sub": user_id, "exp": past}
        expired_token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm,
        )

        resp = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {expired_token}",
        })
        assert resp.status_code == 401
        assert "已过期" in resp.json()["detail"]


class TestRegistrationEdgeCases:
    """注册边界情况"""

    def test_short_password_rejected(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "short@test.com", "password": "12345",
        })
        assert resp.status_code == 422

    def test_duplicate_email_rejected_409(self, client):
        client.post("/api/auth/register", json={
            "email": "dup@test.com", "password": "test123456",
        })
        resp = client.post("/api/auth/register", json={
            "email": "dup@test.com", "password": "test123456",
        })
        assert resp.status_code == 409
        assert "已被注册" in resp.json()["detail"]

    def test_registration_returns_token(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "newuser@test.com", "password": "test123456",
            "display_name": "新用户",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["display_name"] == "新用户"


class TestErrorMessageClarity:
    """错误提示清晰度"""

    def test_login_error_is_chinese_and_actionable(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@test.com", "password": "test123456",
        })
        assert resp.status_code == 401
        detail = resp.json()["detail"]
        # Must be in Chinese and actionable
        assert "邮箱" in detail or "密码" in detail

    def test_unauthorized_error_is_chinese(self, client):
        resp = client.get("/api/auth/me")
        detail = resp.json()["detail"]
        assert any(ch in detail for ch in "登录认证")


def test_register_with_profile_fields_and_recovery_settings(client: TestClient):
    resp = client.post("/api/auth/register", json={
        "email": "recovery@test.com",
        "password": "test123456",
        "display_name": "测试用户",
        "company_name": "美太测试企业",
        "job_title": "创新负责人",
        "recovery_question": "你的第一位直属领导姓名是？",
        "recovery_answer": "张老师",
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["user"]["display_name"] == "测试用户"
    assert data["user"]["company_name"] == "美太测试企业"
    assert data["user"]["job_title"] == "创新负责人"


def test_forgot_password_question_and_reset_flow(client: TestClient):
    client.post("/api/auth/register", json={
        "email": "resetme@test.com",
        "password": "oldpass123",
        "display_name": "可重置用户",
        "recovery_question": "你的第一次独立项目名称是？",
        "recovery_answer": "星火计划",
    })

    question_resp = client.post("/api/auth/forgot-password/question", json={
        "email": "resetme@test.com",
    })
    assert question_resp.status_code == 200, question_resp.text
    assert question_resp.json()["recovery_question"] == "你的第一次独立项目名称是？"

    reset_resp = client.post("/api/auth/forgot-password/reset", json={
        "email": "resetme@test.com",
        "recovery_answer": "星火计划",
        "new_password": "newpass123",
    })
    assert reset_resp.status_code == 200, reset_resp.text
    assert reset_resp.json()["success"] is True

    old_login = client.post("/api/auth/login", json={
        "email": "resetme@test.com",
        "password": "oldpass123",
    })
    assert old_login.status_code == 401

    new_login = client.post("/api/auth/login", json={
        "email": "resetme@test.com",
        "password": "newpass123",
    })
    assert new_login.status_code == 200, new_login.text


def test_forgot_password_requires_existing_recovery_settings(client: TestClient):
    client.post("/api/auth/register", json={
        "email": "norecovery@test.com",
        "password": "test123456",
    })

    question_resp = client.post("/api/auth/forgot-password/question", json={
        "email": "norecovery@test.com",
    })
    assert question_resp.status_code == 404, question_resp.text


def test_forgot_password_sends_reset_email_via_smtp(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    from types import SimpleNamespace

    from app.models.user import User
    from app.services import auth_service

    client.post("/api/auth/register", json={
        "email": "smtp-reset@test.com",
        "password": "test123456",
    })

    sent: dict[str, object] = {}

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int):
            sent["host"] = host
            sent["port"] = port
            sent["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            sent["starttls"] = True

        def login(self, username: str, password: str):
            sent["login"] = (username, password)

        def send_message(self, message):
            sent["message"] = message

    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(
            smtp_enabled=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="smtp-user",
            smtp_password="smtp-pass",
            smtp_from_email="noreply@example.com",
            smtp_from_name="Meitai AI",
            smtp_use_tls=True,
            smtp_use_ssl=False,
            password_reset_url="",
            frontend_origin="http://localhost:3001",
            jwt_expire_minutes=1440,
            jwt_secret_key="test-secret",
            jwt_algorithm="HS256",
        ),
    )
    monkeypatch.setattr(auth_service.smtplib, "SMTP", FakeSMTP)

    response = client.post("/api/auth/forgot-password", json={
        "email": "smtp-reset@test.com",
    })

    assert response.status_code == 200, response.text
    assert sent["host"] == "smtp.example.com"
    assert sent["port"] == 587
    assert sent["starttls"] is True
    assert sent["login"] == ("smtp-user", "smtp-pass")
    message = sent["message"]
    assert message["To"] == "smtp-reset@test.com"
    html_body = message.get_body(preferencelist=("html",))
    assert html_body is not None
    assert "reset-password?token=" in html_body.get_content()

    with db_session.SessionLocal() as db:
        user = db.query(User).filter(User.email == "smtp-reset@test.com").first()
        assert user is not None
        assert user.reset_token is not None
        assert user.reset_token_expires_at is not None


def test_forgot_password_smtp_failure_rolls_back_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    import smtplib
    from types import SimpleNamespace

    from app.models.user import User
    from app.services import auth_service

    client.post("/api/auth/register", json={
        "email": "smtp-fail@test.com",
        "password": "test123456",
    })

    class FailingSMTP:
        def __init__(self, host: str, port: int, timeout: int):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            pass

        def login(self, username: str, password: str):
            pass

        def send_message(self, message):
            raise smtplib.SMTPException("send failed")

    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(
            smtp_enabled=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="smtp-user",
            smtp_password="smtp-pass",
            smtp_from_email="noreply@example.com",
            smtp_from_name="Meitai AI",
            smtp_use_tls=True,
            smtp_use_ssl=False,
            password_reset_url="",
            frontend_origin="http://localhost:3001",
            jwt_expire_minutes=1440,
            jwt_secret_key="test-secret",
            jwt_algorithm="HS256",
        ),
    )
    monkeypatch.setattr(auth_service.smtplib, "SMTP", FailingSMTP)

    response = client.post("/api/auth/forgot-password", json={
        "email": "smtp-fail@test.com",
    })

    assert response.status_code == 503, response.text

    with db_session.SessionLocal() as db:
        user = db.query(User).filter(User.email == "smtp-fail@test.com").first()
        assert user is not None
        assert user.reset_token is None
        assert user.reset_token_expires_at is None
