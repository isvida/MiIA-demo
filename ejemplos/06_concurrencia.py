"""06 · Concurrencia: ¿qué pasa cuando muchos usuarios preguntan a la vez?

    python ejemplos/06_concurrencia.py        # 8 peticiones simultáneas
    python ejemplos/06_concurrencia.py 16

Con vLLM (continuous batching) el rendimiento total crece con la concurrencia.
Con Ollama en CPU se ve cómo las peticiones se encolan (OLLAMA_NUM_PARALLEL limita el paralelismo).
Para compararlos: arranca con --profile gpu y repite; después `docker compose stop vllm`.
"""
import asyncio
import sys
import time

from openai import AsyncOpenAI
from config import cargar_config

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
config = cargar_config()
MODEL = config.model
NT = config.no_think_suffix
client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)


async def una(i: int, t0: float):
    r = await client.chat.completions.create(
        model=MODEL, temperature=config.temperature, max_tokens=120,
        messages=[{"role": "user", "content": f"Dame un dato curioso numerado como #{i} sobre la ciudad de Granada." + NT}],
    )
    t = time.perf_counter() - t0
    print(f"  petición {i:>2} terminada a los {t:5.1f} s")
    return r.usage.completion_tokens if r.usage else 0


async def main():
    print(f"Lanzando {N} peticiones a la vez…")
    t0 = time.perf_counter()
    tokens = await asyncio.gather(*(una(i, t0) for i in range(1, N + 1)))
    total = time.perf_counter() - t0
    print(f"\nTotal: {sum(tokens)} tokens en {total:.1f} s → {sum(tokens) / total:.1f} tokens/s agregados")


asyncio.run(main())
