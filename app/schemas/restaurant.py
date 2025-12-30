from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RestaurantBalanceResponse(BaseModel):
    """Response schema for restaurant balance query."""

    restaurant_id: str = Field(
        ...,
        description="Restaurant identifier",
    )

    currency: str = Field(
        ...,
        description="Currency code",
    )

    available: int = Field(
        ...,
        description="Available balance in cents",
    )

    pending: int = Field(
        default=0,
        description="Pending balance in cents (reserved for payouts)",
    )

    last_event_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last processed event",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "res_001",
                "currency": "PEN",
                "available": 10800,
                "pending": 0,
                "last_event_at": "2025-12-20T15:10:00Z",
            }
        }
