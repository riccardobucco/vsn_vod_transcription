# Phase 1 — Quickstart Verification (Dashboard Submission UX)

Goal: Verify that dashboard submissions never show raw JSON, successful submissions render a confirmation state via PRG, failures render a friendly error page, and job links render a proper HTML 404 page.

## Prerequisites

- Stack configured and running (same as repo README): Postgres, Redis, MinIO, worker, and the app.
- A Logto reviewer user you can log in with.

## Start the stack

- `docker compose up -d`
- Confirm health: `curl http://localhost:7200/api/health`

## Verify happy paths

### 1) URL submission → confirmation

1. Open `http://localhost:7200/` (or your deployed URL).
2. Sign in.
3. Submit a valid direct MP4 URL.
4. Expected:
   - Browser renders a confirmation state/page (no JSON).
   - Confirmation shows status (typically `Queued`) and a label.
   - Actions present: “Back to dashboard” and “View job details”.
5. Refresh the browser on the confirmation state.
   - Expected: no resubmission occurs (PRG), and the dashboard returns to normal state after the flash data is consumed.

### 2) Upload submission → uploading feedback + confirmation

1. On the dashboard, choose an `.mp4`, `.mov`, or `.mkv` file.
2. Click “Upload & Transcribe”.
3. Expected immediately:
   - UI shows “Uploading…”
   - Submit is disabled (double-submit prevented)
   - Progress indicator shows determinate progress when available, otherwise indeterminate
4. Expected after completion:
   - Browser navigates to the confirmation state/page (no JSON).

## Verify error paths

### 3) Submission failure → friendly error page

1. Attempt to upload an unsupported format (e.g. `.txt`) or submit an invalid URL scheme (e.g. `ftp://...`).
2. Expected:
   - A friendly error page is rendered (no JSON, no stack trace).
   - Plain-language message.
   - A small “Details” area contains the specific reason.
   - A single “Back to dashboard” action.

## Verify job not found

### 4) Malformed job id → HTML 404

1. Visit `http://localhost:7200/jobs/not-a-uuid`.
2. Expected:
   - “Job not found” HTML page.
   - HTTP status code 404.
   - “Back to dashboard” action.

### 5) Non-existent job id → HTML 404

1. Visit `http://localhost:7200/jobs/00000000-0000-0000-0000-000000000000`.
2. Expected: same as above.

## Notes

- This quickstart is for reviewer verification of UX behavior. It is not a load/performance test.
