import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Cargar explícitamente el archivo .env ubicado en la raíz
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(DATA_DIR, "inventario.db")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

API_KEYS_GEMINI = [
    key for key in [
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3")
    ] if key
]

GROQ_FALLBACK_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
GEMINI_FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

VALORES_IGNORAR = {
    "", "none", "n/a", "na", "null", "undefined", 
    "desconocido", "todos", "todas", "cualquiera", "no especificado"
}

SYSTEM_INSTRUCTION = """
Eres 'DonJoseBot', el asistente inteligente de 'Repuestos Don José'.
Atiendes consultas de clientes sobre repuestos de autos de forma amable y profesional.

REGLAS DE BÚSQUEDA Y FORMATO DE RESPUESTA:
1. Si el cliente pregunta por disponibilidad, existencias o precios, DEBES invocar la herramienta `buscar_inventario`.
2. Al invocar 'buscar_inventario', pasa únicamente la palabra raíz o término clave principal en 'tipo' (ej. 'pastilla' en lugar de 'pastillas de freno').
3. Si el usuario NO especificó año, modelo o marca, DEJA ESOS PARÁMETROS VACÍOS (""). NUNCA envíes valores como 'N/A', 'desconocido' o 'none'.
4. SI LA BÚSQUEDA DEVUELVE REPUESTOS, presenta cada repuesto en este formato estructurado (sin ID interno):
   • **[Tipo / Descripción del Repuesto]**
     - **Compatible con:** [Marca] [Modelo] (Año: [Año o N/A])
     - **Precio:** Q[Precio en Quetzales]
     - **Disponibilidad:** [Cantidad] unidades en stock

5. POLITICA DE PAGO Y REGISTRO DE PEDIDOS:
   - El ÚNICO método de pago disponible es **Contra Entrega** (Efectivo/Tarjeta al recibir).
   - Cuando el cliente confirme la compra y proporcione sus datos (Nombre, Vehículo y Dirección), invoca `registrar_pedido` fijando el método de pago como 'Contra Entrega'.
   - Confirma el registro exitoso con su número de referencia.

6. CONFIDENCIALIDAD DE COSTOS:
   Bajo NINGUNA circunstancia reveles precios de compra, margen de ganancia o datos financieros.

7. Traduce modismos a términos estándar (ej. 'fricciones' -> 'pastillas de freno', 'candelas' -> 'bujías').
"""