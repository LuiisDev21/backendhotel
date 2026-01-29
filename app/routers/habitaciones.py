""" 
Routers de Habitaciones, se definen los routers de habitaciones para la API.
- CrearHabitacion: Crea una nueva habitación.
- ListarHabitaciones: Lista todas las habitaciones.
- BuscarHabitacionesDisponibles: Busca las habitaciones disponibles para una fecha de entrada y salida.
- ObtenerHabitacion: Obtiene una habitación por su ID.
- ActualizarHabitacion: Actualiza una habitación existente.
- EliminarHabitacion: Elimina una habitación existente.
- SubirImagenHabitacion: Sube una imagen para una habitación y actualiza la URL en la base de datos.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import json
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerAdministrador, ObtenerUsuario
from app.core.storage import SubirImagenHabitacion
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate, HabitacionResponse
from app.services.habitacion_service import ServicioHabitacion
from app.models.usuario import Usuario

router = APIRouter(prefix="/habitaciones", tags=["Habitaciones"])


@router.post("", response_model=HabitacionResponse, dependencies=[Depends(ObtenerAdministrador)])
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
    Servicio = ServicioHabitacion(SesionBD)
    
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
            DatosActualizacion = HabitacionUpdate(imagen_url=url_imagen)
            HabitacionCreada = Servicio.ActualizarHabitacion(HabitacionCreada.id, DatosActualizacion)
        except Exception as e:
            pass
    
    return HabitacionCreada


@router.get("", response_model=List[HabitacionResponse])
def ListarHabitaciones(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.ListarHabitaciones(Saltar=Saltar, Limite=Limite)


@router.get("/buscar", response_model=List[HabitacionResponse])
def BuscarHabitacionesDisponibles(
    FechaEntrada: date = Query(...),
    FechaSalida: date = Query(...),
    Capacidad: Optional[int] = Query(None, ge=1),
    Tipo: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.BuscarDisponibles(
        FechaEntrada=FechaEntrada,
        FechaSalida=FechaSalida,
        Capacidad=Capacidad,
        Tipo=Tipo
    )


@router.get("/{habitacion_id}", response_model=HabitacionResponse)
def ObtenerHabitacion(habitacion_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.ObtenerHabitacion(habitacion_id)


@router.put("/{habitacion_id}", response_model=HabitacionResponse, dependencies=[Depends(ObtenerAdministrador)])
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
    Servicio = ServicioHabitacion(SesionBD)
    
    disponible_bool = disponible.lower() == 'true'
    
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
            DatosImagen = HabitacionUpdate(imagen_url=url_imagen)
            HabitacionActualizada = Servicio.ActualizarHabitacion(habitacion_id, DatosImagen)
        except Exception as e:
            pass
    
    return HabitacionActualizada


@router.delete("/{habitacion_id}", dependencies=[Depends(ObtenerAdministrador)])
def EliminarHabitacion(habitacion_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioHabitacion(SesionBD)
    Servicio.EliminarHabitacion(habitacion_id)
    return {"message": "Habitación eliminada correctamente"}


@router.post("/{habitacion_id}/imagen", dependencies=[Depends(ObtenerAdministrador)])
async def SubirImagenHabitacionEndpoint(
    habitacion_id: int,
    archivo: UploadFile = File(...),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """
    Sube una imagen para una habitación y actualiza la URL en la base de datos
    """
    Servicio = ServicioHabitacion(SesionBD)
    HabitacionEncontrada = Servicio.ObtenerHabitacion(habitacion_id)
    
    # Subir imagen a Supabase
    url_imagen = await SubirImagenHabitacion(archivo, habitacion_id)
    DatosActualizacion = HabitacionUpdate(imagen_url=url_imagen)
    HabitacionActualizada = Servicio.ActualizarHabitacion(habitacion_id, DatosActualizacion)
    
    return {
        "message": "Imagen subida correctamente",
        "imagen_url": url_imagen,
        "habitacion": HabitacionActualizada
    }
