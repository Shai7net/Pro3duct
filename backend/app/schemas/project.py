"""
Pydantic schemas for Projects and Assets.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = "electronics"
    quality_mode: str = "commercial"
    privacy_policy: str = "standard"
    brand: str | None = None
    model_number: str | None = None
    product_url: str | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    depth_mm: float | None = None
    weight_grams: float | None = None
    budget_cents: int = 5000


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    quality_mode: str | None = None
    privacy_policy: str | None = None
    brand: str | None = None
    model_number: str | None = None
    product_url: str | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    depth_mm: float | None = None
    weight_grams: float | None = None
    budget_cents: int | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    category: str
    quality_mode: str
    privacy_policy: str
    status: str
    brand: str | None = None
    model_number: str | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    depth_mm: float | None = None
    weight_grams: float | None = None
    budget_cents: int
    asset_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int


class AssetUploadResponse(BaseModel):
    id: str
    project_id: str
    asset_type: str
    filename: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    is_validated: bool = False
    validation_notes: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
