"""04 · Un agente mínimo con herramientas locales (leer/listar/escribir ficheros).

    python ejemplos/04_agente_minimo.py                 # tarea por defecto; pide confirmación al escribir
    python ejemplos/04_agente_minimo.py --auto          # sin confirmación (¡solo en el sandbox!)
    python ejemplos/04_agente_minimo.py "tu tarea..."

Ideas que muestra: bucle agente, sandbox de rutas, permisos (confirmación humana) y
skills (instrucciones que el agente carga solo cuando la tarea las necesita).
"""
import asyncio
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

from agent_core import run_agent
from config import cargar_config

SANDBOX = Path(os.getenv("SANDBOX", "/workspace")).resolve()
AUTO = "--auto" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
TAREA_PREDETERMINADA = not args
TAREA = args[0] if args else (
    "Para completar la tarea DEBES primero usar cargar_skill con nombre "
    "informe-incidencias, después leer todas las incidencias de la carpeta "
    "incidencias y finalmente usar escribir_fichero para crear informe.md "
    "siguiendo la skill. No basta con responder en el chat."
)


def ruta_segura(ruta: str) -> Path:
    """Solo se permite tocar ficheros dentro del sandbox."""
    p = (SANDBOX / ruta).resolve()
    if p != SANDBOX and SANDBOX not in p.parents:
        raise PermissionError("ruta fuera del sandbox")
    return p


def listar_directorio(ruta: str = ".") -> str:
    p = ruta_segura(ruta)
    return "\n".join(sorted(f"{x.name}{'/' if x.is_dir() else ''}" for x in p.iterdir())) or "(vacío)"


def leer_fichero(ruta: str) -> str:
    return ruta_segura(ruta).read_text(encoding="utf-8")


def escribir_fichero(ruta: str, contenido: str) -> str:
    p = ruta_segura(ruta)
    if not AUTO:
        try:
            ok = input(f"\n  ¿Permitir escribir {p.relative_to(SANDBOX)} ({len(contenido)} caracteres)? [s/N] ")
        except EOFError:
            ok = ""
        if ok.strip().lower() not in {"s", "si", "sí", "y", "yes"}:
            return "El usuario ha denegado la escritura."
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contenido, encoding="utf-8")
    return f"Escrito {p.relative_to(SANDBOX)}"


def catalogo_skills() -> dict[str, tuple[str, str]]:
    """Una 'skill' es una carpeta con un SKILL.md: nombre + descripción (siempre visibles)
    y un cuerpo de instrucciones que solo se carga cuando hace falta."""
    skills = {}
    for f in sorted((SANDBOX / "skills").glob("*/SKILL.md")):
        texto = f.read_text(encoding="utf-8")
        cabecera, _, cuerpo = texto.removeprefix("---\n").partition("\n---\n")
        meta = dict(l.split(": ", 1) for l in cabecera.splitlines() if ": " in l)
        skills[meta.get("name", f.parent.name)] = (meta.get("description", ""), cuerpo.strip())
    return skills


SKILLS = catalogo_skills()


def cargar_skill(nombre: str) -> str:
    if nombre not in SKILLS:
        return f"No existe esa skill. Disponibles: {', '.join(SKILLS)}"
    return SKILLS[nombre][1]


FUNCIONES = {
    "listar_directorio": listar_directorio,
    "leer_fichero": leer_fichero,
    "escribir_fichero": escribir_fichero,
    "cargar_skill": cargar_skill,
}

SYSTEM = (
    "Eres un agente que trabaja con ficheros. Usa las herramientas para completar la tarea y "
    "responde en español.\n"
    "Si una tarea coincide con alguna de estas skills, cárgala con cargar_skill ANTES de actuar "
    "y sigue sus instrucciones:\n"
    + "\n".join(f"- {n}: {d}" for n, (d, _) in SKILLS.items())
)

TOOLS = [
    {"type": "function", "function": {
        "name": "listar_directorio",
        "description": "Lista los ficheros de una carpeta del espacio de trabajo.",
        "parameters": {"type": "object", "properties": {
            "ruta": {"type": "string", "description": "Carpeta relativa; '.' es la raíz"}}}}},
    {"type": "function", "function": {
        "name": "leer_fichero",
        "description": "Lee un fichero de texto del espacio de trabajo.",
        "parameters": {"type": "object", "properties": {
            "ruta": {"type": "string"}}, "required": ["ruta"]}}},
    {"type": "function", "function": {
        "name": "escribir_fichero",
        "description": "Crea o sobrescribe un fichero de texto del espacio de trabajo.",
        "parameters": {"type": "object", "properties": {
            "ruta": {"type": "string"}, "contenido": {"type": "string"}},
            "required": ["ruta", "contenido"]}}},
    {"type": "function", "function": {
        "name": "cargar_skill",
        "description": "Carga las instrucciones completas de una skill por su nombre.",
        "parameters": {"type": "object", "properties": {
            "nombre": {"type": "string"}}, "required": ["nombre"]}}},
]


async def main():
    skill_cargada = False
    informe_escrito = False

    async def dispatch(nombre: str, argumentos: dict) -> str:
        nonlocal skill_cargada, informe_escrito
        resultado = FUNCIONES[nombre](**argumentos)
        if nombre == "cargar_skill" and argumentos.get("nombre") == "informe-incidencias":
            skill_cargada = "informe-incidencias" in SKILLS
        if nombre == "escribir_fichero" and resultado == "Escrito informe.md":
            informe_escrito = bool(argumentos.get("contenido", "").strip())
        return resultado

    config = cargar_config()
    client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
    print(f"Tarea: {TAREA}\n")
    final = await run_agent(
        client, config.model, TAREA, TOOLS, dispatch, system=SYSTEM,
        temperature=config.temperature, no_think=config.no_think,
    )
    print("\n── Respuesta final ──\n" + final)
    if TAREA_PREDETERMINADA and not (skill_cargada and informe_escrito):
        raise SystemExit(
            "Tarea incompleta: se debe cargar la skill informe-incidencias y escribir "
            "informe.md con contenido. La escritura puede haber sido denegada."
        )


if __name__ == "__main__":
    asyncio.run(main())
