"""
Workspace Validation Service
Provides validation functions for workspace names and other workspace-related inputs.
Ref: Module 2 - AC 3: Validation
"""
import re
from typing import Tuple


# Basic profanity filter word list (simplified version)
# In production, use a comprehensive profanity filter library like 'better-profanity'
PROFANITY_WORDS = {
    'spam', 'scam', 'hack', 'abuse', 'offensive',
    # Add more words as needed
}


class WorkspaceValidator:
    """Validation service for workspace-related inputs"""
    
    @staticmethod
    def validate_workspace_name(name: str) -> Tuple[bool, str]:
        """
        Validate workspace name.
        
        Module 2 - AC 3: Validation
        When user enters name with only special characters or profane words,
        system displays error: "WS_001: Tên Không gian làm việc không hợp lệ"
        
        Args:
            name: Workspace name to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
            error_message is None if valid
        """
        # Check if name is empty or only whitespace
        if not name or not name.strip():
            return False, "WS_001: Tên Không gian làm việc không hợp lệ"
        
        # Check length
        if len(name) > 50:
            return False, "WS_002: Tên Không gian làm việc quá dài (tối đa 50 ký tự)"
        
        if len(name.strip()) < 2:
            return False, "WS_003: Tên Không gian làm việc quá ngắn (tối thiểu 2 ký tự)"
        
        # Check if name contains only special characters
        if re.match(r'^[^a-zA-Z0-9\u00C0-\u1EF9]+$', name):
            return False, "WS_001: Tên Không gian làm việc không hợp lệ"
        
        # Check for profanity
        name_lower = name.lower()
        if WorkspaceValidator._contains_profanity(name_lower):
            return False, "WS_001: Tên Không gian làm việc không hợp lệ"
        
        # Check for suspicious patterns
        if WorkspaceValidator._contains_suspicious_pattern(name):
            return False, "WS_001: Tên Không gian làm việc không hợp lệ"
        
        return True, None
    
    @staticmethod
    def _contains_profanity(text: str) -> bool:
        """
        Check if text contains profane words.
        
        Args:
            text: Text to check (should be lowercased)
            
        Returns:
            True if profanity found, False otherwise
        """
        words = re.findall(r'\w+', text)
        return any(word in PROFANITY_WORDS for word in words)
    
    @staticmethod
    def _contains_suspicious_pattern(text: str) -> bool:
        """
        Check for suspicious patterns like excessive repetition or spam-like content.
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious pattern found, False otherwise
        """
        # Check for excessive repetition (e.g., "aaaaaaa")
        if re.search(r'(.)\1{6,}', text):
            return True
        
        # Check for excessive exclamation/question marks
        if text.count('!') > 5 or text.count('?') > 5:
            return True
        
        # Check for URLs (might be spam)
        if re.search(r'https?://', text, re.IGNORECASE):
            return True
        
        return False
    
    @staticmethod
    def validate_description(description: str) -> Tuple[bool, str]:
        """
        Validate workspace description.
        
        Args:
            description: Description to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not description:
            return True, None  # Description is optional
        
        # Check length
        if len(description) > 500:
            return False, "WS_004: Mô tả quá dài (tối đa 500 ký tự)"
        
        # Check for profanity
        if WorkspaceValidator._contains_profanity(description.lower()):
            return False, "WS_005: Mô tả chứa nội dung không phù hợp"
        
        return True, None
    
    @staticmethod
    def validate_timezone(timezone: str) -> Tuple[bool, str]:
        """
        Validate timezone string.
        
        Args:
            timezone: Timezone string (e.g., 'UTC', 'Asia/Ho_Chi_Minh')
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        try:
            import pytz
            pytz.timezone(timezone)
            return True, None
        except pytz.exceptions.UnknownTimeZoneError:
            return False, "WS_006: Múi giờ không hợp lệ"
        except Exception:
            return False, "WS_006: Múi giờ không hợp lệ"
    
    @staticmethod
    def validate_work_days(work_days: str) -> Tuple[bool, str]:
        """
        Validate work days string.
        
        Args:
            work_days: Comma-separated work days (e.g., 'Mon,Tue,Wed,Thu,Fri')
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not work_days:
            return True, None  # Optional
        
        valid_days = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}
        days = [d.strip() for d in work_days.split(',')]
        
        if not days:
            return False, "WS_007: Ngày làm việc không hợp lệ"
        
        for day in days:
            if day not in valid_days:
                return False, f"WS_007: Ngày '{day}' không hợp lệ"
        
        return True, None
    
    @staticmethod
    def validate_work_hours(work_hours: str) -> Tuple[bool, str]:
        """
        Validate work hours string.
        
        Args:
            work_hours: Work hours in format '{"start": "09:00", "end": "18:00"}'
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not work_hours:
            return True, None  # Optional
        
        try:
            import json
            hours = json.loads(work_hours)
            
            if not isinstance(hours, dict):
                return False, "WS_008: Giờ làm việc phải là JSON object"
            
            if 'start' not in hours or 'end' not in hours:
                return False, "WS_008: Giờ làm việc phải có 'start' và 'end'"
            
            # Validate time format (HH:MM)
            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
            
            if not time_pattern.match(hours['start']):
                return False, "WS_008: Giờ bắt đầu không hợp lệ (định dạng: HH:MM)"
            
            if not time_pattern.match(hours['end']):
                return False, "WS_008: Giờ kết thúc không hợp lệ (định dạng: HH:MM)"
            
            return True, None
            
        except json.JSONDecodeError:
            return False, "WS_008: Giờ làm việc phải là JSON hợp lệ"
        except Exception as e:
            return False, f"WS_008: Lỗi xác thực giờ làm việc: {str(e)}"


def validate_workspace_name(name: str) -> Tuple[bool, str]:
    """Convenience function for workspace name validation"""
    return WorkspaceValidator.validate_workspace_name(name)


def validate_workspace_description(description: str) -> Tuple[bool, str]:
    """Convenience function for workspace description validation"""
    return WorkspaceValidator.validate_description(description)
