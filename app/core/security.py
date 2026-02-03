"""
Security utilities for authentication and authorization.
Implements JWT token generation/verification, password hashing, and validation.
"""
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
import re

from app.core.config import settings
from app.db.session import get_db
from app.db.models.users import User, Session as SessionModel, LoginAttempt
from app.db.enums import UserStatus


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Strong hashing
)


# ============= Password & Validation Functions =============

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength according to requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long (max 255 characters)"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username according to requirements:
    - Only letters, numbers, underscores
    - No whitespace
    - 3-30 characters
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must be at most 30 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None


# ============= JWT Token Functions =============

def create_access_token(
    user_id: UUID,
    session_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID to encode in token
        session_id: Session ID to encode in token
        expires_delta: Custom token expiration time
        
    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(user_id),
        "session_id": str(session_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Tuple of (is_valid, payload, error_message)
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        
        if user_id is None or session_id is None:
            return False, None, "Invalid token payload"
        
        return True, payload, None
        
    except jwt.ExpiredSignatureError:
        return False, None, "Token has expired"
    except jwt.InvalidTokenError as e:
        return False, None, f"Invalid token: {str(e)}"


# ============= Brute-Force Protection =============

def check_brute_force(
    email: str,
    db: Session,
    max_attempts: int = 5,
    lockout_minutes: int = 15
) -> Tuple[bool, Optional[str]]:
    """
    Check if user account should be locked due to failed login attempts.
    
    Args:
        email: User email
        db: Database session
        max_attempts: Maximum failed attempts allowed
        lockout_minutes: Minutes to lock account after max attempts
        
    Returns:
        Tuple of (is_locked, error_message)
    """
    # Check failed attempts in the last lockout period
    lockout_threshold = datetime.utcnow() - timedelta(minutes=lockout_minutes)
    
    failed_attempts = db.query(LoginAttempt).filter(
        LoginAttempt.email == email,
        LoginAttempt.success == False,
        LoginAttempt.created_at >= lockout_threshold
    ).count()
    
    if failed_attempts >= max_attempts:
        return True, f"Account temporarily locked. Try again after {lockout_minutes} minutes."
    
    return False, None


def record_login_attempt(
    email: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    success: bool,
    reason: Optional[str],
    db: Session
) -> LoginAttempt:
    """
    Record a login attempt in the database.
    
    Args:
        email: User email
        ip_address: Client IP address
        user_agent: Client user agent
        success: Whether login was successful
        reason: Reason for failure (if not successful)
        db: Database session
        
    Returns:
        Created LoginAttempt record
    """
    attempt = LoginAttempt(
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        reason=reason
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


# ============= Current User Dependency =============

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token in Authorization header.
    
    Args:
        authorization: Authorization header (format: "Bearer <token>")
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token from Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_valid, payload, error_msg = verify_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg or "Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    
    # Verify session still exists and is not revoked
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.revoked_at == None
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    # Update session activity
    session.last_active_at = datetime.utcnow()
    db.commit()
    
    return user


async def get_current_user_with_session(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Tuple[User, UUID]:
    """
    Get the current authenticated user and session ID from JWT token in Authorization header.

    Returns:
        Tuple of (User, session_id)
    """
    # Extract token from Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_valid, payload, error_msg = verify_token(token)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg or "Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    session_id = payload.get("session_id")

    # Verify session still exists and is not revoked
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.revoked_at == None
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    return user, UUID(session_id)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify that current user is active.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if active
        
    Raises:
        HTTPException: If user is not active
    """
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

