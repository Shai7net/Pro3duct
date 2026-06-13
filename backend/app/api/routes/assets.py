"""
Asset upload routes — handles multi-file upload with validation.
"""

import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from app.api.deps import AuthenticatedUser, DBSession
from app.models.project import AssetType, Project, ProjectAsset
from app.schemas.project import AssetUploadResponse
from app.services.asset_service import AssetService

router = APIRouter(prefix="/projects/{project_id}/assets", tags=["Assets"])

# Allowed MIME types by asset type
ALLOWED_MIMES = {
    AssetType.IMAGE: {"image/jpeg", "image/png", "image/webp", "image/tiff"},
    AssetType.CAD: {
        "model/step", "application/step", "application/stp",
        "model/iges", "application/iges",
        "application/octet-stream",  # .step, .stp, .iges files
    },
    AssetType.DOCUMENT: {"application/pdf", "text/plain", "text/markdown"},
    AssetType.LOGO: {"image/png", "image/svg+xml", "image/webp"},
    AssetType.VIDEO: {"video/mp4", "video/webm", "video/quicktime"},
    AssetType.REFERENCE_3D: {
        "model/gltf-binary", "model/gltf+json",
        "application/octet-stream",  # .glb files
    },
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("", response_model=list[AssetUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_assets(
    project_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
    files: list[UploadFile] = File(...),
    asset_type: str = Form("image"),
):
    """Upload one or more assets to a project."""
    service = AssetService(db)
    responses = []
    for file in files:
        asset = await service.add_asset(
            tenant_id=current_user.tenant_id,
            project_id=project_id,
            file=file,
            asset_type_str=asset_type,
        )
        responses.append(
            AssetUploadResponse(
                id=str(asset.id),
                project_id=str(project_id),
                asset_type=asset.asset_type.value if hasattr(asset.asset_type, 'value') else asset.asset_type,
                filename=asset.filename,
                original_filename=asset.original_filename,
                file_size_bytes=asset.file_size_bytes,
                mime_type=asset.mime_type,
                is_validated=asset.is_validated,
                created_at=asset.created_at,
            )
        )
    return responses


@router.get("", response_model=list[AssetUploadResponse])
async def list_assets(
    project_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """List all assets for a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    assets_result = await db.execute(
        select(ProjectAsset).where(
            ProjectAsset.project_id == project_id,
            ProjectAsset.tenant_id == current_user.tenant_id,
        ).order_by(ProjectAsset.created_at)
    )
    assets = assets_result.scalars().all()

    return [
        AssetUploadResponse(
            id=str(a.id),
            project_id=str(project_id),
            asset_type=a.asset_type.value if hasattr(a.asset_type, 'value') else a.asset_type,
            filename=a.filename,
            original_filename=a.original_filename,
            file_size_bytes=a.file_size_bytes,
            mime_type=a.mime_type,
            is_validated=a.is_validated,
            validation_notes=a.validation_notes,
            created_at=a.created_at,
        )
        for a in assets
    ]


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    project_id: uuid.UUID,
    asset_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Delete an asset."""
    service = AssetService(db)
    await service.delete_asset(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
        asset_id=asset_id,
    )
