"""Initial tables: users, transcription_jobs, transcript_segments.

Revision ID: 001_init
Revises:
Create Date: 2026-02-14

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("logto_sub", sa.String(255), unique=True, nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_sign_in_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Job status enum
    job_status_enum = sa.Enum("queued", "processing", "completed", "failed", name="jobstatus")
    job_source_enum = sa.Enum("upload", "url", name="jobsourcetype")

    # Transcription jobs table
    op.create_table(
        "transcription_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_type", job_source_enum, nullable=False),
        sa.Column("source_label", sa.String(1024), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("original_object_key", sa.String(1024), nullable=True),
        sa.Column("audio_object_key", sa.String(1024), nullable=True),
        sa.Column("input_format", sa.String(32), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("status", job_status_enum, nullable=False, server_default="queued"),
        sa.Column("failure_code", sa.String(128), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_transcription_jobs_created_at_desc", "transcription_jobs", [sa.text("created_at DESC")])
    op.create_index("ix_transcription_jobs_status_created_at", "transcription_jobs", ["status", "created_at"])
    op.create_index("ix_transcription_jobs_user_id_created_at", "transcription_jobs", ["user_id", sa.text("created_at DESC")])

    # Transcript segments table
    op.create_table(
        "transcript_segments",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("transcription_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("segment_index", sa.Integer(), nullable=False),
        sa.Column("start_ms", sa.Integer(), nullable=False),
        sa.Column("end_ms", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("avg_logprob", sa.Double(), nullable=True),
        sa.Column("confidence", sa.Double(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(
        "ix_transcript_segments_job_id_index",
        "transcript_segments",
        ["job_id", "segment_index"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("transcript_segments")
    op.drop_table("transcription_jobs")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("DROP TYPE IF EXISTS jobsourcetype")
