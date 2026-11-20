# Informe Técnico — Snake Pygame

**Asignatura:** Programación Orientada a Objetos  
**Proyecto:** Videojuego Snake — Python + Pygame  
**Corporación Universitaria Americana - 2026**

**Autores:**
- Juan Esteban Giraldo Suárez
- Aldimar Andrés Saltarín Arteta
- Jhonn Andrés Colina Ricardo

---

## Tabla de Contenidos

1. [Análisis del Problema](#1-análisis-del-problema)
2. [Diseño Inicial](#2-diseño-inicial)
3. [Arquitectura](#3-arquitectura)
4. [Aplicación de POO](#4-aplicación-de-poo)
5. [Construcción de la Interfaz](#5-construcción-de-la-interfaz)
6. [Proceso de Desarrollo](#6-proceso-de-desarrollo)
7. [Pruebas](#7-pruebas)
8. [Problemas y Soluciones](#8-problemas-y-soluciones)
9. [Conclusiones](#9-conclusiones)

---

## 1. Análisis del Problema

### Necesidad identificada

El proyecto surge como respuesta a un reto académico: demostrar los cuatro pilares de la Programación Orientada a Objetos a través de un software real y funcional, no mediante ejemplos aislados en papel. Se eligió el videojuego Snake porque combina una lógica lo suficientemente rica para justificar el diseño orientado a objetos, y una interfaz lo suficientemente sencilla para que el foco permanezca en el código y no en la complejidad visual.

### Público objetivo

El juego está pensado para dos tipos de usuario simultáneamente: el jugador casual que quiere entretenerse con una mecánica simple y adictiva, y el estudiante o docente que quiere revisar cómo se aplican los conceptos de POO dentro de un proyecto real y ejecutable.

### Funcionalidades identificadas

Antes de escribir una sola línea de código se definió la lista completa de lo que el juego debía ser capaz de hacer:

- Mostrar una pantalla de inicio con selección de dificultad.
- Mover una serpiente de forma continua respondiendo al teclado.
- Generar ítems coleccionables de distintos tipos con efectos diferentes.
- Detectar colisiones con paredes, con el propio cuerpo y con obstáculos.
- Mantener un puntaje y un récord durante la sesión.
- Mostrar un panel de información en tiempo real (HUD).
- Permitir pausar y reanudar la partida.
- Presentar una pantalla de fin de partida con estadísticas.
- Funcionar en tres niveles de dificultad con comportamientos distintos.

### Limitaciones

- El juego no guarda el récord entre sesiones (se reinicia al cerrar).
- No tiene modo multijugador.
- La ventana tiene un tamaño fijo de 600 × 500 píxeles y no es redimensionable.
- No incluye sonido ni música.
- El tablero es siempre del mismo tamaño independientemente de la dificultad.

---

## 2. Diseño Inicial

### Planificación de clases

Antes de construir nada, se identificaron las entidades del problema y se les asignó una responsabilidad única a cada una. Este principio, conocido como separación de responsabilidades, fue la guía principal del diseño.

| Clase identificada | Responsabilidad asignada |
|---|---|
| `ElementoJuego` | Base común de todo objeto que ocupa una celda del tablero. |
| `Consumible` | Generalizar el comportamiento de cualquier ítem que la serpiente puede recoger. |
| `ComidaNormal` | Ítem básico: puntos bajos, siempre disponible. |
| `ComidaDorada` | Ítem premium: más puntos, pero desaparece con el tiempo. |
| `ComidaEspecial` | Ítem turbo: puntos medios más un efecto temporal de velocidad. |
| `Obstaculo` | Muro interior inamovible que aparece en el nivel Difícil. |
| `Serpiente` | Gestionar el cuerpo, la dirección y el movimiento del jugador. |
| `Partida` | Coordinar el ciclo completo del juego: estado, puntaje, colisiones y tiempo. |
| `VentanaJuego` | Mostrar el juego en pantalla y capturar las teclas del usuario. |

### Decisión de separar lógica e interfaz

Desde el principio se decidió que `Partida` no debía saber nada sobre Pygame, y que `VentanaJuego` no debía contener ninguna lógica de juego. Esta separación permite, por ejemplo, ejecutar las pruebas automatizadas sin necesidad de abrir ninguna ventana gráfica, y hace que el código sea mucho más fácil de mantener y modificar.

### Jerarquía de herencia planificada

```
ElementoJuego  (clase base abstracta)
├── Consumible  (clase abstracta intermedia)
│   ├── ComidaNormal
│   ├── ComidaDorada
│   └── ComidaEspecial
└── Obstaculo
```

Esta jerarquía garantiza que todo objeto del tablero comparte una interfaz común (`dibujar` y `obtener_posicion`), y que todos los ítems coleccionables además comparten el contrato de `aplicar_efecto`.

---

## 3. Arquitectura

El proyecto se organiza en tres capas bien diferenciadas que se comunican en una sola dirección: la interfaz consulta a los servicios, y los servicios consultan a los modelos. Ninguna capa inferior conoce a la superior.

```
┌──────────────────────────────────────────────────────────┐
│  CAPA DE PRESENTACIÓN   interfaz/ventana_juego.py        │
│  Dibuja el juego, captura teclas, llama a Partida        │
└─────────────────────────┬────────────────────────────────┘
                          │  Asociación (lee estado, delega acciones)
┌─────────────────────────▼────────────────────────────────┐
│  CAPA DE SERVICIO       servicios/partida.py             │
│  Coordina el ciclo de juego, puntaje, colisiones, tiempo │
└──────────────┬───────────────────────┬───────────────────┘
               │  Composición          │  Agregación
┌──────────────▼──────┐   ┌────────────▼─────────────────┐
│  modelos/           │   │  modelos/                     │
│  serpiente.py       │   │  consumible.py / obstaculo.py │
└─────────────────────┘   └──────────────────────────────┘
```

### Flujo de un frame de juego

Cada vez que el jugador pulsa una tecla o simplemente transcurre tiempo, ocurre lo siguiente en ese orden:

1. `VentanaJuego` detecta el evento de teclado y llama al método correspondiente de `Partida`.
2. `Partida.actualizar()` acumula el tiempo transcurrido y, cuando corresponde, mueve la serpiente.
3. Se verifican colisiones: pared, propio cuerpo, obstáculos, ítems.
4. Si hay colisión con un ítem, se llama a `consumible.aplicar_efecto()` de forma polimórfica.
5. `VentanaJuego` lee el estado actual de `Partida` y dibuja el frame en pantalla.

### Comunicación entre componentes

| Relación | Tipo | Descripción |
|---|---|---|
| `Partida` → `Serpiente` | Composición | Partida crea y destruye la serpiente. Sin Partida no hay Serpiente. |
| `Partida` → `[Consumible]` | Agregación | Partida gestiona la lista de ítems, pero cada ítem existe independientemente. |
| `Partida` → `[Obstaculo]` | Agregación | Igual que los consumibles: lista dinámica gestionada por Partida. |
| `VentanaJuego` → `Partida` | Asociación | La ventana recibe una Partida al construirse pero no la crea ni la destruye. |

---

## 4. Aplicación de POO

### Tabla de conceptos aplicados

| Concepto | Clase o método | Archivo | Explicación |
|---|---|---|---|
| **Clases y objetos** | `Serpiente` | `modelos/serpiente.py` | Representa al jugador. Encapsula el cuerpo, la dirección y la lógica de movimiento. |
| **Clases y objetos** | `Partida` | `servicios/partida.py` | Coordina el ciclo completo del juego como una máquina de estados. |
| **Clases y objetos** | `VentanaJuego` | `interfaz/ventana_juego.py` | Gestiona la ventana Pygame, el dibujo y los eventos de teclado. |
| **Encapsulamiento** | `_cuerpo` / `cuerpo` | `modelos/serpiente.py` | El cuerpo se expone como copia para evitar modificaciones externas accidentales. |
| **Encapsulamiento** | `_direccion` / `direccion` | `modelos/serpiente.py` | El setter rechaza giros de 180° para prevenir auto-colisiones. |
| **Encapsulamiento** | `_puntaje` / `puntaje` | `servicios/partida.py` | El setter impide que el puntaje tome valores negativos. |
| **Encapsulamiento** | `_velocidad` / `velocidad` | `servicios/partida.py` | La velocidad se mantiene siempre entre un mínimo y un máximo definidos. |
| **Encapsulamiento** | `_estado` / `estado` | `servicios/partida.py` | Solo acepta los cuatro estados válidos de la máquina FSM. |
| **Herencia** | `Consumible` hereda de `ElementoJuego` | `modelos/consumible.py` | Consumible añade el contrato de `aplicar_efecto` sobre la base de ElementoJuego. |
| **Herencia** | `ComidaNormal` hereda de `Consumible` | `modelos/consumible.py` | Especializa el efecto: +10 puntos, +1 segmento, sin tiempo límite. |
| **Herencia** | `ComidaDorada` hereda de `Consumible` | `modelos/consumible.py` | Especializa el efecto: +30 puntos, +2 segmentos, expira en 8 segundos. |
| **Herencia** | `ComidaEspecial` hereda de `Consumible` | `modelos/consumible.py` | Especializa el efecto: +20 puntos, turbo de velocidad por 5 segundos. |
| **Herencia** | `Obstaculo` hereda de `ElementoJuego` | `modelos/obstaculo.py` | Implementa un muro inamovible reutilizando la base de ElementoJuego. |
| **Polimorfismo** | `aplicar_efecto()` | `servicios/partida.py` | Se llama sobre cualquier Consumible sin saber su tipo concreto. Cada subclase responde diferente. |
| **Polimorfismo** | `dibujar()` | `modelos/consumible.py` / `obstaculo.py` | Cada subclase dibuja su propia apariencia visual sin que el llamador lo sepa. |
| **Abstracción** | `ElementoJuego(ABC)` | `modelos/elemento_juego.py` | Define el contrato mínimo de todo objeto del tablero: posición y capacidad de dibujarse. |
| **Abstracción** | `Consumible(ABC)` | `modelos/consumible.py` | Añade el contrato de efecto al ser recogido, sin implementarlo. |
| **Relaciones** | `Partida` ↔ `Serpiente` | `servicios/partida.py` | Composición: Partida crea la serpiente y controla su ciclo de vida completo. |
| **Relaciones** | `Partida` ↔ `[Consumible]` | `servicios/partida.py` | Agregación: Partida gestiona la colección dinámica de ítems en el tablero. |
| **Relaciones** | `VentanaJuego` ↔ `Partida` | `interfaz/ventana_juego.py` | Asociación: la ventana usa Partida para leer el estado y delegar acciones. |

### Encapsulamiento — ejemplos de código

El setter de `direccion` en `Serpiente` valida que no se pueda girar en sentido contrario al movimiento actual:

```python
# modelos/serpiente.py
@direccion.setter
def direccion(self, nueva_direccion):
    if nueva_direccion == OPUESTOS.get(self._direccion):
        return  # giro de 180° ignorado silenciosamente
    self._direccion = nueva_direccion
```

El setter de `puntaje` en `Partida` impide valores negativos y actualiza el récord automáticamente:

```python
# servicios/partida.py
@puntaje.setter
def puntaje(self, valor):
    if valor < 0:
        raise ValueError("El puntaje no puede ser negativo")
    self._puntaje = valor
    if self._puntaje > self._record:
        self._record = self._puntaje
```

### Polimorfismo — ejemplo de código

Este es el punto central del diseño: `Partida` llama a `aplicar_efecto` sobre cualquier consumible sin usar `isinstance` ni `type`. Cada subclase responde de forma completamente diferente:

```python
# servicios/partida.py
def _verificar_consumo(self):
    cabeza = self._serpiente.cabeza
    for consumible in self._consumibles:
        if consumible.activo and consumible.obtener_posicion() == cabeza:
            # POLIMORFISMO: sin isinstance, sin type, sin if/elif por tipo
            mensaje = consumible.aplicar_efecto(self._serpiente, self)
            self._ultimo_efecto = mensaje
            break
```

### Abstracción — ejemplo de código

`ElementoJuego` establece el contrato que toda entidad del tablero debe cumplir:

```python
# modelos/elemento_juego.py
class ElementoJuego(ABC):
    @abstractmethod
    def dibujar(self, superficie: pygame.Surface) -> None:
        ...
    @abstractmethod
    def obtener_posicion(self) -> Tuple[int, int]:
        ...
```

Ninguna subclase puede instanciarse sin implementar ambos métodos. Python lo impide en tiempo de ejecución.

---

## 5. Construcción de la Interfaz

### Biblioteca seleccionada

Se utilizó **Pygame 2.6**, una biblioteca de Python especializada en el desarrollo de videojuegos en 2D. Pygame proporciona todo lo necesario: una ventana gráfica, un bucle de eventos, funciones de dibujo de rectángulos, líneas y círculos, y un reloj para controlar los fotogramas por segundo.

Se eligió Pygame por encima de alternativas como `tkinter` o `arcade` porque ofrece control total sobre cada píxel de la pantalla y un manejo de eventos de teclado preciso y en tiempo real, ambos requisitos esenciales para un videojuego de acción.

### Diseño de la interfaz

La estética está inspirada en las pantallas LCD verdes de los teléfonos Nokia de los años 90. Se definió una paleta de seis colores todos en tonos verde oliva que se mantiene coherente en todas las pantallas:

| Token | Color | Uso |
|---|---|---|
| `LCD_FONDO` | Verde claro (#9BB06A) | Área de juego |
| `LCD_OSCURO` | Verde muy oscuro (#2D3B1E) | Menú y HUD |
| `LCD_MEDIO` | Verde medio (#4A7C3F) | Bordes y separadores |
| `LCD_BRILLO` | Verde pálido (#C8DC96) | Títulos y valores importantes |
| `LCD_TEXTO_SEC` | Verde apagado (#6B8C52) | Texto secundario |
| `LCD_GRID` | Verde suave (#8CA05F) | Líneas de cuadrícula |

La ventana tiene dimensiones fijas de **600 × 500 píxeles**. Los primeros 50 píxeles de alto están reservados para el HUD, y el resto forma el tablero de juego dividido en una cuadrícula de celdas de 20 × 20 píxeles, lo que resulta en 30 columnas y 22 filas.

El tablero se renderiza sobre una **subsuperficie** de Pygame, lo que garantiza que los elementos del juego nunca puedan sobreescribir accidentalmente el HUD superior.

### Controles implementados

| Tecla | Estado del juego | Acción |
|---|---|---|
| `1` / `2` / `3` | MENU | Iniciar partida con esa dificultad |
| `ENTER` | MENU | Iniciar partida en Fácil |
| `↑` `↓` `←` `→` / `W` `A` `S` `D` | JUGANDO | Cambiar dirección de la serpiente |
| `P` / `ESC` | JUGANDO | Pausar |
| `P` / `ESC` | PAUSADO | Reanudar |
| `M` | PAUSADO / GAME_OVER | Ir al menú principal |
| `R` / `ENTER` | GAME_OVER | Reiniciar partida |

### Eventos y callbacks

Pygame genera un evento por cada acción del usuario. `VentanaJuego` los captura en su método `_procesar_eventos()` y los delega a `Partida` según el estado activo:

```python
# interfaz/ventana_juego.py
def _manejar_tecla(self, tecla):
    estado = self._partida.estado

    if estado == ESTADO_JUGANDO:
        if tecla in (pygame.K_UP, pygame.K_w):
            self._partida.cambiar_direccion(ARRIBA)
        elif tecla in (pygame.K_p, pygame.K_ESCAPE):
            self._partida.pausar()

    elif estado == ESTADO_GAME_OVER:
        if tecla in (pygame.K_r, pygame.K_RETURN):
            self._partida.reiniciar()
```

### Comunicación con las clases

`VentanaJuego` mantiene una referencia a `Partida` pero no modifica su estado directamente. Solo llama a métodos públicos como `cambiar_direccion()`, `pausar()` o `reiniciar()`. Para dibujar el frame, consulta las propiedades de solo lectura de `Partida`: `serpiente`, `consumibles`, `obstaculos`, `puntaje`, `record`, `estado`, etc.

### Capturas de pantalla

> Las capturas de pantalla deben añadirse aquí una vez el juego esté en ejecución.  
> Se recomienda incluir al menos: pantalla de inicio, partida en curso, pausa y Game Over.

---

## 6. Proceso de Desarrollo

### 1. Formulación de la idea

El punto de partida fue la consigna académica: construir un videojuego completo usando Python y Pygame, demostrando los pilares de la POO. Se eligió Snake porque su mecánica es simple de entender pero suficientemente compleja para justificar una arquitectura bien diseñada.

### 2. Identificación de funcionalidades

Se hizo una lista completa de todo lo que el juego debía hacer antes de tocar el teclado. Esta etapa fue fundamental para no improvisar durante el desarrollo y para poder distribuir el trabajo de manera organizada entre los integrantes del equipo.

### 3. Diseño de clases

Con la lista de funcionalidades en mano, se identificaron las entidades del problema y se diseñó la jerarquía de herencia. Se dibujó el diagrama de clases a mano antes de comenzar a programar, definiendo qué atributos y métodos tendría cada clase y cómo se relacionarían entre sí.

### 4. Construcción de la lógica

Se implementaron primero las clases del modelo (`ElementoJuego`, `Consumible`, `Serpiente`, `Obstaculo`) y luego la clase `Partida`. Esta etapa no requirió Pygame en absoluto, lo que permitió verificar el comportamiento con pruebas unitarias simples desde el principio.

### 5. Desarrollo de la interfaz

Con la lógica ya funcional y probada, se construyó `VentanaJuego`. Se definió la paleta de colores, se diseñó el HUD, se implementó el renderizado de cada estado (menú, juego, pausa, game over) y se conectaron los eventos de teclado con los métodos de `Partida`.

### 6. Integración

Se conectaron las tres capas en `main.py`, que tiene menos de 30 líneas: obtiene las dimensiones del tablero de `VentanaJuego`, crea una instancia de `Partida` con esas dimensiones, le pasa la partida a `VentanaJuego` y arranca el bucle principal.

```python
# main.py
columnas, filas = VentanaJuego.obtener_dimensiones()
partida = Partida(columnas=columnas, filas=filas)
ventana = VentanaJuego(partida=partida)
ventana.ejecutar()
```

### 7. Pruebas y correcciones

Se ejecutó la suite de 54 pruebas automatizadas para verificar que toda la lógica funcionara correctamente. Luego se jugaron partidas reales para detectar problemas visuales y de jugabilidad, entre ellos el error de colisión instantánea en el nivel Difícil que se documenta en la sección siguiente.

---

## 7. Pruebas

### Tabla de pruebas de funcionamiento

| Prueba | Acción realizada | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| **Prueba 1 — Movimiento y crecimiento** | Se inicia una partida en Fácil. La serpiente come tres ítems de Comida Normal consecutivos. | La longitud pasa de 3 a 6 segmentos y el puntaje sube a 30. | ✅ Correcto. La longitud y el puntaje aumentan exactamente como se esperaba. |
| **Prueba 2 — Rechazo de giro de 180°** | Con la serpiente moviéndose hacia la derecha, se pulsa la tecla de izquierda. | La serpiente ignora el giro y continúa hacia la derecha sin colisionar consigo misma. | ✅ Correcto. El setter de `_direccion` rechaza el giro prohibido silenciosamente. |
| **Prueba 3 — Expiración de Comida Dorada** | Aparece una Comida Dorada en el tablero y se espera sin recogerla. | Después de 8 segundos, el ítem parpadea y desaparece del tablero. | ✅ Correcto. El ítem parpadea en los últimos 2 segundos y se elimina al expirar. |
| **Prueba 4 — Turbo de velocidad** | Se recoge una Comida Especial (azul). | La serpiente acelera visiblemente, el HUD muestra el contador de turbo y al cabo de 5 segundos la velocidad vuelve al valor original. | ✅ Correcto. El turbo se activa, se muestra en el HUD y se desactiva automáticamente. |
| **Prueba 5 — Entrada inválida: puntaje negativo** | En la prueba unitaria se asigna `partida.puntaje = -50`. | El sistema debe lanzar un `ValueError` impidiendo el valor negativo. | ✅ Correcto. Se lanza `ValueError: El puntaje no puede ser negativo`. |
| **Prueba 6 — Entrada inválida: estado FSM incorrecto** | En la prueba unitaria se asigna `partida.estado = "VOLANDO"`. | El sistema debe lanzar un `ValueError` rechazando el estado desconocido. | ✅ Correcto. Se lanza `ValueError: Estado inválido: 'VOLANDO'`. |
| **Prueba 7 — Colisión con pared** | Se guía la serpiente directamente hacia el borde izquierdo del tablero. | Al salir del tablero, el juego pasa inmediatamente al estado GAME_OVER. | ✅ Correcto. La pantalla de Game Over aparece en el siguiente tick de movimiento. |

### Ejecución de las pruebas automatizadas

```bash
# Desde la carpeta raíz del proyecto
pytest pruebas/test_juego.py -v
```

Resultado esperado:
```
54 passed in 0.09s
```

---

## 8. Problemas y Soluciones

### Problema 1 — Game Over instantáneo al iniciar el nivel Difícil

**Descripción del error:**
Al seleccionar el nivel de dificultad 3 (Difícil), el juego mostraba la pantalla de Game Over inmediatamente después de comenzar la partida, sin que el jugador hubiera realizado ninguna acción. Era imposible jugar en ese nivel.

**Diagnóstico:**
Al revisar el código se identificó la causa: la serpiente siempre aparece en el centro del tablero, que corresponde a las celdas `(columnas//2, filas//2)`. La función que genera los obstáculos del nivel Difícil colocaba bloques precisamente en esa zona central, incluyendo una franja horizontal y una vertical que pasaban exactamente por las mismas celdas que ocupa la serpiente al nacer. En el primer frame de juego, la detección de colisiones encontraba la cabeza de la serpiente sobre un obstáculo y activaba inmediatamente el Game Over.

**Solución aplicada:**
Se corrigió en dos archivos:

Primero, en `modelos/obstaculo.py` se creó la función `_zona_segura_serpiente()` que calcula el conjunto de celdas que deben quedar libres de obstáculos alrededor del punto de aparición de la serpiente, con un margen suficiente para que el jugador tenga tiempo de reaccionar:

```python
# modelos/obstaculo.py
def _zona_segura_serpiente(columnas, filas, margen=4):
    cx = columnas // 2
    cy = filas // 2
    prohibidas = set()
    for dx in range(-margen, margen + 4):  # +4 cubre los 3 segmentos iniciales
        for dy in range(-margen, margen + 1):
            prohibidas.add((cx + dx, cy + dy))
    return prohibidas
```

Las funciones `crear_obstaculos_media()` y `crear_obstaculos_dificil()` consultan este conjunto y omiten cualquier celda que esté dentro de él.

Segundo, en `servicios/partida.py` se añadió un filtro de seguridad adicional que, después de generar los obstáculos, elimina cualquiera que coincida con las celdas ocupadas por la serpiente recién creada:

```python
# servicios/partida.py — dentro de iniciar_partida()
celdas_serpiente = set(self._serpiente.cuerpo)
self._obstaculos = [
    obs for obs in self._obstaculos
    if obs.obtener_posicion() not in celdas_serpiente
]
```

**Resultado:** el nivel Difícil ahora funciona correctamente. La serpiente aparece siempre en un área libre de obstáculos.

---

### Problema 2 — Acumulación de tiempo durante la pausa causaba movimiento brusco al reanudar

**Descripción del error:**
Al pausar el juego y dejarlo detenido durante varios segundos, al reanudar la serpiente se movía varias celdas de golpe en el primer frame. Esto rompía la fluidez del juego y podía causar colisiones inesperadas que el jugador no podía evitar.

**Diagnóstico:**
El movimiento de la serpiente se controla mediante un acumulador de tiempo: cada frame se suma el tiempo transcurrido desde el frame anterior, y cuando el acumulador supera el intervalo definido por la velocidad, la serpiente avanza una celda. El problema era que cuando el juego estaba pausado, el tiempo seguía corriendo internamente. Al reanudar, el acumulador tenía acumulados varios segundos de tiempo y la serpiente intentaba recuperar todos esos movimientos de golpe en el primer frame disponible.

**Solución aplicada:**
Se modificó el método `pausar()` en `Partida` para que, al reanudar, reinicie el contador del último frame al tiempo actual. Esto descarta el tiempo acumulado durante la pausa:

```python
# servicios/partida.py
def pausar(self):
    if self._estado == ESTADO_JUGANDO:
        self.estado = ESTADO_PAUSADO
    elif self._estado == ESTADO_PAUSADO:
        self.estado = ESTADO_JUGANDO
        # Se reinicia el contador para descartar el tiempo acumulado en pausa
        self._tiempo_ultimo_frame = time.monotonic()
        self._acumulador_tiempo = 0.0
```

**Resultado:** al reanudar la partida, la serpiente continúa su movimiento de forma suave y predecible, como si el tiempo no hubiera pasado.

---

## 9. Conclusiones

Desarrollar este proyecto fue una experiencia que va mucho más allá de aprender a programar en Python. Lo que realmente sucede cuando construyes un videojuego desde cero es que empiezas a pensar de manera diferente: ya no escribes instrucciones, sino que diseñas objetos que colaboran entre sí, cada uno con una responsabilidad clara, como piezas de un mecanismo.

El mayor aprendizaje fue entender que la Programación Orientada a Objetos no es una formalidad académica sino una herramienta práctica. Cuando nos enfrentamos al error del Game Over instantáneo en el nivel Difícil, la solución fue sencilla precisamente porque el código estaba bien organizado: sabíamos exactamente en qué archivo buscar, qué función modificar y cómo agregar la protección sin tocar nada más. En un código desordenado, ese mismo error podría haber tomado horas de búsqueda.

También aprendimos a valorar las pruebas automatizadas. Al principio parecían un trabajo extra innecesario, pero cuando realizamos cambios para corregir errores, las pruebas nos confirmaban en segundos que nada más se había roto. Esa seguridad es invaluable.

En cuanto a las dificultades, la más importante no fue técnica sino de diseño: definir correctamente las responsabilidades de cada clase antes de programar. Cuando alguna clase intentaba hacer demasiadas cosas, el código se volvía confuso y difícil de modificar. Aprender a trazar esa línea fue el reto más importante de todo el proyecto.

### Posibles mejoras

- **Guardar el récord** entre sesiones utilizando un archivo de texto o una base de datos ligera.
- **Agregar sonido**: efectos al comer, al colisionar y música de fondo.
- **Nuevos tipos de consumibles**: comida que ralentice la serpiente, ítems que otorguen puntos sin crecer, entre otros.
- **Modo desafío con tiempo límite**: una variante en la que el jugador debe alcanzar una puntuación antes de que se acabe un contador regresivo.
- **Tabla de puntuaciones**: mostrar los diez mejores puntajes históricos al final de cada partida.
- **Ventana redimensionable**: adaptar automáticamente el tamaño del tablero al tamaño de la ventana.

Estas mejoras serían perfectamente implementables sobre la arquitectura actual sin necesidad de reescribir el proyecto, lo que demuestra que un buen diseño orientado a objetos no solo resuelve el problema de hoy, sino que deja la puerta abierta para el de mañana.
