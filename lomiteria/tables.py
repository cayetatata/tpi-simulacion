from __future__ import annotations

from typing import Any

from .models import SimulationParams


def lookup_tipo_consumo(rnd: float, params: SimulationParams) -> str:
    return "llevar" if rnd < params.prob_llevar else "local"


def lookup_salon(rnd: float, params: SimulationParams) -> str:
    return "rojo" if rnd < params.prob_rojo else "azul"


def lookup_a_value(rnd: float, params: SimulationParams) -> int:
    idx = min(int(rnd * len(params.a_values)), len(params.a_values) - 1)
    return params.a_values[idx]


def permanence_range(salon: str, reloj_min: float, params: SimulationParams | None = None) -> tuple[float, float]:
    params = params or SimulationParams()
    if reloj_min < 60.0:
        return (params.rojo_11_min, params.rojo_11_max) if salon == "rojo" else (params.azul_11_min, params.azul_11_max)
    if reloj_min < 120.0:
        return (params.rojo_12_min, params.rojo_12_max) if salon == "rojo" else (params.azul_12_min, params.azul_12_max)
    if reloj_min < 180.0:
        return (params.rojo_13_min, params.rojo_13_max) if salon == "rojo" else (params.azul_13_min, params.azul_13_max)
    return (params.rojo_14_min, params.rojo_14_max) if salon == "rojo" else (params.azul_14_min, params.azul_14_max)


def intermediate_tables(params: SimulationParams) -> dict[str, list[dict[str, Any]]]:
    a_span = 1.0 / len(params.a_values)
    return {
        "tipo_consumo": [
            {"desde": 0.0, "hasta": params.prob_llevar, "resultado": "llevar"},
            {"desde": params.prob_llevar, "hasta": 1.0, "resultado": "local"},
        ],
        "salon": [
            {"desde": 0.0, "hasta": params.prob_rojo, "resultado": "rojo"},
            {"desde": params.prob_rojo, "hasta": 1.0, "resultado": "azul"},
        ],
        "a_preparacion": [
            {"desde": round(i * a_span, 6), "hasta": round((i + 1) * a_span, 6), "resultado": value}
            for i, value in enumerate(params.a_values)
        ],
        "permanencia": [
            {"horario": "11 a 12", "reloj": "0 a 60", "rojo": f"U({params.rojo_11_min},{params.rojo_11_max})", "azul": f"U({params.azul_11_min},{params.azul_11_max})"},
            {"horario": "12 a 13", "reloj": "60 a 120", "rojo": f"U({params.rojo_12_min},{params.rojo_12_max})", "azul": f"U({params.azul_12_min},{params.azul_12_max})"},
            {"horario": "13 a 14", "reloj": "120 a 180", "rojo": f"U({params.rojo_13_min},{params.rojo_13_max})", "azul": f"U({params.azul_13_min},{params.azul_13_max})"},
            {"horario": "14 a 15", "reloj": "180 a 240", "rojo": f"U({params.rojo_14_min},{params.rojo_14_max})", "azul": f"U({params.azul_14_min},{params.azul_14_max})"},
        ],
    }
