"""
Repositorio de Intentos de autenticación (registro de logins).
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.models.intento_autenticacion import IntentoAutenticacion


class IntentoAutenticacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def Registrar(
        self,
        Email: str,
        Exitoso: bool,
        IpAddress: Optional[str] = None,
        MotivoFallo: Optional[str] = None
    ) -> IntentoAutenticacion:
        intento = IntentoAutenticacion(
            email=Email,
            exitoso=Exitoso,
            ip_address=IpAddress,
            motivo_fallo=MotivoFallo
        )
        self.SesionBD.add(intento)
        self.SesionBD.commit()
        self.SesionBD.refresh(intento)
        return intento
