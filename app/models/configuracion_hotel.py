"""
Modelo de Configuración del hotel.
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ConfiguracionHotel(Base):
    __tablename__ = "configuracion_hotel"

    clave = Column(String(100), primary_key=True)
    valor = Column(Text, nullable=False)
    tipo = Column(String(20), default="string")
    descripcion = Column(Text, nullable=True)
    modificable = Column(Boolean, default=True)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    actualizado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
