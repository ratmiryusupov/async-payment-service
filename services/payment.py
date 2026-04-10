from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.outbox import OutboxEvent
from models.payment import Payment, PaymentStatus
from repositories.outbox import OutboxRepository
from repositories.payment import PaymentRepository
from schemas.payment import PaymentCreateRequest


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.outbox_repo = OutboxRepository(session)

    async def create_payment(
        self,
        payload: PaymentCreateRequest,
        idempotency_key: str,
    ) -> Payment:
        existing_payment = await self.payment_repo.get_by_idempotency_key(idempotency_key)
        if existing_payment is not None:
            return existing_payment

        payment = Payment(
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            metadata_json=payload.metadata,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            webhook_url=str(payload.webhook_url),
        )
        await self.payment_repo.add(payment)
        await self.session.flush()

        outbox_event = OutboxEvent(
            event_type="payment.created",
            aggregate_id=payment.id,
            payload={
                "payment_id": str(payment.id),
            },
        )
        await self.outbox_repo.add(outbox_event)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            existing_payment = await self.payment_repo.get_by_idempotency_key(idempotency_key)
            if existing_payment is None:
                raise
            return existing_payment

        await self.session.refresh(payment)
        return payment

    async def get_payment(self, payment_id: UUID) -> Payment | None:
        return await self.payment_repo.get_by_id(payment_id)