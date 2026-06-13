"""
Database helpers for Temporal Activities.
Provides methods to update job and step states during workflow execution.
"""

import uuid
import time
from sqlalchemy import select
from app.database import async_session_factory
from app.models.job import GenerationJob, JobStep, JobStepType, JobStatus
from app.models.project import Project, ProjectStatus


async def update_job(
    job_id: str,
    status: JobStatus,
    progress_percent: int,
    current_step: str,
    error_message: str | None = None,
    active_provider: str | None = None,
    total_cost_cents: int | None = None,
    candidates: dict | None = None,
    selected_candidate: int | None = None,
) -> None:
    """Updates the overall GenerationJob record in the database."""
    async with async_session_factory() as session:
        try:
            job_uuid = uuid.UUID(job_id)
            result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_uuid))
            job = result.scalar_one_or_none()
            if job:
                job.status = status
                job.progress_percent = progress_percent
                job.current_step = current_step
                if error_message is not None:
                    job.error_message = error_message
                if active_provider is not None:
                    job.active_provider = active_provider
                if total_cost_cents is not None:
                    job.total_cost_cents = total_cost_cents
                if candidates is not None:
                    job.candidates = candidates
                if selected_candidate is not None:
                    job.selected_candidate = selected_candidate
                await session.commit()
        except Exception:
            await session.rollback()
            raise


async def update_project_status(project_id: str, status: ProjectStatus) -> None:
    """Updates the parent project state from an activity."""
    async with async_session_factory() as session:
        try:
            project_uuid = uuid.UUID(project_id)
            result = await session.execute(select(Project).where(Project.id == project_uuid))
            project = result.scalar_one_or_none()
            if project:
                project.status = status
                await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_or_update_step(
    job_id: str,
    step_type: JobStepType,
    status: JobStatus,
    provider: str | None = None,
    cost_cents: int = 0,
    duration_seconds: float | None = None,
    input_data: dict | None = None,
    output_data: dict | None = None,
    error_details: dict | None = None,
) -> str:
    """Creates a new JobStep or updates an existing one if it is already in the database."""
    async with async_session_factory() as session:
        try:
            job_uuid = uuid.UUID(job_id)
            # Find the job first to fetch tenant_id
            job_res = await session.execute(select(GenerationJob).where(GenerationJob.id == job_uuid))
            job = job_res.scalar_one_or_none()
            if not job:
                raise ValueError(f"Job {job_id} not found")

            # Check if step already exists for this job
            step_res = await session.execute(
                select(JobStep).where(
                    JobStep.job_id == job_uuid,
                    JobStep.step_type == step_type,
                )
            )
            step = step_res.scalar_one_or_none()

            if not step:
                # Create new step
                step = JobStep(
                    tenant_id=job.tenant_id,
                    job_id=job_uuid,
                    step_type=step_type,
                    status=status,
                    provider=provider,
                    cost_cents=cost_cents,
                    duration_seconds=duration_seconds,
                    input_data=input_data,
                    output_data=output_data,
                    error_details=error_details,
                )
                session.add(step)
            else:
                # Update existing step
                step.status = status
                if provider is not None:
                    step.provider = provider
                if cost_cents > 0:
                    step.cost_cents = cost_cents
                if duration_seconds is not None:
                    step.duration_seconds = duration_seconds
                if input_data is not None:
                    step.input_data = input_data
                if output_data is not None:
                    step.output_data = output_data
                if error_details is not None:
                    step.error_details = error_details

            # If the step incurred costs, aggregate it into the parent job's total cost
            if cost_cents > 0:
                job.total_cost_cents += cost_cents

            await session.commit()
            return str(step.id)
        except Exception:
            await session.rollback()
            raise
