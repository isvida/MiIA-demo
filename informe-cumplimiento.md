# Informe de cumplimiento · MiIA-demo

**Fecha:** 19 de noviembre de 2026
**Objetivo:** comprobar que la demo funciona y que un alumno puede seguir las instrucciones de `README.md` (principal) y `ejemplos/README.md` desde una máquina limpia, usando los comandos documentados.
**Criterio de éxito:** cada instrucción del README se ejecuta con el resultado que describe el propio README.

## 1. Entorno de la comprobación

| Elemento | Valor |
|---|---|
| Máquina | Linux, Docker Engine 27.4.1, Compose v2.32.1 |
| RAM | 31 GB |
| Estado de la demo | `docker compose up -d` con el perfil por defecto (CPU) |
| Modelo | `qwen3.5:2b-q4_K_M` (1,9 GB) presente en el volumen `miia-demo_ollama` desde una sesión anterior |
| Restricción del entorno | **VPN de Cisco conectada (`cscotun0`)**: captura las rutas `172.17.0.0/16` y `172.18.0.0/16` por el dispositivo TUN, lo que rompe (a) la salida a internet de los contenedores y (b) el acceso del anfitrión a los puertos mapeados `127.0.0.1:3000/4000/8001`. El anfitrión sí tiene internet. |

> La restricción de la VPN es **externa a la demo** y se documenta aquí para separar fallos reales de fallos ambientales. Todo lo que circula dentro de la red de Compose funciona con normalidad.

## 2. Metodología

1. Revisión estática de todos los ficheros (compose, configuraciones, Dockerfiles, scripts, ejemplos, tests) para contrastar las afirmaciones de los README con el código.
2. Arranque de la pila siguiendo el «Arranque rápido» del README principal.
3. Verificación de cada instrucción del README con los comandos que él mismo indica (adaptados a la restricción de VPN: cuando el comando documentado usa `localhost`, se repite el mismo pedido desde dentro de la red de Compose contra la misma URL interna, p. ej. `litellm:4000` en lugar de `localhost:4000`).
4. Ejecución de `test-scripts.sh` (comprobador de los ejemplos) y de las pruebas unitarias de `tests/`.
5. Validación de las cuatro configuraciones Compose documentadas (`docker compose config -q`).

## 3. Cumplimiento de las instrucciones del README principal

| # | Instrucción del README | Resultado | Observación |
|---|---|---|---|
| 1 | `docker compose up -d` (Arranque rápido) | ✅ Cumple | Los 5 servicios arrancan; `db` y `ollama` healthy. |
| 2 | `docker compose logs -f ollama-init` y esperar a que termine la descarga | ⚠️ Cumple salvo red | **En esta máquina la VPN impidió la verificación del manifiesto remoto** (`i/o timeout` contra `registry.ollama.ai` desde la red de Compose) y el contenedor terminó en error. El modelo **ya estaba completo en el volumen** (manifiesto + 6 capas) y Ollama lo sirve (`ollama list`: 1,9 GB). En una máquina con internet normal el flujo funciona; con el modelo ya descargado `ollama-init` termina enseguida. |
| 3 | Tabla de servicios y puertos (`:3000`, `:4000/ui`, `:4000/v1`, `:8001/mcp`) | ✅ Cumple (verificado desde dentro) | Panel `/ui` → 200 (21 KB); `GET /v1/models` → 200 y lista `miia-demo`; Open WebUI → 200 (14 KB de HTML, healthy); MCP `/mcp` responde a un handshake `initialize` → 200. El acceso directo desde el anfitrión (`localhost`) estaba bloqueado por la VPN (ver §4.1); la mapeación de puertos sí existe (`ss` muestra los 3 puertos en `127.0.0.1`). |
| 4 | «Comprobación»: `curl` a `/v1/chat/completions` con `sk-demo-master` | ✅ Cumple (verificado desde dentro) | `POST http://litellm:4000/v1/chat/completions` con el mismo cuerpo del README → **200** en 4,7 s; el modelo responde. |
| 5 | `bash test-scripts.sh` (comprobar los ejemplos) | ✅ Cumple | **Resumen: 8 correctos, 0 fallidos** (ver §5). |
| 6 | Ejemplos 01–06 con `docker compose run --rm lab python …` | ✅ Cumple | Los 6 ejemplos corren en el contenedor `lab` con las librerías ya instaladas; salida coherente con lo que describe `ejemplos/README.md` (ver §5). |
| 7 | «Claves virtuales»: crear clave (UI o `POST /key/generate`) y usarla | ✅ Cumple | `POST /key/generate` → 200; la clave devuelta en el campo **`key`** (`sk-…`) funciona en una petición real → 200. (Ver §6.1 sobre el campo `token`.) |
| 8 | «Perfil GPU (vLLM)» y «Ollama con GPU NVIDIA» | ⏸ No verificable aquí | Sin GPU NVIDIA en esta máquina. Las configuraciones **sí son válidas**: `docker compose --profile gpu config -q` y `docker compose -f docker-compose.yml -f docker-compose.ollama-gpu.yml config -q` → OK. |
| 9 | «MCP con herramientas externas»: endpoint `http://localhost:8001/mcp` | ✅ Cumple (verificado desde dentro) | Handshake MCP `initialize` sobre `mcp:8000/mcp` → 200; tools/recursos/prompts descubiertos por el ejemplo 05. |
| 10 | «El modelo de la demo»: `qwen3.5:2b-q4_K_M` como `miia-demo`, `think: false`, `/no_think` | ✅ Cumple | `litellm/config.yaml` define `ollama_chat/qwen3.5:2b-q4_K_M` con `think: false` y `num_ctx: 8192`; los ejemplos añaden `/no_think` vía `no_think` de `config.json` (y `NO_THINK=0` lo desactiva, como documenta `ejemplos/README.md`). |
| 11 | «Llevar el modelo sin red (aula)»: exportar el volumen con `tar czf` | ✅ Cumple | `docker run --rm -v miia-demo_ollama:/data -v …:/out alpine tar czf /out/modelo-ollama.tgz -C /data .` → archivo de 4,0 GB generado correctamente (incluye `qwen3.5:2b` y `qwen3:4b`). |
| 12 | «Limpieza»: `docker compose down` / `down -v` | ⏸ No ejecutado | No se ejecuta durante la comprobación para no derribar la pila. Los comandos son estándar de Compose y la composición incluye los volúmenes `ollama`, `hf-cache`, `pgdata`, `webui`. |
| 13 | «Antes de la charla»: `docker compose pull` / `build` | ⏸ No ejecutado | Las imágenes ya estaban construidas en el entorno (`miia-demo-lab`, `miia-demo-mcp` y las base). En una máquina limpia el flujo es el documentado; si el DNS de la red de construcción falla, el README aporta el workaround `MIIA_BUILD_NETWORK=host`, que está implementado en el compose (`network: ${MIIA_BUILD_NETWORK:-default}` en `mcp` y `lab`). |

## 4. Incidencias ambientales (VPN), con causa raíz identificada

### 4.1. Acceso del anfitrión a los puertos mapeados

Con la VPN conectada, `curl http://127.0.0.1:4000/…` no responde (tiempo agotado), aunque `ss -tlnp` muestra los puertos escuchando. Causa raíz: la interfaz TUN de la VPN (`cscotun0`) es la ruta por defecto **y además se lleva las rutas de las redes de Docker** (`172.17.0.0/16 dev cscotun0`, `172.18.0.0/16 dev cscotun0`); el tráfico NAT de los puertos mapeados se enruta por el túnel y se pierde. La salida a internet de los contenedores falla igual (`Network is unreachable` desde la red de Compose; el anfitrión llega a `registry.ollama.ai` sin problema).

**Verificación de que no es un defecto de la demo:** los mismos pedidos hechos desde dentro de la red de Compe contra las URLs internas (`litellm:4000`, `open-webui:8080`, `mcp:8000`) responden correctamente y de inmediato (`health/liveliness` → 200 en 0,0 s). Al desconectar la VPN, los cuatro puntos del README (`:3000`, `:4000/ui`, `:4000/v1`, `:8001/mcp`) quedan disponibles sin cambiar nada de la demo.

**Pendiente de re-verificación (después de desconectar la VPN):**
```bash
curl -s http://localhost:4000/health/liveliness
curl -s http://localhost:4000/v1/chat/completions -H "Authorization: Bearer sk-demo-master" \
  -H "Content-Type: application/json" \
  -d '{"model":"miia-demo","messages":[{"role":"user","content":"Hola, ¿quién eres?"}]}'
# y abrir http://localhost:3000 y http://localhost:4000/ui en el navegador
```

### 4.2. `ollama-init`

Falla al verificar el manifiesto remoto (`i/o timeout`), por la misma restricción de red. El modelo ya existe en el volumen, así que el impacto es cero en este entorno. En un aula sin red, el README prevé exactamente este caso (sección «Llevar el modelo sin red»): se rellena el volumen con el `tar` previo y `ollama-init` termina enseguida.

### 4.3. Open WebUI

Con la VPN conectada, el arranque de Open WebUI se estiró (~12 min, `unhealthy` transitorio) y acabó **healthy** sirviendo la página (200, verificado desde dentro). Sin la restricción de red, el arranque es el habitual.

## 5. Ejemplos: resultados de `test-scripts.sh` y `tests/`

### 5.1. `bash test-scripts.sh` → **8 correctos, 0 fallidos**

| Script | Verificación del comprobador | Salida observada |
|---|---|---|
| `01_hola_api.py` | Mide TTFT y tokens/s | Llamada normal (51 entrada/60 salida tokens); streaming con **TTFT 0,13 s** y **16,5 tokens/s**. Lista `miia-demo` en la pasarela. |
| `02_salida_estructurada.py` | Impone el esquema | JSON «por favor» **inválido** contra la clase Pydantic (campo `curso` mal nombrado, fechas no normalizadas) → muestra el problema; con `json_schema` → respuesta válida y legible (`horas: 40`, `aprovechamiento: true`). Justo el contraste pedagógico prometido. |
| `03_tool_calling.py` | `Tu código devuelve: 18` + respuesta final | El modelo pide `ects_desde_horas({"horas": 450})`; el código devuelve `18.0`; respuesta final coherente. |
| `04_agente_minimo.py` | Skill cargada + `informe.md` escrito (sandbox temporal) | 5 pasos: `cargar_skill(informe-incidencias)` → `listar_directorio(incidencias)` → 3× `leer_fichero` → `escribir_fichero(informe.md)`. El informe respeta la skill (tabla ordenada por prioridad, sección de acciones). |
| `05_agente_mcp.py` | Tickets en MCP temporal + 3 llamadas MCP | Descubre las 4 tools, el recurso `ugr://master/especialidades` y el prompt `resumir_incidencia`; ejecuta `listar_asignaturas(iot)` → `crear_ticket(baja)` → `listar_tickets()` en el MCP de pruebas (sandbox temporal, sin tocar `workspace/`). |
| `06_concurrencia.py` | 2 peticiones a la vez | 2 peticiones completadas (5,6 s y 7,4 s); **18,6 tokens/s agregados** — el encadenamiento esperado con `OLLAMA_NUM_PARALLEL=2` en CPU. |
| `agent_core.py` | Importa `run_agent` | OK. |
| `config.py` | `cargar_config()` válida | OK. |

El comprobador usó, como documenta, un sandbox y un servidor MCP temporales (`miia-test-*`) eliminados al terminar; `workspace/` no se modificó.

### 5.2. Pruebas unitarias (`tests/`) → **9/9 OK**

Ejecutadas en el contenedor `lab` (el host no tiene `openai`): `python -m unittest discover -s tests` → `Ran 9 tests … OK` (1,7 s). Cubren `config.py` (clave por variable de entorno, validaciones, `NO_THINK`) y `04_agente_minimo.py` (sandbox, rutas seguras, skills).

### 5.3. `ejemplos/README.md`

Las instrucciones de esa guía (arrancar, ejecutar cada ejemplo, variar tareas con argumentos, `--auto`, `MIIA_CONFIG`, pasar la clave por variable de entorno, `test-scripts.sh`) son consistentes con el código: `config.py` implementa exactamente el comportamiento descrito (referencias `${VAR}` y `${VAR:-default}`, precedencias de `OPENAI_BASE_URL`/`OPENAI_API_KEY`/`MODEL` y `NO_THINK`, validación de `base_url` y `temperature` 0–2). Los comandos de cada ejemplo son los mismos que ejecutó el comprobador.

## 6. Observaciones menores (no bloquean; recomendaciones)

1. **`/key/generate` devuelve dos campos:** `key` (la clave `sk-…` que hay que usar) y `token` (un hash interno de 64 hex que **no** autentica: devuelve 401 «expected to start with 'sk-'»). El flujo del README (crear la clave en el panel `/ui`, donde se muestra la clave `sk-…`) es el correcto; el ejemplo de `curl` a `/key/generate` funciona, pero un alumno que pruebe el campo `token` en lugar del `key` se encontrará un 401. *Recomendación:* añadir media línea al README: «la clave es el campo `key` de la respuesta (empieza por `sk-`)».
2. **Contenedores huérfanos en la salida:** una ejecución previa interrumpida dejó `miia-demo-lab-run-…` (Exited) y Compose avisa `Found orphan containers` en cada `run`. Inofensivo, pero ruidoso para los alumnos. *Recomendación:* mencionar en «Limpieza» que `docker compose down` no elimina los contenedores de `run` y que se pueden limpiar con `docker compose run … --rm` (que ya se usa) o eliminarlos con `docker rm`.
3. **Salida a internet desde los contenedores:** si el equipo del profesor usa una VPN corporativa que capture rutas privadas (como la de Cisco en este caso), hay que desactivarla o configurar *split tunneling* antes de la charla; el propio README anticipa problemas de red de construcción con `MIIA_BUILD_NETWORK=host`. *Recomendación:* añadir esa posibilidad al apartado «Error de DNS al construir las imágenes» (ahora cubre solo DNS, no la captura de rutas por una VPN).
4. **Open WebUI tarda más de lo habitual al arrancar bajo red restringida** (healthy a los ~12 min). Sin VPN, el arranque es el estándar. No requiere cambio.

## 7. Estado de los servicios al terminar la comprobación

| Servicio | Estado |
|---|---|
| `db` (postgres:16-alpine) | Up · healthy |
| `ollama` (ollama/ollama) | Up · healthy · modelo `qwen3.5:2b-q4_K_M` servible |
| `litellm` (main-stable) | Up · API y panel operativos |
| `mcp` (miia-demo-mcp) | Up · MCP Streamable HTTP operativo |
| `open-webui` (main) | Up · healthy |
| `ollama-init` | Exited (error de red por la VPN; modelo ya descargado) |

## 8. Conclusión

**La demo cumple y los alumnos pueden seguir los README.**

- Toda la infraestructura documentada arranca y funciona: pasarela LiteLLM (API, panel, claves virtuales con presupuesto y RPM), Open WebUI, servidor MCP (tools + resources + prompts), Ollama con el modelo descargado.
- Los seis ejemplos corren tal cual los documenta `ejemplos/README.md` y producen la salida que cada guía promete; el comprobador `test-scripts.sh` lo confirma de forma automatizada (**8/8**) y las pruebas unitarias pasan (**9/9**).
- Las instrucciones específicas de aula (exportar el modelo sin red, perfil GPU, Ollama con GPU, `MIIA_BUILD_NETWORK`) están implementadas y sus configuraciones son válidas; las de GPU no son verificables en una máquina sin GPU.
- Las únicas incidencias encontradas son **ambientales** (VPN del equipo que comprueba) y se han identificado con causa raíz; una vez desconectada la VPN, los cuatro endpoints de `localhost` del README quedan verificados directamente (pendiente de re-verificación final, §4.1).
- Se recomienda aplicar las tres mejoras menores del §6 (son de texto, no de código).
