"""
Custom Exceptions for PronaFlow API
"""


class PronaFlowException(Exception):
    """Base exception for PronaFlow application."""
    
    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


class ValidationException(PronaFlowException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, status_code=422, code=code)


class NotFoundException(PronaFlowException):
    """Raised when requested resource is not found."""
    
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(message, status_code=404, code=code)


class UnauthorizedException(PronaFlowException):
    """Raised when user is not authenticated."""
    
    def __init__(self, message: str = "Not authenticated", code: str = "UNAUTHORIZED"):
        super().__init__(message, status_code=401, code=code)


class ForbiddenException(PronaFlowException):
    """Raised when user doesn't have permission."""
    
    def __init__(self, message: str = "Access forbidden", code: str = "FORBIDDEN"):
        super().__init__(message, status_code=403, code=code)


class ConflictException(PronaFlowException):
    """Raised when request conflicts with existing data."""
    
    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(message, status_code=409, code=code)


class DuplicateException(ConflictException):
    """Raised when trying to create duplicate record."""
    
    def __init__(self, message: str, code: str = "DUPLICATE_RECORD"):
        super().__init__(message, code=code)


class InvalidStateException(PronaFlowException):
    """Raised when operation invalid for current state."""
    
    def __init__(self, message: str, code: str = "INVALID_STATE"):
        super().__init__(message, status_code=400, code=code)


class RateLimitException(PronaFlowException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(message, status_code=429, code=code)


class ServiceUnavailableException(PronaFlowException):
    """Raised when external service is unavailable."""
    
    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE"):
        super().__init__(message, status_code=503, code=code)
