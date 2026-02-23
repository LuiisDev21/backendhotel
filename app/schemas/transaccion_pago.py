from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.transaccion_pago import MetodoPago, EstadoPago, TipoTransaccion


class TransaccionPagoBase(BaseModel):
    reserva_id: int
    tipo: TipoTransaccion = TipoTransaccion.CARGO
    monto: Decimal
    metodo_pago: MetodoPago
    numero_transaccion: Optional[str] = None
    referencia_externa: Optional[str] = None
    pasarela_pago: Optional[str] = None
    moneda: str = "USD"
    notas: Optional[str] = None


class TransaccionPagoCreate(BaseModel):
    reserva_id: int
    tipo: TipoTransaccion = TipoTransaccion.CARGO
    monto: Decimal
    metodo_pago: MetodoPago
    numero_transaccion: Optional[str] = None
    referencia_externa: Optional[str] = None
    pasarela_pago: Optional[str] = None
    moneda: str = "USD"
    notas: Optional[str] = None


class TransaccionPagoUpdate(BaseModel):
    estado: Optional[EstadoPago] = None
    numero_transaccion: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    notas: Optional[str] = None


class TransaccionPagoResponse(BaseModel):
    id: int
    reserva_id: int
    tipo: TipoTransaccion
    monto: Decimal
    metodo_pago: MetodoPago
    estado: EstadoPago
    numero_transaccion: Optional[str] = None
    referencia_externa: Optional[str] = None
    pasarela_pago: Optional[str] = None
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    monto_moneda_local: Optional[Decimal] = None
    notas: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True
