""" 
Repositorio de Reserva, se define el repositorio de la reserva con SQLAlchemy.
- ObtenerPorId: Obtiene una reserva por su ID.
- ObtenerPorUsuario: Obtiene todas las reservas de un usuario.
- ObtenerTodas: Obtiene todas las reservas.
- Crear: Crea una nueva reserva usando procedimiento almacenado.
- Actualizar: Actualiza una reserva existente.
- Eliminar: Elimina una reserva existente.
"""
import logging
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date
from app.models.reserva import Reserva
from app.models.historial_estado_reserva import HistorialEstadoReserva
from app.repositories.stored_procedures import StoredProcedures

logger = logging.getLogger(__name__)


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
        UsuarioAuditoriaId: Optional[int] = None,
        CanalReserva: str = "web"
    ) -> Reserva:
        """Crea una reserva usando el procedimiento almacenado (sp_crear_reserva)."""
        try:
            canal = getattr(ReservaNueva, "canal_reserva", None) or CanalReserva
            resultado = self.StoredProcedures.CrearReserva(
                UsuarioId=ReservaNueva.usuario_id,
                HabitacionId=ReservaNueva.habitacion_id,
                FechaEntrada=ReservaNueva.fecha_entrada,
                FechaSalida=ReservaNueva.fecha_salida,
                NumeroHuespedes=ReservaNueva.numero_huespedes,
                Notas=ReservaNueva.notas,
                UsuarioAuditoriaId=UsuarioAuditoriaId,
                CanalReserva=canal,
                PoliticaCancelacionId=getattr(ReservaNueva, "politica_cancelacion_id", None)
            )
            id_reserva = int(resultado["id"])
            return self.ObtenerPorId(id_reserva)
        except Exception as e:
            self.SesionBD.rollback()
            logger.exception("Error en Crear reserva (SP): %s", e)
            raise

    def ObtenerHistorialEstados(self, IdReserva: int) -> List[HistorialEstadoReserva]:
        return (
            self.SesionBD.query(HistorialEstadoReserva)
            .filter(HistorialEstadoReserva.reserva_id == IdReserva)
            .order_by(HistorialEstadoReserva.fecha_cambio.desc())
            .all()
        )

    def Actualizar(self, ReservaActualizada: Reserva) -> Reserva:
        self.SesionBD.commit()
        self.SesionBD.refresh(ReservaActualizada)
        return ReservaActualizada

    def Eliminar(self, ReservaAEliminar: Reserva):
        self.SesionBD.delete(ReservaAEliminar)
        self.SesionBD.commit()
