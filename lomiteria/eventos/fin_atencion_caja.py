"""Evento fin_atencion_caja y sus sorteos asociados."""
from __future__ import annotations

import random
from typing import Any

from ..aleatorios.distribuciones import siguiente_rnd
from ..aleatorios.tablas_probabilidad import buscar_salon, buscar_tipo_consumo, buscar_valor_a
from ..modelo.objetos import SimulationParams
from ..modelo.objetos import INF
from ..simulacion.operaciones_estado import enviar_a_preparacion_o_cola, iniciar_atencion_caja


def sortear_tipo_consumo(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Decide si el cliente compra para llevar o consume en el local."""
    rnd = siguiente_rnd(generador)
    return {"rnd_tipo_consumo": rnd, "tipo_consumo": buscar_tipo_consumo(rnd, parametros)}


def sortear_salon_elegido(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Decide el salon elegido para clientes que consumen en el local."""
    rnd = siguiente_rnd(generador)
    return {"rnd_salon": rnd, "salon": buscar_salon(rnd, parametros)}


def sortear_valor_a_preparacion(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Sortea el valor A usado luego en el calculo RK4."""
    rnd = siguiente_rnd(generador)
    return {"rnd_a_preparacion": rnd, "a_preparacion": buscar_valor_a(rnd, parametros)}


def ejecutar_fin_atencion_caja(estado: Any) -> dict[str, Any]:
    """Procesa el fin de atencion en caja y reocupa la caja si hay cola."""
    id_cliente = estado.caja.cliente_actual
    valores_sorteados: dict[str, Any] = {}

    if id_cliente is not None and id_cliente in estado.clientes:
        cliente = estado.clientes[id_cliente]
        sorteo_consumo = sortear_tipo_consumo(estado.generador, estado.parametros)
        cliente.tipo_consumo = sorteo_consumo["tipo_consumo"]
        valores_sorteados.update(sorteo_consumo)

        if cliente.tipo_consumo == "local":
            sorteo_salon = sortear_salon_elegido(estado.generador, estado.parametros)
            sorteo_valor_a = sortear_valor_a_preparacion(estado.generador, estado.parametros)
            cliente.salon_elegido = sorteo_salon["salon"]
            cliente.a_preparacion = sorteo_valor_a["a_preparacion"]
            valores_sorteados.update(sorteo_salon)
            valores_sorteados.update(sorteo_valor_a)

        cliente.estado = "EPM"
        cliente.hora_inicio_cola_mostrador = estado.reloj
        enviar_a_preparacion_o_cola(estado, id_cliente, valores_sorteados)

    if estado.cola_caja:
        siguiente_cliente = estado.cola_caja.popleft()
        tiempo_espera = estado.reloj - (estado.clientes[siguiente_cliente].hora_inicio_cola_caja or estado.reloj)
        estado.estadisticas.ac_tiempo_cola_caja += tiempo_espera
        valores_sorteados.update(iniciar_atencion_caja(estado, siguiente_cliente))
        return valores_sorteados

    estado.caja.estado = "Libre"
    estado.caja.cliente_actual = None
    estado.caja.hora_inicio_ocupacion = None
    estado.fin_caja = INF
    return valores_sorteados
