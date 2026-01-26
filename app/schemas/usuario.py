from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str
    telefono: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioResponse(UsuarioBase):
    id: int
    es_administrador: bool
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
