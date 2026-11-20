"""06 · El mismo agente, pero las herramientas se DESCUBREN por MCP.

    python ejemplos/06_agente_mcp.py
    python ejemplos/06_agente_mcp.py "tu tarea..."

Compara con 05: el bucle (agent_core.py) no cambia. Solo cambia de dónde salen las
herramientas: en vez de definirlas a mano, se las pedimos al servidor MCP.
"""
import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import AsyncOpenAI

from agent_core import run_agent
from config import cargar_config

MCP_URL = os.getenv("MCP_URL", "http://localhost:8001/mcp")
TAREA = sys.argv[1] if len(sys.argv) > 1 else (
    "Dime qué asignaturas tiene la especialidad de IoT del máster y crea un ticket de prioridad "
    "baja titulado 'Revisar temario IoT' cuya descripción las enumere. Después lista los tickets."
)


async def main():
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as mcp:
            await mcp.initialize()

            # 1) Descubrimiento: el servidor nos dice qué sabe hacer.
            descubiertas = (await mcp.list_tools()).tools
            print("Herramientas descubiertas por MCP:")
            for t in descubiertas:
                print(f"  - {t.name}: {(t.description or '').splitlines()[0]}")
            print("Recursos:", [str(r.uri) for r in (await mcp.list_resources()).resources])
            print("Prompts: ", [p.name for p in (await mcp.list_prompts()).prompts])

            # 2) Traducción: esquema MCP → esquema de herramientas de la API OpenAI (casi idénticos).
            tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema,
                },
            } for t in descubiertas]

            # 3) Ejecución: cada llamada del modelo se reenvía al servidor MCP.
            async def dispatch(nombre: str, argumentos: dict) -> str:
                res = await mcp.call_tool(nombre, argumentos)
                texto = "\n".join(c.text for c in res.content if getattr(c, "type", "") == "text")
                if res.isError:
                    raise RuntimeError(texto or "error en la herramienta")
                return texto

            config = cargar_config()
            client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
            print(f"\nTarea: {TAREA}\n")
            final = await run_agent(
                client, config.model, TAREA, tools, dispatch,
                temperature=config.temperature, no_think=config.no_think,
            )
            print("\n── Respuesta final ──\n" + final)


asyncio.run(main())
