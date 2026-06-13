"""
Temporal Activity: Asset analysis and validation.
"""

import logging
import time
from sqlalchemy import select
from temporalio import activity

from app.database import async_session_factory
from app.models.project import Project, ProjectAsset, ProjectStatus
from app.models.job import JobStatus, JobStepType
from app.workflows.activities.db_helper import (
    create_or_update_step,
    update_job,
    update_project_status,
)

logger = logging.getLogger(__name__)


def _input_value(input_data, key: str, default=None):
    if isinstance(input_data, dict):
        return input_data.get(key, default)
    return getattr(input_data, key, default)


@activity.defn
async def analyze_assets(input_data: dict) -> dict:
    """
    Validate and analyze raw uploaded assets for a project.
    Inspects image resolution, angles, and content type.
    """
    job_id = _input_value(input_data, "job_id")
    project_id = _input_value(input_data, "project_id")

    logger.info(f"Starting asset analysis for job {job_id}, project {project_id}")

    # Mark job and step in progress
    await update_job(
        job_id=job_id,
        status=JobStatus.ANALYZING,
        progress_percent=10,
        current_step="Analyzing and validating uploaded assets",
    )
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.ASSET_VALIDATION,
        status=JobStatus.ANALYZING,
        input_data={"project_id": project_id},
    )

    start_time = time.time()

    # Query project assets
    async with async_session_factory() as session:
        result = await session.execute(
            select(ProjectAsset).where(ProjectAsset.project_id == project_id)
        )
        assets = result.scalars().all()

        proj_res = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = proj_res.scalar_one_or_none()

    if not project:
        error_msg = f"Project {project_id} not found"
        await update_job(
            job_id=job_id,
            status=JobStatus.FAILED,
            progress_percent=10,
            current_step="Failed: Project not found",
            error_message=error_msg,
        )
        await update_project_status(project_id, ProjectStatus.DRAFT)
        return {"is_valid": False, "error": error_msg}

    # Validation criteria: must have at least one image/CAD file
    images = [a for a in assets if a.asset_type.value == "image"]
    cads = [a for a in assets if a.asset_type.value == "cad"]

    errors = []
    warnings = []

    if not images and not cads:
        errors.append("No images or CAD files uploaded. Cannot generate 3D model.")

    if len(images) > 0 and len(images) < 3:
        warnings.append("Less than 3 images uploaded. Quality might be sub-optimal.")

    # Check resolution of images
    for img in images:
        if img.width_px and img.height_px:
            if img.width_px < 512 or img.height_px < 512:
                warnings.append(f"Image {img.original_filename} has low resolution: {img.width_px}x{img.height_px}")

    is_valid = len(errors) == 0
    status_result = JobStatus.COMPLETED if is_valid else JobStatus.FAILED

    output_data = {
        "is_valid": is_valid,
        "assets_count": len(assets),
        "images_count": len(images),
        "cads_count": len(cads),
        "errors": errors,
        "warnings": warnings,
    }

    # Update asset validation status in database
    async with async_session_factory() as session:
        for asset in assets:
            asset_res = await session.execute(select(ProjectAsset).where(ProjectAsset.id == asset.id))
            db_asset = asset_res.scalar_one_or_none()
            if db_asset:
                db_asset.is_validated = is_valid
                db_asset.validation_notes = {
                    "is_valid": is_valid,
                    "errors": errors,
                    "warnings": warnings,
                }
        await session.commit()

    duration = time.time() - start_time

    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.ASSET_VALIDATION,
        status=status_result,
        duration_seconds=duration,
        output_data=output_data,
        error_details={"errors": errors} if errors else None,
    )

    if not is_valid:
        await update_job(
            job_id=job_id,
            status=JobStatus.FAILED,
            progress_percent=15,
            current_step="Asset validation failed",
            error_message="; ".join(errors),
        )
        await update_project_status(project_id, ProjectStatus.DRAFT)

    return output_data
