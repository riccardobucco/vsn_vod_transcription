"""SSR submission routes for dashboard UX."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user, get_session_data
from app.auth.flash import CONFIRMATION_FLASH_KEY, set_flash
from app.db.session import get_db
from app.logging import get_logger
from app.services import submission_errors, submission_service

logger = get_logger(__name__)

router = APIRouter()


@router.post("/submit/upload")
async def submit_upload(
    request: Request,
    db: AsyncSession = Depends(get_db),
    file: UploadFile | None = File(None),
):
    """Handle upload submission for SSR dashboard UX."""
    session_data = await get_session_data(request)
    if session_data is None:
        return RedirectResponse(url="/login", status_code=307)

    user = await current_user(session_data, db)

    try:
        if file is None:
            raise submission_service.SubmissionError("missing_file", "File is required")
        job = await submission_service.create_upload_job(file, user, db)
    except submission_service.SubmissionError as exc:
        error_view = submission_errors.build_submission_error(exc)
        from app.main import templates

        return templates.TemplateResponse(
            "submission_error.html",
            {
                "request": request,
                "message": error_view["message"],
                "details": error_view["details"],
            },
            status_code=400,
        )
    except Exception:
        logger.exception("Unexpected error during upload submission")
        error_view = submission_errors.build_unexpected_error("Upload failed. Please try again.")
        from app.main import templates

        return templates.TemplateResponse(
            "submission_error.html",
            {
                "request": request,
                "message": error_view["message"],
                "details": error_view["details"],
            },
            status_code=400,
        )

    await set_flash(
        request,
        CONFIRMATION_FLASH_KEY,
        {
            "job_id": str(job.id),
            "label": job.source_label,
            "status": job.status.value,
        },
    )

    return RedirectResponse(url="/", status_code=303)


@router.post("/submit/url")
async def submit_url(
    request: Request,
    url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Handle URL submission for SSR dashboard UX."""
    session_data = await get_session_data(request)
    if session_data is None:
        return RedirectResponse(url="/login", status_code=307)

    user = await current_user(session_data, db)

    try:
        job = await submission_service.create_url_job(url, None, user, db)
    except submission_service.SubmissionError as exc:
        error_view = submission_errors.build_submission_error(exc)
        from app.main import templates

        return templates.TemplateResponse(
            "submission_error.html",
            {
                "request": request,
                "message": error_view["message"],
                "details": error_view["details"],
            },
            status_code=400,
        )
    except Exception:
        logger.exception("Unexpected error during URL submission")
        error_view = submission_errors.build_unexpected_error("Submission failed. Please try again.")
        from app.main import templates

        return templates.TemplateResponse(
            "submission_error.html",
            {
                "request": request,
                "message": error_view["message"],
                "details": error_view["details"],
            },
            status_code=400,
        )

    await set_flash(
        request,
        CONFIRMATION_FLASH_KEY,
        {
            "job_id": str(job.id),
            "label": job.source_label,
            "status": job.status.value,
        },
    )

    return RedirectResponse(url="/", status_code=303)
