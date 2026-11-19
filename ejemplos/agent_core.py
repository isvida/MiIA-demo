"""El bucle de un agente, completo. Es lo único que hace falta para entender OpenCode & cía.

    while True:
        respuesta = modelo(mensajes, herramientas)
        si no pide herramientas → terminar
        ejecutar cada herramienta pedida y añadir su resultado a los mensajes

Todo lo demás (permisos, sandbox, memoria, subagentes, skills) se construye alrededor.
"""
import json
from typing import Awaitable, Callable

from openai import AsyncOpenAI

MAX_RESULTADO = 4000   # recortar salidas largas: el contexto es un recurso escaso


async def run_agent(
    client: AsyncOpenAI,
    model: str,
    task: str,
    tools: list[dict],
    dispatch: Callable[[str, dict], Awaitable[str]],
    system: str = "Eres un agente. Usa las herramientas para completar la tarea y responde en español.",
    max_steps: int = 12,
    temperature: float = 0,
    no_think: bool = True,
) -> str:
    if no_think:
        system += " /no_think"      # Qwen3: responder sin la fase de razonamiento (en CPU ahorra minutos)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
    ]
    for paso in range(1, max_steps + 1):
        r = await client.chat.completions.create(
            model=model, messages=messages, tools=tools, tool_choice="auto", temperature=temperature
        )
        msg = r.choices[0].message

        if not msg.tool_calls:
            print(f"\n[paso {paso}] el modelo da por terminada la tarea")
            return msg.content or ""

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
            try:
                args = json.loads(c.function.arguments or "{}")
                print(f"[paso {paso}] → {c.function.name}({json.dumps(args, ensure_ascii=False)[:200]})")
                resultado = await dispatch(c.function.name, args)
            except Exception as e:     # el error vuelve al modelo: puede corregirse solo
                resultado = f"ERROR: {type(e).__name__}: {e}"
                print(f"[paso {paso}]   {resultado}")
            messages.append({
                "role": "tool",
                "tool_call_id": c.id,
                "content": str(resultado)[:MAX_RESULTADO],
            })

    return "(límite de pasos alcanzado sin terminar)"
