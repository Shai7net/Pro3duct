"""
DigitalTwin model — the core product spec with full ProductDigitalTwinSpec.
"""

from __future__ import annotations

import uuid
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TenantScopedModel

if TYPE_CHECKING:
    from app.models.project import Project


class TwinStatus(str, PyEnum):
    GENERATING = "generating"
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


class DigitalTwin(TenantScopedModel):
    __tablename__ = "digital_twins"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    status: Mapped[TwinStatus] = mapped_column(
        Enum(TwinStatus), default=TwinStatus.GENERATING, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # The full ProductDigitalTwinSpec as structured JSON
    spec: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Generated assets (S3 keys)
    glb_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    usdz_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    blend_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    thumbnail_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # PBR Maps
    pbr_maps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Quality metrics
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    validation_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Confidence and AI decision provenance
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_decisions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Publishing
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    publish_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    embed_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performance metrics
    triangle_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    texture_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="digital_twin")
