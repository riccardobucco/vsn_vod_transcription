"""Auth dependencies for route protection."""

import uuid
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session_store import load_session
from app.db.models import User
from app.db.session import get_db
from app.logging import get_logger

logger = get_logger(__name__)


async def get_session_data(request: Request) -> dict | None:
    """Extract session data from the server-side session store."""
    session_id = request.session.get("sid")
    if not session_id:
        return None
    return await load_session(session_id)


async def require_session(request: Request) -> dict:
    """Require an authenticated session. Raises 401 for API, redirects for SSR."""
    session_data = await get_session_data(request)
    if session_data is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session_data


async def require_session_or_redirect(request: Request) -> dict:
    """Require an authenticated session. Redirects to /login for SSR routes."""
    session_data = await get_session_data(request)
    if session_data is None:
        raise HTTPException(
            status_code=307,
            detail="Not authenticated",
            headers={"Location": "/login"},
        )
    return session_data


async def current_user(
    session_data: dict = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get or create the User row for the authenticated subject."""
    sub = session_data["sub"]
    result = await db.execute(select(User).where(User.logto_sub == sub))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            logto_sub=sub,
            display_name=session_data.get("name"),
            last_sign_in_at=datetime.now(UTC),
        )
        db.add(user)
        await db.flush()
        logger.info("Created new user: sub=%s", sub)
    else:
        user.last_sign_in_at = datetime.now(UTC)
        if session_data.get("name") and user.display_name != session_data["name"]:
            user.display_name = session_data["name"]

    return user
