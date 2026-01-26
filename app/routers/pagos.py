from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.pago import PagoCreate, PagoUpdate, PagoResponse
from app.services.pago_service import PagoService
from app.models.usuario import Usuario

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("", response_model=PagoResponse, status_code=201)
def crear_pago(
    pago_data: PagoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PagoService(db)
    pago = service.crear_pago(pago_data)
    
    from app.repositories.reserva_repository import ReservaRepository
    reserva_repo = ReservaRepository(db)
    reserva = reserva_repo.get_by_id(pago_data.reserva_id)
    
    if not current_user.es_administrador and reserva.usuario_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para crear un pago para esta reserva"
        )
    
    return pago


@router.get("", response_model=List[PagoResponse], dependencies=[Depends(get_current_admin)])
def listar_pagos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = PagoService(db)
    return service.listar_pagos(skip=skip, limit=limit)


@router.get("/reserva/{reserva_id}", response_model=PagoResponse)
def obtener_pago_por_reserva(
    reserva_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PagoService(db)
    pago = service.obtener_pago_por_reserva(reserva_id)
    
    from app.repositories.reserva_repository import ReservaRepository
    reserva_repo = ReservaRepository(db)
    reserva = reserva_repo.get_by_id(reserva_id)
    
    if not current_user.es_administrador and reserva.usuario_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver este pago"
        )
    
    return pago


@router.get("/{pago_id}", response_model=PagoResponse, dependencies=[Depends(get_current_admin)])
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    service = PagoService(db)
    return service.obtener_pago(pago_id)


@router.post("/{pago_id}/procesar", response_model=PagoResponse, dependencies=[Depends(get_current_admin)])
def procesar_pago(pago_id: int, db: Session = Depends(get_db)):
    service = PagoService(db)
    return service.procesar_pago(pago_id)


@router.put("/{pago_id}", response_model=PagoResponse, dependencies=[Depends(get_current_admin)])
def actualizar_pago(
    pago_id: int,
    pago_data: PagoUpdate,
    db: Session = Depends(get_db)
):
    service = PagoService(db)
    return service.actualizar_pago(pago_id, pago_data)


@router.post("/{pago_id}/reembolsar", response_model=PagoResponse, dependencies=[Depends(get_current_admin)])
def reembolsar_pago(pago_id: int, db: Session = Depends(get_db)):
    service = PagoService(db)
    return service.reembolsar_pago(pago_id)
