"""
Temporal Client manager.
Provides async connection client singleton for API endpoints.
"""

from temporalio.client import Client
from app.config import get_settings

settings = get_settings()
_temporal_client: Client | None = None


async def get_temporal_client() -> Client:
    """Gets the connected Temporal client instance."""
    global _temporal_client
    if _temporal_client is None:
        _temporal_client = await Client.connect(
            target_host=settings.temporal_host,
            namespace=settings.temporal_namespace,
        )
    return _temporal_client
