"""
Script para inicializar la base de datos
Ejecutar: python scripts/init_database.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import Usuario, Habitacion, Reserva, Pago


def init_db():
    """Crea todas las tablas, tipos ENUM, índices, triggers y vistas en la base de datos"""
    try:
        print("=" * 50)
        print("Inicializando base de datos...")
        print("=" * 50)
        
        # Verificar conexión
        print("\n1. Verificando conexion a la base de datos...")
        with engine.connect() as conn:
            print("[OK] Conexion establecida correctamente")
        
        # Crear tipos ENUM
        print("\n2. Creando tipos ENUM...")
        with engine.begin() as conn:
            # Crear tipo estado_reserva
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE estado_reserva AS ENUM ('pendiente', 'confirmada', 'cancelada', 'completada');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Crear tipo metodo_pago
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE metodo_pago AS ENUM ('tarjeta_credito', 'tarjeta_debito', 'efectivo', 'transferencia');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Crear tipo estado_pago
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE estado_pago AS ENUM ('pendiente', 'completado', 'rechazado', 'reembolsado');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
        print("[OK] Tipos ENUM creados correctamente")
        
        # Crear tablas usando SQLAlchemy
        print("\n3. Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Tablas creadas correctamente")
        
        # Crear índices adicionales
        print("\n4. Creando indices adicionales...")
        with engine.begin() as conn:
            # Índice en email de usuarios (ya existe por index=True, pero lo creamos explícitamente)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
            """))
            
            # Índice en numero de habitaciones (ya existe por index=True)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_habitaciones_numero ON habitaciones(numero);
            """))
            
            # Índices en reservas
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reservas_usuario ON reservas(usuario_id);
                CREATE INDEX IF NOT EXISTS idx_reservas_habitacion ON reservas(habitacion_id);
                CREATE INDEX IF NOT EXISTS idx_reservas_fechas ON reservas(fecha_entrada, fecha_salida);
            """))
            
            # Índices en pagos
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pagos_reserva ON pagos(reserva_id);
                CREATE INDEX IF NOT EXISTS idx_pagos_transaccion ON pagos(numero_transaccion);
            """))
        print("[OK] Indices creados correctamente")
        
        # Crear trigger para fecha_actualizacion
        print("\n5. Creando trigger para fecha_actualizacion...")
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            conn.execute(text("""
                DROP TRIGGER IF EXISTS trigger_update_fecha_actualizacion ON reservas;
                CREATE TRIGGER trigger_update_fecha_actualizacion
                BEFORE UPDATE ON reservas
                FOR EACH ROW
                EXECUTE FUNCTION update_fecha_actualizacion();
            """))
        print("[OK] Trigger creado correctamente")
        
        # Crear vistas
        print("\n6. Creando vistas...")
        with engine.begin() as conn:
            # Vista de reservas completas
            conn.execute(text("""
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
            """))
            
            # Vista de habitaciones disponibles
            conn.execute(text("""
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
            """))
        print("[OK] Vistas creadas correctamente")
        
        # Insertar datos de ejemplo (opcional)
        print("\n7. Insertando datos de ejemplo...")
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO habitaciones (numero, tipo, descripcion, capacidad, precio_por_noche, disponible)
                VALUES
                    ('101', 'Individual', 'Habitación individual con cama de tamaño completo', 1, 50.00, TRUE),
                    ('102', 'Doble', 'Habitación doble con dos camas individuales', 2, 75.00, TRUE),
                    ('103', 'Suite', 'Suite de lujo con sala de estar', 4, 150.00, TRUE),
                    ('201', 'Individual', 'Habitación individual con vista al jardín', 1, 55.00, TRUE),
                    ('202', 'Doble', 'Habitación doble con balcón', 2, 80.00, TRUE),
                    ('203', 'Familiar', 'Habitación familiar con capacidad para 4 personas', 4, 120.00, TRUE)
                ON CONFLICT (numero) DO NOTHING;
            """))
        print("[OK] Datos de ejemplo insertados correctamente")
        
        print("\n" + "=" * 50)
        print("[OK] Base de datos inicializada correctamente")
        print("=" * 50)
        print("\nNota: Para crear un usuario administrador, ejecuta:")
        print("      python scripts/create_admin.py <tu_contraseña>")
        
    except Exception as e:
        print(f"\n[ERROR] Error al inicializar la base de datos:")
        print(f"   {str(e)}")
        print("\nVerifica:")
        print("   1. Que el archivo .env tenga DATABASE_URL configurado correctamente")
        print("   2. Que la base de datos exista y sea accesible")
        print("   3. Que las credenciales sean correctas")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_db()
