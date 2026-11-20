"""Servidor MCP de ejemplo: tres tipos de capacidades que un agente puede descubrir.

  - tools      → acciones que el modelo puede pedir (funciones)
  - resources  → datos de solo lectura que el cliente puede leer
  - prompts    → plantillas de instrucciones reutilizables

Transporte: Streamable HTTP en http://<host>:8000/mcp
"""
import json
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

WORKSPACE = Path("/workspace")
TICKETS = WORKSPACE / "tickets.jsonl"

mcp = FastMCP("ugr-demo", host="0.0.0.0", port=8000)

# Datos de demostración: asignaturas del máster (resumidos de la ficha pública).
ASIGNATURAS = {
    "iot": [
        "Ingeniería del Internet de las Cosas",
        "Ingeniería de Entornos Inteligentes",
        "Desarrollo de Software para Sistemas Empotrados y Dispositivos IoT",
        "Análisis Predictivo y Aprendizaje Automático en el Desarrollo de Software",
        "Representación y Tratamiento de la Información y Web Semántica",
        "Sistemas de Almacenamiento",
        "Transformación Digital y Gemelos Digitales para la Industria 4.0",
    ],
    "visualizacion": [
        "Estructura de Datos y Algoritmos Geométricos de Sistemas Gráficos",
        "Modelado 3D",
        "Programación del Cauce Gráfico en GPU",
        "Animación, Realismo y Simulación",
        "Visualización Científica y Visualización de Datos",
        "Visualización Expresiva y Artística",
    ],
    "interfaces": [
        "Análisis y Evaluación de Sistemas Interactivos",
        "Técnicas de Diseño y Prototipado",
        "Interfaces Conversacionales, Multimodales y Asistentes Virtuales",
        "Tecnologías del Habla y del Lenguaje Natural",
        "Fundamentos de Diseño y Experiencia de Juego",
        "Videojuegos para la Sociedad",
    ],
}


@mcp.tool()
def listar_asignaturas(especialidad: str) -> str:
    """Devuelve las asignaturas propias de una especialidad del máster.

    especialidad debe ser una de: 'iot', 'visualizacion', 'interfaces'.
    """
    clave = especialidad.strip().lower()
    if clave not in ASIGNATURAS:
        return f"Especialidad desconocida. Valores válidos: {', '.join(ASIGNATURAS)}"
    return json.dumps(ASIGNATURAS[clave], ensure_ascii=False)


@mcp.tool()
def hora_actual() -> str:
    """Devuelve la fecha y hora actuales del servidor (ISO 8601)."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


@mcp.tool()
def crear_ticket(titulo: str, descripcion: str, prioridad: str = "media") -> str:
    """Crea un ticket de soporte. prioridad: 'baja', 'media' o 'alta'."""
    if prioridad not in {"baja", "media", "alta"}:
        return "Error: prioridad debe ser 'baja', 'media' o 'alta'."
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    existentes = TICKETS.read_text().splitlines() if TICKETS.exists() else []
    ticket = {
        "id": len(existentes) + 1,
        "creado": datetime.now().astimezone().isoformat(timespec="seconds"),
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
    }
    with TICKETS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ticket, ensure_ascii=False) + "\n")
    return f"Ticket #{ticket['id']} creado."


@mcp.tool()
def listar_tickets() -> str:
    """Lista los tickets creados hasta ahora."""
    if not TICKETS.exists():
        return "[]"
    return json.dumps(
        [json.loads(linea) for linea in TICKETS.read_text().splitlines() if linea.strip()],
        ensure_ascii=False,
    )


@mcp.resource("ugr://master/especialidades")
def especialidades() -> str:
    """Lista de especialidades del máster (recurso de solo lectura)."""
    return json.dumps(list(ASIGNATURAS), ensure_ascii=False)


@mcp.prompt()
def resumir_incidencia(texto: str) -> str:
    """Plantilla para pedir al modelo un resumen estructurado de una incidencia."""
    return (
        "Resume la siguiente incidencia en tres líneas: causa probable, impacto y "
        "siguiente acción recomendada.\n\n" + texto
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
