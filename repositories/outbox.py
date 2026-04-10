from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.outbox import OutboxEvent, OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, event: OutboxEvent) -> OutboxEvent:
        self.session.add(event)
        return event

    async def get_pending_batch(self, limit: int = 100) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxStatus.PENDING)
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_published(self, event: OutboxEvent) -> None:
        event.status = OutboxStatus.PUBLISHED
        event.published_at = datetime.now(timezone.utc)
        event.last_error = None

    async def mark_publish_failed(self, event: OutboxEvent, error_message: str) -> None:
        event.attempts += 1
        event.last_error = error_message