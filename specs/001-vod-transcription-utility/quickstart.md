# Quickstart: VOD Transcription Utility

**Feature**: 001-vod-transcription-utility  
**Date**: 2026-02-14

This document is written for reviewer-verifiable setup in <10 minutes once the source code + `docker-compose.yml` are present.

## Deployment assumptions

- Reverse proxy already terminates TLS and routes `vsn.riccardobucco.com` → the app container port on the home server.
- The entire stack runs via Docker Compose: `docker compose up`.

## Required services (Compose)

- `app` (FastAPI + Jinja2 SSR)
- `worker` (Celery)
- `beat` (Celery Beat for retention cleanup)
- `postgres`
- `redis`
- `minio`
- `logto` (Logto OSS) *(or use Logto Cloud by pointing `LOGTO_ENDPOINT` at cloud and omitting the Logto container)*

## Environment variables

Create a `.env` for Compose with (names are representative; final names should match implementation):

- **App**
  - `APP_BASE_URL` (e.g. `https://vsn.riccardobucco.com`)
  - `SESSION_SECRET_KEY` (random, long)
  - `DATABASE_URL` (Postgres DSN)
  - `REDIS_URL`
  - `MINIO_ENDPOINT` (e.g. `http://minio:9000`)
  - `MINIO_ACCESS_KEY`
  - `MINIO_SECRET_KEY`
  - `MINIO_BUCKET` (e.g. `vod-transcription`)
  - `OPENAI_API_KEY`
  - `OPENAI_TRANSCRIBE_MODEL` (default: `whisper-1`)

- **Logto (OIDC)**
  - `LOGTO_ENDPOINT` (e.g. `http://logto:3001` for OSS, or your cloud endpoint)
  - `LOGTO_APP_ID`
  - `LOGTO_APP_SECRET`
  - `LOGTO_REDIRECT_URI` (e.g. `https://vsn.riccardobucco.com/auth/callback`)
  - `LOGTO_POST_LOGOUT_REDIRECT_URI` (e.g. `https://vsn.riccardobucco.com/`)

- **Optional: bootstrap Reviewer user using Management API**
  - `LOGTO_M2M_CLIENT_ID`
  - `LOGTO_M2M_CLIENT_SECRET`
  - `REVIEWER_USERNAME`
  - `REVIEWER_EMAIL` (optional)
  - `REVIEWER_PASSWORD`

## Logto one-time setup (if self-hosting)

If you self-host Logto via Compose:

1. Start core services: `docker compose up -d postgres redis minio logto`
2. Visit the Logto Console URL (provided by Logto OSS) and create:
   - A **Traditional Web** application for this web app.
   - Redirect URIs:
     - `https://vsn.riccardobucco.com/auth/callback`
   - Post-logout redirect URIs:
     - `https://vsn.riccardobucco.com/`
   - Copy **App ID** and **App Secret** into `.env`.
3. (Optional but recommended) Create a **Machine-to-machine** app with Management API permission `all`, then put its client id/secret in `.env` so the stack can auto-provision/update the Reviewer user.

## Run the stack

From repo root:

- `docker compose up -d`
- `docker compose ps`
- `docker compose logs -f app worker beat`

## Verify the feature

1. Navigate to `https://vsn.riccardobucco.com/`.
2. You should be redirected to the app login page.
3. Click “Sign in” → redirected to Logto sign-in.
4. Sign in as the preconfigured Reviewer.
5. On the dashboard:
   - Submit a job via file upload (MP4/MOV/MKV) and confirm it appears as `queued` or `processing`.
   - Submit a job via direct URL and confirm it appears.
6. Wait for completion and open job details:
   - Confirm time-coded segments are shown.
   - Confirm per-segment confidence indicator is shown.
7. Download exports:
   - `TXT`, `SRT`, `VTT`.

## Notes / operational considerations

- Retention cleanup runs daily and deletes jobs + related objects after 30 days.
- Worker must include ffmpeg tooling to probe duration and extract/compress audio so OpenAI upload stays under 25 MB.
