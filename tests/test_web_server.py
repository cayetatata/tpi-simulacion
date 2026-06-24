import json
import unittest

from lomiteria.interfaz.servidor_web import WEB_DIR, params_from_payload, result_to_payload
from lomiteria.modelo.objetos import SimulationParams
from lomiteria.simulacion.motor import simulate


class WebServerTests(unittest.TestCase):
    def test_web_dir_points_to_real_index_file(self):
        self.assertTrue((WEB_DIR / "index.html").exists())

    def test_result_payload_is_json_serializable(self):
        result = simulate(SimulationParams(x_minutes=5.0, display_from=1, display_count=3, seed=5))
        payload = result_to_payload(result)
        encoded = json.dumps(payload)
        self.assertIn("vector_rows", encoded)
        self.assertEqual(len(payload["vector_rows"]), 3)

    def test_result_payload_exposes_ui_sections(self):
        result = simulate(SimulationParams(x_minutes=30.0, display_from=1, display_count=2, seed=8))
        payload = result_to_payload(result)
        self.assertIn("summary", payload)
        self.assertIn("metrics", payload)
        self.assertIn("final_row", payload)
        self.assertIn("last_rows", payload)
        self.assertIn("controls_15", payload)
        self.assertIn("controls_30", payload)
        self.assertIn("rk4_tables", payload)
        self.assertIn("intermediate_tables", payload)
        self.assertEqual(payload["summary"]["final_event"], "fin_simulacion")
        self.assertLessEqual(len(payload["last_rows"]), 10)

    def test_result_payload_keeps_only_runtime_data_for_frontend(self):
        result = simulate(SimulationParams(x_minutes=30.0, display_from=1, display_count=2, seed=8))
        payload = result_to_payload(result)
        self.assertNotIn("metric_definitions", payload)
        self.assertNotIn("statistic_definitions", payload)
        self.assertNotIn("object_definitions", payload)
        self.assertNotIn("state_definitions", payload)
        self.assertNotIn("random_source_notes", payload)
        self.assertNotIn("box_muller_rows", payload)
        self.assertNotIn("box_muller_summary", payload)

    def test_params_payload_accepts_editable_a_values(self):
        params = params_from_payload({"a_values": "1, 4, 7", "x_minutes": "20"})
        self.assertEqual(params.a_values, (1, 4, 7))
        self.assertEqual(params.x_minutes, 20.0)

    def test_params_payload_accepts_all_editable_fields(self):
        payload = {
            "x_minutes": "180",
            "max_iterations": "1234",
            "display_from": "7",
            "display_count": "10",
            "seed": "99",
            "llegada_media": "1.2",
            "llegada_desvio": "0.4",
            "caja_min": "0.2",
            "caja_max": "0.6",
            "prob_llevar": "0.4",
            "prob_rojo": "0.55",
            "capacidad_rojo": "22",
            "capacidad_azul": "33",
            "preparadores": "4",
            "llevar_min": "1.1",
            "llevar_max": "2.2",
            "a_values": "3, 5, 7",
            "rk_h": "0.02",
            "rk_limit_l": "11",
            "rk_minutes_per_unit": "12",
            "control_mostrador_interval": "12",
            "control_salones_interval": "24",
            "rojo_11_min": "6",
            "rojo_11_max": "26",
            "rojo_12_min": "16",
            "rojo_12_max": "36",
            "rojo_13_min": "21",
            "rojo_13_max": "41",
            "rojo_14_min": "8",
            "rojo_14_max": "28",
            "azul_11_min": "10",
            "azul_11_max": "30",
            "azul_12_min": "20",
            "azul_12_max": "40",
            "azul_13_min": "25",
            "azul_13_max": "45",
            "azul_14_min": "15",
            "azul_14_max": "35",
        }
        params = params_from_payload(payload)
        self.assertEqual(params.max_iterations, 1234)
        self.assertEqual(params.display_from, 7)
        self.assertEqual(params.display_count, 10)
        self.assertEqual(params.seed, 99)
        self.assertEqual(params.preparadores, 4)
        self.assertEqual(params.capacidad_rojo, 22)
        self.assertEqual(params.capacidad_azul, 33)
        self.assertEqual(params.a_values, (3, 5, 7))
        self.assertEqual(params.control_mostrador_interval, 12.0)
        self.assertEqual(params.control_salones_interval, 24.0)
        self.assertEqual(params.azul_14_max, 35.0)


if __name__ == "__main__":
    unittest.main()
