"""Funciones base para sacar RND y aplicar formulas de distribucion."""
from __future__ import annotations

import random


def siguiente_rnd(generador: random.Random) -> float:
    """Devuelve un RND uniforme de Python en el intervalo [0.0, 1.0)."""
    return generador.random()

def uniforme(rnd: float, minimo: float, maximo: float) -> float:
    """Formula de distribucion uniforme: minimo + RND * (maximo - minimo)."""
    return minimo + rnd * (maximo - minimo)
