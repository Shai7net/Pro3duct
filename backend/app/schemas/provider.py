"""
Pydantic schemas for AI Providers.
"""

from pydantic import BaseModel, Field


class ProviderCredentialCreate(BaseModel):
    provider_name: str = Field(min_length=1, max_length=100)
    api_key: str = Field(min_length=1)
    label: str | None = None


class ProviderCredentialResponse(BaseModel):
    id: str
    provider_name: str
    label: str | None = None
    is_active: bool
    total_requests: int
    total_cost_cents: int

    class Config:
        from_attributes = True


class SystemProviderResponse(BaseModel):
    name: str
    display_name: str
    provider_type: str
    capabilities: list[str]
    status: str
    quality_tier: int
    is_on_premise: bool

    class Config:
        from_attributes = True
