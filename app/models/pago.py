""" 
Modelo de Pago, se define el modelo de pago con SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base
from app.core.enum_type import EnumType


class MetodoPago(str, enum.Enum):
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"


class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    RECHAZADO = "rechazado"
    REEMBOLSADO = "reembolsado"


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), unique=True, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(EnumType(MetodoPago), nullable=False)
    estado = Column(EnumType(EstadoPago), default=EstadoPago.PENDIENTE)
    numero_transaccion = Column(String, unique=True, nullable=True)
    fecha_pago = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    reserva = relationship("Reserva", back_populates="pago")
