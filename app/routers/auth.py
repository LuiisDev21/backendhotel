"""
Routers de Autenticación: registro, login con refresh token, listar usuarios (RBAC).
"""
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuario, TienePermiso
from app.schemas.usuario import UsuarioCreate, UsuarioConRolesResponse, UsuarioLogin, Token, RefreshTokenBody, AsignarRolesBody
from app.services.usuario_service import ServicioUsuarios
from app.models.usuario import Usuario
from app.models.rol import Rol

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioConRolesResponse, status_code=201)
def RegistrarUsuario(DatosUsuario: UsuarioCreate, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.CrearUsuario(DatosUsuario)


@router.post("/login", response_model=Token)
def IniciarSesion(
    DatosLogin: UsuarioLogin,
    request: Request,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioUsuarios(SesionBD)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return Servicio.AutenticarUsuario(DatosLogin, IpAddress=ip, UserAgent=user_agent)


@router.post("/refresh", response_model=Token)
def RefrescarToken(
    body: RefreshTokenBody,
    request: Request,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioUsuarios(SesionBD)
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return Servicio.RefrescarToken(body.refresh_token, IpAddress=ip, UserAgent=user_agent)


@router.get("/me", response_model=UsuarioConRolesResponse)
def ObtenerUsuarioEndpoint(UsuarioActual: Usuario = Depends(ObtenerUsuario)):
    return UsuarioActual


@router.get("/usuarios", response_model=List[UsuarioConRolesResponse], dependencies=[Depends(TienePermiso("usuarios.gestionar"))])
def ListarUsuarios(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.ListarUsuarios(Saltar=Saltar, Limite=Limite)


@router.get("/roles", response_model=List[dict])
def ListarRoles(SesionBD: Session = Depends(ObtenerSesionBD)):
    """Lista todos los roles (id, nombre) para asignar a usuarios. Público para poder mostrar en formularios."""
    roles = SesionBD.query(Rol).filter(Rol.activo == True).order_by(Rol.nombre).all()
    return [{"id": r.id, "nombre": r.nombre} for r in roles]


@router.put("/usuarios/{usuario_id}/roles", response_model=UsuarioConRolesResponse, dependencies=[Depends(TienePermiso("usuarios.gestionar"))])
def AsignarRolesUsuario(
    usuario_id: int,
    body: AsignarRolesBody,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Asigna los roles indicados al usuario (reemplaza los actuales). Requiere permiso usuarios.gestionar."""
    Servicio = ServicioUsuarios(SesionBD)
    usuario = Servicio.AsignarRolesUsuario(usuario_id, body.rol_ids, AsignadoPorId=UsuarioActual.id)
    return usuario
