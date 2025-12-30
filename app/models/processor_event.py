from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import DateTime, Integer, String, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ProcessorEvent(BaseModel):
    """
    Stores events received from payment processors.

    Implements idempotency through unique constraint on event_id.
    """

    __tablename__ = "processor_events"

    event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
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

    fee: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_processor_events_restaurant_occurred", "restaurant_id", "occurred_at"),
    )

    def __repr__(self) -> str:
        return f"<ProcessorEvent(event_id={self.event_id}, type={self.event_type})>"
