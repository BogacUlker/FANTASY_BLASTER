"""
Application configuration management with environment-based settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Application
    APP_NAME: str = "Fantasy Basketball Analyzer"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/fantasy_bball",
        description="PostgreSQL connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Max overflow connections")

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_CACHE_TTL_DEFAULT: int = Field(default=300, description="Default cache TTL in seconds")

    # Security
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT signing secret"
    )
    JWT_REFRESH_SECRET_KEY: str = Field(
        default="dev-refresh-secret-key-change-in-production",
        description="JWT refresh token secret"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

    # Yahoo OAuth
    YAHOO_CLIENT_ID: str = Field(default="", description="Yahoo OAuth client ID")
    YAHOO_CLIENT_SECRET: str = Field(default="", description="Yahoo OAuth client secret")
    YAHOO_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/yahoo/callback",
        description="Yahoo OAuth redirect URI"
    )

    # External APIs
    NBA_API_TIMEOUT: int = Field(default=30, description="NBA API request timeout")

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend"
    )

    # Rate Limiting
    RATE_LIMIT_FREE_TIER: int = Field(default=100, description="Free tier requests/hour")
    RATE_LIMIT_PRO_TIER: int = Field(default=1000, description="Pro tier requests/hour")
    RATE_LIMIT_PREMIUM_TIER: int = Field(default=10000, description="Premium tier requests/hour")

    # Monitoring
    SENTRY_DSN: str | None = Field(default=None, description="Sentry DSN for error tracking")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
