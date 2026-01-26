from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuarioActual
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
