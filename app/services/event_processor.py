from datetime import datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.processor_event import ProcessorEvent
from app.models.ledger_entry import LedgerEntry, LedgerEntryType
from app.repositories.event import ProcessorEventRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.payout import PayoutRepository
from app.schemas.processor import ProcessorEventRequest, EventType

logger = get_logger(__name__)


class EventProcessorService:
    """
    Service for processing payment processor events.

    Handles event ingestion with idempotency and ledger entry creation.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.event_repo = ProcessorEventRepository(session)
        self.ledger_repo = LedgerRepository(session)
        self.payout_repo = PayoutRepository(session)

    async def process_event(
        self, event_data: ProcessorEventRequest
    ) -> Tuple[bool, str]:
        """
        Process a payment processor event.

        Args:
            event_data: Event data from request

        Returns:
            Tuple of (is_new_event, message)
        """
        # Check for idempotency
        existing_event = await self.event_repo.get_by_event_id(event_data.event_id)
        if existing_event:
            logger.info(
                "Duplicate event detected",
                extra={
                    "event_id": event_data.event_id,
                    "processed_at": existing_event.processed_at.isoformat()
                    if existing_event.processed_at
                    else None,
                },
            )
            return False, "Event already processed"

        # Create processor event record
        processor_event = ProcessorEvent(
            event_id=event_data.event_id,
            event_type=event_data.event_type.value,
            occurred_at=event_data.occurred_at,
            restaurant_id=event_data.restaurant_id,
            currency=event_data.currency,
            amount=event_data.amount,
            fee=event_data.fee,
            event_metadata=event_data.metadata,
            processed_at=datetime.utcnow(),
        )
        await self.event_repo.create(processor_event)

        # Create ledger entries based on event type
        if event_data.event_type == EventType.CHARGE_SUCCEEDED:
            await self._handle_charge_succeeded(event_data)
        elif event_data.event_type == EventType.REFUND_SUCCEEDED:
            await self._handle_refund_succeeded(event_data)
        elif event_data.event_type == EventType.PAYOUT_PAID:
            await self._handle_payout_paid(event_data)

        logger.info(
            "Event processed successfully",
            extra={
                "event_id": event_data.event_id,
                "event_type": event_data.event_type.value,
                "restaurant_id": event_data.restaurant_id,
            },
        )

        return True, "Event processed successfully"

    async def _handle_charge_succeeded(
        self, event_data: ProcessorEventRequest
    ) -> None:
        """
        Handle charge_succeeded event.

        Creates two ledger entries:
        1. CHARGE: +amount (money in)
        2. FEE: -fee (processor fee deduction)
        """
        # Credit: Money in from charge
        charge_entry = LedgerEntry(
            restaurant_id=event_data.restaurant_id,
            currency=event_data.currency,
            entry_type=LedgerEntryType.CHARGE,
            amount=event_data.amount,
            reference_type="processor_event",
            reference_id=event_data.event_id,
            entry_metadata=event_data.metadata,
        )
        await self.ledger_repo.create(charge_entry)

        # Debit: Fee deduction
        if event_data.fee > 0:
            fee_entry = LedgerEntry(
                restaurant_id=event_data.restaurant_id,
                currency=event_data.currency,
                entry_type=LedgerEntryType.FEE,
                amount=-event_data.fee,  # Negative for deduction
                reference_type="processor_event",
                reference_id=event_data.event_id,
                entry_metadata={"fee_for": event_data.event_id},
            )
            await self.ledger_repo.create(fee_entry)

    async def _handle_refund_succeeded(
        self, event_data: ProcessorEventRequest
    ) -> None:
        """
        Handle refund_succeeded event.

        Creates ledger entry:
        - REFUND: -amount (money out)

        Note: Fee is NOT refunded (business decision).
        """
        refund_entry = LedgerEntry(
            restaurant_id=event_data.restaurant_id,
            currency=event_data.currency,
            entry_type=LedgerEntryType.REFUND,
            amount=-event_data.amount,  # Negative for money out
            reference_type="processor_event",
            reference_id=event_data.event_id,
            entry_metadata=event_data.metadata,
        )
        await self.ledger_repo.create(refund_entry)

    async def _handle_payout_paid(self, event_data: ProcessorEventRequest) -> None:
        """
        Handle payout_paid event.

        Updates payout status and creates PAYOUT_RELEASE ledger entry.
        """
        # Get payout_id from metadata
        payout_id = event_data.metadata.get("payout_id") if event_data.metadata else None
        if not payout_id:
            logger.warning(
                "payout_paid event missing payout_id in metadata",
                extra={"event_id": event_data.event_id},
            )
            return

        # Find the payout
        payout = await self.payout_repo.get_by_payout_id(payout_id)
        if not payout:
            logger.warning(
                "Payout not found for payout_paid event",
                extra={"event_id": event_data.event_id, "payout_id": payout_id},
            )
            return

        # Update payout status to PAID
        payout.status = "paid"
        payout.paid_at = datetime.utcnow()

        # Create PAYOUT_RELEASE ledger entry
        release_entry = LedgerEntry(
            restaurant_id=payout.restaurant_id,
            currency=payout.currency,
            entry_type=LedgerEntryType.PAYOUT_RELEASE,
            amount=-payout.amount,  # Negative for money out
            reference_type="payout",
            reference_id=payout_id,
            entry_metadata={"payout_id": payout_id},
        )
        await self.ledger_repo.create(release_entry)

        logger.info(
            "Payout marked as paid",
            extra={"payout_id": payout_id, "amount": payout.amount},
        )
