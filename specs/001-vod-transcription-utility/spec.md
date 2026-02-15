# Feature Specification: VOD Transcription Utility

**Feature Branch**: `001-vod-transcription-utility`  
**Created**: 2026-02-12  
**Status**: Draft  
**Input**: Private web utility for submitting VOD files (upload or direct URL) and receiving time-coded transcripts with confidence indicators and export formats.

## Clarifications

### Session 2026-02-12

- Q: What authentication method should the utility use? → A: App-managed login route that delegates authentication to Logto Cloud (OIDC) and establishes a secure session cookie; at least one pre-provisioned "Reviewer" identity (created in Logto Cloud Console; no self-service registration).
- Q: What VOD duration should be explicitly supported in the initial release? → A: Up to 30 minutes.
- Q: What input video formats should be supported initially? → A: MP4, MOV, MKV.
- Q: What retention policy should apply to jobs and outputs? → A: Auto-delete after 30 days.
- Q: How should transcript segments be determined? → A: Use the transcription engine’s native segments; do not force fixed-length or sentence re-segmentation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Access & Dashboard Visibility (Priority: P1)

As a stakeholder (Reviewer), I want a secure login barrier and a simple dashboard so I can access the tool immediately and see what has happened to previously submitted videos.

**Why this priority**: Without secure access and a clear dashboard, stakeholders cannot use or trust the utility.

**Independent Test**: Can be fully tested by logging in as the pre-configured Reviewer and confirming the dashboard loads and shows job status information.

**Acceptance Scenarios**:

1. **Given** I am not authenticated, **When** I navigate to the application, **Then** I am required to log in before seeing the dashboard.
2. **Given** I have valid Reviewer credentials, **When** I log in, **Then** I land on the dashboard and can see a list of submitted jobs (if any).
3. **Given** I am authenticated, **When** my session expires or I log out, **Then** I must authenticate again to access the dashboard.

---

### User Story 2 - Submit VOD for Transcription (Upload or URL) (Priority: P2)

As a Reviewer, I want to submit a VOD by uploading a file or pasting a direct link so that I can start a transcription job without needing to keep the browser open.

**Why this priority**: Job submission is the core input to the factory workflow; without it there is no value delivered.

**Independent Test**: Can be tested by submitting one job via upload and one via URL and confirming each job is accepted, visible on the dashboard, and progresses through states asynchronously.

**Acceptance Scenarios**:

1. **Given** I am authenticated, **When** I upload a supported video file, **Then** the system confirms receipt and creates a new job in a "Queued" or "Processing" state.
2. **Given** I am authenticated, **When** I paste a direct, downloadable video URL and submit, **Then** the system confirms receipt and creates a new job in a "Queued" or "Processing" state.
3. **Given** I submit a job successfully, **When** I close my browser and return later, **Then** I can see the job's latest state on the dashboard.
4. **Given** a submitted job fails, **When** I view it on the dashboard, **Then** it shows a "Failed" state and a basic, human-readable reason.

---

### User Story 3 - View Results & Export Standard Formats (Priority: P3)

As a Reviewer, I want completed jobs to show time-coded transcript segments and confidence indicators, and I want to export the transcription as plain text and subtitle formats so I can use the output for captioning and downstream workflows.

**Why this priority**: The utility succeeds only if users can retrieve usable, portable outputs after processing completes.

**Independent Test**: Can be tested by opening a completed job, verifying segments and confidence are present, and downloading each export format.

**Acceptance Scenarios**:

1. **Given** a job is in the "Completed" state, **When** I open the job's detail view, **Then** I see the transcript split into time-coded segments with start and end timestamps.
2. **Given** a job is completed, **When** I view the transcript, **Then** I can see a confidence indicator for each segment and an overall confidence summary.
3. **Given** a job is completed, **When** I choose an export format, **Then** I can download a file in that format (plain text, SRT, and VTT).

### Edge Cases

- Unsupported video format is submitted (upload or URL).
- URL is invalid, not directly downloadable, or requires authentication.
- Uploaded file is corrupted, has no audio track, or cannot be decoded.
- Network interruption occurs during upload; user retries submission.
- Very large files or long-duration VODs cause extended processing times.
- Submitted VOD exceeds the supported duration limit.
- Job fails due to timeouts or resource limits and must show a basic reason.
- Multiple submissions of the same source happen unintentionally; jobs must remain distinct and trackable.

## Requirements *(mandatory)*

### Functional Requirements

Functional requirements are considered satisfied when all acceptance scenarios in the User Scenarios & Testing section pass.

- **FR-001**: System MUST require authentication to access the application via an application-managed login flow (delegates to Logto Cloud as the OIDC provider).
- **FR-002**: System MUST provide at least one pre-provisioned "Reviewer" identity that can sign in without self-service registration (provisioned in Logto Cloud Console).
- **FR-002a**: After login, the system MUST maintain an authenticated session via a secure session cookie.
- **FR-003**: System MUST present a dashboard after login that answers: (a) what jobs exist, (b) what state each job is in, and (c) how to submit a new job.
- **FR-004**: Users MUST be able to submit a transcription job by uploading a supported video file from their computer.
- **FR-005**: Users MUST be able to submit a transcription job by pasting a direct link (URL) to a video file hosted elsewhere.
- **FR-006**: System MUST validate job submissions and provide clear, human-readable feedback when submission is rejected (e.g., unsupported format, invalid URL).
- **FR-006a**: The system MUST support VODs up to 30 minutes in duration; submissions that exceed this limit MUST be rejected or marked Failed with a clear reason.
- **FR-006b**: The system MUST accept MP4, MOV, and MKV video inputs; other formats MUST be rejected or marked Failed with a clear reason.
- **FR-007**: When a submission is accepted, the system MUST immediately confirm receipt and indicate that processing has started.
- **FR-008**: System MUST process transcription asynchronously such that users are not required to keep a browser tab open for the job to continue.
- **FR-009**: Each job MUST have a clearly visible lifecycle state: Queued, Processing, Completed, or Failed.
- **FR-010**: The dashboard MUST show each job's current state and the time the job was submitted.
- **FR-011**: For Failed jobs, the system MUST display a basic failure reason suitable for a non-technical user (e.g., corrupted file, unreachable URL, timeout).
- **FR-012**: For Completed jobs, the system MUST provide a job detail view that includes the transcription broken into time-coded segments with start and end timestamps.
- **FR-012a**: Transcript segmentation MUST use the transcription engine’s native segments; the system MUST NOT force fixed-length chunking or sentence-based re-segmentation.
- **FR-013**: Each time-coded segment MUST include the segment text.
- **FR-014**: The system MUST provide a confidence indicator for transcription quality (at minimum per segment, and optionally an overall summary).
  - Confidence representation MUST be:
    - Per segment: a categorical `confidence_label` in {low, medium, high}
    - Overall: an `overall_confidence_label` in {low, medium, high}
  - Confidence labels MUST be deterministically derived from Whisper segment metadata (e.g., avg_logprob) using documented thresholds in the implementation.
- **FR-015**: Users MUST be able to export and download the completed transcription as a plain text file (.txt).
- **FR-016**: Users MUST be able to export and download the completed transcription as subtitle files in SRT (.srt) and WebVTT (.vtt).
- **FR-017**: Users MUST be able to access completed outputs and exports after returning later (without resubmitting the original source).
- **FR-018**: The system MUST keep a visible record of jobs on the dashboard so users can track historical submissions and outcomes.
- **FR-019**: The system MUST retain jobs and completed outputs for 30 days after submission, after which they MUST be automatically deleted and no longer accessible.

### Key Entities *(include if feature involves data)*

- **User**: A person who can sign in; includes at minimum a "Reviewer" persona used by stakeholders.
- **Transcription Job**: A submitted unit of work representing a single VOD ingestion and transcription attempt; includes submission method (upload vs URL), source label (filename or URL), submission time, current state, and failure reason (if any).
- **Transcript Segment**: A time-coded piece of the transcript for a job; includes start time, end time, text, and confidence indicator.
- **Export**: A downloadable representation of a completed job's transcript in a specific format (TXT, SRT, VTT).

### Assumptions

- The utility is VOD-only (no live streaming ingestion).
- The initial release targets stakeholder usage via a pre-configured Reviewer login and does not include public registration.
- Job history and completed outputs are retained for 30 days and then auto-deleted.

### Out of Scope

- Live stream transcription.
- Manual transcript editing within the utility.
- Translation, summarization, or other post-processing beyond transcription and export.
- Advanced user management (self-service registration, role management, billing).
- Search, tagging, or analytics beyond basic job tracking.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Reviewer can sign in and reach the dashboard in under 30 seconds.
- **SC-002**: A Reviewer can submit a job (upload or URL) and receive receipt confirmation in under 60 seconds.
- **SC-003**: In a test where a user closes the browser immediately after submission and returns later, the job continues processing and the dashboard reflects the latest job state within 60 seconds of the user returning.
- **SC-004**: In a controlled test using VODs up to 30 minutes, at least 90% of jobs reach "Completed" within 10 minutes of submission.
- **SC-005**: At least 95% of submitted jobs either complete successfully or fail with a clear, human-readable reason displayed to the user.
- **SC-006**: Exported subtitle files (SRT/VTT) are usable for caption upload and appear synchronized in typical playback, with stakeholders reporting acceptable alignment in at least 90% of reviewed jobs.
