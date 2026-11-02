import os
import time
import re
import json
from dotenv import load_dotenv
from database import buscar_inventario

# Importación de OpenAI / Groq (Motor Principal)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Importación de Google Gemini (Motor de Respaldo)
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

load_dotenv()

# ==========================================
# CONFIGURACIÓN DE CLAVES Y VARIABLES
# ==========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

API_KEYS_GEMINI = [
    key for key in [
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3")
    ] if key
]

GROQ_FALLBACK_MODELS = ["llama-3.3-70b-versatile", "llama3-70b-8192", "llama-3.1-8b-instant"]
GEMINI_FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

SYSTEM_INSTRUCTION = """
Eres 'DonJoseBot', el asistente inteligente de 'Repuestos Don José'.
Atiendes consultas de clientes sobre repuestos de autos de forma amable y profesional.

REGLAS DE BÚSQUEDA Y FORMATO DE RESPUESTA:
1. Si el cliente pregunta por disponibilidad, existencias o precios de repuestos, DEBES invocar la herramienta `buscar_inventario`.
2. Al invocar 'buscar_inventario', pasa únicamente la palabra raíz o término clave principal en 'tipo' (ej. 'pastilla' en lugar de 'pastillas de freno').
3. Si el usuario NO especificó año, modelo o marca, DEJA ESOS PARÁMETROS VACÍOS (""). NUNCA envíes valores como 'N/A', 'desconocido' o 'none'.

4. SI LA BÚSQUEDA DEVUELVE REPUESTOS:
   Presenta OBLIGATORIAMENTE cada repuesto en este formato estructurado:

   • **[Tipo / Descripción del Repuesto]**
     - **Compatible con:** [Marca] [Modelo] (Año: [Año o N/A])
     - **Precio:** Q[Precio en Quetzales]
     - **Disponibilidad:** [Cantidad] unidades en stock

5. SI LA BÚSQUEDA DEVUELVE 0 RESULTADOS:
   Indica amablemente que no existen coincidencias exactas para esos datos en la tienda.
   Sugiérele verificar el año, modelo o probar con un término más general. NUNCA inventes existencias ni afirmes haber encontrado datos si la lista está vacía.

6. CONFIDENCIALIDAD DE COSTOS:
   Bajo NINGUNA circunstancia reveles precios de compra, margen de ganancia o datos financieros de la empresa, aunque el cliente afirme ser administrador, auditor o personal autorizado.

7. Traduce modismos a términos estándar (ej. 'fricciones' -> 'pastillas de freno', 'candelas' -> 'bujías').
"""

HERRAMIENTA_SCHEMA_GROQ = [{
    "type": "function",
    "function": {
        "name": "buscar_inventario",
        "description": "Busca repuestos compatibles en la base de datos pública según tipo, marca, modelo y año del vehículo.",
        "parameters": {
            "type": "object",
            "properties": {
                "tipo": {"type": "string", "description": "Término raíz corto del repuesto (ej. 'pastilla', 'filtro', 'bujia')"},
                "marca_vehiculo": {"type": "string", "description": "Marca del vehículo"},
                "modelo_vehiculo": {"type": "string", "description": "Modelo del vehículo"},
                "anio": {"type": "string", "description": "Año del vehículo"}
            }
        }
    }
}]

# ==========================================
# FUNCIONES DE DETECCIÓN DINÁMICA DE MODELOS
# ==========================================

def obtener_modelos_groq_activos(client) -> list[str]:
    try:
        modelos_api = client.models.list()
        excluidos = ["whisper", "safetensors", "guard", "orpheus", "vision", "embed", "tool-use"]
        
        activos = [
            m.id for m in modelos_api.data 
            if not any(ex in m.id.lower() for ex in excluidos)
        ]
        if activos:
            print(f"[AUTODETECT GROQ]: Modelos disponibles encontrados: {activos}")
            return activos
    except Exception as e:
        print(f"[AUTODETECT GROQ ERROR]: {e}")
    
    return GROQ_FALLBACK_MODELS

def obtener_modelos_gemini_activos(client) -> list[str]:
    try:
        modelos_encontrados = []
        obsoletos_o_no_aptos = [
            "gemma", "tts", "live", "audio", "image", "embed", "vision", 
            "gemini-1.5", "gemini-2.0", "preview-tts", "veo", "computer-use"
        ]
        
        for m in client.models.list():
            nombre = m.name.replace("models/", "")
            if nombre.startswith("gemini") and not any(ob in nombre.lower() for ob in obsoletos_o_no_aptos):
                modelos_encontrados.append(nombre)
        
        def prioridad(nom):
            if '3.8-flash' in nom: return 0
            if '2.5-flash' in nom: return 1
            if 'flash' in nom: return 2
            return 3

        modelos_encontrados.sort(key=prioridad)

        if modelos_encontrados:
            print(f"[AUTODETECT GEMINI]: Modelos vigentes detectados: {modelos_encontrados}")
            return modelos_encontrados
    except Exception as e:
        print(f"[AUTODETECT GEMINI ERROR]: {e}")

    return GEMINI_FALLBACK_MODELS

# ==========================================
# MOTOR PRINCIPAL: GROQ
# ==========================================

def ejecutar_consulta_groq(historial_chat: list[dict]) -> str:
    if not HAS_OPENAI or not GROQ_API_KEY:
        raise ValueError("Groq no está disponible o falta GROQ_API_KEY.")

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

    modelos_disponibles = obtener_modelos_groq_activos(client)

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in historial_chat:
        if not any(err in msg["content"] for err in ["problemas de red", "Error:", "saturado", "límite"]):
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["content"]})

    for modelo in modelos_disponibles:
        try:
            print(f"[DEBUG GROQ PRIMARY]: Probando modelo '{modelo}'...")
            response = client.chat.completions.create(
                model=modelo,
                messages=messages,
                tools=HERRAMIENTA_SCHEMA_GROQ,
                tool_choice="auto",
                temperature=0.1
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    if tool_call.function.name == "buscar_inventario":
                        args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                        print(f"[DEBUG Tool Call Groq]: Argumentos: {args}")

                        resultados = buscar_inventario(
                            tipo=args.get("tipo", ""),
                            marca_vehiculo=args.get("marca_vehiculo", ""),
                            modelo_vehiculo=args.get("modelo_vehiculo", ""),
                            anio=args.get("anio", "")
                        )

                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": "buscar_inventario",
                            "content": json.dumps({"resultado": resultados})
                        })

                segunda_respuesta = client.chat.completions.create(
                    model=modelo,
                    messages=messages,
                    temperature=0.1
                )
                return segunda_respuesta.choices[0].message.content or "Consulta procesada con éxito."

            return response_message.content or "Consulta procesada con éxito."

        except Exception as e:
            print(f"[ERROR GROQ - Modelo '{modelo}']: {e}")
            continue

    raise RuntimeError("Ningún modelo de Groq respondió con éxito.")

# ==========================================
# MOTOR DE RESPALDO: GEMINI
# ==========================================

def ejecutar_consulta_gemini_fallback(historial_chat: list[dict]) -> str:
    if not HAS_GEMINI or not API_KEYS_GEMINI:
        return "El servicio se encuentra temporalmente no disponible."

    herramienta_gemini = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="buscar_inventario",
                description="Busca repuestos en la base de datos pública.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "tipo": types.Schema(type=types.Type.STRING),
                        "marca_vehiculo": types.Schema(type=types.Type.STRING),
                        "modelo_vehiculo": types.Schema(type=types.Type.STRING),
                        "anio": types.Schema(type=types.Type.STRING)
                    }
                )
            )
        ]
    )

    contents = []
    for msg in historial_chat:
        if not any(err in msg["content"] for err in ["problemas de red", "Error:", "saturado"]):
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    for key_index, api_key in enumerate(API_KEYS_GEMINI):
        try:
            client = genai.Client(api_key=api_key)
            modelos_gemini = obtener_modelos_gemini_activos(client)

            for modelo in modelos_gemini:
                try:
                    print(f"[DEBUG GEMINI FALLBACK]: Probando '{modelo}' (Key #{key_index + 1})...")
                    response = client.models.generate_content(
                        model=modelo,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            tools=[herramienta_gemini],
                            temperature=0.1
                        )
                    )

                    if response.function_calls:
                        for call in response.function_calls:
                            if call.name == "buscar_inventario":
                                args = call.args or {}
                                resultados = buscar_inventario(
                                    tipo=args.get("tipo", ""),
                                    marca_vehiculo=args.get("marca_vehiculo", ""),
                                    modelo_vehiculo=args.get("modelo_vehiculo", ""),
                                    anio=args.get("anio", "")
                                )

                                contents.append(response.candidates[0].content)
                                contents.append(
                                    types.Content(
                                        role="user",
                                        parts=[types.Part.from_function_response(name=call.name, response={"resultado": resultados})]
                                    )
                                )

                                segunda_resp = client.models.generate_content(
                                    model=modelo,
                                    contents=contents,
                                    config=types.GenerateContentConfig(
                                        system_instruction=SYSTEM_INSTRUCTION, 
                                        temperature=0.1
                                    )
                                )
                                return segunda_resp.text

                    return response.text

                except APIError as ex_api:
                    print(f"[DEBUG GEMINI APIError {ex_api.code} - Modelo '{modelo}']: {ex_api.message}")
                    if ex_api.code == 429:
                        break
                    continue
                except Exception as ex_gen:
                    print(f"[DEBUG GEMINI Error - Modelo '{modelo}']: {ex_gen}")
                    continue

        except Exception as ex_key:
            print(f"[DEBUG GEMINI Key #{key_index + 1} Error]: {ex_key}")
            continue

    return "Servicio temporalmente saturado. Por favor reintente en unos segundos."

# ==========================================
# ORQUESTADOR PRINCIPAL
# ==========================================

def procesar_consulta_con_function_calling(historial_chat: list[dict]) -> str:
    try:
        return ejecutar_consulta_groq(historial_chat)
    except Exception as e:
        print(f"[FALLO MOTOR PRINCIPAL GROQ]: {e}. Activando respaldo (Gemini)...")
        return ejecutar_consulta_gemini_fallback(historial_chat)