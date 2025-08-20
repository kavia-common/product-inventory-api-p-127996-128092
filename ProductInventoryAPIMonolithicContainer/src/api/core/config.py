from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (.env)."""

    APP_NAME: str = "Product Inventory API"
    LOG_LEVEL: str = "INFO"

    # Server
    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # Database (MySQL) - fallback to SQLite for local/dev if MYSQL_* not available
    MYSQL_HOST: str = Field(default="", description="MySQL host")
    MYSQL_PORT: int = Field(default=3306, description="MySQL port")
    MYSQL_USER: str = Field(default="", description="MySQL user")
    MYSQL_PASSWORD: str = Field(default="", description="MySQL password")
    MYSQL_DB: str = Field(default="", description="MySQL database")
    SQLITE_URL: str = Field(default="sqlite:///./inventory.db", description="SQLite fallback URL for local dev/testing")
    SQL_ECHO: bool = Field(default=False, description="Echo SQL statements")

    # Auth
    JWT_SECRET_KEY: str = Field(default="change-me", description="Secret key for JWT")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token expiry in minutes")

    # Rate limit (e.g., '100/minute', '1000/hour')
    RATE_LIMIT: str = Field(default="100/minute", description="Global rate limit")

    # Webhooks
    WEBHOOK_SIGNATURE_SECRET: str = Field(default="change-me-webhook", description="Secret for webhook signatures")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def database_url(self) -> str:
        """Build the SQLAlchemy database URL.

        If MYSQL_* settings are provided, use MySQL; otherwise fall back to SQLite.
        """
        if all([self.MYSQL_HOST, self.MYSQL_USER, self.MYSQL_PASSWORD, self.MYSQL_DB]):
            return (
                f"mysql+mysqlclient://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            )
        return self.SQLITE_URL

    def masked_dict(self) -> dict:
        """Return setting values with sensitive data masked."""
        d = self.model_dump()
        for key in list(d.keys()):
            if "PASSWORD" in key or "SECRET" in key or "KEY" in key:
                d[key] = "***"
        return d


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> Settings:
    """This is a public function."""
    return Settings()
