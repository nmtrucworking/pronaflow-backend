"""
Multi-Factor Authentication (MFA) Service
Handles TOTP generation, verification, and backup codes.
"""
from typing import Tuple, List
from uuid import UUID
from datetime import datetime
import secrets
import qrcode
import io
import base64
import pyotp

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.users import User, MFAConfig, MFABackupCode
from app.core.security import hash_password, verify_password


class MFAService:
    """
    Service for Multi-Factor Authentication (MFA) operations.
    Implements TOTP (Time-based One-Time Password) and backup codes.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.BACKUP_CODES_COUNT = 10
        self.BACKUP_CODE_LENGTH = 8
    
    # ============= MFA Setup =============
    
    def enable_mfa(self, user_id: UUID) -> Tuple[str, str, List[str]]:
        """
        Enable MFA for user with TOTP.
        Generates a secret key and QR code.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (secret_key, qr_code_url, backup_codes)
            
        Raises:
            HTTPException: If user not found or MFA already enabled
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if MFA already enabled
        existing_mfa = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        if existing_mfa:
            raise HTTPException(
                status_code=400,
                detail="MFA is already enabled for this user"
            )
        
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Create MFA config record
        mfa_config = MFAConfig(
            user_id=user_id,
            secret_key=secret,
            enabled=False  # Not enabled until user confirms
        )
        
        self.db.add(mfa_config)
        self.db.flush()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='PronaFlow'
        )
        
        qr_code_url = self._generate_qr_code(qr_uri)
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes(mfa_config.id)
        
        # Don't commit yet - user must confirm with valid OTP first
        self.db.flush()
        
        return secret, qr_code_url, backup_codes
    
    def confirm_mfa(self, user_id: UUID, otp_code: str) -> Tuple[bool, List[str]]:
        """
        Confirm MFA setup by verifying TOTP code.
        
        Args:
            user_id: User ID
            otp_code: 6-digit OTP code
            
        Returns:
            Tuple of (success, backup_codes)
            
        Raises:
            HTTPException: If code invalid or user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find unconfirmed MFA config
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == False
        ).first()
        
        if not mfa_config:
            raise HTTPException(
                status_code=400,
                detail="No pending MFA setup found"
            )
        
        # Verify OTP code
        totp = pyotp.TOTP(mfa_config.secret_key)
        if not totp.verify(otp_code, valid_window=1):  # Allow 30-second window
            raise HTTPException(
                status_code=400,
                detail="Invalid OTP code"
            )
        
        # Enable MFA
        mfa_config.enabled = True
        
        # Get backup codes
        backup_codes = self.db.query(MFABackupCode).filter(
            MFABackupCode.mfa_id == mfa_config.id,
            MFABackupCode.used_at == None
        ).all()
        
        backup_codes_list = [code.code_hash for code in backup_codes]
        
        self.db.commit()
        
        return True, backup_codes_list
    
    def disable_mfa(self, user_id: UUID, password: str) -> bool:
        """
        Disable MFA for user (requires password confirmation).
        
        Args:
            user_id: User ID
            password: User password for confirmation
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If password invalid or MFA not enabled
        """
        from app.core.security import verify_password
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Password is incorrect"
            )
        
        # Find enabled MFA config
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        if not mfa_config:
            raise HTTPException(
                status_code=400,
                detail="MFA is not enabled for this user"
            )
        
        # Disable MFA
        mfa_config.enabled = False
        
        # Mark all backup codes as unused
        backup_codes = self.db.query(MFABackupCode).filter(
            MFABackupCode.mfa_id == mfa_config.id
        ).all()
        
        for code in backup_codes:
            code.used_at = None
        
        self.db.commit()
        
        return True
    
    # ============= MFA Verification =============
    
    def verify_otp(self, user_id: UUID, otp_code: str) -> bool:
        """
        Verify TOTP code during login.
        
        Args:
            user_id: User ID
            otp_code: 6-digit OTP code
            
        Returns:
            True if code is valid
            
        Raises:
            HTTPException: If MFA not enabled or code invalid
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        if not mfa_config:
            raise HTTPException(
                status_code=400,
                detail="MFA is not enabled for this user"
            )
        
        totp = pyotp.TOTP(mfa_config.secret_key)
        if not totp.verify(otp_code, valid_window=1):
            raise HTTPException(
                status_code=400,
                detail="Invalid OTP code"
            )
        
        return True
    
    def verify_backup_code(self, user_id: UUID, code: str) -> bool:
        """
        Verify backup code during login.
        
        Args:
            user_id: User ID
            code: Backup code
            
        Returns:
            True if code is valid and unused
            
        Raises:
            HTTPException: If MFA not enabled or code invalid
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        if not mfa_config:
            raise HTTPException(
                status_code=400,
                detail="MFA is not enabled for this user"
            )
        
        # Find and verify backup code
        backup_code = self.db.query(MFABackupCode).filter(
            MFABackupCode.mfa_id == mfa_config.id,
            MFABackupCode.used_at == None
        ).first()
        
        if not backup_code:
            raise HTTPException(
                status_code=400,
                detail="No valid backup codes available"
            )
        
        # Verify code (need to compare with hashed version)
        if not verify_password(code, backup_code.code_hash):
            raise HTTPException(
                status_code=400,
                detail="Invalid backup code"
            )
        
        # Mark backup code as used
        backup_code.used_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def is_mfa_enabled(self, user_id: UUID) -> bool:
        """
        Check if MFA is enabled for user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if MFA is enabled
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        return mfa_config is not None
    
    # ============= Backup Codes Management =============
    
    def _generate_backup_codes(self, mfa_config_id: UUID) -> List[str]:
        """
        Generate backup codes for MFA.
        
        Args:
            mfa_config_id: MFA config ID
            
        Returns:
            List of backup codes
        """
        codes = []
        
        for _ in range(self.BACKUP_CODES_COUNT):
            # Generate random code
            raw_code = secrets.token_hex(self.BACKUP_CODE_LENGTH // 2)
            code_hash = hash_password(raw_code)
            
            # Store hashed code in database
            backup_code = MFABackupCode(
                mfa_id=mfa_config_id,
                code_hash=code_hash
            )
            
            self.db.add(backup_code)
            codes.append(raw_code)
        
        return codes
    
    def regenerate_backup_codes(self, user_id: UUID) -> List[str]:
        """
        Regenerate backup codes (invalidates old ones).
        
        Args:
            user_id: User ID
            
        Returns:
            List of new backup codes
            
        Raises:
            HTTPException: If MFA not enabled
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        if not mfa_config:
            raise HTTPException(
                status_code=400,
                detail="MFA is not enabled for this user"
            )
        
        # Delete old backup codes
        old_codes = self.db.query(MFABackupCode).filter(
            MFABackupCode.mfa_id == mfa_config.id
        ).delete()
        
        # Generate new codes
        new_codes = self._generate_backup_codes(mfa_config.id)
        
        self.db.commit()
        
        return new_codes
    
    def get_backup_codes_count(self, user_id: UUID) -> int:
        """
        Get count of unused backup codes.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unused backup codes
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user_id,
            MFAConfig.enabled == True
        ).first()
        
        if not mfa_config:
            return 0
        
        count = self.db.query(MFABackupCode).filter(
            MFABackupCode.mfa_id == mfa_config.id,
            MFABackupCode.used_at == None
        ).count()
        
        return count
    
    # ============= QR Code Generation =============
    
    def _generate_qr_code(self, uri: str) -> str:
        """
        Generate QR code image and return as data URL.
        
        Args:
            uri: Provisioning URI from pyotp
            
        Returns:
            Data URL for QR code image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to PNG bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Convert to base64 data URL
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
