from pathlib import Path

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "foodstore"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/foodstore?client_encoding=utf8"

    secret_key: str = "dev-secret-key-for-testing-only-minimum-32-chars-required"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    auth_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"
    auth_rate_limit_attempts: int = 5
    auth_rate_limit_window_minutes: int = 15


    debug: bool = True
    app_name: str = "Food Store API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:5173"

    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte string de origins a lista"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
