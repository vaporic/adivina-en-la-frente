#!/usr/bin/env python3
"""Genera los iconos PWA en docs/icons/.

Marca: una «A» de máquina recreativa — extruida en bloque, con filo crema y un
foco detrás — sobre un fondo coral que se oscurece hacia los bordes, con
confeti del juego alrededor. La misma cara del titular (Avenir Next Heavy) y la
misma paleta que la pantalla de partida.

La versión maskable encoge la marca dentro del círculo seguro del 80 % que
Android puede recortar, y mueve el confeti hacia dentro.

Ejecutar sólo cuando cambie la marca; los PNG van versionados en el repo.
"""

import math
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = pathlib.Path(__file__).parent / "docs" / "icons"

CORAL_HI = (255, 90, 130)   # centro del foco
CORAL_LO = (176, 22, 68)    # borde, para que el icono no se aplane
CREAM = (255, 244, 232)
INK = (34, 10, 30)          # el filo, casi negro
SIDE = (128, 16, 56)        # el canto extruido: granate, la sombra propia del coral
LIME = (184, 255, 60)
AMBER = (255, 176, 33)

FONT = "/System/Library/Fonts/Avenir Next.ttc"
HEAVY = 8  # índice de Avenir Next Heavy dentro del .ttc

SS = 4  # supersampling: dibujar en grande y reducir deja los bordes limpios

# Confeti fijo (nada aleatorio: el icono debe salir idéntico en cada ejecución).
# x, y y lado en fracción del lienzo; giro en grados.
CONFETTI = [
    (0.135, 0.175, 0.070, -18, LIME),
    (0.845, 0.150, 0.058, 24, CREAM),
    (0.905, 0.395, 0.050, -40, AMBER),
    (0.075, 0.455, 0.052, 32, CREAM),
    (0.190, 0.815, 0.060, 12, AMBER),
    (0.815, 0.800, 0.066, -28, LIME),
    (0.500, 0.088, 0.044, 45, CREAM),
    (0.955, 0.640, 0.040, 8, LIME),
    (0.048, 0.680, 0.042, -12, AMBER),
]


def radial_background(side, focus_y):
    """Coral que se oscurece hacia los bordes. Da volumen sin usar sombras."""
    n = 256
    y, x = np.mgrid[0:n, 0:n]
    dx = (x + 0.5) / n - 0.5
    dy = (y + 0.5) / n - focus_y
    t = np.clip(np.hypot(dx, dy) / 0.80, 0, 1) ** 1.45
    hi = np.array(CORAL_HI, dtype=float)
    lo = np.array(CORAL_LO, dtype=float)
    rgb = hi + (lo - hi) * t[..., None]
    small = Image.fromarray(rgb.astype("uint8"), "RGB")
    return small.resize((side, side), Image.LANCZOS)


def glow(side, cx, cy, r, strength):
    """Foco difuso detrás de la letra, como el halo de un cartel."""
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=strength)
    return mask.filter(ImageFilter.GaussianBlur(r * 0.55))


def draw_confetti(img, letter_ratio, inset):
    """inset acerca el confeti al centro para la versión recortable."""
    side = img.size[0]
    for fx, fy, fs, ang, color in CONFETTI:
        cx = (fx - 0.5) * inset * side + side / 2
        cy = (fy - 0.5) * inset * side + side / 2
        w = fs * side * (letter_ratio / 0.62)
        h = w * 0.62
        bit = Image.new("RGBA", (int(w), int(h)), color + (255,))
        bit = bit.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(bit, (int(cx - bit.width / 2), int(cy - bit.height / 2)))


def build(name, side, letter_ratio, radius_ratio, inset):
    big = side * SS
    focus_y = 0.42

    img = radial_background(big, focus_y).convert("RGBA")

    # El halo: crema muy transparente, sólo para separar la letra del fondo.
    img.alpha_composite(
        Image.composite(
            Image.new("RGBA", (big, big), CREAM + (255,)),
            Image.new("RGBA", (big, big), CREAM + (0,)),
            glow(big, big // 2, int(big * focus_y), int(big * 0.34), 66),
        )
    )

    draw_confetti(img, letter_ratio, inset)

    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, int(big * letter_ratio), index=HEAVY)
    stroke = max(1, int(big * 0.012))
    box = d.textbbox((0, 0), "A", font=font, stroke_width=stroke)
    depth = int(big * 0.105)
    # Se centra el conjunto letra + extrusión, no sólo la cara.
    x = (big - (box[2] - box[0]) - depth * 0.42) / 2 - box[0]
    y = (big - (box[3] - box[1]) - depth) / 2 - box[1]

    # Extrusión: la misma letra repetida en diagonal hasta formar el bloque.
    # El canto va en granate y sólo el último paso lleva filo oscuro, para que
    # se lea como un volumen y no como un contorno grueso.
    for i in range(depth, 0, -1):
        d.text(
            (x + i * 0.42, y + i), "A", font=font, fill=SIDE,
            stroke_width=stroke if i == depth else 0, stroke_fill=INK,
        )

    # Cara: crema con filo oscuro para que recorte sobre el coral.
    d.text((x, y), "A", font=font, fill=CREAM, stroke_width=stroke, stroke_fill=INK)

    # La cara plana se ve muerta: se le pasa un degradado vertical, blanco
    # arriba y crema abajo, por dentro del filo para no comérselo.
    top, bottom = y + box[1], y + box[3]
    rows = np.clip((np.arange(big) - top) / max(1.0, bottom - top), 0, 1)[:, None]
    shade = np.array((255, 255, 255), float) + (np.array(CREAM, float) - 255) * rows ** 0.85
    gradient = Image.fromarray(
        np.repeat(shade[:, None, :], big, axis=1).astype("uint8"), "RGB"
    ).convert("RGBA")

    face_mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(face_mask).text((x, y), "A", font=font, fill=255)
    img.paste(gradient, (0, 0), face_mask)

    if radius_ratio:
        corner = Image.new("L", (big, big), 0)
        ImageDraw.Draw(corner).rounded_rectangle(
            [0, 0, big - 1, big - 1], radius=int(big * radius_ratio), fill=255
        )
        img.putalpha(corner)

    img.resize((side, side), Image.LANCZOS).save(OUT / name)
    return name


# (archivo, lado, alto de la letra, radio de esquina, acercamiento del confeti)
SPECS = [
    ("icon-192.png", 192, 0.62, 0.22, 1.00),
    ("icon-512.png", 512, 0.62, 0.22, 1.00),
    ("icon-maskable-512.png", 512, 0.42, 0.0, 0.62),  # dentro del círculo seguro
    ("apple-touch-icon.png", 180, 0.62, 0.0, 1.00),   # iOS pone su propia máscara
]

OUT.mkdir(parents=True, exist_ok=True)
for spec in SPECS:
    print("escrito", build(*spec))
