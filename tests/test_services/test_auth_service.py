"""
Unit Tests for Authentication Service
Tests user registration, login, and password management.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.services.auth import AuthService
from app.models.users import User
from app.db.enums import UserStatus


class TestAuthService:
    """Test suite for AuthService"""
    
    def test_register_user_success(self, db_session, mock_email_service):
        """Test successful user registration"""
        auth_service = AuthService(db_session, mock_email_service)
        
        user, error = auth_service.register_user(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!@#"
        )
        
        assert error is None
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.status == UserStatus.PENDING
        assert user.password_hash is not None
        assert user.password_hash != "SecurePass123!@#"  # Password should be hashed
    
    
    def test_register_user_duplicate_email(self, db_session, mock_email_service):
        """Test registration with duplicate email"""
        auth_service = AuthService(db_session, mock_email_service)
        
        # Register first user
        auth_service.register_user(
            email="test@example.com",
            username="testuser1",
            password="SecurePass123!@#"
        )
        
        # Try to register with same email
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(
                email="test@example.com",
                username="testuser2",
                password="SecurePass123!@#"
            )
        
        assert exc_info.value.status_code == 409
        assert "Email already registered" in exc_info.value.detail
    
    
    def test_register_user_duplicate_username(self, db_session, mock_email_service):
        """Test registration with duplicate username"""
        auth_service = AuthService(db_session, mock_email_service)
        
        # Register first user
        auth_service.register_user(
            email="test1@example.com",
            username="testuser",
            password="SecurePass123!@#"
        )
        
        # Try to register with same username
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(
                email="test2@example.com",
                username="testuser",
                password="SecurePass123!@#"
            )
        
        assert exc_info.value.status_code == 409
        assert "Username already taken" in exc_info.value.detail
    
    
    def test_register_user_invalid_email(self, db_session, mock_email_service):
        """Test registration with invalid email"""
        auth_service = AuthService(db_session, mock_email_service)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(
                email="invalid-email",
                username="testuser",
                password="SecurePass123!@#"
            )
        
        assert exc_info.value.status_code == 400
    
    
    def test_register_user_weak_password(self, db_session, mock_email_service):
        """Test registration with weak password"""
        auth_service = AuthService(db_session, mock_email_service)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(
                email="test@example.com",
                username="testuser",
                password="weak"
            )
        
        assert exc_info.value.status_code == 400
    
    
    def test_login_success(self, db_session, mock_email_service):
        """Test successful login"""
        auth_service = AuthService(db_session, mock_email_service)
        
        # Register and verify user
        user, _ = auth_service.register_user(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!@#"
        )
        user.status = UserStatus.ACTIVE
        user.email_verified_at = datetime.utcnow()
        db_session.commit()
        
        # Login
        session_data, error = auth_service.login(
            email="test@example.com",
            password="SecurePass123!@#",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert error is None
        assert session_data is not None
        assert "user_id" in session_data
        assert "token" in session_data
        assert "session_id" in session_data
    
    
    def test_login_invalid_password(self, db_session, mock_email_service):
        """Test login with wrong password"""
        auth_service = AuthService(db_session, mock_email_service)
        
        # Register user
        user, _ = auth_service.register_user(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!@#"
        )
        user.status = UserStatus.ACTIVE
        db_session.commit()
        
        # Try to login with wrong password
        session_data, error = auth_service.login(
            email="test@example.com",
            password="WrongPassword123!@#",
            ip_address="192.168.1.1"
        )
        
        assert session_data is None
        assert error == "Invalid email or password"
    
    
    def test_login_unverified_email(self, db_session, mock_email_service):
        """Test login with unverified email"""
        auth_service = AuthService(db_session, mock_email_service)
        
        # Register user (status PENDING)
        user, _ = auth_service.register_user(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!@#"
        )
        
        # Try to login
        session_data, error = auth_service.login(
            email="test@example.com",
            password="SecurePass123!@#",
            ip_address="192.168.1.1"
        )
        
        assert session_data is None
        assert "Please verify your email" in error


# Fixtures

@pytest.fixture
def db_session():
    """Mock database session"""
    from unittest.mock import MagicMock
    session = MagicMock()
    return session


@pytest.fixture
def mock_email_service():
    """Mock email service"""
    from unittest.mock import MagicMock
    service = MagicMock()
    return service
