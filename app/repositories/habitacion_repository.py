"""
Repositorio de Habitacion, se define el repositorio de la habitacion con SQLAlchemy.
- ObtenerPorId: Obtiene una habitacion por su ID.
- ObtenerPorNumero: Obtiene una habitacion por su numero.
- ObtenerTodas: Obtiene todas las habitaciones.
- Crear: Crea una nueva habitacion (ORM; fallback si el SP no persiste en la BD).
- Actualizar: Actualiza una habitacion existente.
- Eliminar: Elimina una habitacion existente.
- BuscarDisponibles: Busca las habitaciones disponibles usando procedimiento almacenado.
"""

from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date
from decimal import Decimal
from fastapi import HTTPException
from app.models.habitacion import Habitacion
from app.repositories.stored_procedures import StoredProcedures
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria


class HabitacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD
        self.StoredProcedures = StoredProcedures(SesionBD)

    def ObtenerPorId(self, IdHabitacion: int) -> Optional[Habitacion]:
        return (
            self.SesionBD.query(Habitacion)
            .options(
                joinedload(Habitacion.tipo_habitacion),
                joinedload(Habitacion.politica_cancelacion)
            )
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
            .options(
                joinedload(Habitacion.tipo_habitacion),
                joinedload(Habitacion.politica_cancelacion)
            )
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def Crear(
        self,
        HabitacionNueva: Habitacion,
        UsuarioId: Optional[int] = None
    ) -> Habitacion:
        """Crea una habitación por ORM (el SP en la BD no persiste el INSERT en este entorno)."""
        if self.ObtenerPorNumero(HabitacionNueva.numero):
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una habitación con el número {HabitacionNueva.numero}"
            )
        if HabitacionNueva.capacidad <= 0:
            raise HTTPException(status_code=400, detail="La capacidad debe ser mayor a 0")
        if HabitacionNueva.precio_por_noche <= 0:
            raise HTTPException(status_code=400, detail="El precio por noche debe ser mayor a 0")
        try:
            self.SesionBD.add(HabitacionNueva)
            self.SesionBD.flush()
            registrar_auditoria(
                self.SesionBD,
                "habitaciones",
                AccionAuditoria.CREATE,
                RegistroId=HabitacionNueva.id,
                UsuarioId=UsuarioId,
                DatosNuevos=convertir_modelo_a_dict(HabitacionNueva),
            )
            self.SesionBD.commit()
            self.SesionBD.refresh(HabitacionNueva)
            return self.ObtenerPorId(HabitacionNueva.id)
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
                .options(
                    joinedload(Habitacion.tipo_habitacion),
                    joinedload(Habitacion.politica_cancelacion)
                )
                .filter(Habitacion.id.in_(ids))
                .all()
            )
        except Exception as e:
            raise
