from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PagoCreateRequest(BaseModel):
    pedido_id: int = Field(..., ge=1)
    token: str = Field(..., min_length=1)
    payment_method_id: str = Field(..., min_length=1, max_length=50)
    installments: int = Field(default=1, ge=1)
    issuer_id: Optional[str] = Field(default=None, max_length=50)
    payer_email: Optional[EmailStr] = None


class PagoResponse(BaseModel):
    id: int
    pedido_id: int
    mp_payment_id: Optional[int] = None
    mp_status: str
    mp_status_detail: Optional[str] = None
    transaction_amount: Decimal
    payment_method_id: Optional[str] = None
    external_reference: str
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WebhookResponse(BaseModel):
    status: str
