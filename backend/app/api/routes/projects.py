"""
Project CRUD routes — create, list, get, update, delete projects.
All queries are scoped to the authenticated user's tenant.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import AuthenticatedUser, DBSession
from app.models.project import Project, ProjectAsset, ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


def _project_to_response(project: Project, asset_count: int = 0) -> ProjectResponse:
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        category=project.category.value if hasattr(project.category, 'value') else project.category,
        quality_mode=project.quality_mode.value if hasattr(project.quality_mode, 'value') else project.quality_mode,
        privacy_policy=project.privacy_policy.value if hasattr(project.privacy_policy, 'value') else project.privacy_policy,
        status=project.status.value if hasattr(project.status, 'value') else project.status,
        brand=project.brand,
        model_number=project.model_number,
        width_mm=project.width_mm,
        height_mm=project.height_mm,
        depth_mm=project.depth_mm,
        weight_grams=project.weight_grams,
        budget_cents=project.budget_cents,
        asset_count=asset_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Create a new project."""
    service = ProjectService(db)
    project = await service.create_project(
        tenant_id=current_user.tenant_id,
        creator_id=current_user.user_id,
        data=data,
    )
    return _project_to_response(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: AuthenticatedUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = None,
    search: str | None = None,
):
    """List projects for the current tenant with pagination and filters."""
    service = ProjectService(db)
    items, total = await service.list_projects(
        tenant_id=current_user.tenant_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        search=search,
    )
    return ProjectListResponse(
        items=[_project_to_response(proj, count) for proj, count in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Get a specific project by ID."""
    service = ProjectService(db)
    project, asset_count = await service.get_project(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
    )
    return _project_to_response(project, asset_count)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Update a project."""
    service = ProjectService(db)
    project = await service.update_project(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
        data=data,
    )
    # Get count
    _, asset_count = await service.get_project(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
    )
    return _project_to_response(project, asset_count)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: DBSession,
):
    """Delete a project and all associated data."""
    service = ProjectService(db)
    await service.delete_project(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
    )
