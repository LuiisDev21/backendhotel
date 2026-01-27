from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configurar bcrypt con identificación explícita para compatibilidad
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"
)


def VerificarContrasena(ContrasenaPlana: str, ContrasenaEncriptada: str) -> bool:
    """
    Verifica una contraseña plana contra un hash bcrypt.
    
    Args:
        ContrasenaPlana: Contraseña en texto plano
        ContrasenaEncriptada: Hash bcrypt almacenado
        
    Returns:
        True si la contraseña coincide, False en caso contrario
    """
    try:
        # Validar que ambos son strings
        if not isinstance(ContrasenaPlana, str) or not isinstance(ContrasenaEncriptada, str):
            return False
        
        # Verificar la contraseña
        return pwd_context.verify(ContrasenaPlana, ContrasenaEncriptada)
    except (ValueError, TypeError, AttributeError) as e:
        # Si hay error (hash inválido, incompatibilidad, etc.), retornar False
        return False


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
