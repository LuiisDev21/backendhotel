"""
Módulo de ayuda para auditoría.
Proporciona funciones utilitarias para registrar acciones de auditoría de manera consistente.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, date
import uuid
from app.repositories.auditoria_repository import AuditoriaRepository
from app.models.auditoria import AccionAuditoria
from app.models.usuario import Usuario


def _campos_modificados(
    DatosAnteriores: Optional[Dict[str, Any]],
    DatosNuevos: Optional[Dict[str, Any]]
) -> List[str]:
    """Devuelve la lista de claves cuyo valor cambió entre ambos dicts."""
    if not DatosAnteriores and not DatosNuevos:
        return []
    ant = DatosAnteriores or {}
    nuevos = DatosNuevos or {}
    todas_las_claves = set(ant.keys()) | set(nuevos.keys())
    return [k for k in sorted(todas_las_claves) if ant.get(k) != nuevos.get(k)]


def registrar_auditoria(
    SesionBD: Session,
    TablaAfectada: str,
    Accion: AccionAuditoria,
    RegistroId: Optional[int] = None,
    UsuarioId: Optional[int] = None,
    DatosAnteriores: Optional[Dict[str, Any]] = None,
    DatosNuevos: Optional[Dict[str, Any]] = None,
    IpAddress: Optional[str] = None,
    UserAgent: Optional[str] = None,
    Observaciones: Optional[str] = None,
    ResumenCambio: Optional[str] = None,
    CamposModificados: Optional[List[str]] = None
) -> None:
    """
    Registra una acción de auditoría de manera centralizada.

    Si se pasan DatosAnteriores y DatosNuevos y no se pasa CamposModificados,
    se calcula automáticamente la lista de campos que cambiaron.
    """
    try:
        campos = CamposModificados
        if campos is None and DatosAnteriores is not None and DatosNuevos is not None:
            campos = _campos_modificados(DatosAnteriores, DatosNuevos)
        RepositorioAuditoria = AuditoriaRepository(SesionBD)
        RepositorioAuditoria.Crear(
            TablaAfectada=TablaAfectada,
            Accion=Accion,
            RegistroId=RegistroId,
            UsuarioId=UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=DatosNuevos,
            IpAddress=IpAddress,
            UserAgent=UserAgent,
            Observaciones=Observaciones,
            ResumenCambio=ResumenCambio,
            CamposModificados=campos
        )
    except Exception as e:
        # Log del error pero no fallar la operación principal si falla la auditoría
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al registrar auditoría: {str(e)}", exc_info=True)


def convertir_modelo_a_dict(Modelo: Any) -> Dict[str, Any]:
    """
    Convierte un modelo SQLAlchemy a diccionario para auditoría.
    
    Args:
        Modelo: Instancia de modelo SQLAlchemy
        
    Returns:
        Diccionario con los datos del modelo
    """
    if not Modelo:
        return {}
    
    datos = {}
    for columna in Modelo.__table__.columns:
        valor = getattr(Modelo, columna.name, None)
        
        # Convertir tipos especiales a tipos serializables para JSON
        if valor is None:
            datos[columna.name] = None
        elif isinstance(valor, Decimal):
            # Convertir Decimal a float para JSON
            datos[columna.name] = float(valor)
        elif isinstance(valor, (datetime, date)):
            # Convertir datetime/date a string ISO
            datos[columna.name] = valor.isoformat()
        elif hasattr(valor, 'value'):  # Enum
            datos[columna.name] = valor.value
        elif hasattr(valor, 'isoformat'):  # datetime, date (fallback)
            datos[columna.name] = valor.isoformat()
        elif isinstance(valor, uuid.UUID):
            datos[columna.name] = str(valor)
        else:
            datos[columna.name] = valor
    
    return datos
