"""Transcription orchestration — persist segments and derive confidence."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobStatus, TranscriptionJob, TranscriptSegment
from app.logging import get_logger
from app.services.openai_whisper import WhisperSegment

logger = get_logger(__name__)


async def persist_segments(
    db: AsyncSession,
    job: TranscriptionJob,
    whisper_segments: list[WhisperSegment],
) -> None:
    """Save Whisper segments to DB and update job status to completed."""
    for ws in whisper_segments:
        segment = TranscriptSegment(
            job_id=job.id,
            segment_index=ws.segment_index,
            start_ms=ws.start_ms,
            end_ms=ws.end_ms,
            text=ws.text,
            avg_logprob=ws.avg_logprob,
            confidence=ws.confidence,
        )
        db.add(segment)

    job.status = JobStatus.completed
    job.completed_at = datetime.now(UTC)
    await db.flush()
    logger.info("Persisted %d segments for job %s", len(whisper_segments), job.id)


async def mark_job_failed(
    db: AsyncSession,
    job_id: uuid.UUID,
    failure_code: str,
    failure_message: str,
) -> None:
    """Mark a job as failed with a reason."""
    from sqlalchemy import select

    result = await db.execute(select(TranscriptionJob).where(TranscriptionJob.id == job_id))
    job = result.scalar_one_or_none()
    if job:
        job.status = JobStatus.failed
        job.failure_code = failure_code
        job.failure_message = failure_message
        job.completed_at = datetime.now(UTC)
        await db.flush()
