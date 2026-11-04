import streamlit as st
from app.database.schema import inicializar_bd
from app.database.repositories.inventory_repo import obtener_info_tienda
from app.services.llm_orchestrator import procesar_consulta_con_function_calling
from app.views.login_view import render_login
from app.views.admin_dashboard import render_admin_dashboard
from app.views.cashier_dashboard import render_cashier_dashboard

# Inicialización al arrancar
inicializar_bd()

st.set_page_config(
    page_title="AETHER // Repuestos Don José",
    page_icon="⚡",
    layout="wide"
)

# Estilos CSS AETHER (Dark Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #0A0A0A !important;
        border-right: 1px solid #27272A !important;
    }

    .main-title {
        font-size: 1.85rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #FFFFFF;
    }

    .subtitle {
        color: #A1A1AA;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    .mono-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        color: #A1A1AA;
        background-color: #111111;
        border: 1px solid #27272A;
        padding: 6px 12px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 8px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    [data-testid="stChatMessage"] {
        background-color: #111111 !important;
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatInput"] {
        background-color: #111111 !important;
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #27272A !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Estado de Sesión Seguro
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.view_login = False

info_tienda = obtener_info_tienda()

with st.sidebar:
    st.markdown('<div style="font-weight: 700; font-size: 1.2rem; letter-spacing: -0.02em;">AETHER // DON JOSÉ</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**Dirección:** {info_tienda.get('direccion', 'Zona 1, Barrio San Juan, San Juan Chamelco, Alta Verapaz')}")
    st.markdown(f"**Horario:** {info_tienda.get('horario', '8:00 a 18:00 hrs')}")
    st.markdown(f"**Teléfono:** {info_tienda.get('telefono', '+502 1234-5678')}")
    st.markdown("---")
    st.markdown('<div class="mono-badge">OWASP Security Active</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-badge">Cash Control Active</div>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.authenticated:
        if st.button("🔑 Acceso Personal"):
            st.session_state.view_login = True
            st.rerun()
    else:
        st.markdown(f"Usuario: **{st.session_state.username}**")
        st.markdown(f"Rol: `<{st.session_state.user_role.upper()}>`", unsafe_allow_html=True)
        if st.button("🔒 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.view_login = False
            st.rerun()

# ROUTER DE VISTAS POR ROL
if st.session_state.view_login and not st.session_state.authenticated:
    render_login()
elif st.session_state.authenticated:
    if st.session_state.user_role == "admin":
        render_admin_dashboard()
    elif st.session_state.user_role == "empleado":
        render_cashier_dashboard()
else:
    # CHAT PÚBLICO (PÁGINA PRINCIPAL)
    st.markdown('<div class="main-title">Asistente Virtual de Repuestos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Consulta disponibilidad, compatibilidad y realiza tus pedidos contra entrega.</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenido a Repuestos Don José. ¿En qué puedo ayudarle hoy?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escriba su consulta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base de datos..."):
                respuesta_bot = procesar_consulta_con_function_calling(st.session_state.messages) or ""
                st.markdown(respuesta_bot)

        if respuesta_bot:
            st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})