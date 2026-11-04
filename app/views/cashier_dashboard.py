import streamlit as st
import pandas as pd
from app.database.repositories.orders_repo import obtener_pedidos_admin, actualizar_estado_pedido
from app.database.repositories.cash_repo import obtener_o_crear_caja_hoy, obtener_movimientos_caja_hoy

def render_cashier_dashboard():
    st.markdown('<div class="main-title">Panel de Caja y Operaciones</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Sesión activa como **{st.session_state.get("user_nombre")}** (`EMPLEADO/CAJERO`)</div>', unsafe_allow_html=True)

    # Métricas de Caja del Día
    caja_hoy = obtener_o_crear_caja_hoy()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fondo Inicial", f"Q{caja_hoy['monto_inicial']:,.2f}")
    m2.metric("Ingresos Cobrados", f"Q{caja_hoy['ingresos_efectivo']:,.2f}")
    m3.metric("Saldo Actual en Caja", f"Q{caja_hoy['saldo_actual']:,.2f}")
    m4.metric("Estado de Caja", caja_hoy['estado'].upper())

    st.markdown("---")

    t_pedidos, t_arqueo = st.tabs(["Gestión de Despachos", "Movimientos de Caja Chica"])

    with t_pedidos:
        st.markdown("### Pedidos Pendientes de Entrega y Cobro")
        pedidos = obtener_pedidos_admin()

        if pedidos:
            df_pedidos = pd.DataFrame(pedidos)
            st.dataframe(df_pedidos, use_container_width=True)

            st.markdown("#### Cambiar Estado y Procesar Cobro")
            c_id, c_est, c_btn = st.columns([1, 2, 1])
            p_id = c_id.number_input("ID del Pedido", min_value=1, step=1, key="cashier_p_id")
            n_estado = c_est.selectbox("Nuevo Estado", ["Pendiente", "En Camino", "Entregado", "Cancelado"], key="cashier_n_est")

            if c_btn.button("Actualizar Estado", key="btn_update_cashier"):
                if actualizar_estado_pedido(int(p_id), n_estado):
                    if n_estado == "Entregado":
                        st.success(f"¡Pedido #{p_id} marcado como ENTREGADO! Monto sumado a Caja Chica.")
                    else:
                        st.info(f"Pedido #{p_id} actualizado a '{n_estado}'.")
                    st.rerun()
                else:
                    st.error("No se pudo actualizar el pedido.")
        else:
            st.info("No hay pedidos registrados.")

    with t_arqueo:
        st.markdown("### Historial de Transacciones de Caja (Hoy)")
        movimientos = obtener_movimientos_caja_hoy()
        if movimientos:
            st.dataframe(pd.DataFrame(movimientos), use_container_width=True)
        else:
            st.info("No se han registrado cobros en la caja del día de hoy.")