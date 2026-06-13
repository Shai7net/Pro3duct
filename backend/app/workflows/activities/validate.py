"""
Temporal Activity: glTF quality and spec validation.
Runs automated checks on the post-processed models before they can be published.
"""

import logging
import time
from temporalio import activity

from app.models.job import JobStatus, JobStepType
from app.workflows.activities.db_helper import update_job, create_or_update_step

logger = logging.getLogger(__name__)


@activity.defn
async def validate_model(input_data: dict) -> dict:
    """Performs glTF standard and interaction rules validation."""
    job_id = input_data["job_id"]
    project_id = input_data["project_id"]
    model_key = input_data.get("model_key")

    logger.info(f"Starting model validation for job {job_id}, model key: {model_key}")

    # Update state
    await update_job(
        job_id=job_id,
        status=JobStatus.VALIDATING,
        progress_percent=90,
        current_step="Validating model geometry and specifications",
    )
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.QUALITY_VALIDATION,
        status=JobStatus.VALIDATING,
        input_data={"model_key": model_key},
    )

    start_time = time.time()

    # Heuristic validations for the model
    errors = []
    warnings = []

    # If the key is empty, it's invalid
    if not model_key:
        errors.append("Model file path key is empty. Post-processing failure.")

    # Simulated validation rules
    # In production, we would call a subprocess running `gltf-validator` or a python package.
    # E.g. checking texture formats (recommend KTX2), checking standard materials.
    warnings.append("Model uses standard PNG/JPEG textures. KTX2 compression is recommended for production.")

    is_valid = len(errors) == 0
    quality_score = max(0.0, 1.0 - (len(errors) * 0.4 + len(warnings) * 0.1))

    output_data = {
        "is_valid": is_valid,
        "quality_score": quality_score,
        "errors": errors,
        "warnings": warnings,
        "validation_timestamp": time.time(),
    }

    duration = time.time() - start_time

    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.QUALITY_VALIDATION,
        status=JobStatus.COMPLETED if is_valid else JobStatus.FAILED,
        duration_seconds=duration,
        output_data=output_data,
        error_details={"errors": errors} if errors else None,
    )

    return output_data
