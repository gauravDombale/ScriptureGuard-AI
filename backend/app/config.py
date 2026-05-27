from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    dalle_model: str = "gpt-image-2-2026-04-21"

    pinecone_api_key: str | None = None
    pinecone_index_name: str = "bible-kjv"
    pinecone_environment: str = "us-east-1-aws"

    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/christianai"

    secret_key: str = "change-me"
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001"
    )
    log_level: str = "INFO"
    local_fallbacks: bool = True
    external_request_timeout_seconds: float = 60.0
    image_generation_timeout_seconds: float = 300.0
    openai_max_retries: int = 2
    auto_create_tables: bool = True
    api_keys: str = ""
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 120
    max_request_body_bytes: int = 1_000_000
    metrics_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def api_key_set(self) -> set[str]:
        return {key.strip() for key in self.api_keys.split(",") if key.strip()}

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
