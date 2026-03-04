"""
Repositorio de Auditoria, se define el repositorio de auditoría con SQLAlchemy.
- Crear: Registra una acción de auditoría.
- ObtenerPorId: Obtiene un registro de auditoría por su ID.
- ObtenerPorTabla: Obtiene registros de auditoría por tabla.
- ObtenerPorUsuario: Obtiene registros de auditoría por usuario.
- ObtenerPorAccion: Obtiene registros de auditoría por acción.
- ObtenerTodos: Obtiene todos los registros de auditoría con paginación.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from datetime import datetime
import json
from app.models.auditoria import Auditoria, AccionAuditoria


class AuditoriaRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def Crear(
        self,
        TablaAfectada: str,
        Accion: AccionAuditoria,
        RegistroId: Optional[int] = None,
        UsuarioId: Optional[int] = None,
        DatosAnteriores: Optional[dict] = None,
        DatosNuevos: Optional[dict] = None,
        IpAddress: Optional[str] = None,
        UserAgent: Optional[str] = None,
        Observaciones: Optional[str] = None
    ) -> Auditoria:
        """Registra una acción de auditoría usando inserción directa (más confiable)."""
        try:
            # SQLAlchemy maneja JSONB directamente desde diccionarios Python
            # No necesitamos convertir a string JSON
            
            # Crear registro de auditoría directamente usando SQLAlchemy
            RegistroAuditoria = Auditoria(
                tabla_afectada=TablaAfectada,
                registro_id=RegistroId,
                accion=Accion,
                usuario_id=UsuarioId,
                datos_anteriores=DatosAnteriores,  # SQLAlchemy convierte automáticamente
                datos_nuevos=DatosNuevos,  # SQLAlchemy convierte automáticamente
                ip_address=IpAddress,
                user_agent=UserAgent,
                observaciones=Observaciones
            )
            
            self.SesionBD.add(RegistroAuditoria)
            self.SesionBD.commit()
            self.SesionBD.refresh(RegistroAuditoria)
            
            return RegistroAuditoria
        except Exception as e:
            self.SesionBD.rollback()
            # Log del error para debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear registro de auditoría: {str(e)}", exc_info=True)
            raise

    def ObtenerPorId(self, IdAuditoria: int) -> Optional[Auditoria]:
        return self.SesionBD.query(Auditoria).filter(Auditoria.id == IdAuditoria).first()

    def ObtenerPorTabla(
        self, 
        TablaAfectada: str, 
        Saltar: int = 0, 
        Limite: int = 100
    ) -> List[Auditoria]:
        return (
            self.SesionBD.query(Auditoria)
            .filter(Auditoria.tabla_afectada == TablaAfectada)
            .order_by(Auditoria.fecha_accion.desc())
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ObtenerPorUsuario(
        self, 
        UsuarioId: int, 
        Saltar: int = 0, 
        Limite: int = 100
    ) -> List[Auditoria]:
        return (
            self.SesionBD.query(Auditoria)
            .filter(Auditoria.usuario_id == UsuarioId)
            .order_by(Auditoria.fecha_accion.desc())
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ObtenerPorAccion(
        self, 
        Accion: AccionAuditoria, 
        Saltar: int = 0, 
        Limite: int = 100
    ) -> List[Auditoria]:
        return (
            self.SesionBD.query(Auditoria)
            .filter(Auditoria.accion == Accion)
            .order_by(Auditoria.fecha_accion.desc())
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ObtenerTodos(
        self, 
        Saltar: int = 0, 
        Limite: int = 100
    ) -> List[Auditoria]:
        return (
            self.SesionBD.query(Auditoria)
            .order_by(Auditoria.fecha_accion.desc())
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ListarConFiltros(
        self,
        FechaDesde: Optional[datetime] = None,
        FechaHasta: Optional[datetime] = None,
        UsuarioId: Optional[int] = None,
        Accion: Optional[str] = None,
        TablaAfectada: Optional[str] = None,
        Saltar: int = 0,
        Limite: int = 100
    ) -> List[Auditoria]:
        """Lista registros de auditoría con filtros opcionales."""
        query = self.SesionBD.query(Auditoria).options(joinedload(Auditoria.usuario))
        if FechaDesde is not None:
            query = query.filter(Auditoria.fecha_accion >= FechaDesde)
        if FechaHasta is not None:
            query = query.filter(Auditoria.fecha_accion <= FechaHasta)
        if UsuarioId is not None:
            query = query.filter(Auditoria.usuario_id == UsuarioId)
        if Accion is not None:
            query = query.filter(Auditoria.accion == Accion)
        if TablaAfectada is not None:
            query = query.filter(Auditoria.tabla_afectada == TablaAfectada)
        return (
            query.order_by(Auditoria.fecha_accion.desc())
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ObtenerMasReciente(
        self, 
        TablaAfectada: str, 
        RegistroId: Optional[int] = None
    ) -> Optional[Auditoria]:
        query = self.SesionBD.query(Auditoria).filter(
            Auditoria.tabla_afectada == TablaAfectada
        )
        if RegistroId:
            query = query.filter(Auditoria.registro_id == RegistroId)
        return query.order_by(Auditoria.fecha_accion.desc()).first()
