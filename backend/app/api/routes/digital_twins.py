"""
Digital Twin routes — view, update spec, validate, and publish.
"""

import uuid

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.api.deps import AuthenticatedUser, DBSession
from app.config import get_settings
from app.models.digital_twin import DigitalTwin, TwinStatus
from app.schemas.digital_twin import (
    DigitalTwinResponse,
    DigitalTwinUpdate,
    PublishRequest,
    ValidateResponse,
)
from app.services.storage_service import get_storage_service

router = APIRouter(prefix="/digital-twins", tags=["Digital Twins"])
settings = get_settings()


def _twin_asset_url(twin_id: uuid.UUID | str, filename: str) -> str:
    return f"{settings.api_url.rstrip('/')}/api/v1/digital-twins/{twin_id}/{filename}"


def _response_from_twin(twin: DigitalTwin) -> DigitalTwinResponse:
    return DigitalTwinResponse(
        id=str(twin.id),
        project_id=str(twin.project_id),
        status=twin.status.value,
        version=twin.version,
        spec=twin.spec,
        glb_url=_twin_asset_url(twin.id, "model.glb") if twin.glb_key else None,
        usdz_url=_twin_asset_url(twin.id, "model.usdz") if twin.usdz_key else None,
        thumbnail_url=None,
        quality_score=twin.quality_score,
        ai_confidence=twin.ai_confidence,
        is_published=twin.is_published,
        publish_url=twin.publish_url,
        embed_code=twin.embed_code,
        triangle_count=twin.triangle_count,
        file_size_bytes=twin.file_size_bytes,
        created_at=twin.created_at,
        updated_at=twin.updated_at,
    )



@router.get("/project/{project_id}", response_model=DigitalTwinResponse)
async def get_digital_twin_by_project(
    project_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Get a digital twin by its project ID."""
    result = await db.execute(
        select(DigitalTwin).where(
            DigitalTwin.project_id == project_id,
            DigitalTwin.tenant_id == current_user.tenant_id,
        )
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found for this project")

    return _response_from_twin(twin)


@router.get("/{twin_id}/model.glb")
async def download_twin_glb(twin_id: uuid.UUID, db: DBSession):
    """Download the generated GLB for editor/viewer rendering."""
    result = await db.execute(select(DigitalTwin).where(DigitalTwin.id == twin_id))
    twin = result.scalar_one_or_none()
    if not twin or not twin.glb_key:
        raise HTTPException(status_code=404, detail="Generated GLB not found")

    storage = get_storage_service()
    file_bytes = await storage.download_file(settings.s3_bucket_models, twin.glb_key)
    if not file_bytes:
        raise HTTPException(status_code=404, detail="Generated GLB is missing from storage")

    return Response(
        content=file_bytes,
        media_type="model/gltf-binary",
        headers={"Cache-Control": "private, max-age=300"},
    )


@router.get("/{twin_id}/model.usdz")
async def download_twin_usdz(twin_id: uuid.UUID, db: DBSession):
    """Download the generated USDZ package if one exists."""
    result = await db.execute(select(DigitalTwin).where(DigitalTwin.id == twin_id))
    twin = result.scalar_one_or_none()
    if not twin or not twin.usdz_key:
        raise HTTPException(status_code=404, detail="Generated USDZ not found")

    storage = get_storage_service()
    file_bytes = await storage.download_file(settings.s3_bucket_models, twin.usdz_key)
    if not file_bytes:
        raise HTTPException(status_code=404, detail="Generated USDZ is missing from storage")

    return Response(
        content=file_bytes,
        media_type="model/vnd.usdz+zip",
        headers={"Cache-Control": "private, max-age=300"},
    )


@router.get("/public/{twin_id}", response_model=DigitalTwinResponse)
async def get_public_digital_twin(twin_id: uuid.UUID, db: DBSession):
    """Get a published digital twin for public embed pages."""
    result = await db.execute(
        select(DigitalTwin).where(
            DigitalTwin.id == twin_id,
            DigitalTwin.is_published.is_(True),
        )
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Published digital twin not found")

    return _response_from_twin(twin)


@router.get("/{twin_id}", response_model=DigitalTwinResponse)
async def get_digital_twin(

    twin_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Get a digital twin with its full spec."""
    result = await db.execute(
        select(DigitalTwin).where(
            DigitalTwin.id == twin_id,
            DigitalTwin.tenant_id == current_user.tenant_id,
        )
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    return _response_from_twin(twin)


@router.patch("/{twin_id}", response_model=DigitalTwinResponse)
async def update_digital_twin(
    twin_id: uuid.UUID,
    data: DigitalTwinUpdate,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Update a digital twin's spec (from the visual editor)."""
    result = await db.execute(
        select(DigitalTwin).where(
            DigitalTwin.id == twin_id,
            DigitalTwin.tenant_id == current_user.tenant_id,
        )
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    if data.spec is not None:
        twin.spec = data.spec
        twin.version += 1

    if data.status is not None:
        twin.status = TwinStatus(data.status)

    await db.flush()

    return _response_from_twin(twin)


@router.post("/{twin_id}/validate", response_model=ValidateResponse)
async def validate_digital_twin(
    twin_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Run quality and physics validation checks on a digital twin."""
    result = await db.execute(
        select(DigitalTwin).where(
            DigitalTwin.id == twin_id,
            DigitalTwin.tenant_id == current_user.tenant_id,
        )
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    errors = []
    warnings = []

    # Validate spec structure
    spec = twin.spec or {}

    if not spec.get("parts"):
        errors.append({
            "code": "NO_PARTS",
            "message": "Digital twin has no parts defined",
        })

    if not spec.get("product_name"):
        warnings.append({
            "code": "NO_NAME",
            "message": "Product name is not set",
        })

    # Check triangle count
    if twin.triangle_count and twin.triangle_count > 200000:
        warnings.append({
            "code": "HIGH_POLY",
            "message": f"Triangle count ({twin.triangle_count}) exceeds recommended maximum",
        })

    # Check state machine consistency
    state_machine = spec.get("state_machine", {})
    states = set(state_machine.get("states", []))
    for transition in state_machine.get("transitions", []):
        if transition.get("from_state") not in states:
            errors.append({
                "code": "INVALID_STATE",
                "message": f"Transition from unknown state: {transition.get('from_state')}",
            })

    is_valid = len(errors) == 0
    quality_score = 1.0 - (len(errors) * 0.2 + len(warnings) * 0.05)

    twin.validation_results = {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "quality_score": max(0, quality_score),
    }
    twin.quality_score = max(0, quality_score)
    await db.flush()

    return ValidateResponse(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        quality_score=max(0, quality_score),
    )


@router.post("/{twin_id}/publish")
async def publish_digital_twin(
    twin_id: uuid.UUID,
    data: PublishRequest,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Publish a digital twin — generate web package and embed code."""
    result = await db.execute(
        select(DigitalTwin).where(
            DigitalTwin.id == twin_id,
            DigitalTwin.tenant_id == current_user.tenant_id,
        )
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    # Check for critical quality issues
    if twin.validation_results:
        errors = twin.validation_results.get("errors", [])
        critical = [e for e in errors if e.get("code") in ("NO_PARTS",)]
        if critical:
            raise HTTPException(
                status_code=422,
                detail="Cannot publish: critical quality errors exist. Run validation first.",
            )

    # Generate publish URL and embed code
    publish_url = f"{settings.app_url.rstrip('/')}/embed/{twin.id}"
    embed_code = f'<iframe src="{publish_url}" width="100%" height="600" frameborder="0" allowfullscreen></iframe>'

    twin.is_published = True
    twin.publish_url = publish_url
    twin.embed_code = embed_code
    twin.status = TwinStatus.PUBLISHED
    await db.flush()

    return {
        "publish_url": publish_url,
        "embed_code": embed_code,
        "status": "published",
    }
