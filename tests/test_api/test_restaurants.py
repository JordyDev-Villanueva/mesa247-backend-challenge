"""
Tests for restaurant balance endpoint.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_balance_after_charge(client: AsyncClient):
    """Test getting balance after processing a charge event."""
    # First, create a charge event
    event_data = {
        "event_id": "evt_balance_test_001",
        "event_type": "charge_succeeded",
        "occurred_at": "2025-12-30T10:00:00Z",
        "restaurant_id": "res_balance_001",
        "currency": "PEN",
        "amount": 10000,
        "fee": 500,
    }
    await client.post("/v1/processor/events", json=event_data)

    # Get balance
    response = await client.get("/v1/restaurants/res_balance_001/balance?currency=PEN")

    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == "res_balance_001"
    assert data["currency"] == "PEN"
    assert data["available"] == 9500  # 10000 - 500 (fee)
    assert data["pending"] == 0


@pytest.mark.asyncio
async def test_get_balance_with_refund(client: AsyncClient):
    """Test balance calculation with charge and refund."""
    restaurant_id = "res_balance_002"

    # Create charge
    charge_event = {
        "event_id": "evt_balance_charge",
        "event_type": "charge_succeeded",
        "occurred_at": "2025-12-30T10:00:00Z",
        "restaurant_id": restaurant_id,
        "currency": "PEN",
        "amount": 20000,
        "fee": 1000,
    }
    await client.post("/v1/processor/events", json=charge_event)

    # Create refund
    refund_event = {
        "event_id": "evt_balance_refund",
        "event_type": "refund_succeeded",
        "occurred_at": "2025-12-30T11:00:00Z",
        "restaurant_id": restaurant_id,
        "currency": "PEN",
        "amount": 5000,
        "fee": 0,
    }
    await client.post("/v1/processor/events", json=refund_event)

    # Get balance
    response = await client.get(f"/v1/restaurants/{restaurant_id}/balance?currency=PEN")

    assert response.status_code == 200
    data = response.json()
    # 20000 (charge) - 1000 (fee) - 5000 (refund) = 14000
    assert data["available"] == 14000


@pytest.mark.asyncio
async def test_get_balance_restaurant_not_found(client: AsyncClient):
    """Test getting balance for non-existent restaurant."""
    response = await client.get("/v1/restaurants/res_nonexistent/balance?currency=PEN")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "RESTAURANT_NOT_FOUND"
