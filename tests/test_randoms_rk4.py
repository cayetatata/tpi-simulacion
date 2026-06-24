import random
import unittest

from lomiteria.aleatorios.box_muller import EstadoBoxMuller, normal_positiva_con_memoria
from lomiteria.aleatorios.distribuciones import uniforme
from lomiteria.calculos.runge_kutta_preparacion import construir_tablas_rk4
from lomiteria.modelo.objetos import SimulationParams


class RandomsRk4Tests(unittest.TestCase):
    def test_uniform_formula(self):
        self.assertEqual(uniforme(0.5, 10.0, 20.0), 15.0)

    def test_box_muller_reuses_second_value_before_generating_new_pair(self):
        estado_box_muller = EstadoBoxMuller()
        generador = random.Random(17)
        primero = normal_positiva_con_memoria(estado_box_muller, generador, 10.0, 1.0)
        self.assertIsNotNone(estado_box_muller.valor_pendiente)
        segundo = normal_positiva_con_memoria(estado_box_muller, generador, 10.0, 1.0)
        self.assertIsNone(estado_box_muller.valor_pendiente)
        self.assertEqual(primero.rnd1, segundo.rnd1)
        self.assertEqual(primero.rnd2, segundo.rnd2)
        self.assertEqual(primero.formula_usada, "coseno")
        self.assertEqual(segundo.formula_usada, "seno")
        self.assertEqual(segundo.origen, "memoria")

    def test_rk4_tables_cover_all_a_values_and_finish_over_limit(self):
        params = SimulationParams()
        tables, times = construir_tablas_rk4(params)
        self.assertEqual(sorted(tables), [2, 3, 4, 5])
        self.assertTrue(all(times[a] > 0 for a in [2, 3, 4, 5]))
        self.assertGreater(tables[2][-1]["L"], params.rk_limit_l)
        self.assertGreater(tables[5][-1]["L"], params.rk_limit_l)

    def test_rk4_time_for_a_2_uses_first_step_over_limit(self):
        params = SimulationParams()
        _, times = construir_tablas_rk4(params)
        self.assertEqual(times[2], 6.6)
        self.assertEqual(times[3], 4.6)
        self.assertEqual(times[4], 3.3)
        self.assertEqual(times[5], 2.3)


if __name__ == "__main__":
    unittest.main()
