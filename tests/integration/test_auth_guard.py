"""Test: auth guard returns 401 for protected routes without session cookie."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_api_jobs_requires_auth():
    """GET /api/jobs without a session cookie should return 401."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/jobs")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_api_health_no_auth():
    """GET /api/health should not require auth."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
