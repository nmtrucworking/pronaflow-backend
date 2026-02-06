"""
Admin authentication and authorization utilities.
Implements separate admin auth flow (Admin ≠ User).
"""
from datetime import datetime, timedelta
from typing import Optional, List, Callable
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.admin import AdminUser
from app.services.admin import AdminRoleAssignmentService


def create_admin_access_token(
    admin_user_id: UUID,
    roles: List[str],
    permissions: List[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token for admin user."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": str(admin_user_id),
        "type": "admin",
        "roles": roles,
        "permissions": permissions,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_admin_token(token: str) -> dict:
    """Verify admin JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _extract_bearer_token(token: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if token:
        return token
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return authorization


async def get_current_admin_user(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> AdminUser:
    """Get current admin user from admin JWT token."""
    raw_token = _extract_bearer_token(token, authorization)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_admin_token(raw_token)
    admin_user_id = payload.get("sub")
    if not admin_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin_user = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin_user.is_active or admin_user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is not active or is locked",
        )

    return admin_user


def require_admin_roles(*role_names: str) -> Callable:
    """Require admin to have at least one role name."""
    async def checker(
        admin_user: AdminUser = Depends(get_current_admin_user),
        db: Session = Depends(get_db),
    ) -> AdminUser:
        service = AdminRoleAssignmentService(db)
        roles = service.get_user_roles(admin_user.id)
        role_set = {role.name for role in roles}
        if not role_set.intersection(set(role_names)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient admin role",
            )
        return admin_user

    return checker


def require_admin_permissions(*permission_names: str) -> Callable:
    """Require admin to have all specified permission names."""
    async def checker(
        admin_user: AdminUser = Depends(get_current_admin_user),
        db: Session = Depends(get_db),
    ) -> AdminUser:
        service = AdminRoleAssignmentService(db)
        permissions = set(service.get_user_permissions(admin_user.id))
        if not set(permission_names).issubset(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient admin permissions",
            )
        return admin_user

    return checker
