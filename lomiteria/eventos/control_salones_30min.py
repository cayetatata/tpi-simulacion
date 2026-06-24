"""Evento control_salones_30min."""
from __future__ import annotations

from typing import Any


def ejecutar_control_salones_30min(estado: Any) -> dict[str, Any]:
    """Registra ocupacion de salones y agenda el siguiente control."""
    estado.controles_30.append(
        {
            "reloj_min": round(estado.reloj, 4),
            "ocupacion_rojo": estado.rojo.ocupacion,
            "ocupacion_azul": estado.azul.ocupacion,
        }
    )
    estado.proximo_control_30 = estado.reloj + estado.parametros.control_salones_interval
    return {}

