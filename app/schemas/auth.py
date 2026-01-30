"""
Pydantic schemas for Authentication API endpoints.
Includes request/response models for auth flows.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


# ============= User Registration =============

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=30, description="Username")
    password: str = Field(..., min_length=12, description="Password")
    full_name: Optional[str] = Field(None, description="User full name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }


class UserResponse(BaseModel):
    """User response"""
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    status: str
    email_verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Email Verification =============

class EmailVerifyRequest(BaseModel):
    """Email verification request"""
    user_id: UUID = Field(..., description="User ID")
    token: str = Field(..., description="Verification token from email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "token": "verification_token_from_email"
            }
        }


class ResendVerificationRequest(BaseModel):
    """Resend email verification request"""
    user_id: UUID = Field(..., description="User ID")


# ============= Login =============

class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class SessionResponse(BaseModel):
    """Login response - session data"""
    user_id: str
    session_id: str
    token: str
    expires_in: int  # seconds
    user: UserResponse
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "session_id_uuid",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "status": "active",
                    "email_verified_at": "2024-01-30T10:00:00Z",
                    "created_at": "2024-01-29T10:00:00Z"
                }
            }
        }


class MFARequiredResponse(BaseModel):
    """MFA required response - returned when MFA is enabled"""
    session_id: str
    requires_mfa: bool = True
    token: str  # Temporary token for MFA verification
    expires_in: int
    message: str = "Please provide 2FA code to complete login"


# ============= MFA =============

class MFAEnableResponse(BaseModel):
    """MFA enable response"""
    secret_key: str = Field(..., description="TOTP secret key")
    qr_code: str = Field(..., description="QR code as data URL")
    backup_codes: List[str] = Field(..., description="Backup codes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret_key": "JBSWY3DPEBLW64TMMQ======",
                "qr_code": "data:image/png;base64,iVBORw0KGgo...",
                "backup_codes": ["12345678", "87654321", "11223344"]
            }
        }


class MFAConfirmRequest(BaseModel):
    """MFA confirmation request"""
    otp_code: str = Field(..., pattern=r'^\d{6}$', description="6-digit OTP code")


class MFALoginRequest(BaseModel):
    """MFA login request"""
    session_id: str = Field(..., description="Session ID from login attempt")
    otp_code: Optional[str] = Field(None, pattern=r'^\d{6}$', description="6-digit OTP code")
    backup_code: Optional[str] = Field(None, description="Backup code (if OTP unavailable)")


class MFADisableRequest(BaseModel):
    """MFA disable request"""
    password: str = Field(..., description="User password for confirmation")


class BackupCodesResponse(BaseModel):
    """Backup codes response"""
    backup_codes: List[str]


# ============= Password Management =============

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation request"""
    user_id: UUID = Field(..., description="User ID")
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=12, description="New password")


class PasswordChangeRequest(BaseModel):
    """Password change request for authenticated users"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=12, description="New password")


# ============= Session Management =============

class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    device_info: str
    ip_address: Optional[str]
    geo_location: Optional[str]
    last_active_at: datetime
    created_at: datetime
    is_current: bool


class SessionListResponse(BaseModel):
    """List of sessions response"""
    sessions: List[SessionInfo]
    total: int


class RevokeSessionRequest(BaseModel):
    """Revoke session request"""
    session_id: UUID = Field(..., description="Session ID to revoke")


# ============= OAuth2 =============

class OAuthLoginRequest(BaseModel):
    """OAuth2 login request"""
    provider: str = Field(..., description="OAuth provider (google, github)")
    code: str = Field(..., description="Authorization code from provider")
    redirect_uri: str = Field(..., description="Redirect URI used in authorization request")


class OAuthCallbackResponse(BaseModel):
    """OAuth2 callback response"""
    authorization_url: str


# ============= Error Responses =============

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Email already registered",
                "error_code": "EMAIL_ALREADY_EXISTS"
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    detail: List[dict]
