# VOD Transcription Utility

A private, authenticated web utility for transcribing VODs (Video On Demand) with time-coded segments, confidence indicators, and export capabilities (TXT/SRT/VTT).

## Architecture

- **FastAPI** SSR app with Jinja2 templates + REST API
- **Celery** workers for async transcription (Redis broker)
- **PostgreSQL** for jobs, segments, and user metadata
- **MinIO** (S3-compatible) for video/audio object storage
- **Logto Cloud** for OIDC authentication
- **OpenAI Whisper API** for speech-to-text transcription

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- Logto Cloud account (free tier at [logto.io](https://logto.io/))
- Domain with TLS termination (reverse proxy). This is an extra external dependency you must provision (DNS + TLS), and it is required so Logto OIDC callbacks can use your own HTTPS domain and the app can run behind a secure, stable URL.

### Deployment assumptions

- A reverse proxy already terminates TLS and routes your domain to the app container port.
- The entire stack runs via Docker Compose (`docker compose up`).
- The worker image includes ffmpeg tooling for audio extraction and compression.

### Required services (Compose)

- `app` (FastAPI + Jinja2 SSR)
- `worker` (Celery)
- `beat` (Celery Beat for retention cleanup)
- `postgres`
- `redis`
- `minio`

### Setup

1. **Clone and configure:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings (OpenAI key, session secret, Logto Cloud credentials, etc.)
   ```

2. **Configure environment variables:**

   Set your domain and Logto callbacks to match your deployment. Example values below use `vsn.riccardobucco.com`; replace with your domain.
   For local-only testing, use `http://localhost:7200` for `APP_BASE_URL`, `LOGTO_REDIRECT_URI`, and `LOGTO_POST_LOGOUT_REDIRECT_URI` and ensure Logto allows localhost callbacks.

   - `APP_BASE_URL` (e.g. `https://your-domain.com`)
   - `APP_PORT` (default `7200`)
   - `SESSION_SECRET_KEY` (long random string)
   - `DATABASE_URL` (Postgres DSN, default in `.env.example`)
   - `REDIS_URL`
   - `MINIO_ENDPOINT` (e.g. `minio:9000`)
   - `MINIO_ACCESS_KEY`
   - `MINIO_SECRET_KEY`
   - `MINIO_BUCKET`
   - `MINIO_SECURE` (`true` or `false`)
   - `OPENAI_API_KEY`
   - `OPENAI_TRANSCRIBE_MODEL` (default `whisper-1`)
   - `LOGTO_ENDPOINT` (e.g. `https://your-tenant.logto.app`)
   - `LOGTO_APP_ID`
   - `LOGTO_APP_SECRET`
   - `LOGTO_REDIRECT_URI` (e.g. `https://your-domain.com/auth/callback`)
   - `LOGTO_POST_LOGOUT_REDIRECT_URI` (e.g. `https://your-domain.com/`)

   Optional reviewer bootstrap via Logto Management API:

   - `LOGTO_M2M_CLIENT_ID`
   - `LOGTO_M2M_CLIENT_SECRET`
   - `REVIEWER_USERNAME`
   - `REVIEWER_EMAIL`
   - `REVIEWER_PASSWORD`

3. **Configure Logto Cloud** (one-time):

   - Sign up at [logto.io](https://logto.io/) and create a tenant
   - Create a **Traditional Web** application in the Logto Cloud Console
   - Set redirect URI: `https://your-domain.com/auth/callback`
   - Set post-logout redirect URI: `https://your-domain.com/`
   - Copy **App ID** and **App Secret** into `.env`
   - Set `LOGTO_ENDPOINT` to your tenant URL (e.g. `https://your-tenant.logto.app`)
   - Create a Reviewer user account in the Logto Cloud Console (Users → Create User)
   - Optional: create a **Machine-to-machine** app with Management API permission `all` for automated reviewer provisioning

4. **Start the stack:**

   ```bash
   docker compose up -d
   ```

5. **Verify:**

   ```bash
   curl http://localhost:7200/api/health
   # {"status": "ok"}
   ```

   ```bash
   docker compose ps
   docker compose logs -f app worker beat
   ```

### Usage

1. Navigate to your `APP_BASE_URL` (e.g. `https://your-domain.com/`)
2. Sign in via Logto Cloud as the Reviewer
3. Submit a video (upload MP4/MOV/MKV or paste a URL)
4. Confirm the submission on the confirmation page, then return to the dashboard or open job details
5. If a submission fails, review the friendly error page and return to the dashboard
6. If a job link is invalid or missing, the Job not found page will explain the issue
7. Wait for transcription to complete
8. View segments with timestamps and confidence indicators
9. Download exports: TXT, SRT, or VTT

### Sample test videos

If you want a quick URL-based test without uploading a file, these direct MP4 links contain people speaking:

- Short: [podcast_refugee2.mp4](https://archive.org/download/RefugeeLife2Alhaphis/podcast_refugee2.mp4)
- Longer: [CityManagerSearchMeeting_3172022.mp4](https://archive.org/download/city-manager-search-committee-meeting-march-17-2022/1608-1%20CityManagerSearchMeeting_3172022.mp4)
- Very large (may fail with size/timeouts depending on environment): [Stephan Lopes.mp4](https://dn710807.ca.archive.org/0/items/StephanLopes/Stephan%20Lopes.mp4)

## Reviewer Verification (Dashboard Submission UX)

1. Open `http://localhost:7200/` (or your `APP_BASE_URL`) and sign in.
2. URL submission → confirmation
3. Upload submission → uploading feedback + confirmation
4. Submission failure → friendly error page
5. Malformed job id → HTML 404
6. Non-existent job id → HTML 404

**URL submission → confirmation**

1. Submit a valid direct MP4 URL.
2. Expect a confirmation state/page (no JSON) with status label and actions: “Back to dashboard” and “View job details”.
3. Refresh the confirmation page and confirm no resubmission occurs (PRG), and the dashboard returns to normal state after flash data is consumed.

**Upload submission → uploading feedback + confirmation**

1. Choose an `.mp4`, `.mov`, or `.mkv` file.
2. Click “Upload & Transcribe”.
3. Expect immediate feedback. The UI shows “Uploading…”, submit is disabled to prevent double-submit, and the progress indicator is determinate when available (otherwise indeterminate).
4. After completion, the browser navigates to the confirmation state/page (no JSON).

**Submission failure → friendly error page**

1. Upload an unsupported format (e.g. `.txt`) or submit an invalid URL scheme (e.g. `ftp://...`).
2. Expect a friendly error page with plain-language message, a small “Details” area, and a single “Back to dashboard” action.

**Job not found (HTML 404)**

1. Visit `http://localhost:7200/jobs/not-a-uuid`.
2. Expect “Job not found” HTML page, HTTP 404, and “Back to dashboard” action.
3. Visit `http://localhost:7200/jobs/00000000-0000-0000-0000-000000000000`.
4. Expect the same.

## Operational notes

- Retention cleanup runs daily and deletes jobs + related objects after 30 days.
- The worker must include ffmpeg tooling to probe duration and compress audio so OpenAI uploads stay under 25 MB.

## Development

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Install Node dependencies (Tailwind CSS)
npm install

# Run tests
pytest tests/ -x

# Lint
ruff check .
ruff format --check .

# Type check
mypy app worker --ignore-missing-imports

# Build Tailwind CSS
npm run build:css
```

## Port Configuration

| Service | Default Port | Domain |
|---------|-------------|--------|
| App | 7200 | your domain (e.g. your-domain.com) |

## License

Private — All rights reserved.
