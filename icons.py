#!/usr/bin/env python3
"""Genera los iconos PWA en docs/icons/.

Marca: fondo coral, una «A» crema en Avenir Next Heavy — la misma cara que usa
el titular del juego. La versión maskable encoge la letra para que Android
pueda recortarla en círculo sin comerse los vértices.

Ejecutar sólo cuando cambie la marca; los PNG van versionados en el repo.
"""

import pathlib
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(__file__).parent / "docs" / "icons"
CORAL = (255, 61, 110)
CREAM = (255, 244, 232)
INK = (23, 11, 38)
FONT = "/System/Library/Fonts/Avenir Next.ttc"
HEAVY = 8  # índice de Avenir Next Heavy dentro del .ttc

# (archivo, lado, fracción del lado que ocupa la letra, radio de esquina)
SPECS = [
    ("icon-192.png", 192, 0.72, 0.22),
    ("icon-512.png", 512, 0.72, 0.22),
    ("icon-maskable-512.png", 512, 0.50, 0.0),  # relleno completo + zona segura
    ("apple-touch-icon.png", 180, 0.72, 0.0),   # iOS aplica su propia máscara
]

SS = 4  # supersampling: dibujamos en grande y reducimos, así los bordes quedan limpios


def load_font(px):
    try:
        return ImageFont.truetype(FONT, px, index=HEAVY)
    except Exception:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", px)


def build(name, side, letter_ratio, radius_ratio):
    big = side * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if radius_ratio:
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big * radius_ratio), fill=CORAL)
    else:
        d.rectangle([0, 0, big - 1, big - 1], fill=CORAL)

    font = load_font(int(big * letter_ratio))
    box = d.textbbox((0, 0), "A", font=font)
    x = (big - (box[2] - box[0])) / 2 - box[0]
    y = (big - (box[3] - box[1])) / 2 - box[1]

    d.text((x, y + big * 0.012), "A", font=font, fill=INK + (70,))  # sombra corta
    d.text((x, y), "A", font=font, fill=CREAM)

    img.resize((side, side), Image.LANCZOS).save(OUT / name)
    return name


OUT.mkdir(parents=True, exist_ok=True)
for spec in SPECS:
    print("escrito", build(*spec))
