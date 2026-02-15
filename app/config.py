"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_BASE_URL: str = "https://vsn.riccardobucco.com"
    APP_PORT: int = 7200
    SESSION_SECRET_KEY: str = "change-me-to-a-long-random-string"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://vod:vod@postgres:5432/vod_transcription"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "vod-transcription"
    MINIO_SECURE: bool = False

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_TRANSCRIBE_MODEL: str = "whisper-1"

    # Logto Cloud (OIDC)
    LOGTO_ENDPOINT: str = "https://your-tenant.logto.app"
    LOGTO_APP_ID: str = ""
    LOGTO_APP_SECRET: str = ""
    LOGTO_REDIRECT_URI: str = "https://vsn.riccardobucco.com/auth/callback"
    LOGTO_POST_LOGOUT_REDIRECT_URI: str = "https://vsn.riccardobucco.com/"

    # Optional: M2M for Logto bootstrap
    LOGTO_M2M_CLIENT_ID: str = ""
    LOGTO_M2M_CLIENT_SECRET: str = ""
    REVIEWER_USERNAME: str = ""
    REVIEWER_EMAIL: str = ""
    REVIEWER_PASSWORD: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
