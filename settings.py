from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: SecretStr
    db_url: str
    redis_url: str
    stars_per_day: int
    debug: bool

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()