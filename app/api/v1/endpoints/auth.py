"""
Authentication API Endpoints for Module 1: Identity and Access Management (IAM)
"""
from typing import Optional, Tuple
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import (
    get_current_active_user,
    get_current_user_with_session,
    verify_token,
    create_access_token,
    create_refresh_token,
)
from app.core.config import settings
from app.models.users import User, Session as SessionModel
from app.services.auth import AuthService
from app.services.mfa import MFAService
from app.services.session import SessionService
from app.services.email import EmailService
from app.schemas.auth import (
    UserRegisterRequest, UserResponse, LoginRequest, SessionResponse,
    FrontendUserResponse,
    EmailVerifyRequest, ResendVerificationRequest,
    MFAEnableResponse, MFAConfirmRequest, MFALoginRequest, MFADisableRequest,
    RefreshTokenRequest, RefreshTokenResponse,
    PasswordResetRequest, PasswordResetConfirmRequest, PasswordChangeRequest,
    SessionInfo, SessionListResponse, RevokeSessionRequest,
    BackupCodesResponse
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _serialize_frontend_user(user: User, db: Session) -> dict:
    """Build frontend-compatible user payload."""
    mfa_enabled = MFAService(db).is_mfa_enabled(user.id)
    roles = [role.role_name for role in user.roles] if user.roles else []

    return {
        "user_id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "status": getattr(user.status, "value", str(user.status)),
        "email_verified_at": user.email_verified_at,
        "mfa_enabled": mfa_enabled,
        "roles": roles,
        "created_at": user.created_at,
    }


# ============= User Registration =============

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user account with email verification"
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - Email verification is required before full account activation
    - Password must meet strength requirements
    - Username must be unique
    
    Returns:
        Created user object
    """
    auth_service = AuthService(db, EmailService())
    user, error = auth_service.register_user(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return user


# ============= Email Verification =============

@router.post(
    "/verify-email",
    summary="Verify Email",
    description="Verify user email with token from verification email"
)
async def verify_email(
    request: EmailVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token.
    
    Returns:
        Success message
    """
    auth_service = AuthService(db, EmailService())
    
    try:
        auth_service.verify_email(request.user_id, request.token)
        return {"message": "Email verified successfully"}
    except HTTPException as e:
        raise e


@router.post(
    "/resend-verification",
    summary="Resend Verification Email",
    description="Resend email verification link"
)
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend email verification token.
    
    Returns:
        Success message
    """
    auth_service = AuthService(db, EmailService())
    
    try:
        if request.user_id:
            auth_service.resend_verification_email(request.user_id)
            return {"message": "Verification email sent"}

        user = db.query(User).filter(User.email == request.email).first()
        if user:
            auth_service.resend_verification_email(user.id)
        return {"message": "If account exists, verification email has been sent"}
    except HTTPException as e:
        raise e


# ============= Login =============

@router.post(
    "/login",
    response_model=SessionResponse,
    summary="User Login",
    description="Authenticate user and create session"
)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password.
    
    Returns:
        Session with JWT token
        
    Raises:
        - 401: Invalid credentials
        - 403: Account not verified or suspended
        - 429: Too many failed login attempts
    """
    # Get client IP
    client_ip = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("User-Agent")
    
    auth_service = AuthService(db, EmailService())
    
    session_data, error = auth_service.login(
        identifier=request.email,
        password=request.password,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if error:
        raise HTTPException(status_code=401, detail=error)
    
    # Get user object
    user = db.query(User).filter(User.id == UUID(session_data["user_id"])).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Frontend contract: success with mfa_required flag instead of 403.
    mfa_service = MFAService(db)
    mfa_required = mfa_service.is_mfa_enabled(UUID(session_data["user_id"]))

    return {
        **session_data,
        "token": "" if mfa_required else session_data["token"],
        "access_token": "" if mfa_required else session_data["access_token"],
        "refresh_token": "" if mfa_required else session_data["refresh_token"],
        "token_type": "bearer",
        "mfa_required": mfa_required,
        "user": _serialize_frontend_user(user, db),
    }


# ============= MFA =============

@router.post(
    "/mfa/enable",
    response_model=MFAEnableResponse,
    summary="Enable MFA",
    description="Enable Multi-Factor Authentication for user"
)
async def enable_mfa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enable MFA with TOTP.
    
    Returns:
        Secret key, QR code, and backup codes
        User must confirm with valid OTP code
    """
    mfa_service = MFAService(db)
    
    secret, qr_code, backup_codes = mfa_service.enable_mfa(current_user.id)
    
    return {
        "secret_key": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes
    }


@router.post(
    "/mfa/confirm",
    summary="Confirm MFA",
    description="Confirm MFA setup with OTP code"
)
async def confirm_mfa(
    request: MFAConfirmRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Confirm MFA setup by entering OTP code.
    
    Returns:
        Success message with backup codes
    """
    mfa_service = MFAService(db)
    
    success, backup_codes = mfa_service.confirm_mfa(current_user.id, request.otp_code)
    
    return {
        "message": "MFA enabled successfully",
        "backup_codes": backup_codes
    }


@router.post(
    "/mfa/verify",
    response_model=SessionResponse,
    summary="Verify MFA Code",
    description="Verify TOTP or backup code during login"
)
async def verify_mfa(
    request: MFALoginRequest,
    db: Session = Depends(get_db)
):
    """
    Verify MFA code to complete login.
    
    Requires either OTP code or backup code.
    
    Returns:
        Session with JWT token
    """
    mfa_service = MFAService(db)

    session: Optional[SessionModel] = None
    user: Optional[User] = None

    if request.session_id:
        try:
            session_uuid = UUID(request.session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        session = db.query(SessionModel).filter(
            SessionModel.id == session_uuid,
            SessionModel.revoked_at == None
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or revoked")

        user = db.query(User).filter(User.id == session.user_id).first()
    else:
        user = db.query(User).filter(User.email == request.email).first()
        if user:
            session = db.query(SessionModel).filter(
                SessionModel.user_id == user.id,
                SessionModel.revoked_at == None
            ).order_by(SessionModel.created_at.desc()).first()

    if not session or not user:
        raise HTTPException(status_code=404, detail="Pending MFA session not found")
    
    # Verify OTP or backup code
    try:
        if request.otp_code:
            mfa_service.verify_otp(user.id, request.otp_code)
        elif request.backup_code:
            mfa_service.verify_backup_code(user.id, request.backup_code)
    except HTTPException as e:
        raise e

    access_token = create_access_token(user.id, session.id)
    refresh_token = create_refresh_token(user.id, session.id)
    session.token = access_token
    session.last_active_at = datetime.utcnow()
    db.commit()

    return {
        "user_id": str(user.id),
        "session_id": str(session.id),
        "token": access_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "mfa_required": False,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": _serialize_frontend_user(user, db),
    }


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh Access Token",
    description="Refresh access token using refresh token"
)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token for an active session.
    """
    is_valid, payload, error_msg = verify_token(request.refresh_token)
    if not is_valid:
        raise HTTPException(status_code=401, detail=error_msg or "Invalid refresh token")

    if payload.get("token_type") not in (None, "refresh"):
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    session_id = payload.get("session_id")

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.revoked_at == None
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Session has been revoked")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(user.id, session.id)
    refresh_token = create_refresh_token(user.id, session.id)
    session.token = access_token
    session.last_active_at = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/mfa/disable",
    summary="Disable MFA",
    description="Disable Multi-Factor Authentication"
)
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Disable MFA for current user.
    
    Requires password confirmation.
    
    Returns:
        Success message
    """
    mfa_service = MFAService(db)
    
    try:
        mfa_service.disable_mfa(current_user.id, request.password)
        return {"message": "MFA disabled successfully"}
    except HTTPException as e:
        raise e


@router.get(
    "/mfa/backup-codes",
    response_model=BackupCodesResponse,
    summary="Get Backup Codes Count",
    description="Get count of remaining backup codes"
)
async def get_backup_codes_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get unused backup codes count.
    
    Returns:
        Remaining backup codes count
    """
    mfa_service = MFAService(db)
    count = mfa_service.get_backup_codes_count(current_user.id)
    
    return {"backup_codes": [f"Code {i+1}" for i in range(count)]}


@router.post(
    "/mfa/regenerate-backup-codes",
    response_model=BackupCodesResponse,
    summary="Regenerate Backup Codes",
    description="Generate new backup codes (invalidates old ones)"
)
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup codes.
    
    Returns:
        New backup codes
    """
    mfa_service = MFAService(db)
    
    try:
        new_codes = mfa_service.regenerate_backup_codes(current_user.id)
        return {"backup_codes": new_codes}
    except HTTPException as e:
        raise e


# ============= Session Management =============

@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List Sessions",
    description="Get all active sessions for current user"
)
async def list_sessions(
    current_user_session: Tuple[User, UUID] = Depends(get_current_user_with_session),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions for current user.
    
    Returns:
        List of sessions with device info
    """
    current_user, current_session_id = current_user_session
    session_service = SessionService(db)
    sessions = session_service.get_user_sessions(current_user.id, current_session_id)
    
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@router.post(
    "/sessions/revoke",
    summary="Revoke Session",
    description="Logout from a specific device"
)
async def revoke_session(
    request: RevokeSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a specific session.
    
    Returns:
        Success message
    """
    session_service = SessionService(db)
    
    try:
        session_service.revoke_session(current_user.id, request.session_id)
        return {"message": "Session revoked successfully"}
    except HTTPException as e:
        raise e


@router.post(
    "/sessions/revoke-all",
    summary="Logout All Devices",
    description="Logout from all devices except current"
)
async def revoke_all_sessions(
    current_user_session: Tuple[User, UUID] = Depends(get_current_user_with_session),
    db: Session = Depends(get_db)
):
    """
    Revoke all sessions except current.
    
    Returns:
        Number of sessions revoked
    """
    current_user, current_session_id = current_user_session
    session_service = SessionService(db)

    count = session_service.revoke_all_sessions(current_user.id, current_session_id)
    
    return {
        "message": f"Logged out from {count} device(s)",
        "count": count
    }


# ============= Logout =============

@router.post(
    "/logout",
    summary="Logout",
    description="Logout current session"
)
async def logout(
    current_user_session: Tuple[User, UUID] = Depends(get_current_user_with_session),
    db: Session = Depends(get_db)
):
    """
    Logout current user.
    
    Returns:
        Success message
    """
    _, current_session_id = current_user_session
    auth_service = AuthService(db, EmailService())

    auth_service.logout(current_session_id)

    return {"message": "Logged out successfully"}


# ============= Password Management =============

@router.post(
    "/password-reset",
    summary="Request Password Reset",
    description="Send password reset email"
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset.
    
    Sends reset email with one-time link.
    
    Returns:
        Success message
    """
    auth_service = AuthService(db, EmailService())

    try:
        auth_service.request_password_reset(request.email)
    except Exception:
        # Don't reveal if email exists or not
        pass
    
    return {"message": "If email exists, password reset link has been sent"}


@router.post(
    "/password-reset/confirm",
    summary="Reset Password",
    description="Reset password with reset token"
)
async def reset_password(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with reset token.
    
    Returns:
        Success message
    """
    auth_service = AuthService(db, EmailService())
    
    try:
        auth_service.reset_password(request.user_id, request.token, request.new_password)
        return {"message": "Password reset successfully"}
    except HTTPException as e:
        raise e


@router.post(
    "/password-change",
    summary="Change Password",
    description="Change password for authenticated user"
)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change password for current user.
    
    Returns:
        Success message
    """
    auth_service = AuthService(db, EmailService())
    
    try:
        auth_service.change_password(
            current_user.id,
            request.current_password,
            request.new_password
        )
        return {"message": "Password changed successfully"}
    except HTTPException as e:
        raise e


# ============= User Profile =============

@router.get(
    "/me",
    response_model=FrontendUserResponse,
    summary="Get Current User",
    description="Get current authenticated user profile"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile.
    
    Returns:
        Current user object
    """
    return _serialize_frontend_user(current_user, db)


# ============= OAuth Social Login =============

@router.get(
    "/oauth/{provider}/authorize",
    summary="Get OAuth Authorization URL",
    description="Get OAuth authorization URL for social login"
)
async def oauth_authorize(
    provider: str,
    redirect_uri: Optional[str] = None
):
    """
    Get OAuth authorization URL for provider (google, github).
    
    Args:
        provider: OAuth provider name (google, github)
        redirect_uri: Optional custom redirect URI
        
    Returns:
        Authorization URL and state for CSRF protection
    """
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # TODO: Implement OAuth URL generation
    # This requires OAuth app configuration in environment
    raise HTTPException(
        status_code=501,
        detail="OAuth social login is not yet configured. Please set up OAuth credentials in environment variables."
    )


@router.post(
    "/oauth/{provider}/callback",
    response_model=SessionResponse,
    summary="OAuth Callback",
    description="Handle OAuth callback and create session"
)
async def oauth_callback(
    provider: str,
    code: str,
    state: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from provider.
    
    Creates new user if doesn't exist, or links to existing account.
    
    Args:
        provider: OAuth provider name
        code: Authorization code from OAuth provider
        state: State parameter for CSRF validation
        redirect_uri: Redirect URI used in OAuth flow
        
    Returns:
        Session with JWT token
    """
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # TODO: Implement OAuth callback handling
    # 1. Exchange code for access token
    # 2. Get user info from provider
    # 3. Create or link user account
    # 4. Create session
    
    raise HTTPException(
        status_code=501,
        detail="OAuth social login is not yet configured. Please set up OAuth credentials in environment variables."
    )
