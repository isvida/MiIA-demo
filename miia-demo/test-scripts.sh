#!/usr/bin/env bash
set -uo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")" || exit 1

timeout_seconds=${TEST_TIMEOUT:-300}
if [[ ! $timeout_seconds =~ ^[1-9][0-9]*$ ]]; then
    echo "TEST_TIMEOUT debe ser un número entero positivo de segundos." >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Se necesita Docker con Compose v2." >&2
    exit 1
fi

tmp=$(mktemp -d "${TMPDIR:-/tmp}/miia-test-scripts.XXXXXXXX") || exit 1
tmp=$(cd -- "$tmp" && pwd -P) || exit 1
mcp_name="miia-test-${tmp##*/}"
mcp_started=0
cleanup() {
    if (( mcp_started )); then
        if ! docker stop -t 5 "$mcp_name" >/dev/null 2>&1 && \
            docker inspect "$mcp_name" >/dev/null 2>&1; then
            echo "No se pudo detener el MCP temporal $mcp_name; se conserva $tmp." >&2
            return 1
        fi
    fi
    rm -rf -- "$tmp"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if ! mkdir -p "$tmp/agent" "$tmp/mcp"; then
    echo "No se pudieron crear los directorios temporales." >&2
    exit 1
fi
if ! cp -R workspace/incidencias workspace/skills "$tmp/agent/"; then
    echo "No se pudieron copiar los datos de ejemplo al sandbox temporal." >&2
    exit 1
fi

echo "Iniciando servidor MCP aislado..."
cat > "$tmp/mcp-compose.yml" <<'EOF'
services:
  mcp:
    volumes:
      - ${MIIA_TEST_WORKSPACE}:/workspace
EOF
if ! MIIA_TEST_WORKSPACE="$tmp/mcp" docker compose \
    -f docker-compose.yml -f "$tmp/mcp-compose.yml" \
    run --rm -d -T --no-deps --name "$mcp_name" mcp >/dev/null; then
    echo "No se pudo iniciar el servidor MCP de pruebas." >&2
    exit 1
fi
mcp_started=1
mounted=$(docker inspect "$mcp_name" \
    --format '{{range .Mounts}}{{if eq .Destination "/workspace"}}{{.Source}}{{end}}{{end}}')
if [[ $mounted != "$tmp/mcp" ]]; then
    echo "El MCP de pruebas no tiene el sandbox esperado; se aborta por seguridad." >&2
    exit 1
fi

if ! docker compose run --rm -T --no-deps lab \
    python -c 'import socket, sys, time
for _ in range(30):
    try:
        with socket.create_connection((sys.argv[1], 8000), timeout=1):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("El servidor MCP de pruebas no está disponible")' "$mcp_name"; then
    exit 1
fi

passed=0
failed=0
shopt -s nullglob
scripts=(ejemplos/*.py)
if (( ${#scripts[@]} == 0 )); then
    echo "No se encontraron scripts de Python." >&2
    exit 1
fi

for script in "${scripts[@]}"; do
    name=${script##*/}
    log="$tmp/$name.log"
    args=()
    options=()
    case "$name" in
        05_agente_minimo.py)
            options=(-v "$tmp/agent:/test-workspace" -e SANDBOX=/test-workspace)
            args=(--auto)
            ;;
        06_agente_mcp.py)
            options=(-e "MCP_URL=http://$mcp_name:8000/mcp")
            ;;
        02_concurrencia.py)
            args=(2)
            ;;
    esac

    echo
    echo "===== $name ====="
    if [[ $name == agent_core.py ]]; then
        command=(python -c 'from ejemplos.agent_core import run_agent; assert callable(run_agent); print("Bucle del agente importado correctamente")')
    elif [[ $name == config.py ]]; then
        command=(python -c 'from ejemplos.config import cargar_config; cargar_config(); print("Configuración válida")')
    else
        command=(python -u "$script" "${args[@]}")
    fi

    if docker compose run --rm -T --no-deps "${options[@]}" lab \
        timeout "$timeout_seconds" "${command[@]}" 2>&1 | tee "$log"; then
        ok=1
        case "$name" in
            01_hola_api.py)
                grep -q 'TTFT:' "$log" || ok=0
                ;;
            03_salida_estructurada.py)
                grep -q 'Imponiendo el esquema' "$log" || ok=0
                ;;
            04_tool_calling.py)
                grep -q 'Tu código devuelve: 18' "$log" && \
                    grep -q 'Respuesta final' "$log" || ok=0
                ;;
            05_agente_minimo.py)
                if [[ ! -s "$tmp/agent/informe.md" ]]; then
                    echo "No se creó informe.md en el sandbox." >&2
                    ok=0
                fi
                if ! grep -q '\] → cargar_skill(' "$log"; then
                    echo "El agente no llamó a cargar_skill." >&2
                    ok=0
                fi
                ;;
            06_agente_mcp.py)
                [[ -s "$tmp/mcp/tickets.jsonl" ]] && \
                    grep -q '\] → listar_asignaturas(' "$log" && \
                    grep -q '\] → crear_ticket(' "$log" && \
                    grep -q '\] → listar_tickets(' "$log" || {
                        echo "Falta el ticket o alguna de las llamadas MCP esperadas." >&2
                        ok=0
                    }
                ;;
            02_concurrencia.py)
                grep -q 'petición  1 terminada' "$log" && \
                    grep -q 'petición  2 terminada' "$log" || ok=0
                ;;
        esac
        if (( ok )); then
            echo "RESULTADO: OK"
            ((passed+=1))
            continue
        fi
        echo "RESULTADO: FALLO (no se observaron los resultados esperados)" >&2
    else
        echo "RESULTADO: FALLO (error de ejecución o tiempo agotado)" >&2
    fi
    ((failed+=1))
done

echo
echo "Resumen: $passed correctos, $failed fallidos."
(( failed == 0 ))
