"""
Temporal Activity: Digital Twin model publishing and spec generation.
Saves the final ProductDigitalTwinSpec and changes project state to REVIEW.
"""

import logging
import time
import uuid
from sqlalchemy import select
from temporalio import activity

from app.database import async_session_factory
from app.models.project import Project, ProjectStatus
from app.models.digital_twin import DigitalTwin, TwinStatus
from app.models.job import JobStatus, JobStepType
from app.workflows.activities.db_helper import update_job, create_or_update_step

logger = logging.getLogger(__name__)


@activity.defn
async def publish_model(input_data: dict) -> dict:
    """Creates the final DigitalTwin spec package and updates project state."""
    job_id = input_data["job_id"]
    project_id = input_data["project_id"]
    post_process_data = input_data["post_process_data"]
    validation_data = input_data["validation_data"]

    logger.info(f"Starting model publish and spec generation for job {job_id}")

    # Update state
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.ASSET_PACKAGING,
        status=JobStatus.GENERATING,
        input_data={"post_process_data": post_process_data},
    )

    start_time = time.time()

    # Retrieve project & create/update digital twin record
    async with async_session_factory() as session:
        try:
            # 1. Update Project Status to REVIEW
            proj_uuid = uuid.UUID(project_id)
            proj_res = await session.execute(select(Project).where(Project.id == proj_uuid))
            project = proj_res.scalar_one_or_none()
            if not project:
                raise ValueError(f"Project {project_id} not found")
            project.status = ProjectStatus.REVIEW

            initial_spec = {
                "product_name": project.name,
                "brand": project.brand,
                "model_number": project.model_number,
                "category": project.category.value,
                "dimensions": {
                    "width_mm": project.width_mm,
                    "height_mm": project.height_mm,
                    "depth_mm": project.depth_mm,
                    "unit": "mm",
                },
                "source_model": {
                    "format": "glb",
                    "glb_key": post_process_data.get("glb_key"),
                    "provider": post_process_data.get("source_provider"),
                    "source_candidate": post_process_data.get("source_candidate"),
                },
                "parts": [
                    {
                        "id": "part-product",
                        "name": project.name,
                        "type": "other",
                        "visible": True,
                        "mesh_name": "generated_glb",
                        "material": {
                            "color": "#d7dae2",
                            "roughness": 0.55,
                            "metalness": 0.05,
                            "opacity": 1.0,
                        },
                    }
                ],
                "lights": [
                    {
                        "id": "key-light",
                        "type": "directional",
                        "color": "#ffffff",
                        "intensity": 1.4,
                        "position": [2.5, 4.0, 3.0],
                    },
                    {
                        "id": "fill-light",
                        "type": "point",
                        "color": "#a78bfa",
                        "intensity": 0.7,
                        "position": [-2.0, 2.0, 2.5],
                    },
                ],
                "state_machine": {
                    "initial_state": "default",
                    "states": ["default"],
                    "transitions": [],
                },
                "hotspots": [],
                "ai_decisions": [
                    {
                        "type": "mesh_generation",
                        "message": "Generated from uploaded product photos using a real image-to-3D provider.",
                        "provider": post_process_data.get("source_provider"),
                    }
                ],
            }

            # 2. Upsert DigitalTwin record
            twin_res = await session.execute(select(DigitalTwin).where(DigitalTwin.project_id == proj_uuid))
            twin = twin_res.scalar_one_or_none()

            if not twin:
                twin = DigitalTwin(
                    tenant_id=project.tenant_id,
                    project_id=proj_uuid,
                    status=TwinStatus.REVIEW,
                    version=1,
                    spec=initial_spec,
                    glb_key=post_process_data.get("glb_key"),
                    usdz_key=post_process_data.get("usdz_key"),
                    quality_score=validation_data.get("quality_score", 0.9),
                    ai_confidence=0.88,
                    triangle_count=post_process_data.get("processed_triangle_count"),
                    file_size_bytes=post_process_data.get("file_size_bytes"),
                    ai_decisions=initial_spec.get("ai_decisions"),
                    is_published=False,
                )
                session.add(twin)
            else:
                twin.status = TwinStatus.REVIEW
                twin.spec = initial_spec
                twin.glb_key = post_process_data.get("glb_key")
                twin.usdz_key = post_process_data.get("usdz_key")
                twin.quality_score = validation_data.get("quality_score", 0.9)
                twin.triangle_count = post_process_data.get("processed_triangle_count")
                twin.file_size_bytes = post_process_data.get("file_size_bytes")
                twin.ai_decisions = initial_spec.get("ai_decisions")
                twin.is_published = False
                twin.version += 1

            await session.commit()
            twin_id_str = str(twin.id)
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save digital twin spec: {e}")
            raise

    duration = time.time() - start_time
    output_data = {
        "digital_twin_id": twin_id_str,
        "glb_key": post_process_data.get("glb_key"),
        "usdz_key": post_process_data.get("usdz_key"),
        "is_published": False,
        "spec_version": 1,
    }

    # Final updates to job state
    await update_job(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        progress_percent=100,
        current_step="Generation pipeline finished successfully. Digital twin is ready for review.",
    )
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.ASSET_PACKAGING,
        status=JobStatus.COMPLETED,
        duration_seconds=duration,
        output_data=output_data,
    )

    return output_data
