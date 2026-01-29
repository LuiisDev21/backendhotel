"""
Dependencias de FastAPI, se definen las dependencias para la autenticación y autorización de los endpoints.
- OAuth2PasswordBearer: Extrae automáticamente el token del header `Authorization: Bearer <token>`
- ObtenerUsuario: Obtiene el usuario actual a partir del token
- ObtenerAdministrador: Verifica si el usuario actual es administrador
"""




from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import ObtenerSesionBD
from app.core.security import DecodificarTokenAcceso
from app.repositories.usuario_repository import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")


async def ObtenerUsuario(
    Token: str = Depends(oauth2_scheme),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Payload = DecodificarTokenAcceso(Token)
    if Payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Por favor, inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    IdUsuarioStr = Payload.get("sub")
    if IdUsuarioStr is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta información del usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        IdUsuario = int(IdUsuarioStr)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: ID de usuario no válido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    RepositorioUsuario = UsuarioRepository(SesionBD)
    UsuarioEncontrado = RepositorioUsuario.ObtenerPorId(IdUsuario)
    if UsuarioEncontrado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not UsuarioEncontrado.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return UsuarioEncontrado


async def ObtenerAdministrador(
    UsuarioActual = Depends(ObtenerUsuario)
):
    if not UsuarioActual.es_administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return UsuarioActual