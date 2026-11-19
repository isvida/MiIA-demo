"""02 · Salida estructurada: del texto libre a datos validados (patrón EPFReader).

Un "diploma" con ruido de OCR (inventado) se convierte en un objeto Pydantic.
Primero pedimos JSON "por favor"; después lo imponemos con un esquema.
"""
import json
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from config import cargar_config

config = cargar_config()
client = OpenAI(base_url=config.base_url, api_key=config.api_key)
MODEL = config.model
NT = config.no_think_suffix


class Diploma(BaseModel):
    curso: str = Field(description="Nombre del curso, sin comillas")
    entidad_emisora: str
    alumno: str = Field(description="Nombre completo del destinatario")
    fecha_inicio: Optional[str] = Field(description="AAAA-MM-DD o null si no consta")
    fecha_fin: Optional[str] = Field(description="AAAA-MM-DD o null si no consta")
    horas: Optional[int] = Field(description="Duración en horas o null si no consta")
    aprovechamiento: bool = Field(description="true si indica aprovechamiento/superado, false si solo asistencia")


# Texto inventado, con el desorden típico de un OCR.
TEXTO = """
UNIVERS1DAD DE EJEMPLO  -  Centro de Formac ion Continua
CERT1FICA que D.ª María Ejemplo Prueba ha superado con aprovecha-
miento el curso  "Introducción a la Administración de Sistemas Linux"
impartido del 3 al 28 de marzo de 2014, con una duración de 40 horas.
Granada, 2 de abril de 2014          Fdo.: El Director
"""

PROMPT = "Extrae los datos del siguiente diploma (texto de OCR con errores):\n" + TEXTO

print("── 1. Pidiendo JSON sin restricciones ──")
r = client.chat.completions.create(
    model=MODEL, temperature=config.temperature,
    messages=[{"role": "user", "content": PROMPT + "\nResponde solo con JSON." + NT}],
)
bruto = r.choices[0].message.content
print(bruto)
try:
    Diploma.model_validate_json(bruto)
    print("→ Válido (esta vez ha tenido suerte)")
except (ValidationError, ValueError) as e:
    print(f"→ NO válido: {type(e).__name__}. Con 11.500 documentos, esto no escala.")

print("\n── 2. Imponiendo el esquema (salida estructurada) ──")
r = client.chat.completions.create(
    model=MODEL, temperature=config.temperature,
    messages=[{"role": "user", "content": PROMPT + NT}],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "Diploma", "schema": Diploma.model_json_schema(), "strict": True},
    },
)
diploma = Diploma.model_validate_json(r.choices[0].message.content)
print(json.dumps(diploma.model_dump(), ensure_ascii=False, indent=2))
print("\nEl decodificador solo puede generar tokens que respeten el esquema;"
      " vLLM lo llama 'guided decoding' (guided_json / structured outputs).")
