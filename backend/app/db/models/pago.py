from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric
from sqlmodel import Field, SQLModel


class Pago(SQLModel, table=True):

    __tablename__ = "pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    mp_payment_id: Optional[int] = Field(default=None, index=True, unique=True)
    mp_status: str = Field(max_length=30)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)
    transaction_amount: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
    )
    payment_method_id: Optional[str] = Field(default=None, max_length=50)
    external_reference: str = Field(index=True, unique=True, max_length=100)
    idempotency_key: str = Field(index=True, unique=True, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
