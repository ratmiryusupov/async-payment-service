import asyncio
import logging

from core.db import AsyncSessionLocal
from messaging.broker import broker
from repositories.outbox import OutboxRepository
from workers.utils import connect_broker_with_retry


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 3
BATCH_SIZE = 100
ROUTING_KEY = "payments.new"


async def publish_outbox_events() -> None:
    await connect_broker_with_retry(broker)

    try:
        while True:
            async with AsyncSessionLocal() as session:
                repo = OutboxRepository(session)
                events = await repo.get_pending_batch(limit=BATCH_SIZE)

                if not events:
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue

                for event in events:
                    try:
                        await broker.publish(
                            message=event.payload,
                            routing_key=ROUTING_KEY,
                        )
                        await repo.mark_as_published(event)
                        logger.info("Published outbox event %s", event.id)
                    except Exception as exc:
                        await repo.mark_publish_failed(event, str(exc))
                        logger.exception(
                            "Failed to publish outbox event %s: %s",
                            event.id,
                            exc,
                        )

                await session.commit()

            await asyncio.sleep(1)
    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(publish_outbox_events())