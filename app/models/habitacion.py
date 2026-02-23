"""
Modelo de Habitación con SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False, index=True)
    tipo_habitacion_id = Column(Integer, ForeignKey("tipos_habitacion.id", ondelete="RESTRICT"), nullable=False, index=True)
    politica_cancelacion_id = Column(Integer, ForeignKey("politicas_cancelacion.id", ondelete="SET NULL"), nullable=True, index=True)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=False)
    precio_por_noche = Column(Numeric(12, 2), nullable=False)
    estado = Column(String(20), default="disponible", index=True)  # disponible, ocupada, mantenimiento, limpieza, bloqueada
    imagen_url = Column(String(500), nullable=True)
    piso = Column(Integer, nullable=True)
    caracteristicas = Column(JSONB, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tipo_habitacion = relationship("TipoHabitacion", back_populates="habitaciones")
    politica_cancelacion = relationship("PoliticaCancelacion", back_populates="habitaciones")
    reservas = relationship("Reserva", back_populates="habitacion")
