"""
Session Management Service
Handles session tracking, device management, and impossible travel detection.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException

from app.db.models.users import Session as SessionModel


class SessionService:
    """
    Service for session management operations.
    Handles session tracking, concurrent device limits, and security alerts.
    """
    
    def __init__(self, db: DBSession):
        self.db = db
        self.MAX_CONCURRENT_SESSIONS = 5
        self.IMPOSSIBLE_TRAVEL_THRESHOLD_KMH = 900  # ~900 km/h (fastest commercial flight)
        self.IMPOSSIBLE_TRAVEL_TIME_MINUTES = 60
    
    # ============= Session Listing =============
    
    def get_user_sessions(self, user_id: UUID) -> List[dict]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of session information dicts
        """
        sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked_at == None
        ).order_by(SessionModel.last_active_at.desc()).all()
        
        return [self._session_to_dict(session) for session in sessions]
    
    def _session_to_dict(self, session: SessionModel) -> dict:
        """
        Convert session object to dictionary.
        
        Args:
            session: Session object
            
        Returns:
            Session information dict
        """
        return {
            "session_id": str(session.id),
            "device_info": session.device_info or "Unknown Device",
            "ip_address": session.ip_address,
            "geo_location": session.geo_location or "Unknown",
            "last_active_at": session.last_active_at.isoformat(),
            "created_at": session.created_at.isoformat(),
            "is_current": session.token is not None  # Current session has active token
        }
    
    # ============= Session Revocation =============
    
    def revoke_session(self, user_id: UUID, session_id: UUID) -> bool:
        """
        Revoke a specific session.
        
        Args:
            user_id: User ID (for authorization check)
            session_id: Session ID to revoke
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If session not found or unauthorized
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.revoked_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def revoke_all_sessions(self, user_id: UUID, except_session_id: Optional[UUID] = None) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User ID
            except_session_id: Session to keep active (optional)
            
        Returns:
            Number of sessions revoked
        """
        query = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked_at == None
        )
        
        if except_session_id:
            query = query.filter(SessionModel.id != except_session_id)
        
        sessions = query.all()
        now = datetime.utcnow()
        
        for session in sessions:
            session.revoked_at = now
        
        self.db.commit()
        
        return len(sessions)
    
    # ============= Session Cleanup =============
    
    def cleanup_expired_sessions(self, inactivity_days: int = 7) -> int:
        """
        Clean up sessions that have been inactive for a specified time.
        
        Args:
            inactivity_days: Days of inactivity before cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        threshold = datetime.utcnow() - timedelta(days=inactivity_days)
        
        inactive_sessions = self.db.query(SessionModel).filter(
            SessionModel.revoked_at == None,
            SessionModel.last_active_at < threshold
        ).all()
        
        now = datetime.utcnow()
        for session in inactive_sessions:
            session.revoked_at = now
        
        self.db.commit()
        
        return len(inactive_sessions)
    
    # ============= Impossible Travel Detection =============
    
    def detect_impossible_travel(
        self,
        user_id: UUID,
        new_ip: str,
        new_location: str,
        new_timestamp: datetime
    ) -> Tuple[bool, Optional[Tuple[str, str, int]]]:
        """
        Detect impossible travel based on location and time.
        
        Args:
            user_id: User ID
            new_ip: New IP address
            new_location: New location (format: "city, country" or "latitude,longitude")
            new_timestamp: New login timestamp
            
        Returns:
            Tuple of (is_impossible_travel, (prev_location, new_location, time_diff_minutes))
            
        """
        # Get last active session
        last_session = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked_at == None,
            SessionModel.ip_address != new_ip  # Different IP
        ).order_by(SessionModel.last_active_at.desc()).first()
        
        if not last_session or not last_session.geo_location:
            return False, None
        
        # Calculate time difference
        time_diff = new_timestamp - last_session.last_active_at
        time_diff_minutes = int(time_diff.total_seconds() / 60)
        
        if time_diff_minutes < 0:
            return False, None  # Clock skew, ignore
        
        # Calculate distance between locations
        try:
            distance_km = self._calculate_distance(
                last_session.geo_location,
                new_location
            )
            
            # Check if physically possible
            required_speed_kmh = distance_km / (time_diff_minutes / 60) if time_diff_minutes > 0 else float('inf')
            
            if (distance_km > 0 and 
                time_diff_minutes < self.IMPOSSIBLE_TRAVEL_TIME_MINUTES and
                required_speed_kmh > self.IMPOSSIBLE_TRAVEL_THRESHOLD_KMH):
                
                return True, (last_session.geo_location, new_location, time_diff_minutes)
        
        except Exception:
            # If distance calculation fails, skip detection
            pass
        
        return False, None
    
    def _calculate_distance(self, location1: str, location2: str) -> float:
        """
        Calculate distance between two locations.
        Simplified version using string parsing - in production, use GeoIP database.
        
        Args:
            location1: Location string (e.g., "Ho Chi Minh, Vietnam")
            location2: Location string
            
        Returns:
            Distance in kilometers
            
        Note:
            This is a simplified implementation.
            In production, use GeoIP database (MaxMind, IP2Location) for accuracy.
        """
        try:
            # Try to parse as coordinates first
            if ',' in location1 and ',' in location2:
                parts1 = [float(x.strip()) for x in location1.split(',')]
                parts2 = [float(x.strip()) for x in location2.split(',')]
                
                if len(parts1) == 2 and len(parts2) == 2:
                    lat1, lon1 = parts1
                    lat2, lon2 = parts2
                    return self._haversine_distance(lat1, lon1, lat2, lon2)
        except:
            pass
        
        # Fallback: return 0 if same city, large distance if different
        return 0 if location1.lower() == location2.lower() else 1000
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two points on Earth.
        
        Args:
            lat1, lon1: Latitude and longitude of point 1
            lat2, lon2: Latitude and longitude of point 2
            
        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371
        
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    # ============= Session Activity Tracking =============
    
    def update_session_activity(self, session_id: UUID) -> bool:
        """
        Update the last activity time of a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if not session:
            return False
        
        session.last_active_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    # ============= Concurrent Session Management =============
    
    def check_concurrent_session_limit(
        self,
        user_id: UUID,
        max_sessions: int = 5
    ) -> Optional[UUID]:
        """
        Check if user exceeded concurrent session limit.
        Returns the oldest session ID if limit exceeded.
        
        Args:
            user_id: User ID
            max_sessions: Maximum concurrent sessions allowed
            
        Returns:
            Session ID to revoke (if limit exceeded), None otherwise
        """
        active_sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked_at == None
        ).order_by(SessionModel.created_at.asc()).all()
        
        if len(active_sessions) >= max_sessions:
            # Return the oldest session ID
            return active_sessions[0].id
        
        return None
    
    def get_session_info(self, session_id: UUID) -> Optional[dict]:
        """
        Get detailed information about a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session info dict or None if not found
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if not session:
            return None
        
        return self._session_to_dict(session)
