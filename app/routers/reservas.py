from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuarioActual, ObtenerAdministradorActual
from app.schemas.reserva import ReservaCreate, ReservaUpdate, ReservaResponse
from app.services.reserva_service import ReservaService
from app.models.usuario import Usuario

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaResponse, status_code=201)
def CrearReserva(
    DatosReserva: ReservaCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ReservaService(SesionBD)
    return Servicio.CrearReserva(UsuarioActual.id, DatosReserva)


@router.get("", response_model=List[ReservaResponse])
def ListarMisReservas(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ReservaService(SesionBD)
    return Servicio.ListarReservasUsuario(UsuarioActual.id, Saltar=Saltar, Limite=Limite)


@router.get("/todas", response_model=List[ReservaResponse], dependencies=[Depends(ObtenerAdministradorActual)])
def ListarTodasReservas(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ReservaService(SesionBD)
    return Servicio.ListarTodasReservas(Saltar=Saltar, Limite=Limite)


@router.get("/{reserva_id}", response_model=ReservaResponse)
def ObtenerReserva(
    reserva_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ReservaService(SesionBD)
    ReservaEncontrada = Servicio.ObtenerReserva(reserva_id)
    
    if not UsuarioActual.es_administrador and ReservaEncontrada.usuario_id != UsuarioActual.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver esta reserva"
        )
    
    return ReservaEncontrada


@router.put("/{reserva_id}", response_model=ReservaResponse)
def ActualizarReserva(
    reserva_id: int,
    DatosReserva: ReservaUpdate,
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ReservaService(SesionBD)
    ReservaEncontrada = Servicio.ObtenerReserva(reserva_id)
    
    if not UsuarioActual.es_administrador and ReservaEncontrada.usuario_id != UsuarioActual.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para modificar esta reserva"
        )
    
    return Servicio.ActualizarReserva(reserva_id, DatosReserva)


@router.post("/{reserva_id}/cancelar", response_model=ReservaResponse)
def CancelarReserva(
    reserva_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ReservaService(SesionBD)
    ReservaEncontrada = Servicio.ObtenerReserva(reserva_id)
    
    if not UsuarioActual.es_administrador and ReservaEncontrada.usuario_id != UsuarioActual.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para cancelar esta reserva"
        )
    
    return Servicio.CancelarReserva(reserva_id)
