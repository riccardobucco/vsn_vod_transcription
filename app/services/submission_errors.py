"""Mapping helpers for friendly submission error pages."""

from __future__ import annotations

from typing import Any

from app.services import submission_service

GENERIC_MESSAGE = "We couldn't submit your job."


def build_submission_error(error: submission_service.SubmissionError) -> dict[str, Any]:
    """Return a friendly error view model for a submission error."""
    detail = error.detail
    if error.code == "unsupported_format":
        detail = "Unsupported format. Allowed: MP4, MOV, MKV."
    elif error.code == "file_too_large":
        detail = "File too large (max 2 GB)."
    elif error.code == "missing_file":
        detail = "A file is required."
    elif error.code == "invalid_url":
        detail = "Only http and https URLs are supported."
    elif error.code == "missing_url":
        detail = "A URL is required."

    return {
        "message": GENERIC_MESSAGE,
        "details": detail,
    }


def build_unexpected_error(details: str) -> dict[str, Any]:
    """Return a friendly error view model for unexpected failures."""
    return {
        "message": GENERIC_MESSAGE,
        "details": details,
    }
