"""
Modelo de Transacción de pago (1:N por reserva).
"""
from sqlalchemy import Column, BigInteger, Integer, String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
from app.core.enum_type import EnumType


class MetodoPago(str, enum.Enum):
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    PAYPAL = "paypal"
    CRIPTO = "cripto"


class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    RECHAZADO = "rechazado"
    REEMBOLSADO = "reembolsado"
    EN_PROCESO = "en_proceso"
    DISPUTADO = "disputado"


class TipoTransaccion(str, enum.Enum):
    CARGO = "cargo"
    REEMBOLSO = "reembolso"
    DEPOSITO = "deposito"
    AJUSTE = "ajuste"
    PENALIZACION = "penalizacion"


class TransaccionPago(Base):
    __tablename__ = "transacciones_pago"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    reserva_id = Column(BigInteger, ForeignKey("reservas.id", ondelete="RESTRICT"), nullable=False)
    tipo = Column(EnumType(TipoTransaccion), nullable=False, default=TipoTransaccion.CARGO)
    monto = Column(Numeric(12, 2), nullable=False)
    metodo_pago = Column(EnumType(MetodoPago), nullable=False)
    estado = Column(EnumType(EstadoPago), default=EstadoPago.PENDIENTE)
    numero_transaccion = Column(String(150), unique=True, nullable=True)
    referencia_externa = Column(String(255), nullable=True)
    pasarela_pago = Column(String(50), nullable=True)
    moneda = Column(String(3), default="USD")
    tasa_cambio = Column(Numeric(10, 6), default=1.0)
    monto_moneda_local = Column(Numeric(12, 2), nullable=True)
    notas = Column(Text, nullable=True)
    procesado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reserva = relationship("Reserva", back_populates="transacciones_pago")
