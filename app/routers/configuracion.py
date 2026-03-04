"""
Router de Configuración del hotel.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuario, TienePermiso
from app.repositories.configuracion_hotel_repository import ConfiguracionHotelRepository
from app.schemas.configuracion_hotel import ConfiguracionHotelResponse
from pydantic import BaseModel
from app.models.usuario import Usuario

router = APIRouter(prefix="/configuracion", tags=["Configuración"])


class ConfiguracionValorUpdate(BaseModel):
    valor: str


@router.get("", response_model=List[ConfiguracionHotelResponse], dependencies=[Depends(TienePermiso("configuracion.modificar"))])
def ListarConfiguracion(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(500, ge=1, le=500),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Lista todas las claves de configuración del hotel. Requiere permiso configuracion.modificar."""
    repo = ConfiguracionHotelRepository(SesionBD)
    return repo.ListarTodos(Saltar=Saltar, Limite=Limite)


@router.patch("/{clave}", response_model=ConfiguracionHotelResponse, dependencies=[Depends(TienePermiso("configuracion.modificar"))])
def ActualizarConfiguracionClave(
    clave: str,
    body: ConfiguracionValorUpdate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Actualiza el valor de una clave de configuración. Solo claves modificables. Requiere permiso configuracion.modificar."""
    repo = ConfiguracionHotelRepository(SesionBD)
    actualizado = repo.ActualizarValor(Clave=clave, Valor=body.valor, UsuarioId=UsuarioActual.id)
    if not actualizado:
        config = repo.ObtenerPorClave(clave)
        if not config:
            raise HTTPException(status_code=404, detail="Clave de configuración no encontrada")
        raise HTTPException(status_code=400, detail="La clave no es modificable")
    return actualizado
