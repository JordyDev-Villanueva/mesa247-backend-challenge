from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processor_event import ProcessorEvent
from app.repositories.base import BaseRepository


class ProcessorEventRepository(BaseRepository[ProcessorEvent]):
    """Repository for processor event operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(ProcessorEvent, session)

    async def get_by_event_id(self, event_id: str) -> Optional[ProcessorEvent]:
        """
        Get an event by its event_id (for idempotency checks).

        Args:
            event_id: Unique event identifier

        Returns:
            ProcessorEvent if found, None otherwise
        """
        result = await self.session.execute(
            select(ProcessorEvent).where(ProcessorEvent.event_id == event_id)
        )
        return result.scalar_one_or_none()

    async def event_exists(self, event_id: str) -> bool:
        """
        Check if an event already exists.

        Args:
            event_id: Unique event identifier

        Returns:
            True if event exists, False otherwise
        """
        event = await self.get_by_event_id(event_id)
        return event is not None
