"""Export formatters: TXT, SRT, VTT."""

from app.db.models import TranscriptSegment


def _format_time_srt(ms: int) -> str:
    """Format milliseconds as HH:MM:SS,mmm for SRT."""
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def _format_time_vtt(ms: int) -> str:
    """Format milliseconds as HH:MM:SS.mmm for VTT."""
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def to_txt(segments: list[TranscriptSegment]) -> str:
    """Export segments as plain text."""
    lines = [seg.text for seg in segments]
    return "\n".join(lines) + "\n"


def to_srt(segments: list[TranscriptSegment]) -> str:
    """Export segments as SRT subtitle format."""
    blocks: list[str] = []
    for i, seg in enumerate(segments, start=1):
        start = _format_time_srt(seg.start_ms)
        end = _format_time_srt(seg.end_ms)
        blocks.append(f"{i}\n{start} --> {end}\n{seg.text}")
    return "\n\n".join(blocks) + "\n"


def to_vtt(segments: list[TranscriptSegment]) -> str:
    """Export segments as WebVTT subtitle format."""
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = _format_time_vtt(seg.start_ms)
        end = _format_time_vtt(seg.end_ms)
        lines.append(f"{start} --> {end}")
        lines.append(seg.text)
        lines.append("")
    return "\n".join(lines)
