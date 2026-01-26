from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from typing import Optional, List
from app.models.habitacion import Habitacion
from app.repositories.habitacion_repository import HabitacionRepository
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate


class HabitacionService:
    def __init__(self, db: Session):
        self.repository = HabitacionRepository(db)
        self.db = db

    def crear_habitacion(self, habitacion_data: HabitacionCreate) -> Habitacion:
        if self.repository.get_by_numero(habitacion_data.numero):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una habitación con ese número"
            )
        
        nueva_habitacion = Habitacion(**habitacion_data.model_dump())
        return self.repository.create(nueva_habitacion)

    def obtener_habitacion(self, habitacion_id: int) -> Habitacion:
        habitacion = self.repository.get_by_id(habitacion_id)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )
        return habitacion

    def listar_habitaciones(self, skip: int = 0, limit: int = 100) -> List[Habitacion]:
        return self.repository.get_all(skip=skip, limit=limit)

    def buscar_disponibles(
        self,
        fecha_entrada: date,
        fecha_salida: date,
        capacidad: Optional[int] = None,
        tipo: Optional[str] = None
    ) -> List[Habitacion]:
        if fecha_entrada >= fecha_salida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de entrada debe ser anterior a la fecha de salida"
            )
        
        return self.repository.buscar_disponibles(
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            capacidad=capacidad,
            tipo=tipo
        )

    def actualizar_habitacion(
        self,
        habitacion_id: int,
        habitacion_data: HabitacionUpdate
    ) -> Habitacion:
        habitacion = self.obtener_habitacion(habitacion_id)
        update_data = habitacion_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(habitacion, field, value)
        
        return self.repository.update(habitacion)

    def eliminar_habitacion(self, habitacion_id: int):
        habitacion = self.obtener_habitacion(habitacion_id)
        self.repository.delete(habitacion)
