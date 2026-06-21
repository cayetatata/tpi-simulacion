from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SorteoNormal:
    rnd1: float
    rnd2: float
    value: float


def uniforme(rnd: float, minimo: float, maximo: float) -> float:
    """Formula de distribucion uniforme: minimo + RND * (maximo - minimo)."""
    return minimo + rnd * (maximo - minimo)


def normal_positiva(generador: random.Random, media: float, desviacion: float) -> SorteoNormal:
    """Normal por Box-Muller. Repite el sorteo si el tiempo resulta negativo."""
    while True:
        rnd1 = max(generador.random(), 1e-12)
        rnd2 = generador.random()
        z = math.sqrt(-2.0 * math.log(rnd1)) * math.cos(2.0 * math.pi * rnd2)
        valor = media + desviacion * z
        if valor > 0:
            return SorteoNormal(rnd1=rnd1, rnd2=rnd2, value=valor)


# Alias conservados para tests/imports existentes.
NormalDraw = SorteoNormal
uniform = uniforme
normal_positive = normal_positiva
