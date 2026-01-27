from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from typing import Optional, List
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva
from app.repositories.habitacion_repository import HabitacionRepository
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate


class HabitacionService:
    def __init__(self, SesionBD: Session):
        self.Repositorio = HabitacionRepository(SesionBD)
        self.SesionBD = SesionBD

    def CrearHabitacion(self, DatosHabitacion: HabitacionCreate) -> Habitacion:
        if self.Repositorio.ObtenerPorNumero(DatosHabitacion.numero):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una habitación con ese número"
            )
        
        HabitacionNueva = Habitacion(**DatosHabitacion.model_dump())
        return self.Repositorio.Crear(HabitacionNueva)

    def ObtenerHabitacion(self, IdHabitacion: int) -> Habitacion:
        HabitacionEncontrada = self.Repositorio.ObtenerPorId(IdHabitacion)
        if not HabitacionEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )
        return HabitacionEncontrada

    def ListarHabitaciones(self, Saltar: int = 0, Limite: int = 100) -> List[Habitacion]:
        return self.Repositorio.ObtenerTodas(Saltar=Saltar, Limite=Limite)

    def BuscarDisponibles(
        self,
        FechaEntrada: date,
        FechaSalida: date,
        Capacidad: Optional[int] = None,
        Tipo: Optional[str] = None
    ) -> List[Habitacion]:
        if FechaEntrada >= FechaSalida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de entrada debe ser anterior a la fecha de salida"
            )
        
        return self.Repositorio.BuscarDisponibles(
            FechaEntrada=FechaEntrada,
            FechaSalida=FechaSalida,
            Capacidad=Capacidad,
            Tipo=Tipo
        )

    def ActualizarHabitacion(
        self,
        IdHabitacion: int,
        DatosHabitacion: HabitacionUpdate
    ) -> Habitacion:
        HabitacionEncontrada = self.ObtenerHabitacion(IdHabitacion)
        DatosActualizacion = DatosHabitacion.model_dump(exclude_unset=True)
        
        for Campo, Valor in DatosActualizacion.items():
            setattr(HabitacionEncontrada, Campo, Valor)
        
        return self.Repositorio.Actualizar(HabitacionEncontrada)

    def EliminarHabitacion(self, IdHabitacion: int):
        HabitacionEncontrada = self.ObtenerHabitacion(IdHabitacion)
        
        # Verificar si hay reservas asociadas
        ReservasAsociadas = self.SesionBD.query(Reserva).filter(
            Reserva.habitacion_id == IdHabitacion
        ).count()
        
        if ReservasAsociadas > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar la habitación porque tiene {ReservasAsociadas} reserva(s) asociada(s). Por favor, cancela o elimina las reservas primero."
            )
        
        self.Repositorio.Eliminar(HabitacionEncontrada)