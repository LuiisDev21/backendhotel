from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.pago import MetodoPago, EstadoPago


class PagoBase(BaseModel):
    reserva_id: int
    metodo_pago: MetodoPago


class PagoCreate(PagoBase):
    pass


class PagoUpdate(BaseModel):
    estado: Optional[EstadoPago] = None
    numero_transaccion: Optional[str] = None


class PagoResponse(PagoBase):
    id: int
    monto: Decimal
    estado: EstadoPago
    numero_transaccion: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True
