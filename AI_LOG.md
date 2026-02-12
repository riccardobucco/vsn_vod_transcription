# AI Log

<!-- TEMPLATE -->
<!-- ## [Short Title of What You Built]

**Model:** `Claude 3.5 Sonnet` (or `GPT-4o`, etc.)

### Changelog

- [What did the AI actually achieve?]
- [Any specific bug fixed?]
- [Key design decision made?]

### Files Affected

- `src/app/page.tsx`
- `components/ui/button.tsx`
- `lib/utils.ts`

### Prompt / Context

<details>

<summary>Click to expand full prompt</summary>

[PASTE YOUR LONG PROMPT OR CONVERSATION HISTORY HERE]

</details> -->

## Defined Constitution

**Model:** `GPT-5.2`

### Changelog

- Filled the constitution template with minimal, production-shaped requirements for a VOD transcription web app (principles, security/privacy, workflow gates, governance).

### Files Affected

- `.specify/memory/constitution.md`

### Prompt / Context

<details>

<summary>Click to expand full prompt</summary>

```
1.Fill the constitution with the bare minimum requirements for a VOD transcription web app based on the template.

2. Add to the constitution the tech stack requirements for the VOD transcription web app based on the template
```

</details>

## Incorporated Candidate Assignment Invariants

**Model:** `GPT-5.2`

### Changelog

- Updated the constitution to align job statuses with `queued → processing → completed | failed`.
- Added API requirements for job creation inputs (upload or HTTP(S) URL) and export guarantees (`txt` and `srt` or `vtt`).
- Added deliverability/verification invariants to quality gates and governance (README verify in <10 minutes, prompts traceability, deployed URL + reviewer creds).

### Files Affected

- `.specify/memory/constitution.md`

### Prompt / Context

<details>

<summary>Click to expand full prompt</summary>

```
Incorporate these requirements into the constitution using the established template, ensuring minimal disruption to the existing text:
- Job state machine should match the required statuses: queued → processing → completed | failed (current text uses running/succeeded).
- Job creation inputs must support either file upload or HTTP(S) URL reference.
- Exports must guarantee at least txt and srt (or vtt).
- Deliverability/verification: deployed app + reviewer credentials + README “verify in <10 minutes” + prompts/AI traceability folder are submission invariants and fit under governance/quality gates.
```

</details>

## Speckit Specify: VOD Transcription Utility Spec

**Model:** `GPT-5.2`

### Changelog

- Created feature branch `001-vod-transcription-utility` and initialized the spec scaffold under `specs/`.
- Wrote a complete, testable feature spec with prioritized user stories, acceptance scenarios, edge cases, functional requirements, key entities, assumptions, out-of-scope boundaries, and measurable success criteria.
- Added a spec quality checklist and marked items complete after validating the spec has no implementation details and no open clarification markers.

### Files Affected

- `specs/001-vod-transcription-utility/spec.md`
- `specs/001-vod-transcription-utility/checklists/requirements.md`

### Prompt / Context

<details>

<summary>Click to expand full prompt</summary>

```
Follow instructions in [speckit.specify.prompt.md](file:///Users/rbucco/Workspace/Personal/vsn/vsn_vod_transcription_specify/.github/prompts/speckit.specify.prompt.md).

# Product Vision: The VOD Transcription Utility

## The "Why" (Motivation)

We are building this product to solve the "black box" problem of video content. Currently, we have video assets (VODs) containing valuable spoken information that is locked away in binary files. To make this content accessible, searchable, and usable for captioning, we need a reliable, automated pipeline that converts speech to text.

The goal is to move away from manual transcription or fragile, ad-hoc scripts. We need a standardized "factory" where a user can drop a video file and reliably receive a structured, time-coded text document in return. The value proposition is automation, reliability, and accessibility.

## The "What" (Product Specification)

I am building a focused, production-grade web utility for video-to-text conversion. It doesn't need to be flashy, but it must be robust and communicative. The user should trust that once they hand off a file, the system handles the complexity of processing it.

### 1. The User Experience & Interface

- Access Control: The app is private. It requires a secure login barrier. We need a pre-configured "Reviewer" persona so stakeholders can immediately access the tool without registration friction.
- The Dashboard: Upon logging in, the user sees a straightforward dashboard. This is the command center. It shouldn't be cluttered; it just needs to answer: "What happened to the files I sent you?" and "How do I send a new one?"

### 2. Job Submission (The Input)

I want to give users flexibility in how they provide source material. We cannot assume the file is always on their local machine.

- Dual Ingest Methods: The user should be able to:
  1. Upload: Drag and drop a finished video file (like an MP4 or MOV) directly from their computer.
  2. Reference: Paste a direct link (URL) to a video file hosted elsewhere.
- Expectation Management: Since this is VOD (Video On Demand) only, we are not handling live streams. The system should accept the file and immediately confirm receipt, letting the user know the "job" has started.

### 3. The Processing Behavior (Async Workflow)

This is the most critical user experience detail: No watching paint dry.

- Fire and Forget: Transcription is heavy work. The user must not be forced to keep their browser tab open or watch a spinning loader while the video processes.
- State Transparency: The system needs to clearly communicate the lifecycle of a job. The user should see distinct states for every item they've submitted:
  - Queued (We have it, waiting for a worker).
  - Processing (The AI is currently listening).
  - Completed (Ready to view).
  - Failed (Something went wrong).
- Failure Feedback: If a job fails, the user shouldn't just see "Error." They need a basic reason (e.g., "File corrupted" or "Timeout") so they aren't left guessing.

### 4. The Deliverable (The Output)

Once a job is "Completed," the value is delivered. The view for a finished job needs to provide:

- Granularity: I don't just want a wall of text. I need Timecoded Segments. This means breaking the text down by start and end times (e.g., 00:01 - 00:05: "Hello world").
- Confidence: Ideally, the system should indicate how sure it is about the transcription (a confidence score), giving the user an idea of whether they need to manually review it.
- Portability (Exports): The user needs to take this data elsewhere. We must support standard industry formats:
  - Plain Text (.txt): For reading, blog posts, or summaries.
  - Subtitles (.srt or .vtt): For directly uploading captions to video players.

### 5. Summary of Success

A successful build means a user can log in, throw a video link at the system, close their laptop, come back 10 minutes later, see a green "Completed" badge, and download a subtitle file that perfectly matches the video audio.
```

</details>
