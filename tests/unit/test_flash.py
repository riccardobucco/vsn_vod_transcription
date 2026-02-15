"""Test: session flash helpers."""

from types import SimpleNamespace

import pytest
from app.auth import flash


@pytest.mark.anyio
async def test_set_and_pop_flash_value(monkeypatch):
    store = {}

    async def fake_load_session(session_id: str):
        return store.get(session_id)

    async def fake_save_session(session_id: str, data: dict):
        store[session_id] = data

    monkeypatch.setattr(flash, "load_session", fake_load_session)
    monkeypatch.setattr(flash, "save_session", fake_save_session)

    await flash.set_flash_value("sid", "confirmation", {"job_id": "123"})
    assert store["sid"]["flash"]["confirmation"]["job_id"] == "123"

    value = await flash.pop_flash_value("sid", "confirmation")
    assert value == {"job_id": "123"}
    assert "flash" not in store["sid"]


@pytest.mark.anyio
async def test_set_and_pop_flash_with_request(monkeypatch):
    store = {}

    async def fake_load_session(session_id: str):
        return store.get(session_id)

    async def fake_save_session(session_id: str, data: dict):
        store[session_id] = data

    monkeypatch.setattr(flash, "load_session", fake_load_session)
    monkeypatch.setattr(flash, "save_session", fake_save_session)

    request = SimpleNamespace(session={"sid": "abc"})

    await flash.set_flash(request, "error", {"message": "nope"})
    assert store["abc"]["flash"]["error"]["message"] == "nope"

    value = await flash.pop_flash(request, "error")
    assert value == {"message": "nope"}
    assert "flash" not in store["abc"]
