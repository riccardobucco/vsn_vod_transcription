# vsn_vod_transcription_specify Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-14

## Active Technologies
- Python 3.13+ + FastAPI (SSR + REST), Jinja2 templates, TailwindCSS (build step), SQLAlchemy (async), Celery, Redis, MinIO client (002-dashboard-submission-ux)
- PostgreSQL (jobs/segments/users), Redis (server-side session store; Celery broker), MinIO (uploaded media) (002-dashboard-submission-ux)

- Python 3.13+ + FastAPI, Jinja2, TailwindCSS (build step), SQLAlchemy (or equivalent ORM), Alembic, Celery, Redis client, MinIO S3 client, Logto Python SDK, OpenAI Python SDK (001-vod-transcription-utility)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13+: Follow standard conventions

## Recent Changes
- 002-dashboard-submission-ux: Added Python 3.13+ + FastAPI (SSR + REST), Jinja2 templates, TailwindCSS (build step), SQLAlchemy (async), Celery, Redis, MinIO client

- 001-vod-transcription-utility: Added Python 3.13+ + FastAPI, Jinja2, TailwindCSS (build step), SQLAlchemy (or equivalent ORM), Alembic, Celery, Redis client, MinIO S3 client, Logto Python SDK, OpenAI Python SDK

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
