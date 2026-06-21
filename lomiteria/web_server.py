from __future__ import annotations

import json
import mimetypes
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .models import SimulationParams, SimulationResult
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
        "vector_rows": [row.as_grouped_dict() for row in result.rows],
        "vector_flat": [row.flat_dict() for row in result.rows],
        "final_row": result.final_row.as_grouped_dict(),
        "final_flat": result.final_row.flat_dict(),
        "metrics": result.metrics,
        "metric_definitions": metric_definitions(),
        "controls_15": result.controls_15,
        "controls_30": result.controls_30,
        "rk4_tables": result.rk4_tables,
        "intermediate_tables": result.intermediate_tables,
    }


def metric_definitions() -> list[dict[str, Any]]:
    return [
        {
            "metrica": "tiempo_promedio_permanencia_negocio",
            "titulo": "Tiempo promedio de permanencia en el negocio",
            "formula": "ac_tiempo_permanencia_negocio / ct_clientes_finalizados",
            "variables": ["ac_tiempo_permanencia_negocio", "ct_clientes_finalizados"],
            "enunciado": "Responde al punto: Tiempo de permanencia en el negocio.",
        },
        {
            "metrica": "tiempo_promedio_cola_caja",
            "titulo": "Tiempo promedio en cola de caja",
            "formula": "ac_tiempo_cola_caja / ct_clientes_pasan_por_caja",
            "variables": ["ac_tiempo_cola_caja", "ct_clientes_pasan_por_caja"],
            "enunciado": "Responde al punto: Tiempo en cola en la caja.",
        },
        {
            "metrica": "tiempo_promedio_cola_mostrador",
            "titulo": "Tiempo promedio en cola frente al mostrador",
            "formula": "ac_tiempo_cola_mostrador / ct_clientes_pasan_por_mostrador",
            "variables": ["ac_tiempo_cola_mostrador", "ct_clientes_pasan_por_mostrador"],
            "enunciado": "Metrica adicional: demora previa a preparacion.",
        },
        {
            "metrica": "porcentaje_ocupacion_caja",
            "titulo": "Porcentaje de ocupacion de caja",
            "formula": "ac_tiempo_ocupada_caja / reloj_final * 100",
            "variables": ["caja_ac_tiempo_ocupada", "reloj_min"],
            "enunciado": "Metrica adicional: utilizacion del servidor caja.",
        },
        {
            "metrica": "porcentaje_ocupacion_preparadores",
            "titulo": "Porcentaje de ocupacion de preparadores",
            "formula": "sum(ac_tiempo_ocupado_preparador_i) / (preparadores * reloj_final) * 100",
            "variables": ["prep_i_ac_ocupado", "preparadores", "reloj_min"],
            "enunciado": "Metrica adicional: utilizacion del mostrador de preparacion.",
        },
        {
            "metrica": "max_cola_caja",
            "titulo": "Maxima cola de caja",
            "formula": "max(len(cola_caja)) observado en el vector",
            "variables": ["max_cola_caja"],
            "enunciado": "Metrica adicional: pico de congestion en caja.",
        },
        {
            "metrica": "max_cola_mostrador",
            "titulo": "Maxima cola frente al mostrador",
            "formula": "max(len(cola_mostrador)) observado en el vector",
            "variables": ["max_cola_mostrador"],
            "enunciado": "Metrica adicional y apoyo al control cada 15 minutos.",
        },
        {
            "metrica": "clientes_esperaron_salon_rojo_lleno",
            "titulo": "Clientes que esperaron por salon rojo lleno",
            "formula": "conteo de ingresos a cola del salon rojo por capacidad completa",
            "variables": ["ct_esperaron_rojo_lleno", "rojo_ocupacion", "rojo_capacidad"],
            "enunciado": "Metrica adicional vinculada a capacidad del salon rojo.",
        },
        {
            "metrica": "clientes_esperaron_salon_azul_lleno",
            "titulo": "Clientes que esperaron por salon azul lleno",
            "formula": "conteo de ingresos a cola del salon azul por capacidad completa",
            "variables": ["ct_esperaron_azul_lleno", "azul_ocupacion", "azul_capacidad"],
            "enunciado": "Metrica adicional vinculada a capacidad del salon azul.",
        },
        {
            "metrica": "clientes_esperaron_salon_lleno_total",
            "titulo": "Clientes que esperaron por algun salon lleno",
            "formula": "ct_esperaron_rojo_lleno + ct_esperaron_azul_lleno",
            "variables": ["ct_esperaron_rojo_lleno", "ct_esperaron_azul_lleno"],
            "enunciado": "Metrica adicional: total de bloqueos por capacidad de salones.",
        },
        {
            "metrica": "control_15_cola_mostrador",
            "titulo": "Control cada 15 minutos: cola mostrador",
            "formula": "lectura directa de len(cola_mostrador) en cada evento de control",
            "variables": ["control_15_min", "cola_mostrador"],
            "enunciado": "Responde al punto: cada 15 minutos, cantidad de gente en cola frente al mostrador.",
        },
        {
            "metrica": "control_30_ocupacion_salones",
            "titulo": "Control cada 30 minutos: ocupacion de salones",
            "formula": "lectura directa de rojo_ocupacion y azul_ocupacion en cada evento de control",
            "variables": ["control_30_min", "rojo_ocupacion", "azul_ocupacion"],
            "enunciado": "Responde al punto: cada 30 minutos, personas en Salon Rojo y Salon Azul.",
        },
    ]


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
