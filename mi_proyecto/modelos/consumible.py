"""
Módulo que define la jerarquía de consumibles del juego Snake.

Contiene la clase abstracta Consumible y sus tres implementaciones concretas:
ComidaNormal, ComidaDorada y ComidaEspecial. El polimorfismo se ejerce a través
del método aplicar_efecto, invocado por Partida sin condicionales de tipo.
"""

from __future__ import annotations

import time
from abc import abstractmethod
from typing import TYPE_CHECKING, Tuple

import pygame

from modelos.elemento_juego import ElementoJuego

if TYPE_CHECKING:
    from modelos.serpiente import Serpiente
    from servicios.partida import Partida

# ---------------------------------------------------------------------------
# Constantes de paleta retro Nokia
# ---------------------------------------------------------------------------
COLOR_COMIDA_NORMAL: Tuple[int, int, int] = (100, 185, 90)   # verde comida
COLOR_COMIDA_DORADA: Tuple[int, int, int] = (255, 215, 0)    # dorado
COLOR_COMIDA_ESPECIAL: Tuple[int, int, int] = (60, 180, 230) # azul turbo

TAMANO_CELDA: int = 20  # píxeles por celda del tablero


# ---------------------------------------------------------------------------
# Clase abstracta intermedia
# ---------------------------------------------------------------------------

class Consumible(ElementoJuego):
    """
    Clase abstracta que representa cualquier ítem que la serpiente puede consumir.

    Hereda de ElementoJuego e impone el contrato de aplicar_efecto a todas
    las subclases concretas, permitiendo polimorfismo puro sin isinstance().

    Attributes:
        _activo (bool): Indica si el consumible sigue disponible en el tablero.
    """

    def __init__(
        self,
        x: int,
        y: int,
        color: Tuple[int, int, int],
    ) -> None:
        """
        Inicializa el consumible con posición, color y estado activo.

        Args:
            x (int): Coordenada horizontal en la cuadrícula.
            y (int): Coordenada vertical en la cuadrícula.
            color (Tuple[int, int, int]): Color RGB del consumible.
        """
        super().__init__(x, y, color)
        self._activo: bool = True

    @property
    def activo(self) -> bool:
        """Retorna True si el consumible todavía está disponible."""
        return self._activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        """Marca el consumible como consumido o expirado."""
        self._activo = valor

    def obtener_posicion(self) -> Tuple[int, int]:
        """Retorna la posición (x, y) del consumible en la cuadrícula."""
        return (self._x, self._y)

    def dibujar(self, superficie: pygame.Surface) -> None:
        """
        Dibuja el consumible como un cuadrado relleno con borde en la cuadrícula.

        Args:
            superficie (pygame.Surface): Superficie destino de Pygame.
        """
        rect = pygame.Rect(
            self._x * TAMANO_CELDA + 2,
            self._y * TAMANO_CELDA + 2,
            TAMANO_CELDA - 4,
            TAMANO_CELDA - 4,
        )
        pygame.draw.rect(superficie, self._color, rect, border_radius=3)
        # Borde interior para efecto de profundidad retro
        pygame.draw.rect(superficie, (255, 255, 255), rect, width=1, border_radius=3)

    @abstractmethod
    def aplicar_efecto(self, serpiente: "Serpiente", partida: "Partida") -> str:
        """
        Aplica el efecto del consumible sobre la serpiente y la partida.

        Args:
            serpiente (Serpiente): Instancia de la serpiente del jugador.
            partida (Partida): Instancia de la partida activa.

        Returns:
            str: Mensaje descriptivo del efecto para mostrar en el HUD.
        """
        ...

    def esta_expirado(self) -> bool:
        """
        Indica si el consumible ha expirado por tiempo. Base: nunca expira.

        Returns:
            bool: False por defecto; True en subclases con límite temporal.
        """
        return False


# ---------------------------------------------------------------------------
# ComidaNormal
# ---------------------------------------------------------------------------

class ComidaNormal(Consumible):
    """
    Consumible estándar: otorga +10 puntos y hace crecer la serpiente 1 segmento.

    Es el ítem más frecuente en el tablero. No tiene límite de tiempo.
    """

    PUNTOS: int = 10
    CRECIMIENTO: int = 1

    def __init__(self, x: int, y: int) -> None:
        """
        Crea una ComidaNormal en la posición dada.

        Args:
            x (int): Coordenada horizontal.
            y (int): Coordenada vertical.
        """
        super().__init__(x, y, COLOR_COMIDA_NORMAL)

    def aplicar_efecto(self, serpiente: "Serpiente", partida: "Partida") -> str:
        """
        Suma 10 puntos y agrega 1 segmento a la serpiente.

        Args:
            serpiente (Serpiente): Serpiente que consumió el ítem.
            partida (Partida): Partida activa donde se registra el puntaje.

        Returns:
            str: Mensaje para el HUD.
        """
        for _ in range(self.CRECIMIENTO):
            serpiente.crecer()
        partida.puntaje += self.PUNTOS
        self._activo = False
        return f"+{self.PUNTOS} pts  |  Comida normal"

    def dibujar(self, superficie: pygame.Surface) -> None:
        """Dibuja la comida normal como un cuadrado verde."""
        super().dibujar(superficie)
        # Punto brillante decorativo
        px = self._x * TAMANO_CELDA + TAMANO_CELDA // 2
        py = self._y * TAMANO_CELDA + TAMANO_CELDA // 2
        pygame.draw.circle(superficie, (200, 255, 180), (px, py), 3)


# ---------------------------------------------------------------------------
# ComidaDorada
# ---------------------------------------------------------------------------

class ComidaDorada(Consumible):
    """
    Consumible premium: +30 puntos, crece 2 segmentos, expira en 8 segundos.

    Aparece ocasionalmente y desaparece si no es recogida a tiempo.

    Attributes:
        _tiempo_aparicion (float): Marca de tiempo UNIX de cuando fue creada.
        _duracion (float): Segundos disponibles antes de expirar.
    """

    PUNTOS: int = 30
    CRECIMIENTO: int = 2
    DURACION_SEGUNDOS: float = 8.0

    def __init__(self, x: int, y: int) -> None:
        """
        Crea una ComidaDorada en la posición dada, registrando el tiempo de aparición.

        Args:
            x (int): Coordenada horizontal.
            y (int): Coordenada vertical.
        """
        super().__init__(x, y, COLOR_COMIDA_DORADA)
        self._tiempo_aparicion: float = time.monotonic()
        self._duracion: float = self.DURACION_SEGUNDOS

    def esta_expirado(self) -> bool:
        """
        Comprueba si han pasado más de DURACION_SEGUNDOS desde su aparición.

        Returns:
            bool: True si el tiempo disponible se agotó.
        """
        return (time.monotonic() - self._tiempo_aparicion) >= self._duracion

    def tiempo_restante(self) -> float:
        """
        Calcula los segundos que quedan antes de expirar.

        Returns:
            float: Segundos restantes (mínimo 0.0).
        """
        restante = self._duracion - (time.monotonic() - self._tiempo_aparicion)
        return max(0.0, restante)

    def aplicar_efecto(self, serpiente: "Serpiente", partida: "Partida") -> str:
        """
        Suma 30 puntos y agrega 2 segmentos a la serpiente.

        Args:
            serpiente (Serpiente): Serpiente que consumió el ítem.
            partida (Partida): Partida activa.

        Returns:
            str: Mensaje para el HUD.
        """
        for _ in range(self.CRECIMIENTO):
            serpiente.crecer()
        partida.puntaje += self.PUNTOS
        self._activo = False
        return f"+{self.PUNTOS} pts  |  ¡Comida dorada!"

    def dibujar(self, superficie: pygame.Surface) -> None:
        """Dibuja la comida dorada con animación de parpadeo al final de su vida."""
        # Parpadear en los últimos 2 segundos
        if self.tiempo_restante() < 2.0:
            if int(time.monotonic() * 4) % 2 == 0:
                return  # parpadeo: no dibujar en este frame
        super().dibujar(superficie)
        # Estrella pequeña en el centro
        cx = self._x * TAMANO_CELDA + TAMANO_CELDA // 2
        cy = self._y * TAMANO_CELDA + TAMANO_CELDA // 2
        pygame.draw.circle(superficie, (255, 255, 200), (cx, cy), 4)
        pygame.draw.circle(superficie, (200, 160, 0), (cx, cy), 2)


# ---------------------------------------------------------------------------
# ComidaEspecial (Turbo / Bonus)
# ---------------------------------------------------------------------------

class ComidaEspecial(Consumible):
    """
    Consumible turbo: +20 puntos, crece 1 segmento y aumenta la velocidad temporalmente.

    La aceleración dura DURACION_TURBO segundos; Partida gestiona el contador.

    Attributes:
        _duracion_turbo (float): Segundos que dura el efecto de velocidad.
        _incremento_velocidad (int): Celdas/s adicionales durante el turbo.
    """

    PUNTOS: int = 20
    CRECIMIENTO: int = 1
    DURACION_TURBO: float = 5.0
    INCREMENTO_VELOCIDAD: int = 4

    def __init__(self, x: int, y: int) -> None:
        """
        Crea una ComidaEspecial en la posición dada.

        Args:
            x (int): Coordenada horizontal.
            y (int): Coordenada vertical.
        """
        super().__init__(x, y, COLOR_COMIDA_ESPECIAL)
        self._duracion_turbo: float = self.DURACION_TURBO
        self._incremento_velocidad: int = self.INCREMENTO_VELOCIDAD

    @property
    def duracion_turbo(self) -> float:
        """Retorna la duración en segundos del efecto turbo."""
        return self._duracion_turbo

    @property
    def incremento_velocidad(self) -> int:
        """Retorna el incremento de velocidad que concede el turbo."""
        return self._incremento_velocidad

    def aplicar_efecto(self, serpiente: "Serpiente", partida: "Partida") -> str:
        """
        Suma 20 puntos, agrega 1 segmento y activa el turbo de velocidad en Partida.

        Args:
            serpiente (Serpiente): Serpiente que consumió el ítem.
            partida (Partida): Partida activa que gestiona el turbo.

        Returns:
            str: Mensaje para el HUD.
        """
        serpiente.crecer()
        partida.puntaje += self.PUNTOS
        partida.activar_turbo(self._duracion_turbo, self._incremento_velocidad)
        self._activo = False
        return f"+{self.PUNTOS} pts  |  ¡TURBO activado {self._duracion_turbo:.0f}s!"

    def dibujar(self, superficie: pygame.Surface) -> None:
        """Dibuja la comida especial con un efecto de brillo pulsante."""
        super().dibujar(superficie)
        # Rayo central decorativo
        cx = self._x * TAMANO_CELDA + TAMANO_CELDA // 2
        cy = self._y * TAMANO_CELDA + TAMANO_CELDA // 2
        offset = 4
        pygame.draw.line(
            superficie, (255, 255, 255),
            (cx - offset, cy - offset),
            (cx + offset, cy + offset),
            2,
        )
        pygame.draw.line(
            superficie, (255, 255, 255),
            (cx + offset, cy - offset),
            (cx - offset, cy + offset),
            2,
        )
