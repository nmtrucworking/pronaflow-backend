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

    # Personalization & UX Settings (Module 9)
    SUPPORTED_LANGUAGES: List[str] = ["en-US", "vi-VN"]  # Supported language codes
    DEFAULT_LANGUAGE: str = "en-US"  # Default language fallback
    DEFAULT_THEME: str = "system"  # Default theme (light, dark, system)
    DEFAULT_FONT_SIZE: str = "medium"  # Default font size (small, medium, large, extra_large)
    DEFAULT_INFO_DENSITY: str = "comfortable"  # Default info density (comfortable, compact)
    WCAG_COMPLIANCE_LEVEL: str = "AA"  # WCAG accessibility level

    # Analytics & Reporting Settings (Module 11)
    REPORT_DATA_FRESHNESS_MINUTES: int = 1  # Real-time <1 min for operational reports
    TIMESHEET_APPROVAL_REQUIRED: bool = True  # Require PM approval for timesheets
    DAILY_LOG_WARNING_HOURS: int = 12  # Soft warning if daily log exceeds this
    DAILY_LOG_MAX_HOURS: int = 24  # Hard limit for daily time logging
    MAX_REPORT_EXPORT_SIZE_MB: int = 100  # Max export file size for reports
    REPORT_CACHE_TTL_SECONDS: int = 300  # Cache TTL for report results (5 minutes)

    # API Integration Settings (Module 12 - Feature 2.1: API Access)
    API_TOKEN_EXPIRY_DAYS: int = 365  # Default token expiration
    API_TOKEN_HASH_ALGORITHM: str = "sha256"  # Token hashing algorithm
    
    # Rate Limiting Settings (Module 12 - Feature 2.1: Rate Limiting)
    RATE_LIMIT_TIER_FREE_REQ_PER_MIN: int = 60  # Free tier: 60 req/min
    RATE_LIMIT_TIER_PRO_REQ_PER_MIN: int = 1000  # Pro tier: 1000 req/min
    RATE_LIMIT_TIER_ENTERPRISE_REQ_PER_MIN: int = 5000  # Enterprise tier: 5000 req/min
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # Rate limit window in seconds
    
    # Webhook Settings (Module 12 - Feature 2.2: Webhooks)
    WEBHOOK_MAX_RETRIES: int = 5  # Maximum retry attempts
    WEBHOOK_RETRY_BACKOFF_SECONDS: int = 60  # Base backoff in seconds (exponential)
    WEBHOOK_TIMEOUT_SECONDS: int = 30  # Webhook request timeout
    WEBHOOK_MAX_PAYLOAD_SIZE_KB: int = 1024  # Max webhook payload size
    WEBHOOK_DELIVERY_TTL_HOURS: int = 24  # How long to keep delivery records
    WEBHOOK_QUEUE_MAX_SIZE: int = 10000  # Max pending webhook deliveries
    
    # OAuth Settings (Module 12 - Feature 3: OAuth)
    OAUTH_TOKEN_EXPIRY_MINUTES: int = 60  # OAuth token expiration
    OAUTH_REFRESH_TOKEN_EXPIRY_DAYS: int = 30  # Refresh token expiration
    OAUTH_AUTHORIZATION_CODE_EXPIRY_MINUTES: int = 10  # Auth code expiration
    OAUTH_REDIRECT_URI_BASE: str = "http://localhost:3000"  # OAuth redirect base URL
    
    # Plugin Settings (Module 12 - Feature 5: Plugin Marketplace)
    PLUGIN_MAX_SIZE_MB: int = 50  # Max plugin bundle size
    PLUGIN_MAX_INSTALLABLE_PER_WORKSPACE: int = 100  # Max plugins per workspace
    PLUGIN_EXECUTION_TIMEOUT_SECONDS: int = 30  # Plugin execution timeout
    PLUGIN_MANIFEST_VERSION: str = "1.0.0"  # Current plugin manifest version
    
    # Consent & Governance Settings (Module 12 - Feature 6: Governance)
    CONSENT_POLICY_VERSION: int = 1  # Current consent policy version
    CONSENT_AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years for GDPR compliance
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
