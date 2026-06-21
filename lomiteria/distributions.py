from __future__ import annotations

import random
from typing import Any

from .models import SimulationParams
from .randoms import NormalDraw, normal_positive, uniform
from .tables import lookup_a_value, lookup_salon, lookup_tipo_consumo, permanence_range


RANDOM_SOURCE_NOTES = [
    {
        "variable": "Llegada de clientes",
        "rnd": "rnd_llegada_1, rnd_llegada_2",
        "generacion": "Normal por Box-Muller con rechazo si el tiempo generado es menor o igual a cero.",
        "formula": "tiempo = media + desvio * sqrt(-2 ln(RND1)) * cos(2*pi*RND2)",
    },
    {
        "variable": "Atencion en caja",
        "rnd": "rnd_caja",
        "generacion": "Uniforme continua entre caja_min y caja_max.",
        "formula": "tiempo = minimo + RND * (maximo - minimo)",
    },
    {
        "variable": "Tipo de consumo",
        "rnd": "rnd_tipo_consumo",
        "generacion": "Busqueda en tabla intermedia: llevar hasta prob_llevar, local en el resto.",
        "formula": "si RND < prob_llevar => llevar; si no => local",
    },
    {
        "variable": "Salon elegido",
        "rnd": "rnd_salon",
        "generacion": "Busqueda en tabla intermedia: rojo hasta prob_rojo, azul en el resto.",
        "formula": "si RND < prob_rojo => rojo; si no => azul",
    },
    {
        "variable": "Valor A de preparacion local",
        "rnd": "rnd_a_preparacion",
        "generacion": "Uniforme discreta sobre los valores configurados de A.",
        "formula": "intervalos iguales de amplitud 1 / cantidad_de_valores_A",
    },
    {
        "variable": "Preparacion para llevar",
        "rnd": "rnd_preparacion_llevar",
        "generacion": "Uniforme continua entre llevar_min y llevar_max.",
        "formula": "tiempo = minimo + RND * (maximo - minimo)",
    },
    {
        "variable": "Permanencia en salon",
        "rnd": "rnd_permanencia_salon",
        "generacion": "Uniforme continua. El rango depende del salon elegido y de la hora.",
        "formula": "tiempo = minimo_horario + RND * (maximo_horario - minimo_horario)",
    },
]


def draw_arrival(rng: random.Random, reloj: float, params: SimulationParams) -> dict[str, Any]:
    draw: NormalDraw = normal_positive(rng, params.llegada_media, params.llegada_desvio)
    return {
        "rnd_llegada_1": draw.rnd1,
        "rnd_llegada_2": draw.rnd2,
        "tiempo_entre_llegadas": draw.value,
        "proxima_llegada": reloj + draw.value,
    }


def draw_cashier_service(rng: random.Random, reloj: float, params: SimulationParams) -> dict[str, Any]:
    rnd = rng.random()
    service_time = uniform(rnd, params.caja_min, params.caja_max)
    return {"rnd_caja": rnd, "tiempo_caja": service_time, "fin_caja": reloj + service_time}


def draw_consumption_type(rng: random.Random, params: SimulationParams) -> dict[str, Any]:
    rnd = rng.random()
    return {"rnd_tipo_consumo": rnd, "tipo_consumo": lookup_tipo_consumo(rnd, params)}


def draw_salon_choice(rng: random.Random, params: SimulationParams) -> dict[str, Any]:
    rnd = rng.random()
    return {"rnd_salon": rnd, "salon": lookup_salon(rnd, params)}


def draw_a_preparation(rng: random.Random, params: SimulationParams) -> dict[str, Any]:
    rnd = rng.random()
    return {"rnd_a_preparacion": rnd, "a_preparacion": lookup_a_value(rnd, params)}


def draw_takeout_preparation(rng: random.Random, params: SimulationParams) -> dict[str, Any]:
    rnd = rng.random()
    prep_time = uniform(rnd, params.llevar_min, params.llevar_max)
    return {"rnd_preparacion_llevar": rnd, "tiempo_preparacion_llevar": prep_time}


def draw_salon_stay(rng: random.Random, salon_name: str, reloj: float, params: SimulationParams) -> dict[str, Any]:
    rnd = rng.random()
    low, high = permanence_range(salon_name, reloj, params)
    stay = uniform(rnd, low, high)
    return {"rnd_permanencia_salon": rnd, "tiempo_permanencia_salon": stay}
