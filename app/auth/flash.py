"""Session flash helpers for SSR UX."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from app.auth.session_store import load_session, save_session

FLASH_BUCKET_KEY = "flash"
CONFIRMATION_FLASH_KEY = "confirmation"
ERROR_FLASH_KEY = "error"


async def set_flash_value(session_id: str, key: str, value: dict[str, Any]) -> None:
    """Persist a flash value for the given session id."""
    session_data = await load_session(session_id) or {}
    flash = session_data.get(FLASH_BUCKET_KEY)
    if not isinstance(flash, dict):
        flash = {}
    flash[key] = value
    session_data[FLASH_BUCKET_KEY] = flash
    await save_session(session_id, session_data)


async def pop_flash_value(session_id: str, key: str) -> dict[str, Any] | None:
    """Pop and return a flash value for the given session id."""
    session_data = await load_session(session_id)
    if not session_data:
        return None
    flash = session_data.get(FLASH_BUCKET_KEY)
    if not isinstance(flash, dict):
        return None
    value = flash.pop(key, None)
    if value is None:
        return None
    if not isinstance(value, dict):
        return None
    if flash:
        session_data[FLASH_BUCKET_KEY] = flash
    else:
        session_data.pop(FLASH_BUCKET_KEY, None)
    await save_session(session_id, session_data)
    return value


async def set_flash(request: Request, key: str, value: dict[str, Any]) -> None:
    """Persist a flash value for the current request's session."""
    session_id = request.session.get("sid")
    if not session_id:
        return
    await set_flash_value(session_id, key, value)


async def pop_flash(request: Request, key: str) -> dict[str, Any] | None:
    """Pop and return a flash value for the current request's session."""
    session_id = request.session.get("sid")
    if not session_id:
        return None
    return await pop_flash_value(session_id, key)
