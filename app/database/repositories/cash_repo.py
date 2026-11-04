from app.database.connection import obtener_conexion

def obtener_o_crear_caja_hoy() -> dict:
    """Obtiene el registro de caja del día o abre una nueva si no existe."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM caja WHERE fecha = DATE('now', 'localtime')")
        row = cursor.fetchone()

        if not row:
            # Obtener el saldo final de la caja anterior como monto inicial si existe
            cursor.execute("SELECT saldo_actual FROM caja ORDER BY id DESC LIMIT 1")
            prev_row = cursor.fetchone()
            saldo_inicial = prev_row["saldo_actual"] if prev_row else 0.0

            cursor.execute("""
                INSERT INTO caja (monto_inicial, ingresos_efectivo, egresos, saldo_actual, fecha, estado)
                VALUES (?, 0.0, 0.0, ?, DATE('now', 'localtime'), 'abierta')
            """, (saldo_inicial, saldo_inicial))
            conn.commit()
            
            cursor.execute("SELECT * FROM caja WHERE id = ?", (cursor.lastrowid,))
            row = cursor.fetchone()

        conn.close()
        return dict(row)
    except Exception as e:
        print(f"[ERROR cash_repo obtener_caja]: {e}")
        return {"id": 0, "monto_inicial": 0.0, "ingresos_efectivo": 0.0, "egresos": 0.0, "saldo_actual": 0.0, "estado": "cerrada"}

def registrar_ingreso_por_pedido(pedido_id: int, monto: float, descripcion: str) -> bool:
    """Registra automáticamente el ingreso de dinero en caja cuando un pedido 'Contra Entrega' se cobra/entrega."""
    try:
        caja = obtener_o_crear_caja_hoy()
        caja_id = caja["id"]
        nuevo_ingreso = caja["ingresos_efectivo"] + monto
        nuevo_saldo = caja["saldo_actual"] + monto

        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Actualizar total de la caja del día
        cursor.execute("""
            UPDATE caja 
            SET ingresos_efectivo = ?, saldo_actual = ? 
            WHERE id = ?
        """, (nuevo_ingreso, nuevo_saldo, caja_id))

        # Crear ticket de movimiento en historial
        cursor.execute("""
            INSERT INTO movimientos_caja (caja_id, pedido_id, tipo, monto, descripcion)
            VALUES (?, ?, 'ingreso_pedido', ?, ?)
        """, (caja_id, pedido_id, monto, descripcion))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR cash_repo registrar_ingreso]: {e}")
        return False

def obtener_movimientos_caja_hoy() -> list[dict]:
    """Retorna los movimientos financieros del día actual."""
    try:
        caja = obtener_o_crear_caja_hoy()
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, p.cliente 
            FROM movimientos_caja m 
            LEFT JOIN pedidos p ON m.pedido_id = p.id 
            WHERE m.caja_id = ? 
            ORDER BY m.fecha DESC
        """, (caja["id"],))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[ERROR cash_repo movimientos]: {e}")
        return []