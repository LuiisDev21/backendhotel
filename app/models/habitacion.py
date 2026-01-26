from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, nullable=False, index=True)
    tipo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=False)
    precio_por_noche = Column(Numeric(10, 2), nullable=False)
    disponible = Column(Boolean, default=True)
    imagen_url = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    reservas = relationship("Reserva", back_populates="habitacion")
