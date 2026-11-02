import streamlit as st
from backend import procesar_consulta_con_function_calling
from database import obtener_info_tienda, obtener_conexion

st.set_page_config(
    page_title="AETHER // Repuestos Don José",
    page_icon="⚡",
    layout="wide"
)

# Estilos CSS basados en la guía de diseño Aether (Dark Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

    /* Fondo general y colores de texto */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #0A0A0A !important;
        border-right: 1px solid #27272A !important;
    }

    /* Tipografía y encabezados */
    h1, h2, h3, .main-title {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
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

    /* Badges de metadatos */
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

    .sidebar-section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        color: #A1A1AA;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* Mensajes de Chat */
    [data-testid="stChatMessage"] {
        background-color: #111111 !important;
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Campo de entrada del Chat */
    [data-testid="stChatInput"] {
        background-color: #111111 !important;
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        border-bottom: 1px solid #27272A;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #A1A1AA;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 12px 16px;
    }

    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #FFFFFF !important;
        font-weight: 600;
    }

    /* Tablas Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #27272A !important;
        border-radius: 8px !important;
        background-color: #111111 !important;
    }

    hr {
        border-color: #27272A !important;
    }
    </style>
""", unsafe_allow_html=True)

info_tienda = obtener_info_tienda()

with st.sidebar:
    st.markdown('<div style="font-weight: 700; font-size: 1.2rem; letter-spacing: -0.02em;">AETHER // DON JOSÉ</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<p class="sidebar-section-title">Información del Local</p>', unsafe_allow_html=True)
    st.markdown(f"**Dirección:** {info_tienda.get('direccion', '1ra Calle 3-15, Zona 1')}")
    st.markdown(f"**Horario:** {info_tienda.get('horario', '8:00 a 17:30 hrs')}")
    st.markdown(f"**Teléfono:** {info_tienda.get('telefono', '7951-0000')}")
    
    st.markdown('<p class="sidebar-section-title">Estado del Sistema</p>', unsafe_allow_html=True)
    st.markdown('<div class="mono-badge">Function Calling Active</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-badge">SQLite Public View</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-badge">Multi-Model Auto-Fallback</div>', unsafe_allow_html=True)

tab_chat, tab_auditoria = st.tabs(["Atención al Cliente", "Auditoría de Inventario"])

with tab_chat:
    st.markdown('<div class="main-title">Asistente Virtual de Repuestos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Consulta disponibilidad, compatibilidad y precios en tiempo real.</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenido a Repuestos Don José. ¿En qué puedo ayudarle hoy?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escriba su consulta... (ej. ¿Tienes pastillas de freno para Honda Civic?)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base de datos..."):
                # Protección contra devoluciones None para prevenir TypeError
                respuesta_bot = procesar_consulta_con_function_calling(st.session_state.messages) or ""
                st.markdown(respuesta_bot)

        # Validación segura de cadenas contra mensajes de error temporales
        errores_frecuentes = ["límite de peticiones", "saturado", "interrupción", "error"]
        if respuesta_bot and not any(err in respuesta_bot.lower() for err in errores_frecuentes):
            st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})

with tab_auditoria:
    st.markdown("### Vista Pública de Inventario")
    st.caption("Estructura accesible por la herramienta de Function Calling (`vista_inventario_publica`).")
    
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, categoria, precio_venta, equivalencia, stock, ubicacion_estante FROM vista_inventario_publica")
            productos_publicos = [dict(fila) for fila in cursor.fetchall()]
            
            if productos_publicos:
                st.dataframe(productos_publicos)
            else:
                st.info("No hay registros en la vista pública.")

            st.markdown("---")
            st.markdown("### Tabla Privada (Restringida)")
            st.caption("Datos aislados fuera del alcance de la Inteligencia Artificial (`precio_costo`, `proveedor_id`).")
            
            cursor.execute("SELECT codigo, nombre, precio_costo, precio_venta, proveedor_id FROM productos")
            productos_privados = [dict(fila) for fila in cursor.fetchall()]
            st.dataframe(productos_privados)

    except Exception as e:
        st.error(f"Error al consultar la base de datos: {e}")