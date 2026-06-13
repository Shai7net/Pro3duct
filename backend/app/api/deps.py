"""
API Dependencies — FastAPI dependency injection for auth, tenant resolution, and DB sessions.
"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import decode_access_token
from app.models.user import User

security = HTTPBearer()


class CurrentUser:
    """Resolved authenticated user context."""

    def __init__(self, user_id: uuid.UUID, tenant_id: uuid.UUID, email: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.email = email


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CurrentUser:
    """
    Extract and validate JWT token, resolve user and tenant.
    Raises 401 if token is invalid or user is inactive.
    """
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = uuid.UUID(payload["sub"])
    tenant_id = uuid.UUID(payload["tenant_id"])

    # Verify user exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return CurrentUser(user_id=user_id, tenant_id=tenant_id, email=user.email)


# Type alias for convenience
AuthenticatedUser = Annotated[CurrentUser, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
