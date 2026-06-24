"""Evento control_cola_mostrador_15min."""
from __future__ import annotations

from typing import Any


def ejecutar_control_cola_mostrador_15min(estado: Any) -> dict[str, Any]:
    """Registra la cola de mostrador y agenda el siguiente control."""
    estado.controles_15.append(
        {
            "reloj_min": round(estado.reloj, 4),
            "cola_mostrador": len(estado.cola_mostrador),
        }
    )
    estado.proximo_control_15 = estado.reloj + estado.parametros.control_mostrador_interval
    return {}

