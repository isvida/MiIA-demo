---
name: miia-demo
description: "Usa esta skill para responder dudas, explorar, depurar, probar o modificar el proyecto miia-demo: Docker Compose, LiteLLM, Ollama, ejemplos Python, agentes, skills y MCP."
---

# Trabajar con miia-demo

Ayuda a personas con conocimientos de informática que están aprendiendo sobre
LLM, agentes y herramientas. Responde en español, salvo que pidan otro idioma.
Para una duda, explica el mecanismo con referencias a los archivos relevantes;
no modifiques archivos ni ejecutes operaciones por el mero hecho de preguntar.

## Mapa del proyecto

Infraestructura LLM on-premise en miniatura, en Docker Compose y sin GPU:
un único endpoint compatible con OpenAI (`miia-demo`) servido por Ollama (CPU),
una pasarela LiteLLM con claves y consumo, un chat web, un servidor MCP de
ejemplo y seis ejemplos Python progresivos (API → concurrencia → herramientas → agentes → MCP).

| Dónde | Qué es |
|---|---|
| `docker-compose.yml` | Ollama + `ollama-init` (descarga el modelo una vez) + LiteLLM + Postgres + Open WebUI + MCP + servicio `lab` (perfil `lab`) |
| `docker-compose.ollama-gpu.yml` | Overlay opcional: GPU NVIDIA para Ollama (se suma con `-f`) |
| `litellm/config.yaml` | `miia-demo` → `ollama_chat/qwen3.5:2b-q4_K_M`, `think: false`, `num_ctx: 8192`; master key `sk-demo-master` por defecto |
| `litellm/config.gpu.yaml` | Perfil GPU: vLLM (`Qwen/Qwen3-4B`) principal + Ollama como fallback (`fallbacks`) |
| `ejemplos/01…06_*.py` | API/streaming (TTFT, tokens/s), concurrencia, JSON con esquema, tool calling, agente local, agente MCP |
| `ejemplos/agent_core.py` | Bucle de agente compartido (`run_agent`, máx. 12 pasos; los errores de herramientas vuelven al modelo) |
| `ejemplos/config.py` + `config.json` | Configuración compartida: `base_url`, clave (`${LITELLM_MASTER_KEY:-sk-demo-master}`), modelo, `temperature`, `no_think`; las variables `OPENAI_BASE_URL`/`OPENAI_API_KEY`/`MODEL`/`NO_THINK` tienen prioridad |
| `mcp/server.py` | Servidor MCP Streamable HTTP (puerto 8000 interno, 8001 externo): 4 tools, 1 resource, 1 prompt; escribe tickets en `workspace/tickets.jsonl` |
| `workspace/` | Datos de los agentes: `incidencias/` (3 incidentes) y `skills/informe-incidencias/SKILL.md` |
| `test-scripts.sh` | Prueba de integración de todos los ejemplos; usa un sandbox y un MCP temporales; devuelve ≠0 si algo falla |
| `tests/` | Pruebas unitarias (unittest) de `ejemplos/config.py` y `ejemplos/05_agente_minimo.py` |
| `lab/Dockerfile`, `mcp/Dockerfile` | Imágenes: Python 3.12 con `openai`, `pydantic`, `mcp`, `httpx` (lab) y `mcp` (servidor) |

Flujo de una petición: ejemplo (contenedor `lab`) → `litellm:4000/v1` → Ollama.
Open WebUI usa la misma pasarela. Puertos externos (solo `127.0.0.1`):
3000 WebUI · 4000 LiteLLM API+panel · 8001 MCP.

## Operaciones habituales

```bash
docker compose ps                            # estado de los servicios
docker compose logs -f <servicio>            # logs (litellm, ollama, mcp, open-webui…)
docker compose up -d                         # arrancar
docker compose down                          # parar y eliminar contenedores (conserva imágenes y volúmenes)
docker compose run --rm lab python ejemplos/01_hola_api.py      # un ejemplo
docker compose run --rm lab python ejemplos/05_agente_minimo.py --auto  # agente sin confirmación
bash test-scripts.sh                         # probar todos los ejemplos (TEST_TIMEOUT para el límite)
docker compose run --rm -T --no-deps -v "$PWD/tests:/app/tests:ro" lab \
    python -m unittest discover -s tests -v  # pruebas unitarias (el host no tiene las librerías)
docker compose exec ollama ollama list       # modelos descargados
```

- El contenedor `lab` se crea al vuelo (`run`) y se elimina al terminar; la primera
  vez puede construir su imagen. `--no-deps` evita arrancar el resto de servicios.
- Los ejemplos leen `ejemplos/config.json`; fuera de Compose, apunta a
  `http://localhost:4000/v1` (o pasa `OPENAI_BASE_URL`).
- Para verificar una URL interna sin tocar los puertos del host, hazlo desde un
  contenedor de la red: `docker compose run --rm --no-deps mcp python -c "import httpx; …"`.

## Dudas frecuentes

- **No llegan peticiones a `localhost:3000/4000/8001`:** comprueba si una VPN u otra
  herramienta de red captura las rutas de Docker (`ip route`; rutas `172.17/16` o
  `172.18/16` saliendo por un `tun`). Verifica el servicio desde dentro (ver arriba):
  si responde, el problema es el anfitrión, no la demo.
- **`ollama-init` termina en error al descargar el modelo:** si ya hay modelo en el
  volumen, `ollama list` lo muestra y no hay que hacer nada; sin red, ver «Llevar el
  modelo sin red» del README (exportar/importar el volumen `miia-demo_ollama`).
- **Claves virtuales:** el campo `key` de la respuesta de `/key/generate` (empieza por
  `sk-`) es la clave que hay que usar; el campo `token` es un hash interno y **no**
  autentica (da 401). El panel `/ui` muestra la clave directamente.
- **El agente 04/05 no termina la tarea:** las respuestas del modelo son variables;
  mira las líneas `[paso N] → herramienta(args)`. El comprobador verifica resultados
  esenciales (skill cargada, `informe.md` escrito, llamadas MCP, ticket creado), no el
  contenido del informe.
- **Advertencia de contenedores huérfanos** (`Found orphan containers`): son
  contenedores de `docker compose run` interrumpidos que ya no están en la
  configuración; se limpian con `docker rm <nombre>`.
- **Open WebUI tardado en arrancar** (healthy transitorio) con la red restringida;
  sin restricciones el arranque es el habitual.
- **GPU:** el perfil vLLM usa un modelo distinto (`Qwen/Qwen3-4B`) que el de Ollama;
  comparar tiempos entre ambos no aísla solo el motor.

## Cambios y comprobaciones

1. Distingue entre explicar y cambiar; aclara las decisiones que afecten al
   comportamiento. Antes de editar, revisa las configuraciones, usos y pruebas
   relacionados. Mantén los cambios centrados en la petición y actualiza la
   documentación directamente afectada (README principal, `ejemplos/README.md`,
   esta skill si cambia el mapa del proyecto).
2. Conserva los valores y comportamientos existentes salvo que se solicite lo
   contrario. Los ejemplos usan por defecto LiteLLM local y configuración
   compartida en `ejemplos/config.json`; una API externa puede recibir datos y
   generar costes. Nunca incluyas claves reales en archivos ni en respuestas.
3. Ejecuta las comprobaciones más concretas disponibles. Para los ejemplos,
   `bash test-scripts.sh` requiere servicios Docker y puede tardar: usa sandboxes
   temporales, pero aun así consume recursos. Las pruebas unitarias están en
   `tests/`. Para cambios solo de documentación, revisa enlaces y bloques
   pertinentes sin arrancar servicios innecesariamente.
4. No detengas ni alteres contenedores ajenos, ni borres volúmenes o datos sin
   autorización. El ejemplo 05 puede escribir en `workspace/` y el 06 puede
   crear tickets; evita ejecutarlos directamente contra datos reales sin permiso.
   No envíes código, datos del proyecto o credenciales a servicios externos sin
   autorización; revisa el proveedor del modelo y las herramientas usadas.
5. Resume qué cambió y qué comprobaciones se ejecutaron. Indica explícitamente
   errores, limitaciones y cualquier parte que no hayas podido verificar.

## Conocer el proyecto en profundidad

1. Lee el `README.md` de la raíz y, cuando corresponda, `ejemplos/README.md`.
   Comprueba siempre los archivos actuales: no presupongas que la documentación
   o un índice reflejen el estado más reciente.
2. Usa `codebase-memory-mcp` si está disponible: comprueba el estado del índice
   de la raíz del proyecto y actualízalo si está desfasado; busca símbolos y
   relaciones antes de leer el código pertinente. Si no está disponible, utiliza
   las herramientas normales de búsqueda y lectura. El índice es una ayuda, no
   una garantía de corrección ni sustituye la lectura del código.
3. Identifica la ruta completa afectada: `docker-compose.yml` y `litellm/` para
   servicios y modelos; `ejemplos/` para clientes, configuración y agentes;
   `mcp/` para el servidor; `workspace/` para datos y la skill del agente de
   ejemplo; `tests/` y `test-scripts.sh` para comprobaciones.

La skill `workspace/skills/informe-incidencias/` pertenece al agente de ejemplo;
no es esta skill de OpenCode y Claude Code.
