"""msfs_control — controle do Microsoft Flight Simulator 2024 via SimConnect.

Pacote focado em *enviar comandos* e *automatizar rotinas* na aeronave.

Uso rápido::

    from msfs_control import MSFSController

    with MSFSController() as msfs:
        msfs.set_parking_brake(False)
        msfs.throttle(80)
        msfs.gear_up()

Os módulos principais são:

* :mod:`msfs_control.connection` — conexão de baixo nível com o simulador.
* :mod:`msfs_control.controller` — API de alto nível para enviar comandos.
* :mod:`msfs_control.automation` — framework para sequências automatizadas.
"""

from .connection import SimConnection, SimConnectionError
from .controller import MSFSController
from .automation import Sequence, Step, wait_until
from .telemetry import Telemetry, TelemetryReader

__all__ = [
    "SimConnection",
    "SimConnectionError",
    "MSFSController",
    "Sequence",
    "Step",
    "wait_until",
    "Telemetry",
    "TelemetryReader",
]

__version__ = "0.1.0"
