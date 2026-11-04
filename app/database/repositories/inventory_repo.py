from app.database.connection import obtener_conexion
from app.config import VALORES_IGNORAR

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
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[ERROR inventory_repo]: {e}")
        return []

def obtener_info_tienda() -> dict:
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tienda LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    except Exception as e:
        print(f"[ERROR inventory_repo info_tienda]: {e}")
        return {}