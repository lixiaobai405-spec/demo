from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


PaymentProvider = Literal["wechat", "alipay"]
PaymentOrderStatus = Literal["pending", "paid", "failed", "expired", "canceled"]


class PaymentOrderCreateRequest(BaseModel):
    provider: PaymentProvider


class PaymentOrderResponse(BaseModel):
    order_id: str
    order_no: str
    assessment_id: str
    provider: PaymentProvider
    amount_cents: int
    currency: str
    status: PaymentOrderStatus
    qr_code_url: str | None = None
    expires_at: datetime
    paid_at: datetime | None = None
    created_at: datetime


class EntitlementResponse(BaseModel):
    assessment_id: str
    is_unlocked: bool
    can_continue: bool
    locked_after_stage: Literal["canvas"]
    unlock_type: str | None = None
    unlocked_at: datetime | None = None
    latest_order: PaymentOrderResponse | None = None


class PaymentNotifyResponse(BaseModel):
    status: PaymentOrderStatus
    order_no: str
    assessment_id: str
    is_unlocked: bool


class ManualUnlockRequest(BaseModel):
    reason: str = Field(default="manual_admin_unlock", max_length=255)
