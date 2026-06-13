"""
Temporal Activity: Candidate 3D model evaluation.
Compares generated candidates and selects the best one for post-processing.
"""

import logging
import time
from temporalio import activity

from app.models.job import JobStatus, JobStepType
from app.workflows.activities.db_helper import update_job, create_or_update_step

logger = logging.getLogger(__name__)


@activity.defn
async def evaluate_candidates(input_data: dict) -> dict:
    """Evaluates multiple 3D model candidates and selects the best one."""
    job_id = input_data["job_id"]
    project_id = input_data["project_id"]
    candidates = input_data.get("candidates", [])

    logger.info(f"Starting candidate evaluation for job {job_id}, candidates count: {len(candidates)}")

    # Update state
    await update_job(
        job_id=job_id,
        status=JobStatus.EVALUATING,
        progress_percent=50,
        current_step="Evaluating generated 3D candidates",
    )
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.CANDIDATE_EVALUATION,
        status=JobStatus.EVALUATING,
        input_data={"candidates_count": len(candidates)},
    )

    start_time = time.time()

    if not candidates:
        error_msg = "No candidates to evaluate"
        await update_job(
            job_id=job_id,
            status=JobStatus.FAILED,
            progress_percent=50,
            current_step="Evaluation failed: no candidates",
            error_message=error_msg,
        )
        return {"selected_candidate": None, "error": error_msg}

    # Evaluation heuristic: pick candidate with highest quality score,
    # penalize extremely high triangle counts (e.g. > 100k) to optimize for web rendering.
    best_candidate_idx = 0
    best_score = -1.0

    eval_logs = []
    for idx, c in enumerate(candidates):
        quality = c.get("quality_score", 0.8)
        triangles = c.get("triangle_count", 25000)

        # Penalize if polycount is too high for web
        poly_penalty = max(0.0, (triangles - 50000) / 100000.0)
        final_score = quality - poly_penalty

        eval_logs.append({
            "candidate_index": idx,
            "provider": c.get("provider"),
            "quality_score": quality,
            "triangle_count": triangles,
            "poly_penalty": poly_penalty,
            "final_score": final_score,
        })

        if final_score > best_score:
            best_score = final_score
            best_candidate_idx = idx

    duration = time.time() - start_time
    output_data = {
        "selected_candidate": best_candidate_idx,
        "evaluation_results": eval_logs,
    }

    # Update DB
    await update_job(
        job_id=job_id,
        status=JobStatus.EVALUATING,
        progress_percent=60,
        current_step=f"Selected candidate index {best_candidate_idx}",
        selected_candidate=best_candidate_idx,
    )
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.CANDIDATE_EVALUATION,
        status=JobStatus.COMPLETED,
        duration_seconds=duration,
        output_data=output_data,
    )

    return output_data
