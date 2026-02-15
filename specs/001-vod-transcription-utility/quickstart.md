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

Authentication is handled by **Logto Cloud** (external SaaS) — no Logto container needed.

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

- **Logto Cloud (OIDC)**
  - `LOGTO_ENDPOINT` (e.g. `https://your-tenant.logto.app`)
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

## Logto Cloud setup (one-time)

1. Sign up at [logto.io](https://logto.io/) and create a tenant.
2. In the Logto Cloud Console, create a **Traditional Web** application:
   - Redirect URIs: `https://vsn.riccardobucco.com/auth/callback`
   - Post-logout redirect URIs: `https://vsn.riccardobucco.com/`
   - Copy **App ID** and **App Secret** into `.env`.
   - Note your tenant endpoint (e.g. `https://your-tenant.logto.app`) and set it as `LOGTO_ENDPOINT`.
3. Create a Reviewer user account in the Logto Cloud Console (Users → Create User).
4. (Optional) Create a **Machine-to-machine** app with Management API permission `all`, then put its client id/secret in `.env` to enable automated user provisioning.

## Run the stack

From repo root:

- `docker compose up -d`
- `docker compose ps`
- `docker compose logs -f app worker beat`

## Verify the feature

1. Navigate to `https://vsn.riccardobucco.com/`.
2. You should be redirected to the app login page.
3. Click "Sign in" → redirected to Logto Cloud sign-in.
4. Sign in as the preconfigured Reviewer.
5. On the dashboard:
   - Submit a job via file upload (MP4/MOV/MKV) and confirm it appears as `queued` or `processing`.
   - Submit a job via direct URL and confirm it appears.
     - Sample direct MP4 URLs:
       - Short: [podcast_refugee2.mp4](https://archive.org/download/RefugeeLife2Alhaphis/podcast_refugee2.mp4)
       - Longer: [CityManagerSearchMeeting_3172022.mp4](https://archive.org/download/city-manager-search-committee-meeting-march-17-2022/1608-1%20CityManagerSearchMeeting_3172022.mp4)
       - Very large (may fail with size/timeouts depending on environment): [Stephan Lopes.mp4](https://dn710807.ca.archive.org/0/items/StephanLopes/Stephan%20Lopes.mp4)
6. Wait for completion and open job details:
   - Confirm time-coded segments are shown.
   - Confirm per-segment confidence indicator is shown.
7. Download exports:
   - `TXT`, `SRT`, `VTT`.

## Notes / operational considerations

- Retention cleanup runs daily and deletes jobs + related objects after 30 days.
- Worker must include ffmpeg tooling to probe duration and extract/compress audio so OpenAI upload stays under 25 MB.
