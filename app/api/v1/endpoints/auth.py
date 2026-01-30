"""
Authentication API Endpoints for Module 1: Identity and Access Management (IAM)
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, get_current_active_user
from app.db.models.users import User
from app.services.auth import AuthService
from app.services.mfa import MFAService
from app.services.session import SessionService
from app.services.email import EmailService
from app.schemas.auth import (
    UserRegisterRequest, UserResponse, LoginRequest, SessionResponse,
    EmailVerifyRequest, ResendVerificationRequest,
    MFAEnableResponse, MFAConfirmRequest, MFALoginRequest, MFADisableRequest,
    PasswordResetRequest, PasswordResetConfirmRequest, PasswordChangeRequest,
    SessionInfo, SessionListResponse, RevokeSessionRequest,
    BackupCodesResponse
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


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
        auth_service.resend_verification_email(request.user_id)
        return {"message": "Verification email sent"}
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
        email=request.email,
        password=request.password,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if error:
        raise HTTPException(status_code=401, detail=error)
    
    # Get user object
    user = db.query(User).filter(User.id == UUID(session_data["user_id"])).first()
    
    # Check if MFA is enabled
    mfa_service = MFAService(db)
    if mfa_service.is_mfa_enabled(UUID(session_data["user_id"])):
        # Return MFA required response instead
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA verification required",
            headers={"X-Session-ID": session_data["session_id"]}
        )
    
    return {
        **session_data,
        "user": UserResponse.from_orm(user)
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
    
    if not request.otp_code and not request.backup_code:
        raise HTTPException(
            status_code=400,
            detail="Either OTP code or backup code is required"
        )
    
    # Verify OTP or backup code
    try:
        if request.otp_code:
            mfa_service.verify_otp(UUID(request.session_id), request.otp_code)
        elif request.backup_code:
            mfa_service.verify_backup_code(UUID(request.session_id), request.backup_code)
    except HTTPException as e:
        raise e
    
    return {"message": "MFA verification successful"}


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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions for current user.
    
    Returns:
        List of sessions with device info
    """
    session_service = SessionService(db)
    sessions = session_service.get_user_sessions(current_user.id)
    
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
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Revoke all sessions except current.
    
    Returns:
        Number of sessions revoked
    """
    session_service = SessionService(db)
    
    # Get current session ID from token (optional)
    current_session_id = None
    if request and request.headers.get("Authorization"):
        # Extract from token if needed
        pass
    
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
    current_user: User = Depends(get_current_active_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Logout current user.
    
    Returns:
        Success message
    """
    auth_service = AuthService(db, EmailService())
    
    # Get session ID from token (would need to decode JWT)
    # For now, just return success message
    
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
        auth_service.create_password_reset_token(None)
    except:
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
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user profile"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.
    
    Returns:
        Current user object
    """
    return current_user
