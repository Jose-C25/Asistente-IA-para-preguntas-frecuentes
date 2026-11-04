import streamlit as st
from app.database.repositories.users_repo import autenticar_usuario

def render_login():
    st.markdown('<div class="main-title">Acceso de Personal Autorizado</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ingrese sus credenciales para acceder a los módulos de administración y caja.</div>', unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])

    with col_l2:
        with st.form("form_login"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            btn_ingresar = st.form_submit_button("Ingresar al Sistema")

            if btn_ingresar:
                if username and password:
                    res = autenticar_usuario(username, password)
                    if res["exito"]:
                        user = res["usuario"]
                        st.session_state.authenticated = True
                        st.session_state.username = user["username"]
                        st.session_state.user_nombre = user["nombre"]
                        st.session_state.user_role = user["rol"]
                        st.session_state.view_login = False
                        st.success(f"Bienvenido, {user['nombre']}")
                        st.rerun()
                    else:
                        st.error(res["mensaje"])
                else:
                    st.warning("Por favor complete todos los campos.")

        if st.button("← Volver al Chat Público"):
            st.session_state.view_login = False
            st.rerun()