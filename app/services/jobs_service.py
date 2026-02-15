"""Jobs query service for dashboard and API."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TranscriptionJob, TranscriptSegment


async def list_jobs_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[TranscriptionJob]:
    """List all jobs for a user, most recent first."""
    result = await db.execute(
        select(TranscriptionJob).where(TranscriptionJob.user_id == user_id).order_by(TranscriptionJob.created_at.desc())
    )
    return list(result.scalars().all())


async def get_job_by_id(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> TranscriptionJob | None:
    """Get a single job by ID, scoped to the user."""
    result = await db.execute(
        select(TranscriptionJob).where(TranscriptionJob.id == job_id, TranscriptionJob.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_segments_for_job(db: AsyncSession, job_id: uuid.UUID) -> list[TranscriptSegment]:
    """Get all transcript segments for a job, ordered by index."""
    result = await db.execute(
        select(TranscriptSegment).where(TranscriptSegment.job_id == job_id).order_by(TranscriptSegment.segment_index)
    )
    return list(result.scalars().all())


def compute_overall_confidence(segments: list[TranscriptSegment]) -> float | None:
    """Compute duration-weighted average confidence across segments."""
    total_duration = 0
    weighted_sum = 0.0
    has_confidence = False

    for seg in segments:
        duration = seg.end_ms - seg.start_ms
        if seg.confidence is not None and duration > 0:
            weighted_sum += seg.confidence * duration
            total_duration += duration
            has_confidence = True

    if not has_confidence or total_duration == 0:
        return None
    return weighted_sum / total_duration
