from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, timedelta
from decimal import Decimal
from typing import List
from app.models.reserva import Reserva, EstadoReserva
from app.models.habitacion import Habitacion
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.habitacion_repository import HabitacionRepository
from app.schemas.reserva import ReservaCreate, ReservaUpdate


class ReservaService:
    def __init__(self, db: Session):
        self.repository = ReservaRepository(db)
        self.habitacion_repo = HabitacionRepository(db)
        self.db = db

    def calcular_precio_total(
        self,
        habitacion: Habitacion,
        fecha_entrada: date,
        fecha_salida: date
    ) -> Decimal:
        num_noches = (fecha_salida - fecha_entrada).days
        if num_noches <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de salida debe ser posterior a la fecha de entrada"
            )
        return Decimal(str(habitacion.precio_por_noche)) * Decimal(str(num_noches))

    def crear_reserva(
        self,
        usuario_id: int,
        reserva_data: ReservaCreate
    ) -> Reserva:
        habitacion = self.habitacion_repo.get_by_id(reserva_data.habitacion_id)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )
        
        if not habitacion.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La habitación no está disponible"
            )
        
        if reserva_data.numero_huespedes > habitacion.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La habitación solo puede alojar {habitacion.capacidad} huéspedes"
            )
        
        disponibles = self.habitacion_repo.buscar_disponibles(
            reserva_data.fecha_entrada,
            reserva_data.fecha_salida
        )
        
        if habitacion not in disponibles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La habitación no está disponible en las fechas seleccionadas"
            )
        
        precio_total = self.calcular_precio_total(
            habitacion,
            reserva_data.fecha_entrada,
            reserva_data.fecha_salida
        )
        
        nueva_reserva = Reserva(
            usuario_id=usuario_id,
            habitacion_id=reserva_data.habitacion_id,
            fecha_entrada=reserva_data.fecha_entrada,
            fecha_salida=reserva_data.fecha_salida,
            numero_huespedes=reserva_data.numero_huespedes,
            precio_total=precio_total,
            notas=reserva_data.notas,
            estado=EstadoReserva.PENDIENTE
        )
        
        return self.repository.create(nueva_reserva)

    def obtener_reserva(self, reserva_id: int) -> Reserva:
        reserva = self.repository.get_by_id(reserva_id)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        return reserva

    def listar_reservas_usuario(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reserva]:
        return self.repository.get_by_usuario(usuario_id, skip=skip, limit=limit)

    def listar_todas_reservas(self, skip: int = 0, limit: int = 100) -> List[Reserva]:
        return self.repository.get_all(skip=skip, limit=limit)

    def actualizar_reserva(
        self,
        reserva_id: int,
        reserva_data: ReservaUpdate
    ) -> Reserva:
        reserva = self.obtener_reserva(reserva_id)
        update_data = reserva_data.model_dump(exclude_unset=True)
        
        if "fecha_entrada" in update_data or "fecha_salida" in update_data:
            fecha_entrada = update_data.get("fecha_entrada", reserva.fecha_entrada)
            fecha_salida = update_data.get("fecha_salida", reserva.fecha_salida)
            
            habitacion = self.habitacion_repo.get_by_id(reserva.habitacion_id)
            disponibles = self.habitacion_repo.buscar_disponibles(fecha_entrada, fecha_salida)
            
            if habitacion not in disponibles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La habitación no está disponible en las nuevas fechas"
                )
            
            reserva.precio_total = self.calcular_precio_total(habitacion, fecha_entrada, fecha_salida)
        
        for field, value in update_data.items():
            setattr(reserva, field, value)
        
        return self.repository.update(reserva)

    def cancelar_reserva(self, reserva_id: int) -> Reserva:
        reserva = self.obtener_reserva(reserva_id)
        if reserva.estado == EstadoReserva.CANCELADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reserva ya está cancelada"
            )
        reserva.estado = EstadoReserva.CANCELADA
        return self.repository.update(reserva)
