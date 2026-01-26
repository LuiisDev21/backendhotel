# Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el sistema de reservas de hotel en pocos minutos.

## 🚀 Opción Rápida: Docker (Recomendado)

Si tienes Docker instalado, esta es la forma más rápida de empezar:

### 1. Clonar el repositorio
```bash
cd backendhotel
```

### 2. Crear archivo `.env`
```bash
cp .env.example .env
```

Edita `.env` y agrega al menos:
```env
SECRET_KEY=tu-clave-secreta-aqui
```

### 3. Ejecutar con Docker
```bash
docker-compose up --build
```

### 4. Crear usuario administrador
En otra terminal:
```bash
docker-compose exec api python scripts/create_admin.py tu_contraseña
```

### 5. ¡Listo! 🎉
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

**Para más detalles sobre Docker, consulta `docs/DOCKER.md`**

---

## 📦 Opción Tradicional: Instalación Local

Si prefieres instalar todo manualmente o no tienes Docker:

## Prerrequisitos

- Python 3.9 o superior instalado
- PostgreSQL 12 o superior instalado y ejecutándose
- Acceso a línea de comandos (Terminal/PowerShell)

## Paso 1: Configurar Base de Datos

### 1.1. Crear la base de datos

Abre una terminal y ejecuta:

```bash
psql -U postgres
```

Luego ejecuta:

```sql
CREATE DATABASE hotel_db;
\q
```

### 1.2. Ejecutar el script SQL

```bash
psql -U postgres -d hotel_db -f database.sql
```

O si prefieres hacerlo desde psql:

```bash
psql -U postgres -d hotel_db
\i database.sql
\q
```

## Paso 2: Configurar el Proyecto

### 2.1. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2.3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/hotel_db
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=Sistema de Reservas de Hotel

# Configuración de Supabase (opcional, para subir imágenes)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
SUPABASE_BUCKET=habitaciones
```

**Importante:** 
- Reemplaza `tu_contraseña` con tu contraseña de PostgreSQL
- Genera una `SECRET_KEY` segura (puedes usar: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- Las variables de Supabase son opcionales. Si no las configuras, el sistema funcionará pero no podrás subir imágenes de habitaciones

## Paso 3: Crear Usuario Administrador

### Opción 1: Usando el script Python

```bash
python scripts/create_admin.py admin123
```

Copia el hash generado y úsalo en el siguiente comando SQL:

```sql
psql -U postgres -d hotel_db
INSERT INTO usuarios (email, nombre, apellido, hashed_password, es_administrador)
VALUES ('admin@hotel.com', 'Administrador', 'Sistema', '<hash_generado>', TRUE);
\q
```

### Opción 2: Registrar desde la API

Una vez que el servidor esté corriendo, puedes registrar un usuario normal y luego actualizarlo a administrador desde la base de datos:

```sql
UPDATE usuarios SET es_administrador = TRUE WHERE email = 'tu_email@example.com';
```

## Paso 4: Ejecutar el Servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

## Paso 5: Probar la API

### 5.1. Acceder a la documentación interactiva

Abre tu navegador en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5.2. Probar endpoints básicos

**1. Registrar un usuario:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "nombre": "Test",
    "apellido": "User",
    "password": "test123"
  }'
```

**2. Iniciar sesión:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

Guarda el `access_token` de la respuesta.

**3. Listar habitaciones:**
```bash
curl -X GET "http://localhost:8000/api/v1/habitaciones"
```

**4. Buscar habitaciones disponibles:**
```bash
curl -X GET "http://localhost:8000/api/v1/habitaciones/buscar?fecha_entrada=2024-02-01&fecha_salida=2024-02-05"
```

**5. Crear una reserva (con token):**
```bash
curl -X POST "http://localhost:8000/api/v1/reservas" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "habitacion_id": 1,
    "fecha_entrada": "2024-02-01",
    "fecha_salida": "2024-02-05",
    "numero_huespedes": 1
  }'
```

## Solución de Problemas

### Error: "No module named 'fastapi'"
**Solución:** Asegúrate de haber activado el entorno virtual e instalado las dependencias:
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Error: "could not connect to server"
**Solución:** Verifica que PostgreSQL esté ejecutándose y que las credenciales en `.env` sean correctas.

### Error: "relation does not exist"
**Solución:** Asegúrate de haber ejecutado el script `database.sql` correctamente.

### Error: "Invalid token"
**Solución:** Los tokens expiran después de 30 minutos (configurable). Inicia sesión nuevamente para obtener un nuevo token.

## Configuración Opcional: Supabase para Imágenes

Si deseas habilitar la funcionalidad de subir imágenes de habitaciones:

1. Crea una cuenta en [Supabase](https://supabase.com) y crea un proyecto
2. Crea un bucket de Storage llamado `habitaciones` (marcado como público)
3. Configura las políticas RLS en el bucket:
   - SELECT: `true` (lectura pública)
   - INSERT: `true` (subida de archivos)
   - UPDATE: `true` (actualización)
   - DELETE: `true` (eliminación, opcional)
4. Obtén las credenciales de tu proyecto (Settings > API)
5. Agrega las variables `SUPABASE_URL`, `SUPABASE_KEY` y `SUPABASE_BUCKET` a tu archivo `.env`

**Nota:** Las imágenes se suben automáticamente al crear o editar una habitación desde el panel de administrador. No es necesario subirlas por separado.

Para más detalles, consulta la sección "Configuración de Supabase para Imágenes" en `README.md`.

## Próximos Pasos

1. Revisa la documentación completa en `README.md`
2. Consulta la documentación técnica de endpoints en `docs/DOCUMENTACION_ENDPOINTS.md`
3. Explora la API usando Swagger UI en http://localhost:8000/docs
4. Prueba el frontend web abriendo `frontend/index.html` en tu navegador
5. Personaliza la configuración según tus necesidades

## Estructura de Archivos Importantes

```
backendhotel/
├── app/                    # Código de la aplicación
├── frontend/               # Aplicación web frontend
├── scripts/                # Scripts de utilidad
├── docs/                   # Documentación adicional
├── database.sql            # Script de base de datos
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno (crear)
└── README.md               # Documentación principal
```

¡Listo! Tu sistema de reservas de hotel está funcionando. 🎉
