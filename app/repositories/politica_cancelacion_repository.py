"""
Repositorio de Política de cancelación.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.politica_cancelacion import PoliticaCancelacion


class PoliticaCancelacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def Listar(
        self,
        ActivasOnly: bool = True,
        Saltar: int = 0,
        Limite: int = 100
    ) -> List[PoliticaCancelacion]:
        q = self.SesionBD.query(PoliticaCancelacion).order_by(PoliticaCancelacion.nombre)
        if ActivasOnly:
            q = q.filter(PoliticaCancelacion.activa == True)
        return q.offset(Saltar).limit(Limite).all()

    def ObtenerPorId(self, Id: int) -> Optional[PoliticaCancelacion]:
        return self.SesionBD.query(PoliticaCancelacion).filter(PoliticaCancelacion.id == Id).first()
