from fastapi import APIRouter

from app.api.v1 import processor, restaurants, payouts

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(
    processor.router,
    prefix="/processor",
    tags=["processor"],
)

api_router.include_router(
    restaurants.router,
    prefix="/restaurants",
    tags=["restaurants"],
)

api_router.include_router(
    payouts.router,
    prefix="/payouts",
    tags=["payouts"],
)
