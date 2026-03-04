from pydantic import BaseModel, EmailStr
from typing import Optional, List
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


class RefreshTokenBody(BaseModel):
    refresh_token: str


class AsignarRolesBody(BaseModel):
    """IDs de roles a asignar al usuario (reemplaza los actuales)."""
    rol_ids: List[int]


class UsuarioResponse(UsuarioBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class RolEnUsuarioResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class UsuarioConRolesResponse(UsuarioBase):
    id: int
    activo: bool
    fecha_creacion: datetime
    roles: List[RolEnUsuarioResponse] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
