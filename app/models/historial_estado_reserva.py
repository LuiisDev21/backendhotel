"""
Modelo de Historial de estados de reserva.
"""
from sqlalchemy import Column, BigInteger, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.enum_type import EnumType
from app.models.reserva import EstadoReserva


class HistorialEstadoReserva(Base):
    __tablename__ = "historial_estados_reserva"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    reserva_id = Column(BigInteger, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False)
    estado_anterior = Column(EnumType(EstadoReserva), nullable=True)
    estado_nuevo = Column(EnumType(EstadoReserva), nullable=False)
    motivo = Column(Text, nullable=True)
    cambiado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    fecha_cambio = Column(DateTime(timezone=True), server_default=func.now())

    reserva = relationship("Reserva", back_populates="historial_estados")
