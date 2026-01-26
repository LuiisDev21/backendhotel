from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    return service.crear_usuario(usuario_data)


@router.post("/login", response_model=Token)
def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    return service.autenticar_usuario(login_data)


@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(current_user: Usuario = Depends(get_current_user)):
    return current_user
