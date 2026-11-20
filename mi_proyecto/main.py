"""
Punto de entrada principal del juego Snake POO con Pygame.

Este módulo inicializa la partida y la ventana de juego, luego arranca
el bucle principal. La lógica del juego (Partida) está completamente
desacoplada del renderizado (VentanaJuego) siguiendo el principio de
separación de responsabilidades.

Uso:
    python main.py
"""

import sys

from interfaz.ventana_juego import VentanaJuego
from servicios.partida import Partida


def main() -> None:
    """
    Función principal que bootstrapea el juego.

    1. Obtiene las dimensiones del tablero desde VentanaJuego.
    2. Crea la instancia de Partida (lógica).
    3. Crea la instancia de VentanaJuego (presentación) asociándola a la Partida.
    4. Arranca el bucle principal.
    """
    # Las dimensiones del tablero en celdas las define VentanaJuego
    # para mantener la coherencia entre la cuadrícula y los píxeles
    columnas, filas = VentanaJuego.obtener_dimensiones()

    # Crear la lógica del juego
    partida = Partida(columnas=columnas, filas=filas)

    # Crear la ventana y asociarla a la partida
    ventana = VentanaJuego(partida=partida)

    # Iniciar el bucle principal
    ventana.ejecutar()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Snake] Juego interrumpido por el usuario.")
        sys.exit(0)
    except Exception as exc:
        print(f"\n[Snake] Error inesperado: {exc}")
        raise
