"""Testes que rodam SEM o simulador (lógica pura).

Executar::

    python -m pytest tests/            # se tiver pytest
    python -m unittest discover tests  # com a stdlib
"""

import unittest

from msfs_control.controller import _percent_to_axis, _AXIS_MAX


class PercentToAxisTests(unittest.TestCase):
    def test_zero_percent(self):
        self.assertEqual(_percent_to_axis(0), 0)

    def test_full_percent(self):
        self.assertEqual(_percent_to_axis(100), _AXIS_MAX)

    def test_half_percent(self):
        self.assertEqual(_percent_to_axis(50), round(_AXIS_MAX / 2))

    def test_clamps_above_100(self):
        self.assertEqual(_percent_to_axis(150), _AXIS_MAX)

    def test_clamps_below_0(self):
        self.assertEqual(_percent_to_axis(-20), 0)


class ImportSafetyTests(unittest.TestCase):
    """Garante que o pacote importa mesmo sem a lib SimConnect instalada."""

    def test_package_imports(self):
        import msfs_control

        self.assertTrue(hasattr(msfs_control, "MSFSController"))
        self.assertTrue(hasattr(msfs_control, "Sequence"))


if __name__ == "__main__":
    unittest.main()
