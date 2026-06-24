"""Evento fin_permanencia_azul."""
from __future__ import annotations

from typing import Any

from ..simulacion.operaciones_estado import ejecutar_fin_permanencia_salon


def ejecutar_fin_permanencia_azul(estado: Any, id_cliente: int) -> dict[str, Any]:
    """Procesa la salida del cliente del salon azul."""
    return ejecutar_fin_permanencia_salon(estado, "azul", id_cliente)

