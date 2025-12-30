from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    """Valid event types from payment processor."""

    CHARGE_SUCCEEDED = "charge_succeeded"
    REFUND_SUCCEEDED = "refund_succeeded"
    PAYOUT_PAID = "payout_paid"


class ProcessorEventRequest(BaseModel):
    """Request schema for ingesting processor events."""

    event_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique event identifier",
        examples=["evt_000123"],
    )

    event_type: EventType = Field(
        ...,
        description="Type of event",
    )

    occurred_at: datetime = Field(
        ...,
        description="When the event occurred (ISO 8601)",
    )

    restaurant_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Restaurant identifier",
        examples=["res_001"],
    )

    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)",
        examples=["PEN", "USD"],
    )

    amount: int = Field(
        ...,
        gt=0,
        description="Amount in cents (must be positive)",
        examples=[12000],
    )

    fee: int = Field(
        ...,
        ge=0,
        description="Fee in cents (must be non-negative)",
        examples=[600],
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional event metadata",
    )

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        """Ensure currency is uppercase."""
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_000123",
                "event_type": "charge_succeeded",
                "occurred_at": "2025-12-20T15:10:00Z",
                "restaurant_id": "res_001",
                "currency": "PEN",
                "amount": 12000,
                "fee": 600,
                "metadata": {
                    "reservation_id": "rsv_987",
                    "payment_id": "pay_456",
                },
            }
        }


class ProcessorEventResponse(BaseModel):
    """Response schema for processor event ingestion."""

    event_id: str
    status: str = Field(
        ...,
        description="Processing status: 'processed' or 'already_processed'",
    )
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_000123",
                "status": "processed",
                "message": "Event processed successfully",
            }
        }
