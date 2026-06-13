"""
Temporal worker process.
Registers all workflows and activities, then listens to the generation task queue.
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from app.config import get_settings
from app.workflows.generation_workflow import GenerationWorkflow
from app.workflows.activities.analyze import analyze_assets
from app.workflows.activities.generate_3d import generate_3d_candidates
from app.workflows.activities.evaluate import evaluate_candidates
from app.workflows.activities.post_process import post_process_model
from app.workflows.activities.validate import validate_model
from app.workflows.activities.publish import publish_model

# Set up logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Initializing Temporal Worker...")

    try:
        # Connect to Temporal Server
        client = await Client.connect(
            target_host=settings.temporal_host,
            namespace=settings.temporal_namespace,
        )
        logger.info(f"Connected to Temporal server at {settings.temporal_host}")
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {e}")
        return

    # Build list of activities
    activities = [
        analyze_assets,
        generate_3d_candidates,
        evaluate_candidates,
        post_process_model,
        validate_model,
        publish_model,
    ]

    # Create worker
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[GenerationWorkflow],
        activities=activities,
    )

    logger.info(f"Running worker listening on queue: '{settings.temporal_task_queue}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
