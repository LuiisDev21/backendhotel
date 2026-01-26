-- =====================================================
-- Sistema de Reservas de Hotel - Script SQL
-- Base de datos: PostgreSQL
-- =====================================================

-- Crear base de datos (ejecutar como superusuario)
-- CREATE DATABASE hotel_db;
-- \c hotel_db;

-- =====================================================
-- Tabla: usuarios
-- =====================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    hashed_password VARCHAR(255) NOT NULL,
    es_administrador BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);

-- =====================================================
-- Tabla: habitaciones
-- =====================================================
CREATE TABLE IF NOT EXISTS habitaciones (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    capacidad INTEGER NOT NULL,
    precio_por_noche NUMERIC(10, 2) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_habitaciones_numero ON habitaciones(numero);

-- =====================================================
-- Tabla: reservas
-- =====================================================
CREATE TYPE estado_reserva AS ENUM ('pendiente', 'confirmada', 'cancelada', 'completada');

CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    habitacion_id INTEGER NOT NULL REFERENCES habitaciones(id) ON DELETE CASCADE,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    numero_huespedes INTEGER NOT NULL,
    precio_total NUMERIC(10, 2) NOT NULL,
    estado estado_reserva DEFAULT 'pendiente',
    notas VARCHAR(500),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reservas_usuario ON reservas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_reservas_habitacion ON reservas(habitacion_id);
CREATE INDEX IF NOT EXISTS idx_reservas_fechas ON reservas(fecha_entrada, fecha_salida);

-- =====================================================
-- Tabla: pagos
-- =====================================================
CREATE TYPE metodo_pago AS ENUM ('tarjeta_credito', 'tarjeta_debito', 'efectivo', 'transferencia');
CREATE TYPE estado_pago AS ENUM ('pendiente', 'completado', 'rechazado', 'reembolsado');

CREATE TABLE IF NOT EXISTS pagos (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER UNIQUE NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
    monto NUMERIC(10, 2) NOT NULL,
    metodo_pago metodo_pago NOT NULL,
    estado estado_pago DEFAULT 'pendiente',
    numero_transaccion VARCHAR(100) UNIQUE,
    fecha_pago TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pagos_reserva ON pagos(reserva_id);
CREATE INDEX IF NOT EXISTS idx_pagos_transaccion ON pagos(numero_transaccion);

-- =====================================================
-- Trigger para actualizar fecha_actualizacion en reservas
-- =====================================================
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_actualizacion
BEFORE UPDATE ON reservas
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion();

-- =====================================================
-- Datos de ejemplo (opcional)
-- =====================================================

-- Insertar usuario administrador de ejemplo
-- NOTA: Para generar el hash de la contraseña, ejecuta:
-- python scripts/create_admin.py <tu_contraseña>
-- Luego copia el hash generado y úsalo en el INSERT siguiente
-- 
-- Ejemplo con contraseña "admin123":
-- INSERT INTO usuarios (email, nombre, apellido, hashed_password, es_administrador)
-- VALUES (
--     'admin@hotel.com',
--     'Administrador',
--     'Sistema',
--     '<hash_generado_por_el_script>',
--     TRUE
-- ) ON CONFLICT (email) DO NOTHING;

-- Insertar habitaciones de ejemplo
INSERT INTO habitaciones (numero, tipo, descripcion, capacidad, precio_por_noche, disponible)
VALUES
    ('101', 'Individual', 'Habitación individual con cama de tamaño completo', 1, 50.00, TRUE),
    ('102', 'Doble', 'Habitación doble con dos camas individuales', 2, 75.00, TRUE),
    ('103', 'Suite', 'Suite de lujo con sala de estar', 4, 150.00, TRUE),
    ('201', 'Individual', 'Habitación individual con vista al jardín', 1, 55.00, TRUE),
    ('202', 'Doble', 'Habitación doble con balcón', 2, 80.00, TRUE),
    ('203', 'Familiar', 'Habitación familiar con capacidad para 4 personas', 4, 120.00, TRUE)
ON CONFLICT (numero) DO NOTHING;

-- =====================================================
-- Vistas útiles (opcional)
-- =====================================================

-- Vista de reservas con información completa
CREATE OR REPLACE VIEW vista_reservas_completas AS
SELECT 
    r.id,
    r.fecha_entrada,
    r.fecha_salida,
    r.numero_huespedes,
    r.precio_total,
    r.estado,
    u.nombre || ' ' || u.apellido AS nombre_cliente,
    u.email AS email_cliente,
    h.numero AS numero_habitacion,
    h.tipo AS tipo_habitacion,
    p.estado AS estado_pago,
    p.monto AS monto_pago
FROM reservas r
JOIN usuarios u ON r.usuario_id = u.id
JOIN habitaciones h ON r.habitacion_id = h.id
LEFT JOIN pagos p ON r.id = p.reserva_id;

-- Vista de habitaciones disponibles
CREATE OR REPLACE VIEW vista_habitaciones_disponibles AS
SELECT 
    h.id,
    h.numero,
    h.tipo,
    h.descripcion,
    h.capacidad,
    h.precio_por_noche,
    h.disponible,
    COUNT(r.id) AS total_reservas
FROM habitaciones h
LEFT JOIN reservas r ON h.id = r.habitacion_id 
    AND r.estado != 'cancelada'
    AND r.fecha_salida >= CURRENT_DATE
GROUP BY h.id, h.numero, h.tipo, h.descripcion, h.capacidad, h.precio_por_noche, h.disponible;

-- =====================================================
-- Comentarios finales
-- =====================================================
-- Para ejecutar este script:
-- 1. Asegúrate de tener PostgreSQL instalado
-- 2. Crea la base de datos: CREATE DATABASE hotel_db;
-- 3. Ejecuta este script: psql -U usuario -d hotel_db -f database.sql
-- 4. O ejecuta línea por línea en psql
