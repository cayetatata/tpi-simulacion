"""Tablas intermedias y reglas de decision por RND."""
from __future__ import annotations

from typing import Any

from ..modelo.objetos import SimulationParams


def buscar_tipo_consumo(rnd: float, parametros: SimulationParams) -> str:
    return "llevar" if rnd < parametros.prob_llevar else "local"


def buscar_salon(rnd: float, parametros: SimulationParams) -> str:
    return "rojo" if rnd < parametros.prob_rojo else "azul"


def buscar_valor_a(rnd: float, parametros: SimulationParams) -> int:
    indice = min(int(rnd * len(parametros.a_values)), len(parametros.a_values) - 1)
    return parametros.a_values[indice]


def rango_permanencia(salon: str, reloj_min: float, parametros: SimulationParams | None = None) -> tuple[float, float]:
    parametros = parametros or SimulationParams()
    if reloj_min < 60.0:
        return (parametros.rojo_11_min, parametros.rojo_11_max) if salon == "rojo" else (parametros.azul_11_min, parametros.azul_11_max)
    if reloj_min < 120.0:
        return (parametros.rojo_12_min, parametros.rojo_12_max) if salon == "rojo" else (parametros.azul_12_min, parametros.azul_12_max)
    if reloj_min < 180.0:
        return (parametros.rojo_13_min, parametros.rojo_13_max) if salon == "rojo" else (parametros.azul_13_min, parametros.azul_13_max)
    return (parametros.rojo_14_min, parametros.rojo_14_max) if salon == "rojo" else (parametros.azul_14_min, parametros.azul_14_max)




"""Las usamos para mostrarlas en la interfaces."""


def tablas_intermedias(parametros: SimulationParams) -> dict[str, list[dict[str, Any]]]:
    amplitud_a = 1.0 / len(parametros.a_values)
    return {
        "tipo_consumo": [
            {"desde": 0.0, "hasta": parametros.prob_llevar, "resultado": "llevar"},
            {"desde": parametros.prob_llevar, "hasta": 1.0, "resultado": "local"},
        ],
        "salon": [
            {"desde": 0.0, "hasta": parametros.prob_rojo, "resultado": "rojo"},
            {"desde": parametros.prob_rojo, "hasta": 1.0, "resultado": "azul"},
        ],
        "a_preparacion": [
            {"desde": round(i * amplitud_a, 6), "hasta": round((i + 1) * amplitud_a, 6), "resultado": valor}
            for i, valor in enumerate(parametros.a_values)
        ],
        "permanencia": [
            {"horario": "11 a 12", "reloj": "0 a 60", "rojo": f"U({parametros.rojo_11_min},{parametros.rojo_11_max})", "azul": f"U({parametros.azul_11_min},{parametros.azul_11_max})"},
            {"horario": "12 a 13", "reloj": "60 a 120", "rojo": f"U({parametros.rojo_12_min},{parametros.rojo_12_max})", "azul": f"U({parametros.azul_12_min},{parametros.azul_12_max})"},
            {"horario": "13 a 14", "reloj": "120 a 180", "rojo": f"U({parametros.rojo_13_min},{parametros.rojo_13_max})", "azul": f"U({parametros.azul_13_min},{parametros.azul_13_max})"},
            {"horario": "14 a 15", "reloj": "180 a 240", "rojo": f"U({parametros.rojo_14_min},{parametros.rojo_14_max})", "azul": f"U({parametros.azul_14_min},{parametros.azul_14_max})"},
        ],
    }
