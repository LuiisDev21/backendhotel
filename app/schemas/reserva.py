from pydantic import BaseModel, model_validator
from typing import Optional, Any, List
from decimal import Decimal
from datetime import date, datetime
from app.models.reserva import EstadoReserva


class ReservaBase(BaseModel):
    habitacion_id: int
    fecha_entrada: date
    fecha_salida: date
    numero_huespedes: int
    notas: Optional[str] = None


class ReservaCreate(ReservaBase):
    canal_reserva: Optional[str] = "web"
    politica_cancelacion_id: Optional[int] = None


class ReservaUpdate(BaseModel):
    fecha_entrada: Optional[date] = None
    fecha_salida: Optional[date] = None
    numero_huespedes: Optional[int] = None
    estado: Optional[EstadoReserva] = None
    notas: Optional[str] = None


class TransaccionPagoEnReservaResponse(BaseModel):
    id: int
    tipo: str
    monto: Decimal
    metodo_pago: str
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ReservaResponse(ReservaBase):
    id: int
    usuario_id: int
    codigo_reserva: Optional[str] = None
    precio_total: Decimal
    precio_por_noche_snapshot: Optional[Decimal] = None
    canal_reserva: Optional[str] = "web"
    politica_cancelacion_id: Optional[int] = None
    estado: EstadoReserva
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    numero_habitacion: Optional[str] = None
    nombre_usuario: Optional[str] = None
    transacciones: Optional[List[TransaccionPagoEnReservaResponse]] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def extraer_datos_relaciones(cls, data: Any) -> Any:
        if hasattr(data, '__dict__'):
            if hasattr(data, 'habitacion') and data.habitacion:
                data.__dict__.setdefault('numero_habitacion', data.habitacion.numero)
            if hasattr(data, 'usuario') and data.usuario:
                data.__dict__.setdefault('nombre_usuario', f"{data.usuario.nombre} {data.usuario.apellido}")
            if hasattr(data, 'transacciones_pago') and data.transacciones_pago is not None:
                data.__dict__.setdefault('transacciones', data.transacciones_pago)
        return data
