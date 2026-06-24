from collections import deque
import unittest

from lomiteria.modelo.objetos import SimulationParams, StateRow
from lomiteria.simulacion.motor import _guardar_fila, simulate


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

    def test_row_storage_policy_stays_bounded_with_100000_logical_lines(self):
        params = SimulationParams(display_from=99991, display_count=10)
        filas_visibles = []
        ultimas_filas = deque(maxlen=10)
        for nro_evento in range(1, 100001):
            fila = StateRow(
                nro_evento=nro_evento,
                evento="prueba",
                reloj_min=float(nro_evento),
                hora_real="11:00",
                eventos={},
                objetos_permanentes={},
                variables_estadisticas={},
                objetos_temporales={},
            )
            _guardar_fila(fila, filas_visibles, ultimas_filas, params)
        self.assertEqual(len(filas_visibles), 10)
        self.assertEqual(filas_visibles[0].nro_evento, 99991)
        self.assertEqual(filas_visibles[-1].nro_evento, 100000)
        self.assertEqual(len(ultimas_filas), 10)
        self.assertEqual(ultimas_filas[0].nro_evento, 99991)
        self.assertEqual(ultimas_filas[-1].nro_evento, 100000)

    def test_simulation_reaches_100000_iterations_with_bounded_visible_memory(self):
        params = SimulationParams(
            x_minutes=1_000_000.0,
            max_iterations=100000,
            display_from=99991,
            display_count=10,
            seed=123,
        )
        result = simulate(params)
        self.assertEqual(result.total_iterations, 100000)
        self.assertEqual(result.final_row.evento, "limite_iteraciones")
        self.assertEqual(len(result.rows), 10)
        self.assertEqual(result.rows[0].nro_evento, 99991)
        self.assertEqual(result.rows[-1].nro_evento, 100000)
        self.assertEqual(len(result.last_rows), 10)

    def test_simulation_runs_with_all_parameters_changed(self):
        params = SimulationParams(
            x_minutes=120.0,
            max_iterations=5000,
            display_from=3,
            display_count=10,
            seed=77,
            llegada_media=0.8,
            llegada_desvio=0.2,
            caja_min=0.15,
            caja_max=0.45,
            prob_llevar=0.35,
            prob_rojo=0.6,
            capacidad_rojo=18,
            capacidad_azul=26,
            preparadores=4,
            llevar_min=0.9,
            llevar_max=1.7,
            a_values=(3, 4, 6),
            rk_h=0.02,
            rk_limit_l=9.5,
            rk_minutes_per_unit=8.0,
            control_mostrador_interval=12.0,
            control_salones_interval=24.0,
            rojo_11_min=4.0,
            rojo_11_max=18.0,
            rojo_12_min=8.0,
            rojo_12_max=22.0,
            rojo_13_min=10.0,
            rojo_13_max=24.0,
            rojo_14_min=6.0,
            rojo_14_max=20.0,
            azul_11_min=7.0,
            azul_11_max=21.0,
            azul_12_min=11.0,
            azul_12_max=25.0,
            azul_13_min=13.0,
            azul_13_max=27.0,
            azul_14_min=9.0,
            azul_14_max=23.0,
        )
        result = simulate(params)
        self.assertEqual(result.params.preparadores, 4)
        self.assertEqual(sorted(result.rk4_tables), [3, 4, 6])
        self.assertEqual(len(result.rows), 10)
        self.assertEqual(result.rows[0].nro_evento, 3)
        self.assertTrue(result.controls_15)
        self.assertTrue(result.controls_30)
        self.assertIn("tiempo_promedio_cola_mostrador", result.metrics)
        self.assertIn("porcentaje_ocupacion_preparadores", result.metrics)


if __name__ == "__main__":
    unittest.main()
