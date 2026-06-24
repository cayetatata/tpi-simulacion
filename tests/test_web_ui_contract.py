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
        self.assertNotIn("statisticsGrid", html)
        self.assertIn("metric-detail", js)
        self.assertIn("last_rows", js)

    def test_vector_has_grouped_headers_and_next_event_highlight(self):
        js = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("Llegada clientes", js)
        self.assertIn("Objetos permanentes", js)
        self.assertIn("Preparador 1", js)
        self.assertIn("Salon rojo estadisticas", js)
        self.assertIn("formula_box_muller", js)
        self.assertIn("next-event-cell", js)
        self.assertIn("vector-category-row", js)
        self.assertIn("next-event-cell", css)


if __name__ == "__main__":
    unittest.main()
