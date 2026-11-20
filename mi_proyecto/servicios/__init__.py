"""
Paquete servicios: lógica de negocio del juego Snake.

Contiene la clase Partida que coordina el ciclo de vida del juego.
"""

from servicios.partida import Partida, ESTADO_MENU, ESTADO_JUGANDO, ESTADO_PAUSADO, ESTADO_GAME_OVER

__all__ = [
    "Partida",
    "ESTADO_MENU",
    "ESTADO_JUGANDO",
    "ESTADO_PAUSADO",
    "ESTADO_GAME_OVER",
]
