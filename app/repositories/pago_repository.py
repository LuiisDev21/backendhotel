from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.pago import Pago


class PagoRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(self, IdPago: int) -> Optional[Pago]:
        return self.SesionBD.query(Pago).filter(Pago.id == IdPago).first()

    def ObtenerPorReserva(self, IdReserva: int) -> Optional[Pago]:
        return self.SesionBD.query(Pago).filter(Pago.reserva_id == IdReserva).first()

    def ObtenerPorNumeroTransaccion(self, NumeroTransaccion: str) -> Optional[Pago]:
        return self.SesionBD.query(Pago).filter(Pago.numero_transaccion == NumeroTransaccion).first()

    def ObtenerTodos(self, Saltar: int = 0, Limite: int = 100) -> List[Pago]:
        return self.SesionBD.query(Pago).offset(Saltar).limit(Limite).all()

    def Crear(self, PagoNuevo: Pago) -> Pago:
        self.SesionBD.add(PagoNuevo)
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoNuevo)
        return PagoNuevo

    def Actualizar(self, PagoActualizado: Pago) -> Pago:
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoActualizado)
        return PagoActualizado
