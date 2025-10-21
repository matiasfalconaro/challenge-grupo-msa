import os

from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "API de Asignación de Escaños D'Hondt"
    app_version: str = "1.0.0"
    app_description: str = (
        "API para calcular la distribución proporcional de escaños usando el método D'Hondt"
    )

    database_url: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    sqlalchemy_pool_size: int = 10
    sqlalchemy_max_overflow: int = 20
    sqlalchemy_pool_timeout: int = 30
    sqlalchemy_pool_recycle: int = 3600
    sqlalchemy_echo: bool = False

    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:4321",
        "http://frontend:3000",
    ]
    cors_credentials: bool = True
    cors_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: list = ["Content-Type", "Authorization", "X-Request-ID"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
