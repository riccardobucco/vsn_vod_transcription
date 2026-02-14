"""VOD Transcription Utility — FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application startup / shutdown hooks."""
    # Startup: ensure MinIO bucket exists
    from app.services.storage_minio import ensure_bucket

    ensure_bucket()
    yield


app = FastAPI(
    title="VSN VOD Transcription Utility",
    version="0.1.0",
    lifespan=lifespan,
)

# Session middleware (cookie-based session id)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="vsn_session",
    max_age=86400,  # 24 hours
    same_site="lax",
    https_only=settings.APP_BASE_URL.startswith("https"),
)

# Static files
_static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# Templates
_template_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_template_dir))


# Global request_id middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid

    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Import and mount routers
from app.api.exports import router as exports_router  # noqa: E402
from app.api.health import router as health_router  # noqa: E402
from app.api.jobs import router as jobs_router  # noqa: E402
from app.api.metrics import router as metrics_router  # noqa: E402
from app.auth.routes import router as auth_router  # noqa: E402
from app.routes.dashboard import router as dashboard_router  # noqa: E402
from app.routes.job_detail import router as job_detail_router  # noqa: E402

app.include_router(health_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(exports_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(job_detail_router)
