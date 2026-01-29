# RoyalPalms API Endpoints

## Base URL
```
http://localhost:8000/api/v1
```

## Autenticación

Todos los endpoints que requieren autenticación utilizan **Bearer Token** en el header:
```
Authorization: Bearer {access_token}
```

---

## 1. Módulo de Autenticación

### 1.1. Registrar Usuario
**POST** `/auth/register`

**Descripción:** Crea un nuevo usuario en el sistema.

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "string (email válido)",
  "nombre": "string (máx. 100 caracteres)",
  "apellido": "string (máx. 100 caracteres)",
  "telefono": "string (opcional, máx. 20 caracteres)",
  "password": "string (mín. 6 caracteres recomendado)"
}
```

**Response 201:**
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

**Errores:**
- `400`: Email ya registrado
- `422`: Datos de validación inválidos

---

### 1.2. Iniciar Sesión
**POST** `/auth/login`

**Descripción:** Autentica un usuario y devuelve un token JWT.

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "string (email válido)",
  "password": "string"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errores:**
- `401`: Email o contraseña incorrectos
- `403`: Usuario inactivo
- `422`: Datos de validación inválidos

---

### 1.3. Obtener Usuario Actual
**GET** `/auth/me`

**Descripción:** Obtiene la información del usuario autenticado.

**Autenticación:** Requerida

**Response 200:**
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

**Errores:**
- `401`: Token inválido o expirado

---

### 1.4. Listar Usuarios
**GET** `/auth/usuarios`

**Descripción:** Obtiene una lista paginada de todos los usuarios registrados.

**Autenticación:** Requerida (Administrador)

**Query Parameters:**
- `Saltar` (integer, opcional): Número de registros a omitir (default: 0, mín: 0)
- `Limite` (integer, opcional): Número máximo de registros (default: 100, mín: 1, máx: 100)

**Ejemplo:**
```
GET /auth/usuarios?Saltar=0&Limite=10
```

**Response 200:**
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

**Errores:**
- `401`: No autenticado
- `403`: No es administrador

---

## 2. Módulo de Habitaciones

### 2.1. Crear Habitación
**POST** `/habitaciones`

**Descripción:** Crea una nueva habitación en el sistema. Si se proporciona una imagen, se sube automáticamente a Supabase Storage y se asocia a la habitación.

**Autenticación:** Requerida (Administrador)

**Content-Type:** `multipart/form-data`

**Request Body (FormData):**
- `numero` (string, requerido): Número único de la habitación (máx. 10 caracteres)
- `tipo` (string, requerido): Tipo de habitación (máx. 50 caracteres)
- `descripcion` (string, opcional): Descripción de la habitación
- `capacidad` (integer, requerido): Capacidad de huéspedes (mín. 1)
- `precio_por_noche` (decimal, requerido): Precio por noche (mín. 0.01)
- `disponible` (boolean, opcional): Disponibilidad de la habitación (default: true)
- `archivo` (file, opcional): Archivo de imagen
  - Formatos permitidos: JPEG, JPG, PNG, WebP
  - Tamaño máximo: 5MB
  - Si se proporciona, se sube automáticamente a Supabase Storage

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/habitaciones" \
  -H "Authorization: Bearer {token}" \
  -F "numero=101" \
  -F "tipo=Individual" \
  -F "descripcion=Habitación individual con vista al mar" \
  -F "capacidad=1" \
  -F "precio_por_noche=50.00" \
  -F "disponible=true" \
  -F "archivo=@/ruta/a/imagen.jpg"
```

**Response 200:**
```json
{
  "id": 1,
  "numero": "101",
  "tipo": "Individual",
  "descripcion": "Habitación individual con vista al mar",
  "capacidad": 1,
  "precio_por_noche": 50.00,
  "disponible": true,
  "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/habitaciones/1_abc123.jpg",
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

**Nota:** Si se proporciona una imagen, se sube automáticamente a Supabase Storage y la URL se asigna a `imagen_url`. Si la subida de imagen falla, la habitación se crea igualmente pero sin imagen.

**Errores:**
- `400`: Número de habitación ya existe, tipo de archivo no permitido, archivo demasiado grande
- `401`: No autenticado
- `403`: No es administrador
- `422`: Datos de validación inválidos
- `500`: Error al subir imagen a Supabase (si se proporcionó archivo)

---

### 2.2. Listar Habitaciones
**GET** `/habitaciones`

**Descripción:** Obtiene una lista paginada de todas las habitaciones.

**Autenticación:** No requerida

**Query Parameters:**
- `skip` (integer, opcional): Número de registros a omitir (default: 0, mín: 0)
- `limit` (integer, opcional): Número máximo de registros (default: 100, mín: 1, máx: 100)

**Ejemplo:**
```
GET /habitaciones?skip=0&limit=10
```

**Response 200:**
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
    "imagen_url": null,
    "fecha_creacion": "2024-01-25T12:00:00"
  }
]
```

---

### 2.3. Buscar Habitaciones Disponibles
**GET** `/habitaciones/buscar`

**Descripción:** Busca habitaciones disponibles en un rango de fechas específico.

**Autenticación:** No requerida

**Query Parameters:**
- `fecha_entrada` (date, requerido): Fecha de entrada (formato: YYYY-MM-DD)
- `fecha_salida` (date, requerido): Fecha de salida (formato: YYYY-MM-DD)
- `capacidad` (integer, opcional): Capacidad mínima requerida (mín: 1)
- `tipo` (string, opcional): Tipo de habitación

**Ejemplo:**
```
GET /habitaciones/buscar?fecha_entrada=2024-02-01&fecha_salida=2024-02-05&capacidad=2
```

**Response 200:**
```json
[
  {
    "id": 2,
    "numero": "102",
    "tipo": "Doble",
    "descripcion": "Habitación doble",
    "capacidad": 2,
    "precio_por_noche": 75.00,
    "disponible": true,
    "imagen_url": null,
    "fecha_creacion": "2024-01-25T12:00:00"
  }
]
```

**Errores:**
- `400`: Fecha de entrada debe ser anterior a fecha de salida
- `422`: Datos de validación inválidos

---

### 2.4. Obtener Habitación por ID
**GET** `/habitaciones/{habitacion_id}`

**Descripción:** Obtiene los detalles de una habitación específica.

**Autenticación:** No requerida

**Path Parameters:**
- `habitacion_id` (integer): ID de la habitación

**Response 200:**
```json
{
  "id": 1,
  "numero": "101",
  "tipo": "Individual",
  "descripcion": "Habitación individual",
  "capacidad": 1,
  "precio_por_noche": 50.00,
  "disponible": true,
  "imagen_url": null,
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

**Errores:**
- `404`: Habitación no encontrada

---

### 2.5. Actualizar Habitación
**PUT** `/habitaciones/{habitacion_id}`

**Descripción:** Actualiza los datos de una habitación existente. Si se proporciona una imagen, se sube automáticamente a Supabase Storage y reemplaza la imagen anterior.

**Autenticación:** Requerida (Administrador)

**Content-Type:** `multipart/form-data`

**Path Parameters:**
- `habitacion_id` (integer): ID de la habitación

**Request Body (FormData):**
- `tipo` (string, requerido): Tipo de habitación
- `descripcion` (string, opcional): Descripción de la habitación
- `capacidad` (integer, requerido): Capacidad de huéspedes (mín. 1)
- `precio_por_noche` (decimal, requerido): Precio por noche (mín. 0.01)
- `disponible` (string, requerido): Disponibilidad ("true" o "false")
- `archivo` (file, opcional): Archivo de imagen
  - Formatos permitidos: JPEG, JPG, PNG, WebP
  - Tamaño máximo: 5MB
  - Si se proporciona, se sube automáticamente a Supabase Storage y reemplaza la imagen anterior

**Ejemplo con curl:**
```bash
curl -X PUT "http://localhost:8000/api/v1/habitaciones/1" \
  -H "Authorization: Bearer {token}" \
  -F "tipo=Individual Premium" \
  -F "descripcion=Habitación individual actualizada" \
  -F "capacidad=1" \
  -F "precio_por_noche=55.00" \
  -F "disponible=true" \
  -F "archivo=@/ruta/a/nueva-imagen.jpg"
```

**Response 200:**
```json
{
  "id": 1,
  "numero": "101",
  "tipo": "Individual Premium",
  "descripcion": "Habitación individual actualizada",
  "capacidad": 1,
  "precio_por_noche": 55.00,
  "disponible": true,
  "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/habitaciones/1_xyz789.jpg",
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

**Nota:** Si se proporciona una imagen, se sube automáticamente a Supabase Storage y la URL se actualiza en `imagen_url`. Si la subida de imagen falla, los demás campos se actualizan igualmente.

**Errores:**
- `400`: Tipo de archivo no permitido, archivo demasiado grande
- `401`: No autenticado
- `403`: No es administrador
- `404`: Habitación no encontrada
- `500`: Error al subir imagen a Supabase (si se proporcionó archivo)

---

### 2.6. Eliminar Habitación
**DELETE** `/habitaciones/{habitacion_id}`

**Descripción:** Elimina una habitación del sistema. Solo se puede eliminar si todas las reservas asociadas están completadas o canceladas. Las reservas completadas/canceladas y sus pagos asociados se eliminan automáticamente.

**Autenticación:** Requerida (Administrador)

**Path Parameters:**
- `habitacion_id` (integer): ID de la habitación

**Response 200:**
```json
{
  "message": "Habitación eliminada correctamente"
}
```

**Errores:**
- `400`: No se puede eliminar porque tiene reservas activas (pendientes o confirmadas)
- `401`: No autenticado
- `403`: No es administrador
- `404`: Habitación no encontrada

**Nota:** Si la habitación tiene reservas con estado "pendiente" o "confirmada", no se puede eliminar. Primero deben completarse o cancelarse esas reservas.

---

### 2.7. Subir Imagen de Habitación (Endpoint Separado)
**POST** `/habitaciones/{habitacion_id}/imagen`

**Descripción:** Sube una imagen para una habitación y actualiza la URL en la base de datos. La imagen se almacena en Supabase Storage.

**Nota:** Este endpoint está disponible para compatibilidad, pero se recomienda usar el endpoint de crear o actualizar habitación con el campo `archivo` en FormData, ya que sube la imagen automáticamente en una sola operación.

**Autenticación:** Requerida (Administrador)

**Path Parameters:**
- `habitacion_id` (integer): ID de la habitación

**Request Body (multipart/form-data):**
- `archivo` (file, requerido): Archivo de imagen
  - Formatos permitidos: JPEG, JPG, PNG, WebP
  - Tamaño máximo: 5MB

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/habitaciones/1/imagen" \
  -H "Authorization: Bearer {token}" \
  -F "archivo=@/ruta/a/imagen.jpg"
```

**Response 200:**
```json
{
  "message": "Imagen subida correctamente",
  "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/habitaciones/1_abc123.jpg",
  "habitacion": {
    "id": 1,
    "numero": "101",
    "tipo": "Individual",
    "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/habitaciones/1_abc123.jpg",
    ...
  }
}
```

**Errores:**
- `400`: Tipo de archivo no permitido o archivo demasiado grande
- `401`: No autenticado
- `403`: No es administrador
- `404`: Habitación no encontrada
- `500`: Error al subir la imagen o Supabase no configurado

**Notas:**
- Requiere que Supabase esté configurado en las variables de entorno
- La imagen se almacena en el bucket `habitaciones` de Supabase Storage
- El nombre del archivo se genera automáticamente: `{habitacion_id}_{uuid}.{extension}`
- Si ya existe una imagen, se reemplaza automáticamente

---

## 3. Módulo de Reservas

### 3.1. Crear Reserva
**POST** `/reservas`

**Descripción:** Crea una nueva reserva para el usuario autenticado.

**Autenticación:** Requerida

**Request Body:**
```json
{
  "habitacion_id": "integer",
  "fecha_entrada": "date (formato: YYYY-MM-DD)",
  "fecha_salida": "date (formato: YYYY-MM-DD)",
  "numero_huespedes": "integer (mín. 1)",
  "notas": "string (opcional, máx. 500 caracteres)"
}
```

**Response 201:**
```json
{
  "id": 1,
  "usuario_id": 1,
  "habitacion_id": 1,
  "numero_habitacion": "101",
  "nombre_usuario": "Juan Pérez",
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

**Errores:**
- `400`: 
  - Habitación no disponible
  - Habitación no disponible en las fechas seleccionadas
  - Número de huéspedes excede la capacidad
  - Fecha de salida debe ser posterior a fecha de entrada
- `401`: No autenticado
- `404`: Habitación no encontrada
- `422`: Datos de validación inválidos

---

### 3.2. Listar Mis Reservas
**GET** `/reservas`

**Descripción:** Obtiene todas las reservas del usuario autenticado.

**Autenticación:** Requerida

**Query Parameters:**
- `skip` (integer, opcional): Número de registros a omitir (default: 0)
- `limit` (integer, opcional): Número máximo de registros (default: 100, máx: 100)

**Response 200:**
```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "habitacion_id": 1,
    "numero_habitacion": "101",
    "nombre_usuario": "Juan Pérez",
    "fecha_entrada": "2024-02-01",
    "fecha_salida": "2024-02-05",
    "numero_huespedes": 2,
    "precio_total": 200.00,
    "estado": "pendiente",
    "notas": "Llegada tarde",
    "fecha_creacion": "2024-01-25T12:00:00",
    "fecha_actualizacion": "2024-01-25T12:00:00"
  }
]
```

---

### 3.3. Listar Todas las Reservas
**GET** `/reservas/todas`

**Descripción:** Obtiene todas las reservas del sistema (solo administradores).

**Autenticación:** Requerida (Administrador)

**Query Parameters:**
- `skip` (integer, opcional): Número de registros a omitir (default: 0)
- `limit` (integer, opcional): Número máximo de registros (default: 100, máx: 100)

**Response 200:** Array de reservas con `numero_habitacion` y `nombre_usuario` incluidos (mismo formato que 3.2)

**Errores:**
- `401`: No autenticado
- `403`: No es administrador

---

### 3.4. Obtener Reserva por ID
**GET** `/reservas/{reserva_id}`

**Descripción:** Obtiene los detalles de una reserva específica.

**Autenticación:** Requerida

**Path Parameters:**
- `reserva_id` (integer): ID de la reserva

**Response 200:**
```json
{
  "id": 1,
  "usuario_id": 1,
  "habitacion_id": 1,
  "numero_habitacion": "101",
  "nombre_usuario": "Juan Pérez",
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

**Errores:**
- `401`: No autenticado
- `403`: No tiene permiso para ver esta reserva
- `404`: Reserva no encontrada

---

### 3.5. Actualizar Reserva
**PUT** `/reservas/{reserva_id}`

**Descripción:** Actualiza una reserva existente.

**Autenticación:** Requerida (Cliente puede actualizar sus propias reservas, Administrador puede actualizar cualquiera)

**Path Parameters:**
- `reserva_id` (integer): ID de la reserva

**Request Body (todos los campos opcionales):**
```json
{
  "fecha_entrada": "date (opcional)",
  "fecha_salida": "date (opcional)",
  "numero_huespedes": "integer (opcional)",
  "estado": "string (opcional: pendiente, confirmada, cancelada, completada)",
  "notas": "string (opcional)"
}
```

**Response 200:** Reserva actualizada (mismo formato que 3.4)

**Errores:**
- `400`: Habitación no disponible en las nuevas fechas
- `401`: No autenticado
- `403`: No tiene permiso para modificar esta reserva
- `404`: Reserva no encontrada

---

### 3.6. Cancelar Reserva
**POST** `/reservas/{reserva_id}/cancelar`

**Descripción:** Cancela una reserva existente.

**Autenticación:** Requerida (Cliente puede cancelar sus propias reservas, Administrador puede cancelar cualquiera)

**Path Parameters:**
- `reserva_id` (integer): ID de la reserva

**Response 200:**
```json
{
  "id": 1,
  "estado": "cancelada",
  ...
}
```

**Errores:**
- `400`: La reserva ya está cancelada
- `401`: No autenticado
- `403`: No tiene permiso para cancelar esta reserva
- `404`: Reserva no encontrada

---

## 4. Módulo de Pagos

### 4.1. Crear Pago
**POST** `/pagos`

**Descripción:** Crea un pago para una reserva específica.

**Autenticación:** Requerida

**Request Body:**
```json
{
  "reserva_id": "integer",
  "metodo_pago": "string (tarjeta_credito | tarjeta_debito | efectivo | transferencia)"
}
```

**Response 201:**
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

**Errores:**
- `400`: Ya existe un pago para esta reserva
- `401`: No autenticado
- `403`: No tiene permiso para crear un pago para esta reserva
- `404`: Reserva no encontrada
- `422`: Datos de validación inválidos

---

### 4.2. Listar Todos los Pagos
**GET** `/pagos`

**Descripción:** Obtiene todos los pagos del sistema (solo administradores).

**Autenticación:** Requerida (Administrador)

**Query Parameters:**
- `skip` (integer, opcional): Número de registros a omitir (default: 0)
- `limit` (integer, opcional): Número máximo de registros (default: 100, máx: 100)

**Response 200:**
```json
[
  {
    "id": 1,
    "reserva_id": 1,
    "monto": 200.00,
    "metodo_pago": "tarjeta_credito",
    "estado": "pendiente",
    "numero_transaccion": "uuid",
    "fecha_pago": null,
    "fecha_creacion": "2024-01-25T12:00:00"
  }
]
```

---

### 4.3. Obtener Pago por Reserva
**GET** `/pagos/reserva/{reserva_id}`

**Descripción:** Obtiene el pago asociado a una reserva específica.

**Autenticación:** Requerida

**Path Parameters:**
- `reserva_id` (integer): ID de la reserva

**Response 200:**
```json
{
  "id": 1,
  "reserva_id": 1,
  "monto": 200.00,
  "metodo_pago": "tarjeta_credito",
  "estado": "pendiente",
  "numero_transaccion": "uuid",
  "fecha_pago": null,
  "fecha_creacion": "2024-01-25T12:00:00"
}
```

**Errores:**
- `401`: No autenticado
- `403`: No tiene permiso para ver este pago
- `404`: No se encontró pago para esta reserva

---

### 4.4. Obtener Pago por ID
**GET** `/pagos/{pago_id}`

**Descripción:** Obtiene los detalles de un pago específico.

**Autenticación:** Requerida (Administrador)

**Path Parameters:**
- `pago_id` (integer): ID del pago

**Response 200:** Mismo formato que 4.3

**Errores:**
- `401`: No autenticado
- `403`: No es administrador
- `404`: Pago no encontrado

---

### 4.5. Procesar Pago
**POST** `/pagos/{pago_id}/procesar`

**Descripción:** Marca un pago como completado y actualiza el estado de la reserva a "confirmada".

**Autenticación:** Requerida (Administrador)

**Path Parameters:**
- `pago_id` (integer): ID del pago

**Response 200:**
```json
{
  "id": 1,
  "estado": "completado",
  "fecha_pago": "2024-01-25T12:30:00",
  ...
}
```

**Errores:**
- `400`: El pago ya fue procesado
- `401`: No autenticado
- `403`: No es administrador
- `404`: Pago no encontrado

---

### 4.6. Actualizar Pago
**PUT** `/pagos/{pago_id}`

**Descripción:** Actualiza los datos de un pago existente.

**Autenticación:** Requerida (Administrador)

**Path Parameters:**
- `pago_id` (integer): ID del pago

**Request Body (todos los campos opcionales):**
```json
{
  "estado": "string (opcional: pendiente | completado | rechazado | reembolsado)",
  "numero_transaccion": "string (opcional)"
}
```

**Response 200:** Pago actualizado

**Errores:**
- `401`: No autenticado
- `403`: No es administrador
- `404`: Pago no encontrado

---

### 4.7. Reembolsar Pago
**POST** `/pagos/{pago_id}/reembolsar`

**Descripción:** Reembolsa un pago completado y cancela la reserva asociada.

**Autenticación:** Requerida (Administrador)

**Path Parameters:**
- `pago_id` (integer): ID del pago

**Response 200:**
```json
{
  "id": 1,
  "estado": "reembolsado",
  ...
}
```

**Errores:**
- `400`: Solo se pueden reembolsar pagos completados
- `401`: No autenticado
- `403`: No es administrador
- `404`: Pago no encontrado

---

## Estados y Enums

### Estados de Reserva
- `pendiente`: Reserva creada, esperando pago
- `confirmada`: Pago completado, reserva confirmada
- `cancelada`: Reserva cancelada
- `completada`: Reserva completada (check-out realizado)

### Estados de Pago
- `pendiente`: Pago creado, esperando procesamiento
- `completado`: Pago procesado exitosamente
- `rechazado`: Pago rechazado
- `reembolsado`: Pago reembolsado

### Métodos de Pago
- `tarjeta_credito`
- `tarjeta_debito`
- `efectivo`
- `transferencia`

---

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Solicitud inválida
- `401 Unauthorized`: No autenticado o token inválido
- `403 Forbidden`: No tiene permisos para la operación
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación de datos

---

## Notas Importantes

1. **Tokens JWT**: Los tokens expiran después del tiempo configurado en `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 minutos)

2. **Paginación**: Todos los endpoints de listado soportan paginación con `skip` y `limit`

3. **Validación de Fechas**: 
   - La fecha de entrada debe ser anterior a la fecha de salida
   - Las fechas deben estar en formato ISO 8601 (YYYY-MM-DD)

4. **Permisos**:
   - Los clientes solo pueden ver/modificar sus propias reservas y pagos
   - Los administradores tienen acceso completo a todos los recursos

5. **Cálculo de Precios**: El precio total se calcula automáticamente como: `precio_por_noche × número_de_noches`
