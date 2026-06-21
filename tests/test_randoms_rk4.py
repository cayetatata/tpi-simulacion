import unittest

from lomiteria.models import SimulationParams
from lomiteria.randoms import uniform
from lomiteria.rk4 import build_rk4_tables


class RandomsRk4Tests(unittest.TestCase):
    def test_uniform_formula(self):
        self.assertEqual(uniform(0.5, 10.0, 20.0), 15.0)

    def test_rk4_tables_cover_all_a_values_and_finish_over_limit(self):
        params = SimulationParams()
        tables, times = build_rk4_tables(params)
        self.assertEqual(sorted(tables), [2, 3, 4, 5])
        self.assertTrue(all(times[a] > 0 for a in [2, 3, 4, 5]))
        self.assertGreater(tables[2][-1]["L"], params.rk_limit_l)
        self.assertGreater(tables[5][-1]["L"], params.rk_limit_l)

    def test_rk4_time_for_a_2_uses_first_step_over_limit(self):
        params = SimulationParams()
        _, times = build_rk4_tables(params)
        self.assertEqual(times[2], 6.7)


if __name__ == "__main__":
    unittest.main()
