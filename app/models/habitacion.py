"""
Modelo de Habitacion, se define el modelo de la habitacion con SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False, index=True)
    tipo_habitacion_id = Column(Integer, ForeignKey("tipos_habitacion.id"), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=False)
    precio_por_noche = Column(Numeric(10, 2), nullable=False)
    disponible = Column(Boolean, default=True, index=True)
    imagen_url = Column(String(500), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tipo_habitacion = relationship("TipoHabitacion", back_populates="habitaciones")
    reservas = relationship("Reserva", back_populates="habitacion")
