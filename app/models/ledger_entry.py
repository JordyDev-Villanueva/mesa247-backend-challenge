import enum
from typing import Dict, Any, Optional

from sqlalchemy import Integer, String, Enum, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class LedgerEntryType(str, enum.Enum):
    """Types of ledger entries for financial tracking."""

    CHARGE = "charge"  # Money in from successful charge
    FEE = "fee"  # Processor fee deduction
    REFUND = "refund"  # Money out from refund
    REFUND_FEE = "refund_fee"  # Fee refund (if applicable)
    PAYOUT_RESERVE = "payout_reserve"  # Lock funds for payout
    PAYOUT_RELEASE = "payout_release"  # Final payout deduction


class LedgerEntry(BaseModel):
    """
    Double-entry style ledger for tracking all financial movements.

    Each transaction creates appropriate debit/credit entries.
    Immutable once created (no updates, only inserts).
    """

    __tablename__ = "ledger_entries"

    restaurant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    entry_type: Mapped[LedgerEntryType] = mapped_column(
        Enum(LedgerEntryType),
        nullable=False,
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reference_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reference_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    __table_args__ = (
        Index("idx_ledger_restaurant_currency", "restaurant_id", "currency"),
        Index("idx_ledger_reference", "reference_type", "reference_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<LedgerEntry(restaurant_id={self.restaurant_id}, "
            f"type={self.entry_type}, amount={self.amount})>"
        )
