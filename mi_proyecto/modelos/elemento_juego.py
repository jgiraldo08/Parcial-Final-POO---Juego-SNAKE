"""
Módulo que define la clase abstracta base ElementoJuego.

Todos los objetos visibles en el tablero de juego heredan de esta clase,
garantizando una interfaz uniforme para dibujar y obtener posición.
"""

from abc import ABC, abstractmethod
from typing import Tuple
import pygame


class ElementoJuego(ABC):
    """
    Clase abstracta base para todos los elementos que aparecen en el tablero.

    Encapsula las coordenadas del elemento y su color, y declara los contratos
    de comportamiento que cada subclase concreta debe implementar.

    Attributes:
        _x (int): Coordenada horizontal en unidades de celda del tablero.
        _y (int): Coordenada vertical en unidades de celda del tablero.
        _color (Tuple[int, int, int]): Color RGB del elemento.
    """

    def __init__(
        self,
        x: int,
        y: int,
        color: Tuple[int, int, int],
    ) -> None:
        """
        Inicializa las coordenadas y el color del elemento.

        Args:
            x (int): Posición horizontal en la cuadrícula.
            y (int): Posición vertical en la cuadrícula.
            color (Tuple[int, int, int]): Tupla RGB que define el color.
        """
        self._x: int = x
        self._y: int = y
        self._color: Tuple[int, int, int] = color

    # ------------------------------------------------------------------
    # Propiedades de acceso controlado
    # ------------------------------------------------------------------

    @property
    def x(self) -> int:
        """Retorna la coordenada horizontal del elemento."""
        return self._x

    @x.setter
    def x(self, valor: int) -> None:
        """Establece la coordenada horizontal del elemento."""
        self._x = valor

    @property
    def y(self) -> int:
        """Retorna la coordenada vertical del elemento."""
        return self._y

    @y.setter
    def y(self, valor: int) -> None:
        """Establece la coordenada vertical del elemento."""
        self._y = valor

    @property
    def color(self) -> Tuple[int, int, int]:
        """Retorna el color RGB del elemento."""
        return self._color

    @color.setter
    def color(self, nuevo_color: Tuple[int, int, int]) -> None:
        """Establece el color RGB del elemento."""
        self._color = nuevo_color

    # ------------------------------------------------------------------
    # Métodos abstractos obligatorios
    # ------------------------------------------------------------------

    @abstractmethod
    def dibujar(self, superficie: pygame.Surface) -> None:
        """
        Dibuja el elemento sobre la superficie de Pygame.

        Args:
            superficie (pygame.Surface): Superficie donde se renderiza el elemento.
        """
        ...

    @abstractmethod
    def obtener_posicion(self) -> Tuple[int, int]:
        """
        Retorna la posición actual del elemento como tupla (x, y).

        Returns:
            Tuple[int, int]: Coordenadas (x, y) en la cuadrícula.
        """
        ...

    def __repr__(self) -> str:
        """Representación legible del elemento para depuración."""
        return (
            f"{self.__class__.__name__}("
            f"x={self._x}, y={self._y}, color={self._color})"
        )
