"""Calculo de metricas finales a partir de los acumuladores."""
from __future__ import annotations

from typing import Any


def calcular_metricas(estado: Any) -> dict[str, float]:
    """Calcula los indicadores finales a partir de acumuladores del vector."""
    reloj_final = max(estado.reloj, 1e-9)
    ocupacion_total_preparadores = sum(preparador.ac_tiempo_ocupado for preparador in estado.preparadores)
    esperas_por_salon_lleno = estado.estadisticas.ct_esperaron_rojo_lleno + estado.estadisticas.ct_esperaron_azul_lleno
    return {
        "tiempo_promedio_permanencia_negocio": _dividir_si_hay_datos(estado.estadisticas.ac_tiempo_permanencia_negocio, estado.estadisticas.ct_clientes_finalizados),
        "tiempo_promedio_cola_caja": _dividir_si_hay_datos(estado.estadisticas.ac_tiempo_cola_caja, estado.estadisticas.ct_clientes_pasan_por_caja),
        "tiempo_promedio_cola_mostrador": _dividir_si_hay_datos(estado.estadisticas.ac_tiempo_cola_mostrador, estado.estadisticas.ct_clientes_pasan_por_mostrador),
        "porcentaje_ocupacion_caja": estado.caja.ac_tiempo_ocupada / reloj_final * 100.0,
        "porcentaje_ocupacion_preparadores": ocupacion_total_preparadores / (len(estado.preparadores) * reloj_final) * 100.0,
        "clientes_esperaron_salon_lleno_total": float(esperas_por_salon_lleno),
    }
def _dividir_si_hay_datos(numerador: float, denominador: int) -> float:
    return numerador / denominador if denominador else 0.0
