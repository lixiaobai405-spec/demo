from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

TEACHER_EMAIL = "teacher"
TEACHER_PASSWORD = "meitai123456"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def register(db: Session, request: RegisterRequest) -> TokenResponse:
    existing = db.query(User).filter(User.email == request.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册。",
        )

    user = User(
        email=request.email,
        hashed_password=_hash_password(request.password),
        display_name=request.display_name,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user, from_attributes=True),
    )


def authenticate(db: Session, request: LoginRequest) -> TokenResponse:
    # 硬编码讲师账户
    if request.email == TEACHER_EMAIL and request.password == TEACHER_PASSWORD:
        teacher = db.query(User).filter(User.email == TEACHER_EMAIL).first()
        if teacher is None:
            teacher = User(
                email=TEACHER_EMAIL,
                hashed_password=_hash_password(TEACHER_PASSWORD),
                display_name="讲师",
                role="instructor",
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
        token = _create_access_token(teacher.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(teacher, from_attributes=True),
        )

    user = db.query(User).filter(User.email == request.email).first()
    if user is None or not _verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误。",
        )

    token = _create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user, from_attributes=True),
    )


def get_user_from_token(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise _unauthorized()
    except JWTError:
        raise _unauthorized()

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _unauthorized()
    return user


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证信息无效或已过期，请重新登录。",
    )
