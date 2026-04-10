import asyncio
import logging
import random
from uuid import UUID

from core.db import AsyncSessionLocal
from messaging.broker import broker
from models.payment import PaymentStatus
from repositories.payment import PaymentRepository
from services.payment_webhook import build_payment_webhook_payload
from services.webhook import WebhookDeliveryError, WebhookService
from workers.utils import connect_broker_with_retry


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DLQ_ROUTING_KEY = "payments.dlq"


@broker.subscriber("payments.new")
async def handle_new_payment(message: dict) -> None:
    logger.info("Got message: %s", message)

    payment_id_raw = message.get("payment_id")
    if not payment_id_raw:
        logger.warning("Message without payment_id: %s", message)
        return

    payment_id = UUID(payment_id_raw)
    webhook_service = WebhookService()

    async with AsyncSessionLocal() as session:
        repo = PaymentRepository(session)
        payment = await repo.get_by_id(payment_id)

        if payment is None:
            logger.warning("Payment %s not found", payment_id)
            return

        if payment.status != PaymentStatus.PENDING:
            logger.info(
                "Payment %s already processed with status %s",
                payment.id,
                payment.status,
            )
            return

        await asyncio.sleep(random.uniform(2, 5))

        if random.random() < 0.9:
            await repo.mark_as_succeeded(payment)
            logger.info("Payment %s succeeded", payment.id)
        else:
            await repo.mark_as_failed(payment)
            logger.info("Payment %s failed", payment.id)

        await session.commit()
        await session.refresh(payment)

    webhook_payload = build_payment_webhook_payload(payment)

    try:
        await webhook_service.send_with_retry(
            url=payment.webhook_url,
            payload=webhook_payload,
            max_attempts=3,
            base_delay=1.0,
        )
        logger.info("Webhook delivered for payment %s", payment.id)
    except WebhookDeliveryError as exc:
        logger.error(
            "Webhook delivery permanently failed for payment %s: %s",
            payment.id,
            exc,
        )

        await broker.publish(
            message={
                "payment_id": str(payment.id),
                "webhook_url": payment.webhook_url,
                "payload": webhook_payload,
                "error": str(exc),
            },
            routing_key=DLQ_ROUTING_KEY,
        )


async def main() -> None:
    logger.info("Starting payment consumer...")
    await connect_broker_with_retry(broker)
    await broker.start()
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())