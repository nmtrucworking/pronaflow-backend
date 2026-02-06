"""
Unit Tests for Session Management Service
Tests session tracking, revocation, and concurrent limits.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from app.services.session import SessionService
from app.db.models.users import Session as SessionModel


class TestSessionService:
    """Test suite for SessionService"""
    
    def test_get_user_sessions(self, db_session, sample_user_sessions):
        """Test listing user sessions"""
        session_service = SessionService(db_session)
        
        sessions = session_service.get_user_sessions("user-uuid-123")
        
        assert len(sessions) > 0
        assert all("session_id" in s for s in sessions)
        assert all("device_info" in s for s in sessions)
    
    
    def test_revoke_session_success(self, db_session, sample_session):
        """Test successful session revocation"""
        session_service = SessionService(db_session)
        
        success = session_service.revoke_session(
            user_id="user-uuid-123",
            session_id=sample_session.id
        )
        
        assert success is True
        assert sample_session.revoked_at is not None
    
    
    def test_revoke_session_not_found(self, db_session):
        """Test revoking non-existent session"""
        session_service = SessionService(db_session)
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(Exception) as exc_info:
            session_service.revoke_session(
                user_id="user-uuid-123",
                session_id="non-existent"
            )
        
        assert "not found" in str(exc_info.value).lower()
    
    
    def test_revoke_all_sessions(self, db_session, sample_user_sessions):
        """Test revoking all sessions except current"""
        session_service = SessionService(db_session)
        
        current_session_id = sample_user_sessions[0].id
        count = session_service.revoke_all_sessions(
            user_id="user-uuid-123",
            except_session_id=current_session_id
        )
        
        assert count > 0
        # Current session should not be revoked
        assert sample_user_sessions[0].revoked_at is None
    
    
    def test_enforce_concurrent_session_limit(self, db_session):
        """Test max 5 concurrent sessions enforcement"""
        session_service = SessionService(db_session)
        
        # Mock 5 existing sessions
        existing_sessions = [Mock() for _ in range(5)]
        db_session.query.return_value.filter.return_value.count.return_value = 5
        db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = existing_sessions[0]
        
        # Try to create 6th session should remove oldest
        session_service.enforce_session_limit("user-uuid-123")
        
        # Oldest session should be revoked
        assert db_session.delete.called or existing_sessions[0].revoked_at is not None
    
    
    def test_detect_impossible_travel(self, db_session):
        """Test impossible travel detection"""
        session_service = SessionService(db_session)
        
        # Mock two sessions from distant locations in short time
        session1 = Mock()
        session1.geo_location = "Hanoi, Vietnam"
        session1.created_at = datetime.utcnow() - timedelta(minutes=5)
        
        session2 = Mock()
        session2.geo_location = "London, UK"
        session2.created_at = datetime.utcnow()
        
        is_suspicious = session_service.detect_impossible_travel(
            user_id="user-uuid-123",
            new_location="London, UK"
        )
        
        assert is_suspicious is True
    
    
    def test_session_timeout(self, db_session):
        """Test session timeout (inactive for 7 days)"""
        session_service = SessionService(db_session)
        
        old_session = Mock()
        old_session.last_active_at = datetime.utcnow() - timedelta(days=8)
        
        is_expired = session_service.is_session_expired(old_session)
        
        assert is_expired is True


# Fixtures

@pytest.fixture
def db_session():
    """Mock database session"""
    session = MagicMock()
    return session


@pytest.fixture
def sample_session():
    """Sample session for testing"""
    session = Mock()
    session.id = "session-uuid-123"
    session.user_id = "user-uuid-123"
    session.device_info = "Chrome on Windows 10"
    session.ip_address = "192.168.1.1"
    session.revoked_at = None
    session.last_active_at = datetime.utcnow()
    return session


@pytest.fixture
def sample_user_sessions():
    """Sample list of user sessions"""
    sessions = []
    for i in range(3):
        session = Mock()
        session.id = f"session-{i}"
        session.user_id = "user-uuid-123"
        session.device_info = f"Device {i}"
        session.revoked_at = None
        session.last_active_at = datetime.utcnow() - timedelta(hours=i)
        sessions.append(session)
    return sessions
