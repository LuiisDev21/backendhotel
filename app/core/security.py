"""
Funciones de seguridad para la API, se definen las funciones para la autenticación y autorización de los endpoints.
- VerificarContrasena: Verifica una contraseña plana contra un hash bcrypt.
- HashearContra: Hashea una contraseña plana y la devuelve como hash bcrypt.
- CrearTokenAcceso: Crea un token de acceso JWT.
- DecodificarTokenAcceso: Decodifica un token de acceso JWT.
"""

from datetime import datetime, timedelta
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
    if TiempoExpiracion:
        FechaExpiracion = datetime.utcnow() + TiempoExpiracion
    else:
        FechaExpiracion = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    DatosACodificar.update({"exp": FechaExpiracion})
    TokenCodificado = jwt.encode(DatosACodificar, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return TokenCodificado


def DecodificarTokenAcceso(Token: str) -> Optional[dict]:
    try:
        Payload = jwt.decode(Token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return Payload
    except JWTError:
        return None
