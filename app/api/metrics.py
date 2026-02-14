"""Metrics endpoint."""

from fastapi import APIRouter, Depends

from app.auth.deps import require_session
from app.metrics import get_metrics

router = APIRouter(tags=["Metrics"])


@router.get("/metrics", dependencies=[Depends(require_session)])
async def metrics():
    return get_metrics()
