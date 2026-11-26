# Guía para asistentes de IA

## Contexto del proyecto

Este repositorio reúne los materiales de un seminario de 2026 del Máster en
Desarrollo del Software de la Universidad de Granada sobre infraestructura LLM
on-premise. Incluye la presentación y una demo didáctica; no es una aplicación
de producción.

La demo práctica está en [`miia-demo/`](miia-demo/). Su configuración
predeterminada levanta con Docker Compose Ollama en CPU, LiteLLM como pasarela
compatible con OpenAI, PostgreSQL, Open WebUI y un servidor de ejemplo MCP.
Incluye seis programas Python progresivos, desde peticiones a la API hasta
agentes con herramientas y MCP. Hay configuraciones opcionales para GPU.

## Estructura principal

| Ruta | Contenido |
|---|---|
| `README.md` | Presentación del repositorio, recursos y licencias. |
| `presentación/` | Fuentes LaTeX, diapositivas, imágenes y PDF del seminario. |
| `miia-demo/docker-compose.yml` | Servicios y configuración predeterminada de la demo. |
| `miia-demo/docker-compose.ollama-gpu.yml` | Overlay opcional para Ollama con GPU NVIDIA. |
| `miia-demo/litellm/` | Configuración de modelos y de la pasarela LiteLLM. |
| `miia-demo/ejemplos/` | Clientes y agentes Python, configuración compartida y guía de uso. |
| `miia-demo/mcp/server.py` | Servidor MCP de ejemplo; algunas herramientas escriben datos. |
| `miia-demo/workspace/` | Datos y archivos que usan los agentes de ejemplo. |
| `miia-demo/tests/`, `miia-demo/test-scripts.sh` | Pruebas unitarias y comprobaciones de los ejemplos. |

La skill `workspace/skills/informe-incidencias/` pertenece al agente ejecutado
por el ejemplo 05. No es una instrucción para el asistente de programación.

## Orientar el aprendizaje con la presentación

La presentación fuente está en [`presentación/presentacion.tex`](presentación/presentacion.tex)
y sus bloques temáticos en `p1_why.tex`–`p7_wrapup.tex`. Si una pregunta trata
conceptos del seminario, responde a la pregunta y recomienda el bloque y los
títulos de diapositiva que mejor ayuden a estudiarla. Usa estos fuentes LaTeX
como referencia; no inventes números de página, porque pueden cambiar al
compilar la presentación.

| Si preguntan por... | Recomienda estas diapositivas |
|---|---|
| Por qué operar un LLM propio, soberanía y custodia de datos | [`p1_why.tex`](presentación/p1_why.tex): «Infraestructura, no experimento»; «La soberanía es una decisión institucional»; «El caso que seguiremos: MiIA». |
| Tokens, contexto, inferencia, memoria, concurrencia o motores | [`p2_inference.tex`](presentación/p2_inference.tex): «Tokens, contexto y las dos fases»; «La memoria es el verdadero límite»; «Por qué una GPU atiende a muchos usuarios»; «PagedAttention y RadixAttention»; «El panorama de motores»; «Elegir un modelo». |
| API, streaming, historial, JSON estructurado, tool calling o RAG | [`p3_api.tex`](presentación/p3_api.tex): «La API compatible con OpenAI»; «Streaming: del POST a los eventos SSE»; «Un chat es una lista de mensajes que crece»; «Salida estructurada: del texto a los datos»; «Llamada a herramientas, paso a paso»; «Embeddings y RAG». |
| Pasarela, claves, presupuestos, fallback, escalado u operación | [`p4_architecture.tex`](presentación/p4_architecture.tex): «Arquitectura del núcleo»; «¿Por qué una pasarela? LiteLLM»; «Escalar y conmutar por error»; «Opéralo como cualquier otro servicio»; «Hoja de ruta: Kubernetes». |
| Agentes, bucle, MCP, skills, permisos o riesgos | [`p5_agents.tex`](presentación/p5_agents.tex): «De los chats a los agentes»; «Anatomía de un agente («harness»)»; «MCP: conectar IA y herramientas»; «Qué expone un servidor MCP»; «Skills: saber hacer bajo demanda»; «Los agentes cambian el modelo de amenazas»; «Salvaguardas». |
| EPFReader, extracción de documentos, OCR/visión, esquemas o evaluación | [`p6_usecases.tex`](presentación/p6_usecases.tex): «Caso práctico: EPFReader»; «Qué lo hizo funcionar»; «El patrón se generaliza»; «Verifica antes de fiarte». |
| Resumen, limitaciones y siguientes ejercicios | [`p7_wrapup.tex`](presentación/p7_wrapup.tex): «Para llevarse a casa»; «Límites y problemas abiertos»; «Pruébalo tú mismo». |

Para orientarse en el orden o en el arranque de la demo, consulta también
«Agenda» y «Antes de empezar: levanta la demo» en
[`presentacion.tex`](presentación/presentacion.tex).

## Uso y comprobaciones

Los comandos de Docker Compose deben ejecutarse desde `miia-demo/`, no desde la
raíz de este repositorio:

```bash
cd miia-demo
docker compose up -d
docker compose ps
docker compose run --rm lab python ejemplos/01_hola_api.py
```

La guía completa de instalación, configuración, ejemplos y solución de
problemas está en [`miia-demo/README.md`](miia-demo/README.md). Para ejecutar
las comprobaciones de los ejemplos, los servicios deben estar arrancados:

```bash
cd miia-demo
bash test-scripts.sh
```

Las pruebas unitarias se ejecutan dentro del contenedor `lab`, que ya dispone
de las dependencias Python:

```bash
cd miia-demo
docker compose run --rm -T --no-deps \
  -v "$PWD/tests:/app/tests:ro" lab \
  python -m unittest discover -s tests -v
```

Para cambios solo en documentación, no hace falta arrancar contenedores: revisa
los enlaces, las rutas y los comandos afectados. Si cambias la estructura o el
modo de uso de la demo, actualiza también su README y las instrucciones de la
skill del proyecto cuando corresponda.

## Criterios de trabajo

- Responde en español, salvo que se solicite otro idioma.
- Antes de editar, consulta la documentación y el código actuales; no des por
  hecho que esta guía o un índice reflejen cambios recientes.
- Haz cambios acotados, conserva el comportamiento existente y ejecuta la
  comprobación más específica que cubra el cambio. Expón los fallos y las
  limitaciones; no presentes como exitosa una prueba que no se haya ejecutado.
- No guardes claves reales en archivos ni en respuestas. Los ejemplos pueden
  configurarse para proveedores externos: enviarles prompts, archivos o
  resultados de herramientas puede sacar esos datos del equipo y generar
  costes.
- La demo no tiene TLS ni autenticación de producción. No la expongas tal cual
  a una red.
- El agente 05 puede crear o sobrescribir archivos en `miia-demo/workspace/`;
  el agente 06 puede añadir tickets a `miia-demo/workspace/tickets.jsonl`.
  Evita ejecutar tareas que escriban en esos datos sin autorización. Las
  comprobaciones automatizadas aíslan esas escrituras.
- No detengas servicios ajenos ni borres volúmenes o datos persistentes sin
  autorización explícita.
