from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.logging import get_logger
from app.schemas.restaurant import RestaurantBalanceResponse
from app.services.ledger import LedgerService

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/{restaurant_id}/balance",
    response_model=RestaurantBalanceResponse,
    summary="Get restaurant balance",
    description="Retrieve the current balance for a restaurant",
    tags=["restaurants"],
)
async def get_restaurant_balance(
    restaurant_id: str,
    currency: str = Query(
        default="PEN",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)",
    ),
    db: AsyncSession = Depends(get_db),
) -> RestaurantBalanceResponse:
    """
    Get the current balance for a restaurant.

    **Parameters:**
    - **restaurant_id**: Restaurant identifier (e.g., "res_001")
    - **currency**: Currency code (default: "PEN")

    **Returns:**
    - Available balance in cents
    - Last event timestamp
    - Pending balance (reserved for payouts)

    **Raises:**
    - **404 Not Found**: Restaurant has no transactions
    """
    service = LedgerService(db)

    balance = await service.get_restaurant_balance(restaurant_id, currency.upper())

    logger.info(
        "Balance retrieved",
        extra={
            "restaurant_id": restaurant_id,
            "currency": currency,
            "available": balance.available,
        },
    )

    return balance
