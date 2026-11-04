import sqlite3
from app.config import DB_PATH

def obtener_conexion():
    """Obtiene una conexión configurada para devolver filas como diccionarios."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn