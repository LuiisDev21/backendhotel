from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class EstadoReserva(str, enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    numero_huespedes = Column(Integer, nullable=False)
    precio_total = Column(Numeric(10, 2), nullable=False)
    estado = Column(SQLEnum(EstadoReserva), default=EstadoReserva.PENDIENTE)
    notas = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")
    pago = relationship("Pago", back_populates="reserva", uselist=False)
