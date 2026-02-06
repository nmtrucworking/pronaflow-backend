"""
Authentication Service for Module 1: Identity and Access Management (IAM)
Handles user registration, login, email verification, and session management.
"""
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    hash_password, verify_password, validate_password_strength,
    validate_email, validate_username, create_access_token,
    record_login_attempt, check_brute_force
)
from app.models.users import (
    User, Session as SessionModel, PasswordResetToken,
    EmailVerificationToken
)
from app.db.enums import UserStatus
from app.services.email import EmailService


class AuthService:
    """
    Service for authentication operations.
    Handles registration, login, password management, and email verification.
    """
    
    def __init__(self, db: Session, email_service: Optional[EmailService] = None):
        self.db = db
        self.email_service = email_service or EmailService()
    
    # ============= User Registration =============
    
    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> Tuple[User, str]:
        """
        Register a new user with email verification requirement.
        
        Args:
            email: User email
            username: User username
            password: User password
            full_name: User full name (optional)
            
        Returns:
            Tuple of (created_user, error_message) - error_message is None on success
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate inputs
        is_valid, error = validate_email(email)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        is_valid, error = validate_username(username)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Username already taken"
            )
        
        # Create user with PENDING status
        hashed_password = hash_password(password)
        user = User(
            email=email,
            username=username,
            password_hash=hashed_password,
            status=UserStatus.PENDING,
            full_name=full_name
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create default workspace for the user (Module 2 - AC 2)
        self._create_default_workspace(user)
        
        # Create email verification token
        self._create_email_verification_token(user, email)
        
        return user, None
    
    def _create_default_workspace(self, user: User) -> None:
        """
        Create a default workspace for new user.
        
        Module 2 - AC 2: Default Workspace (Logic tự động)
        When user completes registration, system automatically creates a default workspace
        named "{Username}'s Workspace" so user can start working immediately.
        
        Args:
            user: The newly created user
        """
        from app.schemas.workspace import WorkspaceCreate
        from app.services.workspace import WorkspaceService
        
        default_workspace_data = WorkspaceCreate(
            name=f"{user.username}'s Workspace",
            description="Your personal workspace"
        )
        
        WorkspaceService.create_workspace(
            self.db,
            default_workspace_data,
            user.id
        )
    
    # ============= Email Verification =============
    
    def _create_email_verification_token(
        self,
        user: User,
        email: str,
        expires_in_hours: int = 24
    ) -> EmailVerificationToken:
        """
        Create an email verification token.
        
        Args:
            user: User to verify
            email: Email to verify
            expires_in_hours: Token expiration time in hours
            
        Returns:
            Created EmailVerificationToken
        """
        import secrets
        from app.core.security import hash_password
        
        # Generate random token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_password(raw_token)
        
        # Create verification token record
        verification_token = EmailVerificationToken(
            user_id=user.id,
            email=email,
            token=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        
        self.db.add(verification_token)
        self.db.commit()
        self.db.refresh(verification_token)
        
        # Send verification email
        if self.email_service:
            self.email_service.send_email_verification(user.email, raw_token)
        
        return verification_token
    
    def verify_email(self, user_id: UUID, token: str) -> bool:
        """
        Verify user email with a token.
        
        Args:
            user_id: User ID
            token: Verification token from email link
            
        Returns:
            True if verified successfully
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        # Find verification token
        verification_record = self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user_id
        ).order_by(EmailVerificationToken.created_at.desc()).first()
        
        if not verification_record:
            raise HTTPException(
                status_code=400,
                detail="No verification token found for this user"
            )
        
        if verification_record.verified_at:
            raise HTTPException(
                status_code=400,
                detail="Email already verified"
            )
        
        if verification_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Verification token has expired"
            )
        
        # Verify token
        if not verify_password(token, verification_record.token):
            raise HTTPException(
                status_code=400,
                detail="Invalid verification token"
            )
        
        # Update user status and verification record
        user = self.db.query(User).filter(User.id == user_id).first()
        user.status = UserStatus.ACTIVE
        user.email_verified_at = datetime.utcnow()
        
        verification_record.verified_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def resend_verification_email(self, user_id: UUID) -> bool:
        """
        Resend email verification token.
        
        Args:
            user_id: User ID
            
        Returns:
            True if email was sent
            
        Raises:
            HTTPException: If user not found or already verified
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.status == UserStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Email already verified"
            )
        
        self._create_email_verification_token(user, user.email)
        return True
    
    # ============= Login =============
    
    def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Authenticate user and create session.
        
        Args:
            email: User email
            password: User password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (session_data, error_message)
            session_data = {user_id, session_id, token, expires_in}
        """
        # Check brute-force
        is_locked, error_msg = check_brute_force(email, self.db)
        if is_locked:
            record_login_attempt(
                email, ip_address, user_agent, False,
                "Account locked due to too many failed attempts", self.db
            )
            raise HTTPException(status_code=429, detail=error_msg)
        
        # Find user by email
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            record_login_attempt(
                email, ip_address, user_agent, False,
                "User not found", self.db
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check password
        if not verify_password(password, user.password_hash):
            record_login_attempt(
                email, ip_address, user_agent, False,
                "Invalid password", self.db
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check user status
        if user.status != UserStatus.ACTIVE:
            record_login_attempt(
                email, ip_address, user_agent, False,
                f"User status: {user.status}", self.db
            )
            raise HTTPException(
                status_code=403,
                detail=f"User account is {user.status}"
            )
        
        # Check email verified
        if not user.email_verified_at:
            record_login_attempt(
                email, ip_address, user_agent, False,
                "Email not verified", self.db
            )
            raise HTTPException(
                status_code=403,
                detail="Please verify your email before logging in"
            )
        
        # Create session
        session_data = self._create_session(
            user, ip_address, user_agent
        )
        
        # Record successful login
        record_login_attempt(
            email, ip_address, user_agent, True, None, self.db
        )
        
        return session_data, None
    
    def _create_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """
        Create a new session for user.
        
        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Session data with token and metadata
        """
        # Check concurrent session limit (max 5 devices)
        active_sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == user.id,
            SessionModel.revoked_at == None
        ).order_by(SessionModel.created_at.asc()).all()
        
        MAX_CONCURRENT_SESSIONS = 5
        if len(active_sessions) >= MAX_CONCURRENT_SESSIONS:
            # Revoke oldest session
            oldest_session = active_sessions[0]
            oldest_session.revoked_at = datetime.utcnow()
            self.db.commit()
        
        # Create JWT token
        from app.core.security import create_access_token
        
        # Create session record first to get session_id
        session = SessionModel(
            user_id=user.id,
            ip_address=ip_address,
            device_info=self._parse_user_agent(user_agent) if user_agent else None,
            user_agent=user_agent,
            last_active_at=datetime.utcnow()
        )
        
        self.db.add(session)
        self.db.flush()  # Get the ID without committing
        
        # Create token with session ID
        token = create_access_token(user.id, session.id)
        session.token = token
        
        self.db.commit()
        self.db.refresh(session)
        
        return {
            "user_id": str(user.id),
            "session_id": str(session.id),
            "token": token,
            "expires_in": 30 * 60  # 30 minutes in seconds
        }
    
    def _parse_user_agent(self, user_agent: str) -> str:
        """
        Parse user agent string to readable device info.
        
        Args:
            user_agent: User agent string
            
        Returns:
            Readable device info (e.g., "Chrome on Windows 10")
        """
        try:
            from user_agents import parse
            ua = parse(user_agent)
            browser = ua.browser.family
            os = ua.os.family
            return f"{browser} on {os}"
        except:
            return user_agent[:100]  # Fallback to first 100 chars
    
    # ============= Logout =============
    
    def logout(self, session_id: UUID) -> bool:
        """
        Logout user by revoking session.
        
        Args:
            session_id: Session ID to revoke
            
        Returns:
            True if successful
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.revoked_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def logout_all_sessions(self, user_id: UUID) -> int:
        """
        Logout user from all sessions.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions revoked
        """
        now = datetime.utcnow()
        
        sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked_at == None
        ).all()
        
        for session in sessions:
            session.revoked_at = now
        
        self.db.commit()
        
        return len(sessions)
    
    # ============= Password Management =============
    
    def create_password_reset_token(self, user_id: UUID) -> str:
        """
        Create a password reset token.
        
        Args:
            user_id: User ID
            
        Returns:
            Reset token
        """
        import secrets
        from app.core.security import hash_password
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate random token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_password(raw_token)
        
        # Create reset token record (15 minutes expiry)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        
        self.db.add(reset_token)
        self.db.commit()
        
        # Send reset email
        if self.email_service:
            self.email_service.send_password_reset(user.email, raw_token)
        
        return raw_token
    
    def reset_password(
        self,
        user_id: UUID,
        token: str,
        new_password: str
    ) -> bool:
        """
        Reset user password with reset token.
        
        Args:
            user_id: User ID
            token: Reset token from email
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If token invalid or expired
        """
        # Validate new password
        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Find reset token
        reset_record = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id
        ).order_by(PasswordResetToken.created_at.desc()).first()
        
        if not reset_record:
            raise HTTPException(
                status_code=400,
                detail="No password reset request found"
            )
        
        if reset_record.used_at:
            raise HTTPException(
                status_code=400,
                detail="Reset token already used"
            )
        
        if reset_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Reset token has expired"
            )
        
        # Verify token
        if not verify_password(token, reset_record.token):
            raise HTTPException(
                status_code=400,
                detail="Invalid reset token"
            )
        
        # Update password
        user = self.db.query(User).filter(User.id == user_id).first()
        user.password_hash = hash_password(new_password)
        
        reset_record.used_at = datetime.utcnow()
        
        # Logout all sessions for security
        self.logout_all_sessions(user_id)
        
        self.db.commit()
        
        return True
    
    def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change password for logged-in user.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
        """
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Update password
        user.password_hash = hash_password(new_password)
        
        # Logout all sessions
        self.logout_all_sessions(user_id)
        
        self.db.commit()
        
        # Send notification
        if self.email_service:
            self.email_service.send_password_changed_notification(user.email)
        
        return True
