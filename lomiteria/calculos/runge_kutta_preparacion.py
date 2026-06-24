"""Calculo RK4 del tiempo de preparacion para pedidos en local."""
from __future__ import annotations

from ..modelo.objetos import SimulationParams


def construir_tablas_rk4(parametros: SimulationParams) -> tuple[dict[int, list[dict[str, float]]], dict[int, float]]:
    """Calcula las tablas RK4 para cada valor posible de A."""
    tablas: dict[int, list[dict[str, float]]] = {}
    tiempos_listos: dict[int, float] = {}

    for valor_a in parametros.a_values:
        t = 0.0
        valor_l = float(valor_a)
        filas: list[dict[str, float]] = []

        while valor_l <= parametros.rk_limit_l:
            k1 = 6.0 + 3.0 * valor_a
            k2 = 6.0 + 3.0 * valor_a
            k3 = 6.0 + 3.0 * valor_a
            k4 = 6.0 + 3.0 * valor_a
            proximo_l = valor_l + parametros.rk_h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            proximo_t = t + parametros.rk_h

            filas.append(
                {
                    "t": round(t, 6),
                    "L": round(proximo_l, 6),
                    "k1": round(k1, 6),
                    "k2": round(k2, 6),
                    "k3": round(k3, 6),
                    "k4": round(k4, 6),
                    "L(i+1)": round(proximo_l, 6),
                    "t(i+1)": round(proximo_t, 6),
                    "A": float(valor_a),
                    # El tiempo listo se lee en el t de la fila donde L(i+1)
                    # supera el limite, igual que en el planteo de planilla.
                    "tiempo_min": round(t * parametros.rk_minutes_per_unit, 6),
                }
            )
            t = proximo_t
            valor_l = proximo_l

        tablas[valor_a] = filas
        tiempos_listos[valor_a] = filas[-1]["tiempo_min"]

    return tablas, tiempos_listos
