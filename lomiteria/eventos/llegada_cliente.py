"""Evento llegada_cliente y sorteo de la proxima llegada."""
from __future__ import annotations

import random
from typing import Any

from ..aleatorios.box_muller import EstadoBoxMuller, normal_positiva_con_memoria
from ..modelo.objetos import Cliente
from ..modelo.objetos import SimulationParams
from ..simulacion.operaciones_estado import iniciar_atencion_caja


def generar_proxima_llegada(
    estado_box_muller: EstadoBoxMuller,
    generador: random.Random,
    reloj: float,
    parametros: SimulationParams,
) -> dict[str, Any]:
    """Genera la proxima llegada usando Box-Muller con memoria del segundo valor."""
    sorteo = normal_positiva_con_memoria(
        estado_box_muller,
        generador,
        parametros.llegada_media,
        parametros.llegada_desvio,
    )
    return {
        "rnd_llegada_1": sorteo.rnd1,
        "rnd_llegada_2": sorteo.rnd2,
        "formula_box_muller": sorteo.formula_usada,
        "origen_box_muller": sorteo.origen,
        "tiempo_entre_llegadas": sorteo.valor,
        "proxima_llegada": reloj + sorteo.valor,
    }


def ejecutar_llegada_cliente(estado: Any) -> dict[str, Any]:
    """Procesa la llegada de un cliente nuevo al sistema."""
    valores_sorteados = generar_proxima_llegada(estado.box_muller, estado.generador, estado.reloj, estado.parametros)
    estado.proxima_llegada = valores_sorteados["proxima_llegada"]

    id_cliente = estado.proximo_id_cliente
    estado.proximo_id_cliente += 1
    cliente = Cliente(id=id_cliente, estado="EAC", hora_llegada_negocio=estado.reloj)
    estado.clientes[id_cliente] = cliente

    if estado.caja.estado == "Libre":
        valores_sorteados.update(iniciar_atencion_caja(estado, id_cliente))
        return valores_sorteados

    cliente.hora_inicio_cola_caja = estado.reloj
    estado.cola_caja.append(id_cliente)
    estado.estadisticas.max_cola_caja = max(estado.estadisticas.max_cola_caja, len(estado.cola_caja))
    return valores_sorteados
