from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""

    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    # Rate Limiting
    AUTH_RATE_LIMIT: str = "5/minute"  # 5 requests per minute for auth endpoints
    TASKS_RATE_LIMIT: str = "30/minute"  # 30 requests per minute for task endpoints

    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator('BETTER_AUTH_SECRET')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate JWT secret key has minimum length"""
        if len(v) < 32:
            raise ValueError('BETTER_AUTH_SECRET must be at least 32 characters long for security')
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
