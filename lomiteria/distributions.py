from __future__ import annotations

import random
from typing import Any

from .models import SimulationParams
from .randoms import SorteoNormal, normal_positiva, uniforme
from .tables import buscar_salon, buscar_tipo_consumo, buscar_valor_a, rango_permanencia


NOTAS_ORIGEN_RND = [
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


def generar_llegada(generador: random.Random, reloj: float, parametros: SimulationParams) -> dict[str, Any]:
    """Genera la proxima llegada y deja visibles los dos RND de la normal."""
    sorteo: SorteoNormal = normal_positiva(generador, parametros.llegada_media, parametros.llegada_desvio)
    return {
        "rnd_llegada_1": sorteo.rnd1,
        "rnd_llegada_2": sorteo.rnd2,
        "tiempo_entre_llegadas": sorteo.value,
        "proxima_llegada": reloj + sorteo.value,
    }


def generar_atencion_caja(generador: random.Random, reloj: float, parametros: SimulationParams) -> dict[str, Any]:
    """Genera el tiempo de atencion de caja con distribucion uniforme."""
    rnd = generador.random()
    tiempo_atencion = uniforme(rnd, parametros.caja_min, parametros.caja_max)
    return {"rnd_caja": rnd, "tiempo_caja": tiempo_atencion, "fin_caja": reloj + tiempo_atencion}


def generar_tipo_consumo(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Decide si el cliente compra para llevar o consume en el local."""
    rnd = generador.random()
    return {"rnd_tipo_consumo": rnd, "tipo_consumo": buscar_tipo_consumo(rnd, parametros)}


def generar_salon(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Decide el salon elegido para clientes que consumen en el local."""
    rnd = generador.random()
    return {"rnd_salon": rnd, "salon": buscar_salon(rnd, parametros)}


def generar_valor_a(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Sortea el valor A que se usa para buscar el tiempo RK4."""
    rnd = generador.random()
    return {"rnd_a_preparacion": rnd, "a_preparacion": buscar_valor_a(rnd, parametros)}


def generar_preparacion_llevar(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Genera el tiempo de preparacion para pedidos para llevar."""
    rnd = generador.random()
    tiempo_preparacion = uniforme(rnd, parametros.llevar_min, parametros.llevar_max)
    return {"rnd_preparacion_llevar": rnd, "tiempo_preparacion_llevar": tiempo_preparacion}


def generar_permanencia_salon(generador: random.Random, nombre_salon: str, reloj: float, parametros: SimulationParams) -> dict[str, Any]:
    """Genera la permanencia segun salon y franja horaria."""
    rnd = generador.random()
    minimo, maximo = rango_permanencia(nombre_salon, reloj, parametros)
    permanencia = uniforme(rnd, minimo, maximo)
    return {"rnd_permanencia_salon": rnd, "tiempo_permanencia_salon": permanencia}
