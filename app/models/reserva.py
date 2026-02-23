"""
Modelo de Reserva con SQLAlchemy.
"""
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Date, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
from app.core.enum_type import EnumType


class EstadoReserva(str, enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"
    NO_SHOW = "no_show"


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id", ondelete="RESTRICT"), nullable=False)
    politica_cancelacion_id = Column(
        Integer,
        ForeignKey("politicas_cancelacion.id", ondelete="SET NULL"),
        nullable=True
    )
    codigo_reserva = Column(String(20), unique=True, nullable=False, index=True)
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    numero_huespedes = Column(Integer, nullable=False)
    precio_total = Column(Numeric(12, 2), nullable=False)
    precio_por_noche_snapshot = Column(Numeric(12, 2), nullable=False)
    estado = Column(EnumType(EstadoReserva), default=EstadoReserva.PENDIENTE)
    canal_reserva = Column(String(50), default="web")
    notas = Column(String(1000), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")
    politica_cancelacion = relationship("PoliticaCancelacion", back_populates="reservas")
    transacciones_pago = relationship(
        "TransaccionPago",
        back_populates="reserva",
        order_by="TransaccionPago.fecha_creacion"
    )
    historial_estados = relationship(
        "HistorialEstadoReserva",
        back_populates="reserva",
        cascade="all, delete-orphan"
    )
