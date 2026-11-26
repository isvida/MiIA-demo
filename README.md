# MiIA-demo

![Infraestructura LLM on-premise](presentación/portada.png)

Materiales del seminario sobre infraestructura LLM *on-premise* del Máster en
Desarrollo del Software de la Universidad de Granada. El repositorio reúne la
presentación y una demostración práctica para aprender sobre inferencia,
pasarelas, agentes, herramientas y MCP.

## Tabla de contenidos

- [Recursos](#recursos)
- [Instrucciones para asistentes de IA (`AGENTS.md`)](#instrucciones-para-asistentes-de-ia-agentsmd)


## Recursos

- [Presentación en PDF](presentación/presentacion.pdf) y [fuentes LaTeX](presentación/presentacion.tex).
- [Demostración con Docker](miia-demo/README.md): instalación, configuración y uso.
- [Ejemplos y guía](miia-demo/ejemplos/README.md): de la API a los agentes.

## Instrucciones para asistentes de IA (`AGENTS.md`)

[`AGENTS.md`](AGENTS.md) es un archivo de contexto e instrucciones para
asistentes de programación con IA. Resume qué contiene el repositorio, dónde
está la demo, cómo se ejecuta y se comprueba, y qué precauciones tener al
trabajar con sus datos. Sirve para no tener que repetir ese contexto en cada
sesión; es una guía en texto, no una configuración ejecutable ni una barrera de
seguridad.

Colócalo en la **raíz del repositorio**, junto a este `README.md`. Así queda
compartido con el proyecto y puede cubrir tanto la presentación como
`miia-demo/`.

- **OpenCode:** abre la carpeta raíz del repositorio como espacio de trabajo o
  inicia `opencode` desde ella. OpenCode detecta y carga el `AGENTS.md` del
  proyecto.
- **Claude Code:** inicia `claude` desde la carpeta raíz. Desde la versión
  2.1.277, carga `AGENTS.md` por defecto si no encuentra `CLAUDE.md`,
  `.claude/CLAUDE.md` o `CLAUDE.local.md` en la carpeta actual o sus directorios
  superiores. No hace falta copiarlo ni mantener otro archivo. Si ya tienes
  instrucciones `CLAUDE.md` y quieres cargar también `AGENTS.md`, selecciona
  `claude-md-and-agents-md` en `/config`, en **Project instructions**. Para una
  versión anterior, crea `CLAUDE.md` en la misma raíz con `@AGENTS.md` para
  importar la guía, en vez de duplicar su contenido.

```bash
cd ruta/al/repositorio
opencode  # o: claude
```

Consulta la documentación de [instrucciones de OpenCode](https://opencode.ai/docs/instructions/)
y de [memoria e instrucciones de Claude Code](https://code.claude.com/docs/en/memory)
para los detalles de cada herramienta.


## Licencia y cómo citar

Este repositorio acompaña al seminario *Infraestructura LLM on-premise:
inferencia, pasarelas, agentes y MCP* (Máster Universitario en Desarrollo
del Software, Universidad de Granada, 2026).

| Contenido | Licencia |
|---|---|
| Código (`ejemplos/`, `lab/`, `litellm/`, `mcp/`, `tests/`, `workspace/`, `docker-compose*.yml`) | [Apache-2.0](LICENSE) |
| Documentación y diapositivas | [CC BY 4.0](LICENSE-DOCS.md) |

Quedan fuera de ambas licencias las ilustraciones generadas con IA, los
logotipos y marcas de terceros y los componentes que la demo descarga al
ejecutarse (imágenes de contenedor y modelos), que tienen sus propias
condiciones. Detalles en [`NOTICE`](NOTICE).

La presentación está depositada en **Digibug**, el repositorio institucional
de la Universidad de Granada: [https://hdl.handle.net/10481/117143](https://hdl.handle.net/10481/117143)

Para citar este trabajo, usa el botón «Cite this repository» de GitHub
(fichero [`CITATION.cff`](CITATION.cff)) o la referencia de Digibug.

> **Aviso:** la demo es un entorno didáctico en miniatura. No tiene TLS ni
> autenticación de producción y no debe exponerse a una red tal cual.
