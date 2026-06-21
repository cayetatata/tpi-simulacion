from __future__ import annotations

from .models import SimulationParams


def build_rk4_tables(params: SimulationParams) -> tuple[dict[int, list[dict[str, float]]], dict[int, float]]:
    tables: dict[int, list[dict[str, float]]] = {}
    ready_times: dict[int, float] = {}

    for a_value in params.a_values:
        t = 0.0
        l_value = float(a_value)
        rows: list[dict[str, float]] = []

        while l_value <= params.rk_limit_l:
            k1 = 6.0 + 3.0 * a_value
            k2 = 6.0 + 3.0 * a_value
            k3 = 6.0 + 3.0 * a_value
            k4 = 6.0 + 3.0 * a_value
            next_l = l_value + params.rk_h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            next_t = t + params.rk_h

            rows.append(
                {
                    "t": round(t, 6),
                    "L": round(next_l, 6),
                    "k1": round(k1, 6),
                    "k2": round(k2, 6),
                    "k3": round(k3, 6),
                    "k4": round(k4, 6),
                    "L(i+1)": round(next_l, 6),
                    "t(i+1)": round(next_t, 6),
                    "A": float(a_value),
                    "tiempo_min": round(next_t * params.rk_minutes_per_unit, 6),
                }
            )
            t = next_t
            l_value = next_l

        tables[a_value] = rows
        ready_times[a_value] = rows[-1]["tiempo_min"]

    return tables, ready_times
