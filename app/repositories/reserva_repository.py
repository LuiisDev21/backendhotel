""" 
Repositorio de Reserva, se define el repositorio de la reserva con SQLAlchemy.
- ObtenerPorId: Obtiene una reserva por su ID.
- ObtenerPorUsuario: Obtiene todas las reservas de un usuario.
- ObtenerTodas: Obtiene todas las reservas.
- Crear: Crea una nueva reserva usando procedimiento almacenado.
- Actualizar: Actualiza una reserva existente.
- Eliminar: Elimina una reserva existente.
"""
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date
from app.models.reserva import Reserva
from app.repositories.stored_procedures import StoredProcedures


class ReservaRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD
        self.StoredProcedures = StoredProcedures(SesionBD)

    def ObtenerPorId(self, IdReserva: int) -> Optional[Reserva]:
        from app.models.habitacion import Habitacion
        from app.models.tipo_habitacion import TipoHabitacion
        return self.SesionBD.query(Reserva).options(
            joinedload(Reserva.habitacion).joinedload(Habitacion.tipo_habitacion),
            joinedload(Reserva.usuario)
        ).filter(Reserva.id == IdReserva).first()

    def ObtenerPorUsuario(self, IdUsuario: int, Saltar: int = 0, Limite: int = 100) -> List[Reserva]:
        from app.models.habitacion import Habitacion
        from app.models.tipo_habitacion import TipoHabitacion
        return self.SesionBD.query(Reserva).options(
            joinedload(Reserva.habitacion).joinedload(Habitacion.tipo_habitacion),
            joinedload(Reserva.usuario)
        ).filter(
            Reserva.usuario_id == IdUsuario
        ).offset(Saltar).limit(Limite).all()

    def ObtenerTodas(self, Saltar: int = 0, Limite: int = 100) -> List[Reserva]:
        from app.models.habitacion import Habitacion
        from app.models.tipo_habitacion import TipoHabitacion
        return self.SesionBD.query(Reserva).options(
            joinedload(Reserva.habitacion).joinedload(Habitacion.tipo_habitacion),
            joinedload(Reserva.usuario)
        ).offset(Saltar).limit(Limite).all()

    def Crear(
        self, 
        ReservaNueva: Reserva,
        UsuarioAuditoriaId: Optional[int] = None
    ) -> Reserva:
        """Crea una reserva usando el procedimiento almacenado."""
        try:
            resultado = self.StoredProcedures.CrearReserva(
                UsuarioId=ReservaNueva.usuario_id,
                HabitacionId=ReservaNueva.habitacion_id,
                FechaEntrada=ReservaNueva.fecha_entrada,
                FechaSalida=ReservaNueva.fecha_salida,
                NumeroHuespedes=ReservaNueva.numero_huespedes,
                Notas=ReservaNueva.notas,
                UsuarioAuditoriaId=UsuarioAuditoriaId
            )
            
            # Obtener la reserva creada
            return self.ObtenerPorId(resultado['id'])
        except Exception as e:
            self.SesionBD.rollback()
            raise

    def Actualizar(self, ReservaActualizada: Reserva) -> Reserva:
        self.SesionBD.commit()
        self.SesionBD.refresh(ReservaActualizada)
        return ReservaActualizada

    def Eliminar(self, ReservaAEliminar: Reserva):
        self.SesionBD.delete(ReservaAEliminar)
        self.SesionBD.commit()
