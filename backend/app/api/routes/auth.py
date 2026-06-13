"""
Authentication routes — register, login, me.
"""

import uuid
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AuthenticatedUser, DBSession
from app.config import get_settings
from app.middleware.auth import create_access_token, hash_password, verify_password
from app.models.tenant import MemberRole, Tenant, TenantMember, TenantPlan
from app.models.user import User
from app.schemas import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(db: DBSession):
    """Create or reuse a local developer workspace and return a token."""
    if settings.environment != "development" or not settings.dev_auto_login:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    email = settings.dev_user_email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            hashed_password=hash_password(settings.dev_user_password),
            full_name=settings.dev_user_name,
            is_superuser=True,
        )
        db.add(user)
        await db.flush()
    else:
        user.full_name = settings.dev_user_name
        user.is_active = True
        user.is_superuser = True
        if not verify_password(settings.dev_user_password, user.hashed_password):
            user.hashed_password = hash_password(settings.dev_user_password)
        await db.flush()

    membership_result = await db.execute(
        select(TenantMember).where(TenantMember.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    if not membership:
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.slug == "local-development")
        )
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            tenant = Tenant(
                name="Local Development",
                slug="local-development",
                plan=TenantPlan.FREE,
            )
            db.add(tenant)
            await db.flush()

        membership = TenantMember(
            tenant_id=tenant.id,
            user_id=user.id,
            role=MemberRole.OWNER,
        )
        db.add(membership)
        await db.flush()

    token = create_access_token(
        user_id=user.id,
        tenant_id=membership.tenant_id,
        email=user.email,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiration_hours * 3600,
        user_id=str(user.id),
        tenant_id=str(membership.tenant_id),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: DBSession):
    """Register a new user and create their tenant/workspace."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()

    # Create tenant
    slug = data.tenant_name.lower().replace(" ", "-")[:100]
    # Ensure slug uniqueness
    slug_check = await db.execute(select(Tenant).where(Tenant.slug == slug))
    if slug_check.scalar_one_or_none():
        slug = f"{slug}-{str(user.id)[:8]}"

    tenant = Tenant(
        name=data.tenant_name,
        slug=slug,
        plan=TenantPlan.FREE,
    )
    db.add(tenant)
    await db.flush()

    # Create membership
    membership = TenantMember(
        tenant_id=tenant.id,
        user_id=user.id,
        role=MemberRole.OWNER,
    )
    db.add(membership)
    await db.flush()

    # Generate token
    token = create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        email=user.email,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiration_hours * 3600,
        user_id=str(user.id),
        tenant_id=str(tenant.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: DBSession):
    """Authenticate user and return JWT token."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Get user's primary tenant
    membership_result = await db.execute(
        select(TenantMember).where(TenantMember.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No workspace found",
        )

    token = create_access_token(
        user_id=user.id,
        tenant_id=membership.tenant_id,
        email=user.email,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiration_hours * 3600,
        user_id=str(user.id),
        tenant_id=str(membership.tenant_id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: AuthenticatedUser, db: DBSession):
    """Get current authenticated user info."""
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
    )
