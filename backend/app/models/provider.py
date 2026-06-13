"""
Provider models — AI provider credentials and usage tracking.
Supports both system keys and BYOK (Bring Your Own Key).
"""

from __future__ import annotations

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import GlobalModel, TenantScopedModel


class ProviderCapability(str, PyEnum):
    VISION = "vision"
    MULTI_IMAGE_TO_3D = "multi_image_to_3d"
    TEXTURE_GENERATION = "texture_generation"
    SEGMENTATION = "segmentation"
    REASONING = "reasoning"
    TEXT_TO_3D = "text_to_3d"


class ProviderStatus(str, PyEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    COOLDOWN = "cooldown"


class SystemProvider(GlobalModel):
    """System-level provider configuration (managed by platform admins)."""
    __tablename__ = "system_providers"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(100), nullable=False)  # meshy, openai, etc.
    capabilities: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[ProviderStatus] = mapped_column(
        Enum(ProviderStatus), default=ProviderStatus.ACTIVE, nullable=False
    )
    api_base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    encrypted_api_key: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Quality and routing
    quality_tier: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1-10
    cost_per_credit: Mapped[float] = mapped_column(Float, default=0.01, nullable=False)
    max_concurrent: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)

    # Privacy
    allows_data_retention: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_on_premise: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Circuit breaker state
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    circuit_open: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Configuration
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class TenantProviderCredential(TenantScopedModel):
    """BYOK — tenant's own API keys for providers."""
    __tablename__ = "tenant_provider_credentials"

    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(String(2000), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Usage tracking
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ProviderUsageLog(TenantScopedModel):
    """Per-request usage log for cost tracking and analytics."""
    __tablename__ = "provider_usage_logs"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_jobs.id"), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    capability: Mapped[ProviderCapability] = mapped_column(
        Enum(ProviderCapability), nullable=False
    )
    cost_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_byok: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    request_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
