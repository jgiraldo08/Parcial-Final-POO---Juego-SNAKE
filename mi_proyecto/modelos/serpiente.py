"""
Módulo que define la clase Serpiente, el avatar del jugador.

La serpiente gestiona su propio cuerpo, dirección y movimiento.
El encapsulamiento real se implementa mediante @property con validación:
- _cuerpo se expone como copia inmutable para evitar mutación externa.
- _direccion valida que no se permita un giro de 180° (auto-colisión accidental).
"""

from __future__ import annotations

from typing import Deque, List, Tuple
from collections import deque

import pygame

# Direcciones como vectores (dx, dy)
ARRIBA: Tuple[int, int] = (0, -1)
ABAJO: Tuple[int, int] = (0, 1)
IZQUIERDA: Tuple[int, int] = (-1, 0)
DERECHA: Tuple[int, int] = (1, 0)

# Pares opuestos prohibidos
OPUESTOS: dict = {
    ARRIBA: ABAJO,
    ABAJO: ARRIBA,
    IZQUIERDA: DERECHA,
    DERECHA: IZQUIERDA,
}

# Paleta retro Nokia
COLOR_CABEZA: Tuple[int, int, int] = (60, 160, 60)
COLOR_CUERPO: Tuple[int, int, int] = (90, 200, 90)
COLOR_BORDE: Tuple[int, int, int] = (30, 100, 30)
TAMANO_CELDA: int = 20


class Serpiente:
    """
    Representa la serpiente controlada por el jugador.

    Gestiona el cuerpo (deque de posiciones), la dirección de movimiento,
    el crecimiento pendiente y la lógica de colisión con el propio cuerpo.

    Attributes:
        _cuerpo (Deque[Tuple[int, int]]): Cola de posiciones (x, y) de cada segmento.
        _direccion (Tuple[int, int]): Vector de dirección actual.
        _crecimiento_pendiente (int): Segmentos que aún deben añadirse.
    """

    def __init__(self, x_inicial: int, y_inicial: int) -> None:
        """
        Crea la serpiente con 3 segmentos iniciales moviéndose hacia la derecha.

        Args:
            x_inicial (int): Columna de la cabeza en la cuadrícula.
            y_inicial (int): Fila de la cabeza en la cuadrícula.
        """
        self._cuerpo: Deque[Tuple[int, int]] = deque([
            (x_inicial, y_inicial),
            (x_inicial - 1, y_inicial),
            (x_inicial - 2, y_inicial),
        ])
        self._direccion: Tuple[int, int] = DERECHA
        self._crecimiento_pendiente: int = 0

    # ------------------------------------------------------------------
    # Propiedades con encapsulamiento y validación real
    # ------------------------------------------------------------------

    @property
    def cuerpo(self) -> List[Tuple[int, int]]:
        """
        Retorna una copia de la lista del cuerpo para evitar mutación externa directa.

        Returns:
            List[Tuple[int, int]]: Lista de posiciones (x, y) de cabeza a cola.
        """
        return list(self._cuerpo)

    @property
    def cabeza(self) -> Tuple[int, int]:
        """Retorna la posición de la cabeza de la serpiente."""
        return self._cuerpo[0]

    @property
    def direccion(self) -> Tuple[int, int]:
        """Retorna la dirección actual de movimiento."""
        return self._direccion

    @direccion.setter
    def direccion(self, nueva_direccion: Tuple[int, int]) -> None:
        """
        Establece la nueva dirección, rechazando giros de 180° para evitar
        que la serpiente colisione consigo misma en el frame siguiente.

        Args:
            nueva_direccion (Tuple[int, int]): Vector de dirección propuesto.

        Raises:
            ValueError: Si nueva_direccion es la dirección opuesta exacta a la actual.
        """
        if nueva_direccion not in (ARRIBA, ABAJO, IZQUIERDA, DERECHA):
            raise ValueError(f"Dirección inválida: {nueva_direccion}")

        if nueva_direccion == OPUESTOS.get(self._direccion):
            # Giro prohibido: ignorar silenciosamente (comportamiento esperado en juego)
            return

        self._direccion = nueva_direccion

    @property
    def longitud(self) -> int:
        """Retorna el número de segmentos actuales de la serpiente."""
        return len(self._cuerpo)

    # ------------------------------------------------------------------
    # Lógica de movimiento y crecimiento
    # ------------------------------------------------------------------

    def mover(self) -> None:
        """
        Avanza la serpiente un paso en la dirección actual.

        Si hay crecimiento pendiente, no elimina la cola (efecto de crecer).
        """
        dx, dy = self._direccion
        cabeza_x, cabeza_y = self._cuerpo[0]
        nueva_cabeza = (cabeza_x + dx, cabeza_y + dy)
        self._cuerpo.appendleft(nueva_cabeza)

        if self._crecimiento_pendiente > 0:
            self._crecimiento_pendiente -= 1
        else:
            self._cuerpo.pop()

    def crecer(self) -> None:
        """Encola un crecimiento pendiente de 1 segmento para el próximo movimiento."""
        self._crecimiento_pendiente += 1

    def colisiona_consigo_misma(self) -> bool:
        """
        Verifica si la cabeza ocupa la misma celda que algún segmento del cuerpo.

        Returns:
            bool: True si hay auto-colisión.
        """
        cabeza = self._cuerpo[0]
        # El cuerpo relevante es desde el segundo segmento en adelante
        return cabeza in list(self._cuerpo)[1:]

    def colisiona_con_pared(self, columnas: int, filas: int) -> bool:
        """
        Verifica si la cabeza salió de los límites del tablero.

        Args:
            columnas (int): Número de columnas del tablero.
            filas (int): Número de filas del tablero.

        Returns:
            bool: True si la cabeza está fuera del área de juego.
        """
        x, y = self._cuerpo[0]
        return x < 0 or x >= columnas or y < 0 or y >= filas

    def ocupa_posicion(self, pos: Tuple[int, int]) -> bool:
        """
        Comprueba si la serpiente ocupa la posición indicada.

        Args:
            pos (Tuple[int, int]): Posición (x, y) a verificar.

        Returns:
            bool: True si algún segmento ocupa esa celda.
        """
        return pos in self._cuerpo

    def reiniciar(self, x_inicial: int, y_inicial: int) -> None:
        """
        Restablece la serpiente a su estado inicial.

        Args:
            x_inicial (int): Nueva columna de la cabeza.
            y_inicial (int): Nueva fila de la cabeza.
        """
        self._cuerpo = deque([
            (x_inicial, y_inicial),
            (x_inicial - 1, y_inicial),
            (x_inicial - 2, y_inicial),
        ])
        self._direccion = DERECHA
        self._crecimiento_pendiente = 0

    # ------------------------------------------------------------------
    # Renderizado
    # ------------------------------------------------------------------

    def dibujar(self, superficie: pygame.Surface) -> None:
        """
        Dibuja todos los segmentos de la serpiente con un estilo retro Nokia.

        La cabeza se renderiza con un color más oscuro y ojos para distinguirla.

        Args:
            superficie (pygame.Surface): Superficie destino de Pygame.
        """
        cuerpo_lista = list(self._cuerpo)
        total = len(cuerpo_lista)

        for indice, (sx, sy) in enumerate(cuerpo_lista):
            rect = pygame.Rect(
                sx * TAMANO_CELDA + 1,
                sy * TAMANO_CELDA + 1,
                TAMANO_CELDA - 2,
                TAMANO_CELDA - 2,
            )

            if indice == 0:
                # Cabeza: color más oscuro con borde
                pygame.draw.rect(superficie, COLOR_CABEZA, rect, border_radius=4)
                pygame.draw.rect(superficie, COLOR_BORDE, rect, width=2, border_radius=4)
                self._dibujar_ojos(superficie, sx, sy)
            else:
                # Degradado sutil: los segmentos traseros son más claros
                factor = max(0, 1.0 - indice / max(total, 1) * 0.4)
                color_seg = (
                    int(COLOR_CUERPO[0] * factor),
                    int(COLOR_CUERPO[1] * factor),
                    int(COLOR_CUERPO[2] * factor),
                )
                pygame.draw.rect(superficie, color_seg, rect, border_radius=3)
                pygame.draw.rect(superficie, COLOR_BORDE, rect, width=1, border_radius=3)

    def _dibujar_ojos(self, superficie: pygame.Surface, sx: int, sy: int) -> None:
        """
        Dibuja los ojos de la cabeza según la dirección de movimiento.

        Args:
            superficie (pygame.Surface): Superficie destino.
            sx (int): Columna de la cabeza.
            sy (int): Fila de la cabeza.
        """
        cx = sx * TAMANO_CELDA + TAMANO_CELDA // 2
        cy = sy * TAMANO_CELDA + TAMANO_CELDA // 2
        dx, dy = self._direccion
        offset = 4

        if self._direccion == DERECHA:
            ojo1 = (cx + offset, cy - 3)
            ojo2 = (cx + offset, cy + 3)
        elif self._direccion == IZQUIERDA:
            ojo1 = (cx - offset, cy - 3)
            ojo2 = (cx - offset, cy + 3)
        elif self._direccion == ARRIBA:
            ojo1 = (cx - 3, cy - offset)
            ojo2 = (cx + 3, cy - offset)
        else:  # ABAJO
            ojo1 = (cx - 3, cy + offset)
            ojo2 = (cx + 3, cy + offset)

        pygame.draw.circle(superficie, (220, 255, 220), ojo1, 2)
        pygame.draw.circle(superficie, (220, 255, 220), ojo2, 2)

    def __repr__(self) -> str:
        return (
            f"Serpiente(longitud={self.longitud}, "
            f"cabeza={self.cabeza}, dirección={self._direccion})"
        )
