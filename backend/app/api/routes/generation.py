"""
Generation routes — trigger the AI generation pipeline.
"""

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AuthenticatedUser, DBSession
from app.models.job import GenerationJob, JobStatus
from app.models.provider import TenantProviderCredential
from app.models.project import Project, ProjectStatus
from app.schemas.job import GenerateRequest, JobDetailResponse, JobResponse, JobStepResponse
from app.temporal_client import get_temporal_client
from app.workflows.generation_workflow import GenerationWorkflow, GenerationInput
from app.config import get_settings

settings = get_settings()

router = APIRouter(tags=["Generation"])


async def _has_active_meshy_credential(tenant_id: uuid.UUID, db: DBSession) -> bool:
    result = await db.execute(
        select(TenantProviderCredential).where(
            TenantProviderCredential.tenant_id == tenant_id,
            TenantProviderCredential.is_active.is_(True),
        )
    )
    credentials = result.scalars().all()
    return any(c.provider_name.lower().strip() in {"meshy", "meshy ai"} for c in credentials)


@router.get("/generation/capabilities")
async def get_generation_capabilities(
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Report whether this tenant can run real 3D generation right now."""
    has_meshy_key = bool(settings.meshy_api_key.strip()) or await _has_active_meshy_credential(
        current_user.tenant_id,
        db,
    )
    real_3d_enabled = has_meshy_key

    return {
        "real_3d_enabled": real_3d_enabled,
        "demo_generation_enabled": settings.allow_demo_generation,
        "active_provider": "meshy" if has_meshy_key else None,
        "missing_config": [] if has_meshy_key else ["MESHY_API_KEY"],
        "max_images": 4,
        "supported_image_types": ["image/jpeg", "image/png", "image/webp", "image/tiff"],
        "input_method": "local_images_as_base64_data_uri",
        "cost_note": "Meshy Multi Image to 3D Meshy-6 uses provider credits per generation.",
    }


@router.post(
    "/projects/{project_id}/generate",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_generation(
    project_id: uuid.UUID,
    data: GenerateRequest,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """
    Start the AI generation pipeline for a project.
    Creates a GenerationJob and triggers the Temporal workflow.
    """
    # Verify project exists and is ready
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status == ProjectStatus.GENERATING:
        raise HTTPException(
            status_code=409,
            detail="Generation already in progress for this project",
        )

    has_meshy_key = bool(settings.meshy_api_key.strip()) or await _has_active_meshy_credential(
        current_user.tenant_id,
        db,
    )
    if not has_meshy_key and not settings.allow_demo_generation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "חסר מפתח Meshy API. הוסף מפתח במסך הגדרות וחיבורי AI, "
                "או הגדר MESHY_API_KEY בקובץ .env, ואז נסה שוב."
            ),
        )

    # Create the generation job
    job = GenerationJob(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
        status=JobStatus.QUEUED,
        progress_percent=0,
        current_step="Queued for processing",
    )
    db.add(job)

    # Update project status
    project.status = ProjectStatus.GENERATING

    await db.commit()

    # Trigger Temporal workflow
    try:
        temporal_client = await get_temporal_client()
        workflow_id = f"generation-{job.id}"
        await temporal_client.start_workflow(
            GenerationWorkflow.run,
            GenerationInput(
                job_id=str(job.id),
                project_id=str(project_id),
                tenant_id=str(current_user.tenant_id),
                preferred_provider=data.preferred_provider or "meshy",
            ),
            id=workflow_id,
            task_queue=settings.temporal_task_queue,
        )
        job.temporal_workflow_id = workflow_id
        await db.commit()
    except Exception as e:
        # Revert status changes if workflow fails to start
        project.status = ProjectStatus.DRAFT
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start generation workflow: {e}",
        )

    await db.refresh(job)

    return JobResponse(
        id=str(job.id),
        project_id=str(project_id),
        status=job.status.value,
        progress_percent=job.progress_percent,
        current_step=job.current_step,
        active_provider=None,
        total_cost_cents=0,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_status(
    job_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Get detailed job status including all steps."""
    result = await db.execute(
        select(GenerationJob).where(
            GenerationJob.id == job_id,
            GenerationJob.tenant_id == current_user.tenant_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    steps = [
        JobStepResponse(
            id=str(step.id),
            step_type=step.step_type.value,
            status=step.status.value,
            provider=step.provider,
            cost_cents=step.cost_cents,
            duration_seconds=step.duration_seconds,
            output_data=step.output_data,
            created_at=step.created_at,
        )
        for step in job.steps
    ]

    return JobDetailResponse(
        id=str(job.id),
        project_id=str(job.project_id),
        status=job.status.value,
        progress_percent=job.progress_percent,
        current_step=job.current_step,
        active_provider=job.active_provider,
        total_cost_cents=job.total_cost_cents,
        error_message=job.error_message,
        candidates=job.candidates,
        selected_candidate=job.selected_candidate,
        created_at=job.created_at,
        updated_at=job.updated_at,
        steps=steps,
    )


@router.post("/jobs/{job_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_job(
    job_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Cancel a running generation job."""
    result = await db.execute(
        select(GenerationJob).where(
            GenerationJob.id == job_id,
            GenerationJob.tenant_id == current_user.tenant_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
        raise HTTPException(status_code=409, detail="Job already finished")

    job.status = JobStatus.CANCELLED
    project_result = await db.execute(
        select(Project).where(
            Project.id == job.project_id,
            Project.tenant_id == current_user.tenant_id,
        )
    )
    project = project_result.scalar_one_or_none()
    if project and project.status == ProjectStatus.GENERATING:
        project.status = ProjectStatus.DRAFT
    # Cancel the Temporal workflow if it is running
    if job.temporal_workflow_id:
        try:
            temporal_client = await get_temporal_client()
            handle = temporal_client.get_workflow_handle(job.temporal_workflow_id)
            await handle.cancel()
        except Exception as e:
            # Log warning but proceed to cancel DB state
            pass

    await db.flush()
    return {"message": "Job cancelled"}
