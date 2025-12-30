from datetime import date
from typing import List, Dict
import uuid

from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.payout import Payout, PayoutStatus
from app.models.payout_item import PayoutItem
from app.models.ledger_entry import LedgerEntry
from app.repositories.payout import PayoutRepository
from app.repositories.ledger import LedgerRepository
from app.schemas.payout import PayoutResponse, PayoutItemResponse
from app.core.exceptions import PayoutNotFoundError

logger = get_logger(__name__)


class PayoutGeneratorService:
    """Service for generating and managing payouts."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.payout_repo = PayoutRepository(session)
        self.ledger_repo = LedgerRepository(session)

    async def generate_payouts(
        self, currency: str, as_of_date: date, min_amount: int
    ) -> int:
        """
        Generate payouts for all eligible restaurants.

        Args:
            currency: Currency code
            as_of_date: Payout date
            min_amount: Minimum balance required (in cents)

        Returns:
            Number of payouts created
        """
        # Get all unique restaurant IDs with ledger entries in this currency
        result = await self.session.execute(
            select(distinct(LedgerEntry.restaurant_id)).where(
                LedgerEntry.currency == currency
            )
        )
        restaurant_ids = [row[0] for row in result.all()]

        payouts_created = 0

        for restaurant_id in restaurant_ids:
            # Check if payout already exists
            exists = await self.payout_repo.payout_exists_for_date(
                restaurant_id, currency, as_of_date
            )
            if exists:
                logger.info(
                    "Payout already exists, skipping",
                    extra={
                        "restaurant_id": restaurant_id,
                        "as_of_date": as_of_date.isoformat(),
                    },
                )
                continue

            # Get balance
            balance = await self.ledger_repo.get_balance(restaurant_id, currency)

            # Check if meets minimum
            if balance < min_amount:
                logger.debug(
                    "Restaurant balance below minimum, skipping",
                    extra={
                        "restaurant_id": restaurant_id,
                        "balance": balance,
                        "min_amount": min_amount,
                    },
                )
                continue

            # Create payout
            try:
                await self._create_payout(
                    restaurant_id, currency, balance, as_of_date
                )
                payouts_created += 1
            except Exception as e:
                logger.error(
                    "Failed to create payout",
                    extra={
                        "restaurant_id": restaurant_id,
                        "error": str(e),
                    },
                )
                continue

        logger.info(
            "Payout generation completed",
            extra={
                "currency": currency,
                "as_of_date": as_of_date.isoformat(),
                "payouts_created": payouts_created,
            },
        )

        return payouts_created

    async def _create_payout(
        self, restaurant_id: str, currency: str, amount: int, as_of_date: date
    ) -> Payout:
        """
        Create a payout with breakdown items.

        Args:
            restaurant_id: Restaurant identifier
            currency: Currency code
            amount: Payout amount in cents
            as_of_date: Payout date

        Returns:
            Created Payout
        """
        # Generate unique payout_id
        payout_id = f"po_{uuid.uuid4().hex[:12]}"

        # Get ledger breakdown
        breakdown = await self.ledger_repo.get_breakdown(restaurant_id, currency)

        # Create payout
        payout = Payout(
            payout_id=payout_id,
            restaurant_id=restaurant_id,
            currency=currency,
            amount=amount,
            status=PayoutStatus.CREATED,
            as_of_date=as_of_date,
        )
        await self.payout_repo.create(payout)

        # Create payout items from breakdown
        items_to_create = []

        # Charges (gross sales)
        if "charge" in breakdown:
            items_to_create.append(
                PayoutItem(
                    payout_id=payout.id,
                    item_type="gross_sales",
                    amount=breakdown["charge"],
                )
            )

        # Fees
        if "fee" in breakdown:
            items_to_create.append(
                PayoutItem(
                    payout_id=payout.id,
                    item_type="fees",
                    amount=breakdown["fee"],
                )
            )

        # Refunds
        if "refund" in breakdown:
            items_to_create.append(
                PayoutItem(
                    payout_id=payout.id,
                    item_type="refunds",
                    amount=breakdown["refund"],
                )
            )

        # Add items to session
        for item in items_to_create:
            self.session.add(item)

        # Create PAYOUT_RESERVE ledger entry
        from app.models.ledger_entry import LedgerEntry, LedgerEntryType

        reserve_entry = LedgerEntry(
            restaurant_id=restaurant_id,
            currency=currency,
            entry_type=LedgerEntryType.PAYOUT_RESERVE,
            amount=-amount,  # Negative to lock funds
            reference_type="payout",
            reference_id=payout_id,
            entry_metadata={"as_of_date": as_of_date.isoformat()},
        )
        await self.ledger_repo.create(reserve_entry)

        logger.info(
            "Payout created",
            extra={
                "payout_id": payout_id,
                "restaurant_id": restaurant_id,
                "amount": amount,
            },
        )

        return payout

    async def get_payout(self, payout_id: str) -> PayoutResponse:
        """
        Get payout details by payout_id.

        Args:
            payout_id: Unique payout identifier

        Returns:
            PayoutResponse with details

        Raises:
            PayoutNotFoundError: If payout not found
        """
        payout = await self.payout_repo.get_by_payout_id(payout_id)
        if not payout:
            raise PayoutNotFoundError(payout_id)

        # Convert items to response format
        items = [
            PayoutItemResponse(
                type=item.item_type,
                amount=item.amount,
            )
            for item in payout.items
        ]

        return PayoutResponse(
            payout_id=payout.payout_id,
            restaurant_id=payout.restaurant_id,
            currency=payout.currency,
            amount=payout.amount,
            status=payout.status,
            created_at=payout.created_at,
            paid_at=payout.paid_at,
            items=items,
        )
