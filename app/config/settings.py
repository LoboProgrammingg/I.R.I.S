"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    All settings are loaded from environment variables.
    Prefix: IRIS_
    """

    model_config = SettingsConfigDict(
        env_prefix="IRIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "IRIS Billing"
    app_env: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://iris:iris@localhost:5432/iris"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Paytime
    paytime_base_url: str = "https://api.paytime.com.br/v1"
    paytime_api_key: str = ""
    paytime_webhook_secret: str = ""

    # Gemini LLM
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.5-pro"
    gemini_timeout_seconds: int = 30

    # AI Conversation State
    ai_state_ttl_seconds: int = 1800  # 30 minutes
    ai_confirmation_ttl_seconds: int = 300  # 5 minutes

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.app_env == "test"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
