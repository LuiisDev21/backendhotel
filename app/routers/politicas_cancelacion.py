"""
Router de Políticas de cancelación.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.repositories.politica_cancelacion_repository import PoliticaCancelacionRepository
from app.schemas.politica_cancelacion import PoliticaCancelacionResponse

router = APIRouter(prefix="/politicas-cancelacion", tags=["Políticas de cancelación"])


@router.get("", response_model=List[PoliticaCancelacionResponse])
def ListarPoliticasCancelacion(
    SoloActivos: bool = Query(True, description="Solo políticas activas"),
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Lista políticas de cancelación (para formularios de reserva y admin)."""
    repo = PoliticaCancelacionRepository(SesionBD)
    return repo.Listar(ActivasOnly=SoloActivos, Saltar=Saltar, Limite=Limite)


@router.get("/{politica_id}", response_model=PoliticaCancelacionResponse)
def ObtenerPoliticaCancelacion(
    politica_id: int,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Obtiene una política de cancelación por ID."""
    repo = PoliticaCancelacionRepository(SesionBD)
    politica = repo.ObtenerPorId(politica_id)
    if not politica:
        raise HTTPException(status_code=404, detail="Política no encontrada")
    return politica
