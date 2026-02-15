"""Server-side session store using Redis."""

import json
from typing import Any

import redis.asyncio as aioredis

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

SESSION_PREFIX = "session:"
SESSION_TTL = 86400  # 24 hours

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def save_session(session_id: str, data: dict[str, Any]) -> None:
    """Persist session data to Redis."""
    r = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    await r.set(key, json.dumps(data), ex=SESSION_TTL)


async def load_session(session_id: str) -> dict[str, Any] | None:
    """Load session data from Redis."""
    r = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    raw = await r.get(key)
    if raw is None:
        return None
    return dict(json.loads(raw))


async def delete_session(session_id: str) -> None:
    """Delete a session from Redis."""
    r = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    await r.delete(key)
