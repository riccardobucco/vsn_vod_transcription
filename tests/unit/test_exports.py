"""Test: export formatters produce valid TXT/SRT/VTT output."""

import pytest
from app.services.exports import to_srt, to_txt, to_vtt


class FakeSegment:
    """Minimal segment for testing export formatters."""

    def __init__(self, segment_index: int, start_ms: int, end_ms: int, text: str, confidence: float | None = None):
        self.segment_index = segment_index
        self.start_ms = start_ms
        self.end_ms = end_ms
        self.text = text
        self.confidence = confidence


@pytest.fixture
def sample_segments():
    return [
        FakeSegment(0, 0, 5000, "Hello world."),
        FakeSegment(1, 5000, 10500, "This is a test."),
        FakeSegment(2, 10500, 15000, "Goodbye."),
    ]


class TestTxtExport:
    def test_txt_contains_all_text(self, sample_segments):
        result = to_txt(sample_segments)
        assert "Hello world." in result
        assert "This is a test." in result
        assert "Goodbye." in result

    def test_txt_newline_separated(self, sample_segments):
        result = to_txt(sample_segments)
        lines = result.strip().split("\n")
        assert len(lines) == 3


class TestSrtExport:
    def test_srt_has_sequence_numbers(self, sample_segments):
        result = to_srt(sample_segments)
        assert "\n1\n" in result or result.startswith("1\n")
        assert "\n2\n" in result
        assert "\n3\n" in result

    def test_srt_has_timestamps(self, sample_segments):
        result = to_srt(sample_segments)
        assert "00:00:00,000 --> 00:00:05,000" in result
        assert "00:00:05,000 --> 00:00:10,500" in result

    def test_srt_has_text(self, sample_segments):
        result = to_srt(sample_segments)
        assert "Hello world." in result


class TestVttExport:
    def test_vtt_starts_with_header(self, sample_segments):
        result = to_vtt(sample_segments)
        assert result.startswith("WEBVTT")

    def test_vtt_has_timestamps(self, sample_segments):
        result = to_vtt(sample_segments)
        assert "00:00:00.000 --> 00:00:05.000" in result

    def test_vtt_has_text(self, sample_segments):
        result = to_vtt(sample_segments)
        assert "Hello world." in result
