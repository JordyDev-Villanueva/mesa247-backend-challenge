from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import AppException

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    logger.info("Starting application", extra={"app_name": settings.APP_NAME})
    yield
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Payment processing and payout microservice for restaurant operations",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "processor",
            "description": "Payment processor event ingestion",
        },
        {
            "name": "restaurants",
            "description": "Restaurant balance queries",
        },
        {
            "name": "payouts",
            "description": "Payout generation and retrieval",
        },
        {
            "name": "health",
            "description": "Health check endpoints",
        },
    ],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions."""
    logger.error(
        "Application error",
        extra={
            "error_code": exc.code,
            "error_message": exc.message,
            "error_details": exc.details,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.get("/", tags=["health"])
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint for monitoring.
    Checks basic application health.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Import and include routers
from app.api.v1.router import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
