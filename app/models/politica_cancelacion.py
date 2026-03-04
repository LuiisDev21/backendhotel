"""
Modelo de Política de cancelación.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PoliticaCancelacion(Base):
    __tablename__ = "politicas_cancelacion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    horas_anticipacion = Column(Integer, nullable=False)
    porcentaje_penalizacion = Column(Numeric(5, 2), default=0)
    aplica_a_tipo_habitacion_id = Column(
        Integer,
        ForeignKey("tipos_habitacion.id", ondelete="SET NULL"),
        nullable=True
    )
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    reservas = relationship("Reserva", back_populates="politica_cancelacion")
    habitaciones = relationship("Habitacion", back_populates="politica_cancelacion")
