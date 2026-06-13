"""
Provider Adapter Framework — unified interface for all AI providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Capability(str, Enum):
    VISION = "vision"
    MULTI_IMAGE_TO_3D = "multi_image_to_3d"
    TEXTURE_GENERATION = "texture_generation"
    SEGMENTATION = "segmentation"
    REASONING = "reasoning"


@dataclass
class ProviderRequest:
    """Unified request to any AI provider."""
    capability: Capability
    inputs: dict[str, Any]
    quality_tier: int = 5  # 1-10
    max_cost_cents: int = 1000
    timeout_seconds: int = 300
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResponse:
    """Unified response from any AI provider."""
    success: bool
    provider_name: str
    capability: Capability
    data: dict[str, Any] = field(default_factory=dict)
    cost_cents: int = 0
    duration_seconds: float = 0.0
    error_message: str | None = None
    error_code: str | None = None
    raw_response: Any = None


class ProviderAdapter(ABC):
    """
    Abstract base for all AI provider adapters.
    Each adapter must declare capabilities, handle requests,
    and report costs/errors in a standardized way.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider name."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> list[Capability]:
        """List of capabilities this provider supports."""
        ...

    @property
    @abstractmethod
    def quality_tier(self) -> int:
        """Quality tier 1-10 (10 = highest)."""
        ...

    @property
    def allows_data_retention(self) -> bool:
        """Whether the provider may retain uploaded data."""
        return True

    @property
    def is_on_premise(self) -> bool:
        """Whether this provider runs on-premise."""
        return False

    @abstractmethod
    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        """Execute a request against this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available."""
        ...

    def supports(self, capability: Capability) -> bool:
        """Check if this adapter supports a given capability."""
        return capability in self.capabilities
