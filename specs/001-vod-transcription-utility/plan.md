#+#+#+#+### Implementation Plan: VOD Transcription Utility

**Branch**: `001-vod-transcription-utility` | **Date**: 2026-02-14 | **Spec**: specs/001-vod-transcription-utility/spec.md
**Input**: Feature specification from `/specs/001-vod-transcription-utility/spec.md`

## Summary

Deliver a private, authenticated web utility that lets a single “Reviewer” submit VODs (upload or direct URL) and later retrieve time-coded transcript segments with confidence indicators and downloads (TXT/SRT/VTT). The system runs on a single home server via Docker Compose and uses FastAPI (SSR via Jinja2), PostgreSQL, MinIO, Redis, Celery workers, Logto for auth, and the OpenAI Whisper API for transcription.

Phase 0/1 artifacts:
- Research decisions: specs/001-vod-transcription-utility/research.md
- Data model: specs/001-vod-transcription-utility/data-model.md
- API contract: specs/001-vod-transcription-utility/contracts/openapi.yaml
- Ops quickstart: specs/001-vod-transcription-utility/quickstart.md

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: FastAPI, Jinja2, TailwindCSS (build step), SQLAlchemy (or equivalent ORM), Alembic, Celery, Redis client, MinIO S3 client, Logto Python SDK, OpenAI Python SDK  
**Storage**: PostgreSQL (jobs + segments + metadata), MinIO (video/audio objects; optional cached exports)  
**Testing**: pytest (unit + API/contract validation; one end-to-end happy path gated by environment secrets)  
**Target Platform**: Single Linux home server (Docker Compose), public static IP + domain; reverse proxy terminates TLS and routes `vsn.riccardobucco.com` to the app’s exposed local port
**Project Type**: Web application (SSR backend; REST API + HTML routes in one service)  
**Performance Goals**:
- Handle typical stakeholder usage (low concurrency) reliably.
- For VODs ≤ 30 minutes, target “completed” within ~10 minutes in normal conditions (matches SC-004).
**Constraints**:
- Must support async processing (Celery) so jobs continue after browser closes (FR-008).
- OpenAI Audio API upload limit (~25 MB) must be respected by extracting/compressing audio before upload.
- Retention: auto-delete jobs and outputs after 30 days (FR-019).
- Do not log transcript text or user-provided content at info level (constitution).
**Scale/Scope**:
- Single persona (“Reviewer”) and small job volumes.
- Inputs: MP4/MOV/MKV, max 30 minutes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Transcription Is a Verifiable Artifact — PASS
- Persist transcript segments with start/end times.
- Persist provenance metadata: job id, source label, model identifier (`whisper-1`), created_at.

### II. Data Minimization by Default — PASS (with explicit retention)
- Store only what is needed to transcribe and present results.
- Media storage is in MinIO with a fixed 30-day retention cleanup.
- Logging policy: metadata-only at info level; transcript text never logged at info level.

### III. Reliability Over Cleverness — PASS
- Asynchronous, resumable processing with explicit job state machine `queued → processing → completed | failed`.
- Failures surfaced with user-appropriate reason.

### IV. Contract-First API — PASS
- Contract provided in specs/001-vod-transcription-utility/contracts/openapi.yaml.
- Covers upload + URL job creation, status polling, transcript retrieval, and exports.

### V. Observability and Simplicity — PASS
- Structured logs with `request_id` and `job_id`.
- Basic metrics tracked: throughput, latency, failure rate, transcription duration (implementation detail tracked during build).

No constitution violations are required for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/001-vod-transcription-utility/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text

app/
├── main.py
├── api/
│   ├── health.py
│   ├── jobs.py
│   └── exports.py
├── auth/
│   ├── logto_client.py
│   ├── routes.py
│   └── session_store.py
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   └── job_detail.html
├── static/
│   ├── app.css
│   └── tailwind.css
└── services/
  ├── storage_minio.py
  ├── openai_whisper.py
  └── transcription.py

worker/
├── celery_app.py
├── tasks.py
└── media/
  ├── ffprobe.py
  └── ffmpeg.py

migrations/
├── env.py
└── versions/

tests/
├── contract/
├── integration/
└── unit/

docker-compose.yml
docker/
├── Dockerfile.app
└── Dockerfile.worker
```

**Structure Decision**: Single web application repo structure with SSR templates and REST API in the `app/` service, plus a separate `worker/` Celery service for long-running media/transcription work.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
