"""
Pytest configuration and fixtures for Mesa 24/7 Backend Challenge tests.
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db


# Test database URL (uses in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Register custom functions for SQLite to handle UUID
@event.listens_for(test_engine.sync_engine, "connect")
def register_custom_functions(dbapi_conn, connection_record):
    """Register custom SQLite functions for UUID handling."""
    import uuid

    # Register uuid4 function
    dbapi_conn.create_function("uuid4", 0, lambda: str(uuid.uuid4()))


# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test.

    Yields:
        AsyncSession: Test database session
    """
    # Create tables
    async with test_engine.begin() as conn:
        # Monkey patch UUID to String for SQLite
        from sqlalchemy.dialects import sqlite
        from sqlalchemy import String
        from sqlalchemy.types import UUID

        # Make UUID render as String(36) in SQLite
        @event.listens_for(Base.metadata, "before_create")
        def _adapt_uuid_type(target, connection, **kw):
            for table in Base.metadata.sorted_tables:
                for column in table.columns:
                    if isinstance(column.type, UUID):
                        column.type = String(36)

        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.

    Args:
        test_db: Test database session

    Yields:
        AsyncClient: HTTP client for making requests
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
