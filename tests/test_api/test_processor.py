"""
Tests for processor event ingestion endpoint.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_charge_succeeded_event(client: AsyncClient):
    """Test processing a charge_succeeded event."""
    event_data = {
        "event_id": "evt_test_001",
        "event_type": "charge_succeeded",
        "occurred_at": "2025-12-30T10:00:00Z",
        "restaurant_id": "res_test_001",
        "currency": "PEN",
        "amount": 10000,
        "fee": 500,
        "metadata": {"test": "data"},
    }

    response = await client.post("/v1/processor/events", json=event_data)

    assert response.status_code == 201
    data = response.json()
    assert data["event_id"] == "evt_test_001"
    assert data["status"] == "processed"


@pytest.mark.asyncio
async def test_event_idempotency(client: AsyncClient):
    """Test that duplicate event_id returns 200 and doesn't process twice."""
    event_data = {
        "event_id": "evt_test_duplicate",
        "event_type": "charge_succeeded",
        "occurred_at": "2025-12-30T10:00:00Z",
        "restaurant_id": "res_test_001",
        "currency": "PEN",
        "amount": 10000,
        "fee": 500,
    }

    # First submission - should return 201
    response1 = await client.post("/v1/processor/events", json=event_data)
    assert response1.status_code == 201
    assert response1.json()["status"] == "processed"

    # Second submission - should return 200 (already processed)
    response2 = await client.post("/v1/processor/events", json=event_data)
    assert response2.status_code == 200
    assert response2.json()["status"] == "already_processed"


@pytest.mark.asyncio
async def test_refund_succeeded_event(client: AsyncClient):
    """Test processing a refund_succeeded event."""
    event_data = {
        "event_id": "evt_test_refund",
        "event_type": "refund_succeeded",
        "occurred_at": "2025-12-30T11:00:00Z",
        "restaurant_id": "res_test_001",
        "currency": "PEN",
        "amount": 5000,
        "fee": 0,
        "metadata": {"refund_reason": "test"},
    }

    response = await client.post("/v1/processor/events", json=event_data)

    assert response.status_code == 201
    data = response.json()
    assert data["event_id"] == "evt_test_refund"
    assert data["status"] == "processed"


@pytest.mark.asyncio
async def test_invalid_event_type(client: AsyncClient):
    """Test that invalid event type is rejected."""
    event_data = {
        "event_id": "evt_test_invalid",
        "event_type": "invalid_type",
        "occurred_at": "2025-12-30T10:00:00Z",
        "restaurant_id": "res_test_001",
        "currency": "PEN",
        "amount": 10000,
        "fee": 500,
    }

    response = await client.post("/v1/processor/events", json=event_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_invalid_amount(client: AsyncClient):
    """Test that negative or zero amounts are rejected."""
    event_data = {
        "event_id": "evt_test_negative",
        "event_type": "charge_succeeded",
        "occurred_at": "2025-12-30T10:00:00Z",
        "restaurant_id": "res_test_001",
        "currency": "PEN",
        "amount": -1000,  # Invalid: negative amount
        "fee": 500,
    }

    response = await client.post("/v1/processor/events", json=event_data)

    assert response.status_code == 422  # Validation error
