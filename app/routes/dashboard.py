"""Dashboard SSR route."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user, get_session_data
from app.auth.flash import CONFIRMATION_FLASH_KEY, pop_flash
from app.db.session import get_db
from app.services import jobs_service

router = APIRouter()


@router.get("/")
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Render the dashboard. Redirects to /login if unauthenticated."""
    session_data = await get_session_data(request)
    if session_data is None:
        return RedirectResponse(url="/login", status_code=307)

    confirmation = await pop_flash(request, CONFIRMATION_FLASH_KEY)

    # Get or create user
    user = await current_user(session_data, db)
    jobs = await jobs_service.list_jobs_for_user(db, user.id)

    from app.main import templates

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_display_name": user.display_name or "Reviewer",
            "jobs": jobs,
            "confirmation": confirmation,
        },
    )
