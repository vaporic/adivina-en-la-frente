#!/usr/bin/env python3
"""Genera docs/index.html para GitHub Pages.

index.html es el fuente que publica el Artifact: no lleva doctype ni <html>,
porque ahí lo envuelve la plataforma. Para Pages hace falta un documento
completo (sin doctype el navegador entra en quirks mode), así que este script
parte el fuente por <div id="app"> y lo reparte entre <head> y <body>.

Aquí también se inyecta lo que sólo tiene sentido en Pages: el manifiesto y el
service worker. En el Artifact esos dos archivos no existen y la CSP bloquearía
la petición, así que el fuente se queda limpio.
"""

import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "index.html"
OUT = ROOT / "docs" / "index.html"
SPLIT = '<div id="app">'

PWA_HEAD = """
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" href="icons/icon-192.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="¡Adivina!">
"""

PWA_BODY = """
<script>
  if ("serviceWorker" in navigator) {
    addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
</script>
"""

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
    f"{PWA_HEAD.strip()}\n"
    "</head>\n<body>\n"
    f"{body.strip()}\n"
    f"{PWA_BODY.strip()}\n"
    "</body>\n</html>\n",
    encoding="utf-8",
)
print(f"escrito {OUT} ({OUT.stat().st_size} bytes)")
