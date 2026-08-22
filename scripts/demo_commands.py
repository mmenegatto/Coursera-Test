"""Demonstração de envio de comandos individuais ao MSFS 2024.

Execute com o simulador aberto e uma sessão de voo carregada::

    python -m scripts.demo_commands

Cada comando é enviado com uma pequena pausa para você observar o efeito.
"""

from __future__ import annotations

import logging
import time

from msfs_control import MSFSController, SimConnectionError


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        with MSFSController() as msfs:
            print("Conectado ao MSFS. Enviando comandos de demonstração...\n")

            msfs.landing_lights(True)
            time.sleep(1)

            msfs.strobe_lights(True)
            time.sleep(1)

            msfs.set_parking_brake(False)
            time.sleep(1)

            msfs.throttle(50)
            time.sleep(2)

            msfs.throttle_idle()
            time.sleep(1)

            msfs.set_parking_brake(True)
            print("\nDemonstração concluída.")

    except SimConnectionError as exc:
        print(f"[ERRO] {exc}")


if __name__ == "__main__":
    main()
