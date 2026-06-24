"""Evento fin_permanencia_rojo."""
from __future__ import annotations

from typing import Any

from ..simulacion.operaciones_estado import ejecutar_fin_permanencia_salon


def ejecutar_fin_permanencia_rojo(estado: Any, id_cliente: int) -> dict[str, Any]:
    """Procesa la salida del cliente del salon rojo."""
    return ejecutar_fin_permanencia_salon(estado, "rojo", id_cliente)

