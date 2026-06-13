"""
Temporal Workflow for Pro3duct AI Generation Pipeline.
Coordinates image analysis, 3D generation, Blender post-processing, evaluation, validation, and packaging.
"""

from datetime import timedelta
from dataclasses import dataclass
from temporalio import workflow
from temporalio.common import RetryPolicy

# Ensure imports work within Temporal environment sandbox
with workflow.unsafe.imports_passed_through():
    from app.workflows.activities.analyze import analyze_assets
    from app.workflows.activities.generate_3d import generate_3d_candidates
    from app.workflows.activities.evaluate import evaluate_candidates
    from app.workflows.activities.post_process import post_process_model
    from app.workflows.activities.validate import validate_model
    from app.workflows.activities.publish import publish_model


@dataclass
class GenerationInput:
    job_id: str
    project_id: str
    tenant_id: str | None = None
    preferred_provider: str | None = None


@workflow.defn
class GenerationWorkflow:
    """Orchestrates the multi-stage digital twin creation workflow."""

    @workflow.run
    async def run(self, input_data: GenerationInput) -> dict:
        # Common retry policy and timeouts
        default_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=5),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        # ── Stage 1: Analyze & Validate Raw Uploads ──
        analysis_result = await workflow.execute_activity(
            analyze_assets,
            input_data,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=default_retry_policy,
        )

        if not analysis_result.get("is_valid", False):
            return {
                "status": "failed",
                "error": "Asset analysis failed validation check",
                "stage": "analysis",
            }

        # ── Stage 2: 3D Candidate Generation ──
        generation_result = await workflow.execute_activity(
            generate_3d_candidates,
            input_data,
            start_to_close_timeout=timedelta(minutes=45),
            retry_policy=default_retry_policy,
        )

        candidates = generation_result.get("candidates", [])
        if not candidates:
            return {
                "status": "failed",
                "error": "No 3D candidates were successfully generated",
                "stage": "generation",
            }

        # ── Stage 3: Candidate Evaluation ──
        evaluation_result = await workflow.execute_activity(
            evaluate_candidates,
            {
                "job_id": input_data.job_id,
                "project_id": input_data.project_id,
                "candidates": candidates,
            },
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=default_retry_policy,
        )

        selected_candidate_index = evaluation_result.get("selected_candidate", 0)

        # ── Stage 4: Blender Post-Processing (Retopology, UV, Materials, Pivots) ──
        post_process_result = await workflow.execute_activity(
            post_process_model,
            {
                "job_id": input_data.job_id,
                "project_id": input_data.project_id,
                "candidate": candidates[selected_candidate_index],
            },
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=default_retry_policy,
        )

        if not post_process_result.get("success", False):
            return {
                "status": "failed",
                "error": f"Blender post-processing failed: {post_process_result.get('error')}",
                "stage": "post_processing",
            }

        # ── Stage 5: Validation (glTF validation & physics check) ──
        validation_result = await workflow.execute_activity(
            validate_model,
            {
                "job_id": input_data.job_id,
                "project_id": input_data.project_id,
                "model_key": post_process_result.get("glb_key"),
            },
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=default_retry_policy,
        )

        # ── Stage 6: Publish (Finalize TwinSpec and Export Packaging) ──
        publish_result = await workflow.execute_activity(
            publish_model,
            {
                "job_id": input_data.job_id,
                "project_id": input_data.project_id,
                "post_process_data": post_process_result,
                "validation_data": validation_result,
            },
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=default_retry_policy,
        )

        return {
            "status": "completed",
            "job_id": input_data.job_id,
            "project_id": input_data.project_id,
            "output": publish_result,
        }
