"""
Blender Headless Activity Worker.
Runs on nodes containing Blender installations. Registers the post_process_model activity.
"""

import sys
import os
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

# Add backend to path to reuse database, configuration, and activity definitions
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "backend"))
sys.path.append(backend_dir)

from app.config import get_settings
from app.workflows.activities.post_process import post_process_model

# Setup logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("blender_worker")

async def main():
    logger.info("Initializing Blender Activity Worker...")

    try:
        client = await Client.connect(
            target_host=settings.temporal_host,
            namespace=settings.temporal_namespace,
        )
        logger.info(f"Connected to Temporal server at {settings.temporal_host}")
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {e}")
        return

    # Listen on same queue to process heavy Blender tasks
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        activities=[post_process_model],
    )

    logger.info(f"Blender worker listening on task queue: '{settings.temporal_task_queue}'")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
