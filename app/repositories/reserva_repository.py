from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.reserva import Reserva


class ReservaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reserva_id: int) -> Optional[Reserva]:
        return self.db.query(Reserva).filter(Reserva.id == reserva_id).first()

    def get_by_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[Reserva]:
        return self.db.query(Reserva).filter(
            Reserva.usuario_id == usuario_id
        ).offset(skip).limit(limit).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Reserva]:
        return self.db.query(Reserva).offset(skip).limit(limit).all()

    def create(self, reserva: Reserva) -> Reserva:
        self.db.add(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        return reserva

    def update(self, reserva: Reserva) -> Reserva:
        self.db.commit()
        self.db.refresh(reserva)
        return reserva

    def delete(self, reserva: Reserva):
        self.db.delete(reserva)
        self.db.commit()
