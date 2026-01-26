from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.reserva import ReservaCreate, ReservaUpdate, ReservaResponse
from app.services.reserva_service import ReservaService
from app.models.usuario import Usuario

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaResponse, status_code=201)
def crear_reserva(
    reserva_data: ReservaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReservaService(db)
    return service.crear_reserva(current_user.id, reserva_data)


@router.get("", response_model=List[ReservaResponse])
def listar_mis_reservas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReservaService(db)
    return service.listar_reservas_usuario(current_user.id, skip=skip, limit=limit)


@router.get("/todas", response_model=List[ReservaResponse], dependencies=[Depends(get_current_admin)])
def listar_todas_reservas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = ReservaService(db)
    return service.listar_todas_reservas(skip=skip, limit=limit)


@router.get("/{reserva_id}", response_model=ReservaResponse)
def obtener_reserva(
    reserva_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReservaService(db)
    reserva = service.obtener_reserva(reserva_id)
    
    if not current_user.es_administrador and reserva.usuario_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver esta reserva"
        )
    
    return reserva


@router.put("/{reserva_id}", response_model=ReservaResponse)
def actualizar_reserva(
    reserva_id: int,
    reserva_data: ReservaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReservaService(db)
    reserva = service.obtener_reserva(reserva_id)
    
    if not current_user.es_administrador and reserva.usuario_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para modificar esta reserva"
        )
    
    return service.actualizar_reserva(reserva_id, reserva_data)


@router.post("/{reserva_id}/cancelar", response_model=ReservaResponse)
def cancelar_reserva(
    reserva_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReservaService(db)
    reserva = service.obtener_reserva(reserva_id)
    
    if not current_user.es_administrador and reserva.usuario_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para cancelar esta reserva"
        )
    
    return service.cancelar_reserva(reserva_id)
