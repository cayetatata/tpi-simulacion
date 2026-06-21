from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .models import SimulationResult, StateRow


def export_result(result: SimulationResult, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    paths.append(_write_rows(output_dir / "vector_estado.csv", [row.flat_dict() for row in result.rows]))
    paths.append(_write_rows(output_dir / "ultima_fila.csv", [result.final_row.flat_dict()]))
    paths.append(_write_key_values(output_dir / "metricas.csv", result.metrics))
    paths.append(_write_rows(output_dir / "controles_15min.csv", result.controls_15))
    paths.append(_write_rows(output_dir / "controles_30min.csv", result.controls_30))

    for a_value, rows in result.rk4_tables.items():
        paths.append(_write_rows(output_dir / f"runge_kutta_A{a_value}.csv", rows))

    table_rows: list[dict[str, Any]] = []
    for table_name, rows in result.intermediate_tables.items():
        for row in rows:
            table_rows.append({"tabla": table_name, **row})
    paths.append(_write_rows(output_dir / "tablas_intermedias.csv", table_rows))
    return paths


def _write_key_values(path: Path, values: dict[str, Any]) -> Path:
    rows = [{"metrica": key, "valor": value} for key, value in values.items()]
    return _write_rows(path, rows)


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> Path:
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for row in rows:
        for key in row:
            if key not in names:
                names.append(key)
    return names or ["sin_datos"]

