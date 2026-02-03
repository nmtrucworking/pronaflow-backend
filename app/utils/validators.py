"""
Validators for PronaFlow API
"""
import re
from typing import Optional, List
from app.utils.exceptions import ValidationException


class EmailValidator:
    """Email validation utilities."""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate(email: str) -> str:
        """
        Validate email address.
        
        Args:
            email: Email to validate
            
        Returns:
            Lowercase email if valid
            
        Raises:
            ValidationException: If email is invalid
        """
        if not email or not isinstance(email, str):
            raise ValidationException("Email is required and must be a string")
        
        email = email.strip().lower()
        
        if not EmailValidator.EMAIL_PATTERN.match(email):
            raise ValidationException(f"Invalid email format: {email}")
        
        if len(email) > 255:
            raise ValidationException("Email is too long (max 255 characters)")
        
        return email


class PasswordValidator:
    """Password validation utilities."""
    
    @staticmethod
    def validate_strength(password: str) -> None:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationException: If password doesn't meet requirements
        """
        if not password or not isinstance(password, str):
            raise ValidationException("Password is required and must be a string")
        
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationException("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValidationException("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValidationException("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationException("Password must contain at least one special character")


class UsernameValidator:
    """Username validation utilities."""
    
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    
    @staticmethod
    def validate(username: str) -> str:
        """
        Validate username.
        
        Requirements:
        - 3-30 characters
        - Alphanumeric, underscore, or hyphen only
        
        Args:
            username: Username to validate
            
        Returns:
            Lowercase username if valid
            
        Raises:
            ValidationException: If username is invalid
        """
        if not username or not isinstance(username, str):
            raise ValidationException("Username is required and must be a string")
        
        username = username.strip().lower()
        
        if not UsernameValidator.USERNAME_PATTERN.match(username):
            raise ValidationException(
                "Username must be 3-30 characters and contain only letters, numbers, underscores, and hyphens"
            )
        
        return username


class NameValidator:
    """Name validation utilities."""
    
    @staticmethod
    def validate(name: str, field_name: str = "Name") -> str:
        """
        Validate name field.
        
        Args:
            name: Name to validate
            field_name: Field display name for error messages
            
        Returns:
            Trimmed name if valid
            
        Raises:
            ValidationException: If name is invalid
        """
        if not name or not isinstance(name, str):
            raise ValidationException(f"{field_name} is required and must be a string")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValidationException(f"{field_name} must be at least 2 characters long")
        
        if len(name) > 255:
            raise ValidationException(f"{field_name} must not exceed 255 characters")
        
        return name


class URLValidator:
    """URL validation utilities."""
    
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    @staticmethod
    def validate(url: str) -> str:
        """
        Validate URL.
        
        Args:
            url: URL to validate
            
        Returns:
            URL if valid
            
        Raises:
            ValidationException: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationException("URL is required and must be a string")
        
        url = url.strip()
        
        if not URLValidator.URL_PATTERN.match(url):
            raise ValidationException(f"Invalid URL format: {url}")
        
        if len(url) > 2048:
            raise ValidationException("URL is too long (max 2048 characters)")
        
        return url


class SlugValidator:
    """Slug validation utilities."""
    
    SLUG_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    
    @staticmethod
    def validate(slug: str) -> str:
        """
        Validate URL slug.
        
        Requirements:
        - Lowercase letters, numbers, and hyphens only
        - Must start and end with alphanumeric
        
        Args:
            slug: Slug to validate
            
        Returns:
            Slug if valid
            
        Raises:
            ValidationException: If slug is invalid
        """
        if not slug or not isinstance(slug, str):
            raise ValidationException("Slug is required and must be a string")
        
        slug = slug.strip().lower()
        
        if not SlugValidator.SLUG_PATTERN.match(slug):
            raise ValidationException(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        
        if len(slug) < 3:
            raise ValidationException("Slug must be at least 3 characters long")
        
        if len(slug) > 100:
            raise ValidationException("Slug must not exceed 100 characters")
        
        return slug


class ListValidator:
    """List/array validation utilities."""
    
    @staticmethod
    def validate_string_list(items: List[str], min_items: int = 1, max_items: int = 100) -> List[str]:
        """
        Validate list of strings.
        
        Args:
            items: List to validate
            min_items: Minimum number of items
            max_items: Maximum number of items
            
        Returns:
            Validated list
            
        Raises:
            ValidationException: If list is invalid
        """
        if not isinstance(items, list):
            raise ValidationException("Expected a list")
        
        if len(items) < min_items:
            raise ValidationException(f"List must contain at least {min_items} item(s)")
        
        if len(items) > max_items:
            raise ValidationException(f"List must not exceed {max_items} item(s)")
        
        # Validate each item is string
        for item in items:
            if not isinstance(item, str):
                raise ValidationException("All list items must be strings")
        
        return [item.strip() for item in items]


class NumberValidator:
    """Number validation utilities."""
    
    @staticmethod
    def validate_positive(value: int | float, field_name: str = "Value") -> int | float:
        """
        Validate positive number.
        
        Args:
            value: Number to validate
            field_name: Field display name
            
        Returns:
            Value if valid
            
        Raises:
            ValidationException: If value is not positive
        """
        if not isinstance(value, (int, float)):
            raise ValidationException(f"{field_name} must be a number")
        
        if value <= 0:
            raise ValidationException(f"{field_name} must be positive")
        
        return value
    
    @staticmethod
    def validate_percentage(value: int | float) -> int | float:
        """
        Validate percentage (0-100).
        
        Args:
            value: Percentage to validate
            
        Returns:
            Value if valid
            
        Raises:
            ValidationException: If value is not valid percentage
        """
        if not isinstance(value, (int, float)):
            raise ValidationException("Percentage must be a number")
        
        if value < 0 or value > 100:
            raise ValidationException("Percentage must be between 0 and 100")
        
        return value
