# Sistema Web de Reservas de Hotel - Backend API

Sistema backend desarrollado con FastAPI para la gestión de reservas de hotel, incluyendo autenticación de usuarios, búsqueda de habitaciones, gestión de reservas y procesamiento de pagos.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Base de Datos](#base-de-datos)
- [Ejecución](#ejecución)
  - [Opción 1: Con Docker (Recomendado)](#opción-1-con-docker-recomendado-)
  - [Opción 2: Instalación Local (Sin Docker)](#opción-2-instalación-local-sin-docker)
- [Documentación de Endpoints](#documentación-de-endpoints)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Docker](#docker)

## 🚀 Características

### Módulos Implementados

1. **Módulo de Autenticación y Gestión de Usuarios**
   - Registro de usuarios
   - Inicio de sesión con JWT
   - Gestión de perfiles
   - Control de acceso basado en roles (cliente/administrador)
   - Listado de usuarios (solo administradores)

2. **Módulo de Búsqueda y Consulta de Habitaciones**
   - Listado de habitaciones
   - Búsqueda de habitaciones disponibles por fechas
   - Filtros por capacidad y tipo
   - Gestión de habitaciones (solo administradores)
   - **Subida de imágenes a Supabase Storage**
   - Visualización de imágenes en habitaciones

3. **Módulo de Gestión de Reservas**
   - Creación de reservas por clientes
   - Consulta de reservas propias
   - Administración completa de reservas (administradores)
   - Cancelación de reservas
   - Actualización de estado de reservas

4. **Módulo de Pagos y Facturación**
   - Procesamiento de pagos
   - Múltiples métodos de pago
   - Gestión de estados de pago
   - Reembolsos
   - Facturación automática

5. **Frontend Web Completo**
   - Interfaz de usuario moderna y minimalista
   - Panel de administrador con todas las funcionalidades
   - Panel de cliente para reservas
   - Gestión completa de imágenes de habitaciones
   - Diseño responsive y plano (flat design)

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura en capas** que separa las responsabilidades:

```
app/
├── core/           # Configuración y utilidades centrales
├── models/         # Modelos de base de datos (SQLAlchemy)
├── schemas/        # Esquemas de validación (Pydantic)
├── repositories/   # Capa de acceso a datos
├── services/       # Lógica de negocio
└── routers/        # Endpoints de la API
```

### Flujo de Datos

1. **Routers** → Reciben las peticiones HTTP
2. **Services** → Contienen la lógica de negocio
3. **Repositories** → Acceden a la base de datos
4. **Models** → Representan las entidades de la BD
5. **Schemas** → Validan y serializan los datos

## 📦 Requisitos

### Opción 1: Instalación Local
- Python 3.9 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

### Opción 2: Docker (Recomendado)
- Docker 20.10 o superior
- Docker Compose 2.0 o superior

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd backendhotel
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### 1. Crear archivo de variables de entorno

Copia el archivo `.env.example` y créalo como `.env`:

```bash
cp .env.example .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env` con tus configuraciones:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/hotel_db
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
- Cambia `SECRET_KEY` por una clave segura (puedes generar una con: `openssl rand -hex 32`)
- Ajusta `DATABASE_URL` con tus credenciales de PostgreSQL
- Las variables de Supabase son opcionales. Si no las configuras, el sistema funcionará pero no podrás subir imágenes

## 🗄️ Base de Datos

### 1. Crear base de datos en PostgreSQL

```sql
CREATE DATABASE hotel_db;
```

### 2. Ejecutar script SQL

**Opción 1: Desde línea de comandos**
```bash
psql -U usuario -d hotel_db -f database.sql
```

**Opción 2: Desde psql**
```bash
psql -U usuario -d hotel_db
\i database.sql
```

**Opción 3: Ejecutar manualmente**
Copia y pega el contenido de `database.sql` en tu cliente de PostgreSQL.

### 3. Verificar tablas creadas

```sql
\dt
```

Deberías ver las siguientes tablas:
- usuarios
- habitaciones
- reservas
- pagos

## ▶️ Ejecución

### Opción 1: Con Docker (Recomendado) 🐳

Docker es la forma más fácil y rápida de ejecutar la aplicación. La configuración usa tu base de datos externa (Supabase) desde el `.env`.

#### Desarrollo con Docker Compose

1. **Crear archivo `.env`** (si no existe):
   ```bash
   cp .env.example .env
   ```

2. **Configurar variables de entorno** (requerido):
   ```env
   DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_bd
   SECRET_KEY=tu-clave-secreta-aqui
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-anon-key
   SUPABASE_BUCKET=habitaciones
   ```
   > **Importante:** `DATABASE_URL` es **requerido**. La aplicación usará tu base de datos externa.

3. **Construir y ejecutar el contenedor**:
   ```bash
   docker-compose up --build
   ```

3. **La aplicación estará disponible en:**
   - API: http://localhost:8000
   - Documentación Swagger: http://localhost:8000/docs
   - Documentación ReDoc: http://localhost:8000/redoc

5. **Crear un usuario administrador**:
   ```bash
   docker-compose exec api python scripts/create_admin.py tu_contraseña
   ```

#### Producción con Docker Compose

1. **Crear archivo `.env` con variables de producción**:
   ```env
   DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_bd
   SECRET_KEY=clave-secreta-muy-segura-generada-con-openssl-rand-hex-32
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   API_V1_PREFIX=/api/v1
   PROJECT_NAME=Sistema de Reservas de Hotel
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-anon-key
   SUPABASE_BUCKET=habitaciones
   API_PORT=8000
   ```
   > **Importante:** `DATABASE_URL` es **requerido**. La aplicación usará tu base de datos externa.

2. **Ejecutar en modo producción**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

#### Comandos útiles de Docker

```bash
# Ver logs de los contenedores
docker-compose logs -f

# Ver logs solo de la API
docker-compose logs -f api

# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes (¡cuidado! esto borra la base de datos)
docker-compose down -v

# Reconstruir solo la API
docker-compose build api

# Ejecutar comandos dentro del contenedor de la API
docker-compose exec api bash

# Reiniciar un servicio específico
docker-compose restart api
```

#### Estructura de Docker

- **`Dockerfile`**: Define la imagen de la aplicación FastAPI
- **`docker-compose.yml`**: Configuración para desarrollo (con hot-reload, usa `DATABASE_URL` del `.env`)
- **`docker-compose.prod.yml`**: Configuración para producción (sin hot-reload, usa `DATABASE_URL` del `.env`)
- **`.dockerignore`**: Archivos excluidos de la imagen Docker

**Nota importante:** La configuración usa únicamente tu base de datos externa definida en `DATABASE_URL` del `.env`. No se crea ninguna base de datos local.

### Opción 2: Instalación Local (Sin Docker)

#### Modo desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Modo producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Con configuración personalizada

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Una vez ejecutado, la API estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## 📚 Documentación de Endpoints

### Autenticación (`/api/v1/auth`)

#### POST `/api/v1/auth/register`
Registra un nuevo usuario.

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678",
  "password": "contraseña123"
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678",
  "es_administrador": false,
  "activo": true,
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

#### POST `/api/v1/auth/login`
Inicia sesión y obtiene token de acceso.

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "contraseña123"
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/api/v1/auth/me`
Obtiene información del usuario autenticado.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** 200 OK
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678",
  "es_administrador": false,
  "activo": true,
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

#### GET `/api/v1/auth/usuarios`
Lista todos los usuarios registrados. **Requiere autenticación de administrador.**

**Query Parameters:**
- `Saltar` (int, opcional): Número de registros a omitir (default: 0)
- `Limite` (int, opcional): Número máximo de registros (default: 100, max: 100)

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "email": "usuario@example.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+505 1234-5678",
    "es_administrador": false,
    "activo": true,
    "fecha_creacion": "2024-01-25T12:00:00"
  }
]
```

---

### Habitaciones (`/api/v1/habitaciones`)

#### POST `/api/v1/habitaciones`
Crea una nueva habitación. Si se proporciona una imagen, se sube automáticamente a Supabase Storage. **Requiere autenticación de administrador.**

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (FormData):**
- `numero` (string, requerido): Número único de la habitación
- `tipo` (string, requerido): Tipo de habitación
- `descripcion` (string, opcional): Descripción de la habitación
- `capacidad` (integer, requerido): Capacidad de huéspedes
- `precio_por_noche` (decimal, requerido): Precio por noche
- `disponible` (boolean, opcional): Disponibilidad (default: true)
- `archivo` (file, opcional): Archivo de imagen (JPEG, PNG, WebP, máximo 5MB)

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/habitaciones" \
  -H "Authorization: Bearer {token}" \
  -F "numero=301" \
  -F "tipo=Suite" \
  -F "descripcion=Suite de lujo con jacuzzi" \
  -F "capacidad=2" \
  -F "precio_por_noche=200.00" \
  -F "disponible=true" \
  -F "archivo=@/ruta/a/imagen.jpg"
```

**Response:** 200 OK
```json
{
  "id": 7,
  "numero": "301",
  "tipo": "Suite",
  "descripcion": "Suite de lujo con jacuzzi",
  "capacidad": 2,
  "precio_por_noche": 200.00,
  "disponible": true,
  "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/habitaciones/7_abc123.jpg",
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

**Nota:** La imagen se sube automáticamente si se proporciona. Si la subida falla, la habitación se crea igualmente pero sin imagen.

#### POST `/api/v1/habitaciones/{habitacion_id}/imagen`
Sube una imagen para una habitación. **Requiere autenticación de administrador.**

**Nota:** Este endpoint está disponible para compatibilidad, pero se recomienda usar el endpoint de crear o actualizar habitación con el campo `archivo` en FormData, ya que sube la imagen automáticamente en una sola operación.

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (FormData):**
- `archivo`: Archivo de imagen (JPEG, PNG, WebP, máximo 5MB)

**Response:** 200 OK
```json
{
  "message": "Imagen subida correctamente",
  "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/habitaciones/1_abc123.jpg",
  "habitacion": { ... }
}
```

#### GET `/api/v1/habitaciones`
Lista todas las habitaciones.

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir (default: 0)
- `limit` (int, opcional): Número máximo de registros (default: 100, max: 100)

**Ejemplo:**
```
GET /api/v1/habitaciones?skip=0&limit=10
```

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "numero": "101",
    "tipo": "Individual",
    "descripcion": "Habitación individual",
    "capacidad": 1,
    "precio_por_noche": 50.00,
    "disponible": true,
    "fecha_creacion": "2024-01-25T12:00:00"
  }
]
```

#### GET `/api/v1/habitaciones/buscar`
Busca habitaciones disponibles en un rango de fechas.

**Query Parameters:**
- `fecha_entrada` (date, requerido): Fecha de entrada (formato: YYYY-MM-DD)
- `fecha_salida` (date, requerido): Fecha de salida (formato: YYYY-MM-DD)
- `capacidad` (int, opcional): Capacidad mínima requerida
- `tipo` (string, opcional): Tipo de habitación

**Ejemplo:**
```
GET /api/v1/habitaciones/buscar?fecha_entrada=2024-02-01&fecha_salida=2024-02-05&capacidad=2
```

**Response:** 200 OK
```json
[
  {
    "id": 2,
    "numero": "102",
    "tipo": "Doble",
    "capacidad": 2,
    "precio_por_noche": 75.00,
    "disponible": true
  }
]
```

#### GET `/api/v1/habitaciones/{habitacion_id}`
Obtiene los detalles de una habitación específica.

**Response:** 200 OK
```json
{
  "id": 1,
  "numero": "101",
  "tipo": "Individual",
  "descripcion": "Habitación individual",
  "capacidad": 1,
  "precio_por_noche": 50.00,
  "disponible": true,
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

#### PUT `/api/v1/habitaciones/{habitacion_id}`
Actualiza una habitación. Si se proporciona una imagen, se sube automáticamente a Supabase Storage y reemplaza la imagen anterior. **Requiere autenticación de administrador.**

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (FormData):**
- `tipo` (string, requerido): Tipo de habitación
- `descripcion` (string, opcional): Descripción de la habitación
- `capacidad` (integer, requerido): Capacidad de huéspedes
- `precio_por_noche` (decimal, requerido): Precio por noche
- `disponible` (string, requerido): Disponibilidad ("true" o "false")
- `archivo` (file, opcional): Archivo de imagen (JPEG, PNG, WebP, máximo 5MB)

**Ejemplo con curl:**
```bash
curl -X PUT "http://localhost:8000/api/v1/habitaciones/1" \
  -H "Authorization: Bearer {token}" \
  -F "tipo=Individual Premium" \
  -F "descripcion=Habitación actualizada" \
  -F "capacidad=1" \
  -F "precio_por_noche=55.00" \
  -F "disponible=true" \
  -F "archivo=@/ruta/a/nueva-imagen.jpg"
```

**Nota:** La imagen se sube automáticamente si se proporciona. Si la subida falla, los demás campos se actualizan igualmente.

#### DELETE `/api/v1/habitaciones/{habitacion_id}`
Elimina una habitación. **Requiere autenticación de administrador.**

**Response:** 200 OK
```json
{
  "message": "Habitación eliminada correctamente"
}
```

---

### Reservas (`/api/v1/reservas`)

#### POST `/api/v1/reservas`
Crea una nueva reserva. **Requiere autenticación.**

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "habitacion_id": 1,
  "fecha_entrada": "2024-02-01",
  "fecha_salida": "2024-02-05",
  "numero_huespedes": 2,
  "notas": "Llegada tarde"
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "usuario_id": 1,
  "habitacion_id": 1,
  "fecha_entrada": "2024-02-01",
  "fecha_salida": "2024-02-05",
  "numero_huespedes": 2,
  "precio_total": 200.00,
  "estado": "pendiente",
  "notas": "Llegada tarde",
  "fecha_creacion": "2024-01-25T12:00:00",
  "fecha_actualizacion": "2024-01-25T12:00:00"
}
```

#### GET `/api/v1/reservas`
Lista las reservas del usuario autenticado.

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir
- `limit` (int, opcional): Número máximo de registros

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "habitacion_id": 1,
    "fecha_entrada": "2024-02-01",
    "fecha_salida": "2024-02-05",
    "numero_huespedes": 2,
    "precio_total": 200.00,
    "estado": "pendiente"
  }
]
```

#### GET `/api/v1/reservas/todas`
Lista todas las reservas. **Requiere autenticación de administrador.**

#### GET `/api/v1/reservas/{reserva_id}`
Obtiene los detalles de una reserva específica.

#### PUT `/api/v1/reservas/{reserva_id}`
Actualiza una reserva.

**Request Body:**
```json
{
  "fecha_salida": "2024-02-06",
  "notas": "Actualización de notas"
}
```

#### POST `/api/v1/reservas/{reserva_id}/cancelar`
Cancela una reserva.

**Response:** 200 OK
```json
{
  "id": 1,
  "estado": "cancelada",
  ...
}
```

---

### Pagos (`/api/v1/pagos`)

#### POST `/api/v1/pagos`
Crea un pago para una reserva. **Requiere autenticación.**

**Request Body:**
```json
{
  "reserva_id": 1,
  "metodo_pago": "tarjeta_credito"
}
```

**Métodos de pago disponibles:**
- `tarjeta_credito`
- `tarjeta_debito`
- `efectivo`
- `transferencia`

**Response:** 201 Created
```json
{
  "id": 1,
  "reserva_id": 1,
  "monto": 200.00,
  "metodo_pago": "tarjeta_credito",
  "estado": "pendiente",
  "numero_transaccion": "uuid-generado",
  "fecha_pago": null,
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

#### GET `/api/v1/pagos`
Lista todos los pagos. **Requiere autenticación de administrador.**

#### GET `/api/v1/pagos/reserva/{reserva_id}`
Obtiene el pago asociado a una reserva.

#### GET `/api/v1/pagos/{pago_id}`
Obtiene los detalles de un pago específico. **Requiere autenticación de administrador.**

#### POST `/api/v1/pagos/{pago_id}/procesar`
Procesa un pago pendiente. **Requiere autenticación de administrador.**

**Response:** 200 OK
```json
{
  "id": 1,
  "estado": "completado",
  "fecha_pago": "2024-01-25T12:30:00"
}
```

#### PUT `/api/v1/pagos/{pago_id}`
Actualiza un pago. **Requiere autenticación de administrador.**

**Request Body:**
```json
{
  "estado": "rechazado",
  "numero_transaccion": "TXN-12345"
}
```

#### POST `/api/v1/pagos/{pago_id}/reembolsar`
Reembolsa un pago completado. **Requiere autenticación de administrador.**

**Response:** 200 OK
```json
{
  "id": 1,
  "estado": "reembolsado"
}
```

---

## 📁 Estructura del Proyecto

```
backendhotel/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración y variables de entorno
│   │   ├── database.py         # Conexión a base de datos
│   │   ├── security.py         # Funciones de seguridad (JWT, bcrypt)
│   │   ├── dependencies.py     # Dependencias de autenticación
│   │   ├── storage.py          # Funciones para Supabase Storage
│   │   └── enum_type.py        # TypeDecorator para enums
├── Dockerfile                  # Configuración de imagen Docker
├── docker-compose.yml          # Configuración Docker Compose (desarrollo, solo API)
├── docker-compose.prod.yml     # Configuración Docker Compose (producción, solo API)
├── .dockerignore              # Archivos excluidos de imagen Docker
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py          # Modelo Usuario
│   │   ├── habitacion.py       # Modelo Habitación
│   │   ├── reserva.py          # Modelo Reserva
│   │   └── pago.py             # Modelo Pago
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── usuario.py          # Esquemas Pydantic para Usuario
│   │   ├── habitacion.py       # Esquemas Pydantic para Habitación
│   │   ├── reserva.py          # Esquemas Pydantic para Reserva
│   │   └── pago.py             # Esquemas Pydantic para Pago
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── usuario_repository.py
│   │   ├── habitacion_repository.py
│   │   ├── reserva_repository.py
│   │   └── pago_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── usuario_service.py
│   │   ├── habitacion_service.py
│   │   ├── reserva_service.py
│   │   └── pago_service.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py             # Endpoints de autenticación
│       ├── habitaciones.py     # Endpoints de habitaciones
│       ├── reservas.py         # Endpoints de reservas
│       └── pagos.py            # Endpoints de pagos
├── frontend/                    # Aplicación web frontend
│   ├── index.html              # Página de login/registro
│   ├── admin.html              # Panel de administrador
│   ├── cliente.html            # Panel de cliente
│   ├── styles.css              # Estilos CSS
│   ├── api.js                  # Funciones para llamadas API
│   ├── app.js                  # Lógica de autenticación
│   ├── admin.js                # Lógica del panel admin
│   └── cliente.js              # Lógica del panel cliente
├── scripts/
│   ├── create_admin.py         # Script para generar hash de contraseña
│   └── init_database.py       # Script para inicializar BD
├── docs/                        # Documentación adicional
│   ├── DOCUMENTACION_ENDPOINTS.md
│   ├── DOCKER.md                # Guía completa de Docker
│   ├── INICIO_RAPIDO.md
│   └── LIBRO_APRENDIZAJE.md
├── database.sql                 # Script SQL para crear la base de datos
├── requirements.txt            # Dependencias del proyecto
├── .env                        # Variables de entorno (crear)
├── .gitignore
└── README.md                   # Este archivo
```

## 🔐 Seguridad

- **Autenticación JWT**: Tokens de acceso con expiración configurable
- **Encriptación de contraseñas**: Usando bcrypt (librería estándar y segura)
- **Validación de datos**: Pydantic para validación automática
- **Control de acceso**: Roles de usuario (cliente/administrador)
- **CORS**: Configurado para permitir solicitudes desde cualquier origen (ajustar en producción)

## 🧪 Pruebas

Puedes probar la API usando:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc
3. **Postman** o cualquier cliente HTTP
4. **curl** desde la terminal

### Ejemplo con curl

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "nombre": "Test",
    "apellido": "User",
    "password": "test123"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'

# Obtener habitaciones (con token)
curl -X GET "http://localhost:8000/api/v1/habitaciones" \
  -H "Authorization: Bearer {tu_token_aqui}"
```

## 🚀 Despliegue en Producción

### Consideraciones importantes:

1. **Variables de entorno**: Cambiar `SECRET_KEY` por una clave segura
2. **Base de datos**: Usar una base de datos PostgreSQL en producción
3. **HTTPS**: Configurar SSL/TLS para comunicación segura
4. **CORS**: Restringir orígenes permitidos en producción
5. **Servidor WSGI**: Usar Gunicorn o similar con Uvicorn workers
6. **Logging**: Configurar sistema de logs apropiado
7. **Monitoreo**: Implementar monitoreo y alertas

### Ejemplo con Gunicorn:

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📝 Notas Adicionales

- El sistema calcula automáticamente el precio total de las reservas basado en el número de noches
- Las reservas canceladas no bloquean las fechas de las habitaciones
- Los pagos se asocian automáticamente con las reservas
- El estado de las reservas se actualiza automáticamente cuando se procesa un pago
- Las imágenes de habitaciones se almacenan en Supabase Storage (opcional)
- El frontend está incluido en la carpeta `frontend/` y puede abrirse directamente en el navegador

## 🖼️ Configuración de Supabase para Imágenes

Para habilitar la funcionalidad de subida de imágenes de habitaciones:

### 1. Crear el Bucket en Supabase

1. Ve a tu proyecto en Supabase
2. Navega a **Storage** en el menú lateral
3. Haz clic en **New bucket**
4. Nombre del bucket: `habitaciones`
5. Marca como **Public bucket**
6. Haz clic en **Create bucket**

### 2. Configurar Políticas de Storage (IMPORTANTE)

El bucket necesita políticas RLS (Row Level Security) para permitir la subida de archivos.

1. En el bucket `habitaciones`, ve a **Policies**
2. Haz clic en **New Policy**
3. Selecciona **For full customization**
4. Crea las siguientes políticas:

**Política 1: Lectura pública (SELECT)**
- Policy name: `Public read access`
- Allowed operation: SELECT
- Policy definition: `true`

**Política 2: Subida de archivos (INSERT)**
- Policy name: `Allow uploads`
- Allowed operation: INSERT
- Policy definition: `true`

**Política 3: Actualización (UPDATE)**
- Policy name: `Allow updates`
- Allowed operation: UPDATE
- Policy definition: `true`

**Política 4: Eliminación (DELETE) - Opcional**
- Policy name: `Allow deletes`
- Allowed operation: DELETE
- Policy definition: `true`

### 3. Obtener las Credenciales

1. Ve a **Settings** > **API** en tu proyecto de Supabase
2. Copia:
   - **Project URL** (SUPABASE_URL)
   - **anon public** key (SUPABASE_KEY)

### 4. Agregar Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
SUPABASE_BUCKET=habitaciones
```

### 5. Ejecutar Migración de Base de Datos

Si ya tienes la tabla `habitaciones` creada, ejecuta la migración:

```bash
psql -U usuario -d hotel_db -f migrations/add_imagen_url_to_habitaciones.sql
```

O si estás usando `database.sql` desde cero, el campo `imagen_url` ya está incluido.

### Formatos y Límites

- **Formatos soportados**: JPEG, JPG, PNG, WebP
- **Tamaño máximo**: 5MB por imagen
- **Ruta de almacenamiento**: `habitaciones/{habitacion_id}_{uuid}.{extension}`

## 🌐 Frontend Web

El proyecto incluye una aplicación web frontend completa en la carpeta `frontend/`:

### Características del Frontend

- **Interfaz minimalista**: Diseño plano con colores blanco y gris
- **Panel de Administrador**: Gestión completa de habitaciones, reservas, pagos y usuarios
- **Panel de Cliente**: Búsqueda de habitaciones, creación de reservas y gestión de pagos
- **Subida de imágenes**: Interfaz para subir imágenes de habitaciones
- **Responsive**: Adaptable a diferentes tamaños de pantalla

### Uso del Frontend

1. Abre `frontend/index.html` en tu navegador
2. Registra un nuevo usuario o inicia sesión
3. Según tu rol, serás redirigido a:
   - `admin.html` - Si eres administrador
   - `cliente.html` - Si eres cliente

### Configuración

Asegúrate de que el backend esté ejecutándose en:
```
http://127.0.0.1:8000
```

Si el backend está en otra URL, edita `API_BASE_URL` en `frontend/api.js`:

```javascript
const API_BASE_URL = 'http://tu-url:puerto/api/v1';
```

## 🤝 Contribuciones

Este proyecto fue desarrollado como parte de un proyecto académico. Para mejoras o correcciones, por favor crear un issue o pull request.

## 📄 Licencia

Este proyecto es de uso educativo.

---

**Desarrollado con FastAPI, SQLAlchemy y PostgreSQL**

---

## 📖 Documentación Adicional

Este proyecto incluye documentación adicional para facilitar su uso:

- **[docs/INICIO_RAPIDO.md](docs/INICIO_RAPIDO.md)**: Guía paso a paso para poner en marcha el sistema rápidamente
- **[docs/DOCKER.md](docs/DOCKER.md)**: Guía completa de Docker para desarrollo y producción
- **[docs/DOCUMENTACION_ENDPOINTS.md](docs/DOCUMENTACION_ENDPOINTS.md)**: Documentación técnica detallada de todos los endpoints de la API
- **[docs/LIBRO_APRENDIZAJE.md](docs/LIBRO_APRENDIZAJE.md)**: Libro de aprendizaje completo sobre el proyecto
- **[frontend/README.md](frontend/README.md)**: Documentación del frontend web
