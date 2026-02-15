"""Shared job submission helpers for API + SSR flows."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobSourceType, JobStatus, TranscriptionJob, User
from app.logging import get_logger
from app.metrics import inc

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


class SubmissionError(Exception):
    """Validation error for submission flows."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _derive_label_from_url(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    return os.path.basename(path) if path else parsed.netloc


async def create_upload_job(file: UploadFile, user: User, db: AsyncSession) -> TranscriptionJob:
    """Handle file upload job creation."""
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise SubmissionError("unsupported_format", f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    job_id = uuid.uuid4()
    object_key = f"uploads/{job_id}/{filename}"

    file_data = await file.read()
    if len(file_data) > MAX_UPLOAD_SIZE:
        raise SubmissionError("file_too_large", "File too large (max 2 GB)")

    from app.services.storage_minio import put_object

    put_object(object_key, file_data, content_type=file.content_type or "application/octet-stream")

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

    from worker.tasks import process_transcription_job

    process_transcription_job.delay(str(job_id))

    inc("jobs_created")
    logger.info("Created upload job %s for file %s", job_id, filename)

    return job


async def create_url_job(url: str | None, label: str | None, user: User, db: AsyncSession) -> TranscriptionJob:
    """Handle URL-based job creation."""
    if not url:
        raise SubmissionError("missing_url", "URL is required")

    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SubmissionError("invalid_url", "Only http and https URLs are supported")

    if not label:
        label = _derive_label_from_url(url)

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

    from worker.tasks import process_transcription_job

    process_transcription_job.delay(str(job_id))

    inc("jobs_created")
    logger.info("Created URL job %s for %s", job_id, parsed.netloc)

    return job
