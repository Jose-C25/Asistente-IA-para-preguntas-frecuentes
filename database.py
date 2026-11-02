import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "inventario.db")

# Palabras o comodines que deben ignorarse en la consulta SQL
VALORES_IGNORAR = {
    "", "none", "n/a", "na", "null", "undefined", 
    "desconocido", "todos", "todas", "cualquiera", "no especificado"
}

def inicializar_bd():
    """Crea las tablas, la vista pública y carga un inventario representativo."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
                'Ciudad de Guatemala',
                '+502 1234-5678',
                'Lunes a Viernes: 8:00 AM – 6:00 PM | Sábados: 8:00 AM – 2:00 PM',
                'Especialistas en repuestos automotrices multimarca.'
            )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_repuesto TEXT NOT NULL,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            anio TEXT,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            descripcion TEXT
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        repuestos_expandidos = [
            # HONDA
            ('pastillas de freno', 'Honda', 'Civic', '2018', 350.00, 8, 'Pastillas de freno delanteras cerámicas de alta durabilidad'),
            ('pastillas de freno', 'Honda', 'Civic', '2020', 380.00, 5, 'Pastillas de freno traseras cerámicas'),
            ('filtro de aceite', 'Honda', 'Civic', '2018', 65.00, 15, 'Filtro de aceite alto rendimiento'),
            ('filtro de aire', 'Honda', 'Civic', '2019', 110.00, 10, 'Filtro de aire del motor de alto flujo'),
            ('bujias', 'Honda', 'Civic', '2018', 120.00, 20, 'Bujía de encendido iridio larga duración'),
            ('amortiguador', 'Honda', 'CR-V', '2019', 850.00, 4, 'Amortiguador delantero a gas par'),
            ('filtro de aceite', 'Honda', 'CR-V', '2021', 85.00, 12, 'Filtro de aceite sintético'),

            # TOYOTA
            ('filtro de aceite', 'Toyota', 'Corolla', '2020', 70.00, 18, 'Filtro de aceite sintético premium'),
            ('filtro de aire', 'Toyota', 'Corolla', '2019', 95.00, 14, 'Filtro de aire de cabina/polen'),
            ('pastillas de freno', 'Toyota', 'Corolla', '2019', 320.00, 10, 'Pastillas de freno delanteras semi-metálicas'),
            ('disco de freno', 'Toyota', 'Corolla', '2020', 450.00, 6, 'Disco de freno ventilado delantero'),
            ('filtro de aceite', 'Toyota', 'Yaris', '2019', 60.00, 20, 'Filtro de aceite estándar'),
            ('bujias', 'Toyota', 'Yaris', '2017', 45.00, 25, 'Bujía de Iridio Denso'),
            ('pastillas de freno', 'Toyota', 'Hilux', '2021', 420.00, 8, 'Pastillas de freno heavy duty para trabajo pesado'),
            ('amortiguador', 'Toyota', 'Hilux', '2018', 920.00, 6, 'Amortiguador reinforced posterior'),

            # NISSAN
            ('filtro de aceite', 'Nissan', 'Sentra', '2019', 65.00, 15, 'Filtro de aceite motor 1.8L / 2.0L'),
            ('pastillas de freno', 'Nissan', 'Sentra', '2020', 310.00, 7, 'Pastillas de freno cerámicas silenciosas'),
            ('filtro de aire', 'Nissan', 'Frontier', '2018', 130.00, 9, 'Filtro de aire de alto flujo diésel/gasolina'),
            ('bomba de agua', 'Nissan', 'Versa', '2017', 380.00, 5, 'Bomba de agua de aluminio con empaque'),

            # MAZDA
            ('filtro de aceite', 'Mazda', 'Mazda 3', '2018', 75.00, 11, 'Filtro de aceite Skyactiv G'),
            ('pastillas de freno', 'Mazda', 'Mazda 3', '2019', 360.00, 8, 'Pastillas cerámicas de alto agarre'),
            ('amortiguador', 'Mazda', 'CX-5', '2020', 980.00, 4, 'Amortiguador delantero hidráulico gas'),

            # HYUNDAI / KIA
            ('filtro de aceite', 'Hyundai', 'Tucson', '2019', 70.00, 14, 'Filtro de aceite motor 2.0L'),
            ('pastillas de freno', 'Hyundai', 'Elantra', '2018', 290.00, 12, 'Pastillas de freno delanteras cerámicas'),
            ('filtro de aceite', 'Kia', 'Sportage', '2020', 70.00, 10, 'Filtro de aceite original spec'),
            ('batería', 'Kia', 'Rio', '2019', 750.00, 5, 'Batería 12V 500 CCA libre de mantenimiento')
        ]
        
        cursor.executemany("""
            INSERT INTO inventario (tipo_repuesto, marca, modelo, anio, precio, stock, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, repuestos_expandidos)

    cursor.execute("DROP VIEW IF EXISTS vista_inventario_publica;")
    cursor.execute("""
        CREATE VIEW vista_inventario_publica AS
        SELECT id, tipo_repuesto, marca, modelo, anio, precio, stock, descripcion
        FROM inventario;
    """)

    conn.commit()
    conn.close()

def obtener_conexion():
    inicializar_bd()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_info_tienda() -> dict:
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tienda LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception as e:
        print(f"[ERROR BD info_tienda]: {e}")
    
    return {
        "nombre": "Repuestos Don José",
        "direccion": "Ciudad de Guatemala",
        "telefono": "+502 1234-5678",
        "horario": "Lunes a Viernes: 8:00 AM – 6:00 PM | Sábados: 8:00 AM – 2:00 PM",
        "descripcion": "Especialistas en repuestos automotrices multimarca."
    }

def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.strip().lower()
    
    if texto.endswith("es") and len(texto) > 4:
        texto = texto[:-2]
    elif texto.endswith("s") and len(texto) > 3:
        texto = texto[:-1]
        
    return texto

def buscar_inventario(tipo: str = "", marca_vehiculo: str = "", modelo_vehiculo: str = "", anio: str = "") -> list[dict]:
    tipo_norm = normalizar_texto(tipo)
    marca_norm = marca_vehiculo.strip().lower()
    modelo_norm = modelo_vehiculo.strip().lower()
    anio_norm = str(anio).strip().lower()

    print(f"[DEBUG BD Query Input Original]: tipo='{tipo}', marca='{marca_vehiculo}', modelo='{modelo_vehiculo}', anio='{anio}'")

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        query = "SELECT * FROM vista_inventario_publica WHERE 1=1"
        params = []

        if tipo_norm and tipo_norm not in VALORES_IGNORAR:
            query += " AND (LOWER(tipo_repuesto) LIKE ? OR LOWER(descripcion) LIKE ?)"
            params.extend([f"%{tipo_norm}%", f"%{tipo_norm}%"])

        if marca_norm and marca_norm not in VALORES_IGNORAR:
            query += " AND LOWER(marca) LIKE ?"
            params.append(f"%{marca_norm}%")

        if modelo_norm and modelo_norm not in VALORES_IGNORAR:
            query += " AND LOWER(modelo) LIKE ?"
            params.append(f"%{modelo_norm}%")

        if anio_norm and anio_norm not in VALORES_IGNORAR:
            query += " AND (anio = ? OR LOWER(anio) LIKE ?)"
            params.extend([anio_norm, f"%{anio_norm}%"])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        resultados = [dict(r) for r in rows]
        print(f"[DEBUG BD Resultados Encontrados]: {len(resultados)} items.")
        return resultados

    except Exception as e:
        print(f"[ERROR BD]: Fallo al consultar la vista de inventario: {e}")
        return []