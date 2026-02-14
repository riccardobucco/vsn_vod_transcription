
# Tasks: VOD Transcription Utility

**Input**: Design documents from `/specs/001-vod-transcription-utility/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Notes**
- Project structure is defined in `specs/001-vod-transcription-utility/plan.md` (FastAPI SSR app in `app/`, Celery worker in `worker/`).
- Automated tests are included because the feature spec contains a mandatory “User Scenarios & Testing” section and the implementation plan calls for pytest + contract validation.

## Format: `- [ ] T### [P?] [US#?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US#]**: Which user story this task belongs to (US1/US2/US3)
- All task lines include the primary file path(s) they touch

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the repo scaffolding, dependency manifests, and container entrypoints.

- [ ] T001 Create application skeleton directories in app/ and worker/ (app/, worker/, migrations/, tests/)
- [ ] T002 Initialize Python project metadata and dependencies in pyproject.toml (Python 3.13+, FastAPI, Jinja2, SQLAlchemy, Alembic, Celery, redis, minio, openai, httpx, pytest)
- [ ] T003 [P] Add Docker Compose skeleton services in docker-compose.yml (app, worker, beat, postgres, redis, minio, logto)
- [ ] T004 [P] Create app container image definition in docker/Dockerfile.app
- [ ] T005 [P] Create worker/beat container image definition in docker/Dockerfile.worker
- [ ] T006 [P] Add environment variable template in .env.example (APP_BASE_URL, DATABASE_URL, REDIS_URL, MINIO_*, OPENAI_*, LOGTO_*)
- [ ] T007 [P] Scaffold FastAPI entrypoint in app/main.py (app instance, routers mount, template/static setup)
- [ ] T008 [P] Scaffold Celery app in worker/celery_app.py (Redis broker/backend)
- [ ] T009 [P] Add Tailwind build setup in package.json (tailwindcss CLI) and tailwind.config.js
- [ ] T010 [P] Add minimal base templates in app/templates/login.html and app/templates/dashboard.html
- [ ] T011 [P] Add minimal static placeholders in app/static/app.css and app/static/tailwind.css

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must exist before implementing any user story.

- [ ] T012 Create typed settings loader in app/config.py (env vars, defaults, validation)
- [ ] T013 Implement structured logging utilities in app/logging.py (request_id, job_id, no transcript text at info)
- [ ] T014 [P] Add API error response helpers in app/api/errors.py (ErrorResponse shape + HTTPException mapping)
- [ ] T015 Add DB engine/session setup in app/db/session.py (SQLAlchemy engine, sessionmaker)
- [ ] T016 Add Alembic configuration in migrations/env.py and alembic.ini
- [ ] T017 Define ORM models in app/db/models.py (User, TranscriptionJob, TranscriptSegment per data-model.md)
- [ ] T018 Create initial Alembic migration in migrations/versions/001_init.py (tables + indexes)
- [ ] T019 Implement MinIO client wrapper in app/services/storage_minio.py (bucket ensure, put/get/delete by key)
- [ ] T020 Implement OpenAI Whisper client wrapper in app/services/openai_whisper.py (verbose_json segments, model whisper-1)
- [ ] T021 Implement auth/session storage in app/auth/session_store.py (server-side session id → Logto token state in Redis)
- [ ] T022 Implement Logto OIDC client in app/auth/logto_client.py (authorize URL, callback exchange, userinfo)
- [ ] T023 Implement auth routes in app/auth/routes.py (/login, /auth/callback, /logout)
- [ ] T024 Add auth dependency helpers in app/auth/deps.py (require_session; current_user creates/loads User row)
- [ ] T025 Implement health endpoint in app/api/health.py (GET /api/health, no auth)
- [ ] T026 Add API router wiring in app/api/__init__.py and mount under /api in app/main.py

**Checkpoint**: Foundation ready; user stories can proceed.

---

## Phase 3: User Story 1 — Secure Access & Dashboard Visibility (Priority: P1) 🎯 MVP

**Goal**: Require authentication and show a dashboard listing existing jobs with their current status and submission time.

**Independent Test**: Navigate to `/` unauthenticated → redirected to login; authenticate as Reviewer → dashboard loads and lists jobs (possibly empty).

### Tests (US1)

- [ ] T027 [P] [US1] Validate OpenAPI file parses in tests/contract/test_openapi_valid.py using specs/001-vod-transcription-utility/contracts/openapi.yaml
- [ ] T028 [P] [US1] Add API auth guard test for protected route in tests/integration/test_auth_guard.py (401 for /api/* without cookie)

### Implementation (US1)

- [ ] T029 [P] [US1] Implement jobs query service in app/services/jobs_service.py (list jobs for dashboard)
- [ ] T030 [US1] Implement list jobs endpoint in app/api/jobs.py (GET /api/jobs; auth required; returns {jobs: [...]})
- [ ] T031 [US1] Implement dashboard SSR route in app/routes/dashboard.py (GET /; requires auth; renders app/templates/dashboard.html)
- [ ] T032 [US1] Wire SSR routes in app/routes/__init__.py and include in app/main.py
- [ ] T033 [US1] Ensure unauthenticated SSR redirects to /login in app/auth/deps.py and unauthenticated API returns 401 JSON in app/auth/deps.py

**Checkpoint**: US1 complete and independently verifiable.

---

## Phase 4: User Story 2 — Submit VOD for Transcription (Upload or URL) (Priority: P2)

**Goal**: Submit a job via upload or URL, immediately receive confirmation, and process asynchronously to completion/failure.

**Independent Test**: Submit one upload + one URL; each appears on dashboard as queued/processing; closing the browser does not stop processing.

### Tests (US2)

- [ ] T034 [P] [US2] Add submission validation unit tests in tests/unit/test_submission_validation.py (format allowlist; URL validation)
- [ ] T035 [P] [US2] Add API test for POST /api/jobs (upload) in tests/integration/test_create_job_upload.py (returns 201 + status queued/processing)
- [ ] T036 [P] [US2] Add API test for POST /api/jobs (url) in tests/integration/test_create_job_url.py (returns 201 + status queued/processing)

### Implementation (US2)

- [ ] T037 [P] [US2] Implement media probe helpers in worker/media/ffprobe.py (duration_seconds; has_audio)
- [ ] T038 [P] [US2] Implement ffmpeg transcoding helper in worker/media/ffmpeg.py (extract audio; mp3 mono 16k; constrained bitrate)
- [ ] T039 [P] [US2] Implement URL download helper with SSRF protections in worker/media/downloader.py (scheme allowlist; deny private IP; timeouts; size limit)
- [ ] T040 [US2] Implement Celery task pipeline in worker/tasks.py (queued→processing→completed/failed; updates DB)
- [ ] T041 [US2] Implement transcription orchestration in app/services/transcription.py (persist segments; derive per-segment + overall confidence)
- [ ] T042 [US2] Implement create job endpoint in app/api/jobs.py (POST /api/jobs; multipart upload + JSON url; validate; enqueue Celery)
- [ ] T043 [US2] Update dashboard UI to include submission form in app/templates/dashboard.html (upload input + URL input)
- [ ] T044 [US2] Add job failure reason mapping in app/services/failures.py (human-readable messages for common failure codes)

**Checkpoint**: US2 complete; job submission + async processing works.

---

## Phase 5: User Story 3 — View Results & Export Standard Formats (Priority: P3)

**Goal**: For completed jobs, show time-coded segments with confidence indicators and allow TXT/SRT/VTT exports.

**Independent Test**: Open a completed job → see segments with timestamps + per-segment confidence + overall confidence; download TXT/SRT/VTT and verify basic validity.

### Tests (US3)

- [ ] T045 [P] [US3] Add API test for GET /api/jobs/{job_id}/transcript in tests/integration/test_get_transcript.py
- [ ] T046 [P] [US3] Add API test for exports (txt/srt/vtt) in tests/integration/test_exports.py (status 200; basic format markers)

### Implementation (US3)

- [ ] T047 [P] [US3] Implement export formatters in app/services/exports.py (to_txt, to_srt, to_vtt)
- [ ] T048 [US3] Implement transcript endpoint in app/api/jobs.py (GET /api/jobs/{job_id}/transcript; auth required)
- [ ] T049 [US3] Implement export endpoint in app/api/exports.py (GET /api/jobs/{job_id}/export/{format}; validates format)
- [ ] T050 [US3] Implement job detail SSR route in app/routes/job_detail.py (GET /jobs/{job_id}; renders app/templates/job_detail.html)
- [ ] T051 [P] [US3] Add job detail template in app/templates/job_detail.html (segments list + confidence + download links)
- [ ] T052 [US3] Wire job detail link from dashboard in app/templates/dashboard.html

**Checkpoint**: US3 complete; results view + exports work end-to-end for completed jobs.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Retention, operational hardening, and documentation alignment.

- [ ] T053 [P] Implement retention cleanup task in worker/tasks.py (daily delete jobs older than 30 days + MinIO objects)
- [ ] T054 [P] Add Celery beat schedule in worker/celery_app.py (daily retention task)
- [ ] T055 Add safer logging guarantees in app/logging.py (never log transcript text; keep logs metadata-only)
- [ ] T056 [P] Add quickstart verification notes to Candidate Assignment - VSN.md (docker compose + manual verification steps)
- [ ] T057 Ensure OpenAPI contract matches implementation in app/api/jobs.py and app/api/exports.py (response fields, status codes)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** → **Phase 2 (Foundational)** → **Phase 3+ (User Stories)** → **Phase 6 (Polish)**

### User Story Dependencies

- **US1 (P1)** depends on Foundational only.
- **US2 (P2)** can start after Foundational; it benefits from US1 for UI visibility but is not structurally blocked by it.
- **US3 (P3)** depends on US2 producing stored segments.

Recommended order (single developer): US1 → US2 → US3.

---

## Parallel Execution Examples

### US1

- T029 (app/services/jobs_service.py) and T031 (app/routes/dashboard.py) can be developed in parallel.

### US2

- T037 (worker/media/ffprobe.py), T038 (worker/media/ffmpeg.py), and T039 (worker/media/downloader.py) can be developed in parallel.

### US3

- T047 (app/services/exports.py) and T051 (app/templates/job_detail.html) can be developed in parallel.

---

## Implementation Strategy

### MVP First (US1)

1. Complete Setup + Foundational.
2. Implement US1 (auth barrier + dashboard list).
3. Validate the US1 independent test manually.

### Incremental Delivery

- Add US2 next (submission + async processing), then US3 (results + exports), then retention/hardening.
