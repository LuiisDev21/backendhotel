from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.pago import Pago


class PagoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pago_id: int) -> Optional[Pago]:
        return self.db.query(Pago).filter(Pago.id == pago_id).first()

    def get_by_reserva(self, reserva_id: int) -> Optional[Pago]:
        return self.db.query(Pago).filter(Pago.reserva_id == reserva_id).first()

    def get_by_numero_transaccion(self, numero_transaccion: str) -> Optional[Pago]:
        return self.db.query(Pago).filter(Pago.numero_transaccion == numero_transaccion).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pago]:
        return self.db.query(Pago).offset(skip).limit(limit).all()

    def create(self, pago: Pago) -> Pago:
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def update(self, pago: Pago) -> Pago:
        self.db.commit()
        self.db.refresh(pago)
        return pago
