"""
Repositorio de Sesiones de usuario (refresh tokens).
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.sesion_usuario import SesionUsuario


class SesionUsuarioRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def Crear(
        self,
        UsuarioId: int,
        RefreshTokenHash: str,
        FechaExpiracion: datetime,
        IpAddress: Optional[str] = None,
        UserAgent: Optional[str] = None,
        Dispositivo: Optional[str] = None,
    ) -> SesionUsuario:
        sesion = SesionUsuario(
            usuario_id=UsuarioId,
            refresh_token_hash=RefreshTokenHash,
            fecha_expiracion=FechaExpiracion,
            ip_address=IpAddress,
            user_agent=UserAgent,
            dispositivo=Dispositivo,
        )
        self.SesionBD.add(sesion)
        self.SesionBD.commit()
        self.SesionBD.refresh(sesion)
        return sesion

    def ObtenerPorTokenHash(
        self,
        RefreshTokenHash: str
    ) -> Optional[SesionUsuario]:
        return (
            self.SesionBD.query(SesionUsuario)
            .filter(
                SesionUsuario.refresh_token_hash == RefreshTokenHash,
                SesionUsuario.activa == True,
            )
            .first()
        )

    def ActualizarUltimoUso(self, Sesion: SesionUsuario) -> SesionUsuario:
        from datetime import datetime, timezone
        Sesion.fecha_ultimo_uso = datetime.now(timezone.utc)
        self.SesionBD.commit()
        self.SesionBD.refresh(Sesion)
        return Sesion

    def Revocar(self, Sesion: SesionUsuario, RevocadoPor: Optional[int] = None) -> None:
        from datetime import datetime, timezone
        Sesion.activa = False
        Sesion.revocada_en = datetime.now(timezone.utc)
        Sesion.revocada_por = RevocadoPor
        self.SesionBD.commit()
