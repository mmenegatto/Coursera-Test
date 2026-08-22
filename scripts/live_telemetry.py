"""Painel de telemetria ao vivo do MSFS 2024 no console.

Mostra altitude, velocidade, posição (lat/lon), rumo, atitude e razão de
subida atualizando em tempo real, redesenhando no lugar (ANSI). Sem
dependências externas.

Uso (com o simulador aberto e em voo)::

    python -m scripts.live_telemetry
    python -m scripts.live_telemetry --hz 5     # 5 atualizações por segundo

Pressione Ctrl+C para sair.
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Optional

from msfs_control import SimConnection, SimConnectionError
from msfs_control.telemetry import Telemetry, TelemetryReader

# Sequências ANSI.
_CLEAR = "\033[2J"
_HOME = "\033[H"
_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"


def _fmt(value: Optional[float], unit: str = "", decimals: int = 0) -> str:
    """Formata um número com unidade, ou '---' se ausente."""
    if value is None:
        return f"{'---':>10} {unit}".rstrip()
    return f"{value:>10.{decimals}f} {unit}".rstrip()


def _fmt_coord(value: Optional[float], pos: str, neg: str) -> str:
    """Formata coordenada com hemisfério (ex.: 23.5432 S)."""
    if value is None:
        return "        ---"
    hemi = pos if value >= 0 else neg
    return f"{abs(value):9.4f}° {hemi}"


def render(t: Telemetry) -> str:
    """Monta o texto do painel a partir de um snapshot."""
    ground = "SOLO" if t.on_ground else "EM VOO" if t.on_ground is not None else "?"
    lines = [
        "+--------------------------------------------------+",
        "|          MSFS 2024 - TELEMETRIA AO VIVO          |",
        "+--------------------------------------------------+",
        f"|  Estado        : {ground:<31} |",
        "|                                                  |",
        f"|  Altitude MSL  : {_fmt(t.altitude_ft, 'ft'):<31} |",
        f"|  Altura (AGL)  : {_fmt(t.altitude_agl_ft, 'ft'):<31} |",
        f"|  Vel. indicada : {_fmt(t.airspeed_kt, 'kt'):<31} |",
        f"|  Vel. solo     : {_fmt(t.ground_speed_kt, 'kt'):<31} |",
        f"|  Razao subida  : {_fmt(t.vertical_speed_fpm, 'fpm'):<31} |",
        "|                                                  |",
        f"|  Rumo (mag)    : {_fmt(t.heading_deg, 'deg'):<31} |",
        f"|  Pitch         : {_fmt(t.pitch_deg, 'deg', 1):<31} |",
        f"|  Bank          : {_fmt(t.bank_deg, 'deg', 1):<31} |",
        f"|  Throttle      : {_fmt(t.throttle_pct, '%'):<31} |",
        "|                                                  |",
        f"|  Latitude      : {_fmt_coord(t.latitude_deg, 'N', 'S'):<31} |",
        f"|  Longitude     : {_fmt_coord(t.longitude_deg, 'E', 'W'):<31} |",
        "+--------------------------------------------------+",
        "|  Ctrl+C para sair                                |",
        "+--------------------------------------------------+",
    ]
    return "\n".join(lines)


def run(hz: float) -> int:
    interval = 1.0 / hz if hz > 0 else 0.25
    try:
        with SimConnection() as conn:
            reader = TelemetryReader(conn)
            sys.stdout.write(_HIDE_CURSOR + _CLEAR)
            while True:
                snap = reader.read()
                sys.stdout.write(_HOME + render(snap) + "\n")
                sys.stdout.flush()
                time.sleep(interval)
    except SimConnectionError as exc:
        sys.stdout.write(_SHOW_CURSOR)
        print(f"\n[ERRO de conexao] {exc}")
        return 1
    except KeyboardInterrupt:
        sys.stdout.write(_SHOW_CURSOR)
        print("\nEncerrado.")
        return 0
    finally:
        sys.stdout.write(_SHOW_CURSOR)
        sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser(description="Painel de telemetria ao vivo do MSFS 2024.")
    parser.add_argument(
        "--hz", type=float, default=4.0,
        help="Taxa de atualizacao por segundo (padrao: 4).",
    )
    args = parser.parse_args()
    sys.exit(run(args.hz))


if __name__ == "__main__":
    main()
