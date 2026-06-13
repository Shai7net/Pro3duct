"""
Project and ProjectAsset models — organizing digital twin creation.
"""

from __future__ import annotations

import uuid
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TenantScopedModel

if TYPE_CHECKING:
    from app.models.digital_twin import DigitalTwin
    from app.models.job import GenerationJob


class ProductCategory(str, PyEnum):
    ELECTRONICS = "electronics"
    FURNITURE = "furniture"
    APPLIANCE = "appliance"
    PACKAGING = "packaging"
    INDUSTRIAL = "industrial"
    AUTOMOTIVE = "automotive"
    FASHION = "fashion"
    OTHER = "other"


class QualityMode(str, PyEnum):
    COMMERCIAL = "commercial"
    ENGINEERING = "engineering"


class PrivacyPolicy(str, PyEnum):
    STANDARD = "standard"          # Data can be sent to any provider
    RESTRICTED = "restricted"      # Only approved providers
    PRIVATE = "private"            # Only on-premise / private workers


class ProjectStatus(str, PyEnum):
    DRAFT = "draft"
    UPLOADING = "uploading"
    READY = "ready"
    GENERATING = "generating"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AssetType(str, PyEnum):
    IMAGE = "image"
    DIMENSIONS = "dimensions"
    CAD = "cad"
    DOCUMENT = "document"
    LOGO = "logo"
    VIDEO = "video"
    REFERENCE_3D = "reference_3d"


class Project(TenantScopedModel):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[ProductCategory] = mapped_column(
        Enum(ProductCategory), default=ProductCategory.ELECTRONICS, nullable=False
    )
    quality_mode: Mapped[QualityMode] = mapped_column(
        Enum(QualityMode), default=QualityMode.COMMERCIAL, nullable=False
    )
    privacy_policy: Mapped[PrivacyPolicy] = mapped_column(
        Enum(PrivacyPolicy), default=PrivacyPolicy.STANDARD, nullable=False
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False
    )

    # Product metadata
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Dimensions (in millimeters)
    width_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_grams: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Budget
    budget_cents: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)  # $50

    # Owner
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    assets: Mapped[list["ProjectAsset"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["GenerationJob"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    digital_twin: Mapped["DigitalTwin | None"] = relationship(
        back_populates="project", uselist=False
    )


class ProjectAsset(TenantScopedModel):
    __tablename__ = "project_assets"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Image-specific metadata
    width_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    angle_label: Mapped[str | None] = mapped_column(String(50), nullable=True)  # front, back, etc.

    # Validation results
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_notes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="assets")
