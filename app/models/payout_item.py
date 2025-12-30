import uuid

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PayoutItem(BaseModel):
    """
    Line items breaking down payout calculation.

    Shows detailed breakdown of how payout amount was calculated.
    """

    __tablename__ = "payout_items"

    payout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payouts.id", ondelete="CASCADE"),
        nullable=False,
    )

    item_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Relationship back to payout
    payout: Mapped["Payout"] = relationship(
        "Payout",
        back_populates="items",
    )

    def __repr__(self) -> str:
        return f"<PayoutItem(type={self.item_type}, amount={self.amount})>"
