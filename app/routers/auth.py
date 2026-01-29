""" 
Routers de Autenticación, se definen los routers de autenticación para la API.
- RegistrarUsuario: Registra un nuevo usuario.
- IniciarSesion: Inicia sesión de un usuario.
- ObtenerUsuarioEndpoint: Obtiene el usuario actual.
- ListarUsuarios: Lista todos los usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuario, ObtenerAdministrador
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from app.services.usuario_service import ServicioUsuarios
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def RegistrarUsuario(DatosUsuario: UsuarioCreate, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.CrearUsuario(DatosUsuario)


@router.post("/login", response_model=Token)
def IniciarSesion(DatosLogin: UsuarioLogin, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.AutenticarUsuario(DatosLogin)


@router.get("/me", response_model=UsuarioResponse)
def ObtenerUsuarioEndpoint(UsuarioActual: Usuario = Depends(ObtenerUsuario)):
    return UsuarioActual


@router.get("/usuarios", response_model=List[UsuarioResponse], dependencies=[Depends(ObtenerAdministrador)])
def ListarUsuarios(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.ListarUsuarios(Saltar=Saltar, Limite=Limite)
