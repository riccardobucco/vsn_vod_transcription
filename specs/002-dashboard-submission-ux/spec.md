# Feature Specification: Dashboard Submission UX

**Feature Branch**: `002-dashboard-submission-ux`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: User description: "Improve the dashboard job submission experience so users never see raw JSON. On successful submission (upload or URL), show a confirmation page with navigation actions. On submission errors, show a friendly error page with a brief reason and a small details area. For invalid or missing job links, show a Job not found page. While uploading large files, show immediate uploading feedback (with progress when available) and prevent double submits."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - See confirmation after submitting a job (Priority: P1)

As a non-technical dashboard user, when I submit a transcription job (by upload or by URL), I want a clear confirmation page so I know the system accepted my request and where to go next.

**Why this priority**: This is the primary happy-path; it directly replaces confusing raw JSON with a clear, human-friendly confirmation.

**Independent Test**: Can be fully tested by submitting (a) an upload and (b) a URL and verifying the browser shows a confirmation page (not JSON) with correct content and navigation actions.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard with a valid video file selected, **When** I click “Upload & Transcribe”, **Then** I see a confirmation page stating the job was accepted (typically “Queued”) and I can navigate to “Back to dashboard” and “View job details”.
2. **Given** I am on the dashboard with a valid direct video URL entered, **When** I submit the URL for transcription, **Then** I see the same confirmation page pattern with the submitted item label and the two navigation actions.

---

### User Story 2 - See friendly error page on submission failure (Priority: P2)

As a dashboard user, when my job submission fails, I want a friendly error page that tells me what went wrong and how to recover.

**Why this priority**: Non-technical stakeholders should never need to interpret HTTP/JSON error payloads; a clear recovery path reduces confusion and support load.

**Independent Test**: Can be fully tested by triggering a known validation failure (for example: unsupported file type and/or file too large if size limits are enforced) and verifying the browser shows an error page with plain-language text and a single “Back to dashboard” action.

**Acceptance Scenarios**:

1. **Given** I attempt to submit an unsupported file format, **When** the submission is rejected, **Then** I see a friendly error page (not JSON) with a plain-language message and a small Details area that includes the specific reason.
2. **Given** a submission is rejected due to file size limits (if enforced), **When** I submit a too-large file, **Then** I see the same friendly error page pattern and can return to the dashboard.

---

### User Story 3 - Get a real “Job not found” page for invalid links (Priority: P3)

As a user following a job link, if the job does not exist or the link is malformed, I want a simple “Job not found” page so I understand the link can’t be used.

**Why this priority**: Broken or malformed links are common; the experience must remain human-friendly and consistent with the site.

**Independent Test**: Can be fully tested by visiting (a) a well-formed but non-existent job URL and (b) a malformed job identifier URL and verifying both show the Job not found page with a “Back to dashboard” action.

**Acceptance Scenarios**:

1. **Given** I visit a job URL for an identifier that does not exist, **When** the page loads, **Then** I see a “Job not found” page (not JSON) explaining the job doesn’t exist or the link is invalid, with a “Back to dashboard” action.
2. **Given** I visit a job URL with a malformed identifier, **When** the page loads, **Then** I see the same “Job not found” page (not a validation dump).

---

### User Story 4 - See upload feedback and prevent duplicate submits (Priority: P4)

As a user uploading a large file, I want immediate “Uploading…” feedback and protection against double-submitting so I can trust the submission is in progress.

**Why this priority**: Large uploads can appear frozen; immediate feedback reduces uncertainty and prevents accidental duplicate jobs.

**Independent Test**: Can be fully tested by uploading a sufficiently large file (or simulating slow network) and verifying the UI shows an uploading state immediately, disables submission controls, and handles failures by showing the friendly error page.

**Acceptance Scenarios**:

1. **Given** I start uploading a file from the dashboard, **When** I click “Upload & Transcribe”, **Then** I immediately see an “Uploading…” state and the submit action is disabled until the upload completes or fails.
2. **Given** upload progress information is available during submission, **When** the upload is in progress, **Then** I see a progress indicator reflecting progress (for example, percentage or a filled bar).
3. **Given** upload progress information is not available, **When** the upload is in progress, **Then** I see an indeterminate progress indicator.
4. **Given** the upload fails due to network interruption or server rejection, **When** the failure occurs, **Then** I am shown the friendly error page with a “Back to dashboard” action.

### Edge Cases

- Submission succeeds but the user refreshes after seeing the confirmation state (must not resubmit; may return to the normal dashboard state if confirmation flash data was already consumed).
- User double-clicks submit or presses Enter repeatedly during upload (should not create multiple submissions).
- Submission failure reason is available but verbose (Details area should remain small/contained and avoid technical noise).
- Invalid job identifier format (malformed) versus valid format but missing job (both should land on Job not found page).
- Upload is started but the user navigates away (system should not show raw JSON; navigation should behave consistently).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a user submits a transcription job from the dashboard via upload and the submission is accepted, the browser MUST display a human-friendly confirmation page (not raw JSON). This confirmation page MAY be the existing dashboard route re-rendered in a confirmation state.
- **FR-002**: When a user submits a transcription job from the dashboard via direct video URL and the submission is accepted, the browser MUST display the same confirmation page pattern (not raw JSON or alert-only feedback). This confirmation page MAY be the existing dashboard route re-rendered in a confirmation state.
- **FR-003**: The confirmation page MUST clearly state the job was accepted and has started (typically “Queued”).
- **FR-004**: The confirmation page MUST display a submitted item label (for example: filename for uploads or a derived label for URLs).
- **FR-005**: The confirmation page MUST provide two actions: “Back to dashboard” and “View job details” (linking to the existing job details page for the created job).
- **FR-019**: After a successful dashboard submission POST (upload or URL), the server MUST use Post/Redirect/Get: respond with an HTTP 303 redirect to a GET that renders the confirmation state (to avoid resubmission on refresh).
- **FR-020**: The confirmation GET MUST derive its display data (job id/label/status) from server-side session/flash storage (not URL query parameters).
- **FR-006**: If job creation fails when initiated from the dashboard flow (upload or URL), the browser MUST display a friendly error page (not JSON).
- **FR-007**: The friendly error page MUST use plain language and MUST include a small “Details” area containing the specific reason for failure (for example: allowed formats, or “file too large” when applicable).
- **FR-008**: The friendly error page MUST provide a single, obvious recovery action: “Back to dashboard”.
- **FR-009**: The friendly error page MUST avoid technical noise (no stack traces, no raw JSON blobs).
- **FR-010**: If a user opens a job details URL for a non-existent job, the browser MUST display a “Job not found” page (not JSON).
- **FR-011**: If a user opens a job details URL with an invalid/malformed job identifier, the browser MUST display the same “Job not found” page (not a validation/parsing dump).
- **FR-012**: The “Job not found” page MUST include: a clear title (“Job not found”), a brief explanation (“This job doesn’t exist, or the link is invalid.”), and a “Back to dashboard” action.
- **FR-018**: The “Job not found” page MUST return HTTP status code 404.
- **FR-013**: During upload submission, the dashboard MUST show an “Uploading…” state immediately after the user submits.
- **FR-014**: While an upload is in progress, the dashboard MUST disable the submit button (and any equivalent submission action) to prevent duplicate submissions.
- **FR-015**: During upload submission, the dashboard MUST show a progress indicator; if exact progress information is available it MUST show determinate progress, otherwise it MUST show indeterminate progress.
- **FR-016**: If an upload submission fails (network error or server rejection), the user MUST be shown the friendly error page described above.
- **FR-017**: The confirmation, friendly error, and job-not-found pages MUST use the existing site header/navigation and maintain the existing minimal visual style.

### Assumptions & Scope Boundaries

- The existing dashboard already supports creating transcription jobs by upload and by direct video URL.
- The existing job details page already exists and remains the single place to check job status.
- This feature adds only these user-facing pages: submission confirmation, friendly submission error, and job not found. These pages may be rendered via existing routes (for example, re-rendering the dashboard route) and do not necessarily require new URLs.
- This feature does not introduce new job states, filters, search, admin tooling, or changes to the job details page content.
- File size limits may or may not be enforced; if enforced and the server rejects a too-large upload, it is treated as a submission failure and must use the friendly error page.
- Upload progress is best-effort: if the user’s browser provides upload progress events, show determinate progress; otherwise show an indeterminate indicator.

## Clarifications

### Session 2026-02-15

- Q: For upload submissions, which progress behavior do you want? → A: Best-effort determinate: show real progress when the browser provides upload progress events; otherwise show indeterminate.
- Q: Should the confirmation page be a new dedicated route or can it be the existing dashboard page re-rendered? → A: It can be the existing dashboard page re-rendered.
- Q: What HTTP status should the “Job not found” page return? → A: Return HTTP 404 and render the “Job not found” page.
- Q: After a successful dashboard submission, should we use a 303 redirect to a GET (PRG) or render confirmation directly on the POST? → A: Use PRG: after successful POST, respond with 303 redirect to a GET that renders the confirmation state.
- Q: With PRG, how should the GET know what to display on the confirmation state (job id/label/status)? → A: Store confirmation data server-side (session/flash) and redirect to plain /dashboard; the GET reads flash data to render confirmation.

### Dependencies

- Job creation must return (directly or indirectly) a job identifier that can be used to link to the existing job details page.
- When job creation fails, the system must have (or derive) a user-appropriate reason string for the Details area (for example: allowed formats or size limit text).
- The web app must have server-side session/flash storage available to carry confirmation state across the 303 redirect.

### Key Entities *(include if feature involves data)*

- **Transcription Job**: A user-submitted request to transcribe a specific video; includes an identifier, a user-facing label, and a lifecycle status (for example: queued/processing/completed/failed).
- **Submission Source**: The input used to create a job (uploaded file or direct video URL), used for deriving the submitted item label shown to the user.
- **User-Facing Status Page**: A rendered page shown in the browser (confirmation, friendly error, job not found) that communicates outcome and navigation actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For dashboard job submission (upload and URL), 100% of successful submissions result in a rendered confirmation page in the browser; 0% of these flows show raw JSON.
- **SC-002**: For dashboard job submission failures (including unsupported format and file-too-large when enforced), 100% of failures result in the friendly error page; 0% show raw JSON error payloads.
- **SC-003**: For job links that are non-existent or malformed, 100% of visits result in the “Job not found” page; 0% show parsing/validation dumps or raw JSON.
- **SC-004**: Users see an “Uploading…” state within 0.5 seconds after initiating an upload submission, and the submit action remains disabled until the upload completes or fails.
- **SC-005**: While uploading, repeated attempts to submit do not create duplicate submissions (at most one submission is initiated per user action sequence while upload is in progress).
