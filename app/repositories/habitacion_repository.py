"""
Repositorio de Habitacion, se define el repositorio de la habitacion con SQLAlchemy.
- ObtenerPorId: Obtiene una habitacion por su ID.
- ObtenerPorNumero: Obtiene una habitacion por su numero.
- ObtenerTodas: Obtiene todas las habitaciones.
- Crear: Crea una nueva habitacion.
- Actualizar: Actualiza una habitacion existente.
- Eliminar: Elimina una habitacion existente.
- BuscarDisponibles: Busca las habitaciones disponibles para una fecha de entrada y salida.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import date
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva, EstadoReserva


class HabitacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(self, IdHabitacion: int) -> Optional[Habitacion]:
        return self.SesionBD.query(Habitacion).filter(Habitacion.id == IdHabitacion).first()

    def ObtenerPorNumero(self, Numero: str) -> Optional[Habitacion]:
        return self.SesionBD.query(Habitacion).filter(Habitacion.numero == Numero).first()

    def ObtenerTodas(self, Saltar: int = 0, Limite: int = 100) -> List[Habitacion]:
        return self.SesionBD.query(Habitacion).offset(Saltar).limit(Limite).all()

    def Crear(self, HabitacionNueva: Habitacion) -> Habitacion:
        self.SesionBD.add(HabitacionNueva)
        self.SesionBD.commit()
        self.SesionBD.refresh(HabitacionNueva)
        return HabitacionNueva

    def Actualizar(self, HabitacionActualizada: Habitacion) -> Habitacion:
        self.SesionBD.commit()
        self.SesionBD.refresh(HabitacionActualizada)
        return HabitacionActualizada

    def Eliminar(self, HabitacionAEliminar: Habitacion):
        self.SesionBD.delete(HabitacionAEliminar)
        self.SesionBD.commit()

    def BuscarDisponibles(
        self, 
        FechaEntrada: date, 
        FechaSalida: date, 
        Capacidad: Optional[int] = None,
        Tipo: Optional[str] = None
    ) -> List[Habitacion]:
        from sqlalchemy import cast, String
        ValorEstadoCancelada = EstadoReserva.CANCELADA.value
        HabitacionesOcupadas = self.SesionBD.query(Reserva.habitacion_id).filter(
            and_(
                cast(Reserva.estado, String) != ValorEstadoCancelada,
                or_(
                    and_(Reserva.fecha_entrada <= FechaEntrada, Reserva.fecha_salida > FechaEntrada),
                    and_(Reserva.fecha_entrada < FechaSalida, Reserva.fecha_salida >= FechaSalida),
                    and_(Reserva.fecha_entrada >= FechaEntrada, Reserva.fecha_salida <= FechaSalida)
                )
            )
        ).distinct()
        
        IdsHabitacionesOcupadas = [Fila[0] for Fila in HabitacionesOcupadas]

        Consulta = self.SesionBD.query(Habitacion).filter(
            Habitacion.disponible == True
        )
        
        if IdsHabitacionesOcupadas:
            Consulta = Consulta.filter(~Habitacion.id.in_(IdsHabitacionesOcupadas))

        if Capacidad:
            Consulta = Consulta.filter(Habitacion.capacidad >= Capacidad)
        
        if Tipo:
            Consulta = Consulta.filter(Habitacion.tipo == Tipo)

        return Consulta.all()
