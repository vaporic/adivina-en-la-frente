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
- Récord por mazo y métricas globales (partidas, aciertos, mejor ronda), con botón para borrarlas.
- Banda sonora chiptune sintetizada en el navegador y vibración, ambas desactivables.
- Aviso de "gira el teléfono" y bloqueo del apagado de pantalla mientras juegas.

- Instalable como PWA: se juega sin conexión y arranca sin barras del navegador.

Sin dependencias, sin build de terceros, sin red: un único archivo HTML.

## Instalar en el móvil

- **Android / Chrome / Edge**: aparece una tarjeta *Instalar* en la pantalla de inicio del juego.
- **iPhone / iPad**: Safari → Compartir → *Añadir a pantalla de inicio*. Apple no ofrece
  API de instalación, así que ahí sólo se puede explicar el camino.

Una vez instalado arranca en pantalla completa y funciona sin datos.

## Estructura

| Archivo | Para qué sirve |
| --- | --- |
| `index.html` | El juego. Fuente único de la verdad. |
| `build.py` | Envuelve el fuente en un documento completo e inyecta lo de la PWA. |
| `icons.py` | Genera los iconos. Sólo hace falta si cambia la marca. |
| `docs/index.html` | Lo que sirve GitHub Pages. **Generado — no editar a mano.** |
| `docs/manifest.webmanifest`, `docs/sw.js`, `docs/icons/` | La parte PWA. |

Tras tocar `index.html`:

```bash
python3 build.py
```

El manifiesto y el service worker se inyectan sólo en la copia de `docs/`: en el Artifact
esos archivos no existen y la CSP bloquearía la petición, así que el fuente se queda limpio.
Al subir una versión nueva, sube `CACHE` en `docs/sw.js`.

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

## Sonido

Todo se sintetiza en tiempo real con la Web Audio API — no hay ni un archivo de audio que
descargar. Cada efecto son unas pocas voces (osciladores cuadrados y triangulares, más ruido
blanco filtrado) con envolventes cortas, encadenadas a un compresor para que apilar notas no
sature. Hay arpegios distintos para acertar, pasar, empezar ronda, últimos cinco segundos,
fin de tiempo y récord nuevo.

Apagar el sonido no baja el volumen: deja de crear nodos.

**iOS necesita cuidado extra.** Mientras un `AudioContext` está suspendido, `currentTime` se
queda congelado en cero; si programas notas contra ese reloj, toda la envolvente cae en el
pasado y para cuando el audio arranca de verdad ya no queda nada que oír — silencio absoluto,
sin ningún error. Por eso cada efecto pasa por `play()`, que espera a que el contexto esté
realmente en `running` antes de programar nada. Además, al primer gesto se declara
`navigator.audioSession.type = "playback"` (Safari 16.4+), sin lo cual el interruptor físico
de silencio del iPhone calla también el audio de la web, y se dispara un buffer mudo, que es
el ritual que WebKit espera para dar permiso.

## Pantalla completa

Al empezar una ronda el juego pide `requestFullscreen()` y bloquea la rotación en horizontal
con `screen.orientation.lock()`; al acabar suelta la rotación para que leas el repaso en
vertical. Ninguna de las dos está garantizada — dentro de un `iframe` el navegador las
bloquea y **Safari en iPhone no tiene API de pantalla completa** — así que ambas van
envueltas y un fallo nunca corta la partida. En iPhone, la forma de jugar sin barras es
instalarlo desde Safari.

## Vibración

`navigator.vibrate` con un patrón por evento. **En iOS no funciona en ningún navegador** —
tampoco en Chrome, que allí es WebKit por obligación. No es una carencia de Safari que se
pueda rodear: el motor no expone la API. Donde no está, la fila esconde el interruptor y
muestra «No disponible» con el motivo, porque un interruptor muerto se lee como avería.
