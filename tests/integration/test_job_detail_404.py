"""Integration tests: job not found HTML page."""

import uuid
from types import SimpleNamespace

import pytest
from app.db.session import get_db
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _install_common_mocks(monkeypatch):
    from app.routes import job_detail

    async def fake_get_session_data(request):
        return {"sub": "user", "name": "Test User"}

    async def fake_current_user(session_data, db):
        return SimpleNamespace(id=uuid.uuid4(), display_name="Test User")

    async def fake_get_job_by_id(db, job_id, user_id):
        return None

    monkeypatch.setattr(job_detail, "get_session_data", fake_get_session_data)
    monkeypatch.setattr(job_detail, "current_user", fake_current_user)
    monkeypatch.setattr(job_detail.jobs_service, "get_job_by_id", fake_get_job_by_id)


def _override_db(app):
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db


@pytest.mark.anyio
async def test_job_detail_malformed_id_shows_404(monkeypatch):
    from app.main import app

    _install_common_mocks(monkeypatch)
    _override_db(app)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/jobs/not-a-uuid")
        assert response.status_code == 404
        assert "Job not found" in response.text
        assert "Back to dashboard" in response.text

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_job_detail_missing_id_shows_404(monkeypatch):
    from app.main import app

    _install_common_mocks(monkeypatch)
    _override_db(app)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/jobs/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert "Job not found" in response.text
        assert "Back to dashboard" in response.text

    app.dependency_overrides.clear()
