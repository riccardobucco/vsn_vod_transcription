# Phase 1 — Data Model (Dashboard Submission UX)

This feature is primarily SSR UX/state handling. No new database tables are required.

## Existing Entities (unchanged)

### `TranscriptionJob` (PostgreSQL)

- Fields (relevant):
  - `id: UUID`
  - `user_id: UUID`
  - `source_type: enum(upload|url)`
  - `source_label: str`
  - `status: enum(queued|processing|completed|failed)`
  - `failure_message: str | null`
  - timestamps (`created_at`, `updated_at`, ...)

## New Logical Entities (session/flash only)

These are not persisted to Postgres; they are stored in the existing server-side session store (Redis) alongside auth session data.

### `SubmissionConfirmationFlash`

- Stored under a single key, e.g. `session.flash.confirmation`
- Lifetime: consumed on the next `GET /` (read-and-clear). If not consumed, it expires with the session TTL (24h).
- Fields:
  - `job_id: UUID` — used to link to `/jobs/{job_id}`
  - `label: str` — filename for uploads, derived label for URLs
  - `status: str` — display value, typically `queued`

Validation rules:
- `job_id` must be a valid UUID.
- `label` must be present and reasonably short (UI text; do not store full URL).
- `status` must be one of the known job states.

### `SubmissionErrorViewModel`

- Not stored long-term; usually rendered immediately on the error page.
- If stored for PRG alignment, store under `session.flash.error` and consume on first render.
- Fields:
  - `message: str` — plain-language summary (non-technical)
  - `details: str` — small details area content (specific reason; no stack traces; no raw JSON)

Validation rules:
- `message` must be generic and user-safe.
- `details` must be bounded in size and should be derived from known validation failures (allowed formats, file too large, invalid URL scheme, etc.).

## State Transitions

### Dashboard view state

- Normal state: shows submission forms + job list.
- Confirmation state: shows confirmation panel (or page-like section) driven by `SubmissionConfirmationFlash`.
  - After rendering once, the flash is cleared so refresh returns to normal dashboard state (no resubmission).
- Uploading state (client-side): immediate `Uploading…` indicator and disabled submit controls until XHR completes or fails.

### Job detail route state

- Valid UUID + job exists: render job details.
- Valid UUID + job missing: render “Job not found” page with 404.
- Malformed UUID: render “Job not found” page with 404 (not a validation dump).
