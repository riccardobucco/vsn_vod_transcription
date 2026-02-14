"""OpenAI Whisper API client wrapper."""

import math
from dataclasses import dataclass
from pathlib import Path

import openai

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WhisperSegment:
    """A transcript segment returned by the Whisper API."""

    segment_index: int
    start_ms: int
    end_ms: int
    text: str
    avg_logprob: float | None
    confidence: float | None


def transcribe_audio(audio_path: str | Path) -> list[WhisperSegment]:
    """Send audio to OpenAI Whisper and return parsed segments.

    Uses verbose_json response format with segment-level timestamps.
    """
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    with open(audio_path, "rb") as audio_file:
        logger.info("Sending audio to Whisper API (model=%s)", settings.OPENAI_TRANSCRIBE_MODEL)
        response = client.audio.transcriptions.create(
            model=settings.OPENAI_TRANSCRIBE_MODEL,
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments: list[WhisperSegment] = []
    raw_segments = getattr(response, "segments", None) or []

    for idx, seg in enumerate(raw_segments):
        start_s = getattr(seg, "start", 0) or 0
        end_s = getattr(seg, "end", 0) or 0
        text = getattr(seg, "text", "").strip()
        avg_logprob = getattr(seg, "avg_logprob", None)

        confidence: float | None = None
        if avg_logprob is not None:
            confidence = math.exp(avg_logprob)
            confidence = max(0.0, min(1.0, confidence))

        segments.append(
            WhisperSegment(
                segment_index=idx,
                start_ms=int(start_s * 1000),
                end_ms=int(end_s * 1000),
                text=text,
                avg_logprob=avg_logprob,
                confidence=confidence,
            )
        )

    logger.info("Whisper returned %d segments", len(segments))
    return segments
