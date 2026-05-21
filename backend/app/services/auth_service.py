from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordQuestionRequest,
    ForgotPasswordQuestionResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
    UserResponse,
)

TEACHER_EMAIL = "teacher"
TEACHER_PASSWORD = "meitai123456"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _hash_recovery_answer(answer: str) -> str:
    normalized = answer.strip().lower()
    return bcrypt.hashpw(normalized.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_recovery_answer(answer: str, hashed: str) -> bool:
    normalized = answer.strip().lower()
    return bcrypt.checkpw(normalized.encode("utf-8"), hashed.encode("utf-8"))


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
        company_name=request.company_name,
        job_title=request.job_title,
        recovery_question=request.recovery_question.strip()
        if request.recovery_question and request.recovery_question.strip()
        else None,
        recovery_answer_hash=_hash_recovery_answer(request.recovery_answer)
        if request.recovery_answer and request.recovery_answer.strip()
        else None,
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


def get_recovery_question(
    db: Session,
    request: ForgotPasswordQuestionRequest,
) -> ForgotPasswordQuestionResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if (
        user is None
        or not user.recovery_question
        or not user.recovery_answer_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该账户未设置找回问题，请联系使用咨询协助处理。",
        )

    return ForgotPasswordQuestionResponse(
        email=user.email,
        recovery_question=user.recovery_question,
    )


def reset_password(
    db: Session,
    request: ResetPasswordRequest,
) -> ResetPasswordResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if (
        user is None
        or not user.recovery_answer_hash
        or not _verify_recovery_answer(request.recovery_answer, user.recovery_answer_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="找回答案不正确，请重新输入。",
        )

    user.hashed_password = _hash_password(request.new_password)
    db.add(user)
    db.commit()
    return ResetPasswordResponse()


def update_recovery(
    db: Session,
    user: User,
    question: str,
    answer: str,
) -> None:
    user.recovery_question = question.strip()
    user.recovery_answer_hash = _hash_recovery_answer(answer)
    db.add(user)
    db.commit()


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
