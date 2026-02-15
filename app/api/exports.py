"""Export endpoint: download transcript in TXT/SRT/VTT format."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user, require_session
from app.db.models import JobStatus, User
from app.db.session import get_db
from app.services import exports, jobs_service

router = APIRouter(tags=["Jobs"])

EXPORT_FORMATS = {"txt", "srt", "vtt"}
CONTENT_TYPES = {
    "txt": "text/plain; charset=utf-8",
    "srt": "text/plain; charset=utf-8",
    "vtt": "text/vtt; charset=utf-8",
}


@router.get("/jobs/{job_id}/export/{fmt}", dependencies=[Depends(require_session)])
async def export_transcript(
    job_id: uuid.UUID,
    fmt: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download transcript export in the specified format."""
    if fmt not in EXPORT_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {', '.join(EXPORT_FORMATS)}")

    job = await jobs_service.get_job_by_id(db, job_id, user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.completed:
        raise HTTPException(status_code=400, detail="Transcript not available until job is completed")

    segments = await jobs_service.get_segments_for_job(db, job.id)

    if fmt == "txt":
        content = exports.to_txt(segments)
    elif fmt == "srt":
        content = exports.to_srt(segments)
    elif fmt == "vtt":
        content = exports.to_vtt(segments)
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

    filename = f"{job.source_label}.{fmt}"
    return Response(
        content=content,
        media_type=CONTENT_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
