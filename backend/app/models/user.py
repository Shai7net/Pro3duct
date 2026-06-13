"""
User model — authentication and profile data.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import GlobalModel

if TYPE_CHECKING:
    from app.models.tenant import TenantMember


class User(GlobalModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # SSO
    sso_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sso_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    memberships: Mapped[list["TenantMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
