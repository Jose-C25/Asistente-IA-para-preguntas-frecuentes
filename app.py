import os
from dotenv import load_dotenv
from database import obtener_info_tienda, buscar_producto_publico, guardar_historial

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")


def procesar_mensaje_con_ia(mensaje_usuario: str) -> str:
    # Obtener contexto público desde la base de datos
    info_tienda = obtener_info_tienda()
    productos = buscar_producto_publico(mensaje_usuario)
    
    txt_tienda = f"Dirección: {info_tienda.get('direccion')}. Horario: {info_tienda.get('horario')}. Teléfono: {info_tienda.get('telefono')}."
    
    if productos:
        prod = productos[0]
        txt_prod = f"Producto Encontrado: Código {prod[0]} - {prod[1]} ({prod[2]}). Precio público: Q{prod[3]}. Compatibilidad: {prod[4]}. Stock: {prod[5]} unidades."
    else:
        txt_prod = "No se encontraron repuestos específicos bajo esa búsqueda."

    prompt_sistema = f"""
    Eres 'RepuBot', asistente virtual de 'Repuestos Don Jose'.
    Saluda al cliente y responde a su consulta usando ÚNICAMENTE estos datos autorizados:
    [DATOS TIENDA]: {txt_tienda}
    [DATOS PRODUCTO]: {txt_prod}
    
    Reglas de Seguridad:
    1. Si te preguntan por precios de costo o proveedores, di amablemente que es información confidencial.
    2. Sé breve, profesional y amigable.
    """

    try:
        from google import genai
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{prompt_sistema}\n\nCliente: {mensaje_usuario}"
        )
        respuesta = response.text
    except Exception:
        respuesta = f"¡Hola! Soy RepuBot. Sobre tu consulta: {txt_prod} (Dirección del local: {info_tienda.get('direccion')})"

    guardar_historial(mensaje_usuario, respuesta)
    return respuesta


def iniciar_chat():

    print("      ASISTENTE VIRTUAL - REPUESTOS DON JOSÉ         ")
    print("Escribe 'salir' para finalizar la demo.\n")

    while True:
        usuario_input = input("Cliente: ")
        if usuario_input.lower().strip() in ["salir", "exit"]:
            print("\n¡Gracias por usar RepuBot! Hasta luego.")
            break
            
        if not usuario_input.strip():
            continue

        respuesta_bot = procesar_mensaje_con_ia(usuario_input)
        print(f"\nRepuBot: {respuesta_bot}\n")
        print("-" * 54)

if __name__ == "__main__":
    iniciar_chat()