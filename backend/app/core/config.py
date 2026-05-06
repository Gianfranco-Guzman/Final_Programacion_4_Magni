from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno"""

    # Database
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "foodstore"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/foodstore?client_encoding=utf8"

    # JWT
    secret_key: str = "dev-secret-key-for-testing-only-minimum-32-chars-required"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # FastAPI
    debug: bool = True
    app_name: str = "Food Store API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte string de origins a lista"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cache de settings para reutilizar instancia"""
    return Settings()
