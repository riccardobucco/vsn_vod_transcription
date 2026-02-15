---

description: "Task list for Dashboard Submission UX implementation"
---

# Tasks: Dashboard Submission UX

**Input**: Design documents from `/specs/002-dashboard-submission-ux/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Required per constitution; see Phase 8 for unit/integration/contract coverage and end-to-end happy path.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and shared utilities

- [ ] T001 Add session flash helpers for confirmation/error payloads in app/auth/flash.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T002 Extract job creation logic into a shared submission service in app/services/submission_service.py (from app/api/jobs.py)
- [ ] T003 Update app/api/jobs.py to use submission_service helpers while preserving JSON API responses

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - See confirmation after submitting a job (Priority: P1) 🎯 MVP

**Goal**: Successful upload/URL submissions render a confirmation state via PRG instead of raw JSON.

**Independent Test**: Submit one upload and one URL on the dashboard and verify a confirmation page (not JSON) with “Back to dashboard” and “View job details”.

### Implementation for User Story 1

- [ ] T004 [P] [US1] Implement SSR submission routes for /submit/upload and /submit/url with PRG + confirmation flash in app/routes/submissions.py
- [ ] T005 [P] [US1] Register the submissions router in app/main.py
- [ ] T006 [P] [US1] Pop confirmation flash and pass it to the template in app/routes/dashboard.py
- [ ] T007 [US1] Render confirmation state (status, label, actions) in app/templates/dashboard.html
- [ ] T008 [US1] Point dashboard forms at SSR endpoints (/submit/upload, /submit/url) in app/templates/dashboard.html

**Checkpoint**: User Story 1 confirmation flow works independently

---

## Phase 4: User Story 2 - See friendly error page on submission failure (Priority: P2)

**Goal**: Submission failures show a friendly HTML error page with a brief message and details.

**Independent Test**: Trigger an invalid upload or URL and verify the friendly error page (no JSON) with a single “Back to dashboard” action.

### Implementation for User Story 2

- [ ] T009 [P] [US2] Create the friendly error template in app/templates/submission_error.html
- [ ] T010 [P] [US2] Add submission error mapping helpers in app/services/submission_errors.py
- [ ] T011 [US2] Render submission_error.html with HTTP 400 on failures in app/routes/submissions.py

**Checkpoint**: User Story 2 error page renders independently

---

## Phase 5: User Story 3 - Get a real “Job not found” page for invalid links (Priority: P3)

**Goal**: Invalid or missing job links render an HTML 404 page instead of JSON/validation dumps.

**Independent Test**: Visit /jobs/not-a-uuid and /jobs/00000000-0000-0000-0000-000000000000 and verify the Job not found page with HTTP 404.

### Implementation for User Story 3

- [ ] T012 [P] [US3] Create the job-not-found template in app/templates/job_not_found.html
- [ ] T013 [US3] Parse job_id manually and render job_not_found.html with 404 in app/routes/job_detail.py

**Checkpoint**: User Story 3 not-found handling works independently

---

## Phase 6: User Story 4 - See upload feedback and prevent duplicate submits (Priority: P4)

**Goal**: Uploads show immediate “Uploading…” feedback, progress, and prevent double submits.

**Independent Test**: Upload a large file and verify immediate uploading UI, disabled submit, progress indicator, and friendly error page on failure.

### Implementation for User Story 4

- [ ] T014 [US4] Add upload-state UI elements (status text + progress bar) and disabled-state styling in app/templates/dashboard.html
- [ ] T015 [US4] Intercept upload submit with XHR for progress, prevent double submits, follow 303 redirect on success, and render HTML error responses in app/templates/dashboard.html

**Checkpoint**: User Story 4 upload feedback works independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T016 [P] Verify SSR route behavior matches specs/002-dashboard-submission-ux/contracts/openapi.yaml and update the contract if needed
- [ ] T017 Run the quickstart verification checklist in specs/002-dashboard-submission-ux/quickstart.md and note any follow-up fixes
- [ ] T024 Update README (and/or product docs) to describe the new SSR submission UX and error/not-found pages

---

## Phase 8: Tests (Required by Constitution)

**Purpose**: Automated coverage for SSR UX changes and contract validation

- [ ] T018 Add unit tests for flash helpers in tests/unit/test_flash.py
- [ ] T019 Add integration tests for SSR submission PRG confirmation (upload + URL) in tests/integration/test_dashboard_submission_ssr.py
- [ ] T020 Add integration tests for friendly error page on invalid upload/URL in tests/integration/test_submission_error_ssr.py
- [ ] T021 Add integration tests for job-not-found 404 (malformed + missing) in tests/integration/test_job_detail_404.py
- [ ] T022 Add contract/schema validation test for specs/002-dashboard-submission-ux/contracts/openapi.yaml in tests/contract/test_dashboard_submission_contract.py
- [ ] T023 Add end-to-end happy path test for dashboard submit → confirmation render in tests/integration/test_dashboard_happy_path.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational - no dependencies on other stories
- **User Story 2 (P2)**: Starts after Foundational - independent of other stories
- **User Story 3 (P3)**: Starts after Foundational - independent of other stories
- **User Story 4 (P4)**: Starts after Foundational - independent of other stories

### Within Each User Story

- Shared utilities before route/template changes
- Route logic before template wiring
- UI changes before manual verification

---

## Parallel Examples Per User Story

### User Story 1

```bash
Task: "Implement SSR submission routes for /submit/upload and /submit/url with PRG + confirmation flash in app/routes/submissions.py"
Task: "Pop confirmation flash and pass it to the template in app/routes/dashboard.py"
```

### User Story 2

```bash
Task: "Create the friendly error template in app/templates/submission_error.html"
Task: "Add submission error mapping helpers in app/services/submission_errors.py"
```

### User Story 3

```bash
Task: "Create the job-not-found template in app/templates/job_not_found.html"
```

### User Story 4

```bash
Task: "Add upload-state UI elements (status text + progress bar) and disabled-state styling in app/templates/dashboard.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. User Story 1 → Test independently → Demo MVP
3. User Story 2 → Test independently → Demo
4. User Story 3 → Test independently → Demo
5. User Story 4 → Test independently → Demo

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. After Foundational:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4

---

## Notes

- [P] tasks = different files, no dependencies
- Each user story is independently testable using quickstart scenarios
- Avoid exposing raw JSON in SSR flows
