"""
Módulo que define la clase Obstaculo, muros internos del tablero.

Los obstáculos aparecen en dificultades Media y Difícil. Heredan de
ElementoJuego e implementan sus métodos abstractos de dibujo y posición.
"""

from __future__ import annotations

from typing import List, Tuple

import pygame

from modelos.elemento_juego import ElementoJuego

# Paleta retro Nokia
COLOR_OBSTACULO: Tuple[int, int, int] = (50, 80, 50)
COLOR_BORDE_OBSTACULO: Tuple[int, int, int] = (20, 50, 20)
COLOR_DETALLE: Tuple[int, int, int] = (80, 120, 80)

TAMANO_CELDA: int = 20


class Obstaculo(ElementoJuego):
    """
    Muro interno inamovible que provoca Game Over si la serpiente lo toca.

    Attributes:
        _x (int): Columna de la cuadrícula.
        _y (int): Fila de la cuadrícula.
        _color (Tuple[int, int, int]): Color base del obstáculo.
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Crea un obstáculo en la posición indicada.

        Args:
            x (int): Coordenada horizontal en la cuadrícula.
            y (int): Coordenada vertical en la cuadrícula.
        """
        super().__init__(x, y, COLOR_OBSTACULO)

    def obtener_posicion(self) -> Tuple[int, int]:
        """
        Retorna la posición del obstáculo como tupla (x, y).

        Returns:
            Tuple[int, int]: Coordenadas en la cuadrícula.
        """
        return (self._x, self._y)

    def dibujar(self, superficie: pygame.Surface) -> None:
        """
        Dibuja el obstáculo como un bloque con textura de ladrillos retro.

        Args:
            superficie (pygame.Surface): Superficie destino de Pygame.
        """
        rect = pygame.Rect(
            self._x * TAMANO_CELDA,
            self._y * TAMANO_CELDA,
            TAMANO_CELDA,
            TAMANO_CELDA,
        )
        # Relleno base
        pygame.draw.rect(superficie, self._color, rect)

        # Efecto de ladrillo: líneas internas
        px = self._x * TAMANO_CELDA
        py = self._y * TAMANO_CELDA
        mitad = TAMANO_CELDA // 2

        # Línea horizontal central
        pygame.draw.line(
            superficie, COLOR_DETALLE,
            (px + 1, py + mitad),
            (px + TAMANO_CELDA - 1, py + mitad),
            1,
        )
        # Línea vertical a la izquierda del bloque superior
        pygame.draw.line(
            superficie, COLOR_DETALLE,
            (px + mitad // 2, py + 1),
            (px + mitad // 2, py + mitad - 1),
            1,
        )
        # Línea vertical centrada del bloque inferior
        pygame.draw.line(
            superficie, COLOR_DETALLE,
            (px + TAMANO_CELDA - mitad // 2, py + mitad + 1),
            (px + TAMANO_CELDA - mitad // 2, py + TAMANO_CELDA - 1),
            1,
        )
        # Borde exterior
        pygame.draw.rect(superficie, COLOR_BORDE_OBSTACULO, rect, width=1)

    def __repr__(self) -> str:
        return f"Obstaculo(x={self._x}, y={self._y})"


# ---------------------------------------------------------------------------
# Fábrica de obstáculos predefinidos por dificultad
# ---------------------------------------------------------------------------

def _zona_segura_serpiente(columnas: int, filas: int, margen: int = 4) -> set:
    """
    Calcula el conjunto de celdas que deben quedar libres de obstáculos
    para que la serpiente pueda aparecer sin colisión inmediata.

    La serpiente se genera en (columnas//2, filas//2) con 3 segmentos
    moviéndose hacia la derecha, así que se protege esa área más un
    radio de seguridad para que el jugador tenga tiempo de reaccionar.

    Args:
        columnas (int): Número de columnas del tablero.
        filas (int): Número de filas del tablero.
        margen (int): Radio de celdas adicionales a proteger alrededor del spawn.

    Returns:
        set: Conjunto de tuplas (x, y) prohibidas para obstáculos.
    """
    cx = columnas // 2
    cy = filas // 2

    prohibidas: set = set()
    for dx in range(-margen, margen + 4):   # +4 cubre los 3 segmentos iniciales hacia la derecha
        for dy in range(-margen, margen + 1):
            prohibidas.add((cx + dx, cy + dy))

    return prohibidas


def crear_obstaculos_media(columnas: int, filas: int) -> List[Obstaculo]:
    """
    Genera un conjunto de obstáculos simétricos para dificultad Normal/Media.

    Args:
        columnas (int): Número de columnas del tablero.
        filas (int): Número de filas del tablero.

    Returns:
        List[Obstaculo]: Lista de obstáculos para el tablero.
    """
    obstaculos: List[Obstaculo] = []
    cx = columnas // 2
    cy = filas // 2
    prohibidas = _zona_segura_serpiente(columnas, filas, margen=3)

    # Cruz central pequeña — desplazada del centro para no tapar el spawn
    posiciones = [
        (cx - 3, cy), (cx - 2, cy), (cx - 1, cy),
        (cx + 1, cy), (cx + 2, cy), (cx + 3, cy),
        (cx, cy - 3), (cx, cy - 2), (cx, cy - 1),
        (cx, cy + 1), (cx, cy + 2), (cx, cy + 3),
    ]
    for x, y in posiciones:
        if (2 <= x < columnas - 2
                and 2 <= y < filas - 2
                and (x, y) not in prohibidas):
            obstaculos.append(Obstaculo(x, y))

    return obstaculos


def crear_obstaculos_dificil(columnas: int, filas: int) -> List[Obstaculo]:
    """
    Genera un conjunto denso de obstáculos para dificultad Difícil.

    Incluye muros en cuatro esquinas internas y franjas laterales.
    El área de spawn de la serpiente queda siempre libre.

    Args:
        columnas (int): Número de columnas del tablero.
        filas (int): Número de filas del tablero.

    Returns:
        List[Obstaculo]: Lista de obstáculos para el tablero.
    """
    prohibidas = _zona_segura_serpiente(columnas, filas, margen=4)
    obstaculos: List[Obstaculo] = []
    margen = 4

    def bloque(x0: int, y0: int, ancho: int, alto: int) -> List[Obstaculo]:
        """Crea un bloque rectangular de obstáculos respetando la zona segura."""
        blq = []
        for dx in range(ancho):
            for dy in range(alto):
                bx, by = x0 + dx, y0 + dy
                if (margen <= bx < columnas - margen
                        and margen <= by < filas - margen
                        and (bx, by) not in prohibidas):
                    blq.append(Obstaculo(bx, by))
        return blq

    # Cuatro esquinas internas (alejadas del centro)
    obstaculos.extend(bloque(margen, margen, 3, 3))
    obstaculos.extend(bloque(columnas - margen - 3, margen, 3, 3))
    obstaculos.extend(bloque(margen, filas - margen - 3, 3, 3))
    obstaculos.extend(bloque(columnas - margen - 3, filas - margen - 3, 3, 3))

    # Franjas verticales laterales (lejos del centro)
    for cy_off in range(-2, 3):
        obstaculos.extend(bloque(margen + 4, filas // 2 + cy_off, 1, 1))
        obstaculos.extend(bloque(columnas - margen - 5, filas // 2 + cy_off, 1, 1))

    # Franjas horizontales arriba y abajo del centro
    for cx_off in range(-4, 5):
        obstaculos.extend(bloque(columnas // 2 + cx_off, margen + 3, 1, 1))
        obstaculos.extend(bloque(columnas // 2 + cx_off, filas - margen - 4, 1, 1))

    # Eliminar duplicados por posición
    vistos: set = set()
    unicos: List[Obstaculo] = []
    for obs in obstaculos:
        pos = obs.obtener_posicion()
        if pos not in vistos:
            vistos.add(pos)
            unicos.append(obs)

    return unicos
