from app.database.connection import obtener_conexion
from app.core.security import verificar_password, sanitizar_entrada

def autenticar_usuario(username: str, password_plano: str) -> dict:
    username_limpio = sanitizar_entrada(username)
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username_limpio,))
        usuario = cursor.fetchone()

        if not usuario:
            conn.close()
            return {"exito": False, "mensaje": "Usuario o contraseña incorrectos."}

        u_dict = dict(usuario)

        if u_dict["activo"] == 0 or u_dict["intentos_fallidos"] >= 5:
            conn.close()
            return {"exito": False, "mensaje": "Cuenta bloqueada por seguridad. Contacte al administrador."}

        if verificar_password(password_plano, u_dict["password_hash"]):
            cursor.execute("UPDATE usuarios SET intentos_fallidos = 0 WHERE id = ?", (u_dict["id"],))
            conn.commit()
            conn.close()
            return {
                "exito": True,
                "usuario": {
                    "id": u_dict["id"],
                    "username": u_dict["username"],
                    "nombre": u_dict["nombre"],
                    "rol": u_dict["rol"]
                }
            }
        else:
            nuevos_intentos = u_dict["intentos_fallidos"] + 1
            activo_estado = 0 if nuevos_intentos >= 5 else 1
            cursor.execute("UPDATE usuarios SET intentos_fallidos = ?, activo = ? WHERE id = ?", 
                           (nuevos_intentos, activo_estado, u_dict["id"]))
            conn.commit()
            conn.close()
            return {"exito": False, "mensaje": "Usuario o contraseña incorrectos."}

    except Exception as e:
        print(f"[ERROR users_repo autenticar]: {e}")
        return {"exito": False, "mensaje": "Error interno del sistema."}

def obtener_todos_los_usuarios() -> list[dict]:
    """Retorna la lista de usuarios del sistema con su estado actual."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, nombre, rol, activo, intentos_fallidos, creado_en FROM usuarios")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[ERROR users_repo obtener_todos]: {e}")
        return []

def desbloquear_usuario_admin(username: str) -> bool:
    """Restablece los intentos y reactiva la cuenta."""
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
        return True
    except Exception as e:
        print(f"[ERROR users_repo desbloquear]: {e}")
        return False