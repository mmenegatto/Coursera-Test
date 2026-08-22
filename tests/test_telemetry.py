"""Testes de telemetria que rodam SEM o simulador.

Usam uma conexão falsa (fake) que devolve valores brutos pré-definidos,
para validar as conversões de unidade e a robustez a leituras ausentes.
"""

import math
import unittest

from msfs_control.connection import SimConnectionError
from msfs_control.telemetry import Telemetry, TelemetryReader
from scripts.live_telemetry import render, _fmt, _fmt_coord


class FakeConnection:
    """Simula SimConnection.get() a partir de um dicionário de SimVars brutas."""

    def __init__(self, raw: dict, missing=()):
        self._raw = raw
        self._missing = set(missing)

    def get(self, simvar):
        if simvar in self._missing:
            raise SimConnectionError(f"simvar ausente: {simvar}")
        return self._raw.get(simvar)


class TelemetryReaderTests(unittest.TestCase):
    def test_unit_conversions(self):
        raw = {
            "PLANE_LATITUDE": math.radians(-23.5),   # graus -> rad na entrada
            "PLANE_LONGITUDE": math.radians(-46.6),
            "PLANE_ALTITUDE": 3500.0,
            "PLANE_ALT_ABOVE_GROUND": 3400.0,
            "AIRSPEED_INDICATED": 250.0,
            "GROUND_VELOCITY": 260.0,
            "VERTICAL_SPEED": 20.0,                   # fps -> deve virar 1200 fpm
            "PLANE_HEADING_DEGREES_MAGNETIC": math.radians(90),
            "PLANE_PITCH_DEGREES": math.radians(-5),  # sinal invertido -> +5
            "PLANE_BANK_DEGREES": math.radians(10),   # sinal invertido -> -10
            "GENERAL_ENG_THROTTLE_LEVER_POSITION:1": 80.0,
            "SIM_ON_GROUND": 0.0,
        }
        t = TelemetryReader(FakeConnection(raw)).read()

        self.assertAlmostEqual(t.latitude_deg, -23.5, places=3)
        self.assertAlmostEqual(t.longitude_deg, -46.6, places=3)
        self.assertEqual(t.altitude_ft, 3500.0)
        self.assertAlmostEqual(t.vertical_speed_fpm, 1200.0, places=3)
        self.assertAlmostEqual(t.heading_deg, 90.0, places=3)
        self.assertAlmostEqual(t.pitch_deg, 5.0, places=3)
        self.assertAlmostEqual(t.bank_deg, -10.0, places=3)
        self.assertEqual(t.throttle_pct, 80.0)
        self.assertFalse(t.on_ground)

    def test_missing_simvar_becomes_none(self):
        reader = TelemetryReader(FakeConnection({}, missing=["PLANE_ALTITUDE"]))
        t = reader.read()
        self.assertIsNone(t.altitude_ft)

    def test_as_dict_has_all_fields(self):
        t = Telemetry(altitude_ft=1000.0)
        d = t.as_dict()
        self.assertIn("altitude_ft", d)
        self.assertEqual(d["altitude_ft"], 1000.0)
        self.assertIn("latitude_deg", d)


class FormattingTests(unittest.TestCase):
    def test_fmt_none(self):
        self.assertIn("---", _fmt(None, "ft"))

    def test_fmt_value(self):
        self.assertIn("ft", _fmt(1234.0, "ft"))

    def test_fmt_coord_hemispheres(self):
        self.assertIn("S", _fmt_coord(-23.5, "N", "S"))
        self.assertIn("N", _fmt_coord(23.5, "N", "S"))
        self.assertIn("---", _fmt_coord(None, "N", "S"))

    def test_render_runs(self):
        out = render(Telemetry(altitude_ft=3500.0, airspeed_kt=250.0, on_ground=False))
        self.assertIn("TELEMETRIA", out)
        self.assertIn("EM VOO", out)


if __name__ == "__main__":
    unittest.main()
