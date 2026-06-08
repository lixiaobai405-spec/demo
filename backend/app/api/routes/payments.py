from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_instructor
from app.api.routes.assessments import _check_owner_or_instructor, _get_assessment_or_404
from app.db.session import get_db
from app.models.user import User
from app.schemas.payment import (
    EntitlementResponse,
    ManualUnlockRequest,
    PaymentNotifyResponse,
    PaymentOrderCreateRequest,
    PaymentOrderResponse,
)
from app.services.payment_service import EntitlementService, PaymentService

router = APIRouter(tags=["payments"])


@router.get(
    "/api/assessments/{assessment_id}/entitlement",
    response_model=EntitlementResponse,
    status_code=status.HTTP_200_OK,
)
def get_assessment_entitlement(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EntitlementResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    _check_owner_or_instructor(assessment, current_user)
    return EntitlementService().get_status(db, assessment, current_user)


@router.post(
    "/api/assessments/{assessment_id}/entitlement/unlock",
    response_model=EntitlementResponse,
    status_code=status.HTTP_200_OK,
)
def unlock_assessment_manually(
    assessment_id: str,
    _: ManualUnlockRequest,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_instructor),
) -> EntitlementResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    owner_id = assessment.user_id or instructor.id
    service = EntitlementService()
    service.grant(
        db,
        assessment_id=assessment.id,
        user_id=owner_id,
        unlock_type="manual_admin_unlock",
    )
    return service.get_status(db, assessment, instructor)


@router.post(
    "/api/assessments/{assessment_id}/payments/orders",
    response_model=PaymentOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_order(
    assessment_id: str,
    payload: PaymentOrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentOrderResponse:
    assessment = _get_assessment_or_404(db, assessment_id)
    _check_owner_or_instructor(assessment, current_user)
    return PaymentService().create_order(db, assessment, current_user, payload.provider)


@router.get(
    "/api/payments/orders/{order_id}",
    response_model=PaymentOrderResponse,
    status_code=status.HTTP_200_OK,
)
def get_payment_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentOrderResponse:
    return PaymentService().get_order(db, order_id, current_user)


@router.post(
    "/api/payments/wechat/notify",
    response_model=PaymentNotifyResponse,
    status_code=status.HTTP_200_OK,
)
async def handle_wechat_notify(
    request: Request,
    db: Session = Depends(get_db),
) -> PaymentNotifyResponse:
    raw_body = await request.body()
    payload = await _payload_from_request(request, raw_body)
    headers = {key: value for key, value in request.headers.items()}
    return PaymentService().process_wechat_notify(db, payload, raw_body, headers)


@router.post(
    "/api/payments/alipay/notify",
    response_model=PaymentNotifyResponse,
    status_code=status.HTTP_200_OK,
)
async def handle_alipay_notify(
    request: Request,
    db: Session = Depends(get_db),
) -> PaymentNotifyResponse:
    raw_body = await request.body()
    payload = await _payload_from_request(request, raw_body)
    return PaymentService().process_alipay_notify(db, payload)


async def _payload_from_request(request: Request, raw_body: bytes) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return await request.json()
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        return dict(form)
    if not raw_body:
        return {}
    return await request.json()
