# Compilar la presentacion LaTeX

Este directorio contiene la presentacion en Beamer.

Archivo principal:
- presentacion.tex

Salidas esperadas:
- presentacion.pdf
- presentacion-notas.pdf

## Requisitos

- Tener una distribucion LaTeX instalada (TeX Live, MacTeX o similar).
- Tener disponible el comando pdflatex.

## Compilacion rapida

Desde este directorio, ejecuta:

```bash
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex
```

Esto genera y actualiza presentacion.pdf.

## PDF con notas del ponente

Para generar la version con notas en segunda pantalla:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -jobname=presentacion-notas '\def\showpresenternotes{1}\input{presentacion.tex}'
pdflatex -interaction=nonstopmode -halt-on-error -jobname=presentacion-notas '\def\showpresenternotes{1}\input{presentacion.tex}'
```

Esto genera y actualiza presentacion-notas.pdf.

## Compilar ambos en un solo bloque

```bash
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex && \
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex && \
pdflatex -interaction=nonstopmode -halt-on-error -jobname=presentacion-notas '\def\showpresenternotes{1}\input{presentacion.tex}' && \
pdflatex -interaction=nonstopmode -halt-on-error -jobname=presentacion-notas '\def\showpresenternotes{1}\input{presentacion.tex}'
```

## Limpieza opcional

Para borrar archivos auxiliares y conservar solo los PDF:

```bash
rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb
```
