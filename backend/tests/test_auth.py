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
from app.db.base import Base
from app.main import create_app

TEST_DB_PATH = Path(__file__).resolve().parent / "test_auth.db"


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
