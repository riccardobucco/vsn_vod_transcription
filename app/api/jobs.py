"""Jobs API endpoints."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user, require_session
from app.db.models import JobSourceType, JobStatus, TranscriptionJob, User
from app.db.session import get_db
from app.logging import get_logger
from app.metrics import inc
from app.services import jobs_service

logger = get_logger(__name__)

router = APIRouter(tags=["Jobs"])

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


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
        return await _create_upload_job(file, user, db)
    elif "application/json" in content_type:
        body = await request.json()
        url = body.get("url")
        label = body.get("label")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        return await _create_url_job(url, label, user, db)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported content type. Use multipart/form-data or application/json.",
        )


async def _create_upload_job(file: UploadFile, user: User, db: AsyncSession) -> JSONResponse:
    """Handle file upload job creation."""
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    job_id = uuid.uuid4()
    object_key = f"uploads/{job_id}/{filename}"

    # Read file and upload to MinIO
    file_data = await file.read()
    if len(file_data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 2 GB)")

    from app.services.storage_minio import put_object

    put_object(object_key, file_data, content_type=file.content_type or "application/octet-stream")

    # Create job
    job = TranscriptionJob(
        id=job_id,
        user_id=user.id,
        source_type=JobSourceType.upload,
        source_label=filename,
        original_object_key=object_key,
        input_format=ext.lstrip("."),
        status=JobStatus.queued,
    )
    db.add(job)
    await db.commit()

    # Dispatch Celery task
    from worker.tasks import process_transcription_job

    process_transcription_job.delay(str(job_id))

    inc("jobs_created")
    logger.info("Created upload job %s for file %s", job_id, filename)

    return JSONResponse(status_code=201, content=_job_to_dict(job))


async def _create_url_job(url: str, label: str | None, user: User, db: AsyncSession) -> JSONResponse:
    """Handle URL-based job creation."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http and https URLs are supported")

    if not label:
        # Derive label from URL
        path = parsed.path.rstrip("/")
        label = os.path.basename(path) if path else parsed.netloc

    job_id = uuid.uuid4()
    job = TranscriptionJob(
        id=job_id,
        user_id=user.id,
        source_type=JobSourceType.url,
        source_label=label,
        source_url=url,
        status=JobStatus.queued,
    )
    db.add(job)
    await db.commit()

    # Dispatch Celery task
    from worker.tasks import process_transcription_job

    process_transcription_job.delay(str(job_id))

    inc("jobs_created")
    logger.info("Created URL job %s for %s", job_id, parsed.netloc)

    return JSONResponse(status_code=201, content=_job_to_dict(job))


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
