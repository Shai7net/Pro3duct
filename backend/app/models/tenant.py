"""
Tenant model — represents an organization/workspace in the multi-tenant system.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models import GlobalModel, TimestampMixin


class TenantPlan(str, PyEnum):
    FREE = "free"
    PRO = "pro"
    STUDIO = "studio"
    ENTERPRISE = "enterprise"


class MemberRole(str, PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Tenant(GlobalModel):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[TenantPlan] = mapped_column(
        Enum(TenantPlan), default=TenantPlan.FREE, nullable=False
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Billing
    daily_budget_cents: Mapped[int] = mapped_column(default=10000, nullable=False)  # $100
    monthly_budget_cents: Mapped[int] = mapped_column(default=500000, nullable=False)  # $5000

    # Relationships
    members: Mapped[list["TenantMember"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantMember(Base, TimestampMixin):
    __tablename__ = "tenant_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole), default=MemberRole.EDITOR, nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")
