from pydantic import BaseModel, model_validator
from typing import Optional, Any
from decimal import Decimal
from datetime import datetime


class HabitacionBase(BaseModel):
    numero: str
    tipo_habitacion_id: int
    politica_cancelacion_id: Optional[int] = None
    descripcion: Optional[str] = None
    capacidad: int
    precio_por_noche: Decimal
    estado: str = "disponible"
    imagen_url: Optional[str] = None
    piso: Optional[int] = None
    caracteristicas: Optional[dict] = None


class HabitacionCreate(HabitacionBase):
    pass


class HabitacionUpdate(BaseModel):
    tipo_habitacion_id: Optional[int] = None
    politica_cancelacion_id: Optional[int] = None
    descripcion: Optional[str] = None
    capacidad: Optional[int] = None
    precio_por_noche: Optional[Decimal] = None
    estado: Optional[str] = None
    imagen_url: Optional[str] = None
    piso: Optional[int] = None
    caracteristicas: Optional[dict] = None


class HabitacionResponse(HabitacionBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    tipo_nombre: Optional[str] = None
    politica_nombre: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def set_tipo_nombre(cls, data):
        if isinstance(data, dict):
            return data
        if hasattr(data, 'tipo_habitacion') and data.tipo_habitacion:
            if not hasattr(data, 'tipo_nombre') or data.tipo_nombre is None:
                data.tipo_nombre = data.tipo_habitacion.nombre
        if hasattr(data, 'politica_cancelacion') and data.politica_cancelacion:
            if not hasattr(data, 'politica_nombre') or data.politica_nombre is None:
                data.politica_nombre = data.politica_cancelacion.nombre
        return data


class TipoHabitacionBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    capacidad_maxima: int
    precio_base: Decimal
    activo: bool = True


class TipoHabitacionCreate(TipoHabitacionBase):
    pass


class TipoHabitacionUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    capacidad_maxima: Optional[int] = None
    precio_base: Optional[Decimal] = None
    activo: Optional[bool] = None


class TipoHabitacionResponse(TipoHabitacionBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
