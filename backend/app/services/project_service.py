"""
Project Service — Manages projects logic, pagination, and state updates.
"""

import uuid
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.project import Project, ProjectStatus, ProjectAsset
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Encapsulates business operations for Projects."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, tenant_id: uuid.UUID, creator_id: uuid.UUID, data: ProjectCreate) -> Project:
        """Create a new project scoped to the current tenant."""
        project = Project(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            category=data.category,
            quality_mode=data.quality_mode,
            privacy_policy=data.privacy_policy,
            brand=data.brand,
            model_number=data.model_number,
            product_url=data.product_url,
            width_mm=data.width_mm,
            height_mm=data.height_mm,
            depth_mm=data.depth_mm,
            weight_grams=data.weight_grams,
            budget_cents=data.budget_cents,
            created_by=creator_id,
            status=ProjectStatus.DRAFT,
        )
        self.db.add(project)
        await self.db.flush()
        return project

    async def list_projects(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> tuple[list[tuple[Project, int]], int]:
        """List projects with pagination, optional filter, and search. Returns (items_with_count, total_count)."""
        query = select(Project).where(Project.tenant_id == tenant_id)

        if status_filter:
            query = query.where(Project.status == status_filter)
        if search:
            query = query.where(Project.name.ilike(f"%{search}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginate
        query = query.order_by(Project.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        projects = result.scalars().all()

        # Join asset counts
        items = []
        for project in projects:
            asset_count_res = await self.db.execute(
                select(func.count()).where(ProjectAsset.project_id == project.id)
            )
            asset_count = asset_count_res.scalar() or 0
            items.append((project, asset_count))

        return items, total

    async def get_project(self, tenant_id: uuid.UUID, project_id: uuid.UUID) -> tuple[Project, int]:
        """Fetch project details along with asset counts."""
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.tenant_id == tenant_id,
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        asset_count_res = await self.db.execute(
            select(func.count()).where(ProjectAsset.project_id == project.id)
        )
        asset_count = asset_count_res.scalar() or 0

        return project, asset_count

    async def update_project(
        self, tenant_id: uuid.UUID, project_id: uuid.UUID, data: ProjectUpdate
    ) -> Project:
        """Update fields of an existing project."""
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.tenant_id == tenant_id,
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        await self.db.flush()
        return project

    async def delete_project(self, tenant_id: uuid.UUID, project_id: uuid.UUID) -> None:
        """Delete a project and cascade delete associated assets and records."""
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.tenant_id == tenant_id,
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        await self.db.delete(project)
        await self.db.flush()
