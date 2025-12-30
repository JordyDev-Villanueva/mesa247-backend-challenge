import enum
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import DateTime, Integer, String, Enum, Index, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PayoutStatus(str, enum.Enum):
    """Status of a payout."""

    CREATED = "created"  # Payout created, funds reserved
    PAID = "paid"  # Payout successfully paid
    FAILED = "failed"  # Payout failed


class Payout(BaseModel):
    """
    Payout records for restaurant withdrawals.

    Implements idempotency through unique constraint on
    (restaurant_id, currency, as_of_date).
    """

    __tablename__ = "payouts"

    payout_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    restaurant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[PayoutStatus] = mapped_column(
        Enum(PayoutStatus),
        nullable=False,
        default=PayoutStatus.CREATED,
        index=True,
    )

    as_of_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship to payout items
    items: Mapped[List["PayoutItem"]] = relationship(
        "PayoutItem",
        back_populates="payout",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "currency",
            "as_of_date",
            name="uq_payout_restaurant_currency_date",
        ),
        Index("idx_payouts_restaurant", "restaurant_id", "currency", "as_of_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<Payout(payout_id={self.payout_id}, "
            f"restaurant_id={self.restaurant_id}, amount={self.amount})>"
        )
