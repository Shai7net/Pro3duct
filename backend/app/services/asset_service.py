"""
Asset Service — Handles business logic for project assets.
Includes image resolution extraction, validation (MIME, size), and upload orchestration.
"""

import logging
import uuid
from io import BytesIO
from PIL import Image

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status

from app.models.project import AssetType, Project, ProjectAsset
from app.services.storage_service import get_storage_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


class AssetService:
    """Manages project upload assets, validations, and storage interaction."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_service()

    async def add_asset(
        self,
        tenant_id: uuid.UUID,
        project_id: uuid.UUID,
        file: UploadFile,
        asset_type_str: str,
    ) -> ProjectAsset:
        """Validate, upload to S3/MinIO, and record asset in DB."""
        # Check project
        project_result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.tenant_id == tenant_id,
            )
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied",
            )

        try:
            asset_type = AssetType(asset_type_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {asset_type_str}",
            )

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB",
            )

        # Basic metadata
        file_ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
        s3_key = f"tenants/{tenant_id}/projects/{project_id}/assets/{uuid.uuid4()}.{file_ext}"

        # Image extraction
        width_px = None
        height_px = None
        if asset_type == AssetType.IMAGE or asset_type == AssetType.LOGO:
            try:
                with Image.open(BytesIO(content)) as img:
                    width_px, height_px = img.size
            except Exception as e:
                logger.warning(f"Could not read image dimensions for {file.filename}: {e}")

        # Upload to Storage
        success = await self.storage.upload_file(
            bucket=settings.s3_bucket_assets,
            key=s3_key,
            file_data=content,
            mime_type=file.content_type or "application/octet-stream",
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload asset to object storage",
            )

        # Save to DB
        asset = ProjectAsset(
            tenant_id=tenant_id,
            project_id=project_id,
            asset_type=asset_type,
            filename=f"{uuid.uuid4()}.{file_ext}",
            original_filename=file.filename or "unknown",
            s3_key=s3_key,
            mime_type=file.content_type or "application/octet-stream",
            file_size_bytes=len(content),
            width_px=width_px,
            height_px=height_px,
            is_validated=False,
        )

        self.db.add(asset)
        await self.db.flush()
        return asset

    async def get_assets_by_project(self, tenant_id: uuid.UUID, project_id: uuid.UUID) -> list[ProjectAsset]:
        """List all assets associated with a project."""
        result = await self.db.execute(
            select(ProjectAsset).where(
                ProjectAsset.project_id == project_id,
                ProjectAsset.tenant_id == tenant_id,
            ).order_by(ProjectAsset.created_at)
        )
        return list(result.scalars().all())

    async def delete_asset(self, tenant_id: uuid.UUID, project_id: uuid.UUID, asset_id: uuid.UUID) -> None:
        """Delete an asset from database and storage."""
        result = await self.db.execute(
            select(ProjectAsset).where(
                ProjectAsset.id == asset_id,
                ProjectAsset.project_id == project_id,
                ProjectAsset.tenant_id == tenant_id,
            )
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )

        # Delete from storage
        await self.storage.delete_file(settings.s3_bucket_assets, asset.s3_key)

        # Delete from DB
        await self.db.delete(asset)
        await self.db.flush()
