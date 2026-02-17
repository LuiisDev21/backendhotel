from pydantic import BaseModel, model_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime


class HabitacionBase(BaseModel):
    numero: str
    tipo_habitacion_id: int
    descripcion: Optional[str] = None
    capacidad: int
    precio_por_noche: Decimal
    disponible: bool = True
    imagen_url: Optional[str] = None


class HabitacionCreate(HabitacionBase):
    pass


class HabitacionUpdate(BaseModel):
    tipo_habitacion_id: Optional[int] = None
    descripcion: Optional[str] = None
    capacidad: Optional[int] = None
    precio_por_noche: Optional[Decimal] = None
    disponible: Optional[bool] = None
    imagen_url: Optional[str] = None


class HabitacionResponse(HabitacionBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    tipo_nombre: Optional[str] = None  # Campo computado desde relación

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    @classmethod
    def set_tipo_nombre(cls, data):
        """Pobla tipo_nombre desde la relación tipo_habitacion si está disponible."""
        if isinstance(data, dict):
            return data
        
        # Si es un objeto SQLAlchemy con relación cargada
        if hasattr(data, 'tipo_habitacion') and data.tipo_habitacion:
            if not hasattr(data, 'tipo_nombre') or data.tipo_nombre is None:
                data.tipo_nombre = data.tipo_habitacion.nombre
        
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
