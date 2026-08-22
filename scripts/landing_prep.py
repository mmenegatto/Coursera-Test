"""Sequência automatizada de preparação para pouso (approach checklist).

AVISO: Exemplo educativo. Não substitui o pilotar manual do approach; apenas
configura a aeronave. Ajuste velocidades/flaps conforme a aeronave.

Uso (em voo, aproximando-se do aeroporto)::

    python -m scripts.landing_prep
"""

from __future__ import annotations

import logging

from msfs_control import MSFSController, Sequence, Step, SimConnectionError, wait_until

# Abaixo desta velocidade (kt) é seguro estender flaps totais e trem.
GEAR_DOWN_SPEED_KTS = 180


def build_landing_prep_sequence() -> Sequence:
    return Sequence(
        "Preparação para pouso",
        [
            Step("Luzes de pouso ligadas",
                 lambda m: m.landing_lights(True)),
            Step("Desligar piloto automático",
                 lambda m: m.autopilot(False)),
            Step("Flaps de aproximação (posição 2)",
                 lambda m: m.flaps(2)),
            Step(f"Aguardar velocidade segura ({GEAR_DOWN_SPEED_KTS} kt) e baixar trem",
                 lambda m: (
                     wait_until(m, "AIRSPEED_INDICATED",
                                lambda v: v <= GEAR_DOWN_SPEED_KTS, timeout=120),
                     m.gear_down(),
                 )),
            Step("Flaps totais (posição 3)",
                 lambda m: m.flaps(3), delay_after=1),
            Step("Armar spoilers",
                 lambda m: m.spoilers(True)),
        ],
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        with MSFSController() as msfs:
            build_landing_prep_sequence().run(msfs)
            print("\nAeronave configurada para o pouso. Boa aterrissagem!")
    except SimConnectionError as exc:
        print(f"[ERRO de conexão] {exc}")


if __name__ == "__main__":
    main()
