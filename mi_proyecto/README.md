# 🐍 Snake Pygame

> Proyecto universitario desarrollado para la asignatura de **Programación Orientada a Objetos**  
> CORPORACIÓN UNIVERSITARIA AMERICANA - 2026

---

## Tabla de Contenidos

- [Descripción del Problema](#descripción-del-problema)
- [Objetivos](#objetivos)
- [Funcionalidades](#funcionalidades)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Manual de Usuario](#manual-de-usuario)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Autores](#autores)

---

## Descripción del Problema

La principal motivación de este proyecto nace de nuestro cariño hacia los videojuegos y del deseo genuino de conocer qué hay detrás de escenas: cómo un juego cobra vida, cómo responde a cada acción del jugador en tiempo real, cómo gestiona su propio estado interno y cómo logra que una experiencia tan sencilla como mover una serpiente por una pantalla resulte tan entretenida y adictiva.

Elegimos recrear el clásico **Snake de Nokia** porque es un juego que prácticamente todos conocemos, lo que nos permite concentrarnos en el *cómo* está construido en lugar del *qué* hace. A través de este desarrollo comprendimos de primera mano conceptos como el ciclo de juego, la detección de colisiones, el manejo de eventos de teclado y la separación entre la lógica interna del juego y lo que el jugador ve en pantalla. En resumen, desmontamos pieza por pieza un videojuego real y lo volvimos a ensamblar nosotros mismos.

---

## Objetivos

El objetivo principal es que cualquier persona que abra el juego pueda disfrutar de una experiencia sencilla, directa y entretenida. Queremos que el jugador sienta esa chispa de emoción característica del Snake: la tensión de ver crecer la serpiente, la satisfacción de superar el propio récord y la adrenalina de navegar el tablero cuando el espacio libre empieza a escasear.

Más allá del entretenimiento, el juego invita a que cada partida sea un reto personal: ¿hasta qué longitud puede llegar la serpiente? ¿Cuántos puntos es posible acumular antes de cometer un error? Esa pregunta, tan simple como poderosa, es la que mantiene al jugador intentando una partida más.

Desde el punto de vista académico, el proyecto busca demostrar de forma práctica y funcional los cuatro pilares de la Programación Orientada a Objetos aplicados a un problema real, comprobando que el código bien diseñado no solo funciona, sino que es fácil de entender, modificar y ampliar.

---

## Funcionalidades

### Pantalla de inicio
- Selección de dificultad con las teclas `1`, `2` o `3` antes de comenzar a jugar.
- Leyenda visual que explica los tres tipos de ítems disponibles en el tablero.
- Posibilidad de iniciar directamente con `ENTER` (selecciona dificultad Fácil por defecto).

### Tres niveles de dificultad
| Nivel | Velocidad | Obstáculos |
|---|---|---|
| `1` Fácil | Lenta | Sin obstáculos |
| `2` Normal | Media | Sin obstáculos |
| `3` Difícil | Alta | Con muros interiores |

### Tres tipos de ítems coleccionables
| Ítem | Color | Efecto |
|---|---|---|
| Comida Normal | 🟢 Verde | +10 puntos, la serpiente crece 1 segmento |
| Comida Dorada | 🟡 Dorado | +30 puntos, crece 2 segmentos, desaparece en 8 segundos |
| Turbo Especial | 🔵 Azul | +20 puntos, crece 1 segmento, acelera la serpiente por 5 segundos |

### Panel de información (HUD)
Durante el juego, la barra superior muestra en todo momento:
- Puntaje actual de la partida.
- Récord máximo alcanzado en la sesión.
- Nivel de dificultad activo.
- Velocidad de movimiento.
- Longitud actual de la serpiente.
- Notificación del último ítem recogido y tiempo restante del turbo.

### Pausa
- El juego puede pausarse en cualquier momento con `P` o `ESC`.
- Mientras está pausado aparece un panel semitransparente con las opciones disponibles.
- Se puede reanudar o volver al menú principal desde la pausa.

### Fin de partida
- Al colisionar con una pared, con el propio cuerpo o con un obstáculo, se muestra la pantalla de Game Over.
- Se presentan las estadísticas finales: puntaje, récord, longitud alcanzada, dificultad y velocidad.
- El jugador puede reiniciar la partida o volver al menú sin cerrar el juego.

---

## Tecnologías Utilizadas

### Lenguaje
- **Python 3.10+** — lenguaje principal del proyecto.

### Biblioteca principal
- **Pygame 2.6** — motor de ventana, renderizado gráfico, manejo de eventos de teclado y control del ciclo de juego.

### Módulos estándar de Python utilizados
- `abc` — para definir clases abstractas.
- `collections.deque` — estructura de datos eficiente para el cuerpo de la serpiente.
- `time` — control de tiempo para movimiento, expiración de ítems y efecto turbo.
- `random` — generación aleatoria de posición y tipo de los consumibles.
- `typing` — anotaciones de tipos estáticos en todas las funciones.
- `unittest` y `unittest.mock` — suite de pruebas automatizadas.

### Herramientas de desarrollo
- **Visual Studio Code** — editor de código.
- **Git** — control de versiones.
- **pip** — gestor de dependencias de Python.
- **pytest** — ejecución de pruebas unitarias (opcional).

---

## Instalación

### Requisitos previos
- Python **3.10 o superior** instalado en el sistema.
- pip (viene incluido con Python).
- Sistema operativo: Windows, macOS o Linux.

### Pasos

**1. Descargar y extraer el proyecto**

Descarga el archivo `snake_poo_pygame_v2.zip`, haz clic derecho sobre él y selecciona **Extraer aquí**. Navega dentro de las carpetas extraídas hasta encontrar la que contiene el archivo `main.py`.

**2. Abrir una terminal en esa carpeta**

En Visual Studio Code: abre la carpeta con *File → Open Folder*, luego abre la terminal con *Terminal → New Terminal*.

**3. Instalar las dependencias**

```bash
pip install -r requirements.txt
```

Esto instalará Pygame automáticamente. Si el comando falla, intenta:

```bash
pip install pygame
```

---

## Ejecución

Una vez instaladas las dependencias, escribe en la terminal:

```bash
python main.py
```

Si `python` no es reconocido, prueba con:

```bash
py main.py
```

o bien:

```bash
python3 main.py
```

La ventana del juego se abrirá mostrando la pantalla de inicio. Desde allí pulsa `1`, `2` o `3` para elegir la dificultad y comenzar a jugar.

> **Importante:** el comando debe ejecutarse siempre desde la carpeta que contiene `main.py`. Si la terminal muestra una ruta diferente, navega primero con `cd ruta/a/snake_poo_pygame`.

---

## Manual de Usuario

### Pantalla de inicio

Al abrir el juego verás el menú principal con fondo oscuro y cuadrícula retro. Desde aquí puedes elegir con qué dificultad quieres jugar antes de lanzarte a la partida.

```
┌──────────────────────────────────────────┐
│           ■ SNAKE ■                      │
│    Nokia Classic  //  Python POO         │
│                                          │
│  SELECCIONA DIFICULTAD:                  │
│    1 → FÁCIL    Sin obstáculos · lento   │
│    2 → NORMAL   Sin obstáculos · medio   │
│    3 → DIFÍCIL  Con obstáculos · rápido  │
│                                          │
│  ÍTEMS DEL TABLERO:                      │
│    ■ Comida Normal  → +10 pts, +1 seg    │
│    ■ Comida Dorada  → +30 pts, +2 seg    │
│    ■ Turbo Especial → +20 pts, turbo     │
│                                          │
│  Pulsa 1 · 2 · 3 para iniciar            │
└──────────────────────────────────────────┘
```

### Durante el juego

La serpiente se mueve de forma continua. Tu trabajo es guiarla para que coma los ítems que aparecen en el tablero sin chocar contra nada. Cuanto más come, más larga se vuelve y más difícil es maniobrar.

**Controles de movimiento:**

| Tecla | Acción |
|---|---|
| `↑` o `W` | Mover hacia arriba |
| `↓` o `S` | Mover hacia abajo |
| `←` o `A` | Mover hacia la izquierda |
| `→` o `D` | Mover hacia la derecha |
| `P` o `ESC` | Pausar / Reanudar |

> La serpiente no puede girar 180° sobre sí misma. Si vas hacia la derecha, no puedes ir directamente a la izquierda.

**Lectura del panel superior (HUD):**

```
PTS 00150   [ NORMAL ]   ⚡TURBO 3.2s   LEN 012
REC 00330     VEL 10
```

- **PTS** — puntos acumulados en la partida actual.
- **REC** — récord máximo de la sesión.
- **VEL** — velocidad actual de la serpiente.
- **LEN** — longitud actual en segmentos.
- **TURBO** — aparece cuando la serpiente está acelerada y muestra el tiempo restante.

### Los tres tipos de ítems

**Comida Normal (verde):** aparece siempre en el tablero. Al comerla sumas 10 puntos y la serpiente crece un segmento.

**Comida Dorada (dorada/amarilla):** aparece ocasionalmente. Vale 30 puntos y crece 2 segmentos, pero desaparece en 8 segundos. Cuando le queda poco tiempo, empieza a parpadear como advertencia.

**Turbo Especial (azul):** aparece de vez en cuando. Vale 20 puntos, crece 1 segmento y además acelera la serpiente durante 5 segundos. Durante el turbo, la velocidad aumenta y el contador aparece en el HUD.

### Pantalla de pausa

Pulsa `P` o `ESC` en cualquier momento para pausar. El juego se detiene y aparece un panel con las opciones disponibles:

- `P` / `ESC` → Reanudar la partida.
- `M` → Volver al menú principal.

### Pantalla de Game Over

La partida termina si la serpiente choca contra una pared, contra su propio cuerpo o contra un muro interior (en dificultad Difícil). Se muestra un resumen con tus estadísticas finales:

```
        GAME OVER
  ─────────────────────
  Puntaje        00150
  Récord         00330
  Longitud          12
  Dificultad    Normal
  Velocidad         10
  ─────────────────────
  ENTER / R  →  Nueva partida
  M          →  Menú principal
```

### Consejos para principiantes

- Empieza en **Fácil** para familiarizarte con los controles y la velocidad.
- Intenta siempre moverte en espiral hacia el centro del tablero, dejando espacio libre alrededor.
- La **Comida Dorada** vale mucho, pero no te arriesgues si la serpiente ya es larga.
- En **Difícil**, aprende primero dónde están los muros antes de ir por los ítems.

---

## Estructura del Proyecto

```
snake_poo_pygame/
│
├── main.py                 → Punto de entrada. Arranca el juego.
├── requirements.txt        → Lista de dependencias (pygame).
├── README.md               → Este archivo.
│
├── modelos/                → Las entidades del juego
│   ├── elemento_juego.py   → Clase base de todo objeto visible en el tablero.
│   ├── consumible.py       → Los tres tipos de ítems coleccionables.
│   ├── serpiente.py        → La serpiente del jugador: movimiento y crecimiento.
│   └── obstaculo.py        → Los muros interiores del nivel Difícil.
│
├── servicios/              → La lógica interna del juego
│   └── partida.py          → Coordina todo: estado, puntaje, colisiones y tiempo.
│
├── interfaz/               → Lo que el jugador ve en pantalla
│   └── ventana_juego.py    → Dibuja el juego y captura las teclas del usuario.
│
├── pruebas/                → Pruebas automáticas
│   └── test_juego.py       → 54 pruebas que verifican que todo funcione bien.
│
└── docs/
    └── INFORME_TECNICO.md  → Documentación técnica completa del proyecto.
```

---

## Autores

Proyecto desarrollado por:

- **Juan Esteban Giraldo Suárez**
- **Aldimar Andrés Saltarín Arteta**
- **Jhonn Andrés Colina Ricardo**

Asignatura: Programación Orientada a Objetos  
CORPORACIÓN UNIVERSITARIA AMERICANA, 2026 - II
