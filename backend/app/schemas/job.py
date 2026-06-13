"""
Pydantic schemas for Jobs.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    quality_mode: str = "commercial"
    budget_cents: int | None = None
    preferred_provider: str | None = None


class JobResponse(BaseModel):
    id: str
    project_id: str
    status: str
    progress_percent: int
    current_step: str | None = None
    active_provider: str | None = None
    total_cost_cents: int
    error_message: str | None = None
    candidates: dict | None = None
    selected_candidate: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobStepResponse(BaseModel):
    id: str
    step_type: str
    status: str
    provider: str | None = None
    cost_cents: int
    duration_seconds: float | None = None
    output_data: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    steps: list[JobStepResponse] = []
