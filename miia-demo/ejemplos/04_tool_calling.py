"""04 · Tool calling a mano: el modelo NO ejecuta nada, solo pide que lo ejecutes tú.

Imprime los mensajes en bruto para ver el ciclo completo:
  usuario → modelo pide herramienta → tu código la ejecuta → modelo redacta la respuesta
"""
import json

from openai import OpenAI
from config import cargar_config

config = cargar_config()
client = OpenAI(base_url=config.base_url, api_key=config.api_key)
MODEL = config.model
NT = config.no_think_suffix


def ects_desde_horas(horas: float) -> float:
    """Convierte horas de trabajo del estudiante a créditos ECTS (criterio: 25 h = 1 ECTS)."""
    return round(horas / 25, 2)


TOOLS = [{
    "type": "function",
    "function": {
        "name": "ects_desde_horas",
        "description": "Convierte horas de trabajo del estudiante a créditos ECTS (25 h = 1 ECTS).",
        "parameters": {
            "type": "object",
            "properties": {"horas": {"type": "number", "description": "Horas de trabajo"}},
            "required": ["horas"],
        },
    },
}]

messages = [{"role": "user", "content": "¿Cuántos ECTS son 450 horas de trabajo?" + NT}]

r = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, temperature=config.temperature)
msg = r.choices[0].message

if not msg.tool_calls:
    print("El modelo respondió sin usar la herramienta:\n", msg.content)
    raise SystemExit

print("── El modelo pide ejecutar ──")
for c in msg.tool_calls:
    print(f"  {c.function.name}({c.function.arguments})")

# Repetimos el mensaje del asistente tal cual y añadimos el resultado de cada llamada.
messages.append({
    "role": "assistant",
    "content": msg.content or "",
    "tool_calls": [
        {"id": c.id, "type": "function",
         "function": {"name": c.function.name, "arguments": c.function.arguments}}
        for c in msg.tool_calls
    ],
})
for c in msg.tool_calls:
    args = json.loads(c.function.arguments)
    resultado = ects_desde_horas(**args)          # ← aquí manda tu código, no el modelo
    print(f"── Tu código devuelve: {resultado}")
    messages.append({"role": "tool", "tool_call_id": c.id, "content": str(resultado)})

r = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, temperature=config.temperature)
print("\n── Respuesta final ──")
print(r.choices[0].message.content)
