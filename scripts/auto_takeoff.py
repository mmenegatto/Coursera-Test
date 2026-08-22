"""Sequência automatizada de decolagem para o MSFS 2024.

AVISO: Este é um exemplo educativo. Automação de decolagem depende muito da
aeronave (velocidades V1/VR, configuração de flaps, etc.). Ajuste as
velocidades e a configuração conforme a aeronave que você estiver usando.

Uso (com o sim aberto, aeronave alinhada na pista)::

    python -m scripts.auto_takeoff
"""

from __future__ import annotations

import logging

from msfs_control import MSFSController, Sequence, Step, SimConnectionError, wait_until

# Velocidade de rotação (nós). Ajuste conforme a aeronave.
ROTATE_SPEED_KTS = 130
# Altitude (pés AGL aproximada) para recolher o trem.
GEAR_UP_ALT_FT = 100


def build_takeoff_sequence() -> Sequence:
    return Sequence(
        "Decolagem automática",
        [
            Step("Luzes de pouso e strobes ligados",
                 lambda m: (m.landing_lights(True), m.strobe_lights(True))),
            Step("Flaps de decolagem (posição 1)",
                 lambda m: m.flaps(1)),
            Step("Liberar freio de estacionamento",
                 lambda m: m.set_parking_brake(False)),
            Step("Aplicar potência total",
                 lambda m: m.throttle_full()),
            Step(f"Aguardar velocidade de rotação ({ROTATE_SPEED_KTS} kt)",
                 lambda m: wait_until(
                     m, "AIRSPEED_INDICATED",
                     lambda v: v >= ROTATE_SPEED_KTS, timeout=90)),
            Step(f"Aguardar subida ({GEAR_UP_ALT_FT} ft) e recolher trem",
                 lambda m: (
                     wait_until(m, "PLANE_ALT_ABOVE_GROUND",
                                lambda v: v >= GEAR_UP_ALT_FT, timeout=60),
                     m.gear_up(),
                 )),
            Step("Recolher flaps",
                 lambda m: m.flaps(0), delay_after=2),
        ],
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        with MSFSController() as msfs:
            build_takeoff_sequence().run(msfs)
            print("\nDecolagem concluída. Bom voo!")
    except SimConnectionError as exc:
        print(f"[ERRO de conexão] {exc}")


if __name__ == "__main__":
    main()
