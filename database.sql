-- =====================================================
-- Royal Palm Hotel — Base de Datos
-- =====================================================

-- =====================================================
-- Extensiones
-- =====================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

SET timezone = 'America/Managua';

-- =====================================================
-- Tabla: tipos_habitacion
-- =====================================================
CREATE TABLE IF NOT EXISTS tipos_habitacion (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(50)    UNIQUE NOT NULL,
    nombre      VARCHAR(100)   NOT NULL,
    descripcion TEXT,
    capacidad_maxima INTEGER   NOT NULL,
    precio_base NUMERIC(12, 2) NOT NULL,
    activo      BOOLEAN        DEFAULT TRUE,
    fecha_creacion     TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_precio_base_positivo  CHECK (precio_base > 0),
    CONSTRAINT chk_capacidad_razonable   CHECK (capacidad_maxima BETWEEN 1 AND 20)
);

COMMENT ON TABLE  tipos_habitacion IS 'Catálogo de tipos de habitación con sus características y precio base.';
COMMENT ON COLUMN tipos_habitacion.precio_base IS 'Precio base por noche para este tipo de habitación.';

CREATE INDEX IF NOT EXISTS idx_tipos_habitacion_codigo ON tipos_habitacion(codigo);
CREATE INDEX IF NOT EXISTS idx_tipos_habitacion_activo ON tipos_habitacion(activo);

-- =====================================================
-- Tabla: roles  (RBAC)
-- =====================================================
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN     DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE roles IS 'Roles del sistema para control de acceso basado en roles (RBAC).';

-- =====================================================
-- Tabla: permisos  (RBAC)
-- =====================================================
CREATE TABLE IF NOT EXISTS permisos (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(100) UNIQUE NOT NULL,
    nombre      VARCHAR(150) NOT NULL,
    modulo      VARCHAR(50)  NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE  permisos IS 'Permisos granulares del sistema. Formato de código: modulo.accion (ej: reservas.crear).';

-- =====================================================
-- Tabla: rol_permisos  (RBAC — N:M)
-- =====================================================
CREATE TABLE IF NOT EXISTS rol_permisos (
    rol_id     INTEGER NOT NULL REFERENCES roles(id)    ON DELETE CASCADE,
    permiso_id INTEGER NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id),
    fecha_asignacion TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rol_permisos_rol     ON rol_permisos(rol_id);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_permiso ON rol_permisos(permiso_id);

-- =====================================================
-- Tabla: usuarios
-- =====================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id                  SERIAL PRIMARY KEY,
    email               VARCHAR(255) UNIQUE NOT NULL,
    nombre              VARCHAR(100) NOT NULL,
    apellido            VARCHAR(100) NOT NULL,
    telefono            VARCHAR(20),
    hashed_password     VARCHAR(255) NOT NULL,
    activo              BOOLEAN      DEFAULT TRUE,
    email_verificado    BOOLEAN      DEFAULT FALSE,
    intentos_fallidos   INTEGER      DEFAULT 0,
    bloqueado_hasta     TIMESTAMPTZ,
    fecha_ultimo_login  TIMESTAMPTZ,
    fecha_creacion      TIMESTAMPTZ  DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT chk_email_formato
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_password_longitud
        CHECK (LENGTH(hashed_password) >= 60),
    CONSTRAINT chk_telefono_formato
        CHECK (telefono IS NULL OR telefono ~ '^\+?[0-9\s\-\(\)]{7,20}$')
);

COMMENT ON TABLE  usuarios IS 'Usuarios del sistema: clientes, recepcionistas y administradores.';
COMMENT ON COLUMN usuarios.hashed_password     IS 'Hash de contraseña con bcrypt o argon2. NUNCA almacenar texto plano.';
COMMENT ON COLUMN usuarios.intentos_fallidos   IS 'Contador de intentos de login fallidos consecutivos. Se resetea al login exitoso.';
COMMENT ON COLUMN usuarios.bloqueado_hasta     IS 'Si es una fecha futura, el usuario no puede iniciar sesión hasta esa hora.';

CREATE INDEX IF NOT EXISTS idx_usuarios_email  ON usuarios(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

-- =====================================================
-- Tabla: usuario_roles  (RBAC — N:M)
-- =====================================================
CREATE TABLE IF NOT EXISTS usuario_roles (
    usuario_id       INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    rol_id           INTEGER NOT NULL REFERENCES roles(id)    ON DELETE CASCADE,
    PRIMARY KEY (usuario_id, rol_id),
    asignado_por     INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_asignacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_expiracion TIMESTAMPTZ
);

COMMENT ON COLUMN usuario_roles.fecha_expiracion IS 'Permite roles temporales. NULL = sin expiración.';

CREATE INDEX IF NOT EXISTS idx_usuario_roles_usuario ON usuario_roles(usuario_id);

-- =====================================================
-- Tabla: sesiones_usuario
-- =====================================================
CREATE TABLE IF NOT EXISTS sesiones_usuario (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id          INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    refresh_token_hash  VARCHAR(255) NOT NULL UNIQUE,
    ip_address          INET,
    user_agent          TEXT,
    dispositivo         VARCHAR(100),
    activa              BOOLEAN     DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ DEFAULT NOW(),
    fecha_expiracion    TIMESTAMPTZ NOT NULL,
    fecha_ultimo_uso    TIMESTAMPTZ DEFAULT NOW(),
    revocada_en         TIMESTAMPTZ,
    revocada_por        INTEGER REFERENCES usuarios(id) ON DELETE SET NULL
);

COMMENT ON TABLE  sesiones_usuario IS 'Sesiones activas. Permite revocar accesos comprometidos sin esperar expiración del JWT.';
COMMENT ON COLUMN sesiones_usuario.refresh_token_hash IS 'Hash SHA-256 del refresh token. Nunca almacenar el token en texto plano.';

CREATE INDEX IF NOT EXISTS idx_sesiones_usuario ON sesiones_usuario(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sesiones_token   ON sesiones_usuario(refresh_token_hash);
CREATE INDEX IF NOT EXISTS idx_sesiones_activa  ON sesiones_usuario(activa, fecha_expiracion);

-- =====================================================
-- Tabla: intentos_autenticacion
-- =====================================================
CREATE TABLE IF NOT EXISTS intentos_autenticacion (
    id             BIGSERIAL PRIMARY KEY,
    email          VARCHAR(255) NOT NULL,
    ip_address     INET,
    exitoso        BOOLEAN      NOT NULL,
    motivo_fallo   VARCHAR(100),
    fecha_intento  TIMESTAMPTZ  DEFAULT NOW()
);

COMMENT ON TABLE intentos_autenticacion IS 'Registro de intentos de login para detección de fuerza bruta.';

CREATE INDEX IF NOT EXISTS idx_intentos_email ON intentos_autenticacion(email, fecha_intento DESC);
CREATE INDEX IF NOT EXISTS idx_intentos_ip    ON intentos_autenticacion(ip_address, fecha_intento DESC);

-- =====================================================
-- Tabla: habitaciones
-- =====================================================
CREATE TABLE IF NOT EXISTS habitaciones (
    id                  SERIAL PRIMARY KEY,
    numero              VARCHAR(10)    UNIQUE NOT NULL,
    tipo_habitacion_id  INTEGER        NOT NULL,
    descripcion         TEXT,
    capacidad                INTEGER        NOT NULL,
    precio_por_noche         NUMERIC(12, 2) NOT NULL,
    estado                   VARCHAR(20)    DEFAULT 'disponible',
    imagen_url               VARCHAR(500),
    piso                     INTEGER,
    caracteristicas          JSONB,
    fecha_creacion           TIMESTAMPTZ    DEFAULT NOW(),
    fecha_actualizacion      TIMESTAMPTZ    DEFAULT NOW(),
    CONSTRAINT fk_habitacion_tipo FOREIGN KEY (tipo_habitacion_id)
        REFERENCES tipos_habitacion(id) ON DELETE RESTRICT,
    CONSTRAINT chk_estado_habitacion
        CHECK (estado IN ('disponible','ocupada','mantenimiento','limpieza','bloqueada')),
    CONSTRAINT chk_capacidad_positiva    CHECK (capacidad > 0),
    CONSTRAINT chk_precio_noche_positivo CHECK (precio_por_noche > 0)
);

COMMENT ON TABLE  habitaciones IS 'Inventario de habitaciones físicas del hotel.';
COMMENT ON COLUMN habitaciones.estado          IS 'Estado operativo: disponible, ocupada, mantenimiento, limpieza, bloqueada.';
COMMENT ON COLUMN habitaciones.caracteristicas IS 'JSON con amenidades: {"wifi": true, "tv": true, "jacuzzi": false, "vista_mar": true}';

CREATE INDEX IF NOT EXISTS idx_habitaciones_numero ON habitaciones(numero);
CREATE INDEX IF NOT EXISTS idx_habitaciones_tipo   ON habitaciones(tipo_habitacion_id);
CREATE INDEX IF NOT EXISTS idx_habitaciones_estado ON habitaciones(estado);

-- =====================================================
-- Tabla: politicas_cancelacion
-- =====================================================
CREATE TABLE IF NOT EXISTS politicas_cancelacion (
    id                          SERIAL PRIMARY KEY,
    nombre                      VARCHAR(100)   NOT NULL,
    descripcion                 TEXT,
    horas_anticipacion          INTEGER        NOT NULL,
    porcentaje_penalizacion     NUMERIC(5, 2)  DEFAULT 0,
    aplica_a_tipo_habitacion_id INTEGER        REFERENCES tipos_habitacion(id) ON DELETE SET NULL,
    activa                      BOOLEAN        DEFAULT TRUE,
    fecha_creacion              TIMESTAMPTZ    DEFAULT NOW(),
    CONSTRAINT chk_porcentaje_valido CHECK (porcentaje_penalizacion BETWEEN 0 AND 100)
);

COMMENT ON TABLE  politicas_cancelacion IS 'Políticas de cancelación con penalizaciones configurables por tipo de habitación.';
COMMENT ON COLUMN politicas_cancelacion.horas_anticipacion      IS 'Horas antes del check-in para cancelar sin penalización.';
COMMENT ON COLUMN politicas_cancelacion.porcentaje_penalizacion IS '% del precio total que se cobra como penalización si se cancela fuera del plazo.';

-- Columna politica_cancelacion_id en habitaciones (política por habitación, definida por admin)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'habitaciones' AND column_name = 'politica_cancelacion_id'
    ) THEN
        ALTER TABLE habitaciones
        ADD COLUMN politica_cancelacion_id INTEGER REFERENCES politicas_cancelacion(id) ON DELETE SET NULL;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_habitaciones_politica ON habitaciones(politica_cancelacion_id);

-- =====================================================
-- Catálogo: estado_reserva
-- =====================================================
CREATE TABLE IF NOT EXISTS catalogo_estado_reserva (
    codigo      VARCHAR(50) PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN DEFAULT TRUE
);

INSERT INTO catalogo_estado_reserva (codigo, nombre, descripcion, activo) VALUES
    ('pendiente',  'Pendiente',  'Reserva creada, aún no confirmada.',                  TRUE),
    ('confirmada', 'Confirmada', 'Reserva confirmada y con pago suficiente.',          TRUE),
    ('cancelada',  'Cancelada',  'Reserva cancelada.',                                 TRUE),
    ('completada', 'Completada', 'Estancia completada (check-out realizado).',        TRUE),
    ('no_show',    'No-show',    'El huésped no se presentó.',                         TRUE)
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- Secuencia para código de reserva legible
-- =====================================================
CREATE SEQUENCE IF NOT EXISTS seq_codigo_reserva START 1;

-- =====================================================
-- Tabla: reservas
-- =====================================================
CREATE TABLE IF NOT EXISTS reservas (
    id                          BIGSERIAL PRIMARY KEY,
    usuario_id                  INTEGER        NOT NULL,
    habitacion_id               INTEGER        NOT NULL,
    politica_cancelacion_id     INTEGER,
    codigo_reserva              VARCHAR(20)    UNIQUE NOT NULL
                                    DEFAULT ('RPH-' || TO_CHAR(NOW(), 'YYYY') || '-'
                                             || LPAD(nextval('seq_codigo_reserva')::TEXT, 5, '0')),
    fecha_entrada               DATE           NOT NULL,
    fecha_salida                DATE           NOT NULL,
    numero_huespedes            INTEGER        NOT NULL,
    moneda                      CHAR(3)        NOT NULL DEFAULT 'USD',
    tasa_cambio                 NUMERIC(10, 6) NOT NULL DEFAULT 1.0,
    subtotal                    NUMERIC(12, 2) NOT NULL,
    impuestos                   NUMERIC(12, 2) NOT NULL DEFAULT 0,
    descuentos                  NUMERIC(12, 2) NOT NULL DEFAULT 0,
    otros_cargos                NUMERIC(12, 2) NOT NULL DEFAULT 0,
    precio_total                NUMERIC(12, 2) NOT NULL,
    precio_por_noche_snapshot   NUMERIC(12, 2) NOT NULL,
    estado                      VARCHAR(50)    DEFAULT 'pendiente',
    canal_reserva               VARCHAR(50)    DEFAULT 'web',
    notas                       VARCHAR(1000),
    fecha_creacion              TIMESTAMPTZ    DEFAULT NOW(),
    fecha_actualizacion         TIMESTAMPTZ    DEFAULT NOW(),
    CONSTRAINT fk_reserva_usuario   FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)              ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_habitacion FOREIGN KEY (habitacion_id)
        REFERENCES habitaciones(id)          ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_politica  FOREIGN KEY (politica_cancelacion_id)
        REFERENCES politicas_cancelacion(id) ON DELETE SET NULL,
    CONSTRAINT chk_fechas_reserva        CHECK (fecha_salida > fecha_entrada),
    CONSTRAINT chk_huespedes_positivos   CHECK (numero_huespedes > 0),
    CONSTRAINT chk_precio_total_positivo CHECK (precio_total > 0),
    CONSTRAINT chk_precio_total_desglose CHECK (
        precio_total = subtotal + otros_cargos + impuestos - descuentos
    ),
    CONSTRAINT fk_reserva_estado_catalogo
        FOREIGN KEY (estado) REFERENCES catalogo_estado_reserva(codigo)
);

COMMENT ON TABLE  reservas IS 'Registro central de todas las reservas del hotel.';
COMMENT ON COLUMN reservas.precio_por_noche_snapshot IS 'Precio por noche al momento de crear la reserva. Inmutable aunque cambie el precio del tipo de habitación.';
COMMENT ON COLUMN reservas.codigo_reserva            IS 'Código legible para el cliente. Formato: RPH-YYYY-NNNNN';
COMMENT ON COLUMN reservas.canal_reserva             IS 'Origen de la reserva: web, telefono, agencia, walk-in.';

CREATE INDEX IF NOT EXISTS idx_reservas_usuario       ON reservas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_reservas_habitacion    ON reservas(habitacion_id);
CREATE INDEX IF NOT EXISTS idx_reservas_fechas        ON reservas(fecha_entrada, fecha_salida);
CREATE INDEX IF NOT EXISTS idx_reservas_estado        ON reservas(estado);
CREATE INDEX IF NOT EXISTS idx_reservas_codigo        ON reservas(codigo_reserva);
CREATE INDEX IF NOT EXISTS idx_reservas_disponibilidad
    ON reservas(habitacion_id, fecha_entrada, fecha_salida)
    WHERE estado != 'cancelada';
CREATE INDEX IF NOT EXISTS idx_reservas_activas
    ON reservas(estado, fecha_entrada)
    WHERE estado IN ('pendiente', 'confirmada');

-- =====================================================
-- Tabla: historial_estados_reserva
-- =====================================================
CREATE TABLE IF NOT EXISTS historial_estados_reserva (
    id              BIGSERIAL PRIMARY KEY,
    reserva_id      BIGINT         NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(50),
    estado_nuevo    VARCHAR(50)    NOT NULL,
    motivo          TEXT,
    cambiado_por    INTEGER        REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_cambio    TIMESTAMPTZ    DEFAULT NOW()
);

COMMENT ON TABLE historial_estados_reserva IS 'Trazabilidad completa de todos los cambios de estado de cada reserva.';

ALTER TABLE historial_estados_reserva
    ADD CONSTRAINT fk_historial_estado_anterior_catalogo
        FOREIGN KEY (estado_anterior) REFERENCES catalogo_estado_reserva(codigo);

ALTER TABLE historial_estados_reserva
    ADD CONSTRAINT fk_historial_estado_nuevo_catalogo
        FOREIGN KEY (estado_nuevo) REFERENCES catalogo_estado_reserva(codigo);

CREATE INDEX IF NOT EXISTS idx_historial_reserva ON historial_estados_reserva(reserva_id);
CREATE INDEX IF NOT EXISTS idx_historial_fecha   ON historial_estados_reserva(fecha_cambio DESC);

-- =====================================================
-- Catálogos: pagos
-- =====================================================

CREATE TABLE IF NOT EXISTS catalogo_metodo_pago (
    codigo      VARCHAR(50) PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN DEFAULT TRUE
);

INSERT INTO catalogo_metodo_pago (codigo, nombre, descripcion, activo) VALUES
    ('tarjeta_credito', 'Tarjeta de crédito', 'Pago con tarjeta de crédito.', TRUE),
    ('tarjeta_debito',  'Tarjeta de débito',  'Pago con tarjeta de débito.',  TRUE),
    ('efectivo',        'Efectivo',          'Pago en efectivo.',             TRUE),
    ('transferencia',   'Transferencia',     'Pago mediante transferencia.',  TRUE),
    ('paypal',          'PayPal',            'Pago a través de PayPal.',      TRUE),
    ('cripto',          'Criptomonedas',     'Pago con criptomonedas.',       TRUE)
ON CONFLICT (codigo) DO NOTHING;

CREATE TABLE IF NOT EXISTS catalogo_estado_pago (
    codigo      VARCHAR(50) PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN DEFAULT TRUE
);

INSERT INTO catalogo_estado_pago (codigo, nombre, descripcion, activo) VALUES
    ('pendiente',   'Pendiente',   'Pago registrado pero no completado.',           TRUE),
    ('completado',  'Completado',  'Pago procesado y aplicado.',                    TRUE),
    ('rechazado',   'Rechazado',   'Pago rechazado por el medio de pago.',          TRUE),
    ('reembolsado', 'Reembolsado', 'Pago reembolsado total o parcialmente.',        TRUE),
    ('en_proceso',  'En proceso',  'Pago en proceso de confirmación.',              TRUE),
    ('disputado',   'Disputado',   'Pago en disputa.',                               TRUE)
ON CONFLICT (codigo) DO NOTHING;

CREATE TABLE IF NOT EXISTS catalogo_tipo_transaccion (
    codigo      VARCHAR(50) PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN DEFAULT TRUE
);

INSERT INTO catalogo_tipo_transaccion (codigo, nombre, descripcion, activo) VALUES
    ('cargo',        'Cargo',        'Cargo normal de la reserva.',                  TRUE),
    ('reembolso',    'Reembolso',    'Devolución parcial o total de un cargo.',      TRUE),
    ('deposito',     'Depósito',     'Depósito anticipado.',                         TRUE),
    ('ajuste',       'Ajuste',       'Ajuste manual de saldo.',                      TRUE),
    ('penalizacion', 'Penalización', 'Cargo por penalización (ej. cancelación).',   TRUE)
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- Tabla: transacciones_pago  (reemplaza pagos 1:1)
-- =====================================================
CREATE TABLE IF NOT EXISTS transacciones_pago (
    id                   BIGSERIAL PRIMARY KEY,
    reserva_id           BIGINT         NOT NULL REFERENCES reservas(id) ON DELETE RESTRICT,
    tipo                 VARCHAR(50)    NOT NULL DEFAULT 'cargo',
    monto                NUMERIC(12, 2) NOT NULL,
    metodo_pago          VARCHAR(50)    NOT NULL,
    estado               VARCHAR(50)    DEFAULT 'pendiente',
    numero_transaccion   VARCHAR(150)   UNIQUE,
    referencia_externa   VARCHAR(255),
    pasarela_pago        VARCHAR(50),
    moneda               CHAR(3)        DEFAULT 'USD',
    tasa_cambio          NUMERIC(10, 6) DEFAULT 1.0,
    monto_moneda_local   NUMERIC(12, 2),
    notas                TEXT,
    procesado_por        INTEGER        REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_pago           TIMESTAMPTZ,
    fecha_creacion       TIMESTAMPTZ    DEFAULT NOW(),
    fecha_actualizacion  TIMESTAMPTZ    DEFAULT NOW(),
    CONSTRAINT chk_monto_no_cero    CHECK (monto != 0),
    CONSTRAINT chk_monto_tipo_coherente CHECK (
        (tipo IN ('cargo','deposito','ajuste','penalizacion') AND monto > 0)
        OR
        (tipo = 'reembolso' AND monto < 0)
    ),
    CONSTRAINT chk_moneda_formato   CHECK (moneda ~ '^[A-Z]{3}$'),
    CONSTRAINT fk_tipo_transaccion_catalogo
        FOREIGN KEY (tipo) REFERENCES catalogo_tipo_transaccion(codigo),
    CONSTRAINT fk_metodo_pago_catalogo
        FOREIGN KEY (metodo_pago) REFERENCES catalogo_metodo_pago(codigo),
    CONSTRAINT fk_estado_pago_catalogo
        FOREIGN KEY (estado) REFERENCES catalogo_estado_pago(codigo)
);

COMMENT ON TABLE  transacciones_pago IS 'Historial completo de transacciones financieras. Soporta pagos parciales, depósitos y reembolsos.';
COMMENT ON COLUMN transacciones_pago.monto              IS 'Positivo para cargos/depósitos. Negativo para reembolsos.';
COMMENT ON COLUMN transacciones_pago.referencia_externa IS 'ID de transacción';

CREATE INDEX IF NOT EXISTS idx_transacciones_reserva    ON transacciones_pago(reserva_id);
CREATE INDEX IF NOT EXISTS idx_transacciones_estado     ON transacciones_pago(estado);
CREATE INDEX IF NOT EXISTS idx_transacciones_fecha      ON transacciones_pago(fecha_pago DESC);
CREATE INDEX IF NOT EXISTS idx_transacciones_referencia ON transacciones_pago(referencia_externa);

-- =====================================================
-- Tabla: configuracion_hotel
-- =====================================================
CREATE TABLE IF NOT EXISTS configuracion_hotel (
    clave               VARCHAR(100) PRIMARY KEY,
    valor               TEXT         NOT NULL,
    tipo                VARCHAR(20)  DEFAULT 'string',
    descripcion         TEXT,
    modificable         BOOLEAN      DEFAULT TRUE,
    fecha_actualizacion TIMESTAMPTZ  DEFAULT NOW(),
    actualizado_por     INTEGER      REFERENCES usuarios(id) ON DELETE SET NULL
);

COMMENT ON TABLE  configuracion_hotel IS 'Configuración global del hotel. Evita hardcoding en la aplicación.';
COMMENT ON COLUMN configuracion_hotel.tipo IS 'Tipo del valor: string, integer, decimal, boolean, json.';

-- =====================================================
-- Catálogo: acciones de auditoría
-- =====================================================
CREATE TABLE IF NOT EXISTS catalogo_accion_auditoria (
    codigo      VARCHAR(50) PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN DEFAULT TRUE
);

INSERT INTO catalogo_accion_auditoria (codigo, nombre, descripcion, activo) VALUES
    ('CREATE',             'Crear registro',                 'Operación de inserción de un registro.',                         TRUE),
    ('UPDATE',             'Actualizar registro',            'Operación de actualización de un registro.',                    TRUE),
    ('DELETE',             'Eliminar registro',              'Operación de eliminación de un registro.',                      TRUE),
    ('LOGIN',              'Inicio de sesión',               'Inicio de sesión exitoso de un usuario.',                       TRUE),
    ('LOGOUT',             'Cierre de sesión',               'Cierre de sesión de un usuario.',                               TRUE),
    ('LOGIN_FAILED',       'Inicio de sesión fallido',       'Intento de inicio de sesión fallido.',                          TRUE),
    ('RESERVA_CREATE',     'Reserva creada',                 'Creación de una reserva.',                                      TRUE),
    ('RESERVA_CANCEL',     'Reserva cancelada',              'Cancelación de una reserva.',                                   TRUE),
    ('RESERVA_CONFIRM',    'Reserva confirmada',             'Confirmación de una reserva.',                                  TRUE),
    ('RESERVA_CHECKIN',    'Check-in realizado',             'Registro de check-in de una reserva.',                          TRUE),
    ('RESERVA_CHECKOUT',   'Check-out realizado',            'Registro de check-out de una reserva.',                         TRUE),
    ('PAGO_PROCESS',       'Pago procesado',                 'Procesamiento exitoso de un pago.',                             TRUE),
    ('PAGO_REFUND',        'Pago reembolsado',               'Reembolso de un pago.',                                         TRUE),
    ('PAGO_FAILED',        'Pago fallido',                   'Fallo en el procesamiento de un pago.',                         TRUE),
    ('USUARIO_BLOQUEO',    'Usuario bloqueado',              'Bloqueo de un usuario.',                                        TRUE),
    ('USUARIO_DESBLOQUEO', 'Usuario desbloqueado',           'Desbloqueo de un usuario.',                                     TRUE),
    ('CONFIGURACION_CAMBIO','Cambio de configuración',       'Cambio en la configuración del sistema.',                       TRUE)
ON CONFLICT (codigo) DO NOTHING;

-- =====================================================
-- Tabla: auditoria
-- =====================================================
CREATE TABLE IF NOT EXISTS auditoria (
    id                BIGSERIAL PRIMARY KEY,
    tabla_afectada    VARCHAR(100)     NOT NULL,
    registro_id       BIGINT,
    accion            VARCHAR(50)      NOT NULL,
    usuario_id        INTEGER          REFERENCES usuarios(id) ON DELETE SET NULL,
    datos_anteriores  JSONB,
    datos_nuevos      JSONB,
    ip_address        INET,
    user_agent        TEXT,
    endpoint          VARCHAR(255),
    fecha_accion      TIMESTAMPTZ      DEFAULT NOW(),
    observaciones     TEXT,
    CONSTRAINT fk_auditoria_accion_catalogo
        FOREIGN KEY (accion) REFERENCES catalogo_accion_auditoria(codigo)
);

COMMENT ON TABLE  auditoria IS 'Registro inmutable de todas las acciones del sistema.';
COMMENT ON COLUMN auditoria.datos_anteriores IS 'Snapshot JSON del registro antes de la modificación.';
COMMENT ON COLUMN auditoria.datos_nuevos     IS 'Snapshot JSON del registro después de la modificación.';
COMMENT ON COLUMN auditoria.endpoint         IS 'Endpoint de la API que originó la acción.';

CREATE INDEX IF NOT EXISTS idx_auditoria_tabla      ON auditoria(tabla_afectada);
CREATE INDEX IF NOT EXISTS idx_auditoria_registro   ON auditoria(registro_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario    ON auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion     ON auditoria(accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha      ON auditoria(fecha_accion DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_tabla_fecha ON auditoria(tabla_afectada, fecha_accion DESC);

-- Trigger para hacer inmutable la tabla de auditoría (no UPDATE/DELETE directos)
CREATE OR REPLACE FUNCTION fn_bloquear_modificacion_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'La tabla de auditoría es inmutable: no se permiten UPDATE ni DELETE sobre auditoria'
        USING ERRCODE = 'P0100';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bloquear_modificacion_auditoria
    BEFORE UPDATE OR DELETE ON auditoria
    FOR EACH ROW EXECUTE FUNCTION fn_bloquear_modificacion_auditoria();

-- =====================================================
-- Función: registrar_auditoria  (SECURITY DEFINER)
-- =====================================================
CREATE OR REPLACE FUNCTION registrar_auditoria(
    p_tabla             VARCHAR(100),
    p_registro_id       BIGINT,
    p_accion            VARCHAR(50),
    p_usuario_id        INTEGER  DEFAULT NULL,
    p_datos_anteriores  JSONB    DEFAULT NULL,
    p_datos_nuevos      JSONB    DEFAULT NULL,
    p_observaciones     TEXT     DEFAULT NULL,
    p_ip_address        INET     DEFAULT NULL,
    p_user_agent        TEXT     DEFAULT NULL,
    p_endpoint          VARCHAR(255) DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    BEGIN
        INSERT INTO auditoria (
            tabla_afectada, registro_id, accion, usuario_id,
            datos_anteriores, datos_nuevos, observaciones,
            ip_address, user_agent, endpoint, fecha_accion
        ) VALUES (
            p_tabla, p_registro_id, p_accion, p_usuario_id,
            p_datos_anteriores, p_datos_nuevos, p_observaciones,
            p_ip_address, p_user_agent, p_endpoint, NOW()
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'Error al registrar auditoría para tabla % registro %: %',
            p_tabla, p_registro_id, SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION registrar_auditoria IS
    'Registra eventos de auditoría. SECURITY DEFINER protege la tabla de modificaciones no autorizadas.';

-- =====================================================
-- Función trigger genérica: actualizar timestamp
-- (Una sola función para todas las tablas)
-- =====================================================
CREATE OR REPLACE FUNCTION fn_actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ts_tipos_habitacion
    BEFORE UPDATE ON tipos_habitacion
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_ts_roles
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_ts_usuarios
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_ts_habitaciones
    BEFORE UPDATE ON habitaciones
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_ts_reservas
    BEFORE UPDATE ON reservas
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_ts_transacciones_pago
    BEFORE UPDATE ON transacciones_pago
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

-- =====================================================
-- Trigger: historial de cambios de estado de reserva
-- =====================================================
CREATE OR REPLACE FUNCTION fn_registrar_cambio_estado_reserva()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.estado IS DISTINCT FROM NEW.estado THEN
        INSERT INTO historial_estados_reserva
            (reserva_id, estado_anterior, estado_nuevo)
        VALUES
            (NEW.id, OLD.estado, NEW.estado);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_historial_estado_reserva
    AFTER UPDATE ON reservas
    FOR EACH ROW EXECUTE FUNCTION fn_registrar_cambio_estado_reserva();

-- =====================================================
-- Trigger: validar capacidad de habitación vs tipo
-- =====================================================
CREATE OR REPLACE FUNCTION fn_validar_capacidad_habitacion()
RETURNS TRIGGER AS $$
DECLARE
    v_capacidad_maxima INTEGER;
BEGIN
    SELECT capacidad_maxima INTO v_capacidad_maxima
    FROM tipos_habitacion
    WHERE id = NEW.tipo_habitacion_id;

    IF NEW.capacidad > v_capacidad_maxima THEN
        RAISE EXCEPTION
            'La capacidad de la habitación (%) no puede exceder la capacidad máxima del tipo (%)',
            NEW.capacidad, v_capacidad_maxima
            USING ERRCODE = 'P0004';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_capacidad_habitacion
    BEFORE INSERT OR UPDATE ON habitaciones
    FOR EACH ROW EXECUTE FUNCTION fn_validar_capacidad_habitacion();

-- =====================================================
-- Trigger: prevención de doble reserva
-- (Compatible con Supabase — reemplaza EXCLUSION CONSTRAINT
--  que no funciona con tablas particionadas ni en Supabase)
-- =====================================================
CREATE OR REPLACE FUNCTION fn_validar_no_solapamiento_reserva()
RETURNS TRIGGER AS $$
BEGIN
    -- Bloqueo lógico por habitación para evitar condiciones de carrera en alta concurrencia.
    -- Garantiza que solo una transacción a la vez pueda validar/insertar reservas
    -- para la misma habitación dentro de la transacción actual.
    PERFORM pg_advisory_xact_lock(NEW.habitacion_id);

    IF NEW.estado = 'cancelada' THEN
        RETURN NEW;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM   reservas r
        WHERE  r.habitacion_id = NEW.habitacion_id
          AND  r.id IS DISTINCT FROM NEW.id
          AND  r.estado NOT IN ('cancelada', 'completada')
          AND  daterange(r.fecha_entrada, r.fecha_salida, '[)')
            && daterange(NEW.fecha_entrada, NEW.fecha_salida, '[)')
    ) THEN
        RAISE EXCEPTION
            'La habitación % ya tiene una reserva activa que se solapa con las fechas % - %',
            NEW.habitacion_id, NEW.fecha_entrada, NEW.fecha_salida
            USING ERRCODE = 'P0010';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_no_solapamiento
    BEFORE INSERT OR UPDATE ON reservas
    FOR EACH ROW EXECUTE FUNCTION fn_validar_no_solapamiento_reserva();

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

-- sp_crear_habitacion
CREATE OR REPLACE FUNCTION sp_crear_habitacion(
    p_numero            VARCHAR(10),
    p_tipo_habitacion_id INTEGER,
    p_descripcion       TEXT,
    p_capacidad         INTEGER,
    p_precio_por_noche  NUMERIC,
    p_estado            VARCHAR(20) DEFAULT 'disponible',
    p_imagen_url        VARCHAR(500) DEFAULT NULL,
    p_piso              INTEGER      DEFAULT NULL,
    p_caracteristicas   JSONB        DEFAULT NULL,
    p_usuario_id        INTEGER      DEFAULT NULL
)
RETURNS TABLE (
    id                  INTEGER,
    numero              VARCHAR(10),
    tipo_habitacion_id  INTEGER,
    descripcion         TEXT,
    capacidad           INTEGER,
    precio_por_noche    NUMERIC,
    estado              VARCHAR(20),
    imagen_url          VARCHAR(500),
    fecha_creacion      TIMESTAMPTZ
) AS $$
DECLARE
    v_habitacion_id INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM habitaciones WHERE habitaciones.numero = p_numero) THEN
        RAISE EXCEPTION 'Ya existe una habitación con el número %', p_numero
            USING ERRCODE = 'P0001';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM tipos_habitacion th
        WHERE th.id = p_tipo_habitacion_id AND th.activo = TRUE
    ) THEN
        RAISE EXCEPTION 'El tipo de habitación no existe o no está activo'
            USING ERRCODE = 'P0002';
    END IF;
    IF p_capacidad <= 0 THEN
        RAISE EXCEPTION 'La capacidad debe ser mayor a 0' USING ERRCODE = 'P0003';
    END IF;
    IF p_precio_por_noche <= 0 THEN
        RAISE EXCEPTION 'El precio por noche debe ser mayor a 0' USING ERRCODE = 'P0004';
    END IF;

    INSERT INTO habitaciones (
        numero, tipo_habitacion_id, descripcion, capacidad,
        precio_por_noche, estado, imagen_url, piso, caracteristicas
    ) VALUES (
        p_numero, p_tipo_habitacion_id, p_descripcion, p_capacidad,
        p_precio_por_noche, p_estado, p_imagen_url, p_piso, p_caracteristicas
    ) RETURNING habitaciones.id INTO v_habitacion_id;

    PERFORM registrar_auditoria(
        'habitaciones', v_habitacion_id, 'CREATE', p_usuario_id,
        NULL, row_to_json(h.*)::JSONB
    ) FROM habitaciones h WHERE h.id = v_habitacion_id;

    RETURN QUERY
    SELECT h.id, h.numero, h.tipo_habitacion_id, h.descripcion,
           h.capacidad, h.precio_por_noche, h.estado,
           h.imagen_url, h.fecha_creacion
    FROM habitaciones h WHERE h.id = v_habitacion_id;
END;
$$ LANGUAGE plpgsql;

-- sp_buscar_habitaciones_disponibles
CREATE OR REPLACE FUNCTION sp_buscar_habitaciones_disponibles(
    p_fecha_entrada      DATE,
    p_fecha_salida       DATE,
    p_capacidad          INTEGER DEFAULT NULL,
    p_tipo_habitacion_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id                 INTEGER,
    numero             VARCHAR(10),
    tipo_habitacion_id INTEGER,
    tipo_nombre        VARCHAR(100),
    descripcion        TEXT,
    capacidad          INTEGER,
    precio_por_noche   NUMERIC,
    estado             VARCHAR(20),
    imagen_url         VARCHAR(500),
    caracteristicas    JSONB
) AS $$
BEGIN
    IF p_fecha_entrada >= p_fecha_salida THEN
        RAISE EXCEPTION 'La fecha de entrada debe ser anterior a la fecha de salida'
            USING ERRCODE = 'P0001';
    END IF;
    IF p_fecha_entrada < CURRENT_DATE THEN
        RAISE EXCEPTION 'La fecha de entrada no puede ser en el pasado'
            USING ERRCODE = 'P0002';
    END IF;

    RETURN QUERY
    SELECT
        h.id, h.numero, h.tipo_habitacion_id,
        th.nombre AS tipo_nombre,
        h.descripcion, h.capacidad, h.precio_por_noche,
        h.estado, h.imagen_url, h.caracteristicas
    FROM habitaciones h
    INNER JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
    WHERE h.estado = 'disponible'
      AND NOT EXISTS (
            SELECT 1 FROM reservas r
            WHERE  r.habitacion_id = h.id
              AND  r.estado NOT IN ('cancelada', 'completada')
              AND  daterange(r.fecha_entrada, r.fecha_salida, '[)')
                && daterange(p_fecha_entrada, p_fecha_salida, '[)')
          )
      AND (p_capacidad          IS NULL OR h.capacidad          >= p_capacidad)
      AND (p_tipo_habitacion_id IS NULL OR h.tipo_habitacion_id  = p_tipo_habitacion_id)
    ORDER BY h.precio_por_noche ASC;
END;
$$ LANGUAGE plpgsql;

-- sp_crear_reserva  (con bloqueo pesimista FOR UPDATE)
CREATE OR REPLACE FUNCTION sp_crear_reserva(
    p_usuario_id               INTEGER,
    p_habitacion_id            INTEGER,
    p_fecha_entrada            DATE,
    p_fecha_salida             DATE,
    p_numero_huespedes         INTEGER,
    p_notas                    VARCHAR(1000) DEFAULT NULL,
    p_usuario_auditoria_id     INTEGER       DEFAULT NULL,
    p_canal_reserva            VARCHAR(50)   DEFAULT 'web',
    p_politica_cancelacion_id   INTEGER       DEFAULT NULL
)
RETURNS TABLE (
    id               BIGINT,
    usuario_id       INTEGER,
    habitacion_id    INTEGER,
    codigo_reserva   VARCHAR(20),
    fecha_entrada    DATE,
    fecha_salida     DATE,
    numero_huespedes INTEGER,
    moneda           CHAR(3),
    subtotal         NUMERIC,
    impuestos        NUMERIC,
    descuentos       NUMERIC,
    otros_cargos     NUMERIC,
    precio_total     NUMERIC,
    estado           VARCHAR(50),
    notas            VARCHAR(1000),
    fecha_creacion   TIMESTAMPTZ
) AS $$
DECLARE
    v_reserva_id     BIGINT;
    v_precio_noche   NUMERIC;
    v_capacidad      INTEGER;
    v_subtotal       NUMERIC;
    v_impuestos      NUMERIC;
    v_descuentos     NUMERIC;
    v_otros_cargos   NUMERIC;
    v_precio_total   NUMERIC;
    v_moneda         CHAR(3);
    v_impuesto_pct   NUMERIC;
BEGIN
    IF p_fecha_entrada < CURRENT_DATE THEN
        RAISE EXCEPTION 'La fecha de entrada no puede ser en el pasado'
            USING ERRCODE = 'P0001';
    END IF;
    IF p_fecha_entrada >= p_fecha_salida THEN
        RAISE EXCEPTION 'La fecha de entrada debe ser anterior a la fecha de salida'
            USING ERRCODE = 'P0002';
    END IF;

    -- Bloqueo pesimista: evita condición de carrera entre solicitudes concurrentes
    SELECT h.precio_por_noche, h.capacidad
    INTO   v_precio_noche, v_capacidad
    FROM   habitaciones h
    WHERE  h.id = p_habitacion_id AND h.estado = 'disponible'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'La habitación no existe o no está disponible'
            USING ERRCODE = 'P0003';
    END IF;

    IF p_numero_huespedes > v_capacidad THEN
        RAISE EXCEPTION 'El número de huéspedes (%) excede la capacidad de la habitación (%)',
            p_numero_huespedes, v_capacidad
            USING ERRCODE = 'P0004';
    END IF;

    -- Calcular noches y subtotal
    v_subtotal := v_precio_noche * (p_fecha_salida - p_fecha_entrada);

    -- Obtener configuración de impuestos y moneda
    SELECT COALESCE(NULLIF(valor, ''), 'USD')::CHAR(3)
    INTO v_moneda
    FROM configuracion_hotel
    WHERE clave = 'hotel_moneda';

    IF v_moneda IS NULL THEN
        v_moneda := 'USD';
    END IF;

    SELECT COALESCE(valor::NUMERIC, 0)
    INTO v_impuesto_pct
    FROM configuracion_hotel
    WHERE clave = 'impuesto_porcentaje';

    IF v_impuesto_pct IS NULL THEN
        v_impuesto_pct := 0;
    END IF;

    v_impuestos := ROUND(v_subtotal * v_impuesto_pct / 100, 2);
    v_descuentos := 0;
    v_otros_cargos := 0;
    v_precio_total := v_subtotal + v_otros_cargos + v_impuestos - v_descuentos;

    INSERT INTO reservas (
        usuario_id, habitacion_id, politica_cancelacion_id,
        fecha_entrada, fecha_salida, numero_huespedes,
        moneda, tasa_cambio,
        subtotal, impuestos, descuentos, otros_cargos, precio_total,
        precio_por_noche_snapshot,
        notas, canal_reserva
    ) VALUES (
        p_usuario_id, p_habitacion_id, p_politica_cancelacion_id,
        p_fecha_entrada, p_fecha_salida, p_numero_huespedes,
        v_moneda, 1.0,
        v_subtotal, v_impuestos, v_descuentos, v_otros_cargos, v_precio_total,
        v_precio_noche,
        p_notas, p_canal_reserva
    ) RETURNING reservas.id INTO v_reserva_id;

    PERFORM registrar_auditoria(
        'reservas', v_reserva_id, 'RESERVA_CREATE', p_usuario_auditoria_id,
        NULL, row_to_json(r.*)::JSONB, 'Reserva creada'
    ) FROM reservas r WHERE r.id = v_reserva_id;

    RETURN QUERY
    SELECT r.id, r.usuario_id, r.habitacion_id, r.codigo_reserva,
           r.fecha_entrada, r.fecha_salida, r.numero_huespedes,
           r.moneda, r.subtotal, r.impuestos, r.descuentos, r.otros_cargos,
           r.precio_total, r.estado, r.notas, r.fecha_creacion
    FROM reservas r WHERE r.id = v_reserva_id;
END;
$$ LANGUAGE plpgsql;

-- sp_procesar_pago
CREATE OR REPLACE FUNCTION sp_procesar_pago(
    p_reserva_id          BIGINT,
    p_monto               NUMERIC,
    p_metodo_pago         VARCHAR(50),
    p_tipo                VARCHAR(50) DEFAULT 'cargo',
    p_numero_transaccion  VARCHAR(150)     DEFAULT NULL,
    p_referencia_externa  VARCHAR(255)     DEFAULT NULL,
    p_pasarela_pago       VARCHAR(50)      DEFAULT NULL,
    p_usuario_id          INTEGER          DEFAULT NULL
)
RETURNS TABLE (
    id                  BIGINT,
    reserva_id          BIGINT,
    monto               NUMERIC,
    metodo_pago         VARCHAR(50),
    estado              VARCHAR(50),
    numero_transaccion  VARCHAR(150),
    fecha_pago          TIMESTAMPTZ
) AS $$
DECLARE
    v_transaccion_id  BIGINT;
    v_precio_reserva  NUMERIC;
    v_estado_reserva  VARCHAR(50);
    v_total_pagado    NUMERIC;
BEGIN
    SELECT r.precio_total, r.estado
    INTO   v_precio_reserva, v_estado_reserva
    FROM   reservas r WHERE r.id = p_reserva_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'La reserva no existe' USING ERRCODE = 'P0001';
    END IF;
    IF v_estado_reserva = 'cancelada' THEN
        RAISE EXCEPTION 'No se puede procesar un pago para una reserva cancelada'
            USING ERRCODE = 'P0002';
    END IF;
    IF p_monto <= 0 THEN
        RAISE EXCEPTION 'El monto debe ser mayor a 0' USING ERRCODE = 'P0003';
    END IF;

    INSERT INTO transacciones_pago (
        reserva_id, tipo, monto, metodo_pago, estado,
        numero_transaccion, referencia_externa, pasarela_pago,
        fecha_pago, procesado_por
    ) VALUES (
        p_reserva_id, p_tipo, p_monto, p_metodo_pago, 'completado',
        p_numero_transaccion, p_referencia_externa, p_pasarela_pago,
        NOW(), p_usuario_id
    ) RETURNING transacciones_pago.id INTO v_transaccion_id;

    -- Confirmar reserva automáticamente si el total pagado cubre el precio
    SELECT COALESCE(SUM(monto), 0)
    INTO   v_total_pagado
    FROM   transacciones_pago
    WHERE  reserva_id = p_reserva_id
      AND  estado = 'completado'
      AND  tipo = 'cargo';

    IF v_total_pagado >= v_precio_reserva THEN
        UPDATE reservas SET estado = 'confirmada' WHERE id = p_reserva_id;
    END IF;

    PERFORM registrar_auditoria(
        'transacciones_pago', v_transaccion_id, 'PAGO_PROCESS', p_usuario_id,
        NULL, row_to_json(tp.*)::JSONB, 'Pago procesado exitosamente'
    ) FROM transacciones_pago tp WHERE tp.id = v_transaccion_id;

    RETURN QUERY
    SELECT tp.id, tp.reserva_id, tp.monto, tp.metodo_pago,
           tp.estado, tp.numero_transaccion, tp.fecha_pago
    FROM transacciones_pago tp WHERE tp.id = v_transaccion_id;
END;
$$ LANGUAGE plpgsql;

-- sp_obtener_estadisticas_reservas
CREATE OR REPLACE FUNCTION sp_obtener_estadisticas_reservas(
    p_fecha_inicio DATE DEFAULT NULL,
    p_fecha_fin    DATE DEFAULT NULL
)
RETURNS TABLE (
    total_reservas       BIGINT,
    reservas_pendientes  BIGINT,
    reservas_confirmadas BIGINT,
    reservas_canceladas  BIGINT,
    reservas_completadas BIGINT,
    ingresos_totales     NUMERIC,
    promedio_reserva     NUMERIC,
    tasa_cancelacion     NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE r.estado = 'pendiente')::BIGINT,
        COUNT(*) FILTER (WHERE r.estado = 'confirmada')::BIGINT,
        COUNT(*) FILTER (WHERE r.estado = 'cancelada')::BIGINT,
        COUNT(*) FILTER (WHERE r.estado = 'completada')::BIGINT,
        COALESCE(SUM(r.precio_total)  FILTER (WHERE r.estado != 'cancelada'), 0),
        COALESCE(AVG(r.precio_total)  FILTER (WHERE r.estado != 'cancelada'), 0),
        CASE WHEN COUNT(*) > 0
             THEN ROUND(
                    COUNT(*) FILTER (WHERE r.estado = 'cancelada')::NUMERIC
                    / COUNT(*) * 100, 2)
             ELSE 0
        END
    FROM reservas r
    WHERE (p_fecha_inicio IS NULL OR r.fecha_creacion >= p_fecha_inicio::TIMESTAMPTZ)
      AND (p_fecha_fin    IS NULL OR r.fecha_creacion <= (p_fecha_fin + INTERVAL '1 day')::TIMESTAMPTZ);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Vista: reservas_completas
-- =====================================================
CREATE OR REPLACE VIEW vista_reservas_completas AS
SELECT
    r.id,
    r.codigo_reserva,
    r.fecha_entrada,
    r.fecha_salida,
    r.numero_huespedes,
    r.moneda,
    r.subtotal,
    r.impuestos,
    r.descuentos,
    r.otros_cargos,
    r.precio_total,
    r.estado,
    r.canal_reserva,
    r.fecha_creacion,
    u.id                AS usuario_id,
    u.nombre || ' ' || u.apellido AS nombre_cliente,
    u.email             AS email_cliente,
    h.id                AS habitacion_id,
    h.numero            AS numero_habitacion,
    h.piso,
    th.nombre           AS tipo_habitacion,
    th.codigo           AS codigo_tipo_habitacion,
    COALESCE(SUM(tp.monto) FILTER (WHERE tp.estado = 'completado' AND tp.tipo = 'cargo'),      0) AS total_pagado,
    COALESCE(SUM(tp.monto) FILTER (WHERE tp.estado = 'completado' AND tp.tipo = 'reembolso'),  0) AS total_reembolsado
FROM reservas r
JOIN usuarios u          ON r.usuario_id          = u.id
JOIN habitaciones h      ON r.habitacion_id        = h.id
JOIN tipos_habitacion th ON h.tipo_habitacion_id   = th.id
LEFT JOIN transacciones_pago tp ON r.id = tp.reserva_id
GROUP BY r.id, r.codigo_reserva, r.fecha_entrada, r.fecha_salida,
         r.numero_huespedes, r.moneda, r.subtotal, r.impuestos, r.descuentos, r.otros_cargos, r.precio_total,
         r.estado, r.canal_reserva, r.fecha_creacion,
         u.id, u.nombre, u.apellido, u.email,
         h.id, h.numero, h.piso, th.nombre, th.codigo;

-- =====================================================
-- Vista: habitaciones_disponibles
-- =====================================================
CREATE OR REPLACE VIEW vista_habitaciones_disponibles AS
SELECT
    h.id,
    h.numero,
    h.piso,
    h.tipo_habitacion_id,
    th.codigo           AS codigo_tipo,
    th.nombre           AS tipo_nombre,
    th.descripcion      AS tipo_descripcion,
    h.descripcion       AS habitacion_descripcion,
    h.capacidad,
    h.precio_por_noche,
    h.estado,
    h.imagen_url,
    h.caracteristicas,
    COUNT(r.id) FILTER (
        WHERE r.estado != 'cancelada' AND r.fecha_salida >= CURRENT_DATE
    ) AS total_reservas_activas
FROM habitaciones h
INNER JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
LEFT JOIN  reservas r          ON h.id = r.habitacion_id
GROUP BY h.id, h.numero, h.piso, h.tipo_habitacion_id,
         th.codigo, th.nombre, th.descripcion,
         h.descripcion, h.capacidad, h.precio_por_noche,
         h.estado, h.imagen_url, h.caracteristicas;

-- =====================================================
-- Vista materializada: estadísticas mensuales
-- =====================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_estadisticas_mensuales AS
SELECT
    DATE_TRUNC('month', fecha_entrada)                                           AS mes,
    COUNT(*)                                                                     AS total_reservas,
    COUNT(*) FILTER (WHERE estado = 'confirmada')                                AS confirmadas,
    COUNT(*) FILTER (WHERE estado = 'cancelada')                                 AS canceladas,
    COUNT(*) FILTER (WHERE estado = 'completada')                                AS completadas,
    COALESCE(SUM(precio_total) FILTER (WHERE estado != 'cancelada'), 0)          AS ingresos,
    COALESCE(AVG(precio_total) FILTER (WHERE estado != 'cancelada'), 0)          AS ticket_promedio,
    COALESCE(AVG(fecha_salida - fecha_entrada)::NUMERIC, 0)                      AS estancia_promedio_noches
FROM reservas
GROUP BY DATE_TRUNC('month', fecha_entrada)
WITH DATA;

CREATE UNIQUE INDEX ON mv_estadisticas_mensuales(mes);

-- Función para refrescar la vista materializada (llamar periódicamente)
CREATE OR REPLACE FUNCTION fn_refrescar_estadisticas()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_estadisticas_mensuales;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Datos iniciales
-- =====================================================

INSERT INTO tipos_habitacion (codigo, nombre, descripcion, capacidad_maxima, precio_base) VALUES
    ('IND',   'Individual', 'Habitación individual con cama de tamaño completo',    1,  50.00),
    ('DBL',   'Doble',      'Habitación doble con dos camas individuales',           2,  75.00),
    ('SUITE', 'Suite',      'Suite de lujo con sala de estar',                       4, 150.00),
    ('FAM',   'Familiar',   'Habitación familiar con capacidad para 4 personas',     4, 120.00)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO roles (nombre, descripcion) VALUES
    ('administrador', 'Acceso total al sistema'),
    ('recepcionista', 'Gestión de reservas y check-in/check-out'),
    ('gerente',       'Reportes, estadísticas y gestión de precios'),
    ('huesped',       'Acceso al portal de clientes')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO permisos (codigo, nombre, modulo) VALUES
    ('reservas.crear',          'Crear reservas',                    'reservas'),
    ('reservas.cancelar',       'Cancelar reservas',                 'reservas'),
    ('reservas.ver_todas',      'Ver todas las reservas',            'reservas'),
    ('habitaciones.gestionar',  'Gestionar habitaciones',            'habitaciones'),
    ('usuarios.gestionar',      'Gestionar usuarios',                'usuarios'),
    ('pagos.procesar',          'Procesar pagos',                    'pagos'),
    ('pagos.reembolsar',        'Procesar reembolsos',               'pagos'),
    ('reportes.ver',            'Ver reportes y estadísticas',       'reportes'),
    ('configuracion.modificar', 'Modificar configuración del hotel', 'configuracion')
ON CONFLICT (codigo) DO NOTHING;

-- Asignar permisos a cada rol (RBAC)
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r, permisos p
WHERE r.nombre = 'administrador'
ON CONFLICT (rol_id, permiso_id) DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r, permisos p
WHERE r.nombre = 'recepcionista'
  AND p.codigo IN ('reservas.crear', 'reservas.cancelar', 'reservas.ver_todas', 'habitaciones.gestionar', 'pagos.procesar', 'pagos.reembolsar')
ON CONFLICT (rol_id, permiso_id) DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r, permisos p
WHERE r.nombre = 'gerente'
  AND p.codigo IN ('reservas.ver_todas', 'habitaciones.gestionar', 'pagos.procesar', 'pagos.reembolsar', 'reportes.ver', 'configuracion.modificar')
ON CONFLICT (rol_id, permiso_id) DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id FROM roles r, permisos p
WHERE r.nombre = 'huesped'
  AND p.codigo IN ('reservas.crear', 'reservas.cancelar')
ON CONFLICT (rol_id, permiso_id) DO NOTHING;

INSERT INTO politicas_cancelacion (nombre, descripcion, horas_anticipacion, porcentaje_penalizacion) VALUES
    ('Flexible', 'Cancelación gratuita hasta 24h antes del check-in',              24,   0),
    ('Moderada', 'Cancelación gratuita hasta 72h antes; 50% de penalización luego', 72,  50),
    ('Estricta', 'No reembolsable',                                                  0, 100)
ON CONFLICT DO NOTHING;

INSERT INTO configuracion_hotel (clave, valor, tipo, descripcion) VALUES
    ('hotel_nombre',                   'Royal Palm Hotel',                  'string',  'Nombre del hotel'),
    ('hotel_moneda',                   'USD',                               'string',  'Moneda principal (ISO 4217)'),
    ('checkin_hora',                   '15:00',                             'string',  'Hora estándar de check-in'),
    ('checkout_hora',                  '11:00',                             'string',  'Hora estándar de check-out'),
    ('max_dias_anticipacion_reserva',  '365',                               'integer', 'Máximo de días con anticipación para reservar'),
    ('min_noches_estancia',            '1',                                 'integer', 'Mínimo de noches por reserva'),
    ('impuesto_porcentaje',            '15.00',                             'decimal', 'Porcentaje de impuesto (IVA Nicaragua)'),
    ('email_notificaciones',           'reservas@royalpalmhotel.com',       'string',  'Email para notificaciones del sistema'),
    ('max_intentos_login',             '5',                                 'integer', 'Máximo de intentos de login antes de bloqueo temporal'),
    ('minutos_bloqueo_login',          '30',                                'integer', 'Minutos de bloqueo tras exceder intentos de login'),
    ('timezone',                       'America/Managua',                   'string',  'Zona horaria del hotel (Nicaragua UTC-6)')
ON CONFLICT (clave) DO NOTHING;
