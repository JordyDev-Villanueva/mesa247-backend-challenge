from typing import Optional, List
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payout import Payout, PayoutStatus
from app.repositories.base import BaseRepository


class PayoutRepository(BaseRepository[Payout]):
    """Repository for payout operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Payout, session)

    async def get_by_payout_id(self, payout_id: str) -> Optional[Payout]:
        """
        Get a payout by its payout_id.

        Args:
            payout_id: Unique payout identifier

        Returns:
            Payout if found, None otherwise
        """
        result = await self.session.execute(
            select(Payout)
            .where(Payout.payout_id == payout_id)
            .options(selectinload(Payout.items))
        )
        return result.scalar_one_or_none()

    async def payout_exists_for_date(
        self, restaurant_id: str, currency: str, as_of_date: date
    ) -> bool:
        """
        Check if a payout already exists for a restaurant on a specific date.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code
            as_of_date: Payout date

        Returns:
            True if payout exists, False otherwise
        """
        result = await self.session.execute(
            select(Payout).where(
                and_(
                    Payout.restaurant_id == restaurant_id,
                    Payout.currency == currency,
                    Payout.as_of_date == as_of_date,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_by_restaurant_and_date(
        self, restaurant_id: str, currency: str, as_of_date: date
    ) -> Optional[Payout]:
        """
        Get payout for a restaurant on a specific date.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code
            as_of_date: Payout date

        Returns:
            Payout if found, None otherwise
        """
        result = await self.session.execute(
            select(Payout)
            .where(
                and_(
                    Payout.restaurant_id == restaurant_id,
                    Payout.currency == currency,
                    Payout.as_of_date == as_of_date,
                )
            )
            .options(selectinload(Payout.items))
        )
        return result.scalar_one_or_none()

    async def get_restaurants_with_balance(
        self, currency: str, min_amount: int
    ) -> List[str]:
        """
        Get list of restaurant IDs that have sufficient balance.

        Note: This is a placeholder. Actual implementation would query
        ledger entries to calculate balances.

        Args:
            currency: Currency code
            min_amount: Minimum balance required

        Returns:
            List of restaurant IDs
        """
        # This will be implemented in the service layer using LedgerRepository
        return []
