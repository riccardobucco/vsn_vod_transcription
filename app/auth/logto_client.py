"""Logto Cloud OIDC client for authentication."""

import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TokenResponse:
    access_token: str
    id_token: str
    refresh_token: str | None
    expires_in: int
    token_type: str


@dataclass
class UserInfo:
    sub: str
    name: str | None = None
    email: str | None = None
    picture: str | None = None


# Cache OIDC discovery
_oidc_config: dict | None = None


async def _discover_oidc() -> dict:
    """Fetch OIDC discovery configuration."""
    global _oidc_config
    if _oidc_config is not None:
        return _oidc_config

    url = f"{settings.LOGTO_ENDPOINT}/oidc/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        _oidc_config = resp.json()
    return _oidc_config


def generate_state() -> str:
    """Generate a random state parameter for CSRF protection."""
    return secrets.token_urlsafe(32)


async def get_authorize_url(state: str) -> str:
    """Build the authorization URL for Logto redirect."""
    config = await _discover_oidc()
    authorization_endpoint = config["authorization_endpoint"]

    params = {
        "client_id": settings.LOGTO_APP_ID,
        "redirect_uri": settings.LOGTO_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
        "prompt": "login",
    }
    return f"{authorization_endpoint}?{urlencode(params)}"


async def exchange_code(code: str) -> TokenResponse:
    """Exchange authorization code for tokens."""
    config = await _discover_oidc()
    token_endpoint = config["token_endpoint"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            token_endpoint,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.LOGTO_APP_ID,
                "client_secret": settings.LOGTO_APP_SECRET,
                "redirect_uri": settings.LOGTO_REDIRECT_URI,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return TokenResponse(
        access_token=data["access_token"],
        id_token=data.get("id_token", ""),
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in", 3600),
        token_type=data.get("token_type", "Bearer"),
    )


async def get_userinfo(access_token: str) -> UserInfo:
    """Fetch user info from Logto."""
    config = await _discover_oidc()
    userinfo_endpoint = config["userinfo_endpoint"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        data = resp.json()

    return UserInfo(
        sub=data["sub"],
        name=data.get("name") or data.get("username"),
        email=data.get("email"),
        picture=data.get("picture"),
    )


async def get_end_session_url(id_token: str | None = None) -> str:
    """Build the end-session (logout) URL."""
    config = await _discover_oidc()
    end_session_endpoint = config.get("end_session_endpoint", f"{settings.LOGTO_ENDPOINT}/oidc/session/end")

    params: dict[str, str] = {}
    if id_token:
        params["id_token_hint"] = id_token
    if settings.LOGTO_POST_LOGOUT_REDIRECT_URI:
        params["post_logout_redirect_uri"] = settings.LOGTO_POST_LOGOUT_REDIRECT_URI

    if params:
        return f"{end_session_endpoint}?{urlencode(params)}"
    return end_session_endpoint
