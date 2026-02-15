"""Celery application configuration."""

import os

from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Allow eager mode for testing
CELERY_ALWAYS_EAGER = os.getenv("CELERY_ALWAYS_EAGER", "false").lower() == "true"

celery_app = Celery(
    "vod_transcription",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=CELERY_ALWAYS_EAGER,
    task_eager_propagates=CELERY_ALWAYS_EAGER,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "retention-cleanup-daily": {
        "task": "worker.tasks.retention_cleanup",
        "schedule": crontab(hour=3, minute=0),  # Run daily at 03:00 UTC
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["worker"])
