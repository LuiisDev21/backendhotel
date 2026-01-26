from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuarioActual, ObtenerAdministradorActual
from app.schemas.pago import PagoCreate, PagoUpdate, PagoResponse
from app.services.pago_service import PagoService
from app.models.usuario import Usuario

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("", response_model=PagoResponse, status_code=201)
def CrearPago(
    DatosPago: PagoCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = PagoService(SesionBD)
    PagoCreado = Servicio.CrearPago(DatosPago)
    
    from app.repositories.reserva_repository import ReservaRepository
    RepositorioReserva = ReservaRepository(SesionBD)
    ReservaEncontrada = RepositorioReserva.ObtenerPorId(DatosPago.reserva_id)
    
    if not UsuarioActual.es_administrador and ReservaEncontrada.usuario_id != UsuarioActual.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para crear un pago para esta reserva"
        )
    
    return PagoCreado


@router.get("", response_model=List[PagoResponse], dependencies=[Depends(ObtenerAdministradorActual)])
def ListarPagos(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = PagoService(SesionBD)
    return Servicio.ListarPagos(Saltar=Saltar, Limite=Limite)


@router.get("/reserva/{reserva_id}", response_model=PagoResponse)
def ObtenerPagoPorReserva(
    reserva_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuarioActual),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = PagoService(SesionBD)
    PagoEncontrado = Servicio.ObtenerPagoPorReserva(reserva_id)
    
    from app.repositories.reserva_repository import ReservaRepository
    RepositorioReserva = ReservaRepository(SesionBD)
    ReservaEncontrada = RepositorioReserva.ObtenerPorId(reserva_id)
    
    if not UsuarioActual.es_administrador and ReservaEncontrada.usuario_id != UsuarioActual.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver este pago"
        )
    
    return PagoEncontrado


@router.get("/{pago_id}", response_model=PagoResponse, dependencies=[Depends(ObtenerAdministradorActual)])
def ObtenerPago(pago_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = PagoService(SesionBD)
    return Servicio.ObtenerPago(pago_id)


@router.post("/{pago_id}/procesar", response_model=PagoResponse, dependencies=[Depends(ObtenerAdministradorActual)])
def ProcesarPago(pago_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = PagoService(SesionBD)
    return Servicio.ProcesarPago(pago_id)


@router.put("/{pago_id}", response_model=PagoResponse, dependencies=[Depends(ObtenerAdministradorActual)])
def ActualizarPago(
    pago_id: int,
    DatosPago: PagoUpdate,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = PagoService(SesionBD)
    return Servicio.ActualizarPago(pago_id, DatosPago)


@router.post("/{pago_id}/reembolsar", response_model=PagoResponse, dependencies=[Depends(ObtenerAdministradorActual)])
def ReembolsarPago(pago_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = PagoService(SesionBD)
    return Servicio.ReembolsarPago(pago_id)
