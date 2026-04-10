import pytest


API_KEY = "supersecretkey"


@pytest.mark.asyncio
async def test_create_payment(client):
    response = await client.post(
        "/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": "test-1",
        },
        json={
            "amount": "100.00",
            "currency": "USD",
            "description": "test payment",
            "metadata": {"a": 1},
            "webhook_url": "http://example.com/webhook",
        },
    )

    assert response.status_code == 202
    data = response.json()

    assert "payment_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_payment(client):
    create_resp = await client.post(
        "/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": "test-2",
        },
        json={
            "amount": "200.00",
            "currency": "EUR",
            "description": "test payment",
            "metadata": {"b": 2},
            "webhook_url": "http://example.com/webhook",
        },
    )

    payment_id = create_resp.json()["payment_id"]

    get_resp = await client.get(
        f"/api/v1/payments/{payment_id}",
        headers={"X-API-Key": API_KEY},
    )

    assert get_resp.status_code == 200
    data = get_resp.json()

    assert data["id"] == payment_id
    assert data["metadata"]["b"] == 2


@pytest.mark.asyncio
async def test_idempotency(client):
    payload = {
        "amount": "300.00",
        "currency": "USD",
        "description": "idempotency test",
        "metadata": {"c": 3},
        "webhook_url": "http://example.com/webhook",
    }

    headers = {
        "X-API-Key": API_KEY,
        "Idempotency-Key": "same-key",
    }

    resp1 = await client.post("/api/v1/payments", headers=headers, json=payload)
    resp2 = await client.post("/api/v1/payments", headers=headers, json=payload)

    assert resp1.status_code == 202
    assert resp2.status_code == 202

    assert resp1.json()["payment_id"] == resp2.json()["payment_id"]


@pytest.mark.asyncio
async def test_api_key_required(client):
    response = await client.post(
        "/api/v1/payments",
        headers={"Idempotency-Key": "no-key"},
        json={
            "amount": "100.00",
            "currency": "USD",
            "description": "no key",
            "metadata": {},
            "webhook_url": "http://example.com",
        },
    )

    assert response.status_code == 422 or response.status_code == 401