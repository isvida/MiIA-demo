# MiIA-demo

![Infraestructura LLM on-premise](presentación/portada.png)

Materiales del seminario sobre infraestructura LLM *on-premise* del Máster en
Desarrollo del Software de la Universidad de Granada. El repositorio reúne la
presentación y una demostración práctica para aprender sobre inferencia,
pasarelas, agentes, herramientas y MCP.

## Tabla de contenidos

- [Recursos](#recursos)


## Recursos

- [Presentación en PDF](presentación/presentacion.pdf) y [fuentes LaTeX](presentación/presentacion.tex).
- [Demostración con Docker](miia-demo/README.md): instalación, configuración y uso.
- [Ejemplos y guía](miia-demo/ejemplos/README.md): de la API a los agentes.


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
