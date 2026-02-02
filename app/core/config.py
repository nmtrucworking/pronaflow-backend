"""
Configuration settings for PronaFlow backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5432/pronaflow"
    
    # Application
    APP_NAME: str = "PronaFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Session Management
    MAX_CONCURRENT_SESSIONS: int = 5
    SESSION_INACTIVITY_DAYS: int = 7
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    
    # Brute-Force Protection
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # Email Configuration (SMTP)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@pronaflow.com"
    
    # OAuth2 Providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # GeoIP Configuration
    GEOIP_DATABASE_PATH: Optional[str] = None
    
    # Redis Configuration (Event Bus)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Notification Settings
    NOTIFICATION_DEBOUNCE_MS: int = 5000
    NOTIFICATION_MAX_RETRIES: int = 3
    NOTIFICATION_RETRY_BACKOFF: List[int] = [1, 5, 25]  # Seconds
    NOTIFICATION_TTL_MINUTES: int = 30
    
    # Archive & Compliance Settings (Module 8)
    ARCHIVE_INACTIVE_DAYS: int = 180  # Days before auto-archiving
    TRASH_BIN_RETENTION_DAYS: int = 30  # Days to keep deleted items
    SYSTEM_LOGS_RETENTION_DAYS: int = 90  # Days to keep audit logs
    EXPORT_LINK_EXPIRY_HOURS: int = 24  # Hours until export link expires
    MAX_EXPORT_FILE_SIZE_MB: int = 500  # Max export file size
    BACKGROUND_JOB_INTERVAL_HOURS: int = 24  # Scheduled job interval
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
