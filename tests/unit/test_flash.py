"""Test: session flash helpers."""

from types import SimpleNamespace
from typing import Any, cast

import pytest
from app.auth import flash
from starlette.requests import Request


@pytest.mark.anyio
async def test_set_and_pop_flash_value(monkeypatch):
    store: dict[str, dict[str, Any]] = {}

    async def fake_load_session(session_id: str) -> dict[str, Any] | None:
        return store.get(session_id)

    async def fake_save_session(session_id: str, data: dict[str, Any]) -> None:
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
    store: dict[str, dict[str, Any]] = {}

    async def fake_load_session(session_id: str) -> dict[str, Any] | None:
        return store.get(session_id)

    async def fake_save_session(session_id: str, data: dict[str, Any]) -> None:
        store[session_id] = data

    monkeypatch.setattr(flash, "load_session", fake_load_session)
    monkeypatch.setattr(flash, "save_session", fake_save_session)

    request = cast(Request, SimpleNamespace(session={"sid": "abc"}))

    await flash.set_flash(request, "error", {"message": "nope"})
    assert store["abc"]["flash"]["error"]["message"] == "nope"

    value = await flash.pop_flash(request, "error")
    assert value == {"message": "nope"}
    assert "flash" not in store["abc"]
