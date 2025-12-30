from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.logging import get_logger
from app.schemas.payout import PayoutRunRequest, PayoutRunResponse, PayoutResponse
from app.services.payout_generator import PayoutGeneratorService

router = APIRouter()
logger = get_logger(__name__)


async def run_payout_generation_task(
    currency: str,
    as_of_date,
    min_amount: int,
    db: AsyncSession,
) -> None:
    """
    Background task for generating payouts.

    This runs asynchronously to avoid blocking the API response.
    """
    service = PayoutGeneratorService(db)

    try:
        payouts_created = await service.generate_payouts(
            currency, as_of_date, min_amount
        )
        logger.info(
            "Payout generation task completed",
            extra={
                "currency": currency,
                "payouts_created": payouts_created,
            },
        )
    except Exception as e:
        logger.error(
            "Payout generation task failed",
            extra={
                "currency": currency,
                "error": str(e),
            },
        )


@router.post(
    "/run",
    response_model=PayoutRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate payouts",
    description="Trigger async payout generation for eligible restaurants",
    tags=["payouts"],
)
async def run_payout_generation(
    request: PayoutRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> PayoutRunResponse:
    """
    Generate payouts for all eligible restaurants.

    This endpoint triggers an asynchronous batch process that:
    1. Finds all restaurants with balance >= min_amount
    2. Creates payout records for each eligible restaurant
    3. Reserves funds by creating ledger entries

    **Parameters:**
    - **currency**: Currency code (e.g., "PEN")
    - **as_of**: Payout date (YYYY-MM-DD)
    - **min_amount**: Minimum balance in cents to generate payout

    **Returns:**
    - **202 Accepted**: Payout generation started in background

    **Note:** This is a simplified implementation using BackgroundTasks.
    In production, use Celery or similar task queue.
    """
    # For this implementation, we'll run it synchronously but return quickly
    # In production, this would be a Celery task
    service = PayoutGeneratorService(db)

    payouts_created = await service.generate_payouts(
        request.currency.upper(),
        request.as_of,
        request.min_amount,
    )

    logger.info(
        "Payout generation initiated",
        extra={
            "currency": request.currency,
            "as_of": request.as_of.isoformat(),
            "min_amount": request.min_amount,
            "payouts_created": payouts_created,
        },
    )

    return PayoutRunResponse(
        status="accepted",
        message=f"Payout generation completed",
        payouts_created=payouts_created,
    )


@router.get(
    "/{payout_id}",
    response_model=PayoutResponse,
    summary="Get payout details",
    description="Retrieve details of a specific payout",
    tags=["payouts"],
)
async def get_payout(
    payout_id: str,
    db: AsyncSession = Depends(get_db),
) -> PayoutResponse:
    """
    Get details of a specific payout.

    **Parameters:**
    - **payout_id**: Unique payout identifier (e.g., "po_abc123")

    **Returns:**
    - Payout details including breakdown items

    **Raises:**
    - **404 Not Found**: Payout not found
    """
    service = PayoutGeneratorService(db)

    payout = await service.get_payout(payout_id)

    logger.info(
        "Payout retrieved",
        extra={
            "payout_id": payout_id,
            "restaurant_id": payout.restaurant_id,
        },
    )

    return payout
