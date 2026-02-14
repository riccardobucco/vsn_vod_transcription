# VOD Transcription Utility

A private, authenticated web utility for transcribing VODs (Video On Demand) with time-coded segments, confidence indicators, and export capabilities (TXT/SRT/VTT).

## Architecture

- **FastAPI** SSR app with Jinja2 templates + REST API
- **Celery** workers for async transcription (Redis broker)
- **PostgreSQL** for jobs, segments, and user metadata
- **MinIO** (S3-compatible) for video/audio object storage
- **Logto** for OIDC authentication
- **OpenAI Whisper API** for speech-to-text transcription

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- Domain with TLS termination (reverse proxy)

### Setup

1. **Clone and configure:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings (OpenAI key, session secret, etc.)
   ```

2. **Start infrastructure services:**

   ```bash
   docker compose up -d postgres redis minio logto
   ```

3. **Configure Logto** (one-time):

   - Visit the Logto Admin Console at `http://localhost:3002`
   - Create a **Traditional Web** application
   - Set redirect URI: `https://vsn.riccardobucco.com/auth/callback`
   - Set post-logout redirect URI: `https://vsn.riccardobucco.com/`
   - Copy App ID and App Secret into `.env`
   - Create a Reviewer user account in Logto Console

4. **Start the full stack:**

   ```bash
   docker compose up -d
   ```

5. **Verify:**

   ```bash
   curl http://localhost:7200/api/health
   # {"status": "ok"}
   ```

### Usage

1. Navigate to `https://vsn.riccardobucco.com/`
2. Sign in via Logto as the Reviewer
3. Submit a video (upload MP4/MOV/MKV or paste a URL)
4. Wait for transcription to complete
5. View segments with timestamps and confidence indicators
6. Download exports: TXT, SRT, or VTT

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
| Logto | 7201 | vsn-logto.riccardobucco.com |

## License

Private — All rights reserved.
