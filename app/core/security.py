from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def VerificarContrasena(ContrasenaPlana: str, ContrasenaEncriptada: str) -> bool:
    return pwd_context.verify(ContrasenaPlana, ContrasenaEncriptada)


def ObtenerHashContrasena(Contrasena: str) -> str:
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
