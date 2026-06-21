from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalDraw:
    rnd1: float
    rnd2: float
    value: float


def uniform(rnd: float, low: float, high: float) -> float:
    return low + rnd * (high - low)


def normal_positive(rng: random.Random, mean: float, deviation: float) -> NormalDraw:
    while True:
        rnd1 = max(rng.random(), 1e-12)
        rnd2 = rng.random()
        z = math.sqrt(-2.0 * math.log(rnd1)) * math.cos(2.0 * math.pi * rnd2)
        value = mean + deviation * z
        if value > 0:
            return NormalDraw(rnd1=rnd1, rnd2=rnd2, value=value)

