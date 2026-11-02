from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend import procesar_consulta_con_function_calling

app = FastAPI(
    title="Repuestos Don José - API con Function Calling",
    version="2.0.0"
)

class MensajeCliente(BaseModel):
    mensaje: str

@app.post("/chat")
def chat_asistente(data: MensajeCliente):
    if not data.mensaje.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")
    
    respuesta = procesar_consulta_con_function_calling(data.mensaje)
    return {"respuesta": respuesta}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)