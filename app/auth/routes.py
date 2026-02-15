"""Auth routes: /login, /auth/callback, /logout."""

import secrets

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.auth import logto_client, session_store
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Auth"])


@router.get("/login")
async def login(request: Request):
    """Initiate Logto OIDC login flow."""
    state = logto_client.generate_state()
    # Store state in Starlette session for CSRF verification
    request.session["oauth_state"] = state
    authorize_url = await logto_client.get_authorize_url(state)
    return RedirectResponse(url=authorize_url)


@router.get("/auth/callback")
async def auth_callback(request: Request, code: str | None = None, state: str | None = None):
    """Handle Logto OIDC callback."""
    stored_state = request.session.get("oauth_state")
    if not state or state != stored_state:
        logger.warning("OAuth state mismatch")
        return RedirectResponse(url="/login")

    if not code:
        logger.warning("No authorization code in callback")
        return RedirectResponse(url="/login")

    try:
        token_response = await logto_client.exchange_code(code)
        userinfo = await logto_client.get_userinfo(token_response.access_token)
    except Exception:
        logger.exception("Failed to exchange code or fetch userinfo")
        return RedirectResponse(url="/login")

    # Create server-side session
    session_id = secrets.token_urlsafe(32)
    await session_store.save_session(
        session_id,
        {
            "sub": userinfo.sub,
            "name": userinfo.name,
            "email": userinfo.email,
            "access_token": token_response.access_token,
            "id_token": token_response.id_token,
        },
    )

    # Set session id in Starlette session cookie
    request.session["sid"] = session_id
    request.session.pop("oauth_state", None)

    logger.info("User authenticated: sub=%s", userinfo.sub)
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request):
    """Log out and redirect to Logto end-session."""
    session_id = request.session.get("sid")
    id_token = None

    if session_id:
        session_data = await session_store.load_session(session_id)
        if session_data:
            id_token = session_data.get("id_token")
        await session_store.delete_session(session_id)

    request.session.clear()

    end_session_url = await logto_client.get_end_session_url(id_token)
    return RedirectResponse(url=end_session_url)
