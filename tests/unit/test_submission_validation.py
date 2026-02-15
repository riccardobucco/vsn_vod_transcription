"""Test: submission validation (format allowlist, URL validation)."""

import pytest


class TestFormatAllowlist:
    """Test that only MP4/MOV/MKV formats are accepted."""

    @pytest.mark.parametrize("ext", [".mp4", ".mov", ".mkv"])
    def test_allowed_extensions(self, ext):
        from app.api.jobs import ALLOWED_EXTENSIONS

        assert ext in ALLOWED_EXTENSIONS

    @pytest.mark.parametrize("ext", [".avi", ".wmv", ".flv", ".webm", ".txt", ".py"])
    def test_disallowed_extensions(self, ext):
        from app.api.jobs import ALLOWED_EXTENSIONS

        assert ext not in ALLOWED_EXTENSIONS


class TestUrlValidation:
    """Test URL validation for SSRF protections."""

    def test_http_allowed(self):
        from worker.media.downloader import validate_url

        # Should not raise
        validate_url("http://example.com/video.mp4")

    def test_https_allowed(self):
        from worker.media.downloader import validate_url

        validate_url("https://example.com/video.mp4")

    def test_ftp_rejected(self):
        from worker.media.downloader import validate_url

        with pytest.raises(ValueError, match="Unsupported scheme"):
            validate_url("ftp://example.com/video.mp4")

    def test_file_scheme_rejected(self):
        from worker.media.downloader import validate_url

        with pytest.raises(ValueError, match="Unsupported scheme"):
            validate_url("file:///etc/passwd")

    def test_no_hostname_rejected(self):
        from worker.media.downloader import validate_url

        with pytest.raises(ValueError):
            validate_url("http:///path")
