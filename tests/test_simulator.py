import unittest

from lomiteria.models import SimulationParams
from lomiteria.simulator import simulate


class SimulatorTests(unittest.TestCase):
    def test_simulation_keeps_requested_rows_and_final_row(self):
        params = SimulationParams(x_minutes=20.0, max_iterations=1000, display_from=2, display_count=5, seed=123)
        result = simulate(params)
        self.assertEqual(len(result.rows), 5)
        self.assertEqual(result.final_row.evento, "fin_simulacion")
        self.assertEqual(result.final_row.reloj_min, 20.0)
        self.assertLessEqual(result.total_iterations, 1000)

    def test_simulation_exposes_controls_and_metrics(self):
        params = SimulationParams(x_minutes=45.0, max_iterations=1000, display_from=1, display_count=3, seed=321)
        result = simulate(params)
        self.assertTrue(result.controls_15)
        self.assertTrue(result.controls_30)
        self.assertIn("tiempo_promedio_permanencia_negocio", result.metrics)
        self.assertIn("porcentaje_ocupacion_caja", result.metrics)

    def test_vector_rows_are_categorized_and_include_random_columns(self):
        params = SimulationParams(x_minutes=10.0, max_iterations=1000, display_from=1, display_count=2, seed=44)
        result = simulate(params)
        row = result.rows[0]
        grouped = row.as_grouped_dict()
        self.assertEqual(
            set(grouped),
            {"RELOJ_EVENTO", "EVENTOS", "OBJETOS_PERMANENTES", "VARIABLES_ESTADISTICAS", "OBJETOS_TEMPORALES"},
        )
        self.assertIn("rnd_llegada_1", grouped["EVENTOS"])
        self.assertIn("estado_caja", grouped["OBJETOS_PERMANENTES"])

    def test_simulation_keeps_only_last_ten_rows_for_recent_view(self):
        params = SimulationParams(x_minutes=80.0, max_iterations=1000, display_from=1, display_count=2, seed=45)
        result = simulate(params)
        self.assertLessEqual(len(result.last_rows), 10)
        self.assertEqual(result.last_rows[-1].evento, result.final_row.evento)
        self.assertEqual(result.last_rows[-1].reloj_min, result.final_row.reloj_min)


if __name__ == "__main__":
    unittest.main()
