"""
Configuración de la aplicación, se define la configuración central de la API con Pydantic Settings: 
    - lee las variables del archivo .env (base de datos, clave JWT, Supabase, etc.)
    - las valida y las expone mediante la instancia global settings para que el resto de la aplicación las use de forma tipada y segura.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RoyalPalms API"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET: str = "habitaciones"
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
