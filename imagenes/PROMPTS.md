# Prompts de imágenes · «Tu propio servicio de LLM»

Ocho ilustraciones para la presentación en la plantilla **latexUGR v2**. Cada una sustituye a un bloque de texto o a un diagrama que se entiende mejor como metáfora visual. Si un fichero no existe, la presentación compila igual y muestra un recuadro «Imagen pendiente» con el nombre esperado.

Los prompts están en inglés porque los generadores de imagen responden mejor así. La explicación va en español.

## Cómo usarlos

1. **Empieza por `s01_infraestructura.jpeg`.** Cuando te guste el resultado, úsalo como imagen de referencia de estilo (*style reference*, *image prompt* o equivalente) en las demás. Así las ocho comparten trazo y paleta.
2. **Pega siempre el bloque «ESTILO COMÚN» antes de la escena.** Es lo que las hace compatibles con la plantilla (rojo UGR, grises cálidos, el cuadrado como motivo).
3. **Respeta las proporciones exactas.** Las imágenes a sangre y la de portada se estiran a su marco sin conservar la proporción; si no coinciden, se deforman.
4. **Deja el texto fuera de la imagen.** Los generadores escriben mal; los rótulos ya los pone LaTeX. Si aparecen letras, repite la generación con el negativo reforzado.
5. **Guarda los ficheros en `imagenes/` con el nombre indicado** y compila dos veces con `pdflatex`.
6. **Pies de imagen.** Los marcos a sangre ya llevan «Ilustración generada con IA». Mantenlo.

## ESTILO COMÚN (pégalo al principio de cada prompt)

```
Flat vector editorial illustration for a university technology talk. Geometric, minimal, clean. Strictly limited palette: UGR red #D53044 as the single main accent (deeper red #A8202F only for small details), charcoal #25272A, warm grey #4A4D50, light sand #F4F3F1 and pale line grey #E2E1DE. At most ONE secondary accent colour, used sparingly, chosen from blue #185FA5, green #3B8C2A, purple #534AB7 or amber #B07A17. Recurring motif: small rounded squares arranged on a loose grid like a mosaic, with varying opacity (some solid, some 10-45% tinted, some empty), used as texture and as the "pixels" of objects. Slightly rounded corners, uniform stroke weight, solid flat fills, generous negative space. Solid warm off-white #F4F3F1 background unless stated otherwise. No gradients, no drop shadows, no 3D rendering, no photorealism, no textures or noise, no text, no letters, no numbers, no logos, no watermarks, no human faces.
```

**Prompt negativo** (si el generador lo admite):

```
text, letters, words, numbers, logo, watermark, photo, photorealistic, 3D render, gradient, glossy, drop shadow, neon, dark background, human face, hands, cluttered, busy background
```

## Resumen

| Fichero | Proporción y tamaño | Dónde se usa |
|---|---|---|
| `portada.png` | **0,64 : 1** · 1152 × 1800 px | Panel derecho de la portada |
| `s01_infraestructura.jpeg` | 16 : 9 · 1920 × 1080 px | Apertura del bloque 01 |
| `s04_pasarela.jpeg` | 16 : 9 · 1920 × 1080 px | Apertura del bloque 04 |
| `s05_agente.jpeg` | 16 : 9 · 1920 × 1080 px | Apertura del bloque 05 |
| `s06_diplomas.jpeg` | 16 : 9 · 1920 × 1080 px | Apertura del bloque 06 |
| `mcp_conector.jpeg` | 16 : 9 · 1920 × 1080 px | Diapositiva «MCP: conectar IA y herramientas» |
| `skills_carpetas.jpeg` | 3 : 2 · 1800 × 1200 px | Diapositiva «Skills: saber hacer bajo demanda» |
| `inyeccion_prompt.jpeg` | 3 : 2 · 1800 × 1200 px | Diapositiva «Los agentes cambian el modelo de amenazas» |

**Zona segura en las cuatro imágenes a sangre (16 : 9).** La plantilla tapa el 25 % inferior con una banda oscura con el título y el pie. Coloca todo lo importante en el 70 % superior y deja el resto en calma (suelo, arena, unos pocos cuadrados).

---

## 1 · `portada.png` — portada

Formato: **1152 × 1800 px (0,64 : 1, vertical)**. Es el panel derecho de la portada; la plantilla añade una barra roja fina en su borde izquierdo.

Idea: una torre de servidores hecha con cuadrados, de la que salen «tokens» que se desvanecen hacia arriba.

```
[ESTILO COMÚN]

Scene: vertical composition on a sand #F4F3F1 background. In the centre, a tall server rack / GPU tower built entirely from stacked rounded squares, about 60% of the canvas height: charcoal #25272A squares form the frame, a handful of UGR red #D53044 squares act as active units, the rest are pale tints with thin line-grey outlines. Above the tower, small squares detach and drift upward in a loose column, getting smaller and more transparent as they rise, like tokens being generated. Keep an 8% safe margin on every side. Calm, balanced, lots of empty space. Aspect ratio 0.64:1 (1152x1800), portrait.
```

## 2 · `s01_infraestructura.jpeg` — «El LLM, nueva infraestructura básica»

Formato: 1920 × 1080 px (16 : 9). Apertura del bloque 01. Metáfora: el modelo de lenguaje como un servicio más junto al correo, las bases de datos y el almacenamiento.

```
[ESTILO COMÚN]

Scene: isometric flat view (30 degrees) of a calm, empty campus plot. Four small identical utility cabinets stand in a row on a sand-coloured ground plane. On the door of each one a simple pictogram, no text: an envelope (mail), a database cylinder, a cloud-with-folder (storage), and on the fourth, the newest and slightly larger, a speech bubble with a small spark. The first three are charcoal and pale grey; the fourth is solid UGR red #D53044. Thin charcoal conduits link all four to a stylised university building at the left, drawn as a simple block with a row of tiny rounded squares as its roof. Place every subject in the upper 70% of the canvas; leave the bottom 25% as quiet ground with a few scattered mosaic squares. 16:9, 1920x1080.
```

## 3 · `s04_pasarela.jpeg` — «Un único punto de entrada»

Formato: 1920 × 1080 px (16 : 9). Apertura del bloque 04. Muchos clientes, una pasarela, varios backends.

```
[ESTILO COMÚN]

Scene: left-to-right flow. On the left third, about a dozen small rounded-square "clients" with simple pictograms (laptop, browser window, code brackets, envelope) queue loosely and converge toward the centre. In the centre, a single tall doorway in solid UGR red #D53044 with a round keyhole, and three small key shapes floating beside it. On the right third, three server racks of different heights built from rounded squares, connected to the doorway by thin routed lines in warm grey #4A4D50; the smallest rack is drawn with a dashed outline to suggest a cloud backup. Everything in the upper 70% of the canvas; the bottom 25% stays calm with a few mosaic squares. 16:9, 1920x1080.
```

## 4 · `s05_agente.jpeg` — «De responder a actuar»

Formato: 1920 × 1080 px (16 : 9). Apertura del bloque 05. Un modelo en el centro, un banco de herramientas alrededor y un bucle.

```
[ESTILO COMÚN]

Scene: top-down view of a workbench on sand #F4F3F1. In the centre, a large charcoal #25272A rounded square (the model) surrounded by a thin circular arrow loop in UGR red #D53044. Laid out around it, flat tool pictograms in pale tints with thin outlines: a wrench, a magnifying glass, a folder, a terminal window (a rounded rectangle with a small ">" prompt symbol and a blinking cursor block, no words), a notebook with abstract lines. One tool, the magnifying glass, is solid UGR red, with a dashed path going from the central square to it and back. Plenty of empty space. All subjects in the upper 70% of the canvas; the bottom 25% remains calm with a few mosaic squares. 16:9, 1920x1080.
```

## 5 · `s06_diplomas.jpeg` — «11.500 diplomas, un único formato»

Formato: 1920 × 1080 px (16 : 9). Apertura del bloque 06. Del caos de documentos heterogéneos a una tabla ordenada.

```
[ESTILO COMÚN]

Scene: left-to-right transformation. On the left, a tall, slightly chaotic stack of paper certificates tilted at different angles; each sheet has a different layout made of abstract blocks: a circular seal in UGR red #D53044, a loose scribble line for a signature, a few grey bars as unreadable text lines, a small square for a logo. In the centre, a slim charcoal scanner frame or funnel with a thin arrow passing through it. On the right, a neat grid of aligned rounded-square cells forming a table, in sand with line-grey borders, with a few cells carrying small red check marks: order emerging from chaos. Everything in the upper 70% of the canvas; the bottom 25% stays calm with a few mosaic squares. 16:9, 1920x1080.
```

## 6 · `mcp_conector.jpeg` — MCP

Formato: 1920 × 1080 px (16 : 9). Va dentro de la diapositiva, junto a la cifra «N + M». Fondo arena o transparente. Idea: un conector estándar único entre clientes y servicios.

```
[ESTILO COMÚN]

Scene: one universal connector. On the left, three different client devices as simple flat pictograms stacked vertically: a laptop with a chat bubble, a code editor window, and an agent badge (a rounded square with a circular arrow). Each has a cable ending in exactly the same round plug. In the centre, a charcoal #25272A rounded-square hub with a grid of identical round sockets; one socket is highlighted in UGR red #D53044. On the right, four service pictograms stacked vertically: a folder, a ticket, a database cylinder, a cloud, each also connected with the very same plug. All plugs identical to convey a single standard. Centred composition, generous margins, sand or transparent background. 16:9, 1920x1080.
```

## 7 · `skills_carpetas.jpeg` — Skills

Formato: 1800 × 1200 px (3 : 2). Va junto a los tres pasos de la revelación progresiva. Idea: solo se ve la pestaña de cada carpeta hasta que hace falta una.

```
[ESTILO COMÚN]

Scene: a wall shelf holding a row of about eight closed folders standing upright, only their small tabs visible; the tabs are pale tints, one tab is UGR red #D53044. The folders themselves are sand with thin line-grey outlines. In front of the shelf, one folder pulled out and opened, outlined in charcoal #25272A, showing a sheet with abstract text lines and a small red check mark. A magnifying-glass outline hovers over the row of tabs. Calm, tidy, symmetrical, with generous margins. Aspect ratio 3:2, 1800x1200.
```

## 8 · `inyeccion_prompt.jpeg` — Modelo de amenazas

Formato: 1800 × 1200 px (3 : 2). Va a la izquierda de las tres amenazas. Idea: un documento con una instrucción oculta llega a un agente que tiene llaves.

```
[ESTILO COMÚN]

Scene: on the left, a neat document page with abstract grey text lines; a UGR red #D53044 sticky note peeks out from behind the page, marked with a small triangle with a dot inside (no words). A dashed red path leaves the document toward the centre, where a small charcoal #25272A rounded-square "agent" badge holds a ring of keys, standing in front of a padlock-shaped shield. On the right, a folder and a cloud pictogram; a faint dashed arrow from the agent toward the cloud is stopped by a small barrier, suggesting data that should not leave. Calm and explanatory, not alarming. Aspect ratio 3:2, 1800x1200.
```

---

## Lista de comprobación antes de aceptar una imagen

- Cabe en la paleta: rojo UGR, grises cálidos, arena y, como mucho, un acento secundario.
- No contiene letras, números ni logos.
- Las proporciones y los píxeles son los de la tabla.
- En las imágenes a sangre, lo importante queda en el 70 % superior.
- Se parece en trazo y densidad de cuadrados a las demás.
