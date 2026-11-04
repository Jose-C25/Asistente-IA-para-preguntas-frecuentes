from app.database.connection import obtener_conexion
from app.core.security import generar_hash_password

def inicializar_bd():
    """Inicializa tablas, vistas, usuarios y esquema de caja chica."""
    conn = obtener_conexion()
    cursor = conn.cursor()

    # 1. Tabla Tienda (Dirección actualizada)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tienda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            direccion TEXT,
            telefono TEXT,
            horario TEXT,
            descripcion TEXT
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM tienda")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO tienda (nombre, direccion, telefono, horario, descripcion)
            VALUES (
                'Repuestos Don José',
                'Zona 1, Barrio San Juan, San Juan Chamelco, Alta Verapaz',
                '+502 1234-5678',
                'Lunes a Viernes: 8:00 AM – 6:00 PM | Sábados: 8:00 AM – 2:00 PM',
                'Especialistas en repuestos automotrices multimarca.'
            )
        """)
    else:
        cursor.execute("""
            UPDATE tienda SET direccion = 'Zona 1, Barrio San Juan, San Juan Chamelco, Alta Verapaz' WHERE id = 1
        """)

    # 2. Tabla Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            rol TEXT CHECK(rol IN ('admin', 'empleado')) NOT NULL,
            activo INTEGER DEFAULT 1,
            intentos_fallidos INTEGER DEFAULT 0,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO usuarios (username, password_hash, nombre, rol)
            VALUES (?, ?, ?, ?)
        """, [
            ("admin", generar_hash_password("admin123"), "Administrador General", "admin"),
            ("cajero", generar_hash_password("cajero123"), "Cajero / Encargado", "empleado")
        ])

    # 3. Tabla Inventario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_repuesto TEXT NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            anio TEXT,
            precio REAL NOT NULL,
            precio_costo REAL DEFAULT 0.0,
            stock INTEGER NOT NULL,
            descripcion TEXT
        );
    """)

    cursor.execute("PRAGMA table_info(inventario)")
    cols = [col[1] for col in cursor.fetchall()]
    if "precio_costo" not in cols:
        cursor.execute("ALTER TABLE inventario ADD COLUMN precio_costo REAL DEFAULT 0.0;")

    cursor.execute("SELECT COUNT(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        repuestos = [
            ('pastillas de freno', 'Honda', 'Civic', '2018', 350.00, 200.00, 8, 'Pastillas cerámicas delanteras'),
            ('pastillas de freno', 'Honda', 'Civic', '2020', 380.00, 220.00, 5, 'Pastillas cerámicas traseras'),
            ('filtro de aceite', 'Honda', 'Civic', '2018', 65.00, 35.00, 15, 'Filtro de aceite alto rendimiento'),
            ('filtro de aceite', 'Toyota', 'Corolla', '2020', 70.00, 40.00, 18, 'Filtro de aceite sintético'),
            ('pastillas de freno', 'Toyota', 'Corolla', '2019', 320.00, 180.00, 10, 'Pastillas semi-metálicas delanteras'),
            ('filtro de aceite', 'Nissan', 'Sentra', '2019', 65.00, 35.00, 15, 'Filtro de aceite 1.8L / 2.0L')
        ]
        cursor.executemany("""
            INSERT INTO inventario (tipo_repuesto, marca, modelo, anio, precio, precio_costo, stock, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, repuestos)

    # 4. Tabla Pedidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            vehiculo TEXT NOT NULL,
            direccion TEXT NOT NULL,
            metodo_pago TEXT DEFAULT 'Contra Entrega',
            total REAL NOT NULL,
            detalle_items TEXT,
            estado TEXT DEFAULT 'Pendiente',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 5. Tabla Caja Chica
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto_inicial REAL NOT NULL DEFAULT 0.0,
            ingresos_efectivo REAL NOT NULL DEFAULT 0.0,
            egresos REAL NOT NULL DEFAULT 0.0,
            saldo_actual REAL NOT NULL DEFAULT 0.0,
            fecha DATE UNIQUE NOT NULL DEFAULT (DATE('now', 'localtime')),
            estado TEXT CHECK(estado IN ('abierta', 'cerrada')) DEFAULT 'abierta'
        );
    """)

    # 6. Tabla Movimientos de Caja
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caja_id INTEGER NOT NULL,
            pedido_id INTEGER,
            tipo TEXT CHECK(tipo IN ('ingreso_pedido', 'apertura', 'egreso', 'ajuste')) NOT NULL,
            monto REAL NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(caja_id) REFERENCES caja(id),
            FOREIGN KEY(pedido_id) REFERENCES pedidos(id)
        );
    """)
    # Agregar en inicializar_bd() dentro de app/database/schema.py:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        accion TEXT NOT NULL,
        detalles TEXT,
        ip TEXT DEFAULT '127.0.0.1',
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

    # 7. Vista Pública aislada
    cursor.execute("DROP VIEW IF EXISTS vista_inventario_publica;")
    cursor.execute("""
        CREATE VIEW vista_inventario_publica AS
        SELECT id, tipo_repuesto, marca, modelo, anio, precio, stock, descripcion
        FROM inventario;
    """)



    conn.commit()
    conn.close()