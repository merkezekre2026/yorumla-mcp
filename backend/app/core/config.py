from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Yorumla MCP"
    database_url: str = "sqlite+aiosqlite:///./yorumla.db"
    cache_ttl_hours: int = 24
    max_reviews_per_product: int = 25
    scraper_timeout_ms: int = 12_000
    scraper_total_timeout_seconds: int = 25
    scraper_max_pages: int = 2
    scraper_headless: bool = True
    backend_cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    mcp_auth_token: str = Field(default="change-me")
    port: int = 8000

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
