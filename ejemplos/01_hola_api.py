"""01 · Hablar con el LLM: la API compatible con OpenAI y qué mide la inferencia.

Muestra: listado de modelos, una llamada normal con uso de tokens y una llamada en
streaming midiendo latencia hasta el primer token (TTFT) y velocidad de generación.
"""
import time

from openai import OpenAI
from config import cargar_config

config = cargar_config()
client = OpenAI(base_url=config.base_url, api_key=config.api_key)
MODEL = config.model
NT = config.no_think_suffix

print("Modelos disponibles en la pasarela:")
for m in client.models.list().data:
    print("  -", m.id)

messages = [
    {"role": "system", "content": "Eres un asistente técnico. Responde en español, breve."+NT},
    {"role": "user", "content": "Explica en dos frases qué es la caché KV en un LLM."},
]

print("\n── Llamada normal ──")
t0 = time.perf_counter()
r = client.chat.completions.create(model=MODEL, messages=messages, temperature=config.temperature)
print(r.choices[0].message.content)
print(f"[{time.perf_counter() - t0:.1f} s · tokens: {r.usage.prompt_tokens} entrada / "
      f"{r.usage.completion_tokens} salida]")

print("\n── Streaming ──")
t0 = time.perf_counter()
primero = None
chunks = 0
usage = None
stream = client.chat.completions.create(
    model=MODEL, messages=messages, temperature=config.temperature,
    stream=True, stream_options={"include_usage": True},
)
for ev in stream:
    if ev.usage:
        usage = ev.usage
    if ev.choices and ev.choices[0].delta.content:
        if primero is None:
            primero = time.perf_counter() - t0
        chunks += 1
        print(ev.choices[0].delta.content, end="", flush=True)
total = time.perf_counter() - t0
salida = usage.completion_tokens if usage else chunks   # sin usage, aproximamos por fragmentos
print(f"\n\nTTFT: {primero:.2f} s (preparar el contexto: 'prefill')")
print(f"Generación: {salida / max(total - primero, 1e-6):.1f} tokens/s ('decode')")
