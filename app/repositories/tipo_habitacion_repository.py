"""
Repositorio de TipoHabitacion, se define el repositorio de tipo de habitación con SQLAlchemy.
- ObtenerPorId: Obtiene un tipo de habitación por su ID.
- ObtenerPorCodigo: Obtiene un tipo de habitación por su código.
- ObtenerTodos: Obtiene todos los tipos de habitación activos.
- Crear: Crea un nuevo tipo de habitación.
- Actualizar: Actualiza un tipo de habitación existente.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.tipo_habitacion import TipoHabitacion


class TipoHabitacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(self, IdTipoHabitacion: int) -> Optional[TipoHabitacion]:
        return self.SesionBD.query(TipoHabitacion).filter(TipoHabitacion.id == IdTipoHabitacion).first()

    def ObtenerPorCodigo(self, Codigo: str) -> Optional[TipoHabitacion]:
        return self.SesionBD.query(TipoHabitacion).filter(TipoHabitacion.codigo == Codigo).first()

    def ObtenerTodos(self, SoloActivos: bool = True, Saltar: int = 0, Limite: int = 100) -> List[TipoHabitacion]:
        query = self.SesionBD.query(TipoHabitacion)
        if SoloActivos:
            query = query.filter(TipoHabitacion.activo == True)
        return query.offset(Saltar).limit(Limite).all()

    def Crear(self, TipoHabitacionNuevo: TipoHabitacion) -> TipoHabitacion:
        self.SesionBD.add(TipoHabitacionNuevo)
        self.SesionBD.commit()
        self.SesionBD.refresh(TipoHabitacionNuevo)
        return TipoHabitacionNuevo

    def Actualizar(self, TipoHabitacionActualizado: TipoHabitacion) -> TipoHabitacion:
        self.SesionBD.commit()
        self.SesionBD.refresh(TipoHabitacionActualizado)
        return TipoHabitacionActualizado
