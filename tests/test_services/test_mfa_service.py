"""
Unit Tests for MFA Service
Tests TOTP setup, verification, and backup codes.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
import pyotp

from app.services.mfa import MFAService
from app.db.models.users import User, MFAConfig, MFABackupCode


class TestMFAService:
    """Test suite for MFAService"""
    
    def test_enable_mfa_success(self, db_session, sample_user):
        """Test successful MFA enablement"""
        mfa_service = MFAService(db_session)
        
        secret, qr_code, backup_codes = mfa_service.enable_mfa(sample_user.id)
        
        assert secret is not None
        assert len(secret) == 32  # Base32 secret
        assert qr_code is not None
        assert qr_code.startswith("data:image/png;base64,")
        assert len(backup_codes) == 10
        assert all(len(code) == 8 for code in backup_codes)
    
    
    def test_enable_mfa_already_enabled(self, db_session, sample_user_with_mfa):
        """Test enabling MFA when already enabled"""
        mfa_service = MFAService(db_session)
        
        with pytest.raises(Exception) as exc_info:
            mfa_service.enable_mfa(sample_user_with_mfa.id)
        
        assert "already enabled" in str(exc_info.value).lower()
    
    
    def test_confirm_mfa_valid_otp(self, db_session, sample_user, mfa_config):
        """Test MFA confirmation with valid OTP"""
        mfa_service = MFAService(db_session)
        
        # Generate valid OTP
        totp = pyotp.TOTP(mfa_config.secret_key)
        valid_otp = totp.now()
        
        success, backup_codes = mfa_service.confirm_mfa(sample_user.id, valid_otp)
        
        assert success is True
        assert len(backup_codes) == 10
        assert mfa_config.enabled is True
    
    
    def test_confirm_mfa_invalid_otp(self, db_session, sample_user, mfa_config):
        """Test MFA confirmation with invalid OTP"""
        mfa_service = MFAService(db_session)
        
        success, backup_codes = mfa_service.confirm_mfa(sample_user.id, "000000")
        
        assert success is False
        assert backup_codes is None or len(backup_codes) == 0
        assert mfa_config.enabled is False
    
    
    def test_verify_otp_success(self, db_session, sample_user_with_mfa, mfa_config):
        """Test OTP verification success"""
        mfa_service = MFAService(db_session)
        
        # Generate valid OTP
        totp = pyotp.TOTP(mfa_config.secret_key)
        valid_otp = totp.now()
        
        is_valid = mfa_service.verify_otp(sample_user_with_mfa.id, valid_otp)
        
        assert is_valid is True
    
    
    def test_verify_otp_invalid(self, db_session, sample_user_with_mfa):
        """Test OTP verification with invalid code"""
        mfa_service = MFAService(db_session)
        
        is_valid = mfa_service.verify_otp(sample_user_with_mfa.id, "000000")
        
        assert is_valid is False
    
    
    def test_verify_backup_code_success(self, db_session, sample_user_with_mfa, backup_code):
        """Test backup code verification"""
        mfa_service = MFAService(db_session)
        
        is_valid = mfa_service.verify_backup_code(sample_user_with_mfa.id, backup_code)
        
        assert is_valid is True
        # Backup code should be marked as used
        assert backup_code.used_at is not None
    
    
    def test_verify_backup_code_already_used(self, db_session, sample_user_with_mfa, used_backup_code):
        """Test verification of already used backup code"""
        mfa_service = MFAService(db_session)
        
        is_valid = mfa_service.verify_backup_code(sample_user_with_mfa.id, used_backup_code)
        
        assert is_valid is False
    
    
    def test_disable_mfa_success(self, db_session, sample_user_with_mfa):
        """Test MFA disable with correct password"""
        mfa_service = MFAService(db_session)
        
        success = mfa_service.disable_mfa(sample_user_with_mfa.id, "correct_password")
        
        assert success is True
        # MFA config should be deleted or disabled
    
    
    def test_regenerate_backup_codes(self, db_session, sample_user_with_mfa):
        """Test backup codes regeneration"""
        mfa_service = MFAService(db_session)
        
        new_codes = mfa_service.regenerate_backup_codes(sample_user_with_mfa.id)
        
        assert len(new_codes) == 10
        assert all(len(code) == 8 for code in new_codes)
        # Old codes should be deleted


# Fixtures

@pytest.fixture
def db_session():
    """Mock database session"""
    session = MagicMock()
    return session


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    user = Mock()
    user.id = "user-uuid-123"
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_user_with_mfa(sample_user):
    """Sample user with MFA enabled"""
    sample_user.mfa_enabled = True
    return sample_user


@pytest.fixture
def mfa_config():
    """Sample MFA config"""
    config = Mock()
    config.secret_key = pyotp.random_base32()
    config.enabled = False
    return config


@pytest.fixture
def backup_code():
    """Sample unused backup code"""
    code = Mock()
    code.code_hash = "hashed_code"
    code.used_at = None
    return code


@pytest.fixture
def used_backup_code():
    """Sample used backup code"""
    code = Mock()
    code.code_hash = "hashed_code"
    code.used_at = datetime.utcnow()
    return code
