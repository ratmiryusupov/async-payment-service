import pytest

from services.webhook import WebhookService, WebhookDeliveryError


@pytest.mark.asyncio
async def test_webhook_retry_fail():
    service = WebhookService(timeout=0.1)

    with pytest.raises(WebhookDeliveryError):
        await service.send_with_retry(
            url="http://127.0.0.1:9999/fail",
            payload={"x": 1},
            max_attempts=3,
            base_delay=0.1,
        )