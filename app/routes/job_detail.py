"""Job detail SSR route."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user, get_session_data
from app.db.session import get_db
from app.services import jobs_service

router = APIRouter()


@router.get("/jobs/{job_id}")
async def job_detail(
    job_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Render the job detail page."""
    session_data = await get_session_data(request)
    if session_data is None:
        return RedirectResponse(url="/login", status_code=307)

    user = await current_user(session_data, db)
    job = await jobs_service.get_job_by_id(db, job_id, user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    segments = await jobs_service.get_segments_for_job(db, job.id)
    overall_confidence = jobs_service.compute_overall_confidence(segments)

    from app.main import templates

    return templates.TemplateResponse(
        "job_detail.html",
        {
            "request": request,
            "job": job,
            "segments": segments,
            "overall_confidence": overall_confidence,
        },
    )
