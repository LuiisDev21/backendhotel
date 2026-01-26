from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate, HabitacionResponse
from app.services.habitacion_service import HabitacionService
from app.models.usuario import Usuario

router = APIRouter(prefix="/habitaciones", tags=["Habitaciones"])


@router.post("", response_model=HabitacionResponse, dependencies=[Depends(get_current_admin)])
def crear_habitacion(habitacion_data: HabitacionCreate, db: Session = Depends(get_db)):
    service = HabitacionService(db)
    return service.crear_habitacion(habitacion_data)


@router.get("", response_model=List[HabitacionResponse])
def listar_habitaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = HabitacionService(db)
    return service.listar_habitaciones(skip=skip, limit=limit)


@router.get("/buscar", response_model=List[HabitacionResponse])
def buscar_habitaciones_disponibles(
    fecha_entrada: date = Query(...),
    fecha_salida: date = Query(...),
    capacidad: Optional[int] = Query(None, ge=1),
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = HabitacionService(db)
    return service.buscar_disponibles(
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        capacidad=capacidad,
        tipo=tipo
    )


@router.get("/{habitacion_id}", response_model=HabitacionResponse)
def obtener_habitacion(habitacion_id: int, db: Session = Depends(get_db)):
    service = HabitacionService(db)
    return service.obtener_habitacion(habitacion_id)


@router.put("/{habitacion_id}", response_model=HabitacionResponse, dependencies=[Depends(get_current_admin)])
def actualizar_habitacion(
    habitacion_id: int,
    habitacion_data: HabitacionUpdate,
    db: Session = Depends(get_db)
):
    service = HabitacionService(db)
    return service.actualizar_habitacion(habitacion_id, habitacion_data)


@router.delete("/{habitacion_id}", dependencies=[Depends(get_current_admin)])
def eliminar_habitacion(habitacion_id: int, db: Session = Depends(get_db)):
    service = HabitacionService(db)
    service.eliminar_habitacion(habitacion_id)
    return {"message": "Habitación eliminada correctamente"}
