"""
Modelo de Intento de autenticación (auditoría de login).
"""
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func
from app.core.database import Base


class IntentoAutenticacion(Base):
    __tablename__ = "intentos_autenticacion"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    ip_address = Column(INET, nullable=True)
    exitoso = Column(Boolean, nullable=False)
    motivo_fallo = Column(String(100), nullable=True)
    fecha_intento = Column(DateTime(timezone=True), server_default=func.now())
