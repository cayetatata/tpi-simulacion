import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lomiteria.exporter import export_result
from lomiteria.models import SimulationParams
from lomiteria.simulator import simulate


class ExporterTests(unittest.TestCase):
    def test_export_result_writes_required_csv_files(self):
        result = simulate(SimulationParams(x_minutes=5.0, display_from=1, display_count=2, seed=12))
        with TemporaryDirectory() as tmp:
            paths = export_result(result, Path(tmp))
            names = {path.name for path in paths}
            self.assertIn("vector_estado.csv", names)
            self.assertIn("ultima_fila.csv", names)
            self.assertIn("metricas.csv", names)
            self.assertIn("controles_15min.csv", names)
            self.assertIn("controles_30min.csv", names)
            self.assertIn("runge_kutta_A2.csv", names)
            self.assertIn("tablas_intermedias.csv", names)


if __name__ == "__main__":
    unittest.main()
