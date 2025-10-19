from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (.env supported)."""

    # MongoDB
    mongodb_uri: SecretStr = Field(alias="MONGODB_URI")
    mongodb_database: str = Field(alias="MONGODB_DATABASE", default="m365_organizer")

    # Azure AD / M365
    azure_client_id: str = Field(alias="AZURE_CLIENT_ID")
    azure_client_secret: SecretStr = Field(alias="AZURE_CLIENT_SECRET")
    azure_tenant_id: str = Field(alias="AZURE_TENANT_ID")
    azure_redirect_uri: Optional[str] = Field(alias="AZURE_REDIRECT_URI", default=None)

    # Claude API
    anthropic_api_key: SecretStr = Field(alias="ANTHROPIC_API_KEY")

    # App settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        alias="LOG_LEVEL", default="INFO"
    )
    batch_size: int = Field(alias="BATCH_SIZE", default=10, ge=1, le=100)
    max_file_size_mb: int = Field(alias="MAX_FILE_SIZE_MB", default=150, ge=1)
    processing_mode: Literal["batch", "continuous"] = Field(
        alias="PROCESSING_MODE", default="batch"
    )

    # FastAPI (optional)
    api_host: str = Field(alias="API_HOST", default="0.0.0.0")
    api_port: int = Field(alias="API_PORT", default=8000, ge=1, le=65535)
    api_workers: int = Field(alias="API_WORKERS", default=4, ge=1, le=64)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    @validator("azure_redirect_uri")
    def _validate_redirect_uri(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("AZURE_REDIRECT_URI must start with http:// or https://")
        return v


settings = Settings()  # Singleton instance used across the app
