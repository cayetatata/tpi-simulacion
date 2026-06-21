import json
import unittest

from lomiteria.models import SimulationParams
from lomiteria.simulator import simulate
from lomiteria.web_server import params_from_payload, result_to_payload


class WebServerTests(unittest.TestCase):
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
        self.assertIn("controls_15", payload)
        self.assertIn("controls_30", payload)
        self.assertIn("rk4_tables", payload)
        self.assertIn("intermediate_tables", payload)
        self.assertEqual(payload["summary"]["final_event"], "fin_simulacion")

    def test_params_payload_accepts_editable_a_values(self):
        params = params_from_payload({"a_values": "1, 4, 7", "x_minutes": "20"})
        self.assertEqual(params.a_values, (1, 4, 7))
        self.assertEqual(params.x_minutes, 20.0)


if __name__ == "__main__":
    unittest.main()
