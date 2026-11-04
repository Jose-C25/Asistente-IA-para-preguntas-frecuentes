from app.database.connection import obtener_conexion
from app.database.repositories.cash_repo import registrar_ingreso_por_pedido

def registrar_pedido(cliente: str, vehiculo: str, direccion: str, metodo_pago: str = "Contra Entrega", total: float = 0.0, detalle_items: str = "") -> dict:
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (cliente, vehiculo, direccion, metodo_pago, total, detalle_items, estado)
            VALUES (?, ?, ?, 'Contra Entrega', ?, ?, 'Pendiente')
        """, (cliente, vehiculo, direccion, total, detalle_items))
        pedido_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"status": "exito", "pedido_id": pedido_id, "mensaje": f"Pedido #{pedido_id} registrado con pago Contra Entrega."}
    except Exception as e:
        print(f"[ERROR orders_repo registrar_pedido]: {e}")
        return {"status": "error", "mensaje": str(e)}

def obtener_pedidos_admin() -> list[dict]:
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos ORDER BY fecha DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[ERROR orders_repo obtener_pedidos]: {e}")
        return []

def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str) -> bool:
    """Actualiza el estado del pedido e impacta en la caja si se completa la entrega."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            conn.close()
            return False

        estado_anterior = pedido["estado"]
        cursor.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (nuevo_estado, pedido_id))
        conn.commit()
        conn.close()

        # Si cambió a 'Entregado' y antes no lo estaba, sumar automáticamente a la Caja Chica
        if nuevo_estado == "Entregado" and estado_anterior != "Entregado":
            registrar_ingreso_por_pedido(
                pedido_id=pedido["id"],
                monto=pedido["total"],
                descripcion=f"Cobro Contra Entrega - Pedido #{pedido['id']} ({pedido['cliente']})"
            )

        return True
    except Exception as e:
        print(f"[ERROR orders_repo actualizar_estado]: {e}")
        return False