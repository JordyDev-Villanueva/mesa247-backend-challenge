from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.logging import get_logger
from app.schemas.processor import ProcessorEventRequest, ProcessorEventResponse
from app.services.event_processor import EventProcessorService

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/events",
    response_model=ProcessorEventResponse,
    summary="Ingest payment processor events",
    description="Process events from payment processor with idempotency",
    tags=["processor"],
    responses={
        201: {"description": "Event processed for the first time"},
        200: {"description": "Event already processed (idempotency)"},
    },
)
async def ingest_processor_event(
    event: ProcessorEventRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> ProcessorEventResponse:
    """
    Ingest and process a payment processor event.

    This endpoint is idempotent - submitting the same event_id multiple times
    will only process it once.

    **Event Types:**
    - `charge_succeeded`: Money in from successful charge
    - `refund_succeeded`: Money out from refund
    - `payout_paid`: Mark payout as paid

    **Returns:**
    - **201 Created**: Event processed for the first time
    - **200 OK**: Event already processed (idempotency)
    """
    service = EventProcessorService(db)

    # Process the event
    is_new, message = await service.process_event(event)

    # Set appropriate status code
    if is_new:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    return ProcessorEventResponse(
        event_id=event.event_id,
        status="processed" if is_new else "already_processed",
        message=message,
    )
