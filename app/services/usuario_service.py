"""
Servicio de Usuarios: registro, login con protección fuerza bruta y sesiones (refresh token).
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta, datetime, timezone
from typing import Optional
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.configuracion_hotel_repository import ConfiguracionHotelRepository
from app.repositories.sesion_usuario_repository import SesionUsuarioRepository
from app.repositories.intento_autenticacion_repository import IntentoAutenticacionRepository
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, Token
from app.core.security import (
    VerificarContrasena,
    HashearContra,
    CrearTokenAcceso,
    GenerarRefreshToken,
    HashearRefreshToken,
)
from app.core.config import settings

# Días de validez del refresh token por defecto
REFRESH_TOKEN_EXPIRE_DAYS = 7


class ServicioUsuarios:
    def __init__(self, SesionBD: Session):
        self.Repositorio = UsuarioRepository(SesionBD)
        self.RepoConfig = ConfiguracionHotelRepository(SesionBD)
        self.RepoSesion = SesionUsuarioRepository(SesionBD)
        self.RepoIntento = IntentoAutenticacionRepository(SesionBD)
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

    def AutenticarUsuario(
        self,
        DatosLogin: UsuarioLogin,
        IpAddress: Optional[str] = None,
        UserAgent: Optional[str] = None
    ) -> Token:
        max_intentos = self.RepoConfig.ObtenerValorEntero("max_intentos_login", 5)
        minutos_bloqueo = self.RepoConfig.ObtenerValorEntero("minutos_bloqueo_login", 30)

        UsuarioEncontrado = self.Repositorio.ObtenerPorEmail(DatosLogin.email)
        if not UsuarioEncontrado:
            self.RepoIntento.Registrar(
                Email=DatosLogin.email,
                Exitoso=False,
                IpAddress=IpAddress,
                MotivoFallo="usuario_no_existe"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        ahora = datetime.now(timezone.utc)
        if UsuarioEncontrado.bloqueado_hasta and UsuarioEncontrado.bloqueado_hasta > ahora:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cuenta bloqueada hasta {UsuarioEncontrado.bloqueado_hasta.isoformat()}"
            )

        if not VerificarContrasena(DatosLogin.password, UsuarioEncontrado.hashed_password):
            UsuarioEncontrado.intentos_fallidos = (UsuarioEncontrado.intentos_fallidos or 0) + 1
            if UsuarioEncontrado.intentos_fallidos >= max_intentos:
                from datetime import timedelta as td
                UsuarioEncontrado.bloqueado_hasta = ahora + td(minutes=minutos_bloqueo)
            self.Repositorio.Actualizar(UsuarioEncontrado)
            self.RepoIntento.Registrar(
                Email=DatosLogin.email,
                Exitoso=False,
                IpAddress=IpAddress,
                MotivoFallo="password_incorrecto"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        if not UsuarioEncontrado.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )

        UsuarioEncontrado.intentos_fallidos = 0
        UsuarioEncontrado.bloqueado_hasta = None
        UsuarioEncontrado.fecha_ultimo_login = ahora
        self.Repositorio.Actualizar(UsuarioEncontrado)
        self.RepoIntento.Registrar(
            Email=DatosLogin.email,
            Exitoso=True,
            IpAddress=IpAddress
        )

        TiempoExpiracion = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        TokenAcceso = CrearTokenAcceso(
            Datos={"sub": str(UsuarioEncontrado.id)},
            TiempoExpiracion=TiempoExpiracion
        )
        RefreshToken = GenerarRefreshToken()
        RefreshHash = HashearRefreshToken(RefreshToken)
        FechaExpiracionRefresh = ahora + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        self.RepoSesion.Crear(
            UsuarioId=UsuarioEncontrado.id,
            RefreshTokenHash=RefreshHash,
            FechaExpiracion=FechaExpiracionRefresh,
            IpAddress=IpAddress,
            UserAgent=UserAgent
        )
        return Token(
            access_token=TokenAcceso,
            token_type="bearer",
            refresh_token=RefreshToken,
            expires_in=int(TiempoExpiracion.total_seconds())
        )

    def RefrescarToken(
        self,
        RefreshToken: str,
        IpAddress: Optional[str] = None,
        UserAgent: Optional[str] = None
    ) -> Token:
        RefreshHash = HashearRefreshToken(RefreshToken)
        Sesion = self.RepoSesion.ObtenerPorTokenHash(RefreshHash)
        if not Sesion:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado"
            )
        ahora = datetime.now(timezone.utc)
        if Sesion.fecha_expiracion and Sesion.fecha_expiracion < ahora:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado"
            )
        self.RepoSesion.ActualizarUltimoUso(Sesion)
        UsuarioEncontrado = self.Repositorio.ObtenerPorId(Sesion.usuario_id)
        if not UsuarioEncontrado or not UsuarioEncontrado.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no válido"
            )
        TiempoExpiracion = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        TokenAcceso = CrearTokenAcceso(
            Datos={"sub": str(UsuarioEncontrado.id)},
            TiempoExpiracion=TiempoExpiracion
        )
        return Token(
            access_token=TokenAcceso,
            token_type="bearer",
            refresh_token=RefreshToken,
            expires_in=int(TiempoExpiracion.total_seconds())
        )

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

    def AsignarRolesUsuario(
        self,
        UsuarioId: int,
        RolIds: list,
        AsignadoPorId: Optional[int] = None
    ) -> Usuario:
        """Asigna los roles indicados al usuario (reemplaza los actuales)."""
        from app.models.rol import Rol
        usuario = self.Repositorio.ObtenerPorId(UsuarioId)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        if RolIds:
            roles_existentes = self.SesionBD.query(Rol).filter(Rol.id.in_(RolIds), Rol.activo == True).all()
            ids_validos = {r.id for r in roles_existentes}
            invalidos = set(RolIds) - ids_validos
            if invalidos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Roles no encontrados o inactivos: {sorted(invalidos)}"
                )
        return self.Repositorio.AsignarRoles(UsuarioId, list(RolIds), AsignadoPorId)
