from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings


class UsuarioService:
    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)
        self.db = db

    def crear_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        if self.repository.get_by_email(usuario_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        hashed_password = get_password_hash(usuario_data.password)
        nuevo_usuario = Usuario(
            email=usuario_data.email,
            nombre=usuario_data.nombre,
            apellido=usuario_data.apellido,
            telefono=usuario_data.telefono,
            hashed_password=hashed_password
        )
        return self.repository.create(nuevo_usuario)

    def autenticar_usuario(self, login_data: UsuarioLogin) -> Token:
        usuario = self.repository.get_by_email(login_data.email)
        if not usuario or not verify_password(login_data.password, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(usuario.id)},  # Convertir a string porque JWT requiere que 'sub' sea string
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def obtener_usuario_actual(self, usuario_id: int) -> Usuario:
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario
