"""
Repositorio de Habitacion, se define el repositorio de la habitacion con SQLAlchemy.
- ObtenerPorId: Obtiene una habitacion por su ID.
- ObtenerPorNumero: Obtiene una habitacion por su numero.
- ObtenerTodas: Obtiene todas las habitaciones.
- Crear: Crea una nueva habitacion usando procedimiento almacenado.
- Actualizar: Actualiza una habitacion existente.
- Eliminar: Elimina una habitacion existente.
- BuscarDisponibles: Busca las habitaciones disponibles usando procedimiento almacenado.
"""

from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date
from decimal import Decimal
from app.models.habitacion import Habitacion
from app.repositories.stored_procedures import StoredProcedures


class HabitacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD
        self.StoredProcedures = StoredProcedures(SesionBD)

    def ObtenerPorId(self, IdHabitacion: int) -> Optional[Habitacion]:
        return (
            self.SesionBD.query(Habitacion)
            .options(joinedload(Habitacion.tipo_habitacion))
            .filter(Habitacion.id == IdHabitacion)
            .first()
        )

    def ObtenerPorNumero(self, Numero: str) -> Optional[Habitacion]:
        return (
            self.SesionBD.query(Habitacion)
            .options(joinedload(Habitacion.tipo_habitacion))
            .filter(Habitacion.numero == Numero)
            .first()
        )

    def ObtenerTodas(self, Saltar: int = 0, Limite: int = 100) -> List[Habitacion]:
        return (
            self.SesionBD.query(Habitacion)
            .options(joinedload(Habitacion.tipo_habitacion))
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def Crear(
        self, 
        HabitacionNueva: Habitacion,
        UsuarioId: Optional[int] = None
    ) -> Habitacion:
        """Crea una habitación usando el procedimiento almacenado."""
        try:
            resultado = self.StoredProcedures.CrearHabitacion(
                Numero=HabitacionNueva.numero,
                TipoHabitacionId=HabitacionNueva.tipo_habitacion_id,
                Descripcion=HabitacionNueva.descripcion,
                Capacidad=HabitacionNueva.capacidad,
                PrecioPorNoche=HabitacionNueva.precio_por_noche,
                Disponible=HabitacionNueva.disponible,
                ImagenUrl=HabitacionNueva.imagen_url,
                UsuarioId=UsuarioId
            )
            
            # Obtener la habitación creada
            return self.ObtenerPorId(resultado['id'])
        except Exception as e:
            self.SesionBD.rollback()
            raise

    def Actualizar(self, HabitacionActualizada: Habitacion) -> Habitacion:
        self.SesionBD.commit()
        self.SesionBD.refresh(HabitacionActualizada)
        return HabitacionActualizada

    def Eliminar(self, HabitacionAEliminar: Habitacion):
        self.SesionBD.delete(HabitacionAEliminar)
        self.SesionBD.commit()

    def BuscarDisponibles(
        self, 
        FechaEntrada: date, 
        FechaSalida: date, 
        Capacidad: Optional[int] = None,
        TipoHabitacionId: Optional[int] = None
    ) -> List[Habitacion]:
        """Busca habitaciones disponibles usando el procedimiento almacenado."""
        try:
            resultados = self.StoredProcedures.BuscarHabitacionesDisponibles(
                FechaEntrada=FechaEntrada,
                FechaSalida=FechaSalida,
                Capacidad=Capacidad,
                TipoHabitacionId=TipoHabitacionId
            )
            
            # Convertir resultados a objetos Habitacion
            ids = [r['id'] for r in resultados]
            if not ids:
                return []
            
            return (
                self.SesionBD.query(Habitacion)
                .options(joinedload(Habitacion.tipo_habitacion))
                .filter(Habitacion.id.in_(ids))
                .all()
            )
        except Exception as e:
            raise
