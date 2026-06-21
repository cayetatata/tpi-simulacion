from __future__ import annotations

import json
import mimetypes
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .distributions import NOTAS_ORIGEN_RND
from .metrics import definiciones_metricas
from .models import SimulationParams, SimulationResult
from .object_definitions import DEFINICIONES_ESTADOS_CLIENTE, DEFINICIONES_OBJETOS, DEFINICIONES_VARIABLES_ESTADISTICAS
from .simulator import simulate


WEB_DIR = Path(__file__).resolve().parent.parent / "web"


def result_to_payload(result: SimulationResult) -> dict[str, Any]:
    return {
        "summary": {
            "iterations": result.total_iterations,
            "final_event": result.final_row.evento,
            "final_clock": result.final_row.reloj_min,
            "final_hour": result.final_row.hora_real,
            "visible_rows": len(result.rows),
            "controls_15": len(result.controls_15),
            "controls_30": len(result.controls_30),
        },
        "rk4_parameters": {
            "h": result.params.rk_h,
            "limite_l": result.params.rk_limit_l,
            "minutos_por_t": result.params.rk_minutes_per_unit,
            "regla_l_inicial": "L inicial = A",
            "ecuacion": "dL/dt = 3A + 6",
        },
        "vector_rows": [row.as_grouped_dict() for row in result.rows],
        "last_rows": [row.as_grouped_dict() for row in result.last_rows],
        "vector_flat": [row.flat_dict() for row in result.rows],
        "final_row": result.final_row.as_grouped_dict(),
        "final_flat": result.final_row.flat_dict(),
        "metrics": result.metrics,
        "metric_definitions": definiciones_metricas(),
        "statistic_definitions": DEFINICIONES_VARIABLES_ESTADISTICAS,
        "object_definitions": DEFINICIONES_OBJETOS,
        "state_definitions": DEFINICIONES_ESTADOS_CLIENTE,
        "random_source_notes": NOTAS_ORIGEN_RND,
        "controls_15": result.controls_15,
        "controls_30": result.controls_30,
        "rk4_tables": result.rk4_tables,
        "intermediate_tables": result.intermediate_tables,
    }


def params_from_payload(payload: dict[str, Any]) -> SimulationParams:
    valid_fields = set(SimulationParams.__dataclass_fields__)
    values: dict[str, Any] = {}
    for key, value in payload.items():
        if key not in valid_fields or value == "":
            continue
        if key == "a_values":
            values[key] = tuple(int(part.strip()) for part in str(value).split(",") if part.strip())
        elif key in {"max_iterations", "display_from", "display_count", "seed", "capacidad_rojo", "capacidad_azul", "preparadores"}:
            values[key] = int(value)
        else:
            values[key] = float(value)
    return SimulationParams(**values)


def create_handler() -> type[BaseHTTPRequestHandler]:
    class LomiteriaHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib method name
            path = self.path.split("?", 1)[0]
            if path == "/":
                path = "/index.html"
            file_path = (WEB_DIR / path.lstrip("/")).resolve()
            if not str(file_path).startswith(str(WEB_DIR.resolve())) or not file_path.exists():
                self._send_json({"error": "No encontrado"}, status=404)
                return

            content = file_path.read_bytes()
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self) -> None:  # noqa: N802 - stdlib method name
            if self.path != "/api/simulate":
                self._send_json({"error": "Endpoint no encontrado"}, status=404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(body or "{}")
                params = params_from_payload(payload)
                result = simulate(params)
                self._send_json(result_to_payload(result))
            except Exception as exc:  # keep API error readable for class demo
                self._send_json({"error": str(exc)}, status=400)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
            content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    return LomiteriaHandler


def run_web_app(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    server = ThreadingHTTPServer((host, port), create_handler())
    url = f"http://{host}:{port}"
    print(f"Servidor Lomiteria: {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
