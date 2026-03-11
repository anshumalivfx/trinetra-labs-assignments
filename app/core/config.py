"""
Core Configuration Module
Centralized settings management using Pydantic Settings
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_NAME: str = "AI Agent Orchestration System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    SECRET_KEY: str = Field(..., min_length=32)

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Mistral AI
    MISTRAL_API_KEY: str = Field(..., description="Mistral AI API key")
    MISTRAL_MODEL: str = "open-mixtral-8x7b"  # Free tier model

    # Email Configuration
    EMAIL_PROVIDER: str = "sendgrid"  # or smtp
    SENDGRID_API_KEY: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@trinetralabs.ai"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"

    # Performance
    WORKER_TIMEOUT: int = 300
    MAX_CONCURRENT_JOBS: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
