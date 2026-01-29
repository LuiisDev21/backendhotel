from pydantic import BaseModel, model_validator
from typing import Optional, Any
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
    pass


class ReservaUpdate(BaseModel):
    fecha_entrada: Optional[date] = None
    fecha_salida: Optional[date] = None
    numero_huespedes: Optional[int] = None
    estado: Optional[EstadoReserva] = None
    notas: Optional[str] = None


class ReservaResponse(ReservaBase):
    id: int
    usuario_id: int
    precio_total: Decimal
    estado: EstadoReserva
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    numero_habitacion: Optional[str] = None
    nombre_usuario: Optional[str] = None

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    @classmethod
    def extraer_datos_relaciones(cls, data: Any) -> Any:
        # Si es un objeto ORM, extraer datos de las relaciones
        if hasattr(data, '__dict__'):
            # Extraer número de habitación
            if hasattr(data, 'habitacion') and data.habitacion:
                data.__dict__['numero_habitacion'] = data.habitacion.numero
            # Extraer nombre completo del usuario
            if hasattr(data, 'usuario') and data.usuario:
                data.__dict__['nombre_usuario'] = f"{data.usuario.nombre} {data.usuario.apellido}"
        return data
