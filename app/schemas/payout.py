from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.payout import PayoutStatus


class PayoutRunRequest(BaseModel):
    """Request schema for running payout generation."""

    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Currency code for payouts",
        examples=["PEN"],
    )

    as_of: date = Field(
        ...,
        description="Payout date (YYYY-MM-DD)",
        examples=["2025-12-27"],
    )

    min_amount: int = Field(
        ...,
        gt=0,
        description="Minimum amount in cents to generate payout",
        examples=[5000],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "currency": "PEN",
                "as_of": "2025-12-27",
                "min_amount": 5000,
            }
        }


class PayoutRunResponse(BaseModel):
    """Response schema for payout run."""

    status: str = Field(
        ...,
        description="Job status",
    )

    message: str

    payouts_created: int = Field(
        ...,
        description="Number of payouts created",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "accepted",
                "message": "Payout generation started",
                "payouts_created": 3,
            }
        }


class PayoutItemResponse(BaseModel):
    """Response schema for payout item."""

    type: str = Field(
        ...,
        description="Item type (e.g., 'net_sales', 'fees')",
    )

    amount: int = Field(
        ...,
        description="Amount in cents",
    )

    class Config:
        from_attributes = True


class PayoutResponse(BaseModel):
    """Response schema for payout details."""

    payout_id: str = Field(
        ...,
        description="Payout identifier",
    )

    restaurant_id: str = Field(
        ...,
        description="Restaurant identifier",
    )

    currency: str = Field(
        ...,
        description="Currency code",
    )

    amount: int = Field(
        ...,
        description="Total payout amount in cents",
    )

    status: PayoutStatus = Field(
        ...,
        description="Payout status",
    )

    created_at: datetime = Field(
        ...,
        description="When payout was created",
    )

    paid_at: Optional[datetime] = Field(
        default=None,
        description="When payout was paid",
    )

    items: List[PayoutItemResponse] = Field(
        default_factory=list,
        description="Breakdown of payout calculation",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "payout_id": "po_0001",
                "restaurant_id": "res_001",
                "currency": "PEN",
                "amount": 10800,
                "status": "created",
                "created_at": "2025-12-27T18:00:00Z",
                "paid_at": None,
                "items": [
                    {"type": "gross_sales", "amount": 12000},
                    {"type": "fees", "amount": -600},
                    {"type": "refunds", "amount": -600},
                ],
            }
        }
