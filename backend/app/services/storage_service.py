"""
Storage Service — Abstraction for S3-compatible object storage (MinIO / AWS S3).
Handles uploading, downloading, generating presigned URLs, and deleting objects.
"""

import logging
from collections.abc import AsyncGenerator
import aioboto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageService:
    """Manages object storage operations using aioboto3."""

    def __init__(self) -> None:
        self.session = aioboto3.Session()
        # Common client config for S3/MinIO
        self.client_kwargs = {
            "service_name": "s3",
            "region_name": settings.s3_region,
            "aws_access_key_id": settings.s3_access_key,
            "aws_secret_access_key": settings.s3_secret_key,
            "endpoint_url": settings.s3_endpoint if settings.s3_endpoint else None,
            "config": Config(signature_version="s3v4"),
        }

    async def upload_file(
        self, bucket: str, key: str, file_data: bytes, mime_type: str = "application/octet-stream"
    ) -> bool:
        """Upload a file directly to the specified bucket and key."""
        try:
            async with self.session.client(**self.client_kwargs) as s3:
                await s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=file_data,
                    ContentType=mime_type,
                )
                logger.info(f"Successfully uploaded s3://{bucket}/{key}")
                return True
        except ClientError as e:
            logger.error(f"Failed to upload s3://{bucket}/{key}: {e}")
            return False

    async def download_file(self, bucket: str, key: str) -> bytes | None:
        """Download file data from the specified bucket and key."""
        try:
            async with self.session.client(**self.client_kwargs) as s3:
                response = await s3.get_object(Bucket=bucket, Key=key)
                async with response["Body"] as stream:
                    return await stream.read()
        except ClientError as e:
            logger.error(f"Failed to download s3://{bucket}/{key}: {e}")
            return None

    async def delete_file(self, bucket: str, key: str) -> bool:
        """Delete an object from the specified bucket."""
        try:
            async with self.session.client(**self.client_kwargs) as s3:
                await s3.delete_object(Bucket=bucket, Key=key)
                logger.info(f"Successfully deleted s3://{bucket}/{key}")
                return True
        except ClientError as e:
            logger.error(f"Failed to delete s3://{bucket}/{key}: {e}")
            return False

    async def generate_presigned_url(
        self, bucket: str, key: str, expires_in: int = 3600, method: str = "get_object"
    ) -> str | None:
        """Generate a presigned URL for GET or PUT operations."""
        try:
            async with self.session.client(**self.client_kwargs) as s3:
                url = await s3.generate_presigned_url(
                    ClientMethod=method,
                    Params={"Bucket": bucket, "Key": key},
                    ExpiresIn=expires_in,
                )
                return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for s3://{bucket}/{key}: {e}")
            return None


_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Singleton getter for the StorageService."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
