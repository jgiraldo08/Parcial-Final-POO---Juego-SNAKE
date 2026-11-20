"""
Módulo que define la clase Partida, corazón de la lógica del juego.

Partida coordina todos los elementos del juego: posee la Serpiente (composición),
gestiona las colecciones de Consumibles y Obstáculos (agregación), controla el estado
de la máquina de estados FSM y delega el renderizado a VentanaJuego (asociación).

El polimorfismo se ejerce aquí al invocar consumible.aplicar_efecto() sin
ningún isinstance() o type() que condicione el comportamiento.
"""

from __future__ import annotations

import random
import time
from typing import List, Optional, Tuple

from modelos.serpiente import Serpiente
from modelos.consumible import (
    Consumible,
    ComidaNormal,
    ComidaDorada,
    ComidaEspecial,
)
from modelos.obstaculo import (
    Obstaculo,
    crear_obstaculos_media,
    crear_obstaculos_dificil,
)

# ---------------------------------------------------------------------------
# Enumeración de estados de la partida
# ---------------------------------------------------------------------------

ESTADO_MENU: str = "MENU"
ESTADO_JUGANDO: str = "JUGANDO"
ESTADO_PAUSADO: str = "PAUSADO"
ESTADO_GAME_OVER: str = "GAME_OVER"

ESTADOS_VALIDOS: Tuple[str, ...] = (
    ESTADO_MENU,
    ESTADO_JUGANDO,
    ESTADO_PAUSADO,
    ESTADO_GAME_OVER,
)

# ---------------------------------------------------------------------------
# Configuraciones de dificultad
# ---------------------------------------------------------------------------

DIFICULTADES: dict = {
    1: {"nombre": "Fácil",   "velocidad": 6,  "obstaculos": False},
    2: {"nombre": "Normal",  "velocidad": 10, "obstaculos": False},
    3: {"nombre": "Difícil", "velocidad": 15, "obstaculos": True},
}

VELOCIDAD_MINIMA: int = 4
VELOCIDAD_MAXIMA: int = 25

# Probabilidades de aparición (porcentaje sobre 100)
PROB_DORADA: int = 15      # 15 % de que el nuevo consumible sea dorado
PROB_ESPECIAL: int = 10    # 10 % de que sea especial (turbo)

MAX_INTENTOS_POSICION: int = 500  # límite para evitar bucles infinitos


class Partida:
    """
    Gestiona el estado completo de una partida de Snake.

    Responsabilidades:
    - Crear y destruir la Serpiente (composición).
    - Administrar listas de Consumibles y Obstáculos (agregación).
    - Actualizar la física del juego frame a frame.
    - Detectar colisiones y transitar entre estados.
    - Exponer el estado serializable para que VentanaJuego lo renderice.

    Attributes:
        _columnas (int): Número de columnas del tablero.
        _filas (int): Número de filas del tablero.
        _dificultad (int): Nivel de dificultad (1, 2 o 3).
        _estado (str): Estado actual de la máquina FSM.
        _puntaje (int): Puntaje acumulado en la partida actual.
        _record (int): Mayor puntaje alcanzado en la sesión.
        _velocidad (int): Movimientos por segundo de la serpiente.
        _serpiente (Serpiente): Instancia activa de la serpiente.
        _consumibles (List[Consumible]): Colección de ítems en el tablero.
        _obstaculos (List[Obstaculo]): Colección de muros en el tablero.
        _ultimo_efecto (str): Último mensaje de efecto para el HUD.
        _tiempo_ultimo_efecto (float): Timestamp del último efecto recibido.
        _turbo_activo (bool): Si hay un turbo de velocidad en curso.
        _turbo_fin (float): Timestamp en que termina el turbo.
        _velocidad_base (int): Velocidad sin turbo para restaurar al finalizar.
        _acumulador_tiempo (float): Acumula el tiempo transcurrido para mover.
        _tiempo_ultimo_frame (float): Timestamp del último frame procesado.
    """

    def __init__(self, columnas: int, filas: int) -> None:
        """
        Inicializa la partida en estado MENU con tablero de tamaño dado.

        Args:
            columnas (int): Número de columnas del tablero de juego.
            filas (int): Número de filas del tablero de juego.
        """
        self._columnas: int = columnas
        self._filas: int = filas
        self._dificultad: int = 1
        self._estado: str = ESTADO_MENU
        self._puntaje: int = 0
        self._record: int = 0
        self._velocidad: int = DIFICULTADES[1]["velocidad"]
        self._velocidad_base: int = self._velocidad

        # Composición: Partida crea y posee la serpiente
        self._serpiente: Serpiente = self._crear_serpiente()

        # Agregación: colecciones de consumibles y obstáculos
        self._consumibles: List[Consumible] = []
        self._obstaculos: List[Obstaculo] = []

        # HUD
        self._ultimo_efecto: str = ""
        self._tiempo_ultimo_efecto: float = 0.0

        # Turbo
        self._turbo_activo: bool = False
        self._turbo_fin: float = 0.0

        # Control de tiempo para movimiento basado en velocidad
        self._acumulador_tiempo: float = 0.0
        self._tiempo_ultimo_frame: float = time.monotonic()

    # ------------------------------------------------------------------
    # Propiedades con validación (encapsulamiento real)
    # ------------------------------------------------------------------

    @property
    def puntaje(self) -> int:
        """Retorna el puntaje actual de la partida."""
        return self._puntaje

    @puntaje.setter
    def puntaje(self, valor: int) -> None:
        """
        Establece el puntaje; no permite valores negativos.

        Args:
            valor (int): Nuevo puntaje.

        Raises:
            ValueError: Si el valor es negativo.
        """
        if valor < 0:
            raise ValueError(f"El puntaje no puede ser negativo. Valor recibido: {valor}")
        self._puntaje = valor
        if self._puntaje > self._record:
            self._record = self._puntaje

    @property
    def record(self) -> int:
        """Retorna el récord de la sesión."""
        return self._record

    @property
    def velocidad(self) -> int:
        """Retorna la velocidad actual en movimientos por segundo."""
        return self._velocidad

    @velocidad.setter
    def velocidad(self, valor: int) -> None:
        """
        Establece la velocidad dentro de los límites permitidos.

        Args:
            valor (int): Velocidad propuesta en movimientos/segundo.
        """
        self._velocidad = max(VELOCIDAD_MINIMA, min(VELOCIDAD_MAXIMA, valor))

    @property
    def estado(self) -> str:
        """Retorna el estado FSM actual de la partida."""
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado: str) -> None:
        """
        Transita a un nuevo estado FSM.

        Args:
            nuevo_estado (str): Estado destino.

        Raises:
            ValueError: Si el estado no pertenece a ESTADOS_VALIDOS.
        """
        if nuevo_estado not in ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado inválido: '{nuevo_estado}'. "
                f"Válidos: {ESTADOS_VALIDOS}"
            )
        self._estado = nuevo_estado

    @property
    def serpiente(self) -> Serpiente:
        """Retorna la instancia de la serpiente activa."""
        return self._serpiente

    @property
    def consumibles(self) -> List[Consumible]:
        """Retorna la lista de consumibles activos en el tablero."""
        return self._consumibles

    @property
    def obstaculos(self) -> List[Obstaculo]:
        """Retorna la lista de obstáculos del tablero."""
        return self._obstaculos

    @property
    def columnas(self) -> int:
        """Retorna el número de columnas del tablero."""
        return self._columnas

    @property
    def filas(self) -> int:
        """Retorna el número de filas del tablero."""
        return self._filas

    @property
    def dificultad(self) -> int:
        """Retorna el nivel de dificultad activo (1=Fácil, 2=Normal, 3=Difícil)."""
        return self._dificultad

    @property
    def nombre_dificultad(self) -> str:
        """Retorna el nombre textual de la dificultad activa."""
        return DIFICULTADES[self._dificultad]["nombre"]

    @property
    def ultimo_efecto(self) -> str:
        """Retorna el mensaje del último efecto consumido para el HUD."""
        return self._ultimo_efecto

    @property
    def turbo_activo(self) -> bool:
        """Retorna True si el turbo de velocidad está en curso."""
        return self._turbo_activo

    # ------------------------------------------------------------------
    # Inicialización y reinicio de partida
    # ------------------------------------------------------------------

    def iniciar_partida(self, dificultad: int) -> None:
        """
        Arranca una nueva partida con la dificultad seleccionada.

        Args:
            dificultad (int): Nivel de dificultad (1, 2 o 3).
        """
        if dificultad not in DIFICULTADES:
            raise ValueError(f"Dificultad inválida: {dificultad}. Use 1, 2 o 3.")

        self._dificultad = dificultad
        cfg = DIFICULTADES[dificultad]
        self._velocidad_base = cfg["velocidad"]
        self._velocidad = self._velocidad_base
        self._puntaje = 0

        # Reiniciar serpiente (composición)
        self._serpiente = self._crear_serpiente()

        # Cargar obstáculos según dificultad (agregación)
        self._obstaculos = []
        if cfg["obstaculos"]:
            if dificultad == 2:
                self._obstaculos = crear_obstaculos_media(self._columnas, self._filas)
            else:
                self._obstaculos = crear_obstaculos_dificil(self._columnas, self._filas)

        # Capa de seguridad: eliminar cualquier obstáculo que coincida
        # con una celda ocupada por la serpiente recién creada.
        # Esto garantiza que nunca haya Game Over instantáneo al iniciar.
        celdas_serpiente = set(self._serpiente.cuerpo)
        self._obstaculos = [
            obs for obs in self._obstaculos
            if obs.obtener_posicion() not in celdas_serpiente
        ]

        # Reiniciar consumibles y agregar el primero
        self._consumibles = []
        self._agregar_consumible_aleatorio()

        # Reiniciar HUD y turbo
        self._ultimo_efecto = "¡Suerte!"
        self._tiempo_ultimo_efecto = time.monotonic()
        self._turbo_activo = False
        self._turbo_fin = 0.0

        # Control de tiempo
        self._acumulador_tiempo = 0.0
        self._tiempo_ultimo_frame = time.monotonic()

        self.estado = ESTADO_JUGANDO

    def reiniciar(self) -> None:
        """Reinicia la partida con la misma dificultad anterior."""
        self.iniciar_partida(self._dificultad)

    # ------------------------------------------------------------------
    # Bucle de actualización principal
    # ------------------------------------------------------------------

    def actualizar(self) -> None:
        """
        Procesa un tick de lógica de juego.

        Debe llamarse cada frame desde VentanaJuego. Internamente acumula
        el tiempo transcurrido y solo mueve la serpiente cuando ha pasado
        1/velocidad segundos, desacoplando la velocidad del juego de la
        tasa de frames del renderizador.
        """
        if self._estado != ESTADO_JUGANDO:
            return

        ahora = time.monotonic()
        delta = ahora - self._tiempo_ultimo_frame
        self._tiempo_ultimo_frame = ahora
        self._acumulador_tiempo += delta

        intervalo = 1.0 / self._velocidad

        if self._acumulador_tiempo >= intervalo:
            self._acumulador_tiempo -= intervalo
            self._mover_y_verificar()

        # Gestionar expiración de turbo
        if self._turbo_activo and ahora >= self._turbo_fin:
            self._desactivar_turbo()

        # Limpiar consumibles expirados y consumidos
        self._limpiar_consumibles()

        # Asegurar al menos un consumible en el tablero
        consumibles_activos = [c for c in self._consumibles if c.activo]
        if not consumibles_activos:
            self._agregar_consumible_aleatorio()

        # Expirar mensaje HUD después de 3 segundos
        if ahora - self._tiempo_ultimo_efecto > 3.0:
            self._ultimo_efecto = ""

    # ------------------------------------------------------------------
    # Lógica de movimiento y colisiones
    # ------------------------------------------------------------------

    def _mover_y_verificar(self) -> None:
        """Mueve la serpiente y ejecuta todas las verificaciones de colisión."""
        self._serpiente.mover()

        if self._serpiente.colisiona_con_pared(self._columnas, self._filas):
            self._fin_partida()
            return

        if self._serpiente.colisiona_consigo_misma():
            self._fin_partida()
            return

        if self._colisiona_con_obstaculos():
            self._fin_partida()
            return

        self._verificar_consumo()

    def _colisiona_con_obstaculos(self) -> bool:
        """
        Comprueba si la cabeza de la serpiente toca algún obstáculo.

        Returns:
            bool: True si hay colisión con obstáculo.
        """
        cabeza = self._serpiente.cabeza
        return any(obs.obtener_posicion() == cabeza for obs in self._obstaculos)

    def _verificar_consumo(self) -> None:
        """
        Detecta si la cabeza toca un consumible y ejecuta su efecto.

        El polimorfismo se ejerce aquí: aplicar_efecto() se llama directamente
        sobre cada Consumible sin ningún isinstance() o type().
        """
        cabeza = self._serpiente.cabeza
        for consumible in self._consumibles:
            if consumible.activo and consumible.obtener_posicion() == cabeza:
                # POLIMORFISMO PURO: sin isinstance ni type
                mensaje = consumible.aplicar_efecto(self._serpiente, self)
                self._ultimo_efecto = mensaje
                self._tiempo_ultimo_efecto = time.monotonic()
                # Generar nuevo consumible después de consumir
                self._agregar_consumible_aleatorio()
                break

    # ------------------------------------------------------------------
    # Gestión de consumibles
    # ------------------------------------------------------------------

    def _agregar_consumible_aleatorio(self) -> None:
        """
        Genera un consumible en una posición libre del tablero.

        El tipo se selecciona aleatoriamente según probabilidades definidas.
        Tiene un límite de intentos para prevenir bucles infinitos en tableros llenos.
        """
        posicion = self._posicion_libre_aleatoria()
        if posicion is None:
            return  # tablero lleno; no agregar

        x, y = posicion
        tirada = random.randint(1, 100)

        if tirada <= PROB_ESPECIAL:
            nuevo = ComidaEspecial(x, y)
        elif tirada <= PROB_ESPECIAL + PROB_DORADA:
            nuevo = ComidaDorada(x, y)
        else:
            nuevo = ComidaNormal(x, y)

        self._consumibles.append(nuevo)

    def _posicion_libre_aleatoria(self) -> Optional[Tuple[int, int]]:
        """
        Encuentra una celda vacía en el tablero por muestreo aleatorio.

        Evita posiciones ocupadas por la serpiente, obstáculos y consumibles activos.

        Returns:
            Optional[Tuple[int, int]]: Posición libre o None si no hay espacio.
        """
        ocupadas: set = set(self._serpiente.cuerpo)
        ocupadas.update(obs.obtener_posicion() for obs in self._obstaculos)
        ocupadas.update(
            c.obtener_posicion() for c in self._consumibles if c.activo
        )

        total_celdas = self._columnas * self._filas
        if len(ocupadas) >= total_celdas:
            return None  # tablero completamente lleno

        for _ in range(MAX_INTENTOS_POSICION):
            x = random.randint(0, self._columnas - 1)
            y = random.randint(0, self._filas - 1)
            if (x, y) not in ocupadas:
                return (x, y)

        # Fallback determinístico: recorrer todas las celdas
        for x in range(self._columnas):
            for y in range(self._filas):
                if (x, y) not in ocupadas:
                    return (x, y)

        return None

    def _limpiar_consumibles(self) -> None:
        """Elimina consumibles que fueron consumidos o que han expirado."""
        self._consumibles = [
            c for c in self._consumibles
            if c.activo and not c.esta_expirado()
        ]

    # ------------------------------------------------------------------
    # Turbo de velocidad
    # ------------------------------------------------------------------

    def activar_turbo(self, duracion: float, incremento: int) -> None:
        """
        Activa el efecto turbo de velocidad durante un tiempo determinado.

        Args:
            duracion (float): Segundos que dura el turbo.
            incremento (int): Unidades adicionales de velocidad.
        """
        self._turbo_activo = True
        self._turbo_fin = time.monotonic() + duracion
        self.velocidad = self._velocidad_base + incremento

    def _desactivar_turbo(self) -> None:
        """Restaura la velocidad base al finalizar el turbo."""
        self._turbo_activo = False
        self.velocidad = self._velocidad_base

    def tiempo_restante_turbo(self) -> float:
        """
        Calcula los segundos restantes del turbo activo.

        Returns:
            float: Segundos restantes (0.0 si el turbo no está activo).
        """
        if not self._turbo_activo:
            return 0.0
        return max(0.0, self._turbo_fin - time.monotonic())

    # ------------------------------------------------------------------
    # Control de estado FSM
    # ------------------------------------------------------------------

    def pausar(self) -> None:
        """Alterna entre JUGANDO y PAUSADO."""
        if self._estado == ESTADO_JUGANDO:
            self.estado = ESTADO_PAUSADO
            # Resetear el acumulador para no acumular tiempo pausado
            self._tiempo_ultimo_frame = time.monotonic()
        elif self._estado == ESTADO_PAUSADO:
            self.estado = ESTADO_JUGANDO
            self._tiempo_ultimo_frame = time.monotonic()

    def _fin_partida(self) -> None:
        """Transita al estado GAME_OVER."""
        self.estado = ESTADO_GAME_OVER

    def ir_a_menu(self) -> None:
        """Transita al estado MENU."""
        self.estado = ESTADO_MENU

    # ------------------------------------------------------------------
    # Cambio de dirección (delegado a Serpiente con validación)
    # ------------------------------------------------------------------

    def cambiar_direccion(self, nueva_direccion: Tuple[int, int]) -> None:
        """
        Propaga el cambio de dirección a la serpiente.

        La validación del giro de 180° se realiza en el setter de Serpiente.

        Args:
            nueva_direccion (Tuple[int, int]): Vector de dirección propuesto.
        """
        if self._estado == ESTADO_JUGANDO:
            self._serpiente.direccion = nueva_direccion

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _crear_serpiente(self) -> Serpiente:
        """
        Crea una serpiente centrada en el tablero.

        Returns:
            Serpiente: Nueva instancia lista para jugar.
        """
        x_inicial = self._columnas // 2
        y_inicial = self._filas // 2
        return Serpiente(x_inicial, y_inicial)

    def estadisticas_finales(self) -> dict:
        """
        Retorna un dict con las estadísticas de la partida terminada.

        Returns:
            dict: Puntaje, récord, longitud, dificultad y velocidad final.
        """
        return {
            "puntaje": self._puntaje,
            "record": self._record,
            "longitud": self._serpiente.longitud,
            "dificultad": self.nombre_dificultad,
            "velocidad": self._velocidad,
        }

    def __repr__(self) -> str:
        return (
            f"Partida(estado={self._estado}, puntaje={self._puntaje}, "
            f"velocidad={self._velocidad}, dificultad={self.nombre_dificultad})"
        )
