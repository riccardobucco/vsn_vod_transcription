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
- Domain with TLS termination (reverse proxy)

### Setup

1. **Clone and configure:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings (OpenAI key, session secret, Logto Cloud credentials, etc.)
   ```

2. **Configure Logto Cloud** (one-time):

   - Sign up at [logto.io](https://logto.io/) and create a tenant
   - Create a **Traditional Web** application in the Logto Cloud Console
   - Set redirect URI: `https://vsn.riccardobucco.com/auth/callback`
   - Set post-logout redirect URI: `https://vsn.riccardobucco.com/`
   - Copy **App ID** and **App Secret** into `.env`
   - Set `LOGTO_ENDPOINT` to your tenant URL (e.g. `https://your-tenant.logto.app`)
   - Create a Reviewer user account in the Logto Cloud Console (Users → Create User)

3. **Start the stack:**

   ```bash
   docker compose up -d
   ```

4. **Verify:**

   ```bash
   curl http://localhost:7200/api/health
   # {"status": "ok"}
   ```

### Usage

1. Navigate to `https://vsn.riccardobucco.com/`
2. Sign in via Logto Cloud as the Reviewer
3. Submit a video (upload MP4/MOV/MKV or paste a URL)
4. Wait for transcription to complete
5. View segments with timestamps and confidence indicators
6. Download exports: TXT, SRT, or VTT

### Sample test videos

If you want a quick URL-based test without uploading a file, these direct MP4 links contain people speaking:

- Short: [podcast_refugee2.mp4](https://archive.org/download/RefugeeLife2Alhaphis/podcast_refugee2.mp4)
- Longer: [CityManagerSearchMeeting_3172022.mp4](https://archive.org/download/city-manager-search-committee-meeting-march-17-2022/1608-1%20CityManagerSearchMeeting_3172022.mp4)
- Very large (may fail with size/timeouts depending on environment): [Stephan Lopes.mp4](https://dn710807.ca.archive.org/0/items/StephanLopes/Stephan%20Lopes.mp4)

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
| App | 7200 | vsn.riccardobucco.com |

## License

Private — All rights reserved.
