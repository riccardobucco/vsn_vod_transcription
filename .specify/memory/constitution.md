# VOD Transcription Web App Constitution

## Core Principles

### I. Transcription Is a Verifiable Artifact
Transcription output must be reproducible and auditable:
- Persist the raw transcript text plus basic provenance (source media identifier, transcription model/service identifier, language, created_at).
- Preserve timing information when available (segments with start/end times).
- Store enough metadata to explain “what produced this transcript” without exposing secrets.

### II. Data Minimization by Default
Handle media and user data conservatively:
- Only collect what is needed to transcribe and present results.
- Avoid storing raw media unless required; if stored, set explicit retention windows.
- Never log transcript text or user-provided content at info level; keep logs metadata-only.

### III. Reliability Over Cleverness
Transcription must be resilient to long-running operations and failures:
- Jobs are asynchronous and resumable (safe retries; idempotent job creation where feasible).
- Surface clear job states (queued/running/succeeded/failed) and stable job identifiers.
- Failures must be actionable (error codes/messages suitable for user display and support).

### IV. Contract-First API
The web app’s core capabilities must be accessible via stable API contracts:
- Define request/response schemas for job submission, status polling, and transcript retrieval.
- Backwards compatibility is the default; breaking changes require versioning.
- Minimum automated coverage includes schema validation + at least one end-to-end happy path.

### V. Observability and Simplicity
Keep the system diagnosable and minimal:
- Structured logs include correlation IDs (request_id, job_id) and timings.
- Track basic metrics: job throughput, job latency, failure rate, transcription duration.
- Prefer straightforward implementations; introduce new infrastructure only when justified.

## Technology Stack (Minimum Requirements)
- API: REST
- Backend runtime: Python + FastAPI
- Database: Postgres
- Background processing: required (queue/worker pattern); Celery/RQ or equivalent.
- Storage for uploaded media: S3-compatible object storage.
- Transcription engine: Whisper API (must be real, no mocked transcription).
- Frontend: minimal UI; must support job creation, status, and transcript viewing.
- Configuration: all secrets and provider credentials via environment variables (never committed).

## Security & Privacy
- Transport: HTTPS only.
- Authentication/authorization required for any non-public media, job creation, and transcript access.
- Secrets (API keys, tokens) must not be committed; use environment configuration.
- Storage encryption at rest where supported by the platform/provider.
- Retention: define and document retention for transcripts and any stored media; support deletion.

## Development Workflow & Quality Gates
- Every change includes tests appropriate to the layer (unit tests for pure logic; integration tests for API/job flow).
- API/schema changes require updating contract tests.
- CI must run lint + typecheck (if applicable) + tests before merge.
- User-visible behavior changes require updating product/README docs.

## Governance
This constitution supersedes other practices for this repo.

Amendments must include:
- The updated text.
- Rationale and impact.
- Migration/rollout plan if behavior or contracts change.

All PRs must confirm:
- No transcript/user content leaked into logs.
- Job and API contracts remain stable or are versioned.
- Data retention/deletion behavior is unchanged or documented.

**Version**: 1.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-12
