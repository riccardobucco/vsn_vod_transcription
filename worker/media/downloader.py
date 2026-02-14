"""URL download helper with SSRF protections."""

import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from app.logging import get_logger

logger = get_logger(__name__)

ALLOWED_SCHEMES = {"http", "https"}
MAX_DOWNLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
DOWNLOAD_TIMEOUT = 600  # 10 minutes


def _is_private_ip(hostname: str) -> bool:
    """Check if a hostname resolves to a private/reserved IP address."""
    try:
        addrs = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for _, _, _, _, sockaddr in addrs:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return True
    except (socket.gaierror, ValueError):
        return True  # Can't resolve → block
    return False


def validate_url(url: str) -> None:
    """Validate the URL for safety (scheme, SSRF)."""
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("No hostname in URL")

    if _is_private_ip(hostname):
        raise ValueError("URL points to a private/reserved address")


def download_file(url: str, dest_path: str) -> int:
    """Download a file from URL to local path. Returns file size in bytes.

    Raises ValueError for SSRF violations or size limits.
    """
    validate_url(url)

    downloaded = 0
    with httpx.stream("GET", url, timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as response:
        response.raise_for_status()

        # Check Content-Length if available
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_DOWNLOAD_SIZE:
            raise ValueError("File exceeds maximum download size")

        with open(dest_path, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=65536):
                downloaded += len(chunk)
                if downloaded > MAX_DOWNLOAD_SIZE:
                    raise ValueError("Download exceeded maximum size")
                f.write(chunk)

    logger.info("Downloaded %d bytes from URL", downloaded)
    return downloaded
