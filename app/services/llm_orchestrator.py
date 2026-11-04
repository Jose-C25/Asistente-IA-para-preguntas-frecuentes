import json
from app.config import (
    GROQ_API_KEY, 
    API_KEYS_GEMINI, 
    SYSTEM_INSTRUCTION, 
    GROQ_FALLBACK_MODELS, 
    GEMINI_FALLBACK_MODELS
)
from app.services.tools import HERRAMIENTAS_GROQ, ejecutar_herramienta

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


def obtener_modelos_groq_activos(client) -> list[str]:
    """Detecta dinámicamente qué modelos de chat están disponibles en la API de Groq."""
    try:
        modelos_api = client.models.list()
        excluidos = ["whisper", "safetensors", "guard", "orpheus", "vision", "embed", "tool-use"]
        activos = [m.id for m in modelos_api.data if not any(ex in m.id.lower() for ex in excluidos)]
        if activos:
            print(f"[AUTODETECT GROQ]: Modelos disponibles: {activos}")
            return activos
    except Exception as e:
        print(f"[AUTODETECT GROQ ERROR]: {e}")
    return GROQ_FALLBACK_MODELS


def obtener_modelos_gemini_activos(client) -> list[str]:
    """Detecta dinámicamente qué modelos válidos de Gemini están disponibles."""
    try:
        modelos = []
        obsoletos = ["gemma", "tts", "live", "audio", "image", "embed", "vision", "gemini-1.5", "gemini-2.0", "veo"]
        for m in client.models.list():
            nombre = m.name.replace("models/", "")
            if nombre.startswith("gemini") and not any(ob in nombre.lower() for ob in obsoletos):
                modelos.append(nombre)
        
        def prioridad(nom):
            if '3.8-flash' in nom: return 0
            if '2.5-flash' in nom: return 1
            if 'flash' in nom: return 2
            return 3

        modelos.sort(key=prioridad)
        if modelos:
            return modelos
    except Exception as e:
        print(f"[AUTODETECT GEMINI ERROR]: {e}")
    return GEMINI_FALLBACK_MODELS


def ejecutar_consulta_groq(historial_chat: list[dict]) -> str:
    """Ejecuta consulta con Groq detectando dinámicamente los modelos habilitados."""
    if not HAS_OPENAI or not GROQ_API_KEY:
        raise ValueError("Groq no disponible o sin API Key.")

    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
    modelos = obtener_modelos_groq_activos(client)

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in historial_chat:
        if not any(err in msg["content"] for err in ["Error:", "saturado", "límite"]):
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["content"]})

    for modelo in modelos:
        try:
            print(f"[DEBUG GROQ PRIMARY]: Probando modelo '{modelo}'...")
            response = client.chat.completions.create(
                model=modelo,
                messages=messages,
                tools=HERRAMIENTAS_GROQ,
                tool_choice="auto",
                temperature=0.1
            )

            response_msg = response.choices[0].message
            if response_msg.tool_calls:
                messages.append(response_msg)
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                    print(f"[DEBUG Tool Call Groq]: {func_name} | Args: {args}")

                    res_tool = ejecutar_herramienta(func_name, args)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(res_tool)
                    })

                second_resp = client.chat.completions.create(
                    model=modelo,
                    messages=messages,
                    temperature=0.1
                )
                return second_resp.choices[0].message.content or "Consulta procesada con éxito."

            return response_msg.content or "Consulta procesada con éxito."

        except Exception as e:
            print(f"[ERROR GROQ - Modelo '{modelo}']: {e}")
            continue

    raise RuntimeError("Ningún modelo de Groq respondió con éxito.")


def ejecutar_consulta_gemini_fallback(historial_chat: list[dict]) -> str:
    """Motor de respaldo en Gemini si Groq falla completamente."""
    if not HAS_GEMINI or not API_KEYS_GEMINI:
        return "El servicio no está disponible en este momento."

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
            ),
            types.FunctionDeclaration(
                name="registrar_pedido",
                description="Registra una compra confirmada.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "cliente": types.Schema(type=types.Type.STRING),
                        "vehiculo": types.Schema(type=types.Type.STRING),
                        "direccion": types.Schema(type=types.Type.STRING),
                        "total": types.Schema(type=types.Type.NUMBER),
                        "detalle_items": types.Schema(type=types.Type.STRING)
                    },
                    required=["cliente", "vehiculo", "direccion", "total"]
                )
            )
        ]
    )

    contents = []
    for msg in historial_chat:
        if not any(err in msg["content"] for err in ["Error:", "saturado"]):
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
                            res_tool = ejecutar_herramienta(call.name, call.args or {})
                            contents.append(response.candidates[0].content)
                            contents.append(
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_function_response(name=call.name, response=res_tool)]
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
                    print(f"[DEBUG GEMINI APIError {ex_api.code} - '{modelo}']: {ex_api.message}")
                    if ex_api.code == 429:
                        break
                    continue
                except Exception as ex:
                    print(f"[DEBUG GEMINI Error - '{modelo}']: {ex}")
                    continue

        except Exception as ex_key:
            print(f"[DEBUG GEMINI Key Error]: {ex_key}")
            continue

    return "Servicio temporalmente saturado. Por favor reintente en unos segundos."


def procesar_consulta_con_function_calling(historial_chat: list[dict]) -> str:
    """Orquestador principal."""
    try:
        return ejecutar_consulta_groq(historial_chat)
    except Exception as e:
        print(f"[FALLO GROQ PRINCIPAL]: {e}. Activando Gemini Fallback...")
        return ejecutar_consulta_gemini_fallback(historial_chat)