from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Reservas de Hotel"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
