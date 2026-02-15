"""Jobs API endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user, require_session
from app.db.models import JobStatus, TranscriptionJob, User
from app.db.session import get_db
from app.services import jobs_service, submission_service

router = APIRouter(tags=["Jobs"])

ALLOWED_EXTENSIONS = submission_service.ALLOWED_EXTENSIONS
MAX_UPLOAD_SIZE = submission_service.MAX_UPLOAD_SIZE


def _job_to_dict(job: TranscriptionJob, overall_confidence: float | None = None) -> dict:
    """Serialize a TranscriptionJob to API response dict."""
    d = {
        "id": str(job.id),
        "source_type": job.source_type.value,
        "source_label": job.source_label,
        "source_url": job.source_url,
        "duration_seconds": job.duration_seconds,
        "status": job.status.value,
        "failure_message": job.failure_message,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "overall_confidence": overall_confidence,
    }
    return d


@router.get("/jobs", dependencies=[Depends(require_session)])
async def list_jobs(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all transcription jobs for the authenticated user."""
    jobs = await jobs_service.list_jobs_for_user(db, user.id)

    job_dicts = []
    for job in jobs:
        # Compute overall confidence for completed jobs
        overall_conf = None
        if job.status == JobStatus.completed:
            segments = await jobs_service.get_segments_for_job(db, job.id)
            overall_conf = jobs_service.compute_overall_confidence(segments)
        job_dicts.append(_job_to_dict(job, overall_conf))

    return {"jobs": job_dicts}


@router.get("/jobs/{job_id}", dependencies=[Depends(require_session)])
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single job by ID."""
    job = await jobs_service.get_job_by_id(db, job_id, user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    overall_conf = None
    if job.status == JobStatus.completed:
        segments = await jobs_service.get_segments_for_job(db, job.id)
        overall_conf = jobs_service.compute_overall_confidence(segments)

    return _job_to_dict(job, overall_conf)


@router.post("/jobs", dependencies=[Depends(require_session)])
async def create_job(
    request: Request,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
    file: UploadFile | None = File(None),
):
    """Create a transcription job from file upload or URL."""
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type and file is not None:
        try:
            job = await submission_service.create_upload_job(file, user, db)
        except submission_service.SubmissionError as exc:
            raise HTTPException(status_code=400, detail=exc.detail) from exc
        return JSONResponse(status_code=201, content=_job_to_dict(job))
    elif "application/json" in content_type:
        body = await request.json()
        url = body.get("url")
        label = body.get("label")
        try:
            job = await submission_service.create_url_job(url, label, user, db)
        except submission_service.SubmissionError as exc:
            raise HTTPException(status_code=400, detail=exc.detail) from exc
        return JSONResponse(status_code=201, content=_job_to_dict(job))
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported content type. Use multipart/form-data or application/json.",
        )


@router.get("/jobs/{job_id}/transcript", dependencies=[Depends(require_session)])
async def get_transcript(
    job_id: uuid.UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transcript segments for a completed job."""
    job = await jobs_service.get_job_by_id(db, job_id, user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    segments = await jobs_service.get_segments_for_job(db, job.id)
    return {
        "job_id": str(job.id),
        "segments": [
            {
                "segment_index": s.segment_index,
                "start_ms": s.start_ms,
                "end_ms": s.end_ms,
                "text": s.text,
                "confidence": s.confidence,
            }
            for s in segments
        ],
    }
