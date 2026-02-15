---

description: "Task list for Dashboard Submission UX feature implementation"
---

# Tasks: Dashboard Submission UX

**Input**: Design documents from `/specs/002-dashboard-submission-ux/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Only include test tasks if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create SSR submission endpoints in app/routes/dashboard.py
- [ ] T002 Initialize TailwindCSS build step in tailwind.config.js
- [ ] T002b Create app/static/app.js and link in app/templates/base.html
- [ ] T003 [P] Configure pytest for contract/integration/unit tests in tests/
- [ ] T004 [P] Setup Redis session/flash storage in app/auth/session_store.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T005 Extend job creation logic to support SSR inputs in app/services/jobs_service.py
- [ ] T006 [P] Ensure TranscriptionJob model supports required fields in app/db/models.py
- [ ] T007 [P] Add error handling for SSR routes in app/api/errors.py
- [ ] T008 Configure session flash consumption logic in app/auth/session_store.py
- [ ] T009 Setup base dashboard template for confirmation/error/not-found states in app/templates/dashboard.html

---

## Phase 3: User Story 1 - Confirmation after submitting a job (Priority: P1) 🎯 MVP

**Goal**: Show a confirmation page after successful job submission (upload or URL).

**Independent Test**: Submit a job (upload or URL) and verify the browser shows a confirmation page (not JSON) with correct content and navigation actions.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Add SubmissionConfirmationFlash logic in app/auth/session_store.py
- [ ] T011 [P] [US1] Implement confirmation state rendering in app/routes/dashboard.py
- [ ] T012 [US1] Update dashboard.html to show confirmation panel with job id, label, status, and navigation actions
- [ ] T013 [US1] Add PRG (303 redirect) logic for SSR submission endpoints in app/routes/dashboard.py
- [ ] T014 [US1] Add contract test for confirmation flow in tests/contract/test_openapi_schema_validation.py
- [ ] T015 [US1] Add integration test for confirmation page in tests/integration/test_dashboard_confirmation.py

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Friendly error page on submission failure (Priority: P2)

**Goal**: Show a friendly error page with a brief reason and recovery action when submission fails.

**Independent Test**: Trigger a known validation failure and verify the browser shows an error page with plain-language text and a single “Back to dashboard” action.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Add SubmissionErrorViewModel logic in app/auth/session_store.py
- [ ] T017 [P] [US2] Implement error state rendering in app/routes/dashboard.py
- [ ] T018 [US2] Update dashboard.html to show error panel with message, details, and recovery action
- [ ] T019 [US2] Add contract test for error flow in tests/contract/test_openapi_schema_validation.py
- [ ] T020 [US2] Add integration test for error page in tests/integration/test_dashboard_error.py

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Job not found page for invalid links (Priority: P3)

**Goal**: Show a “Job not found” page for non-existent or malformed job links.

**Independent Test**: Visit a well-formed but non-existent job URL and a malformed job identifier URL; verify both show the Job not found page with a “Back to dashboard” action.

### Implementation for User Story 3

- [ ] T021 [P] [US3] Add job_id parsing and not-found logic in app/routes/job_detail.py
- [ ] T022 [US3] Implement not-found state rendering in app/routes/job_detail.py
- [ ] T023 [US3] Update job_detail.html to show not-found page with title, explanation, and recovery action
- [ ] T024 [US3] Add contract test for not-found flow in tests/contract/test_openapi_schema_validation.py
- [ ] T025 [US3] Add integration test for not-found page in tests/integration/test_job_not_found.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Upload feedback and prevent duplicate submits (Priority: P4)

**Goal**: Show immediate “Uploading…” feedback and prevent duplicate submissions during file upload.

**Independent Test**: Upload a large file and verify the UI shows an uploading state immediately, disables submission controls, and handles failures by showing the friendly error page.

### Implementation for User Story 4

- [ ] T026 [P] [US4] Add JS upload interception and progress logic in app/static/app.js
- [ ] T027 [US4] Update dashboard.html to show uploading/progress indicator and disable submit controls
- [ ] T028 [US4] Add integration test for upload feedback (verify <0.5s "Uploading..." state) in tests/integration/test_dashboard_upload_feedback.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T029 [P] Documentation updates in AI_LOG.md
- [ ] T030 Code cleanup and refactoring in app/
- [ ] T031 Performance optimization across all stories in app/
- [ ] T032 [P] Additional unit tests in tests/unit/
- [ ] T033 Security hardening in app/
- [ ] T034 Run quickstart.md validation in specs/002-dashboard-submission-ux/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

- T010 [P] [US1] Add SubmissionConfirmationFlash logic in app/auth/session_store.py
- T011 [P] [US1] Implement confirmation state rendering in app/routes/dashboard.py

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
