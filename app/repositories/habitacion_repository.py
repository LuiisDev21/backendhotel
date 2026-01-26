from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import date
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva, EstadoReserva


class HabitacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, habitacion_id: int) -> Optional[Habitacion]:
        return self.db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()

    def get_by_numero(self, numero: str) -> Optional[Habitacion]:
        return self.db.query(Habitacion).filter(Habitacion.numero == numero).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Habitacion]:
        return self.db.query(Habitacion).offset(skip).limit(limit).all()

    def create(self, habitacion: Habitacion) -> Habitacion:
        self.db.add(habitacion)
        self.db.commit()
        self.db.refresh(habitacion)
        return habitacion

    def update(self, habitacion: Habitacion) -> Habitacion:
        self.db.commit()
        self.db.refresh(habitacion)
        return habitacion

    def delete(self, habitacion: Habitacion):
        self.db.delete(habitacion)
        self.db.commit()

    def buscar_disponibles(
        self, 
        fecha_entrada: date, 
        fecha_salida: date, 
        capacidad: Optional[int] = None,
        tipo: Optional[str] = None
    ) -> List[Habitacion]:
        # Habitaciones con reservas en conflicto
        habitaciones_ocupadas = self.db.query(Reserva.habitacion_id).filter(
            and_(
                Reserva.estado != EstadoReserva.CANCELADA,
                or_(
                    and_(Reserva.fecha_entrada <= fecha_entrada, Reserva.fecha_salida > fecha_entrada),
                    and_(Reserva.fecha_entrada < fecha_salida, Reserva.fecha_salida >= fecha_salida),
                    and_(Reserva.fecha_entrada >= fecha_entrada, Reserva.fecha_salida <= fecha_salida)
                )
            )
        ).distinct()

        query = self.db.query(Habitacion).filter(
            Habitacion.disponible == True,
            ~Habitacion.id.in_(habitaciones_ocupadas)
        )

        if capacidad:
            query = query.filter(Habitacion.capacidad >= capacidad)
        
        if tipo:
            query = query.filter(Habitacion.tipo == tipo)

        return query.all()
