# Phase 0 Research: VOD Transcription Utility

**Feature**: 001-vod-transcription-utility  
**Date**: 2026-02-14

## Decisions

### Authentication: Logto Cloud OIDC + app-managed session cookie

- Decision: Use Logto Cloud as the Identity Provider via OIDC redirect flow. The FastAPI app provides an application-managed `/login` page (SSR) that initiates the redirect-based sign-in. The app maintains its own secure session cookie (session id only) and stores Logto token state server-side.
- Rationale:
  - Meets spec requirement for an “application-managed login page” and “secure session cookie” without exposing OAuth tokens to the browser.
  - Aligns with the mandated stack (Logto) and standard OIDC best practice (redirect-based auth).
- Alternatives considered:
  - App-local username/password in env (no Logto): simpler but violates the defined stack and misses central auth management.
  - Cookie-storing tokens (Starlette session cookie): easy but leaks sensitive bearer tokens to the client (not acceptable).

### Preconfigured “Reviewer” account

- Decision: Provision a single Logto user (Reviewer) whose credentials are set via the Logto Cloud Console, but credentials are validated by Logto Cloud (not the app). The FastAPI app simply requires authenticated sessions.
- Rationale:
  - Satisfies FR-002 (preconfigured Reviewer) while keeping password handling inside Logto Cloud.
- Implementation note:
  - **Recommended**: Create the Reviewer user manually in the Logto Cloud Console (accounts are managed centrally in the cloud dashboard).
  - **Optional**: Provide `LOGTO_M2M_CLIENT_ID/SECRET` to allow a bootstrap step that creates/updates the Reviewer user via the Logto Management API.

### Media ingestion & storage

- Decision: Store uploaded videos (or downloaded URL videos) in MinIO (S3-compatible) under a per-job object key. Store derived audio (transcription input) as a separate object.
- Rationale:
  - Supports asynchronous processing and “return later” access.
  - Object storage fits large binary payloads better than Postgres.
- Alternatives considered:
  - Store only audio and discard original video immediately: better minimization, but makes debugging and re-export/retry harder.

### Format validation and duration limit

- Decision: Enforce initial format allowlist by extension + best-effort MIME, then validate by attempting to probe/decode with ffmpeg tooling in the worker. Enforce the 30-minute limit by computing duration via `ffprobe`.
- Rationale:
  - Extension checks are fast UX feedback; ffprobe/ffmpeg is the authoritative validator for corrupted or mislabeled files.
- Alternatives considered:
  - Pure-Python metadata parsing: fewer system deps but less reliable across containers/formats.

### OpenAI Whisper transcription approach (segments + timestamps)

- Decision: Use OpenAI’s Audio Transcriptions endpoint with `model="whisper-1"` and `response_format="verbose_json"` plus `timestamp_granularities=["segment"]` to obtain native segments with start/end times.
- Rationale:
  - Meets FR-012/FR-012a (native segments, time-coded).
  - `timestamp_granularities` support is specific to `whisper-1`.
- Alternatives considered:
  - `gpt-4o-transcribe` with `include=["logprobs"]`: provides token logprobs but (currently) only supports `json` output and not `verbose_json` segment timestamps.

### Handling OpenAI 25MB upload limit

- Decision: Always transcode extracted audio to a constrained bitrate (e.g., mono 16kHz MP3 at 48–64 kbps) before sending to OpenAI, targeting <25MB for the 30-minute max.
- Rationale:
  - 30 minutes at 64 kbps ≈ 14.4 MB, safely under the limit.
- Alternatives considered:
  - Chunking audio by size/time: workable but complicates timestamp continuity and retries. Kept as fallback if transcoding still exceeds limits.

### Confidence indicators

- Decision: Use per-segment confidence derived from Whisper’s verbose segment metadata when available (commonly `avg_logprob`). Convert to a 0–1 score via $p=\exp(\text{avg\_logprob})$ and present a simple indicator (e.g., Low/Med/High). Overall confidence is a duration-weighted average of segment scores.
- Rationale:
  - Produces a reproducible, auditable metric without inventing re-segmentation.
- Alternatives considered:
  - Heuristics from text (punctuation, filler words): not grounded in engine signal.

### Retention & deletion (30 days)

- Decision: Implement retention as a daily Celery Beat task that deletes expired jobs (older than 30 days) and cascades deletions of transcript segments and associated MinIO objects.
- Rationale:
  - Matches spec (FR-019) and constitution (explicit retention, deletion support).
- Alternatives considered:
  - DB-native cron/partition TTL: powerful but adds complexity compared to one scheduled task.

### API contracts & SSR

- Decision: Provide a stable REST API (JSON + file downloads) for job submission/status/transcript/export, in addition to SSR routes that render the UI using Jinja2.
- Rationale:
  - Constitution mandates contract-first API; SSR satisfies the frontend strategy.

## Key Risks / Mitigations

- Risk: Logto Cloud account configuration.
  - Mitigation: Logto Cloud Console provides a straightforward UI for creating applications and users. Optional automated bootstrap via M2M credentials is supported.
- Risk: ffmpeg availability in worker containers.
  - Mitigation: Use an image that includes ffmpeg or install it in the worker Dockerfile; document as required.
- Risk: URL ingestion SSRF and large downloads.
  - Mitigation: Restrict schemes to `http/https`, apply timeouts, enforce max content length, and deny private IP ranges by default.

