-- =====================================================
-- Royal Palm Hotel - Base de Datos
-- =====================================================

-- =====================================================
-- Tabla: tipos_habitacion
-- =====================================================
CREATE TABLE IF NOT EXISTS tipos_habitacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    capacidad_maxima INTEGER NOT NULL,
    precio_base NUMERIC(10, 2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tipos_habitacion_codigo ON tipos_habitacion(codigo);
CREATE INDEX IF NOT EXISTS idx_tipos_habitacion_activo ON tipos_habitacion(activo);

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
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

-- =====================================================
-- Tabla: habitaciones
-- =====================================================
CREATE TABLE IF NOT EXISTS habitaciones (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) UNIQUE NOT NULL,
    tipo_habitacion_id INTEGER NOT NULL REFERENCES tipos_habitacion(id) ON DELETE RESTRICT,
    descripcion TEXT,
    capacidad INTEGER NOT NULL,
    precio_por_noche NUMERIC(10, 2) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE,
    imagen_url VARCHAR(500),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_habitacion_tipo FOREIGN KEY (tipo_habitacion_id) REFERENCES tipos_habitacion(id)
);

CREATE INDEX IF NOT EXISTS idx_habitaciones_numero ON habitaciones(numero);
CREATE INDEX IF NOT EXISTS idx_habitaciones_tipo ON habitaciones(tipo_habitacion_id);
CREATE INDEX IF NOT EXISTS idx_habitaciones_disponible ON habitaciones(disponible);

-- =====================================================
-- Tabla: reservas
-- =====================================================
CREATE TYPE estado_reserva AS ENUM ('pendiente', 'confirmada', 'cancelada', 'completada');

CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    habitacion_id INTEGER NOT NULL REFERENCES habitaciones(id) ON DELETE RESTRICT,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    numero_huespedes INTEGER NOT NULL,
    precio_total NUMERIC(10, 2) NOT NULL,
    estado estado_reserva DEFAULT 'pendiente',
    notas VARCHAR(500),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fechas_reserva CHECK (fecha_salida > fecha_entrada),
    CONSTRAINT chk_huespedes_positivos CHECK (numero_huespedes > 0)
);

CREATE INDEX IF NOT EXISTS idx_reservas_usuario ON reservas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_reservas_habitacion ON reservas(habitacion_id);
CREATE INDEX IF NOT EXISTS idx_reservas_fechas ON reservas(fecha_entrada, fecha_salida);
CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado);

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
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_monto_positivo CHECK (monto > 0)
);

CREATE INDEX IF NOT EXISTS idx_pagos_reserva ON pagos(reserva_id);
CREATE INDEX IF NOT EXISTS idx_pagos_transaccion ON pagos(numero_transaccion);
CREATE INDEX IF NOT EXISTS idx_pagos_estado ON pagos(estado);

-- =====================================================
-- Tabla: auditoria
-- =====================================================
CREATE TYPE accion_auditoria AS ENUM (
    'CREATE', 'UPDATE', 'DELETE',
    'LOGIN', 'LOGOUT',
    'RESERVA_CREATE', 'RESERVA_CANCEL', 'RESERVA_CONFIRM',
    'PAGO_PROCESS', 'PAGO_REFUND'
);

CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(100) NOT NULL,
    registro_id INTEGER,
    accion accion_auditoria NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT
);

CREATE INDEX IF NOT EXISTS idx_auditoria_tabla ON auditoria(tabla_afectada);
CREATE INDEX IF NOT EXISTS idx_auditoria_registro ON auditoria(registro_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON auditoria(accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha_accion);

-- =====================================================
-- Función para registrar auditoría
-- =====================================================
CREATE OR REPLACE FUNCTION registrar_auditoria(
    p_tabla VARCHAR(100),
    p_registro_id INTEGER,
    p_accion accion_auditoria,
    p_usuario_id INTEGER DEFAULT NULL,
    p_datos_anteriores JSONB DEFAULT NULL,
    p_datos_nuevos JSONB DEFAULT NULL,
    p_observaciones TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO auditoria (
        tabla_afectada,
        registro_id,
        accion,
        usuario_id,
        datos_anteriores,
        datos_nuevos,
        observaciones,
        fecha_accion
    ) VALUES (
        p_tabla,
        p_registro_id,
        p_accion,
        p_usuario_id,
        p_datos_anteriores,
        p_datos_nuevos,
        p_observaciones,
        CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Triggers fecha_actualizacion
-- =====================================================
CREATE OR REPLACE FUNCTION update_fecha_actualizacion_tipos_habitacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_tipos_habitacion
BEFORE UPDATE ON tipos_habitacion
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_tipos_habitacion();

CREATE OR REPLACE FUNCTION update_fecha_actualizacion_usuarios()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_usuarios
BEFORE UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_usuarios();

CREATE OR REPLACE FUNCTION update_fecha_actualizacion_habitaciones()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_habitaciones
BEFORE UPDATE ON habitaciones
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_habitaciones();

CREATE OR REPLACE FUNCTION update_fecha_actualizacion_reservas()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_reservas
BEFORE UPDATE ON reservas
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_reservas();

CREATE OR REPLACE FUNCTION update_fecha_actualizacion_pagos()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_pagos
BEFORE UPDATE ON pagos
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion_pagos();

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

CREATE OR REPLACE FUNCTION sp_crear_habitacion(
    p_numero VARCHAR(10),
    p_tipo_habitacion_id INTEGER,
    p_descripcion TEXT,
    p_capacidad INTEGER,
    p_precio_por_noche NUMERIC,
    p_disponible BOOLEAN DEFAULT TRUE,
    p_imagen_url VARCHAR(500) DEFAULT NULL,
    p_usuario_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    numero VARCHAR(10),
    tipo_habitacion_id INTEGER,
    descripcion TEXT,
    capacidad INTEGER,
    precio_por_noche NUMERIC,
    disponible BOOLEAN,
    imagen_url VARCHAR(500),
    fecha_creacion TIMESTAMP
) AS $$
DECLARE
    v_habitacion_id INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM habitaciones WHERE habitaciones.numero = p_numero) THEN
        RAISE EXCEPTION 'Ya existe una habitación con el número %', p_numero;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM tipos_habitacion WHERE tipos_habitacion.id = p_tipo_habitacion_id AND tipos_habitacion.activo = TRUE) THEN
        RAISE EXCEPTION 'El tipo de habitación especificado no existe o no está activo';
    END IF;
    IF p_capacidad <= 0 THEN
        RAISE EXCEPTION 'La capacidad debe ser mayor a 0';
    END IF;
    IF p_precio_por_noche <= 0 THEN
        RAISE EXCEPTION 'El precio por noche debe ser mayor a 0';
    END IF;
    INSERT INTO habitaciones (
        numero, tipo_habitacion_id, descripcion, capacidad,
        precio_por_noche, disponible, imagen_url
    ) VALUES (
        p_numero, p_tipo_habitacion_id, p_descripcion, p_capacidad,
        p_precio_por_noche, p_disponible, p_imagen_url
    ) RETURNING habitaciones.id INTO v_habitacion_id;
    PERFORM registrar_auditoria(
        'habitaciones',
        v_habitacion_id,
        'CREATE',
        p_usuario_id,
        NULL,
        row_to_json(h.*)::JSONB
    ) FROM habitaciones h WHERE h.id = v_habitacion_id;
    RETURN QUERY
    SELECT h.id, h.numero, h.tipo_habitacion_id, h.descripcion,
           h.capacidad, h.precio_por_noche, h.disponible, h.imagen_url, h.fecha_creacion
    FROM habitaciones h
    WHERE h.id = v_habitacion_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_buscar_habitaciones_disponibles(
    p_fecha_entrada DATE,
    p_fecha_salida DATE,
    p_capacidad INTEGER DEFAULT NULL,
    p_tipo_habitacion_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    numero VARCHAR(10),
    tipo_habitacion_id INTEGER,
    tipo_nombre VARCHAR(100),
    descripcion TEXT,
    capacidad INTEGER,
    precio_por_noche NUMERIC,
    disponible BOOLEAN,
    imagen_url VARCHAR(500)
) AS $$
BEGIN
    IF p_fecha_entrada >= p_fecha_salida THEN
        RAISE EXCEPTION 'La fecha de entrada debe ser anterior a la fecha de salida';
    END IF;
    RETURN QUERY
    SELECT
        h.id,
        h.numero,
        h.tipo_habitacion_id,
        th.nombre AS tipo_nombre,
        h.descripcion,
        h.capacidad,
        h.precio_por_noche,
        h.disponible,
        h.imagen_url
    FROM habitaciones h
    INNER JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
    WHERE h.disponible = TRUE
        AND h.id NOT IN (
            SELECT DISTINCT r.habitacion_id
            FROM reservas r
            WHERE r.estado != 'cancelada'
                AND (
                    (r.fecha_entrada <= p_fecha_entrada AND r.fecha_salida > p_fecha_entrada)
                    OR (r.fecha_entrada < p_fecha_salida AND r.fecha_salida >= p_fecha_salida)
                    OR (r.fecha_entrada >= p_fecha_entrada AND r.fecha_salida <= p_fecha_salida)
                )
        )
        AND (p_capacidad IS NULL OR h.capacidad >= p_capacidad)
        AND (p_tipo_habitacion_id IS NULL OR h.tipo_habitacion_id = p_tipo_habitacion_id)
    ORDER BY h.precio_por_noche ASC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_crear_reserva(
    p_usuario_id INTEGER,
    p_habitacion_id INTEGER,
    p_fecha_entrada DATE,
    p_fecha_salida DATE,
    p_numero_huespedes INTEGER,
    p_notas VARCHAR(500) DEFAULT NULL,
    p_usuario_auditoria_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    usuario_id INTEGER,
    habitacion_id INTEGER,
    fecha_entrada DATE,
    fecha_salida DATE,
    numero_huespedes INTEGER,
    precio_total NUMERIC,
    estado estado_reserva,
    notas VARCHAR(500),
    fecha_creacion TIMESTAMP
) AS $$
DECLARE
    v_reserva_id INTEGER;
    v_precio_noche NUMERIC;
    v_numero_noches INTEGER;
    v_precio_total NUMERIC;
    v_capacidad INTEGER;
BEGIN
    IF p_fecha_entrada >= p_fecha_salida THEN
        RAISE EXCEPTION 'La fecha de entrada debe ser anterior a la fecha de salida';
    END IF;
    SELECT h.precio_por_noche, h.capacidad INTO v_precio_noche, v_capacidad
    FROM habitaciones h
    WHERE h.id = p_habitacion_id AND h.disponible = TRUE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'La habitación no existe o no está disponible';
    END IF;
    IF p_numero_huespedes > v_capacidad THEN
        RAISE EXCEPTION 'El número de huéspedes excede la capacidad de la habitación';
    END IF;
    IF EXISTS (
        SELECT 1 FROM reservas r
        WHERE r.habitacion_id = p_habitacion_id
            AND r.estado != 'cancelada'
            AND (
                (r.fecha_entrada <= p_fecha_entrada AND r.fecha_salida > p_fecha_entrada)
                OR (r.fecha_entrada < p_fecha_salida AND r.fecha_salida >= p_fecha_salida)
                OR (r.fecha_entrada >= p_fecha_entrada AND r.fecha_salida <= p_fecha_salida)
            )
    ) THEN
        RAISE EXCEPTION 'La habitación no está disponible en las fechas especificadas';
    END IF;
    v_numero_noches := p_fecha_salida - p_fecha_entrada;
    v_precio_total := v_precio_noche * v_numero_noches;
    INSERT INTO reservas (
        usuario_id, habitacion_id, fecha_entrada, fecha_salida,
        numero_huespedes, precio_total, notas
    ) VALUES (
        p_usuario_id, p_habitacion_id, p_fecha_entrada, p_fecha_salida,
        p_numero_huespedes, v_precio_total, p_notas
    ) RETURNING reservas.id INTO v_reserva_id;
    PERFORM registrar_auditoria(
        'reservas',
        v_reserva_id,
        'RESERVA_CREATE',
        p_usuario_auditoria_id,
        NULL,
        row_to_json(r.*)::JSONB,
        'Reserva creada'
    ) FROM reservas r WHERE r.id = v_reserva_id;
    RETURN QUERY
    SELECT r.id, r.usuario_id, r.habitacion_id, r.fecha_entrada, r.fecha_salida,
           r.numero_huespedes, r.precio_total, r.estado, r.notas, r.fecha_creacion
    FROM reservas r
    WHERE r.id = v_reserva_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_procesar_pago(
    p_reserva_id INTEGER,
    p_monto NUMERIC,
    p_metodo_pago metodo_pago,
    p_numero_transaccion VARCHAR(100) DEFAULT NULL,
    p_usuario_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    reserva_id INTEGER,
    monto NUMERIC,
    metodo_pago metodo_pago,
    estado estado_pago,
    numero_transaccion VARCHAR(100),
    fecha_pago TIMESTAMP
) AS $$
DECLARE
    v_pago_id INTEGER;
    v_precio_reserva NUMERIC;
BEGIN
    SELECT r.precio_total INTO v_precio_reserva
    FROM reservas r
    WHERE r.id = p_reserva_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'La reserva no existe';
    END IF;
    IF p_monto <= 0 THEN
        RAISE EXCEPTION 'El monto debe ser mayor a 0';
    END IF;
    IF EXISTS (SELECT 1 FROM pagos p WHERE p.reserva_id = p_reserva_id) THEN
        RAISE EXCEPTION 'Ya existe un pago para esta reserva';
    END IF;
    INSERT INTO pagos (
        reserva_id, monto, metodo_pago, estado, numero_transaccion, fecha_pago
    ) VALUES (
        p_reserva_id, p_monto, p_metodo_pago, 'completado', p_numero_transaccion, CURRENT_TIMESTAMP
    ) RETURNING pagos.id INTO v_pago_id;
    UPDATE reservas r
    SET estado = 'confirmada'
    WHERE r.id = p_reserva_id;
    PERFORM registrar_auditoria(
        'pagos',
        v_pago_id,
        'PAGO_PROCESS',
        p_usuario_id,
        NULL,
        row_to_json(p.*)::JSONB,
        'Pago procesado exitosamente'
    ) FROM pagos p WHERE p.id = v_pago_id;
    RETURN QUERY
    SELECT p.id, p.reserva_id, p.monto, p.metodo_pago, p.estado,
           p.numero_transaccion, p.fecha_pago
    FROM pagos p
    WHERE p.id = v_pago_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_obtener_estadisticas_reservas(
    p_fecha_inicio DATE DEFAULT NULL,
    p_fecha_fin DATE DEFAULT NULL
)
RETURNS TABLE (
    total_reservas BIGINT,
    reservas_pendientes BIGINT,
    reservas_confirmadas BIGINT,
    reservas_canceladas BIGINT,
    reservas_completadas BIGINT,
    ingresos_totales NUMERIC,
    promedio_reserva NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_reservas,
        COUNT(*) FILTER (WHERE r.estado = 'pendiente')::BIGINT AS reservas_pendientes,
        COUNT(*) FILTER (WHERE r.estado = 'confirmada')::BIGINT AS reservas_confirmadas,
        COUNT(*) FILTER (WHERE r.estado = 'cancelada')::BIGINT AS reservas_canceladas,
        COUNT(*) FILTER (WHERE r.estado = 'completada')::BIGINT AS reservas_completadas,
        COALESCE(SUM(r.precio_total) FILTER (WHERE r.estado != 'cancelada'), 0) AS ingresos_totales,
        COALESCE(AVG(r.precio_total) FILTER (WHERE r.estado != 'cancelada'), 0) AS promedio_reserva
    FROM reservas r
    WHERE (p_fecha_inicio IS NULL OR r.fecha_creacion >= p_fecha_inicio)
        AND (p_fecha_fin IS NULL OR r.fecha_creacion <= p_fecha_fin);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Vistas
-- =====================================================
CREATE OR REPLACE VIEW vista_reservas_completas AS
SELECT
    r.id,
    r.fecha_entrada,
    r.fecha_salida,
    r.numero_huespedes,
    r.precio_total,
    r.estado,
    r.fecha_creacion,
    u.id AS usuario_id,
    u.nombre || ' ' || u.apellido AS nombre_cliente,
    u.email AS email_cliente,
    h.id AS habitacion_id,
    h.numero AS numero_habitacion,
    th.nombre AS tipo_habitacion,
    th.codigo AS codigo_tipo_habitacion,
    p.estado AS estado_pago,
    p.monto AS monto_pago,
    p.metodo_pago AS metodo_pago
FROM reservas r
JOIN usuarios u ON r.usuario_id = u.id
JOIN habitaciones h ON r.habitacion_id = h.id
JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
LEFT JOIN pagos p ON r.id = p.reserva_id;

CREATE OR REPLACE VIEW vista_habitaciones_disponibles AS
SELECT
    h.id,
    h.numero,
    h.tipo_habitacion_id,
    th.codigo AS codigo_tipo,
    th.nombre AS tipo_nombre,
    th.descripcion AS tipo_descripcion,
    h.descripcion AS habitacion_descripcion,
    h.capacidad,
    h.precio_por_noche,
    h.disponible,
    h.imagen_url,
    COUNT(r.id) FILTER (WHERE r.estado != 'cancelada' AND r.fecha_salida >= CURRENT_DATE) AS total_reservas_activas
FROM habitaciones h
INNER JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
LEFT JOIN reservas r ON h.id = r.habitacion_id
GROUP BY h.id, h.numero, h.tipo_habitacion_id, th.codigo, th.nombre, th.descripcion,
         h.descripcion, h.capacidad, h.precio_por_noche, h.disponible, h.imagen_url;

-- =====================================================
-- Insertar datos iniciales: Tipos de habitación
-- =====================================================
INSERT INTO tipos_habitacion (codigo, nombre, descripcion, capacidad_maxima, precio_base) VALUES
    ('IND', 'Individual', 'Habitación individual con cama de tamaño completo', 1, 50.00),
    ('DBL', 'Doble', 'Habitación doble con dos camas individuales', 2, 75.00),
    ('SUITE', 'Suite', 'Suite de lujo con sala de estar', 4, 150.00),
    ('FAM', 'Familiar', 'Habitación familiar con capacidad para 4 personas', 4, 120.00)
ON CONFLICT (codigo) DO NOTHING;
