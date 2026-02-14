# Phase 1 Data Model: VOD Transcription Utility

**Feature**: 001-vod-transcription-utility  
**Date**: 2026-02-14

## Entities

### User

Represents an authenticated principal.

- `id` (UUID, PK)
- `logto_sub` (string, unique, nullable=false)
- `display_name` (string, nullable=true)
- `created_at` (timestamptz)
- `last_sign_in_at` (timestamptz, nullable=true)

Notes:
- The app authorizes requests by the presence of a valid app session; `User` exists mainly for auditing and future extensibility.

### TranscriptionJob

A submitted unit of work representing a single VOD ingestion and transcription attempt.

- `id` (UUID, PK)
- `user_id` (UUID, FK → `User.id`, nullable=false)
- `source_type` (enum: `upload` | `url`)
- `source_label` (string, nullable=false)  
  - Upload: original filename
  - URL: hostname/path display label
- `source_url` (string, nullable=true)  
  - required when `source_type=url`
- `original_object_key` (string, nullable=true)  
  - MinIO key for the uploaded/downloaded video (optional if minimization chooses to discard originals)
- `audio_object_key` (string, nullable=true)  
  - MinIO key for derived audio used for transcription
- `input_format` (string, nullable=true)  
  - one of: mp4/mov/mkv (best-effort)
- `duration_seconds` (integer, nullable=true)
- `status` (enum: `queued` | `processing` | `completed` | `failed`)
- `failure_code` (string, nullable=true)
- `failure_message` (string, nullable=true)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `started_at` (timestamptz, nullable=true)
- `completed_at` (timestamptz, nullable=true)

Validation rules:
- If `duration_seconds > 1800` (30 minutes), the job is rejected at submit time when known, otherwise transitions to `failed` with a clear message.
- If the source cannot be downloaded/decoded or contains no audio track, transition to `failed`.

State transitions:
- `queued → processing → completed | failed`
- Terminal states: `completed`, `failed`.

Indexes:
- `(created_at desc)` for dashboard list.
- `(status, created_at)` for operational queries.
- `(user_id, created_at desc)` for user-scoped dashboard.

### TranscriptSegment

A native time-coded piece of transcript produced by the engine.

- `id` (bigint / serial PK)
- `job_id` (UUID, FK → `TranscriptionJob.id`, nullable=false)
- `segment_index` (int, nullable=false)  
  - stable ordering as produced by the engine
- `start_ms` (integer, nullable=false)
- `end_ms` (integer, nullable=false)
- `text` (text, nullable=false)
- `avg_logprob` (double precision, nullable=true)  
  - raw engine signal when available
- `confidence` (double precision, nullable=true)  
  - derived, e.g. $\exp(\text{avg\_logprob})$
- `created_at` (timestamptz)

Validation rules:
- `start_ms >= 0`, `end_ms >= start_ms`.
- `segment_index` is unique per `(job_id, segment_index)`.

### Export (virtual)

Exports are generated from stored segments.

- Formats:
  - `txt`
  - `srt`
  - `vtt`

Storage policy:
- Default: generate on-demand and stream to the client (no DB persistence).
- Optional optimization: cache export files in MinIO with:
  - `job_id`
  - `format`
  - `object_key`
  - `created_at`

## Relationships

- `User 1 ── * TranscriptionJob`
- `TranscriptionJob 1 ── * TranscriptSegment`

## Retention

- Jobs and all related segments must be deleted after 30 days (FR-019).
- Deletion must also remove associated objects in MinIO (`original_object_key`, `audio_object_key`, and any cached exports).

