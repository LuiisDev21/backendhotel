"""
Repositorio de Configuración del hotel (lectura por clave, listar, actualizar).
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.configuracion_hotel import ConfiguracionHotel


class ConfiguracionHotelRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorClave(self, Clave: str) -> Optional[ConfiguracionHotel]:
        return (
            self.SesionBD.query(ConfiguracionHotel)
            .filter(ConfiguracionHotel.clave == Clave)
            .first()
        )

    def ListarTodos(self, Saltar: int = 0, Limite: int = 500) -> List[ConfiguracionHotel]:
        return (
            self.SesionBD.query(ConfiguracionHotel)
            .order_by(ConfiguracionHotel.clave)
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ActualizarValor(
        self,
        Clave: str,
        Valor: str,
        UsuarioId: Optional[int] = None
    ) -> Optional[ConfiguracionHotel]:
        row = self.ObtenerPorClave(Clave)
        if not row:
            return None
        if not row.modificable:
            return None
        row.valor = Valor
        if UsuarioId is not None:
            row.actualizado_por = UsuarioId
        self.SesionBD.commit()
        self.SesionBD.refresh(row)
        return row

    def ObtenerValorEntero(self, Clave: str, Default: int = 0) -> int:
        row = self.ObtenerPorClave(Clave)
        if row is None:
            return Default
        try:
            return int(row.valor)
        except (ValueError, TypeError):
            return Default
