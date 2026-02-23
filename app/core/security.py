"""
Funciones de seguridad para la API.
"""
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


#! Configuracion de Bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"
)


def VerificarContrasena(ContrasenaPlana: str, ContrasenaEncriptada: str) -> bool:
    try:
        if not isinstance(ContrasenaPlana, str) or not isinstance(ContrasenaEncriptada, str):
            return False
        return pwd_context.verify(ContrasenaPlana, ContrasenaEncriptada)
    except (ValueError, TypeError, AttributeError) as e:
        return False


def HashearContra(Contrasena: str) -> str:
    return pwd_context.hash(Contrasena)


def CrearTokenAcceso(Datos: dict, TiempoExpiracion: Optional[timedelta] = None) -> str:
    DatosACodificar = Datos.copy()
    now = datetime.now(timezone.utc)
    if TiempoExpiracion:
        FechaExpiracion = now + TiempoExpiracion
    else:
        FechaExpiracion = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    DatosACodificar.update({"exp": FechaExpiracion})
    TokenCodificado = jwt.encode(DatosACodificar, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return TokenCodificado


def GenerarRefreshToken() -> str:
    """Genera un token de refresco aleatorio (url-safe)."""
    return secrets.token_urlsafe(64)


def HashearRefreshToken(Token: str) -> str:
    """Hash SHA-256 del refresh token para almacenar en BD."""
    return hashlib.sha256(Token.encode()).hexdigest()


def DecodificarTokenAcceso(Token: str) -> Optional[dict]:
    try:
        Payload = jwt.decode(Token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return Payload
    except JWTError:
        return None
