"""API de alto nível para *enviar comandos* à aeronave no MSFS 2024.

A classe :class:`MSFSController` traduz ações intuitivas ("subir o trem de
pouso", "acelerar a 80%") nos eventos SimConnect correspondentes, escondendo
os nomes técnicos dos eventos.

Exemplo::

    from msfs_control import MSFSController

    with MSFSController() as msfs:
        msfs.set_parking_brake(False)
        msfs.throttle(100)
        msfs.gear_up()
        msfs.flaps(0)
        msfs.autopilot(True)
"""

from __future__ import annotations

import logging
from typing import Optional

from .connection import SimConnection

logger = logging.getLogger(__name__)

# Faixa usada pelos eventos de eixo do SimConnect (-16383 .. +16383).
_AXIS_MAX = 16383


def _percent_to_axis(percent: float) -> int:
    """Converte 0..100 (%) para a faixa 0..16383 dos eventos de throttle."""
    percent = max(0.0, min(100.0, percent))
    return int(round(percent / 100.0 * _AXIS_MAX))


class MSFSController:
    """Fachada de comandos para a aeronave.

    Pode receber uma :class:`SimConnection` existente ou criar a sua própria.

    Parameters
    ----------
    connection:
        Conexão já aberta a reaproveitar. Se ``None``, uma nova conexão é
        criada (mas só é aberta ao entrar no ``with`` ou ao chamar
        :meth:`connect`).
    """

    def __init__(self, connection: Optional[SimConnection] = None) -> None:
        self._owns_connection = connection is None
        self._conn = connection or SimConnection(auto_connect=False)

    # ------------------------------------------------------------------ #
    # Ciclo de vida
    # ------------------------------------------------------------------ #
    def connect(self) -> "MSFSController":
        if not self._conn.connected:
            self._conn.connect()
        return self

    def close(self) -> None:
        if self._owns_connection:
            self._conn.close()

    def __enter__(self) -> "MSFSController":
        return self.connect()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @property
    def connection(self) -> SimConnection:
        """Acesso à conexão subjacente para comandos avançados."""
        return self._conn

    # ------------------------------------------------------------------ #
    # Motores / potência
    # ------------------------------------------------------------------ #
    def throttle(self, percent: float) -> None:
        """Define a potência de *todos* os motores (0 a 100%)."""
        self._conn.trigger("THROTTLE_SET", _percent_to_axis(percent))
        logger.info("Throttle ajustado para %.0f%%.", percent)

    def throttle_full(self) -> None:
        """Potência máxima (atalho para 100%)."""
        self.throttle(100)

    def throttle_idle(self) -> None:
        """Marcha lenta (atalho para 0%)."""
        self.throttle(0)

    # ------------------------------------------------------------------ #
    # Trem de pouso e freios
    # ------------------------------------------------------------------ #
    def gear_up(self) -> None:
        """Recolhe o trem de pouso."""
        self._conn.trigger("GEAR_UP")
        logger.info("Trem de pouso: recolhendo.")

    def gear_down(self) -> None:
        """Baixa o trem de pouso."""
        self._conn.trigger("GEAR_DOWN")
        logger.info("Trem de pouso: baixando.")

    def set_parking_brake(self, engaged: bool) -> None:
        """Aciona (``True``) ou libera (``False``) o freio de estacionamento."""
        # PARKING_BRAKE_SET espera 1 (acionado) ou 0 (liberado).
        self._conn.trigger("PARKING_BRAKE_SET", 1 if engaged else 0)
        logger.info("Freio de estacionamento: %s.", "acionado" if engaged else "liberado")

    def brakes(self) -> None:
        """Aplica os freios das rodas (toque único)."""
        self._conn.trigger("BRAKES")

    # ------------------------------------------------------------------ #
    # Superfícies de controle
    # ------------------------------------------------------------------ #
    def flaps(self, position: int) -> None:
        """Define a posição dos flaps por índice de detente (0 = recolhido).

        A maioria das aeronaves usa índices 0..3 ou 0..4. Índices inválidos
        são simplesmente ignorados pelo simulador.
        """
        # FLAPS_SET usa a faixa de eixo; mapeamos detentes de forma simples
        # para aeronaves comuns. Para controle fino use eventos específicos.
        mapping = {0: 0, 1: 4096, 2: 8192, 3: 12288, 4: _AXIS_MAX}
        self._conn.trigger("FLAPS_SET", mapping.get(position, 0))
        logger.info("Flaps: posição %d.", position)

    def flaps_up(self) -> None:
        """Recolhe os flaps um passo."""
        self._conn.trigger("FLAPS_UP")

    def flaps_down(self) -> None:
        """Estende os flaps um passo."""
        self._conn.trigger("FLAPS_DOWN")

    def spoilers(self, deployed: bool) -> None:
        """Estende (``True``) ou recolhe (``False``) os spoilers/aerofreios."""
        self._conn.trigger("SPOILERS_SET", 1 if deployed else 0)
        logger.info("Spoilers: %s.", "estendidos" if deployed else "recolhidos")

    # ------------------------------------------------------------------ #
    # Piloto automático
    # ------------------------------------------------------------------ #
    def autopilot(self, enabled: bool) -> None:
        """Liga (``True``) ou desliga (``False``) o piloto automático mestre.

        Usa os eventos determinísticos ``AUTOPILOT_ON``/``AUTOPILOT_OFF`` em
        vez do toggle ``AP_MASTER``, para que o estado final seja previsível
        independentemente do estado anterior.
        """
        self._conn.trigger("AUTOPILOT_ON" if enabled else "AUTOPILOT_OFF")
        logger.info("Piloto automático: %s.", "ligado" if enabled else "desligado")

    def set_heading(self, degrees: int) -> None:
        """Define o rumo (heading bug) do piloto automático em graus (0..359)."""
        degrees %= 360
        self._conn.trigger("HEADING_BUG_SET", degrees)
        logger.info("Heading do AP: %d°.", degrees)

    def set_altitude(self, feet: int) -> None:
        """Define a altitude alvo do piloto automático em pés."""
        self._conn.trigger("AP_ALT_VAR_SET_ENGLISH", int(feet))
        logger.info("Altitude alvo do AP: %d ft.", feet)

    # ------------------------------------------------------------------ #
    # Sistemas diversos
    # ------------------------------------------------------------------ #
    def landing_lights(self, on: bool) -> None:
        """Liga/desliga as luzes de pouso."""
        self._conn.trigger("LANDING_LIGHTS_SET", 1 if on else 0)

    def strobe_lights(self, on: bool) -> None:
        """Liga/desliga os strobes."""
        self._conn.trigger("STROBES_SET", 1 if on else 0)

    def pushback(self) -> None:
        """Alterna o pushback (empurrar a aeronave para trás)."""
        self._conn.trigger("TOGGLE_PUSHBACK")

    def pause(self, paused: bool) -> None:
        """Pausa (``True``) ou retoma (``False``) a simulação."""
        self._conn.trigger("PAUSE_SET", 1 if paused else 0)

    # ------------------------------------------------------------------ #
    # Comando genérico (escape hatch)
    # ------------------------------------------------------------------ #
    def send_event(self, event_name: str, value: int = 0) -> None:
        """Dispara qualquer evento SimConnect pelo nome.

        Útil para comandos não cobertos pelos helpers acima.
        """
        self._conn.trigger(event_name, value)
