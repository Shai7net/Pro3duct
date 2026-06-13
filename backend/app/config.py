"""
Pro3duct Configuration — Centralized settings using Pydantic BaseSettings.
All config is loaded from environment variables / .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── General ──
    app_name: str = "Pro3duct"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    dev_auto_login: bool = False
    dev_user_email: str = "developer@pro3duct.local"
    dev_user_password: str = "development-only"
    dev_user_name: str = "Local Developer"

    # ── Database ──
    database_url: str = "postgresql+asyncpg://pro3duct:pro3duct_dev@localhost:5432/pro3duct"
    database_sync_url: str = "postgresql://pro3duct:pro3duct_dev@localhost:5432/pro3duct"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    # ── Redis ──
    redis_url: str = "redis://localhost:6379/0"

    # ── Object Storage ──
    s3_endpoint: str = "http://localhost:9000"
    s3_public_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "pro3duct_minio"
    s3_secret_key: str = "pro3duct_minio_secret"
    s3_bucket_assets: str = "pro3duct-assets"
    s3_bucket_models: str = "pro3duct-models"
    s3_bucket_published: str = "pro3duct-published"
    s3_region: str = "us-east-1"

    # ── Authentication ──
    jwt_secret: str = "your-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # ── Temporal ──
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "pro3duct"
    temporal_task_queue: str = "generation-pipeline"

    # ── AI Providers ──
    meshy_api_key: str = ""
    meshy_api_url: str = "https://api.meshy.ai"
    allow_demo_generation: bool = False
    meshy_target_polycount: int = 30000
    meshy_request_timeout_seconds: int = 2700
    meshy_poll_interval_seconds: int = 10
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # ── Encryption ──
    encryption_key: str = "your-32-byte-encryption-key-here"

    # ── CORS ──
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # ── Rate Limiting ──
    rate_limit_per_minute: int = 60

    # ── Logging ──
    log_level: str = "DEBUG"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
