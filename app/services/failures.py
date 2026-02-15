"""Human-readable failure reason mapping."""

FAILURE_MESSAGES: dict[str, str] = {
    "unsupported_format": "The uploaded file format is not supported. Please use MP4, MOV, or MKV.",
    "no_audio_track": "The video file does not contain an audio track.",
    "duration_exceeded": "The video exceeds the 30-minute maximum duration.",
    "download_failed": "Failed to download the video from the provided URL.",
    "download_timeout": "The download timed out. The file may be too large or the server too slow.",
    "download_size_exceeded": "The file exceeds the maximum download size.",
    "ssrf_blocked": "The provided URL points to a restricted network address.",
    "transcription_failed": "The transcription service encountered an error. Please try again.",
    "probe_failed": "Could not read the video file. It may be corrupted or in an unsupported format.",
    "transcode_failed": "Failed to extract and compress audio from the video.",
    "storage_error": "Failed to store the file. Please try again.",
    "unknown": "An unexpected error occurred. Please try again later.",
}


def get_failure_message(code: str) -> str:
    """Get a human-readable message for a failure code."""
    return FAILURE_MESSAGES.get(code, FAILURE_MESSAGES["unknown"])
