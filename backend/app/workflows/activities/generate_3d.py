"""
Temporal Activity: real 3D candidate model generation.

Loads uploaded project images from local object storage, converts them to Meshy-compatible
Data URIs, creates a Multi-Image-to-3D task, downloads the generated GLB, and stores it
back in Pro3duct's local S3-compatible storage.
"""

from __future__ import annotations

import base64
import logging
import time
import uuid
from io import BytesIO
from typing import Any

import httpx
from PIL import Image, ImageOps
from sqlalchemy import select
from temporalio import activity

from app.config import get_settings
from app.database import async_session_factory
from app.models.job import JobStatus, JobStepType
from app.models.project import AssetType, ProjectAsset, ProjectStatus
from app.models.provider import TenantProviderCredential
from app.providers import Capability, ProviderRequest
from app.providers.meshy_adapter import MeshyAdapter
from app.providers.mock_adapter import MockProviderAdapter
from app.providers.router import ProviderRouter, RoutingContext
from app.services.provider_service import get_provider_service
from app.services.storage_service import get_storage_service
from app.workflows.activities.db_helper import (
    create_or_update_step,
    update_job,
    update_project_status,
)

logger = logging.getLogger(__name__)

MAX_MESHY_IMAGES = 4
MAX_IMAGE_SIDE_PX = 2048


def _input_value(input_data: Any, key: str, default: Any = None) -> Any:
    if isinstance(input_data, dict):
        return input_data.get(key, default)
    return getattr(input_data, key, default)


def _image_to_data_uri(image_bytes: bytes) -> tuple[str, str, int]:
    """Normalize any uploaded image to JPEG/PNG Data URI accepted by Meshy."""
    with Image.open(BytesIO(image_bytes)) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((MAX_IMAGE_SIDE_PX, MAX_IMAGE_SIDE_PX), Image.Resampling.LANCZOS)

        has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
        output = BytesIO()
        if has_alpha:
            image.save(output, format="PNG", optimize=True)
            mime_type = "image/png"
        else:
            image.convert("RGB").save(output, format="JPEG", quality=92, optimize=True)
            mime_type = "image/jpeg"

    normalized = output.getvalue()
    encoded = base64.b64encode(normalized).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", mime_type, len(normalized)


async def _resolve_meshy_api_key(tenant_id: str | None) -> tuple[str | None, bool]:
    """Return a Meshy API key from env first, then tenant BYOK credentials."""
    settings = get_settings()
    if settings.meshy_api_key.strip():
        return settings.meshy_api_key.strip(), False

    if not tenant_id:
        return None, False

    provider_service = get_provider_service()
    async with async_session_factory() as session:
        result = await session.execute(
            select(TenantProviderCredential).where(
                TenantProviderCredential.tenant_id == uuid.UUID(tenant_id),
                TenantProviderCredential.is_active.is_(True),
            )
        )
        credentials = result.scalars().all()

    for credential in credentials:
        provider_name = credential.provider_name.lower().strip()
        if provider_name in {"meshy", "meshy ai"}:
            api_key = provider_service.decrypt_key(credential.encrypted_api_key)
            if api_key:
                return api_key, True

    return None, False


async def _load_project_image_data_uris(project_id: str) -> list[dict[str, Any]]:
    """Load up to four project images from storage and convert them to Meshy input."""
    storage = get_storage_service()
    settings = get_settings()

    async with async_session_factory() as session:
        result = await session.execute(
            select(ProjectAsset)
            .where(
                ProjectAsset.project_id == uuid.UUID(project_id),
                ProjectAsset.asset_type == AssetType.IMAGE,
            )
            .order_by(ProjectAsset.created_at)
        )
        image_assets = list(result.scalars().all())[:MAX_MESHY_IMAGES]

    images: list[dict[str, Any]] = []
    for asset in image_assets:
        image_bytes = await storage.download_file(settings.s3_bucket_assets, asset.s3_key)
        if not image_bytes:
            logger.warning("Could not download source image %s from storage", asset.s3_key)
            continue

        try:
            data_uri, mime_type, normalized_size = _image_to_data_uri(image_bytes)
        except Exception as exc:
            logger.warning("Could not normalize image %s: %s", asset.original_filename, exc)
            continue

        images.append(
            {
                "asset_id": str(asset.id),
                "filename": asset.original_filename,
                "mime_type": mime_type,
                "size_bytes": normalized_size,
                "data_uri": data_uri,
            }
        )

    return images


async def _store_provider_model(project_id: str, job_id: str, model_url: str) -> tuple[str, int]:
    """Download the provider GLB URL before it expires and store it locally."""
    settings = get_settings()
    storage = get_storage_service()

    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
        response = await client.get(model_url)
        response.raise_for_status()
        model_bytes = response.content

    if not model_bytes:
        raise ValueError("Provider returned an empty GLB file")

    s3_key = f"tenants/generated/{project_id}/{job_id}/{uuid.uuid4()}.glb"
    uploaded = await storage.upload_file(
        bucket=settings.s3_bucket_assets,
        key=s3_key,
        file_data=model_bytes,
        mime_type="model/gltf-binary",
    )
    if not uploaded:
        raise ValueError("Failed to save generated GLB to local object storage")

    return s3_key, len(model_bytes)


async def _fail_generation(
    job_id: str,
    project_id: str,
    message: str,
    *,
    provider: str | None = None,
    code: str | None = None,
    duration: float | None = None,
) -> dict:
    await update_job(
        job_id=job_id,
        status=JobStatus.FAILED,
        progress_percent=30,
        current_step="3D candidate generation failed",
        error_message=message,
    )
    await update_project_status(project_id, ProjectStatus.DRAFT)
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.THREE_D_GENERATION,
        status=JobStatus.FAILED,
        provider=provider,
        duration_seconds=duration,
        error_details={"error": message, "code": code},
    )
    return {"candidates": [], "error": message}


@activity.defn
async def generate_3d_candidates(input_data: dict) -> dict:
    """Runs real Multi-Image-to-3D generation using uploaded project images."""
    job_id = _input_value(input_data, "job_id")
    project_id = _input_value(input_data, "project_id")
    tenant_id = _input_value(input_data, "tenant_id")
    preferred_provider = _input_value(input_data, "preferred_provider", "meshy")

    logger.info("Starting 3D generation for job %s, project %s", job_id, project_id)

    await update_job(
        job_id=job_id,
        status=JobStatus.GENERATING,
        progress_percent=30,
        current_step="Preparing uploaded photos for real 3D generation",
    )
    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.THREE_D_GENERATION,
        status=JobStatus.GENERATING,
        input_data={"project_id": project_id},
    )

    start_time = time.time()
    settings = get_settings()

    source_images = await _load_project_image_data_uris(project_id)
    if not source_images:
        return await _fail_generation(
            job_id,
            project_id,
            "לא נמצאו תמונות תקינות לשליחה ליצירת מודל תלת-ממדי.",
            code="NO_VALID_IMAGES",
            duration=time.time() - start_time,
        )

    meshy_api_key, is_byok = await _resolve_meshy_api_key(tenant_id)
    if not meshy_api_key and not settings.allow_demo_generation:
        return await _fail_generation(
            job_id,
            project_id,
            (
                "חסר מפתח Meshy API. הוסף מפתח במסך הגדרות וחיבורי AI, "
                "או הגדר MESHY_API_KEY בקובץ .env, ואז נסה שוב."
            ),
            code="MISSING_MESHY_API_KEY",
            duration=time.time() - start_time,
        )

    router = ProviderRouter()
    if meshy_api_key:
        router.register(MeshyAdapter(meshy_api_key, settings.meshy_api_url))
    if settings.allow_demo_generation:
        router.register(MockProviderAdapter())

    request = ProviderRequest(
        capability=Capability.MULTI_IMAGE_TO_3D,
        inputs={
            "project_id": project_id,
            "image_urls": [image["data_uri"] for image in source_images],
            "image_asset_ids": [image["asset_id"] for image in source_images],
            "ai_model": "meshy-6",
            "should_texture": True,
            "enable_pbr": True,
            "target_formats": ["glb"],
            "should_remesh": True,
            "target_polycount": settings.meshy_target_polycount,
            "image_enhancement": True,
            "remove_lighting": True,
            "poll_interval_seconds": settings.meshy_poll_interval_seconds,
        },
        timeout_seconds=settings.meshy_request_timeout_seconds,
        metadata={"is_byok": is_byok, "source_image_count": len(source_images)},
    )

    context = RoutingContext(
        privacy_level="standard",
        min_quality_tier=3,
        preferred_provider=preferred_provider,
    )

    response = await router.route(request, context)
    duration = time.time() - start_time

    if not response.success:
        return await _fail_generation(
            job_id,
            project_id,
            response.error_message or "AI Generation failed",
            provider=response.provider_name,
            code=response.error_code,
            duration=duration,
        )

    model_data = response.data.get("model", {})
    model_url = model_data.get("model_url")
    s3_key = model_data.get("s3_key")
    file_size_bytes = model_data.get("file_size_bytes")

    if model_url:
        try:
            s3_key, file_size_bytes = await _store_provider_model(project_id, job_id, model_url)
        except Exception as exc:
            return await _fail_generation(
                job_id,
                project_id,
                f"המודל נוצר אצל הספק, אבל שמירת קובץ ה-GLB נכשלה: {exc}",
                provider=response.provider_name,
                code="MODEL_DOWNLOAD_FAILED",
                duration=time.time() - start_time,
            )

    if not s3_key:
        return await _fail_generation(
            job_id,
            project_id,
            "הספק לא החזיר קובץ GLB שניתן לשמור.",
            provider=response.provider_name,
            code="MISSING_MODEL_OUTPUT",
            duration=time.time() - start_time,
        )

    triangle_count = model_data.get("triangle_count", settings.meshy_target_polycount)
    candidates = [
        {
            "id": 0,
            "provider": response.provider_name,
            "format": model_data.get("format", "glb"),
            "s3_key": s3_key,
            "triangle_count": triangle_count,
            "quality_score": model_data.get("quality_score", 0.88),
            "cost_cents": response.cost_cents,
            "file_size_bytes": file_size_bytes,
            "provider_task_id": model_data.get("task_id"),
            "source_image_count": len(source_images),
            "is_byok": is_byok,
        }
    ]

    await update_job(
        job_id=job_id,
        status=JobStatus.GENERATING,
        progress_percent=45,
        current_step="Real 3D candidate model generated successfully",
        active_provider=response.provider_name,
        total_cost_cents=response.cost_cents,
        candidates={"candidates": candidates},
        selected_candidate=0,
    )

    await create_or_update_step(
        job_id=job_id,
        step_type=JobStepType.THREE_D_GENERATION,
        status=JobStatus.COMPLETED,
        provider=response.provider_name,
        cost_cents=response.cost_cents,
        duration_seconds=time.time() - start_time,
        output_data={
            "candidates": candidates,
            "source_images": [
                {
                    "asset_id": image["asset_id"],
                    "filename": image["filename"],
                    "mime_type": image["mime_type"],
                    "size_bytes": image["size_bytes"],
                }
                for image in source_images
            ],
        },
    )

    return {"candidates": candidates}
