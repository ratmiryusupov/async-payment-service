from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db_session
from core.security import verify_api_key
from schemas.payment import (
    PaymentCreateRequest,
    PaymentCreateResponse,
    PaymentResponse,
)
from services.payment import PaymentService


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "",
    response_model=PaymentCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_api_key)],
)
async def create_payment(
    payload: PaymentCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> PaymentCreateResponse:
    service = PaymentService(session)
    payment = await service.create_payment(payload, idempotency_key)

    return PaymentCreateResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> PaymentResponse:
    service = PaymentService(session)
    payment = await service.get_payment(payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return PaymentResponse.model_validate(payment)