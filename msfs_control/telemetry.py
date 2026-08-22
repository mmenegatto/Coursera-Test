"""Leitura de telemetria ao vivo do MSFS 2024.

Agrupa a leitura de várias SimVars em um único *snapshot* imutável
(:class:`Telemetry`) e oferece um :class:`TelemetryReader` para amostrar o
estado da aeronave repetidamente.

Exemplo::

    from msfs_control import SimConnection
    from msfs_control.telemetry import TelemetryReader

    with SimConnection() as conn:
        reader = TelemetryReader(conn)
        snap = reader.read()
        print(snap.altitude_ft, snap.airspeed_kt)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import Optional

from .connection import SimConnection, SimConnectionError

# Constante para converter radianos (formato interno do SimConnect para
# lat/lon/heading) em graus.
_RAD_TO_DEG = 180.0 / math.pi


@dataclass(frozen=True)
class Telemetry:
    """Snapshot imutável do estado da aeronave em um instante.

    Todos os campos podem ser ``None`` se a SimVar não pôde ser lida.
    """

    # Posição
    latitude_deg: Optional[float] = None
    longitude_deg: Optional[float] = None
    altitude_ft: Optional[float] = None          # altitude MSL
    altitude_agl_ft: Optional[float] = None      # altura acima do solo

    # Velocidades
    airspeed_kt: Optional[float] = None           # velocidade indicada (IAS)
    ground_speed_kt: Optional[float] = None
    vertical_speed_fpm: Optional[float] = None    # razão de subida/descida

    # Atitude / rumo
    heading_deg: Optional[float] = None           # rumo magnético
    pitch_deg: Optional[float] = None
    bank_deg: Optional[float] = None

    # Motor / sistemas
    throttle_pct: Optional[float] = None
    on_ground: Optional[bool] = None

    def as_dict(self) -> dict:
        """Retorna os campos como dicionário (útil para logging/JSON)."""
        return {f.name: getattr(self, f.name) for f in fields(self)}


# Mapa: campo do dataclass -> (SimVar, função de conversão da unidade bruta).
# O SimConnect retorna latitude/longitude/heading em radianos e velocidades
# em pés/segundo ou m/s dependendo da variável; convertemos aqui.
def _fps_to_fpm(v: float) -> float:
    return v * 60.0


def _ms_to_kt(v: float) -> float:
    return v * 1.943844


_FIELD_MAP = {
    "latitude_deg": ("PLANE_LATITUDE", lambda v: v * _RAD_TO_DEG),
    "longitude_deg": ("PLANE_LONGITUDE", lambda v: v * _RAD_TO_DEG),
    "altitude_ft": ("PLANE_ALTITUDE", float),
    "altitude_agl_ft": ("PLANE_ALT_ABOVE_GROUND", float),
    "airspeed_kt": ("AIRSPEED_INDICATED", float),
    "ground_speed_kt": ("GROUND_VELOCITY", float),
    "vertical_speed_fpm": ("VERTICAL_SPEED", _fps_to_fpm),
    "heading_deg": ("PLANE_HEADING_DEGREES_MAGNETIC", lambda v: v * _RAD_TO_DEG),
    "pitch_deg": ("PLANE_PITCH_DEGREES", lambda v: -v * _RAD_TO_DEG),
    "bank_deg": ("PLANE_BANK_DEGREES", lambda v: -v * _RAD_TO_DEG),
    "throttle_pct": ("GENERAL_ENG_THROTTLE_LEVER_POSITION:1", float),
    "on_ground": ("SIM_ON_GROUND", lambda v: bool(round(v))),
}


class TelemetryReader:
    """Lê telemetria da aeronave a partir de uma :class:`SimConnection`."""

    def __init__(self, connection: SimConnection) -> None:
        self._conn = connection

    def read(self) -> Telemetry:
        """Coleta um snapshot completo do estado atual.

        Uma SimVar que falhar na leitura vira ``None`` no snapshot, em vez de
        interromper a coleta inteira — assim o painel continua funcionando
        mesmo que uma variável não exista na aeronave atual.
        """
        values = {}
        for field_name, (simvar, convert) in _FIELD_MAP.items():
            try:
                raw = self._conn.get(simvar)
            except SimConnectionError:
                raw = None
            if raw is None:
                values[field_name] = None
            else:
                try:
                    values[field_name] = convert(float(raw))
                except (TypeError, ValueError):
                    values[field_name] = None
        return Telemetry(**values)
