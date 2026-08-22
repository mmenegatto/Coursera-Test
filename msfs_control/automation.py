"""Framework simples de automação para o MSFS 2024.

Permite descrever *rotinas* (checklists, decolagem, pouso...) como uma
sequência de passos. Cada passo é uma função que recebe o
:class:`~msfs_control.controller.MSFSController`. Entre passos é possível
esperar um tempo fixo ou esperar até que uma condição de SimVar seja
satisfeita.

Exemplo::

    from msfs_control import MSFSController, Sequence, Step, wait_until

    seq = Sequence("Decolagem", [
        Step("Liberar freio", lambda m: m.set_parking_brake(False)),
        Step("Potência total", lambda m: m.throttle_full()),
        Step("Aguardar rotação",
             lambda m: wait_until(m, "AIRSPEED_INDICATED", lambda v: v >= 130)),
        Step("Recolher trem", lambda m: m.gear_up()),
    ])

    with MSFSController() as msfs:
        seq.run(msfs)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, List, Sequence as _Seq

from .connection import SimConnectionError
from .controller import MSFSController

logger = logging.getLogger(__name__)

# Tipo de uma ação de passo: recebe o controlador, não retorna nada.
StepAction = Callable[[MSFSController], None]


class AutomationError(RuntimeError):
    """Erro durante a execução de uma sequência de automação."""


@dataclass
class Step:
    """Um passo nomeado de uma sequência.

    Parameters
    ----------
    name:
        Descrição legível do passo (aparece nos logs).
    action:
        Função que executa o passo, recebendo o controlador.
    delay_after:
        Segundos a aguardar *depois* de executar a ação (padrão 0).
    """

    name: str
    action: StepAction
    delay_after: float = 0.0


class Sequence:
    """Uma rotina automatizada composta por vários :class:`Step`."""

    def __init__(self, name: str, steps: _Seq[Step]) -> None:
        self.name = name
        self.steps: List[Step] = list(steps)

    def run(self, controller: MSFSController, *, stop_on_error: bool = True) -> None:
        """Executa todos os passos em ordem.

        Parameters
        ----------
        controller:
            Controlador conectado ao simulador.
        stop_on_error:
            Se ``True`` (padrão), interrompe na primeira falha. Se ``False``,
            registra o erro e segue para o próximo passo.
        """
        logger.info("=== Iniciando sequência: %s (%d passos) ===",
                    self.name, len(self.steps))
        for i, step in enumerate(self.steps, start=1):
            logger.info("[%d/%d] %s", i, len(self.steps), step.name)
            try:
                step.action(controller)
            except (SimConnectionError, AutomationError) as exc:
                logger.error("Falha no passo '%s': %s", step.name, exc)
                if stop_on_error:
                    raise AutomationError(
                        f"Sequência '{self.name}' interrompida no passo "
                        f"'{step.name}'."
                    ) from exc
            if step.delay_after > 0:
                time.sleep(step.delay_after)
        logger.info("=== Sequência concluída: %s ===", self.name)


def wait_until(
    controller: MSFSController,
    simvar: str,
    predicate: Callable[[float], bool],
    *,
    timeout: float = 120.0,
    poll_interval: float = 0.5,
) -> float:
    """Bloqueia até que ``predicate(valor_da_simvar)`` seja verdadeiro.

    Útil dentro de passos para sincronizar com o estado do voo — por
    exemplo, esperar a velocidade de rotação antes de puxar o manche.

    Parameters
    ----------
    controller:
        Controlador conectado.
    simvar:
        Nome da SimVar a monitorar (ex.: ``"AIRSPEED_INDICATED"``).
    predicate:
        Função que recebe o valor lido e retorna ``True`` quando a condição
        foi satisfeita.
    timeout:
        Tempo máximo de espera em segundos antes de lançar erro.
    poll_interval:
        Intervalo entre leituras, em segundos.

    Returns
    -------
    float
        O valor da SimVar que satisfez a condição.

    Raises
    ------
    AutomationError
        Se o tempo limite for atingido.
    """
    deadline = time.monotonic() + timeout
    conn = controller.connection
    while time.monotonic() < deadline:
        value = conn.get(simvar)
        if value is not None and predicate(float(value)):
            logger.debug("Condição satisfeita: %s = %s", simvar, value)
            return float(value)
        time.sleep(poll_interval)
    raise AutomationError(
        f"Tempo limite ({timeout:.0f}s) esperando condição em '{simvar}'."
    )
