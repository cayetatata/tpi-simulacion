from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WebUiContractTests(unittest.TestCase):
    def test_web_ui_removes_demo_and_export_actions(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("Cargar demo", html)
        self.assertNotIn("Exportacion", html)
        self.assertNotIn("downloadCsv", js)

    def test_vector_has_category_filter_controls(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-vector-filter="OBJETOS_TEMPORALES"', html)
        self.assertIn('data-vector-filter="VARIABLES_ESTADISTICAS"', html)
        self.assertIn('data-vector-filter="OBJETOS_PERMANENTES"', html)
        self.assertIn('data-vector-filter="EVENTOS"', html)

    def test_vector_and_results_expose_recent_rows_and_stat_cards(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('data-row-scope="last"', html)
        self.assertIn("statisticsGrid", html)
        self.assertIn("renderStatisticCards", js)
        self.assertIn("last_rows", js)


if __name__ == "__main__":
    unittest.main()
