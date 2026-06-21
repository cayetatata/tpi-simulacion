from __future__ import annotations

from typing import Any


def calculate_metrics(state: Any) -> dict[str, float]:
    final_clock = max(state.reloj, 1e-9)
    prep_total = sum(prep.ac_tiempo_ocupado for prep in state.preparadores)
    local_waits = state.stats.ct_esperaron_rojo_lleno + state.stats.ct_esperaron_azul_lleno
    return {
        "tiempo_promedio_permanencia_negocio": _safe_div(state.stats.ac_tiempo_permanencia_negocio, state.stats.ct_clientes_finalizados),
        "tiempo_promedio_cola_caja": _safe_div(state.stats.ac_tiempo_cola_caja, state.stats.ct_clientes_pasan_por_caja),
        "tiempo_promedio_cola_mostrador": _safe_div(state.stats.ac_tiempo_cola_mostrador, state.stats.ct_clientes_pasan_por_mostrador),
        "porcentaje_ocupacion_caja": state.caja.ac_tiempo_ocupada / final_clock * 100.0,
        "porcentaje_ocupacion_preparadores": prep_total / (len(state.preparadores) * final_clock) * 100.0,
        "max_cola_caja": float(state.stats.max_cola_caja),
        "max_cola_mostrador": float(state.stats.max_cola_mostrador),
        "clientes_esperaron_salon_rojo_lleno": float(state.stats.ct_esperaron_rojo_lleno),
        "clientes_esperaron_salon_azul_lleno": float(state.stats.ct_esperaron_azul_lleno),
        "clientes_esperaron_salon_lleno_total": float(local_waits),
    }


def metric_definitions() -> list[dict[str, Any]]:
    return [
        {
            "metrica": "tiempo_promedio_permanencia_negocio",
            "titulo": "Tiempo promedio de permanencia en el negocio",
            "tipo": "Pedida por el enunciado",
            "formula": "ac_tiempo_permanencia_negocio / ct_clientes_finalizados",
            "variables": ["ac_tiempo_permanencia_negocio", "ct_clientes_finalizados"],
            "enunciado": "Tiempo de permanencia en el negocio.",
        },
        {
            "metrica": "tiempo_promedio_cola_caja",
            "titulo": "Tiempo promedio en cola de caja",
            "tipo": "Pedida por el enunciado",
            "formula": "ac_tiempo_cola_caja / ct_clientes_pasan_por_caja",
            "variables": ["ac_tiempo_cola_caja", "ct_clientes_pasan_por_caja"],
            "enunciado": "Tiempo en cola en la caja.",
        },
        {
            "metrica": "control_15_cola_mostrador",
            "titulo": "Control cada 15 minutos: cola mostrador",
            "tipo": "Pedida por el enunciado",
            "formula": "lectura directa de len(cola_mostrador) en cada evento de control",
            "variables": ["control_15_min", "cola_mostrador"],
            "enunciado": "Cada 15 minutos, cantidad de gente en cola frente al mostrador.",
        },
        {
            "metrica": "control_30_ocupacion_salones",
            "titulo": "Control cada 30 minutos: ocupacion de salones",
            "tipo": "Pedida por el enunciado",
            "formula": "lectura directa de rojo_ocupacion y azul_ocupacion en cada evento de control",
            "variables": ["control_30_min", "rojo_ocupacion", "azul_ocupacion"],
            "enunciado": "Cada 30 minutos, personas en Salon Rojo y Salon Azul.",
        },
        {
            "metrica": "tiempo_promedio_cola_mostrador",
            "titulo": "Tiempo promedio en cola frente al mostrador",
            "tipo": "Metrica adicional",
            "formula": "ac_tiempo_cola_mostrador / ct_clientes_pasan_por_mostrador",
            "variables": ["ac_tiempo_cola_mostrador", "ct_clientes_pasan_por_mostrador"],
            "enunciado": "Metrica adicional: demora previa a preparacion.",
        },
        {
            "metrica": "porcentaje_ocupacion_caja",
            "titulo": "Porcentaje de ocupacion de caja",
            "tipo": "Metrica adicional",
            "formula": "ac_tiempo_ocupada_caja / reloj_final * 100",
            "variables": ["caja_ac_tiempo_ocupada", "reloj_min"],
            "enunciado": "Metrica adicional: utilizacion del servidor caja.",
        },
        {
            "metrica": "porcentaje_ocupacion_preparadores",
            "titulo": "Porcentaje de ocupacion de preparadores",
            "tipo": "Metrica adicional",
            "formula": "sum(ac_tiempo_ocupado_preparador_i) / (preparadores * reloj_final) * 100",
            "variables": ["prep_i_ac_ocupado", "preparadores", "reloj_min"],
            "enunciado": "Metrica adicional: utilizacion del mostrador de preparacion.",
        },
        {
            "metrica": "max_cola_caja",
            "titulo": "Maxima cola de caja",
            "tipo": "Metrica adicional",
            "formula": "max(len(cola_caja)) observado en el vector",
            "variables": ["max_cola_caja"],
            "enunciado": "Metrica adicional: pico de congestion en caja.",
        },
        {
            "metrica": "max_cola_mostrador",
            "titulo": "Maxima cola frente al mostrador",
            "tipo": "Metrica adicional",
            "formula": "max(len(cola_mostrador)) observado en el vector",
            "variables": ["max_cola_mostrador"],
            "enunciado": "Metrica adicional y apoyo al control cada 15 minutos.",
        },
        {
            "metrica": "clientes_esperaron_salon_rojo_lleno",
            "titulo": "Clientes que esperaron por salon rojo lleno",
            "tipo": "Metrica adicional",
            "formula": "conteo de ingresos a cola del salon rojo por capacidad completa",
            "variables": ["ct_esperaron_rojo_lleno", "rojo_ocupacion", "rojo_capacidad"],
            "enunciado": "Metrica adicional vinculada a capacidad del salon rojo.",
        },
        {
            "metrica": "clientes_esperaron_salon_azul_lleno",
            "titulo": "Clientes que esperaron por salon azul lleno",
            "tipo": "Metrica adicional",
            "formula": "conteo de ingresos a cola del salon azul por capacidad completa",
            "variables": ["ct_esperaron_azul_lleno", "azul_ocupacion", "azul_capacidad"],
            "enunciado": "Metrica adicional vinculada a capacidad del salon azul.",
        },
        {
            "metrica": "clientes_esperaron_salon_lleno_total",
            "titulo": "Clientes que esperaron por algun salon lleno",
            "tipo": "Metrica adicional",
            "formula": "ct_esperaron_rojo_lleno + ct_esperaron_azul_lleno",
            "variables": ["ct_esperaron_rojo_lleno", "ct_esperaron_azul_lleno"],
            "enunciado": "Metrica adicional: total de bloqueos por capacidad de salones.",
        },
    ]


def _safe_div(numerator: float, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
