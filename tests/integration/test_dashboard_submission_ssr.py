"""Integration tests: SSR submission PRG confirmation."""

import uuid
from types import SimpleNamespace

import pytest
from app.db.models import JobStatus
from app.db.session import get_db
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _install_common_mocks(monkeypatch, stored_flash):
    from app.routes import dashboard, submissions

    async def fake_get_session_data(request):
        return {"sub": "user", "name": "Test User"}

    async def fake_current_user(session_data, db):
        return SimpleNamespace(id=uuid.uuid4(), display_name="Test User")

    async def fake_list_jobs(db, user_id):
        return []

    async def fake_set_flash(request, key, value):
        stored_flash[key] = value

    async def fake_pop_flash(request, key):
        return stored_flash.pop(key, None)

    monkeypatch.setattr(submissions, "get_session_data", fake_get_session_data)
    monkeypatch.setattr(dashboard, "get_session_data", fake_get_session_data)
    monkeypatch.setattr(submissions, "current_user", fake_current_user)
    monkeypatch.setattr(dashboard, "current_user", fake_current_user)
    monkeypatch.setattr(dashboard.jobs_service, "list_jobs_for_user", fake_list_jobs)
    monkeypatch.setattr(submissions, "set_flash", fake_set_flash)
    monkeypatch.setattr(dashboard, "pop_flash", fake_pop_flash)


def _override_db(app):
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db


@pytest.mark.anyio
async def test_submit_url_prg_confirmation(monkeypatch):
    from app.main import app
    from app.routes import submissions

    stored_flash = {}
    _install_common_mocks(monkeypatch, stored_flash)
    _override_db(app)

    job_id = uuid.uuid4()

    async def fake_create_url_job(url, label, user, db):
        return SimpleNamespace(id=job_id, source_label="example.mp4", status=JobStatus.queued)

    monkeypatch.setattr(submissions.submission_service, "create_url_job", fake_create_url_job)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/submit/url", data={"url": "https://example.com/video.mp4"})
        assert response.status_code == 303
        assert response.headers.get("location") == "/"

        dashboard = await client.get("/")
        assert dashboard.status_code == 200
        assert "Submission accepted" in dashboard.text
        assert "example.mp4" in dashboard.text
        assert f"/jobs/{job_id}" in dashboard.text

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_submit_upload_prg_confirmation(monkeypatch):
    from app.main import app
    from app.routes import submissions

    stored_flash = {}
    _install_common_mocks(monkeypatch, stored_flash)
    _override_db(app)

    job_id = uuid.uuid4()

    async def fake_create_upload_job(file, user, db):
        return SimpleNamespace(id=job_id, source_label="upload.mov", status=JobStatus.queued)

    monkeypatch.setattr(submissions.submission_service, "create_upload_job", fake_create_upload_job)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/submit/upload",
            files={"file": ("upload.mov", b"data", "video/quicktime")},
        )
        assert response.status_code == 303
        assert response.headers.get("location") == "/"

        dashboard = await client.get("/")
        assert dashboard.status_code == 200
        assert "Submission accepted" in dashboard.text
        assert "upload.mov" in dashboard.text
        assert f"/jobs/{job_id}" in dashboard.text

    app.dependency_overrides.clear()
