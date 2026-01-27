from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.reserva import Reserva


class ReservaRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(self, IdReserva: int) -> Optional[Reserva]:
        return self.SesionBD.query(Reserva).options(
            joinedload(Reserva.habitacion),
            joinedload(Reserva.usuario)
        ).filter(Reserva.id == IdReserva).first()

    def ObtenerPorUsuario(self, IdUsuario: int, Saltar: int = 0, Limite: int = 100) -> List[Reserva]:
        return self.SesionBD.query(Reserva).options(
            joinedload(Reserva.habitacion),
            joinedload(Reserva.usuario)
        ).filter(
            Reserva.usuario_id == IdUsuario
        ).offset(Saltar).limit(Limite).all()

    def ObtenerTodas(self, Saltar: int = 0, Limite: int = 100) -> List[Reserva]:
        return self.SesionBD.query(Reserva).options(
            joinedload(Reserva.habitacion),
            joinedload(Reserva.usuario)
        ).offset(Saltar).limit(Limite).all()

    def Crear(self, ReservaNueva: Reserva) -> Reserva:
        self.SesionBD.add(ReservaNueva)
        self.SesionBD.commit()
        self.SesionBD.refresh(ReservaNueva)
        return ReservaNueva

    def Actualizar(self, ReservaActualizada: Reserva) -> Reserva:
        self.SesionBD.commit()
        self.SesionBD.refresh(ReservaActualizada)
        return ReservaActualizada

    def Eliminar(self, ReservaAEliminar: Reserva):
        self.SesionBD.delete(ReservaAEliminar)
        self.SesionBD.commit()
