"""FFmpeg helper — extract and transcode audio."""

import subprocess

from app.logging import get_logger

logger = get_logger(__name__)


def extract_audio(input_path: str, output_path: str) -> None:
    """Extract audio from video, transcode to mono 16kHz MP3 at 48kbps.

    This ensures the output stays well under OpenAI's 25MB limit for 30-minute videos.
    30 min × 48 kbps ≈ 10.8 MB.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vn",  # No video
        "-acodec",
        "libmp3lame",  # MP3 codec
        "-ar",
        "16000",  # 16 kHz sample rate
        "-ac",
        "1",  # Mono
        "-b:a",
        "48k",  # 48 kbps bitrate
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        logger.warning("ffmpeg failed: %s", result.stderr[:500])
        raise RuntimeError(f"ffmpeg audio extraction failed: {result.stderr[:200]}")
    logger.info("Extracted audio: %s -> %s", input_path, output_path)
