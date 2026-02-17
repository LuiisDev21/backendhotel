"""
Modelo de TipoHabitacion, se define el modelo de tipo de habitación con SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TipoHabitacion(Base):
    __tablename__ = "tipos_habitacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    capacidad_maxima = Column(Integer, nullable=False)
    precio_base = Column(Numeric(10, 2), nullable=False)
    activo = Column(Boolean, default=True, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habitaciones = relationship("Habitacion", back_populates="tipo_habitacion")
