from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordQuestionRequest,
    ForgotPasswordQuestionResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordByTokenRequest,
    ResetPasswordByTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SetupRecoveryRequest,
    SetupRecoveryResponse,
    TokenResponse,
    UpdateRecoveryRequest,
    UpdateRecoveryResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.authenticate(db, payload)


@router.post(
    "/forgot-password/question",
    response_model=ForgotPasswordQuestionResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password_question(
    payload: ForgotPasswordQuestionRequest,
    db: Session = Depends(get_db),
):
    return auth_service.get_recovery_question(db, payload)


@router.post(
    "/forgot-password/reset",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password_reset(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    return auth_service.reset_password(db, payload)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user, from_attributes=True)


@router.put(
    "/me/recovery",
    response_model=UpdateRecoveryResponse,
    status_code=status.HTTP_200_OK,
)
def update_my_recovery(
    payload: UpdateRecoveryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """已登录用户补充或更新找回密码设置。"""
    auth_service.update_recovery(db, current_user, payload.recovery_question, payload.recovery_answer)
    return UpdateRecoveryResponse()


@router.post(
    "/setup-recovery",
    response_model=SetupRecoveryResponse,
    status_code=status.HTTP_200_OK,
)
def setup_recovery(
    payload: SetupRecoveryRequest,
    db: Session = Depends(get_db),
):
    """用邮箱+当前密码验证身份，为历史老账号补录找回问题。无需已登录。"""
    auth_service.setup_recovery(
        db,
        email=payload.email,
        password=payload.password,
        question=payload.recovery_question,
        answer=payload.recovery_answer,
    )
    return SetupRecoveryResponse()


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """发送密码重置邮件（当前版本生成 token 并返回，生产环境改为发送邮件）。"""
    auth_service.request_password_reset(db, payload.email)
    return ForgotPasswordResponse()


@router.post(
    "/reset-password",
    response_model=ResetPasswordByTokenResponse,
    status_code=status.HTTP_200_OK,
)
def reset_password_by_token(
    payload: ResetPasswordByTokenRequest,
    db: Session = Depends(get_db),
):
    """通过邮件中的重置 token 设置新密码。"""
    auth_service.reset_password_by_token(db, payload.token, payload.new_password)
    return ResetPasswordByTokenResponse()
