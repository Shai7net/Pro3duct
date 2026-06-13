"""
Provider credential routes — BYOK key management.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AuthenticatedUser, DBSession
from app.models.provider import SystemProvider, TenantProviderCredential
from app.schemas.provider import (
    ProviderCredentialCreate,
    ProviderCredentialResponse,
    SystemProviderResponse,
)

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/system", response_model=list[SystemProviderResponse])
async def list_system_providers(
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """List all available system AI providers."""
    result = await db.execute(select(SystemProvider).order_by(SystemProvider.quality_tier.desc()))
    providers = result.scalars().all()

    return [
        SystemProviderResponse(
            name=p.name,
            display_name=p.display_name,
            provider_type=p.provider_type,
            capabilities=p.capabilities,
            status=p.status.value,
            quality_tier=p.quality_tier,
            is_on_premise=p.is_on_premise,
        )
        for p in providers
    ]


from app.services.provider_service import get_provider_service

@router.post(
    "/credentials",
    response_model=ProviderCredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_provider_credential(
    data: ProviderCredentialCreate,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Add a BYOK API key for a provider."""
    provider_service = get_provider_service()
    encrypted_key = provider_service.encrypt_key(data.api_key)

    credential = TenantProviderCredential(
        tenant_id=current_user.tenant_id,
        provider_name=data.provider_name,
        encrypted_api_key=encrypted_key,
        label=data.label,
    )
    db.add(credential)
    await db.flush()

    return ProviderCredentialResponse(
        id=str(credential.id),
        provider_name=credential.provider_name,
        label=credential.label,
        is_active=credential.is_active,
        total_requests=0,
        total_cost_cents=0,
    )


@router.get("/credentials", response_model=list[ProviderCredentialResponse])
async def list_provider_credentials(
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """List tenant's BYOK credentials (keys are never exposed)."""
    result = await db.execute(
        select(TenantProviderCredential).where(
            TenantProviderCredential.tenant_id == current_user.tenant_id,
        )
    )
    credentials = result.scalars().all()

    return [
        ProviderCredentialResponse(
            id=str(c.id),
            provider_name=c.provider_name,
            label=c.label,
            is_active=c.is_active,
            total_requests=c.total_requests,
            total_cost_cents=c.total_cost_cents,
        )
        for c in credentials
    ]


@router.delete("/credentials/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider_credential(
    credential_id: str,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Remove a BYOK credential."""
    import uuid as uuid_mod
    result = await db.execute(
        select(TenantProviderCredential).where(
            TenantProviderCredential.id == uuid_mod.UUID(credential_id),
            TenantProviderCredential.tenant_id == current_user.tenant_id,
        )
    )
    credential = result.scalar_one_or_none()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    await db.delete(credential)
