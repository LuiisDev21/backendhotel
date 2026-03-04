"""
Dependencias de FastAPI para autenticación y autorización.
- ObtenerUsuario: Obtiene el usuario actual con roles y permisos cargados.
- TienePermiso: Verifica que el usuario tenga un permiso por código (RBAC).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import ObtenerSesionBD
from app.core.security import DecodificarTokenAcceso
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def ObtenerUsuario(
    Token: str = Depends(oauth2_scheme),
    SesionBD: Session = Depends(ObtenerSesionBD)
) -> Usuario:
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
    UsuarioEncontrado = RepositorioUsuario.ObtenerPorId(IdUsuario, ConRolesPermisos=True)
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


def _codigos_permisos(UsuarioActual: Usuario) -> set:
    codigos = set()
    for rol in (UsuarioActual.roles or []):
        for permiso in (rol.permisos or []):
            if hasattr(permiso, "codigo"):
                codigos.add(permiso.codigo)
    return codigos


def UsuarioTienePermiso(UsuarioActual: Usuario, permiso_requerido: str) -> bool:
    """Comprueba si el usuario tiene el permiso (para uso en rutas: propio recurso o permiso)."""
    return permiso_requerido in _codigos_permisos(UsuarioActual)


def TienePermiso(permiso_requerido: str):
    """Dependencia que exige que el usuario tenga el permiso indicado (RBAC)."""

    async def _verificar(
        UsuarioActual: Usuario = Depends(ObtenerUsuario)
    ) -> Usuario:
        if permiso_requerido not in _codigos_permisos(UsuarioActual):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permiso: {permiso_requerido}"
            )
        return UsuarioActual

    return _verificar
