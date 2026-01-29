"""  
Servicio de Usuarios, se define el servicio de usuarios con SQLAlchemy.
- CrearUsuario: Crea un nuevo usuario.
- AutenticarUsuario: Autentica un usuario.
- ObtenerUsuario: Obtiene un usuario por su ID.
- ListarUsuarios: Lista todos los usuarios.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, Token
from app.core.security import VerificarContrasena, HashearContra, CrearTokenAcceso
from app.core.config import settings


class ServicioUsuarios:
    def __init__(self, SesionBD: Session):
        self.Repositorio = UsuarioRepository(SesionBD)
        self.SesionBD = SesionBD

    def CrearUsuario(self, DatosUsuario: UsuarioCreate) -> Usuario:
        if self.Repositorio.ObtenerPorEmail(DatosUsuario.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        ContrasenaEncriptada = HashearContra(DatosUsuario.password)
        
        NuevoUsuario = Usuario(
            email=DatosUsuario.email,
            nombre=DatosUsuario.nombre,
            apellido=DatosUsuario.apellido,
            telefono=DatosUsuario.telefono,
            hashed_password=ContrasenaEncriptada
        )
        return self.Repositorio.Crear(NuevoUsuario)

    def AutenticarUsuario(self, DatosLogin: UsuarioLogin) -> Token:
        
        UsuarioEncontrado = self.Repositorio.ObtenerPorEmail(DatosLogin.email)
        if not UsuarioEncontrado or not VerificarContrasena(DatosLogin.password, UsuarioEncontrado.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        if not UsuarioEncontrado.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        TiempoExpiracion = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        TokenAcceso = CrearTokenAcceso(
            Datos={"sub": str(UsuarioEncontrado.id)},
            TiempoExpiracion=TiempoExpiracion
        )
        return Token(access_token=TokenAcceso, token_type="bearer")

    def ObtenerUsuario(self, IdUsuario: int) -> Usuario:
        UsuarioEncontrado = self.Repositorio.ObtenerPorId(IdUsuario)
        if not UsuarioEncontrado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UsuarioEncontrado

    def ListarUsuarios(self, Saltar: int = 0, Limite: int = 100):
        return self.Repositorio.ObtenerTodos(Saltar=Saltar, Limite=Limite)
