# Phase 0 — Research (Dashboard Submission UX)

This document resolves technical clarifications and records decisions for implementing the “Dashboard Submission UX” feature.

## Decision 1: Keep `/api/jobs` as JSON; add dedicated SSR submission endpoints

- Decision: Dashboard submissions will POST to SSR endpoints (e.g. `POST /submit/upload` and `POST /submit/url`) which perform job creation and then use PRG (303) to redirect to `GET /` for the confirmation state.
- Rationale:
  - The dashboard currently posts the upload form directly to `POST /api/jobs`, which returns JSON and causes the browser to show raw JSON.
  - Preserves the existing REST API behavior and avoids breaking contract tests or any non-browser clients.
  - Makes it easy to return HTML error pages for the dashboard flows.
- Alternatives considered:
  - Change `POST /api/jobs` to content-negotiate (HTML redirect vs JSON) based on `Accept` header — rejected because browser form submits often send broad `Accept` headers and the behavior can be ambiguous; also increases risk of breaking API clients.
  - Keep posting to `POST /api/jobs` and wrap everything in frontend JS — rejected because the spec requires server-side PRG and server-side flash data for confirmation.

## Decision 2: Store confirmation data in the existing server-side session store (Redis)

- Decision: Store a small “flash” payload inside the Redis session data keyed by `sid` (already used by auth). The dashboard `GET /` will read-and-clear the flash to render the confirmation state.
- Rationale:
  - Meets FR-020 (“derive display data from server-side session/flash storage”).
  - Avoids query parameters and keeps UX consistent on refresh (PRG).
  - Keeps stored data minimal and bounded in size.
- Alternatives considered:
  - Put the flash payload in the signed cookie session — rejected because the app already treats the cookie as a session-id carrier and keeps user data in Redis; also cookie size limits and security posture are better with server-side storage.
  - Add a database table for transient flashes — rejected as unnecessary infrastructure for a one-request UX state.

## Decision 3: Handle malformed job identifiers as HTML 404 (not FastAPI 422 JSON)

- Decision: Update the SSR job detail route signature to accept `job_id: str` and manually parse it as a UUID. On parse failure, render the “Job not found” page with HTTP 404.
- Rationale:
  - With `job_id: uuid.UUID`, FastAPI raises a validation error for malformed IDs, typically producing a JSON 422 error response, which violates FR-011.
  - Manual parsing keeps the behavior deterministic and allows rendering the correct HTML page.
- Alternatives considered:
  - Install a global exception handler for `RequestValidationError` and map specific paths to HTML 404 — rejected as broader blast radius and harder to scope safely.

## Decision 4: Upload progress via `XMLHttpRequest` (best-effort determinate)

- Decision: Intercept the upload form submit with JS and submit the file via `XMLHttpRequest` so we can listen to `xhr.upload.onprogress`. Show a determinate progress indicator when computable, otherwise indeterminate.
- Rationale:
  - Standard HTML form submits do not reliably expose upload progress events.
  - XHR provides the most compatible progress API for classic SSR pages without introducing heavier front-end tooling.
- Alternatives considered:
  - `fetch()` with streams — rejected due to inconsistent upload progress support across browsers and more complex implementation.
  - No JS / rely on browser spinner — rejected because FR-013/FR-015 explicitly require immediate feedback + progress indicator.

## Decision 5: Error and not-found are rendered by dedicated HTML templates

- Decision: Add templates for:
  - Friendly submission error page (plain language, small Details area, back action)
  - Job not found page (title, explanation, back action, 404)
  The pages will reuse the existing header/navigation styles.
- Rationale:
  - Keeps logic simple and avoids mixing error layout into the main dashboard template.
  - Ensures we never show raw JSON or a default exception page.
- Alternatives considered:
  - Re-render the dashboard with an inline error banner — rejected because the spec asks for a friendly error “page” and because some errors occur after PRG boundaries.

## Notes / Non-goals

- This feature does not change job state machine, background processing, API schemas, or transcript rendering.
- No new UI themes/components beyond existing minimal Tailwind usage.
