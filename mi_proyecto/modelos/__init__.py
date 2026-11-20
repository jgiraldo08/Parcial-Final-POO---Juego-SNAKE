"""
Paquete modelos: clases del dominio del juego Snake.

Exporta las entidades principales para acceso conveniente.
"""

from modelos.elemento_juego import ElementoJuego
from modelos.consumible import Consumible, ComidaNormal, ComidaDorada, ComidaEspecial
from modelos.serpiente import Serpiente
from modelos.obstaculo import Obstaculo, crear_obstaculos_media, crear_obstaculos_dificil

__all__ = [
    "ElementoJuego",
    "Consumible",
    "ComidaNormal",
    "ComidaDorada",
    "ComidaEspecial",
    "Serpiente",
    "Obstaculo",
    "crear_obstaculos_media",
    "crear_obstaculos_dificil",
]
