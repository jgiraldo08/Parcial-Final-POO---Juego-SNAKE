"""
Módulo que define VentanaJuego, capa de presentación del juego Snake.

VentanaJuego se asocia con Partida para leer su estado y renderizar cada frame.
No contiene lógica de juego: su única responsabilidad es capturar eventos de
entrada del usuario, delegarlos a Partida, y dibujar la interfaz retro Nokia.

Paleta retro Nokia:
  - Fondo LCD:          #9BB06A  (verde oliva claro)
  - Fondo oscuro:       #2D3B1E  (verde muy oscuro)
  - Acento primario:    #4A7C3F  (verde medio)
  - Texto principal:    #1A2410  (casi negro verdoso)
  - Texto secundario:   #6B8C52  (verde apagado)
  - Brillo HUD:         #C8DC96  (verde pálido)
"""

from __future__ import annotations

import sys
from typing import Optional, Tuple

import pygame

from servicios.partida import (
    Partida,
    ESTADO_MENU,
    ESTADO_JUGANDO,
    ESTADO_PAUSADO,
    ESTADO_GAME_OVER,
    DIFICULTADES,
)
from modelos.serpiente import ARRIBA, ABAJO, IZQUIERDA, DERECHA

# ---------------------------------------------------------------------------
# Paleta de colores retro Nokia
# ---------------------------------------------------------------------------
LCD_FONDO: Tuple[int, int, int] = (155, 176, 106)      # verde LCD claro
LCD_OSCURO: Tuple[int, int, int] = (45, 59, 30)         # fondo oscuro
LCD_MEDIO: Tuple[int, int, int] = (74, 124, 63)         # verde medio
LCD_TEXTO: Tuple[int, int, int] = (26, 36, 16)          # casi negro verdoso
LCD_TEXTO_SEC: Tuple[int, int, int] = (107, 140, 82)    # verde apagado
LCD_BRILLO: Tuple[int, int, int] = (200, 220, 150)      # verde pálido
LCD_GRID: Tuple[int, int, int] = (140, 160, 95)         # líneas de cuadrícula
COLOR_TURBO: Tuple[int, int, int] = (60, 220, 240)      # azul turbo HUD
COLOR_DORADO: Tuple[int, int, int] = (220, 180, 20)     # dorado HUD

# ---------------------------------------------------------------------------
# Dimensiones
# ---------------------------------------------------------------------------
TAMANO_CELDA: int = 20
ALTO_HUD: int = 50
ANCHO_VENTANA: int = 600
ALTO_VENTANA: int = 500
FPS: int = 60

COLUMNAS: int = ANCHO_VENTANA // TAMANO_CELDA        # 30
FILAS: int = (ALTO_VENTANA - ALTO_HUD) // TAMANO_CELDA  # 22


class VentanaJuego:
    """
    Capa de presentación y control de eventos del juego Snake.

    Recibe una instancia de Partida (asociación), captura eventos de teclado
    y llama a los métodos apropiados de Partida. Dibuja cada frame según el
    estado FSM activo.

    Attributes:
        _partida (Partida): Instancia de la lógica del juego (asociación).
        _pantalla (pygame.Surface): Superficie principal de la ventana.
        _reloj (pygame.time.Clock): Controlador de FPS.
        _fuente_grande (pygame.font.Font): Fuente para títulos.
        _fuente_media (pygame.font.Font): Fuente para HUD y textos medianos.
        _fuente_pequena (pygame.font.Font): Fuente para etiquetas pequeñas.
        _ejecutando (bool): Bandera de control del bucle principal.
    """

    def __init__(self, partida: Partida) -> None:
        """
        Inicializa Pygame y crea la ventana del juego.

        Args:
            partida (Partida): Instancia de la lógica del juego.

        Raises:
            SystemExit: Si Pygame no puede inicializarse correctamente.
        """
        self._partida: Partida = partida
        self._ejecutando: bool = True

        try:
            pygame.init()
            pygame.display.set_caption("SNAKE  —  Nokia Classic  |  POO Python")
        except pygame.error as e:
            print(f"[ERROR] No se pudo inicializar Pygame: {e}")
            sys.exit(1)

        self._pantalla: pygame.Surface = pygame.display.set_mode(
            (ANCHO_VENTANA, ALTO_VENTANA)
        )
        self._reloj: pygame.time.Clock = pygame.time.Clock()

        # Tipografía: usar fuentes del sistema con fallback seguro
        self._fuente_grande: pygame.font.Font = pygame.font.SysFont(
            "couriernew,monospace", 36, bold=True
        )
        self._fuente_media: pygame.font.Font = pygame.font.SysFont(
            "couriernew,monospace", 16, bold=False
        )
        self._fuente_pequena: pygame.font.Font = pygame.font.SysFont(
            "couriernew,monospace", 12, bold=False
        )

        # Superficie para overlays semitransparentes
        self._overlay: pygame.Surface = pygame.Surface(
            (ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA
        )

    # ------------------------------------------------------------------
    # Bucle principal
    # ------------------------------------------------------------------

    def ejecutar(self) -> None:
        """Inicia el bucle principal de renderizado y eventos."""
        while self._ejecutando:
            self._procesar_eventos()
            self._partida.actualizar()
            self._renderizar()
            self._reloj.tick(FPS)

        pygame.quit()
        sys.exit(0)

    # ------------------------------------------------------------------
    # Procesamiento de eventos de teclado
    # ------------------------------------------------------------------

    def _procesar_eventos(self) -> None:
        """Captura y delega todos los eventos de entrada del usuario."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                self._manejar_tecla(evento.key)

    def _manejar_tecla(self, tecla: int) -> None:
        """
        Gestiona la pulsación de una tecla según el estado actual de la partida.

        Args:
            tecla (int): Código de la tecla pulsada (pygame.K_*).
        """
        estado = self._partida.estado

        # --- MENU ---
        if estado == ESTADO_MENU:
            if tecla == pygame.K_1:
                self._partida.iniciar_partida(1)
            elif tecla == pygame.K_2:
                self._partida.iniciar_partida(2)
            elif tecla == pygame.K_3:
                self._partida.iniciar_partida(3)
            elif tecla == pygame.K_RETURN or tecla == pygame.K_KP_ENTER:
                self._partida.iniciar_partida(1)  # default fácil con Enter

        # --- JUGANDO ---
        elif estado == ESTADO_JUGANDO:
            # Movimiento con flechas
            if tecla in (pygame.K_UP, pygame.K_w):
                self._partida.cambiar_direccion(ARRIBA)
            elif tecla in (pygame.K_DOWN, pygame.K_s):
                self._partida.cambiar_direccion(ABAJO)
            elif tecla in (pygame.K_LEFT, pygame.K_a):
                self._partida.cambiar_direccion(IZQUIERDA)
            elif tecla in (pygame.K_RIGHT, pygame.K_d):
                self._partida.cambiar_direccion(DERECHA)
            # Pausa
            elif tecla in (pygame.K_p, pygame.K_ESCAPE):
                self._partida.pausar()

        # --- PAUSADO ---
        elif estado == ESTADO_PAUSADO:
            if tecla in (pygame.K_p, pygame.K_ESCAPE):
                self._partida.pausar()
            elif tecla == pygame.K_m:
                self._partida.ir_a_menu()

        # --- GAME OVER ---
        elif estado == ESTADO_GAME_OVER:
            if tecla in (pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER):
                self._partida.reiniciar()
            elif tecla == pygame.K_m:
                self._partida.ir_a_menu()

    # ------------------------------------------------------------------
    # Renderizado principal (despachador de estados)
    # ------------------------------------------------------------------

    def _renderizar(self) -> None:
        """Dibuja el frame actual según el estado FSM de la partida."""
        self._pantalla.fill(LCD_FONDO)

        estado = self._partida.estado

        if estado == ESTADO_MENU:
            self._dibujar_menu()
        elif estado == ESTADO_JUGANDO:
            self._dibujar_juego()
        elif estado == ESTADO_PAUSADO:
            self._dibujar_juego()
            self._dibujar_overlay_pausa()
        elif estado == ESTADO_GAME_OVER:
            self._dibujar_juego()
            self._dibujar_overlay_game_over()

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Pantalla de MENÚ
    # ------------------------------------------------------------------

    def _dibujar_menu(self) -> None:
        """Dibuja la pantalla de inicio con selección de dificultad y leyenda."""
        self._pantalla.fill(LCD_OSCURO)
        self._dibujar_cuadricula_menu()

        y = 40

        # Título principal
        titulo = self._fuente_grande.render("■ SNAKE ■", True, LCD_BRILLO)
        sub = self._fuente_media.render("Nokia Classic  //  Python POO", True, LCD_TEXTO_SEC)
        self._pantalla.blit(titulo, titulo.get_rect(centerx=ANCHO_VENTANA // 2, top=y))
        y += 48
        self._pantalla.blit(sub, sub.get_rect(centerx=ANCHO_VENTANA // 2, top=y))
        y += 36

        # Separador
        pygame.draw.line(self._pantalla, LCD_MEDIO, (60, y), (ANCHO_VENTANA - 60, y), 1)
        y += 16

        # Selección de dificultad
        titulo_dif = self._fuente_media.render("SELECCIONA DIFICULTAD:", True, LCD_BRILLO)
        self._pantalla.blit(titulo_dif, (60, y))
        y += 28

        descripciones = {
            1: ("1  →  FÁCIL",   "Sin obstáculos · Velocidad lenta",    LCD_TEXTO_SEC),
            2: ("2  →  NORMAL",  "Sin obstáculos · Velocidad media",    LCD_MEDIO),
            3: ("3  →  DIFÍCIL", "Con obstáculos · Velocidad alta",     COLOR_DORADO),
        }
        for _nivel, (etiqueta, desc, color) in descripciones.items():
            surf_et = self._fuente_media.render(etiqueta, True, LCD_BRILLO)
            surf_desc = self._fuente_pequena.render(desc, True, color)
            self._pantalla.blit(surf_et, (80, y))
            self._pantalla.blit(surf_desc, (280, y + 2))
            y += 26

        y += 10
        pygame.draw.line(self._pantalla, LCD_MEDIO, (60, y), (ANCHO_VENTANA - 60, y), 1)
        y += 16

        # Leyenda de consumibles
        leyenda_titulo = self._fuente_media.render("ÍTEMS DEL TABLERO:", True, LCD_BRILLO)
        self._pantalla.blit(leyenda_titulo, (60, y))
        y += 26

        leyenda = [
            ((100, 185, 90),  "Comida Normal  → +10 pts, +1 segmento"),
            ((255, 215, 0),   "Comida Dorada  → +30 pts, +2 seg, expira en 8s"),
            ((60, 180, 230),  "Turbo Especial → +20 pts, +1 seg, acelera 5s"),
        ]
        for color_item, texto in leyenda:
            pygame.draw.rect(self._pantalla, color_item, (80, y + 3, 14, 14), border_radius=2)
            surf = self._fuente_pequena.render(texto, True, LCD_TEXTO_SEC)
            self._pantalla.blit(surf, (102, y))
            y += 20

        y += 14

        # Instrucción de inicio
        pygame.draw.line(self._pantalla, LCD_MEDIO, (60, y), (ANCHO_VENTANA - 60, y), 1)
        y += 14
        inicio = self._fuente_media.render(
            "Pulsa  1 · 2 · 3  para iniciar  |  ENTER → Fácil", True, LCD_MEDIO
        )
        self._pantalla.blit(inicio, inicio.get_rect(centerx=ANCHO_VENTANA // 2, top=y))

        # Controles breves
        y += 26
        ctrl = self._fuente_pequena.render(
            "Movimiento: Flechas o WASD  |  Pausa: P / ESC  |  Menú: M",
            True, LCD_TEXTO_SEC,
        )
        self._pantalla.blit(ctrl, ctrl.get_rect(centerx=ANCHO_VENTANA // 2, top=y))

    def _dibujar_cuadricula_menu(self) -> None:
        """Dibuja una cuadrícula sutil de fondo para el menú."""
        for x in range(0, ANCHO_VENTANA, TAMANO_CELDA):
            pygame.draw.line(self._pantalla, (35, 48, 22), (x, 0), (x, ALTO_VENTANA), 1)
        for y in range(0, ALTO_VENTANA, TAMANO_CELDA):
            pygame.draw.line(self._pantalla, (35, 48, 22), (0, y), (ANCHO_VENTANA, y), 1)

    # ------------------------------------------------------------------
    # Pantalla de JUEGO (HUD + tablero)
    # ------------------------------------------------------------------

    def _dibujar_juego(self) -> None:
        """Dibuja el HUD superior y el tablero de juego completo."""
        self._dibujar_hud()
        self._dibujar_tablero()
        self._dibujar_elementos()

    def _dibujar_hud(self) -> None:
        """Dibuja la barra superior con puntaje, récord, dificultad y efecto."""
        # Fondo del HUD
        hud_rect = pygame.Rect(0, 0, ANCHO_VENTANA, ALTO_HUD)
        pygame.draw.rect(self._pantalla, LCD_OSCURO, hud_rect)
        pygame.draw.line(self._pantalla, LCD_MEDIO, (0, ALTO_HUD), (ANCHO_VENTANA, ALTO_HUD), 2)

        p = self._partida

        # Puntaje
        surf_pts = self._fuente_media.render(
            f"PTS {p.puntaje:05d}", True, LCD_BRILLO
        )
        self._pantalla.blit(surf_pts, (10, 8))

        # Récord
        surf_rec = self._fuente_pequena.render(
            f"REC {p.record:05d}", True, LCD_TEXTO_SEC
        )
        self._pantalla.blit(surf_rec, (10, 30))

        # Dificultad centrada
        surf_dif = self._fuente_pequena.render(
            f"[ {p.nombre_dificultad.upper()} ]", True, LCD_MEDIO
        )
        self._pantalla.blit(surf_dif, surf_dif.get_rect(centerx=ANCHO_VENTANA // 2, top=8))

        # Velocidad
        surf_vel = self._fuente_pequena.render(
            f"VEL {p.velocidad:02d}", True, LCD_TEXTO_SEC
        )
        self._pantalla.blit(surf_vel, surf_vel.get_rect(centerx=ANCHO_VENTANA // 2, top=30))

        # Longitud de serpiente
        surf_lon = self._fuente_pequena.render(
            f"LEN {p.serpiente.longitud:03d}", True, LCD_TEXTO_SEC
        )
        self._pantalla.blit(surf_lon, (ANCHO_VENTANA - 110, 30))

        # Turbo activo
        if p.turbo_activo:
            t_rest = p.tiempo_restante_turbo()
            surf_turbo = self._fuente_pequena.render(
                f"⚡TURBO {t_rest:.1f}s", True, COLOR_TURBO
            )
            self._pantalla.blit(surf_turbo, (ANCHO_VENTANA - 120, 8))
        else:
            # Último efecto (máx. 20 chars para que no desborde)
            efecto = p.ultimo_efecto[:32] if p.ultimo_efecto else ""
            if efecto:
                surf_ef = self._fuente_pequena.render(efecto, True, COLOR_DORADO)
                self._pantalla.blit(surf_ef, (ANCHO_VENTANA - 220, 8))

    def _dibujar_tablero(self) -> None:
        """Dibuja el área de juego con cuadrícula LCD sutil."""
        area = pygame.Rect(0, ALTO_HUD, ANCHO_VENTANA, ALTO_VENTANA - ALTO_HUD)
        pygame.draw.rect(self._pantalla, LCD_FONDO, area)

        # Cuadrícula sutil
        for x in range(0, ANCHO_VENTANA, TAMANO_CELDA):
            pygame.draw.line(
                self._pantalla, LCD_GRID,
                (x, ALTO_HUD), (x, ALTO_VENTANA), 1,
            )
        for y in range(ALTO_HUD, ALTO_VENTANA, TAMANO_CELDA):
            pygame.draw.line(
                self._pantalla, LCD_GRID,
                (0, y), (ANCHO_VENTANA, y), 1,
            )

        # Borde del área de juego
        pygame.draw.rect(self._pantalla, LCD_OSCURO, area, width=3)

    def _dibujar_elementos(self) -> None:
        """Dibuja la serpiente, consumibles y obstáculos en el tablero."""
        # Offset vertical del HUD aplicado vía desplazamiento de la superficie
        # Los elementos ya tienen coordenadas relativas a la cuadrícula;
        # se usa una subsuperficie para evitar sobrescribir el HUD.
        area_juego = self._pantalla.subsurface(
            pygame.Rect(0, ALTO_HUD, ANCHO_VENTANA, ALTO_VENTANA - ALTO_HUD)
        )

        # Obstáculos
        for obs in self._partida.obstaculos:
            obs.dibujar(area_juego)

        # Consumibles activos
        for consumible in self._partida.consumibles:
            if consumible.activo:
                consumible.dibujar(area_juego)

        # Serpiente
        self._partida.serpiente.dibujar(area_juego)

    # ------------------------------------------------------------------
    # Overlay de PAUSA
    # ------------------------------------------------------------------

    def _dibujar_overlay_pausa(self) -> None:
        """Dibuja un overlay semitransparente con el mensaje de pausa."""
        self._overlay.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self._overlay,
            (20, 35, 15, 180),
            pygame.Rect(100, 150, ANCHO_VENTANA - 200, 180),
            border_radius=8,
        )
        pygame.draw.rect(
            self._overlay,
            (74, 124, 63, 220),
            pygame.Rect(100, 150, ANCHO_VENTANA - 200, 180),
            width=2,
            border_radius=8,
        )
        self._pantalla.blit(self._overlay, (0, 0))

        cx = ANCHO_VENTANA // 2

        pausa_surf = self._fuente_grande.render("⏸  PAUSA", True, LCD_BRILLO)
        self._pantalla.blit(pausa_surf, pausa_surf.get_rect(centerx=cx, top=175))

        inst1 = self._fuente_media.render("P / ESC  →  Reanudar", True, LCD_TEXTO_SEC)
        inst2 = self._fuente_media.render("M        →  Menú principal", True, LCD_TEXTO_SEC)
        self._pantalla.blit(inst1, inst1.get_rect(centerx=cx, top=230))
        self._pantalla.blit(inst2, inst2.get_rect(centerx=cx, top=256))

    # ------------------------------------------------------------------
    # Overlay de GAME OVER
    # ------------------------------------------------------------------

    def _dibujar_overlay_game_over(self) -> None:
        """Dibuja el overlay de fin de partida con estadísticas finales."""
        self._overlay.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self._overlay,
            (10, 18, 7, 210),
            pygame.Rect(60, 100, ANCHO_VENTANA - 120, 280),
            border_radius=10,
        )
        pygame.draw.rect(
            self._overlay,
            (100, 160, 60, 230),
            pygame.Rect(60, 100, ANCHO_VENTANA - 120, 280),
            width=2,
            border_radius=10,
        )
        self._pantalla.blit(self._overlay, (0, 0))

        cx = ANCHO_VENTANA // 2
        stats = self._partida.estadisticas_finales()

        # Título
        titulo = self._fuente_grande.render("GAME OVER", True, LCD_BRILLO)
        self._pantalla.blit(titulo, titulo.get_rect(centerx=cx, top=120))

        # Separador
        pygame.draw.line(
            self._pantalla, LCD_MEDIO,
            (80, 168), (ANCHO_VENTANA - 80, 168), 1,
        )

        # Estadísticas
        filas_stats = [
            (f"Puntaje    {stats['puntaje']:>6}",  LCD_BRILLO),
            (f"Récord     {stats['record']:>6}",   COLOR_DORADO),
            (f"Longitud   {stats['longitud']:>6}", LCD_TEXTO_SEC),
            (f"Dificultad {stats['dificultad']:>6}", LCD_MEDIO),
            (f"Velocidad  {stats['velocidad']:>6}", LCD_TEXTO_SEC),
        ]
        y_stat = 180
        for texto, color in filas_stats:
            surf = self._fuente_media.render(texto, True, color)
            self._pantalla.blit(surf, surf.get_rect(centerx=cx, top=y_stat))
            y_stat += 22

        # Separador
        pygame.draw.line(
            self._pantalla, LCD_MEDIO,
            (80, y_stat + 4), (ANCHO_VENTANA - 80, y_stat + 4), 1,
        )

        # Instrucciones
        y_inst = y_stat + 14
        inst1 = self._fuente_media.render(
            "ENTER / R  →  Nueva partida", True, LCD_BRILLO
        )
        inst2 = self._fuente_media.render(
            "M          →  Menú principal", True, LCD_TEXTO_SEC
        )
        self._pantalla.blit(inst1, inst1.get_rect(centerx=cx, top=y_inst))
        self._pantalla.blit(inst2, inst2.get_rect(centerx=cx, top=y_inst + 24))

    # ------------------------------------------------------------------
    # Acceso a dimensiones del tablero para Partida
    # ------------------------------------------------------------------

    @staticmethod
    def obtener_dimensiones() -> Tuple[int, int]:
        """
        Retorna las dimensiones del tablero en celdas (columnas, filas).

        Returns:
            Tuple[int, int]: (columnas, filas).
        """
        return (COLUMNAS, FILAS)
