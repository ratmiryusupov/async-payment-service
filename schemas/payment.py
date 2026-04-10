from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from models.payment import Currency, PaymentStatus


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=2)
    currency: Currency
    description: str = Field(..., min_length=1, max_length=1000)
    metadata: dict = Field(default_factory=dict)
    webhook_url: HttpUrl


class PaymentCreateResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    currency: Currency
    description: str

    metadata: dict = Field(validation_alias="metadata_json", serialization_alias="metadata")

    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime