from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    log_level: str = "INFO"
    local_fallbacks: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
