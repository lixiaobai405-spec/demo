from __future__ import annotations

import base64
import json
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from urllib.parse import urlencode

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assessment import Assessment
from app.models.generated_report import GeneratedReport
from app.models.payment import AssessmentEntitlement, PaymentOrder
from app.models.user import User
from app.schemas.payment import EntitlementResponse, PaymentNotifyResponse, PaymentOrderResponse

PAID_UNLOCK_TYPE = "paid_assessment"
LOCKED_AFTER_STAGE = "canvas"
PAYMENT_REQUIRED_DETAIL = {
    "code": "PAYMENT_REQUIRED",
    "message": "Commercial canvas diagnosis is free. Please unlock the full AI innovation plan before continuing.",
    "locked_after_stage": LOCKED_AFTER_STAGE,
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_pem(value: str) -> bytes:
    return value.replace("\\n", "\n").encode("utf-8")


def _decimal_yuan_to_cents(value: str | int | float | Decimal) -> int:
    decimal_value = Decimal(str(value))
    cents = (decimal_value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


class EntitlementService:
    def has_paid_access(self, db: Session, assessment: Assessment, user: User) -> bool:
        if user.role == "instructor":
            return True
        record = db.scalar(
            select(AssessmentEntitlement).where(
                AssessmentEntitlement.assessment_id == assessment.id,
                AssessmentEntitlement.user_id == user.id,
            )
        )
        return record is not None

    def require_paid_access(self, db: Session, assessment: Assessment, user: User) -> None:
        if self.has_paid_access(db, assessment, user):
            return
        detail = dict(PAYMENT_REQUIRED_DETAIL)
        detail["assessment_id"] = assessment.id
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)

    def get_status(self, db: Session, assessment: Assessment, user: User) -> EntitlementResponse:
        latest_order = db.scalar(
            select(PaymentOrder)
            .where(
                PaymentOrder.assessment_id == assessment.id,
                PaymentOrder.user_id == user.id,
            )
            .order_by(PaymentOrder.created_at.desc())
        )
        entitlement = db.scalar(
            select(AssessmentEntitlement).where(
                AssessmentEntitlement.assessment_id == assessment.id,
                AssessmentEntitlement.user_id == user.id,
            )
        )
        if user.role == "instructor" and entitlement is None:
            return EntitlementResponse(
                assessment_id=assessment.id,
                is_unlocked=True,
                can_continue=True,
                locked_after_stage=LOCKED_AFTER_STAGE,
                unlock_type="role_bypass",
                unlocked_at=None,
                latest_order=self._order_to_response(latest_order) if latest_order else None,
            )

        return EntitlementResponse(
            assessment_id=assessment.id,
            is_unlocked=entitlement is not None,
            can_continue=entitlement is not None,
            locked_after_stage=LOCKED_AFTER_STAGE,
            unlock_type=entitlement.unlock_type if entitlement else None,
            unlocked_at=entitlement.unlocked_at if entitlement else None,
            latest_order=self._order_to_response(latest_order) if latest_order else None,
        )

    def grant(
        self,
        db: Session,
        assessment_id: str,
        user_id: str,
        source_order_id: str | None = None,
        unlock_type: str = PAID_UNLOCK_TYPE,
    ) -> AssessmentEntitlement:
        record = db.scalar(
            select(AssessmentEntitlement).where(
                AssessmentEntitlement.assessment_id == assessment_id,
                AssessmentEntitlement.user_id == user_id,
            )
        )
        if record is not None:
            return record

        record = AssessmentEntitlement(
            assessment_id=assessment_id,
            user_id=user_id,
            unlock_type=unlock_type,
            source_order_id=source_order_id,
            unlocked_at=_now(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def _order_to_response(self, order: PaymentOrder | None) -> PaymentOrderResponse | None:
        if order is None:
            return None
        return PaymentOrderResponse(
            order_id=order.id,
            order_no=order.order_no,
            assessment_id=order.assessment_id,
            provider=order.provider,  # type: ignore[arg-type]
            amount_cents=order.amount_cents,
            currency=order.currency,
            status=order.status,  # type: ignore[arg-type]
            qr_code_url=order.qr_code_url,
            expires_at=order.expires_at,
            paid_at=order.paid_at,
            created_at=order.created_at,
        )


class PaymentService:
    def __init__(self) -> None:
        self.entitlements = EntitlementService()

    def create_order(
        self,
        db: Session,
        assessment: Assessment,
        user: User,
        provider: str,
    ) -> PaymentOrderResponse:
        if self.entitlements.has_paid_access(db, assessment, user):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This assessment has already been unlocked.",
            )

        existing = db.scalar(
            select(PaymentOrder)
            .where(
                PaymentOrder.assessment_id == assessment.id,
                PaymentOrder.user_id == user.id,
                PaymentOrder.provider == provider,
                PaymentOrder.status == "pending",
            )
            .order_by(PaymentOrder.created_at.desc())
        )
        if existing is not None and _as_utc(existing.expires_at) > _now():
            return self.entitlements._order_to_response(existing)  # type: ignore[return-value]

        order = PaymentOrder(
            order_no=self._new_order_no(),
            assessment_id=assessment.id,
            user_id=user.id,
            provider=provider,
            amount_cents=settings.payment_amount_cents,
            currency=settings.payment_currency,
            status="pending",
            expires_at=_now() + timedelta(minutes=settings.payment_order_expire_minutes),
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        qr_code_url, provider_payload = self._create_provider_order(order, assessment)
        order.qr_code_url = qr_code_url
        order.provider_payload = json.dumps(provider_payload, ensure_ascii=False)
        db.add(order)
        db.commit()
        db.refresh(order)
        return self.entitlements._order_to_response(order)  # type: ignore[return-value]

    def get_order(self, db: Session, order_id: str, user: User) -> PaymentOrderResponse:
        order = db.get(PaymentOrder, order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Payment order not found.")
        if user.role != "instructor" and order.user_id != user.id:
            raise HTTPException(status_code=403, detail="No permission to view this payment order.")
        if order.status == "pending" and _as_utc(order.expires_at) <= _now():
            order.status = "expired"
            db.add(order)
            db.commit()
            db.refresh(order)
        return self.entitlements._order_to_response(order)  # type: ignore[return-value]

    def process_wechat_notify(
        self,
        db: Session,
        payload: dict[str, Any],
        raw_body: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> PaymentNotifyResponse:
        data = (
            self._decrypt_wechat_notify(raw_body, headers or {})
            if settings.payment_provider_mode == "live" and payload.get("resource")
            else payload
        )
        order_no = data.get("out_trade_no")
        transaction_id = data.get("transaction_id")
        trade_state = data.get("trade_state")
        amount_cents = data.get("total_amount_cents")
        if amount_cents is None and isinstance(data.get("amount"), dict):
            amount_cents = data["amount"].get("total")
        return self._apply_paid_notify(
            db=db,
            provider="wechat",
            order_no=str(order_no or ""),
            amount_cents=int(amount_cents or 0),
            transaction_id=str(transaction_id or ""),
            success=trade_state == "SUCCESS",
            raw_payload=data,
        )

    def process_alipay_notify(
        self,
        db: Session,
        payload: dict[str, Any],
    ) -> PaymentNotifyResponse:
        if settings.payment_provider_mode == "live":
            self._verify_alipay_notify(payload)
        order_no = str(payload.get("out_trade_no") or "")
        trade_no = str(payload.get("trade_no") or "")
        trade_status = str(payload.get("trade_status") or "")
        amount_cents = payload.get("total_amount_cents")
        if amount_cents is None and payload.get("total_amount") is not None:
            amount_cents = _decimal_yuan_to_cents(payload["total_amount"])
        return self._apply_paid_notify(
            db=db,
            provider="alipay",
            order_no=order_no,
            amount_cents=int(amount_cents or 0),
            transaction_id=trade_no,
            success=trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"),
            raw_payload=payload,
        )

    def _apply_paid_notify(
        self,
        db: Session,
        provider: str,
        order_no: str,
        amount_cents: int,
        transaction_id: str,
        success: bool,
        raw_payload: dict[str, Any],
    ) -> PaymentNotifyResponse:
        order = db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == order_no))
        if order is None:
            raise HTTPException(status_code=404, detail="Payment order not found.")
        if order.provider != provider:
            raise HTTPException(status_code=400, detail="Payment provider mismatch.")
        if amount_cents != order.amount_cents:
            raise HTTPException(status_code=400, detail="Payment amount mismatch.")
        if order.status == "paid":
            return PaymentNotifyResponse(
                status="paid",
                order_no=order.order_no,
                assessment_id=order.assessment_id,
                is_unlocked=True,
            )
        if not success:
            order.status = "failed"
            order.provider_payload = json.dumps(raw_payload, ensure_ascii=False)
            db.add(order)
            db.commit()
            db.refresh(order)
            return PaymentNotifyResponse(
                status="failed",
                order_no=order.order_no,
                assessment_id=order.assessment_id,
                is_unlocked=False,
            )

        order.status = "paid"
        order.provider_transaction_id = transaction_id
        order.provider_payload = json.dumps(raw_payload, ensure_ascii=False)
        order.paid_at = _now()
        db.add(order)
        db.commit()
        db.refresh(order)
        self.entitlements.grant(
            db,
            assessment_id=order.assessment_id,
            user_id=order.user_id,
            source_order_id=order.id,
        )
        return PaymentNotifyResponse(
            status="paid",
            order_no=order.order_no,
            assessment_id=order.assessment_id,
            is_unlocked=True,
        )

    def _create_provider_order(
        self,
        order: PaymentOrder,
        assessment: Assessment,
    ) -> tuple[str, dict[str, Any]]:
        if settings.payment_provider_mode != "live":
            return (
                f"mockpay://{order.provider}/{order.order_no}",
                {"mode": "mock", "order_no": order.order_no},
            )
        if order.provider == "wechat":
            return self._create_wechat_native_order(order, assessment)
        if order.provider == "alipay":
            return self._create_alipay_precreate_order(order, assessment)
        raise HTTPException(status_code=400, detail="Unsupported payment provider.")

    def _create_wechat_native_order(
        self,
        order: PaymentOrder,
        assessment: Assessment,
    ) -> tuple[str, dict[str, Any]]:
        required = [
            settings.wechat_pay_app_id,
            settings.wechat_pay_mch_id,
            settings.wechat_pay_merchant_serial_no,
            settings.wechat_pay_merchant_private_key,
            settings.wechat_pay_api_v3_key,
            settings.payment_notify_base_url,
        ]
        if any(not value for value in required):
            raise HTTPException(status_code=503, detail="WeChat Pay credentials are incomplete.")

        path = "/v3/pay/transactions/native"
        body = {
            "appid": settings.wechat_pay_app_id,
            "mchid": settings.wechat_pay_mch_id,
            "description": f"{assessment.company_name} AI innovation plan unlock"[:127],
            "out_trade_no": order.order_no,
            "time_expire": _as_utc(order.expires_at).isoformat().replace("+00:00", "Z"),
            "notify_url": f"{settings.payment_notify_base_url.rstrip('/')}/api/payments/wechat/notify",
            "amount": {"total": order.amount_cents, "currency": order.currency},
        }
        body_text = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        authorization = self._wechat_authorization("POST", path, body_text)
        response = httpx.post(
            f"{settings.wechat_pay_api_base_url.rstrip('/')}{path}",
            content=body_text.encode("utf-8"),
            headers={
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"WeChat Pay order creation failed: {response.text}")
        payload = response.json()
        code_url = payload.get("code_url")
        if not code_url:
            raise HTTPException(status_code=502, detail="WeChat Pay response did not include code_url.")
        return str(code_url), payload

    def _create_alipay_precreate_order(
        self,
        order: PaymentOrder,
        assessment: Assessment,
    ) -> tuple[str, dict[str, Any]]:
        required = [
            settings.alipay_app_id,
            settings.alipay_private_key,
            settings.payment_notify_base_url,
        ]
        if any(not value for value in required):
            raise HTTPException(status_code=503, detail="Alipay credentials are incomplete.")

        biz_content = {
            "out_trade_no": order.order_no,
            "total_amount": f"{Decimal(order.amount_cents) / Decimal('100'):.2f}",
            "subject": f"{assessment.company_name} AI innovation plan unlock"[:256],
            "timeout_express": f"{settings.payment_order_expire_minutes}m",
        }
        params: dict[str, str] = {
            "app_id": settings.alipay_app_id,
            "method": "alipay.trade.precreate",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": _now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": f"{settings.payment_notify_base_url.rstrip('/')}/api/payments/alipay/notify",
            "biz_content": json.dumps(biz_content, ensure_ascii=False, separators=(",", ":")),
        }
        params["sign"] = self._alipay_sign(params)
        response = httpx.post(
            settings.alipay_gateway_url,
            content=urlencode(params).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            timeout=15,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Alipay order creation failed: {response.text}")
        payload = response.json()
        result = payload.get("alipay_trade_precreate_response", payload)
        qr_code = result.get("qr_code")
        if not qr_code:
            raise HTTPException(status_code=502, detail="Alipay response did not include qr_code.")
        return str(qr_code), payload

    def _wechat_authorization(self, method: str, path: str, body_text: str) -> str:
        timestamp = str(int(_now().timestamp()))
        nonce = secrets.token_urlsafe(16)
        message = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body_text}\n".encode("utf-8")
        private_key = serialization.load_pem_private_key(
            _normalize_pem(settings.wechat_pay_merchant_private_key),
            password=None,
        )
        signature = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
        signature_text = base64.b64encode(signature).decode("ascii")
        return (
            'WECHATPAY2-SHA256-RSA2048 '
            f'mchid="{settings.wechat_pay_mch_id}",'
            f'nonce_str="{nonce}",'
            f'timestamp="{timestamp}",'
            f'serial_no="{settings.wechat_pay_merchant_serial_no}",'
            f'signature="{signature_text}"'
        )

    def _decrypt_wechat_notify(
        self,
        raw_body: bytes,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        self._verify_wechat_signature(raw_body, headers)
        payload = json.loads(raw_body.decode("utf-8"))
        resource = payload.get("resource") or {}
        ciphertext = base64.b64decode(resource.get("ciphertext", ""))
        nonce = str(resource.get("nonce", "")).encode("utf-8")
        associated_data = str(resource.get("associated_data", "")).encode("utf-8")
        aesgcm = AESGCM(settings.wechat_pay_api_v3_key.encode("utf-8"))
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
        return json.loads(plaintext.decode("utf-8"))

    def _verify_wechat_signature(self, raw_body: bytes, headers: dict[str, str]) -> None:
        if not settings.wechat_pay_platform_public_key:
            raise HTTPException(status_code=503, detail="WeChat Pay platform public key is not configured.")
        timestamp = headers.get("wechatpay-timestamp") or headers.get("Wechatpay-Timestamp")
        nonce = headers.get("wechatpay-nonce") or headers.get("Wechatpay-Nonce")
        signature = headers.get("wechatpay-signature") or headers.get("Wechatpay-Signature")
        if not timestamp or not nonce or not signature:
            raise HTTPException(status_code=401, detail="Missing WeChat Pay notification signature headers.")
        message = f"{timestamp}\n{nonce}\n{raw_body.decode('utf-8')}\n".encode("utf-8")
        public_key = serialization.load_pem_public_key(
            _normalize_pem(settings.wechat_pay_platform_public_key)
        )
        try:
            public_key.verify(
                base64.b64decode(signature),
                message,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Invalid WeChat Pay notification signature.") from exc

    def _alipay_sign(self, params: dict[str, str]) -> str:
        message = self._alipay_signing_text(params).encode("utf-8")
        private_key = serialization.load_pem_private_key(
            _normalize_pem(settings.alipay_private_key),
            password=None,
        )
        signature = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
        return base64.b64encode(signature).decode("ascii")

    def _verify_alipay_notify(self, payload: dict[str, Any]) -> None:
        if not settings.alipay_public_key:
            raise HTTPException(status_code=503, detail="Alipay public key is not configured.")
        signature = payload.get("sign")
        if not signature:
            raise HTTPException(status_code=401, detail="Missing Alipay notification signature.")
        message = self._alipay_signing_text(payload).encode("utf-8")
        public_key = serialization.load_pem_public_key(_normalize_pem(settings.alipay_public_key))
        try:
            public_key.verify(
                base64.b64decode(str(signature)),
                message,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Invalid Alipay notification signature.") from exc

    def _alipay_signing_text(self, params: dict[str, Any]) -> str:
        clean_params = {
            key: str(value)
            for key, value in params.items()
            if key not in ("sign", "sign_type") and value is not None and str(value) != ""
        }
        return "&".join(f"{key}={clean_params[key]}" for key in sorted(clean_params))

    def _new_order_no(self) -> str:
        return f"MT{_now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(4).upper()}"


def require_report_paid_access(db: Session, report: GeneratedReport, user: User) -> None:
    assessment = db.get(Assessment, report.assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    if user.role != "instructor" and assessment.user_id != user.id:
        raise HTTPException(status_code=403, detail="No permission to view this report.")
    EntitlementService().require_paid_access(db, assessment, user)
