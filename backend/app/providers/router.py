"""
Provider Router — intelligent routing of requests to the best available provider.
Considers quality tier, privacy, cost, availability, and circuit breaker state.
"""

import logging
from dataclasses import dataclass, field

from app.providers import Capability, ProviderAdapter, ProviderRequest, ProviderResponse
from app.providers.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


@dataclass
class RoutingContext:
    """Context for routing decisions."""
    privacy_level: str = "standard"  # standard, restricted, private
    max_cost_cents: int = 1000
    min_quality_tier: int = 3
    preferred_provider: str | None = None


class ProviderRouter:
    """
    Routes AI requests to the best available provider.

    Selection criteria (in order):
    1. Capability match
    2. Privacy compliance
    3. Quality tier >= minimum
    4. Circuit breaker status (must be CLOSED or HALF_OPEN)
    5. Preferred provider (if specified)
    6. Highest quality tier first
    7. Lowest cost

    Will NOT fall back to a lower-quality provider if no qualifying
    provider is available — the task waits and reports to the user.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, ProviderAdapter] = {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    def register(self, adapter: ProviderAdapter) -> None:
        """Register a provider adapter."""
        self._adapters[adapter.name] = adapter
        self._circuit_breakers[adapter.name] = CircuitBreaker()
        logger.info(
            f"Registered provider: {adapter.name} "
            f"(capabilities: {[c.value for c in adapter.capabilities]})"
        )

    def _get_candidates(
        self,
        capability: Capability,
        context: RoutingContext,
    ) -> list[ProviderAdapter]:
        """Get ordered list of candidate providers for a request."""
        candidates = []

        for name, adapter in self._adapters.items():
            # Must support the capability
            if not adapter.supports(capability):
                continue

            # Privacy check
            if context.privacy_level == "private" and not adapter.is_on_premise:
                continue
            if context.privacy_level == "restricted" and adapter.allows_data_retention:
                continue

            # Quality check
            if adapter.quality_tier < context.min_quality_tier:
                continue

            # Circuit breaker check
            cb = self._circuit_breakers[name]
            if not cb.can_execute():
                logger.warning(f"Provider {name} circuit is open, skipping")
                continue

            candidates.append(adapter)

        # Sort: preferred first, then by quality tier (desc)
        def sort_key(a: ProviderAdapter) -> tuple:
            is_preferred = a.name == context.preferred_provider
            return (not is_preferred, -a.quality_tier)

        candidates.sort(key=sort_key)
        return candidates

    async def route(
        self,
        request: ProviderRequest,
        context: RoutingContext | None = None,
    ) -> ProviderResponse:
        """
        Route a request to the best available provider.
        Tries providers in order until one succeeds.
        """
        ctx = context or RoutingContext()
        candidates = self._get_candidates(request.capability, ctx)

        if not candidates:
            return ProviderResponse(
                success=False,
                provider_name="none",
                capability=request.capability,
                error_message=(
                    "No provider available that meets quality and privacy requirements. "
                    "Please check provider configuration or wait for cooldown."
                ),
                error_code="NO_PROVIDER",
            )

        last_error = None
        for adapter in candidates:
            cb = self._circuit_breakers[adapter.name]
            try:
                logger.info(f"Routing {request.capability.value} to {adapter.name}")
                response = await adapter.execute(request)

                if response.success:
                    cb.record_success()
                    return response
                else:
                    cb.record_failure(response.error_code)
                    last_error = response
                    logger.warning(
                        f"Provider {adapter.name} returned error: {response.error_message}"
                    )

            except Exception as e:
                cb.record_failure("EXCEPTION")
                last_error = ProviderResponse(
                    success=False,
                    provider_name=adapter.name,
                    capability=request.capability,
                    error_message=str(e),
                    error_code="EXCEPTION",
                )
                logger.error(f"Provider {adapter.name} raised exception: {e}")

        return last_error or ProviderResponse(
            success=False,
            provider_name="none",
            capability=request.capability,
            error_message="All providers failed",
            error_code="ALL_FAILED",
        )

    def get_provider_status(self) -> dict[str, dict]:
        """Get status of all registered providers."""
        status = {}
        for name, adapter in self._adapters.items():
            cb = self._circuit_breakers[name]
            status[name] = {
                "display_name": adapter.display_name,
                "capabilities": [c.value for c in adapter.capabilities],
                "quality_tier": adapter.quality_tier,
                "circuit_state": cb.state.value,
                "failure_count": cb.failure_count,
                "can_execute": cb.can_execute(),
            }
        return status
