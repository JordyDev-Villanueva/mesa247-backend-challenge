from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.ledger import LedgerRepository
from app.schemas.restaurant import RestaurantBalanceResponse
from app.core.exceptions import RestaurantNotFoundError


class LedgerService:
    """Service for ledger operations and balance calculations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ledger_repo = LedgerRepository(session)

    async def get_restaurant_balance(
        self, restaurant_id: str, currency: str = "PEN"
    ) -> RestaurantBalanceResponse:
        """
        Get balance for a restaurant.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code (defaults to PEN)

        Returns:
            RestaurantBalanceResponse with balance details

        Raises:
            RestaurantNotFoundError: If restaurant has no transactions
        """
        # Calculate available balance
        available = await self.ledger_repo.get_balance(restaurant_id, currency)

        # Get last event timestamp
        last_event_at = await self.ledger_repo.get_last_event_time(
            restaurant_id, currency
        )

        # If no transactions found, restaurant doesn't exist
        if available == 0 and last_event_at is None:
            raise RestaurantNotFoundError(restaurant_id)

        return RestaurantBalanceResponse(
            restaurant_id=restaurant_id,
            currency=currency,
            available=available,
            pending=0,  # Not implemented yet (bonus feature)
            last_event_at=last_event_at,
        )

    async def get_ledger_breakdown(
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
        return await self.ledger_repo.get_breakdown(restaurant_id, currency)
