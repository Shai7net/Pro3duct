"""
Meshy AI Provider Adapter — Multi-Image to 3D generation.
"""

import asyncio
import logging
import time

import httpx

from app.providers import Capability, ProviderAdapter, ProviderRequest, ProviderResponse

logger = logging.getLogger(__name__)


class MeshyAdapter(ProviderAdapter):
    """
    Adapter for the Meshy AI Multi-Image to 3D API.
    Supports creating 3D models from 1-4 product images.
    """

    def __init__(self, api_key: str, api_url: str = "https://api.meshy.ai") -> None:
        self._api_key = api_key
        self._api_url = api_url

    @property
    def name(self) -> str:
        return "meshy"

    @property
    def display_name(self) -> str:
        return "Meshy AI"

    @property
    def capabilities(self) -> list[Capability]:
        return [Capability.MULTI_IMAGE_TO_3D]

    @property
    def quality_tier(self) -> int:
        return 7

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        """Send images to Meshy and poll for completion."""
        start = time.time()
        image_urls = request.inputs.get("image_urls", [])

        if not image_urls:
            return ProviderResponse(
                success=False,
                provider_name=self.name,
                capability=request.capability,
                error_message="No image URLs provided",
                error_code="MISSING_INPUT",
            )

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Create task
                payload = {
                    "image_urls": image_urls[:4],
                    "ai_model": request.inputs.get("ai_model", "meshy-6"),
                    "should_texture": request.inputs.get("should_texture", True),
                    "enable_pbr": request.inputs.get("enable_pbr", True),
                    "target_formats": request.inputs.get("target_formats", ["glb"]),
                    "should_remesh": request.inputs.get("should_remesh", True),
                    "target_polycount": request.inputs.get("target_polycount", 30000),
                    "image_enhancement": request.inputs.get("image_enhancement", True),
                    "remove_lighting": request.inputs.get("remove_lighting", True),
                }
                create_response = await client.post(
                    f"{self._api_url}/openapi/v1/multi-image-to-3d",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if create_response.status_code == 401:
                    return ProviderResponse(
                        success=False,
                        provider_name=self.name,
                        capability=request.capability,
                        error_message="Invalid API key",
                        error_code="401",
                    )

                if create_response.status_code == 402:
                    return ProviderResponse(
                        success=False,
                        provider_name=self.name,
                        capability=request.capability,
                        error_message="Insufficient credits",
                        error_code="402",
                    )

                if create_response.status_code == 429:
                    return ProviderResponse(
                        success=False,
                        provider_name=self.name,
                        capability=request.capability,
                        error_message="Rate limited",
                        error_code="429",
                    )

                create_response.raise_for_status()
                task_data = create_response.json()
                task_id = task_data.get("result")

                # Poll for completion
                poll_interval = max(5, int(request.inputs.get("poll_interval_seconds", 10)))
                max_polls = max(1, request.timeout_seconds // poll_interval)
                for _ in range(max_polls):
                    await asyncio.sleep(poll_interval)

                    status_response = await client.get(
                        f"{self._api_url}/openapi/v1/multi-image-to-3d/{task_id}",
                        headers={"Authorization": f"Bearer {self._api_key}"},
                    )
                    status_response.raise_for_status()
                    status_data = status_response.json()

                    if status_data.get("status") == "SUCCEEDED":
                        model_url = status_data.get("model_urls", {}).get("glb")
                        if not model_url:
                            return ProviderResponse(
                                success=False,
                                provider_name=self.name,
                                capability=request.capability,
                                error_message="Meshy task succeeded but did not return a GLB URL",
                                error_code="MISSING_GLB_URL",
                                raw_response=status_data,
                            )

                        duration = time.time() - start
                        return ProviderResponse(
                            success=True,
                            provider_name=self.name,
                            capability=request.capability,
                            data={
                                "model": {
                                    "format": "glb",
                                    "model_url": model_url,
                                    "texture_urls": status_data.get("texture_urls", []),
                                    "thumbnail_url": status_data.get("thumbnail_url"),
                                    "task_id": task_id,
                                    "triangle_count": payload.get("target_polycount", 30000),
                                }
                            },
                            cost_cents=int(status_data.get("consumed_credits") or 30),
                            duration_seconds=duration,
                            raw_response=status_data,
                        )

                    if status_data.get("status") == "FAILED":
                        return ProviderResponse(
                            success=False,
                            provider_name=self.name,
                            capability=request.capability,
                            error_message=f"Task failed: {status_data.get('error', 'Unknown')}",
                            error_code="TASK_FAILED",
                        )

                return ProviderResponse(
                    success=False,
                    provider_name=self.name,
                    capability=request.capability,
                    error_message="Task timed out",
                    error_code="TIMEOUT",
                )

        except httpx.HTTPStatusError as e:
            return ProviderResponse(
                success=False,
                provider_name=self.name,
                capability=request.capability,
                error_message=f"HTTP error: {e.response.status_code}",
                error_code=str(e.response.status_code),
            )
        except Exception as e:
            return ProviderResponse(
                success=False,
                provider_name=self.name,
                capability=request.capability,
                error_message=str(e),
                error_code="EXCEPTION",
            )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self._api_url}/openapi/v1/multi-image-to-3d",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                return response.status_code != 401
        except Exception:
            return False
