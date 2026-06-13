"""
Database configuration — Async SQLAlchemy engine and session factory.
Uses asyncpg for PostgreSQL with connection pooling.
"""

from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.db_base import Base

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Import all models to register them with Base.metadata
from app.models.tenant import Tenant, TenantMember
from app.models.user import User
from app.models.project import Project, ProjectAsset
from app.models.digital_twin import DigitalTwin
from app.models.job import GenerationJob, JobStep
from app.models.provider import ProviderStatus, ProviderUsageLog, SystemProvider, TenantProviderCredential
from app.models.audit import AuditLog


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (for development only — use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_system_providers()


async def seed_system_providers() -> None:
    """Ensure built-in provider definitions exist for local development."""
    async with async_session_factory() as session:
        existing = await session.execute(
            select(SystemProvider).where(SystemProvider.name == "meshy")
        )
        if existing.scalar_one_or_none():
            return

        session.add(
            SystemProvider(
                name="meshy",
                display_name="Meshy AI",
                provider_type="meshy",
                capabilities=["multi_image_to_3d"],
                status=ProviderStatus.ACTIVE,
                api_base_url=settings.meshy_api_url,
                quality_tier=7,
                cost_per_credit=0.01,
                max_concurrent=2,
                timeout_seconds=settings.meshy_request_timeout_seconds,
                allows_data_retention=True,
                is_on_premise=False,
                config={
                    "supports_data_uri": True,
                    "supported_image_formats": ["image/jpeg", "image/png"],
                    "max_images": 4,
                    "target_formats": ["glb"],
                },
            )
        )
        await session.commit()
