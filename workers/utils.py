import asyncio
import logging

from faststream.rabbit import RabbitBroker


logger = logging.getLogger(__name__)


async def connect_broker_with_retry(
    broker: RabbitBroker,
    retry_delay: float = 3.0,
) -> None:
    while True:
        try:
            await broker.connect()
            logger.info("Successfully connected to RabbitMQ")
            return
        except Exception as exc:
            logger.warning(
                "RabbitMQ is not ready yet, retrying in %.1f seconds: %s",
                retry_delay,
                exc,
            )
            await asyncio.sleep(retry_delay)