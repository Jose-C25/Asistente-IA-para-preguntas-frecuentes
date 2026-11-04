import time
import streamlit as st

DURACION_MAXIMA_SESION = 1800  # 30 minutos de inactividad

def validar_sesion_activa():
    """Invalida la sesión si ha superado el tiempo máximo de inactividad."""
    if st.session_state.get("authenticated"):
        ultima_actividad = st.session_state.get("last_activity", time.time())
        if time.time() - ultima_actividad > DURACION_MAXIMA_SESION:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.view_login = False
            st.warning("Su sesión ha expirado por inactividad.")
            st.rerun()
        else:
            st.session_state.last_activity = time.time()