"""It manages the .env file."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DISABLED_VALUES = {"", "none", "null", "false", "disabled"}


class Settings(BaseSettings):
    """All configuration comes from environment variables / the .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Nexgen Server"
    environment: str = "development"
    log_level: str = "INFO"

    # Auth
    api_key: str | None = None

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "nexgen"
    mongodb_max_pool_size: int = Field(default=100, ge=1)
    mongodb_min_pool_size: int = Field(default=0, ge=0)

    @property
    def api_keys(self) -> list[str]:
        """Parsed list of valid keys. Empty list => auth disabled."""
        if self.api_key is None:
            return []
        keys = [k.strip() for k in self.api_key.split(",")]
        return [k for k in keys if k.lower() not in _DISABLED_VALUES]

    @property
    def auth_enabled(self) -> bool:
        """It checks that auth is enabled or not."""
        return len(self.api_keys) > 0


@lru_cache
def get_settings() -> Settings:
    """It returns the settings."""
    return Settings()
