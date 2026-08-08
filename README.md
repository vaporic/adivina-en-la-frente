# ¡Adivina! — mímica para la frente

Juego de fiesta al estilo *Guess Up* / *Heads Up*, hecho para el móvil. Te pones el
teléfono en la frente, tus amigos actúan y tú adivinas antes de que se acabe el tiempo.

**Jugar:** https://vaporic.github.io/adivina-en-la-frente/

## Cómo se juega

1. Elige un mazo y la duración de la ronda.
2. Sujeta el móvil en la frente, en horizontal, con la pantalla hacia tus amigos.
3. **Inclina hacia abajo** cuando aciertes, **hacia arriba** para pasar.
4. Si los sensores no responden, toca la mitad derecha para acertar y la izquierda para pasar.

## Qué trae

- 8 mazos en español: Películas, Animales, Comida, Famosos, Mímica, Música, Deportes, Cosas.
- Rondas de 60, 90 o 120 segundos con cuenta atrás y barra de tiempo.
- Modo equipos A vs B con marcador acumulado.
- Repaso al final: toca cualquier palabra para corregir el resultado.
- Récord por mazo guardado en el propio dispositivo.
- Sonido sintetizado en el navegador, vibración, aviso de "gira el teléfono" y bloqueo
  del apagado de pantalla mientras juegas.

Sin dependencias, sin build de terceros, sin red: un único archivo HTML.

## Estructura

| Archivo | Para qué sirve |
| --- | --- |
| `index.html` | El juego. Fuente único de la verdad. |
| `build.py` | Envuelve el fuente en un documento HTML completo. |
| `docs/index.html` | Lo que sirve GitHub Pages. **Generado — no editar a mano.** |

Tras tocar `index.html`:

```bash
python3 build.py
```

## Control por inclinación

El acierto y el paso se deciden con la componente vertical de la normal de la pantalla,
calculada desde `deviceorientation`:

```js
pitch = cos(beta) * cos(gamma)   //  +1 mirando al cielo, -1 al suelo, 0 en vertical
```

Al ser independiente de la rotación, funciona igual en horizontal que en vertical, sin
tener que distinguir el modo de pantalla. Un umbral de ±0.6 dispara la acción y hay que
volver por debajo de 0.35 para rearmarla, así una sola inclinación no cuenta dos veces.

iOS 13+ pide permiso explícito para los sensores, y dentro de un `iframe` puede no llegar
nunca: por eso el control táctil no es un apaño, es un camino de primera clase.
