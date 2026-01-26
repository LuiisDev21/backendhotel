from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuarioActual, ObtenerAdministradorActual
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def RegistrarUsuario(DatosUsuario: UsuarioCreate, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = UsuarioService(SesionBD)
    return Servicio.CrearUsuario(DatosUsuario)


@router.post("/login", response_model=Token)
def IniciarSesion(DatosLogin: UsuarioLogin, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = UsuarioService(SesionBD)
    return Servicio.AutenticarUsuario(DatosLogin)


@router.get("/me", response_model=UsuarioResponse)
def ObtenerUsuarioActualEndpoint(UsuarioActual: Usuario = Depends(ObtenerUsuarioActual)):
    return UsuarioActual


@router.get("/usuarios", response_model=List[UsuarioResponse], dependencies=[Depends(ObtenerAdministradorActual)])
def ListarUsuarios(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = UsuarioService(SesionBD)
    return Servicio.ListarUsuarios(Saltar=Saltar, Limite=Limite)
