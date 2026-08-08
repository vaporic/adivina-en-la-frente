#!/usr/bin/env python3
"""Genera docs/index.html para GitHub Pages.

index.html es el fuente que publica el Artifact: no lleva doctype ni <html>,
porque ahí lo envuelve la plataforma. Para Pages hace falta un documento
completo (sin doctype el navegador entra en quirks mode), así que este script
parte el fuente por <div id="app"> y lo reparte entre <head> y <body>.
"""

import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "index.html"
OUT = ROOT / "docs" / "index.html"
SPLIT = '<div id="app">'

src = SRC.read_text(encoding="utf-8")
if SPLIT not in src:
    raise SystemExit(f"No encuentro {SPLIT!r} en {SRC}")

head, body = src.split(SPLIT, 1)
body = SPLIT + body

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(
    "<!doctype html>\n"
    '<html lang="es">\n<head>\n'
    f"{head.strip()}\n"
    "</head>\n<body>\n"
    f"{body.strip()}\n"
    "</body>\n</html>\n",
    encoding="utf-8",
)
print(f"escrito {OUT} ({OUT.stat().st_size} bytes)")
