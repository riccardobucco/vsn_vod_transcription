"""Celery tasks for VOD transcription processing."""

import os
import tempfile
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import settings
from app.db.models import (
    JobSourceType,
    JobStatus,
    TranscriptionJob,
    TranscriptSegment,
)
from app.logging import get_logger, job_id_var
from app.metrics import Timer, inc
from app.services.failures import get_failure_message
from celery import shared_task
from sqlalchemy import create_engine, select
from worker.celery_app import celery_app as _celery_app  # noqa: F401 — ensure app is current
from sqlalchemy.orm import Session, sessionmaker

logger = get_logger(__name__)

# Sync engine for Celery tasks (Celery doesn't support async easily)
_sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2").replace("postgresql+psycopg2", "postgresql")
_engine = create_engine(_sync_url, pool_pre_ping=True)
_SessionFactory = sessionmaker(bind=_engine)


def _get_sync_session() -> Session:
    return _SessionFactory()


@shared_task(bind=True, max_retries=0, acks_late=True)
def process_transcription_job(self, job_id_str: str) -> None:
    """Main transcription pipeline: download/fetch → probe → transcode → transcribe → persist."""
    job_id = uuid.UUID(job_id_str)
    token = job_id_var.set(str(job_id))

    try:
        _process_job(job_id)
    except Exception:
        logger.exception("Unhandled error processing job %s", job_id)
        _fail_job(job_id, "unknown", get_failure_message("unknown"))
        inc("jobs_failed")
    finally:
        job_id_var.reset(token)


def _process_job(job_id: uuid.UUID) -> None:
    with _get_sync_session() as db:
        job = db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id)).scalar_one_or_none()
        if job is None:
            logger.warning("Job %s not found", job_id)
            return

        # Mark as processing
        job.status = JobStatus.processing
        job.started_at = datetime.now(UTC)
        db.commit()

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "input_video")
        audio_path = os.path.join(tmpdir, "audio.mp3")

        # Step 1: Get the video file
        with _get_sync_session() as db:
            job = db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id)).scalar_one()

        try:
            if job.source_type == JobSourceType.upload:
                _download_from_minio(job.original_object_key, video_path)
            elif job.source_type == JobSourceType.url:
                _download_from_url(job.source_url, video_path, job_id)
        except ValueError as e:
            error_str = str(e)
            if "private" in error_str.lower() or "reserved" in error_str.lower():
                code = "ssrf_blocked"
            elif "size" in error_str.lower():
                code = "download_size_exceeded"
            elif "timeout" in error_str.lower():
                code = "download_timeout"
            else:
                code = "download_failed"
            _fail_job(job_id, code, get_failure_message(code))
            inc("jobs_failed")
            return
        except Exception:
            logger.exception("Download failed for job %s", job_id)
            _fail_job(job_id, "download_failed", get_failure_message("download_failed"))
            inc("jobs_failed")
            return

        # Step 2: Probe media
        try:
            from worker.media.ffprobe import get_duration_seconds
            from worker.media.ffprobe import has_audio as check_audio

            duration = get_duration_seconds(video_path)
            audio_present = check_audio(video_path)
        except Exception:
            logger.exception("Probe failed for job %s", job_id)
            _fail_job(job_id, "probe_failed", get_failure_message("probe_failed"))
            inc("jobs_failed")
            return

        if not audio_present:
            _fail_job(job_id, "no_audio_track", get_failure_message("no_audio_track"))
            inc("jobs_failed")
            return

        if duration is not None and duration > 1800:
            _fail_job(job_id, "duration_exceeded", get_failure_message("duration_exceeded"))
            inc("jobs_failed")
            return

        # Update job with duration
        with _get_sync_session() as db:
            j = db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id)).scalar_one()
            j.duration_seconds = duration
            # Detect format from extension
            if j.source_type == JobSourceType.upload and j.original_object_key:
                ext = Path(j.original_object_key).suffix.lstrip(".").lower()
                j.input_format = ext
            db.commit()

        # Step 3: Extract audio
        try:
            from worker.media.ffmpeg import extract_audio

            extract_audio(video_path, audio_path)
        except Exception:
            logger.exception("Transcode failed for job %s", job_id)
            _fail_job(job_id, "transcode_failed", get_failure_message("transcode_failed"))
            inc("jobs_failed")
            return

        # Upload audio to MinIO
        try:
            from app.services.storage_minio import put_object

            audio_key = f"audio/{job_id}/audio.mp3"
            with open(audio_path, "rb") as f:
                put_object(audio_key, f.read(), content_type="audio/mpeg")

            with _get_sync_session() as db:
                j = db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id)).scalar_one()
                j.audio_object_key = audio_key
                db.commit()
        except Exception:
            logger.exception("Storage error for job %s", job_id)
            _fail_job(job_id, "storage_error", get_failure_message("storage_error"))
            inc("jobs_failed")
            return

        # Step 4: Transcribe with Whisper
        try:
            from app.services.openai_whisper import transcribe_audio

            with Timer("transcription_duration"):
                whisper_segments = transcribe_audio(audio_path)
        except Exception:
            logger.exception("Transcription failed for job %s", job_id)
            _fail_job(job_id, "transcription_failed", get_failure_message("transcription_failed"))
            inc("jobs_failed")
            return

        # Step 5: Persist segments and mark complete
        try:
            with _get_sync_session() as db:
                j = db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id)).scalar_one()

                for ws in whisper_segments:
                    seg = TranscriptSegment(
                        job_id=job_id,
                        segment_index=ws.segment_index,
                        start_ms=ws.start_ms,
                        end_ms=ws.end_ms,
                        text=ws.text,
                        avg_logprob=ws.avg_logprob,
                        confidence=ws.confidence,
                    )
                    db.add(seg)

                j.status = JobStatus.completed
                j.completed_at = datetime.now(UTC)
                db.commit()

            inc("jobs_completed")
            logger.info("Job %s completed with %d segments", job_id, len(whisper_segments))
        except Exception:
            logger.exception("Failed to persist segments for job %s", job_id)
            _fail_job(job_id, "unknown", get_failure_message("unknown"))
            inc("jobs_failed")


def _download_from_minio(object_key: str | None, dest_path: str) -> None:
    """Download a file from MinIO to local path."""
    if not object_key:
        raise ValueError("No object key")
    from app.services.storage_minio import get_object

    data = get_object(object_key)
    with open(dest_path, "wb") as f:
        f.write(data)


def _download_from_url(url: str | None, dest_path: str, job_id: uuid.UUID) -> None:
    """Download a file from external URL to local path."""
    if not url:
        raise ValueError("No URL")
    from worker.media.downloader import download_file

    download_file(url, dest_path)


def _fail_job(job_id: uuid.UUID, code: str, message: str) -> None:
    """Mark a job as failed in the DB."""
    try:
        with _get_sync_session() as db:
            j = db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id)).scalar_one_or_none()
            if j and j.status not in (JobStatus.completed, JobStatus.failed):
                j.status = JobStatus.failed
                j.failure_code = code
                j.failure_message = message
                j.completed_at = datetime.now(UTC)
                db.commit()
    except Exception:
        logger.exception("Failed to mark job %s as failed", job_id)


@shared_task
def retention_cleanup() -> None:
    """Delete jobs older than 30 days along with their MinIO objects."""
    cutoff = datetime.now(UTC) - timedelta(days=30)
    logger.info("Running retention cleanup for jobs older than %s", cutoff.isoformat())

    with _get_sync_session() as db:
        old_jobs = db.execute(select(TranscriptionJob).where(TranscriptionJob.created_at < cutoff)).scalars().all()

        deleted_count = 0
        for job in old_jobs:
            # Delete MinIO objects
            from app.services.storage_minio import delete_object

            if job.original_object_key:
                try:
                    delete_object(job.original_object_key)
                except Exception:
                    logger.warning("Failed to delete MinIO object: %s", job.original_object_key)

            if job.audio_object_key:
                try:
                    delete_object(job.audio_object_key)
                except Exception:
                    logger.warning("Failed to delete MinIO object: %s", job.audio_object_key)

            # Delete job (cascades to segments)
            db.delete(job)
            deleted_count += 1

        db.commit()
        logger.info("Retention cleanup: deleted %d jobs", deleted_count)
        inc("retention_deleted", deleted_count)
