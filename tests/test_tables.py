import unittest

from lomiteria.aleatorios.tablas_probabilidad import buscar_salon, buscar_tipo_consumo, buscar_valor_a, rango_permanencia
from lomiteria.modelo.objetos import SimulationParams


class TableTests(unittest.TestCase):
    def test_tipo_consumo_table_boundaries(self):
        params = SimulationParams()
        self.assertEqual(buscar_tipo_consumo(0.0, params), "llevar")
        self.assertEqual(buscar_tipo_consumo(0.249, params), "llevar")
        self.assertEqual(buscar_tipo_consumo(0.25, params), "local")
        self.assertEqual(buscar_tipo_consumo(0.99, params), "local")

    def test_salon_table_boundaries(self):
        params = SimulationParams()
        self.assertEqual(buscar_salon(0.0, params), "rojo")
        self.assertEqual(buscar_salon(0.299, params), "rojo")
        self.assertEqual(buscar_salon(0.30, params), "azul")
        self.assertEqual(buscar_salon(0.99, params), "azul")

    def test_a_value_uses_four_equal_intervals(self):
        params = SimulationParams()
        self.assertEqual(buscar_valor_a(0.00, params), 2)
        self.assertEqual(buscar_valor_a(0.26, params), 3)
        self.assertEqual(buscar_valor_a(0.50, params), 4)
        self.assertEqual(buscar_valor_a(0.99, params), 5)

    def test_permanence_range_uses_clock_minute_band(self):
        self.assertEqual(rango_permanencia("rojo", 0), (5.0, 35.0))
        self.assertEqual(rango_permanencia("rojo", 60), (15.0, 45.0))
        self.assertEqual(rango_permanencia("azul", 120), (35.0, 55.0))
        self.assertEqual(rango_permanencia("azul", 180), (20.0, 50.0))

    def test_permanence_range_can_be_changed_from_params(self):
        params = SimulationParams(rojo_11_min=1.0, rojo_11_max=2.0, azul_14_min=3.0, azul_14_max=4.0)
        self.assertEqual(rango_permanencia("rojo", 0, params), (1.0, 2.0))
        self.assertEqual(rango_permanencia("azul", 180, params), (3.0, 4.0))


if __name__ == "__main__":
    unittest.main()
