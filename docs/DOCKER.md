# Guía de Docker para Sistema de Reservas de Hotel

Esta guía explica cómo usar Docker para ejecutar la aplicación de manera sencilla y consistente.

## 📋 Requisitos Previos

- **Docker**: Versión 20.10 o superior
- **Docker Compose**: Versión 2.0 o superior

### Verificar instalación

```bash
docker --version
docker-compose --version
```

## 🚀 Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd backendhotel
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita `.env` con tus configuraciones. Tienes dos opciones:

**Opción A: Usar base de datos externa (ej: Supabase)**
```env
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_bd
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_BUCKET=habitaciones
```

> **Importante:** Si defines `DATABASE_URL` en tu `.env`, Docker la usará automáticamente y no necesitarás el servicio `db` local (aunque seguirá iniciándose, no causa problemas).

**Opción B: Usar base de datos local de Docker (por defecto)**
```env
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
# No necesitas DATABASE_URL, se construye automáticamente desde el contenedor db
```

### 3. Ejecutar con Docker Compose

**Si usas base de datos externa (tienes DATABASE_URL en .env):**
```bash
# Opción 1: Usar docker-compose normal (funciona con DATABASE_URL del .env)
docker-compose up --build

# Opción 2: Usar configuración específica para BD externa (sin servicio db)
docker-compose -f docker-compose.external-db.yml up --build
```

**Si usas base de datos local (no tienes DATABASE_URL en .env):**
```bash
docker-compose up --build
```

### 4. Acceder a la aplicación

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Crear usuario administrador

```bash
docker-compose exec api python scripts/create_admin.py tu_contraseña
```

## 🏗️ Arquitectura de Contenedores

El proyecto puede funcionar de dos formas:

### Opción 1: Base de datos local (por defecto)

Utiliza dos contenedores:

1. **`db`**: Contenedor de PostgreSQL 15
   - Puerto: 5432
   - Base de datos: `hotel_db`
   - Usuario: `postgres`
   - Contraseña: `postgres` (cambiar en producción)

2. **`api`**: Contenedor de la aplicación FastAPI
   - Puerto: 8000
   - Incluye inicialización automática de la base de datos
   - Hot-reload habilitado en desarrollo

### Opción 2: Base de datos externa

Si defines `DATABASE_URL` en tu `.env`, la aplicación usará esa base de datos externa (ej: Supabase, AWS RDS, etc.) y el contenedor `db` no se utilizará (aunque seguirá iniciándose, no causa problemas).

**Ventajas de base de datos externa:**
- No necesitas gestionar PostgreSQL localmente
- Datos persistentes en la nube
- Fácil de escalar
- Ideal para producción

## 📁 Archivos Docker

### `Dockerfile`

Define la imagen de la aplicación:
- Base: Python 3.11-slim
- Instala dependencias del sistema (gcc, postgresql-client)
- Instala dependencias de Python desde `requirements.txt`
- Expone el puerto 8000
- Ejecuta uvicorn

### `docker-compose.yml`

Configuración para **desarrollo**:
- Hot-reload habilitado (`--reload`)
- Volúmenes montados para desarrollo
- Valores por defecto para variables de entorno

### `docker-compose.prod.yml`

Configuración para **producción**:
- Sin hot-reload
- Variables de entorno desde `.env`
- Reinicio automático de contenedores
- Usa `DATABASE_URL` del `.env` si está definida, sino construye desde variables individuales

### `docker-compose.external-db.yml`

Configuración alternativa para usar **solo base de datos externa**:
- No incluye el servicio `db` local
- Requiere `DATABASE_URL` en el `.env`
- Ideal cuando usas Supabase u otra BD externa
- Uso: `docker-compose -f docker-compose.external-db.yml up --build`

### `.dockerignore`

Excluye archivos innecesarios de la imagen:
- Archivos de Python (`__pycache__`, `.pyc`)
- Entornos virtuales
- Archivos de IDE
- Documentación (excepto README.md)
- Frontend (si está en el mismo repo)

## 🔧 Comandos Útiles

### Gestión de contenedores

```bash
# Iniciar contenedores
docker-compose up

# Iniciar en segundo plano
docker-compose up -d

# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes (¡cuidado! borra la BD)
docker-compose down -v

# Reiniciar un servicio
docker-compose restart api

# Ver estado de contenedores
docker-compose ps
```

### Logs

```bash
# Ver todos los logs
docker-compose logs

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo de la API
docker-compose logs -f api

# Ver logs solo de la base de datos
docker-compose logs -f db
```

### Ejecutar comandos dentro de contenedores

```bash
# Abrir shell en el contenedor de la API
docker-compose exec api bash

# Ejecutar script de inicialización de BD
docker-compose exec api python scripts/init_database.py

# Crear usuario administrador
docker-compose exec api python scripts/create_admin.py contraseña

# Ejecutar comandos Python
docker-compose exec api python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### Reconstrucción

```bash
# Reconstruir todos los servicios
docker-compose build

# Reconstruir solo la API
docker-compose build api

# Reconstruir sin caché
docker-compose build --no-cache api

# Reconstruir y reiniciar
docker-compose up --build
```

### Base de datos

```bash
# Conectarse a PostgreSQL
docker-compose exec db psql -U postgres -d hotel_db

# Hacer backup de la base de datos
docker-compose exec db pg_dump -U postgres hotel_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres hotel_db < backup.sql
```

## 🚢 Despliegue en Producción

### 1. Preparar archivo `.env` de producción

Tienes dos opciones:

**Opción A: Base de datos externa (recomendado para producción)**
```env
# Base de datos externa (ej: Supabase, AWS RDS, etc.)
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_bd

# API
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=Sistema de Reservas de Hotel
API_PORT=8000

# Supabase (para imágenes)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_BUCKET=habitaciones
```

**Opción B: Base de datos local de Docker**
```env
# Base de datos local
POSTGRES_USER=admin
POSTGRES_PASSWORD=contraseña_muy_segura
POSTGRES_DB=hotel_db_prod

# API
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=Sistema de Reservas de Hotel
API_PORT=8000

# Supabase (opcional)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_BUCKET=habitaciones
```

> **Nota:** Si defines `DATABASE_URL`, Docker la usará automáticamente y no necesitarás las variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.

### 2. Ejecutar en producción

**Si usas base de datos externa (tienes DATABASE_URL en .env):**
```bash
# Opción 1: Usar docker-compose.prod.yml (funciona con DATABASE_URL del .env)
docker-compose -f docker-compose.prod.yml up -d --build

# Opción 2: Usar configuración específica para BD externa (sin servicio db)
docker-compose -f docker-compose.external-db.yml up -d --build
```

**Si usas base de datos local:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. Verificar que está funcionando

```bash
# Verificar estado
docker-compose -f docker-compose.prod.yml ps

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f api

# Probar endpoint de salud
curl http://localhost:8000/health
```

### 4. Configurar reinicio automático

Los contenedores ya están configurados con `restart: unless-stopped`, por lo que se reiniciarán automáticamente si el servidor se reinicia.

## 🔒 Seguridad en Producción

### 1. Cambiar credenciales por defecto

**Nunca uses las credenciales por defecto en producción:**

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=contraseña_muy_segura_y_larga
SECRET_KEY=generar-con-openssl-rand-hex-32
```

### 2. Generar SECRET_KEY segura

```bash
openssl rand -hex 32
```

### 3. Limitar acceso a la base de datos

En producción, considera:
- No exponer el puerto 5432 públicamente
- Usar un firewall
- Configurar SSL para conexiones a PostgreSQL

### 4. Variables de entorno sensibles

No commits el archivo `.env` al repositorio. Usa:
- Secretos de Docker Swarm
- Variables de entorno del sistema
- Servicios de gestión de secretos (HashiCorp Vault, AWS Secrets Manager, etc.)

## 🐛 Solución de Problemas

### El contenedor de la API no inicia

```bash
# Ver logs detallados
docker-compose logs api

# Verificar que la base de datos está lista
docker-compose exec db pg_isready -U postgres

# Verificar variables de entorno
docker-compose exec api env | grep DATABASE_URL
```

### Error de conexión a la base de datos

1. Verifica que el contenedor `db` esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Verifica la URL de conexión:
   ```bash
   docker-compose exec api python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
   ```

3. Prueba la conexión manualmente:
   ```bash
   docker-compose exec db psql -U postgres -d hotel_db -c "SELECT 1;"
   ```

### La base de datos no se inicializa

```bash
# Ejecutar manualmente el script de inicialización
docker-compose exec api python scripts/init_database.py
```

### Puerto 8000 ya está en uso

Cambia el puerto en `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

O detén el proceso que está usando el puerto 8000.

### Limpiar todo y empezar de nuevo

```bash
# Detener y eliminar contenedores
docker-compose down -v

# Eliminar imágenes
docker-compose down --rmi all

# Limpiar sistema Docker (¡cuidado!)
docker system prune -a --volumes

# Reconstruir desde cero
docker-compose up --build
```

## 📊 Monitoreo

### Ver uso de recursos

```bash
# Estadísticas de contenedores
docker stats

# Estadísticas de un contenedor específico
docker stats backendhotel_api
```

### Verificar salud de servicios

```bash
# Health check de la API
curl http://localhost:8000/health

# Health check de la base de datos
docker-compose exec db pg_isready -U postgres
```

## 🔄 Actualización de la Aplicación

### 1. Obtener última versión del código

```bash
git pull origin main
```

### 2. Reconstruir y reiniciar

```bash
docker-compose up -d --build
```

### 3. Verificar que funciona

```bash
docker-compose logs -f api
curl http://localhost:8000/health
```

## 📝 Notas Adicionales

- Los datos de PostgreSQL se persisten en un volumen Docker llamado `postgres_data`
- El hot-reload en desarrollo solo funciona si montas el código como volumen (ya configurado)
- Para producción, considera usar un reverse proxy (nginx, Traefik) frente a la API
- Para alta disponibilidad, considera usar Docker Swarm o Kubernetes

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica la documentación en `README.md`
3. Consulta la documentación de endpoints en `docs/DOCUMENTACION_ENDPOINTS.md`
