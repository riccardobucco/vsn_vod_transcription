"""Integration tests: friendly submission error pages."""

import uuid
from types import SimpleNamespace

import pytest
from app.db.session import get_db
from app.services import submission_service
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _install_common_mocks(monkeypatch):
    from app.routes import submissions

    async def fake_get_session_data(request):
        return {"sub": "user", "name": "Test User"}

    async def fake_current_user(session_data, db):
        return SimpleNamespace(id=uuid.uuid4(), display_name="Test User")

    monkeypatch.setattr(submissions, "get_session_data", fake_get_session_data)
    monkeypatch.setattr(submissions, "current_user", fake_current_user)


def _override_db(app):
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db


@pytest.mark.anyio
async def test_submit_upload_shows_error_page(monkeypatch):
    from app.main import app
    from app.routes import submissions

    _install_common_mocks(monkeypatch)
    _override_db(app)

    async def fake_create_upload_job(file, user, db):
        raise submission_service.SubmissionError("unsupported_format", "Unsupported format")

    monkeypatch.setattr(submissions.submission_service, "create_upload_job", fake_create_upload_job)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/submit/upload",
            files={"file": ("bad.txt", b"oops", "text/plain")},
        )
        assert response.status_code == 400
        assert "Submission failed" in response.text
        assert "Details" in response.text
        assert "Back to dashboard" in response.text

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_submit_url_shows_error_page(monkeypatch):
    from app.main import app
    from app.routes import submissions

    _install_common_mocks(monkeypatch)
    _override_db(app)

    async def fake_create_url_job(url, label, user, db):
        raise submission_service.SubmissionError("invalid_url", "Only http and https URLs are supported")

    monkeypatch.setattr(submissions.submission_service, "create_url_job", fake_create_url_job)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/submit/url", data={"url": "ftp://bad"})
        assert response.status_code == 400
        assert "Submission failed" in response.text
        assert "Details" in response.text
        assert "Back to dashboard" in response.text

    app.dependency_overrides.clear()
