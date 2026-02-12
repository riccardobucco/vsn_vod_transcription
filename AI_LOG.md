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