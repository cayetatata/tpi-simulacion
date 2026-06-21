import unittest

from lomiteria.models import SimulationParams
from lomiteria.tables import lookup_a_value, lookup_salon, lookup_tipo_consumo, permanence_range


class TableTests(unittest.TestCase):
    def test_tipo_consumo_table_boundaries(self):
        params = SimulationParams()
        self.assertEqual(lookup_tipo_consumo(0.0, params), "llevar")
        self.assertEqual(lookup_tipo_consumo(0.249, params), "llevar")
        self.assertEqual(lookup_tipo_consumo(0.25, params), "local")
        self.assertEqual(lookup_tipo_consumo(0.99, params), "local")

    def test_salon_table_boundaries(self):
        params = SimulationParams()
        self.assertEqual(lookup_salon(0.0, params), "rojo")
        self.assertEqual(lookup_salon(0.299, params), "rojo")
        self.assertEqual(lookup_salon(0.30, params), "azul")
        self.assertEqual(lookup_salon(0.99, params), "azul")

    def test_a_value_uses_four_equal_intervals(self):
        params = SimulationParams()
        self.assertEqual(lookup_a_value(0.00, params), 2)
        self.assertEqual(lookup_a_value(0.26, params), 3)
        self.assertEqual(lookup_a_value(0.50, params), 4)
        self.assertEqual(lookup_a_value(0.99, params), 5)

    def test_permanence_range_uses_clock_minute_band(self):
        self.assertEqual(permanence_range("rojo", 0), (5.0, 35.0))
        self.assertEqual(permanence_range("rojo", 60), (15.0, 45.0))
        self.assertEqual(permanence_range("azul", 120), (35.0, 55.0))
        self.assertEqual(permanence_range("azul", 180), (20.0, 50.0))

    def test_permanence_range_can_be_changed_from_params(self):
        params = SimulationParams(rojo_11_min=1.0, rojo_11_max=2.0, azul_14_min=3.0, azul_14_max=4.0)
        self.assertEqual(permanence_range("rojo", 0, params), (1.0, 2.0))
        self.assertEqual(permanence_range("azul", 180, params), (3.0, 4.0))


if __name__ == "__main__":
    unittest.main()
