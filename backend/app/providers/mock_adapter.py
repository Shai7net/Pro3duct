"""
Mock Provider Adapter — for development and testing.
Simulates AI responses without making real API calls.
"""

import asyncio
import random
import time

from app.providers import Capability, ProviderAdapter, ProviderRequest, ProviderResponse


class MockProviderAdapter(ProviderAdapter):
    """
    Mock adapter that simulates all AI capabilities.
    Returns realistic-looking responses with configurable delays.
    """

    @property
    def name(self) -> str:
        return "mock"

    @property
    def display_name(self) -> str:
        return "Mock Provider (Development)"

    @property
    def capabilities(self) -> list[Capability]:
        return [
            Capability.VISION,
            Capability.MULTI_IMAGE_TO_3D,
            Capability.TEXTURE_GENERATION,
            Capability.SEGMENTATION,
            Capability.REASONING,
        ]

    @property
    def quality_tier(self) -> int:
        return 5

    @property
    def allows_data_retention(self) -> bool:
        return False

    @property
    def is_on_premise(self) -> bool:
        return True

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        """Simulate provider execution with realistic delays."""
        start = time.time()

        # Simulate processing time
        delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(delay)

        handlers = {
            Capability.VISION: self._handle_vision,
            Capability.MULTI_IMAGE_TO_3D: self._handle_3d_generation,
            Capability.TEXTURE_GENERATION: self._handle_texture,
            Capability.SEGMENTATION: self._handle_segmentation,
            Capability.REASONING: self._handle_reasoning,
        }

        handler = handlers.get(request.capability)
        if not handler:
            return ProviderResponse(
                success=False,
                provider_name=self.name,
                capability=request.capability,
                error_message=f"Unsupported capability: {request.capability}",
                error_code="UNSUPPORTED",
            )

        data = handler(request)
        duration = time.time() - start

        return ProviderResponse(
            success=True,
            provider_name=self.name,
            capability=request.capability,
            data=data,
            cost_cents=random.randint(5, 50),
            duration_seconds=duration,
        )

    def _handle_vision(self, request: ProviderRequest) -> dict:
        return {
            "analysis": {
                "product_type": "electronic_device",
                "parts_detected": [
                    {"name": "body", "confidence": 0.95, "type": "enclosure"},
                    {"name": "screen", "confidence": 0.92, "type": "display"},
                    {"name": "button_power", "confidence": 0.88, "type": "button"},
                    {"name": "port_usb", "confidence": 0.85, "type": "port"},
                ],
                "materials_detected": [
                    {"name": "plastic_matte", "region": "body", "confidence": 0.90},
                    {"name": "glass", "region": "screen", "confidence": 0.93},
                ],
                "dimensions_estimated": {"width": 0.15, "height": 0.08, "depth": 0.03},
                "interactions_suggested": [
                    {"part": "button_power", "type": "press", "action": "toggle_power"},
                    {"part": "screen", "type": "display", "content": "dynamic"},
                ],
            }
        }

    def _handle_3d_generation(self, request: ProviderRequest) -> dict:
        return {
            "model": {
                "format": "glb",
                "s3_key": f"generated/mock_{random.randint(1000,9999)}.glb",
                "triangle_count": random.randint(5000, 50000),
                "texture_resolution": 2048,
                "quality_score": random.uniform(0.7, 0.95),
            }
        }

    def _handle_texture(self, request: ProviderRequest) -> dict:
        return {
            "textures": {
                "base_color": "textures/base_color.png",
                "normal": "textures/normal.png",
                "metalness": "textures/metalness.png",
                "roughness": "textures/roughness.png",
                "ao": "textures/ao.png",
            }
        }

    def _handle_segmentation(self, request: ProviderRequest) -> dict:
        return {
            "segments": [
                {"label": "body", "mask_key": "masks/body.png", "area_percent": 60},
                {"label": "screen", "mask_key": "masks/screen.png", "area_percent": 25},
                {"label": "buttons", "mask_key": "masks/buttons.png", "area_percent": 5},
            ]
        }

    def _handle_reasoning(self, request: ProviderRequest) -> dict:
        return {
            "reasoning": {
                "product_category": "electronics",
                "suggested_interactions": [
                    "Power button toggles device on/off",
                    "Screen displays status information",
                    "USB port on the side for charging",
                ],
                "state_machine": {
                    "initial_state": "off",
                    "states": ["off", "on", "standby"],
                    "transitions": [
                        {"from": "off", "to": "on", "trigger": "press_power"},
                        {"from": "on", "to": "standby", "trigger": "idle_timeout"},
                        {"from": "on", "to": "off", "trigger": "press_power"},
                        {"from": "standby", "to": "on", "trigger": "press_power"},
                    ],
                },
            }
        }

    async def health_check(self) -> bool:
        return True
