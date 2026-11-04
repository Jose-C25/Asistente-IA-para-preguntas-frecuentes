# desbloquear.py
from app.database.connection import obtener_conexion

def desbloquear_cuenta(username: str = "admin"):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios 
            SET intentos_fallidos = 0, activo = 1 
            WHERE username = ?
        """, (username,))
        conn.commit()
        conn.close()
        print(f"✓ Usuario '{username}' desbloqueado exitosamente.")
    except Exception as e:
        print(f"❌ Error al desbloquear usuario: {e}")

if __name__ == "__main__":
    desbloquear_cuenta("admin")