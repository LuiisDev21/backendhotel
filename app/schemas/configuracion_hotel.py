from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfiguracionHotelBase(BaseModel):
    clave: str
    valor: str
    tipo: str = "string"
    descripcion: Optional[str] = None
    modificable: bool = True


class ConfiguracionHotelResponse(ConfiguracionHotelBase):
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


class ConfiguracionHotelUpdate(BaseModel):
    valor: Optional[str] = None
