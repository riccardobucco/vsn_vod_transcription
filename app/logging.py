"""Structured logging utilities."""

import logging
import sys
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
job_id_var: ContextVar[str | None] = ContextVar("job_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Formatter that adds request_id and job_id when available."""

    def format(self, record: logging.LogRecord) -> str:
        record.request_id = request_id_var.get()  # type: ignore[attr-defined]
        record.job_id = job_id_var.get()  # type: ignore[attr-defined]
        return super().format(record)


def setup_logging(level: int = logging.INFO) -> None:
    formatter = StructuredFormatter(
        fmt="%(asctime)s %(levelname)s [req=%(request_id)s job=%(job_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
