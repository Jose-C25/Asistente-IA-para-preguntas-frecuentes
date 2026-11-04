import logging
import os
from datetime import datetime
from app.database.connection import obtener_conexion

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configuración del logger de sistema en archivo
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def registrar_evento_seguridad(usuario: str, accion: str, detalles: str, ip: str = "127.0.0.1"):
    """Registra un evento de auditoría tanto en archivo físico como en SQLite."""
    mensaje = f"USUARIO: {usuario} | ACCIÓN: {accion} | DETALLES: {detalles} | IP: {ip}"
    logging.info(mensaje)

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs_auditoria (usuario, accion, detalles, ip)
            VALUES (?, ?, ?, ?)
        """, (usuario, accion, detalles, ip))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Fallo al registrar evento en BD: {e}")