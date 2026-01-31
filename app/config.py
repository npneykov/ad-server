"""Centralized configuration using Pydantic Settings."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    # Environment
    app_env: str = 'production'

    # Database
    database_url: str | None = None
    local_database_url: str = 'sqlite:///./adserver.db'

    # Security
    admin_key: str | None = None

    # External services
    adsterra_smartlink: str = (
        'https://www.revenuecpmgate.com/kh3axptg1?key=1685a081c46f9b5d7aaa7abf4d050eb3'
    )

    # Paths
    blog_dir: str = os.path.join('templates', 'public')

    @property
    def effective_database_url(self) -> str:
        """Return the appropriate database URL based on environment."""
        if self.app_env == 'development':
            return self.local_database_url
        if not self.database_url:
            raise ValueError('DATABASE_URL environment variable is not set.')
        return self.database_url

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == 'development'


def get_settings() -> Settings:
    """Get settings instance (reads from environment each time)."""
    return Settings()
