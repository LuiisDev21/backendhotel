from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import json
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerAdministradorActual, ObtenerUsuarioActual
from app.core.storage import SubirImagenHabitacion
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate, HabitacionResponse
from app.services.habitacion_service import HabitacionService
from app.models.usuario import Usuario

router = APIRouter(prefix="/habitaciones", tags=["Habitaciones"])


@router.post("", response_model=HabitacionResponse, dependencies=[Depends(ObtenerAdministradorActual)])
async def CrearHabitacion(
    numero: str = Form(...),
    tipo: str = Form(...),
    descripcion: Optional[str] = Form(None),
    capacidad: int = Form(...),
    precio_por_noche: float = Form(...),
    disponible: bool = Form(True),
    archivo: Optional[UploadFile] = File(None),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """
    Crea una nueva habitación. Si se proporciona una imagen, se sube automáticamente a Supabase.
    """
    Servicio = HabitacionService(SesionBD)
    
    # Crear objeto HabitacionCreate
    DatosHabitacion = HabitacionCreate(
        numero=numero,
        tipo=tipo,
        descripcion=descripcion,
        capacidad=capacidad,
        precio_por_noche=precio_por_noche,
        disponible=disponible
    )
    
    # Crear la habitación primero
    HabitacionCreada = Servicio.CrearHabitacion(DatosHabitacion)
    
    # Si hay una imagen, subirla
    if archivo and archivo.filename:
        try:
            url_imagen = await SubirImagenHabitacion(archivo, HabitacionCreada.id)
            # Actualizar la habitación con la URL de la imagen
            DatosActualizacion = HabitacionUpdate(imagen_url=url_imagen)
            HabitacionCreada = Servicio.ActualizarHabitacion(HabitacionCreada.id, DatosActualizacion)
        except Exception as e:
            # Si falla la subida de imagen, la habitación ya está creada
            # Podríamos eliminar la habitación o solo registrar el error
            pass
    
    return HabitacionCreada


@router.get("", response_model=List[HabitacionResponse])
def ListarHabitaciones(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = HabitacionService(SesionBD)
    return Servicio.ListarHabitaciones(Saltar=Saltar, Limite=Limite)


@router.get("/buscar", response_model=List[HabitacionResponse])
def BuscarHabitacionesDisponibles(
    FechaEntrada: date = Query(...),
    FechaSalida: date = Query(...),
    Capacidad: Optional[int] = Query(None, ge=1),
    Tipo: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = HabitacionService(SesionBD)
    return Servicio.BuscarDisponibles(
        FechaEntrada=FechaEntrada,
        FechaSalida=FechaSalida,
        Capacidad=Capacidad,
        Tipo=Tipo
    )


@router.get("/{habitacion_id}", response_model=HabitacionResponse)
def ObtenerHabitacion(habitacion_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = HabitacionService(SesionBD)
    return Servicio.ObtenerHabitacion(habitacion_id)


@router.put("/{habitacion_id}", response_model=HabitacionResponse, dependencies=[Depends(ObtenerAdministradorActual)])
async def ActualizarHabitacion(
    habitacion_id: int,
    tipo: str = Form(...),
    descripcion: Optional[str] = Form(None),
    capacidad: int = Form(...),
    precio_por_noche: float = Form(...),
    disponible: str = Form(...),  # Recibir como string
    archivo: Optional[UploadFile] = File(None),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """
    Actualiza una habitación. Si se proporciona una imagen, se sube automáticamente a Supabase.
    """
    Servicio = HabitacionService(SesionBD)
    
    # Convertir disponible de string a boolean
    disponible_bool = disponible.lower() == 'true'
    
    # Crear objeto HabitacionUpdate
    DatosHabitacion = HabitacionUpdate(
        tipo=tipo,
        descripcion=descripcion if descripcion else None,
        capacidad=capacidad,
        precio_por_noche=precio_por_noche,
        disponible=disponible_bool
    )
    
    # Actualizar la habitación
    HabitacionActualizada = Servicio.ActualizarHabitacion(habitacion_id, DatosHabitacion)
    
    # Si hay una imagen, subirla
    if archivo and archivo.filename:
        try:
            url_imagen = await SubirImagenHabitacion(archivo, habitacion_id)
            # Actualizar la habitación con la URL de la imagen
            DatosImagen = HabitacionUpdate(imagen_url=url_imagen)
            HabitacionActualizada = Servicio.ActualizarHabitacion(habitacion_id, DatosImagen)
        except Exception as e:
            # Si falla la subida de imagen, la actualización de otros campos ya está hecha
            pass
    
    return HabitacionActualizada


@router.delete("/{habitacion_id}", dependencies=[Depends(ObtenerAdministradorActual)])
def EliminarHabitacion(habitacion_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = HabitacionService(SesionBD)
    Servicio.EliminarHabitacion(habitacion_id)
    return {"message": "Habitación eliminada correctamente"}


@router.post("/{habitacion_id}/imagen", dependencies=[Depends(ObtenerAdministradorActual)])
async def SubirImagenHabitacionEndpoint(
    habitacion_id: int,
    archivo: UploadFile = File(...),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """
    Sube una imagen para una habitación y actualiza la URL en la base de datos
    """
    Servicio = HabitacionService(SesionBD)
    
    # Verificar que la habitación existe
    HabitacionEncontrada = Servicio.ObtenerHabitacion(habitacion_id)
    
    # Subir imagen a Supabase
    url_imagen = await SubirImagenHabitacion(archivo, habitacion_id)
    
    # Actualizar habitación con la URL de la imagen
    DatosActualizacion = HabitacionUpdate(imagen_url=url_imagen)
    HabitacionActualizada = Servicio.ActualizarHabitacion(habitacion_id, DatosActualizacion)
    
    return {
        "message": "Imagen subida correctamente",
        "imagen_url": url_imagen,
        "habitacion": HabitacionActualizada
    }
