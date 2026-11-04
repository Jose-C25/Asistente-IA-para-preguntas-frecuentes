import streamlit as st
import pandas as pd
from app.database.repositories.orders_repo import obtener_pedidos_admin, actualizar_estado_pedido
from app.database.repositories.cash_repo import obtener_o_crear_caja_hoy, obtener_movimientos_caja_hoy
from app.database.repositories.users_repo import obtener_todos_los_usuarios, desbloquear_usuario_admin
from app.database.connection import obtener_conexion

def render_admin_dashboard():
    st.markdown('<div class="main-title">Panel de Control General</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Sesión activa como **{st.session_state.get("user_nombre", "Administrador")}** (`ADMINISTRADOR`)</div>', unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Pedidos y Entregas", "Inventario & Costos (CRUD)", "Arqueo de Caja Chica", "Gestión de Usuarios"])

    # SUB-PESTAÑA 1: PEDIDOS
    with t1:
        st.markdown("### Monitoreo de Pedidos")
        pedidos = obtener_pedidos_admin()
        if pedidos:
            df = pd.DataFrame(pedidos)
            col_a, col_b = st.columns(2)
            col_a.metric("Total Pedidos", len(pedidos))
            col_b.metric("Ventas Totales", f"Q{df['total'].sum():,.2f}")

            st.dataframe(df, use_container_width=True)

            st.markdown("#### Cambiar Estado del Pedido")
            col_id, col_est, col_btn = st.columns([1, 2, 1])
            pid = col_id.number_input("ID Pedido", min_value=1, step=1, key="admin_pid")
            est = col_est.selectbox("Estado", ["Pendiente", "En Camino", "Entregado", "Cancelado"], key="admin_est")

            if col_btn.button("Guardar Estado", key="admin_btn_est"):
                if actualizar_estado_pedido(int(pid), est):
                    st.success(f"Pedido #{pid} actualizado.")
                    st.rerun()
        else:
            st.info("No existen pedidos registrados.")

    # SUB-PESTAÑA 2: INVENTARIO & COSTOS
    with t2:
        st.markdown("### Gestión de Inventario Completo")
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo_repuesto, marca, modelo, anio, precio AS precio_venta, precio_costo, stock, descripcion FROM inventario ORDER BY id DESC")
            items = [dict(r) for r in cursor.fetchall()]
            conn.close()

            if items:
                df_inv = pd.DataFrame(items)
                df_inv["margen_quetzales"] = df_inv["precio_venta"] - df_inv["precio_costo"]
                st.dataframe(df_inv, use_container_width=True)

            st.markdown("---")
            st.markdown("#### Agregar Nuevo Repuesto")
            with st.form("form_nuevo_prod"):
                f1, f2 = st.columns(2)
                tipo = f1.text_input("Categoría / Tipo (ej. pastillas de freno)")
                marca = f2.text_input("Marca del Vehículo")

                f3, f4 = st.columns(2)
                modelo = f3.text_input("Modelo del Vehículo")
                anio = f4.text_input("Año")

                f5, f6, f7 = st.columns(3)
                prc_v = f5.number_input("Precio Venta (Q)", min_value=0.0, step=10.0)
                prc_c = f6.number_input("Precio Costo (Q)", min_value=0.0, step=10.0)
                stk = f7.number_input("Stock Inicial", min_value=1, step=1)

                desc = st.text_area("Descripción")
                submit = st.form_submit_button("Guardar en Inventario")

                if submit and tipo and marca and modelo:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO inventario (tipo_repuesto, marca, modelo, anio, precio, precio_costo, stock, descripcion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (tipo, marca, modelo, anio, prc_v, prc_c, stk, desc))
                    conn.commit()
                    conn.close()
                    st.success("Repuesto ingresado al catálogo.")
                    st.rerun()
        except Exception as e:
            st.error(f"Error inventario: {e}")

    # SUB-PESTAÑA 3: CAJA CHICA
    with t3:
        st.markdown("### Arqueo y Balance de Caja Chica")
        caja = obtener_o_crear_caja_hoy()
        c1, c2, c3 = st.columns(3)
        c1.metric("Fondo Inicial", f"Q{caja['monto_inicial']:,.2f}")
        c2.metric("Ingresos Hoy", f"Q{caja['ingresos_efectivo']:,.2f}")
        c3.metric("Saldo Final Actual", f"Q{caja['saldo_actual']:,.2f}")

        st.markdown("#### Movimientos del Día")
        movs = obtener_movimientos_caja_hoy()
        if movs:
            st.dataframe(pd.DataFrame(movs), use_container_width=True)
        else:
            st.info("Sin registros de caja para el día de hoy.")

    # SUB-PESTAÑA 4: GESTIÓN DE USUARIOS Y DESBLOQUEO
    with t4:
        st.markdown("### Control de Usuarios y Seguridad")
        usuarios = obtener_todos_los_usuarios()
        if usuarios:
            st.dataframe(pd.DataFrame(usuarios), use_container_width=True)

            st.markdown("---")
            st.markdown("#### Desbloquear Cuenta de Usuario")
            bloqueados = [u["username"] for u in usuarios if u["activo"] == 0 or u["intentos_fallidos"] >= 5]
            
            if bloqueados:
                col_usr, col_btn = st.columns([2, 1])
                user_select = col_usr.selectbox("Seleccionar Usuario Bloqueado", bloqueados)
                
                if col_btn.button("🔓 Desbloquear Usuario"):
                    if user_select and desbloquear_usuario_admin(user_select):
                        st.success(f"La cuenta del usuario '{user_select}' ha sido reactivada correctamente.")
                        st.rerun()
            else:
                st.info("No hay usuarios bloqueados actualmente.")
        else:
            st.info("No hay registros de usuarios en la base de datos.")