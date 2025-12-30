from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger_entry import LedgerEntry, LedgerEntryType
from app.repositories.base import BaseRepository


class LedgerRepository(BaseRepository[LedgerEntry]):
    """Repository for ledger entry operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(LedgerEntry, session)

    async def get_balance(self, restaurant_id: str, currency: str) -> int:
        """
        Calculate available balance for a restaurant in a specific currency.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code

        Returns:
            Available balance in cents
        """
        result = await self.session.execute(
            select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
                and_(
                    LedgerEntry.restaurant_id == restaurant_id,
                    LedgerEntry.currency == currency,
                )
            )
        )
        balance = result.scalar_one()
        return int(balance)

    async def get_last_event_time(
        self, restaurant_id: str, currency: str
    ) -> Optional[datetime]:
        """
        Get the timestamp of the last ledger entry for a restaurant.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code

        Returns:
            Timestamp of last entry, or None if no entries exist
        """
        result = await self.session.execute(
            select(func.max(LedgerEntry.created_at)).where(
                and_(
                    LedgerEntry.restaurant_id == restaurant_id,
                    LedgerEntry.currency == currency,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_breakdown(
        self, restaurant_id: str, currency: str
    ) -> dict:
        """
        Get detailed breakdown of ledger entries for payout calculation.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code

        Returns:
            Dictionary with breakdown by entry type
        """
        # Get sum grouped by entry type
        result = await self.session.execute(
            select(
                LedgerEntry.entry_type,
                func.sum(LedgerEntry.amount).label("total"),
            )
            .where(
                and_(
                    LedgerEntry.restaurant_id == restaurant_id,
                    LedgerEntry.currency == currency,
                )
            )
            .group_by(LedgerEntry.entry_type)
        )

        breakdown = {}
        for row in result:
            breakdown[row.entry_type.value] = int(row.total)

        return breakdown
