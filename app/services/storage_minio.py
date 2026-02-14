"""MinIO storage client wrapper."""

from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    return _client


def ensure_bucket() -> None:
    """Create the bucket if it doesn't exist."""
    client = get_minio_client()
    bucket = settings.MINIO_BUCKET
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info("Created MinIO bucket: %s", bucket)
    except S3Error:
        logger.exception("Failed to ensure MinIO bucket")
        raise


def put_object(key: str, data: bytes | BytesIO, content_type: str = "application/octet-stream") -> None:
    """Upload an object to the bucket."""
    client = get_minio_client()
    if isinstance(data, bytes):
        data = BytesIO(data)
    size = data.seek(0, 2)
    data.seek(0)
    client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=key,
        data=data,
        length=size,
        content_type=content_type,
    )
    logger.info("Uploaded object: %s (%d bytes)", key, size)


def get_object(key: str) -> bytes:
    """Download an object from the bucket."""
    client = get_minio_client()
    response = client.get_object(settings.MINIO_BUCKET, key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def delete_object(key: str) -> None:
    """Delete an object from the bucket."""
    client = get_minio_client()
    try:
        client.remove_object(settings.MINIO_BUCKET, key)
        logger.info("Deleted object: %s", key)
    except S3Error:
        logger.warning("Failed to delete object: %s", key)
