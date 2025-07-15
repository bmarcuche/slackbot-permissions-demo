"""
Configuration management for Slackbot Demo.

Handles environment variables, validation, and configuration defaults.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Slack Configuration
    slack_bot_token: str
    slack_signing_secret: str
    
    # Application Configuration
    log_level: str = "INFO"
    debug: bool = False
    port: int = 3000
    
    # Permission System Configuration
    admin_users: List[str] = []
    permission_cache_ttl: int = 300
    strict_mode: bool = True
    
    # Security Configuration
    rate_limit_requests: int = 10
    rate_limit_window: int = 60
    
    # Monitoring Configuration
    enable_metrics: bool = True
    metrics_port: int = 8080
    
    # Database Configuration
    database_url: Optional[str] = None
    
    @validator('admin_users', pre=True)
    def parse_admin_users(cls, v):
        """Parse comma-separated admin users."""
        if isinstance(v, str):
            return [user.strip() for user in v.split(',') if user.strip()]
        return v or []
    
    @validator('slack_bot_token')
    def validate_bot_token(cls, v):
        """Validate Slack bot token format."""
        if not v.startswith('xoxb-'):
            raise ValueError('Slack bot token must start with "xoxb-"')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def is_admin_user(user_id: str) -> bool:
    """Check if user is configured as admin."""
    return user_id in settings.admin_users


def get_database_url() -> str:
    """Get database URL with fallback to in-memory."""
    return settings.database_url or "sqlite:///:memory:"
