"""
GenerationJob model — tracks the AI generation pipeline for each project.
"""

from __future__ import annotations

import uuid
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TenantScopedModel

if TYPE_CHECKING:
    from app.models.project import Project


class JobStatus(str, PyEnum):
    QUEUED = "queued"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    EVALUATING = "evaluating"
    POST_PROCESSING = "post_processing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_USER = "waiting_user"


class JobStepType(str, PyEnum):
    ASSET_VALIDATION = "asset_validation"
    AI_ANALYSIS = "ai_analysis"
    THREE_D_GENERATION = "3d_generation"
    CANDIDATE_EVALUATION = "candidate_evaluation"
    BLENDER_POST_PROCESS = "blender_post_process"
    INTERACTION_GENERATION = "interaction_generation"
    QUALITY_VALIDATION = "quality_validation"
    ASSET_PACKAGING = "asset_packaging"


class GenerationJob(TenantScopedModel):
    __tablename__ = "generation_jobs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.QUEUED, nullable=False
    )

    # Temporal workflow reference
    temporal_workflow_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    temporal_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Active provider
    active_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Cost tracking (in cents)
    total_cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Progress
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_step: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Results
    candidates: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    selected_candidate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evaluation_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="jobs")
    steps: Mapped[list["JobStep"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", order_by="JobStep.created_at"
    )


class JobStep(TenantScopedModel):
    __tablename__ = "job_steps"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False
    )
    step_type: Mapped[JobStepType] = mapped_column(Enum(JobStepType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.QUEUED, nullable=False
    )
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Step-specific data
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationship
    job: Mapped["GenerationJob"] = relationship(back_populates="steps")
