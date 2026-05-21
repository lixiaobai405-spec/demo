from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)
    company_name: str | None = Field(default=None, max_length=255)
    job_title: str | None = Field(default=None, max_length=100)
    recovery_question: str | None = Field(default=None, max_length=255)
    recovery_answer: str | None = Field(default=None, max_length=255)


class CreateInstructorRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str | None
    company_name: str | None
    job_title: str | None
    role: str
    has_recovery: bool = False
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordQuestionRequest(BaseModel):
    email: str = Field(max_length=255)


class ForgotPasswordQuestionResponse(BaseModel):
    email: str
    recovery_question: str


class ResetPasswordRequest(BaseModel):
    email: str = Field(max_length=255)
    recovery_answer: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=6, max_length=128)


class ResetPasswordResponse(BaseModel):
    success: bool = True


class UpdateRecoveryRequest(BaseModel):
    recovery_question: str = Field(min_length=1, max_length=255)
    recovery_answer: str = Field(min_length=1, max_length=255)


class UpdateRecoveryResponse(BaseModel):
    success: bool = True
