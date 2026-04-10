import asyncio
import logging

import httpx


logger = logging.getLogger(__name__)


class WebhookDeliveryError(Exception):
    pass


class WebhookService:
    def __init__(self, timeout: float = 5.0) -> None:
        self.timeout = timeout

    async def send(self, url: str, payload: dict) -> None:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

    async def send_with_retry(
        self,
        url: str,
        payload: dict,
        max_attempts: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        last_exception: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                await self.send(url, payload)
                logger.info(
                    "Webhook delivered successfully to %s on attempt %s",
                    url,
                    attempt,
                )
                return
            except Exception as exc:
                last_exception = exc
                logger.warning(
                    "Webhook delivery failed to %s on attempt %s/%s: %s",
                    url,
                    attempt,
                    max_attempts,
                    exc,
                )

                if attempt < max_attempts:
                    delay = base_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

        raise WebhookDeliveryError(
            f"Webhook delivery failed after {max_attempts} attempts"
        ) from last_exception