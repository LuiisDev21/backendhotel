from supabase import create_client, Client
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import uuid
from typing import Optional


def ObtenerClienteSupabase() -> Optional[Client]:
    """Obtiene el cliente de Supabase si está configurado"""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    try:
        # Inicializar cliente de Supabase usando parámetros posicionales
        # create_client(url, key) es la forma estándar
        cliente = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return cliente
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inicializar cliente de Supabase: {str(e)}"
        )


async def SubirImagenHabitacion(archivo: UploadFile, habitacion_id: int) -> str:
    """
    Sube una imagen a Supabase Storage y retorna la URL pública
    
    Args:
        archivo: Archivo de imagen a subir
        habitacion_id: ID de la habitación
        
    Returns:
        URL pública de la imagen subida
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase no está configurado"
        )
    
    # Validar tipo de archivo
    tipos_permitidos = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if archivo.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(tipos_permitidos)}"
        )
    
    # Validar tamaño (máximo 5MB)
    contenido = await archivo.read()
    if len(contenido) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo es demasiado grande. Tamaño máximo: 5MB"
        )
    
    try:
        supabase = ObtenerClienteSupabase()
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo inicializar el cliente de Supabase"
            )
        
        # Generar nombre único para el archivo
        extension = archivo.filename.split('.')[-1] if '.' in archivo.filename else 'jpg'
        nombre_archivo = f"{habitacion_id}_{uuid.uuid4().hex}.{extension}"
        ruta_archivo = f"habitaciones/{nombre_archivo}"
        
        # Subir archivo a Supabase Storage
        # La API de Supabase Storage espera que los valores en file_options sean strings
        resultado = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=ruta_archivo,
            file=contenido,
            file_options={
                "content-type": archivo.content_type,
                "upsert": "true"  # Debe ser string, no booleano
            }
        )
        
        # Obtener URL pública
        url_publica = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(ruta_archivo)
        
        return url_publica
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la imagen: {str(e)}"
        )


async def EliminarImagenHabitacion(imagen_url: str) -> bool:
    """
    Elimina una imagen de Supabase Storage
    
    Args:
        imagen_url: URL de la imagen a eliminar
        
    Returns:
        True si se eliminó correctamente
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return False
    
    try:
        supabase = ObtenerClienteSupabase()
        
        # Extraer el nombre del archivo de la URL
        # La URL de Supabase tiene el formato: https://[project].supabase.co/storage/v1/object/public/[bucket]/[path]
        partes = imagen_url.split('/')
        if 'public' in partes:
            indice_public = partes.index('public')
            ruta_archivo = '/'.join(partes[indice_public + 1:])
            
            supabase.storage.from_(settings.SUPABASE_BUCKET).remove([ruta_archivo])
            return True
        
        return False
    except Exception:
        return False
