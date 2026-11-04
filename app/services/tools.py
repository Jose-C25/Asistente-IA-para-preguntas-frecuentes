import json
from app.database.repositories.inventory_repo import buscar_inventario
from app.database.repositories.orders_repo import registrar_pedido

HERRAMIENTAS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "buscar_inventario",
            "description": "Busca repuestos compatibles en la base de datos pública según tipo, marca, modelo y año.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "description": "Término raíz del repuesto"},
                    "marca_vehiculo": {"type": "string", "description": "Marca del vehículo"},
                    "modelo_vehiculo": {"type": "string", "description": "Modelo del vehículo"},
                    "anio": {"type": "string", "description": "Año del vehículo"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_pedido",
            "description": "Registra una compra confirmada con pago Contra Entrega.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente": {"type": "string", "description": "Nombre del cliente"},
                    "vehiculo": {"type": "string", "description": "Vehículo (marca, modelo, año)"},
                    "direccion": {"type": "string", "description": "Dirección completa"},
                    "total": {"type": "number", "description": "Monto total en Quetzales"},
                    "detalle_items": {"type": "string", "description": "Resumen de repuestos"}
                },
                "required": ["cliente", "vehiculo", "direccion", "total"]
            }
        }
    }
]

def ejecutar_herramienta(nombre_func: str, args: dict) -> dict:
    if nombre_func == "buscar_inventario":
        return {
            "resultado": buscar_inventario(
                tipo=args.get("tipo", ""),
                marca_vehiculo=args.get("marca_vehiculo", ""),
                modelo_vehiculo=args.get("modelo_vehiculo", ""),
                anio=args.get("anio", "")
            )
        }
    elif nombre_func == "registrar_pedido":
        return registrar_pedido(
            cliente=args.get("cliente", "Cliente General"),
            vehiculo=args.get("vehiculo", "N/A"),
            direccion=args.get("direccion", "N/A"),
            total=float(args.get("total", 0.0)),
            detalle_items=args.get("detalle_items", "")
        )
    return {"error": f"Herramienta '{nombre_func}' no válida."}