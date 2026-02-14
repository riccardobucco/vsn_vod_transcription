"""FFprobe helper — extract media duration and audio presence."""

import json
import subprocess

from app.logging import get_logger

logger = get_logger(__name__)


def probe_media(file_path: str) -> dict:
    """Run ffprobe on a file and return parsed JSON output."""
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        logger.warning("ffprobe failed: %s", result.stderr[:500])
        raise RuntimeError(f"ffprobe failed: {result.stderr[:200]}")
    return json.loads(result.stdout)


def get_duration_seconds(file_path: str) -> int | None:
    """Get duration of the media file in seconds (rounded)."""
    try:
        info = probe_media(file_path)
        duration_str = info.get("format", {}).get("duration")
        if duration_str:
            return int(float(duration_str))
    except Exception:
        logger.exception("Failed to get duration for %s", file_path)
    return None


def has_audio(file_path: str) -> bool:
    """Check if the media file has at least one audio stream."""
    try:
        info = probe_media(file_path)
        streams = info.get("streams", [])
        return any(s.get("codec_type") == "audio" for s in streams)
    except Exception:
        logger.exception("Failed to check audio for %s", file_path)
        return False
