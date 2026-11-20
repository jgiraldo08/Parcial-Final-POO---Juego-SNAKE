"""
Suite de pruebas unitarias para el proyecto Snake POO.

Verifica los contratos de comportamiento de cada capa de la aplicación:
- Modelos: ElementoJuego, Consumible, Serpiente, Obstaculo
- Servicios: Partida (FSM, puntaje, velocidad, polimorfismo)

Se usa unittest estándar de Python. No requiere Pygame activo
para correr las pruebas de lógica pura.

Ejecución:
    python -m pytest pruebas/test_juego.py -v
    # o bien
    python -m unittest pruebas.test_juego -v
"""

import sys
import os
import time
import unittest
from unittest.mock import MagicMock, patch
from typing import Tuple

# Asegurar que el directorio raíz del proyecto esté en PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mockear pygame antes de importar cualquier módulo que lo use
# para poder ejecutar pruebas sin pantalla gráfica
sys.modules["pygame"] = MagicMock()
import pygame  # noqa: E402  (import después del mock)
pygame.Surface = MagicMock
pygame.Rect = MagicMock
pygame.draw = MagicMock()
pygame.font = MagicMock()

from modelos.serpiente import (  # noqa: E402
    Serpiente,
    ARRIBA, ABAJO, IZQUIERDA, DERECHA,
)
from modelos.consumible import (  # noqa: E402
    ComidaNormal, ComidaDorada, ComidaEspecial
)
from modelos.obstaculo import Obstaculo  # noqa: E402
from servicios.partida import (  # noqa: E402
    Partida,
    ESTADO_MENU, ESTADO_JUGANDO, ESTADO_PAUSADO, ESTADO_GAME_OVER,
)


# ===========================================================================
# Pruebas de Serpiente
# ===========================================================================

class TestSerpiente(unittest.TestCase):
    """Pruebas para la clase Serpiente."""

    def setUp(self) -> None:
        """Crea una serpiente centrada en (10, 10) antes de cada test."""
        self.serpiente = Serpiente(10, 10)

    # --- Inicialización ---

    def test_longitud_inicial_es_tres(self) -> None:
        """La serpiente debe inicializarse con 3 segmentos."""
        self.assertEqual(self.serpiente.longitud, 3)

    def test_cabeza_inicial_correcta(self) -> None:
        """La cabeza debe estar en la posición inicial dada."""
        self.assertEqual(self.serpiente.cabeza, (10, 10))

    def test_direccion_inicial_es_derecha(self) -> None:
        """La dirección inicial debe ser DERECHA."""
        self.assertEqual(self.serpiente.direccion, DERECHA)

    # --- Encapsulamiento: cuerpo devuelve copia ---

    def test_cuerpo_retorna_copia(self) -> None:
        """Modificar el retorno de cuerpo no debe afectar el estado interno."""
        copia = self.serpiente.cuerpo
        longitud_original = self.serpiente.longitud
        copia.append((99, 99))  # mutación externa
        self.assertEqual(self.serpiente.longitud, longitud_original)

    # --- Encapsulamiento: setter de dirección valida giro 180° ---

    def test_giro_180_derecha_a_izquierda_ignorado(self) -> None:
        """Giro de DERECHA a IZQUIERDA debe ser silenciosamente ignorado."""
        self.serpiente.direccion = DERECHA  # asegurar estado inicial
        self.serpiente.direccion = IZQUIERDA  # giro 180° prohibido
        self.assertEqual(self.serpiente.direccion, DERECHA)

    def test_giro_180_arriba_a_abajo_ignorado(self) -> None:
        """Giro de ARRIBA a ABAJO debe ser silenciosamente ignorado."""
        self.serpiente.direccion = ARRIBA
        self.serpiente.direccion = ABAJO
        self.assertEqual(self.serpiente.direccion, ARRIBA)

    def test_giro_valido_derecha_a_arriba(self) -> None:
        """Giro de DERECHA a ARRIBA es válido y debe aceptarse."""
        self.serpiente.direccion = ARRIBA
        self.assertEqual(self.serpiente.direccion, ARRIBA)

    def test_direccion_invalida_lanza_error(self) -> None:
        """Dirección fuera del conjunto válido debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            self.serpiente.direccion = (5, 5)  # vector inválido

    # --- Movimiento ---

    def test_mover_avanza_cabeza(self) -> None:
        """Después de mover, la cabeza debe desplazarse en la dirección activa."""
        cabeza_antes = self.serpiente.cabeza
        self.serpiente.mover()
        cabeza_despues = self.serpiente.cabeza
        self.assertEqual(cabeza_despues[0], cabeza_antes[0] + 1)  # DERECHA → x+1
        self.assertEqual(cabeza_despues[1], cabeza_antes[1])      # y sin cambio

    def test_mover_mantiene_longitud(self) -> None:
        """Mover sin crecer debe conservar la longitud."""
        longitud_antes = self.serpiente.longitud
        self.serpiente.mover()
        self.assertEqual(self.serpiente.longitud, longitud_antes)

    def test_crecer_aumenta_longitud_en_siguiente_movimiento(self) -> None:
        """Crecer una vez y luego mover debe aumentar la longitud en 1."""
        longitud_antes = self.serpiente.longitud
        self.serpiente.crecer()
        self.serpiente.mover()
        self.assertEqual(self.serpiente.longitud, longitud_antes + 1)

    def test_crecer_multiple(self) -> None:
        """Crecer N veces y moverse N veces aumenta la longitud en N."""
        longitud_antes = self.serpiente.longitud
        n = 4
        for _ in range(n):
            self.serpiente.crecer()
        for _ in range(n):
            self.serpiente.mover()
        self.assertEqual(self.serpiente.longitud, longitud_antes + n)

    # --- Colisiones ---

    def test_sin_colision_consigo_misma_al_inicio(self) -> None:
        """La serpiente recién creada no debe colisionar consigo misma."""
        self.assertFalse(self.serpiente.colisiona_consigo_misma())

    def test_colision_con_pared_izquierda(self) -> None:
        """La cabeza en x<0 debe detectarse como colisión con pared."""
        # La serpiente inicia en DERECHA; para ir a IZQUIERDA hay que girar
        # primero ARRIBA (giro válido) y luego IZQUIERDA (giro válido desde ARRIBA)
        s = Serpiente(2, 10)
        s.direccion = ARRIBA      # giro válido: DERECHA → ARRIBA
        s.mover()
        s.direccion = IZQUIERDA   # giro válido: ARRIBA → IZQUIERDA
        s.mover()
        s.mover()
        s.mover()  # cabeza en x = 2-3 = -1 → fuera del tablero
        self.assertTrue(s.colisiona_con_pared(20, 20))

    def test_colision_con_pared_superior(self) -> None:
        """La cabeza en y<0 debe detectarse como colisión con pared."""
        s = Serpiente(10, 0)
        s.direccion = ARRIBA
        s.mover()
        self.assertTrue(s.colisiona_con_pared(20, 20))

    def test_no_colision_en_centro(self) -> None:
        """La cabeza dentro del tablero no debe reportar colisión con pared."""
        self.assertFalse(self.serpiente.colisiona_con_pared(20, 20))

    # --- Reinicio ---

    def test_reiniciar_restaura_estado(self) -> None:
        """Reiniciar debe devolver la serpiente al estado inicial."""
        for _ in range(5):
            self.serpiente.crecer()
            self.serpiente.mover()
        self.serpiente.reiniciar(10, 10)
        self.assertEqual(self.serpiente.longitud, 3)
        self.assertEqual(self.serpiente.cabeza, (10, 10))
        self.assertEqual(self.serpiente.direccion, DERECHA)


# ===========================================================================
# Pruebas de Consumibles (jerarquía y polimorfismo)
# ===========================================================================

class TestConsumibles(unittest.TestCase):
    """Pruebas para la jerarquía de consumibles y su polimorfismo."""

    def _partida_mock(self, puntaje_inicial: int = 0) -> MagicMock:
        """Crea un mock de Partida con puntaje controlado."""
        partida = MagicMock()
        partida.puntaje = puntaje_inicial
        return partida

    def _serpiente_mock(self) -> MagicMock:
        """Crea un mock de Serpiente."""
        return MagicMock()

    # --- ComidaNormal ---

    def test_comida_normal_posicion(self) -> None:
        """ComidaNormal debe reportar su posición correctamente."""
        c = ComidaNormal(5, 7)
        self.assertEqual(c.obtener_posicion(), (5, 7))

    def test_comida_normal_efecto(self) -> None:
        """ComidaNormal aplica +10 puntos y llama crecer una vez."""
        c = ComidaNormal(5, 7)
        partida = self._partida_mock(puntaje_inicial=0)
        serpiente = self._serpiente_mock()

        mensaje = c.aplicar_efecto(serpiente, partida)

        self.assertIn("10", mensaje)
        serpiente.crecer.assert_called_once()
        self.assertFalse(c.activo)

    def test_comida_normal_no_expira(self) -> None:
        """ComidaNormal nunca debe expirar por tiempo."""
        c = ComidaNormal(1, 1)
        self.assertFalse(c.esta_expirado())

    # --- ComidaDorada ---

    def test_comida_dorada_efecto(self) -> None:
        """ComidaDorada aplica +30 puntos y llama crecer dos veces."""
        c = ComidaDorada(3, 4)
        partida = self._partida_mock()
        serpiente = self._serpiente_mock()

        mensaje = c.aplicar_efecto(serpiente, partida)

        self.assertIn("30", mensaje)
        self.assertEqual(serpiente.crecer.call_count, 2)
        self.assertFalse(c.activo)

    def test_comida_dorada_expira_por_tiempo(self) -> None:
        """ComidaDorada debe reportar expiración cuando su tiempo se agota."""
        c = ComidaDorada(2, 2)
        # Forzar que el tiempo de aparición sea muy antiguo
        c._tiempo_aparicion = time.monotonic() - 100.0
        self.assertTrue(c.esta_expirado())

    def test_comida_dorada_no_expira_recien_creada(self) -> None:
        """ComidaDorada recién creada no debe estar expirada."""
        c = ComidaDorada(2, 2)
        self.assertFalse(c.esta_expirado())

    def test_comida_dorada_tiempo_restante_positivo(self) -> None:
        """ComidaDorada recién creada debe tener tiempo restante positivo."""
        c = ComidaDorada(1, 1)
        self.assertGreater(c.tiempo_restante(), 0.0)

    # --- ComidaEspecial ---

    def test_comida_especial_efecto(self) -> None:
        """ComidaEspecial aplica +20 puntos, crece y activa turbo."""
        c = ComidaEspecial(6, 8)
        partida = self._partida_mock()
        serpiente = self._serpiente_mock()

        mensaje = c.aplicar_efecto(serpiente, partida)

        self.assertIn("20", mensaje)
        serpiente.crecer.assert_called_once()
        partida.activar_turbo.assert_called_once()
        self.assertFalse(c.activo)

    def test_comida_especial_no_expira(self) -> None:
        """ComidaEspecial no debe expirar por tiempo."""
        c = ComidaEspecial(1, 1)
        self.assertFalse(c.esta_expirado())

    # --- Polimorfismo ---

    def test_polimorfismo_aplicar_efecto(self) -> None:
        """
        La invocación polimórfica de aplicar_efecto debe funcionar
        sin ningún isinstance() o type() en el llamador.
        """
        consumibles = [
            ComidaNormal(1, 1),
            ComidaDorada(2, 2),
            ComidaEspecial(3, 3),
        ]
        partida = self._partida_mock()
        serpiente = self._serpiente_mock()

        mensajes = []
        for consumible in consumibles:
            # POLIMORFISMO PURO: sin condición de tipo
            msg = consumible.aplicar_efecto(serpiente, partida)
            mensajes.append(msg)

        # Todos deben retornar un string no vacío
        for msg in mensajes:
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0)


# ===========================================================================
# Pruebas de Obstaculo
# ===========================================================================

class TestObstaculo(unittest.TestCase):
    """Pruebas para la clase Obstaculo."""

    def test_posicion_correcta(self) -> None:
        """Obstaculo debe reportar su posición exacta."""
        obs = Obstaculo(7, 3)
        self.assertEqual(obs.obtener_posicion(), (7, 3))

    def test_color_base_definido(self) -> None:
        """Obstaculo debe tener un color base no nulo."""
        obs = Obstaculo(1, 1)
        self.assertIsNotNone(obs.color)
        self.assertEqual(len(obs.color), 3)


# ===========================================================================
# Pruebas de Partida
# ===========================================================================

class TestPartida(unittest.TestCase):
    """Pruebas para la clase Partida (lógica de juego y FSM)."""

    def setUp(self) -> None:
        """Crea una partida 20x20 antes de cada test."""
        self.partida = Partida(columnas=20, filas=20)

    # --- Estado inicial ---

    def test_estado_inicial_es_menu(self) -> None:
        """La partida debe iniciar en estado MENU."""
        self.assertEqual(self.partida.estado, ESTADO_MENU)

    def test_puntaje_inicial_es_cero(self) -> None:
        """El puntaje inicial debe ser cero."""
        self.assertEqual(self.partida.puntaje, 0)

    # --- Encapsulamiento: puntaje ---

    def test_puntaje_acepta_valor_positivo(self) -> None:
        """El setter de puntaje debe aceptar valores no negativos."""
        self.partida.puntaje = 100
        self.assertEqual(self.partida.puntaje, 100)

    def test_puntaje_no_puede_ser_negativo(self) -> None:
        """El setter de puntaje debe rechazar valores negativos con ValueError."""
        with self.assertRaises(ValueError):
            self.partida.puntaje = -1

    # --- Encapsulamiento: velocidad ---

    def test_velocidad_respeta_maximo(self) -> None:
        """El setter de velocidad no debe superar VELOCIDAD_MAXIMA."""
        self.partida.velocidad = 9999
        self.assertLessEqual(self.partida.velocidad, 25)

    def test_velocidad_respeta_minimo(self) -> None:
        """El setter de velocidad no debe bajar de VELOCIDAD_MINIMA."""
        self.partida.velocidad = 0
        self.assertGreaterEqual(self.partida.velocidad, 4)

    # --- Encapsulamiento: estado ---

    def test_estado_invalido_lanza_error(self) -> None:
        """Asignar un estado no reconocido debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            self.partida.estado = "ESTADO_INVENTADO"

    def test_estado_valido_menu(self) -> None:
        """Asignar MENU como estado debe aceptarse."""
        self.partida.estado = ESTADO_MENU
        self.assertEqual(self.partida.estado, ESTADO_MENU)

    # --- Transiciones FSM ---

    def test_iniciar_partida_cambia_estado_a_jugando(self) -> None:
        """iniciar_partida debe mover el estado a JUGANDO."""
        self.partida.iniciar_partida(1)
        self.assertEqual(self.partida.estado, ESTADO_JUGANDO)

    def test_pausar_desde_jugando_pasa_a_pausado(self) -> None:
        """pausar() en JUGANDO debe mover a PAUSADO."""
        self.partida.iniciar_partida(1)
        self.partida.pausar()
        self.assertEqual(self.partida.estado, ESTADO_PAUSADO)

    def test_pausar_desde_pausado_vuelve_a_jugando(self) -> None:
        """Segundo pausar() en PAUSADO debe volver a JUGANDO."""
        self.partida.iniciar_partida(1)
        self.partida.pausar()
        self.partida.pausar()
        self.assertEqual(self.partida.estado, ESTADO_JUGANDO)

    def test_ir_a_menu_cambia_estado(self) -> None:
        """ir_a_menu() debe mover el estado a MENU."""
        self.partida.iniciar_partida(1)
        self.partida.ir_a_menu()
        self.assertEqual(self.partida.estado, ESTADO_MENU)

    def test_dificultad_invalida_lanza_error(self) -> None:
        """iniciar_partida con dificultad fuera de rango debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            self.partida.iniciar_partida(99)

    # --- Récord de sesión ---

    def test_record_se_actualiza_al_superar_puntaje(self) -> None:
        """El récord debe actualizarse automáticamente cuando el puntaje lo supera."""
        self.partida.puntaje = 500
        self.assertEqual(self.partida.record, 500)
        self.partida.puntaje = 300  # menor, no cambia el récord
        self.assertEqual(self.partida.record, 500)

    # --- Composición: Serpiente ---

    def test_partida_crea_serpiente(self) -> None:
        """Partida debe poseer una instancia de Serpiente."""
        self.assertIsInstance(self.partida.serpiente, Serpiente)

    def test_reiniciar_crea_serpiente_nueva(self) -> None:
        """reiniciar() debe resetear la serpiente a su estado inicial."""
        self.partida.iniciar_partida(1)
        longitud_inicial = self.partida.serpiente.longitud
        # Hacer crecer la serpiente
        for _ in range(5):
            self.partida.serpiente.crecer()
            self.partida.serpiente.mover()
        self.partida.reiniciar()
        self.assertEqual(self.partida.serpiente.longitud, longitud_inicial)

    # --- Agregación: Consumibles ---

    def test_partida_tiene_consumibles_al_iniciar(self) -> None:
        """Al iniciar la partida debe haber al menos un consumible en el tablero."""
        self.partida.iniciar_partida(1)
        self.assertGreater(len(self.partida.consumibles), 0)

    def test_obstaculos_en_dificultad_dificil(self) -> None:
        """La dificultad 3 debe generar obstáculos en el tablero."""
        self.partida.iniciar_partida(3)
        self.assertGreater(len(self.partida.obstaculos), 0)

    def test_sin_obstaculos_en_dificultad_facil(self) -> None:
        """La dificultad 1 no debe generar obstáculos."""
        self.partida.iniciar_partida(1)
        self.assertEqual(len(self.partida.obstaculos), 0)

    # --- Turbo ---

    def test_activar_turbo_incrementa_velocidad(self) -> None:
        """activar_turbo debe aumentar la velocidad de la partida."""
        self.partida.iniciar_partida(1)
        vel_antes = self.partida.velocidad
        self.partida.activar_turbo(5.0, 4)
        self.assertGreater(self.partida.velocidad, vel_antes)

    def test_turbo_activo_tras_activacion(self) -> None:
        """turbo_activo debe ser True inmediatamente tras activar_turbo."""
        self.partida.iniciar_partida(1)
        self.partida.activar_turbo(5.0, 4)
        self.assertTrue(self.partida.turbo_activo)

    # --- Estadísticas finales ---

    def test_estadisticas_finales_contiene_claves(self) -> None:
        """estadisticas_finales debe retornar dict con las claves esperadas."""
        self.partida.iniciar_partida(1)
        stats = self.partida.estadisticas_finales()
        for clave in ("puntaje", "record", "longitud", "dificultad", "velocidad"):
            self.assertIn(clave, stats)

    # --- Cambio de dirección (delegación a Serpiente) ---

    def test_cambiar_direccion_solo_en_estado_jugando(self) -> None:
        """cambiar_direccion no debe tener efecto si el estado no es JUGANDO."""
        self.partida.estado = ESTADO_MENU
        dir_antes = self.partida.serpiente.direccion
        self.partida.cambiar_direccion(ARRIBA)
        self.assertEqual(self.partida.serpiente.direccion, dir_antes)


# ===========================================================================
# Pruebas de integración ligera
# ===========================================================================

class TestIntegracion(unittest.TestCase):
    """Pruebas de integración entre Serpiente, Consumibles y Partida."""

    def test_flujo_completo_consumir_comida_normal(self) -> None:
        """
        Simula que la serpiente come una ComidaNormal:
        el puntaje debe incrementarse y la serpiente crecer.
        """
        partida = Partida(columnas=20, filas=20)
        partida.iniciar_partida(1)

        puntaje_inicial = partida.puntaje
        longitud_inicial = partida.serpiente.longitud

        # Crear comida en la posición de la cabeza de la serpiente
        cabeza = partida.serpiente.cabeza
        comida = ComidaNormal(cabeza[0], cabeza[1])

        # Aplicar efecto directamente (polimorfismo)
        comida.aplicar_efecto(partida.serpiente, partida)

        self.assertGreater(partida.puntaje, puntaje_inicial)

        # crecer() encola el crecimiento; mover() lo materializa
        partida.serpiente.mover()
        self.assertGreater(partida.serpiente.longitud, longitud_inicial)

    def test_record_se_mantiene_tras_reinicio(self) -> None:
        """El récord no debe resetearse al reiniciar la partida."""
        partida = Partida(columnas=20, filas=20)
        partida.iniciar_partida(1)
        partida.puntaje = 350
        record_antes = partida.record

        partida.reiniciar()

        self.assertEqual(partida.record, record_antes)
        self.assertEqual(partida.puntaje, 0)


# ===========================================================================
# Punto de entrada para ejecución directa
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
