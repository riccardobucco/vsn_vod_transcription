## Implementation Plan: Dashboard Submission UX

**Branch**: `002-dashboard-submission-ux` | **Date**: 2026-02-15 | **Spec**: specs/002-dashboard-submission-ux/spec.md
**Input**: Feature specification from `/specs/002-dashboard-submission-ux/spec.md`

## Summary

Replace the dashboard’s current raw-JSON submission behavior with a consistent, SSR-friendly UX:

- Successful job submissions (upload or URL) use Post/Redirect/Get (HTTP 303) and render a human-friendly confirmation state (with “Back to dashboard” and “View job details”).
- Submission failures render a friendly error page with a small “Details” area and a single recovery action.
- Job detail links that are missing or malformed render a “Job not found” page with HTTP 404 (never JSON / validation dumps).
- Upload submits show immediate “Uploading…” feedback with best-effort progress and prevent double submits.

Phase 0/1 artifacts:
- Research decisions: specs/002-dashboard-submission-ux/research.md
- Data model: specs/002-dashboard-submission-ux/data-model.md
- UX/route contract: specs/002-dashboard-submission-ux/contracts/openapi.yaml
- Verification quickstart: specs/002-dashboard-submission-ux/quickstart.md

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: FastAPI (SSR + REST), Jinja2 templates, TailwindCSS (build step), SQLAlchemy (async), Celery, Redis, MinIO client  
**Storage**: PostgreSQL (jobs/segments/users), Redis (server-side session store; Celery broker), MinIO (uploaded media)  
**Testing**: pytest (unit + integration + contract validation)  
**Target Platform**: Linux server (Docker Compose)  
**Project Type**: Web application (single FastAPI app: HTML routes + REST API in one service)  
**Performance Goals**: UX responsiveness: show “Uploading…” immediately; prevent duplicate submissions while upload is in-flight  
**Constraints**:
- Maintain existing minimal visual style (reuse current templates/header; no new design system).
- Avoid breaking `/api/*` JSON contracts; changes should be isolated to dashboard SSR behavior.
- Confirmation display data must come from server-side session/flash storage (not query params).
- “Job not found” must return HTTP 404 and must handle both missing job and malformed identifiers.
**Scale/Scope**: Low concurrency, stakeholder-driven usage; UX correctness over throughput

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Transcription Is a Verifiable Artifact — PASS
- This feature changes only submission UX and HTML error rendering; transcription artifacts and provenance remain unchanged.

### II. Data Minimization by Default — PASS
- Confirmation and error display data will store only minimal fields (job id, label, status; short error reason) in the existing server-side session store.
- No transcript text or user-provided media content will be logged as part of this UX work.

### III. Reliability Over Cleverness — PASS
- Post/Redirect/Get (303) prevents accidental resubmission on refresh.
- Duplicate submission prevention is explicit in the browser UI state (disabled controls) and avoids initiating multiple POSTs.

### IV. Contract-First API — PASS (no breaking changes)
- `/api/jobs` remains a JSON API for programmatic clients.
- Dashboard submission will use separate SSR endpoints (or content-negotiated behavior) so API clients are unaffected.
- SSR routes added/changed are captured as a small “UX/route contract” in specs/002-dashboard-submission-ux/contracts/openapi.yaml.

### V. Observability and Simplicity — PASS
- No new infrastructure.
- Existing request_id header remains; errors shown to users stay plain-language without stack traces.

No constitution violations are required for this feature.

**Post-Phase-1 Re-check**: PASS — Design keeps `/api/*` contracts stable, stores only minimal flash data server-side, and ensures HTML error/404 rendering for SSR routes.

## Project Structure

### Documentation (this feature)

```text
specs/002-dashboard-submission-ux/
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
│   ├── jobs.py
│   └── ...
├── routes/
│   ├── dashboard.py
│   └── job_detail.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── job_detail.html
│   └── login.html
├── static/
│   ├── app.css
│   └── tailwind.css
└── auth/
  ├── deps.py
  ├── routes.py
  └── session_store.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Implement this UX entirely within the existing FastAPI SSR app (`app/routes/*` + `app/templates/*`) with minimal, explicit changes to job submission and error rendering, while keeping the JSON API stable.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
