import asyncio
import logging

from messaging.broker import broker
from workers.utils import connect_broker_with_retry


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@broker.subscriber("payments.dlq")
async def handle_dlq_message(message: dict) -> None:
    logger.error("DLQ message received: %s", message)


async def main() -> None:
    logger.info("Starting DLQ consumer...")
    await connect_broker_with_retry(broker)
    await broker.start()
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())