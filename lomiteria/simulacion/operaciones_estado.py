"""Subpasos de la simulacion que actualizan el estado entre eventos principales."""
from __future__ import annotations

import heapq
import random
from typing import Any

from ..aleatorios.distribuciones import siguiente_rnd, uniforme
from ..aleatorios.tablas_probabilidad import rango_permanencia
from ..modelo.objetos import INF, Preparador, Salon, SimulationParams


def sortear_fin_atencion_caja(generador: random.Random, reloj: float, parametros: SimulationParams) -> dict[str, Any]:
    """Sortea el tiempo de caja y deja programado su fin."""
    rnd = siguiente_rnd(generador)
    tiempo_atencion = uniforme(rnd, parametros.caja_min, parametros.caja_max)
    return {"rnd_caja": rnd, "tiempo_caja": tiempo_atencion, "fin_caja": reloj + tiempo_atencion}


def sortear_tiempo_preparacion_llevar(generador: random.Random, parametros: SimulationParams) -> dict[str, Any]:
    """Sortea el tiempo de preparacion para pedidos para llevar."""
    rnd = siguiente_rnd(generador)
    tiempo_preparacion = uniforme(rnd, parametros.llevar_min, parametros.llevar_max)
    return {"rnd_preparacion_llevar": rnd, "tiempo_preparacion_llevar": tiempo_preparacion}


def sortear_tiempo_permanencia_salon(
    generador: random.Random,
    nombre_salon: str,
    reloj: float,
    parametros: SimulationParams,
) -> dict[str, Any]:
    """Sortea la permanencia del cliente segun salon y franja horaria."""
    rnd = siguiente_rnd(generador)
    minimo, maximo = rango_permanencia(nombre_salon, reloj, parametros)
    permanencia = uniforme(rnd, minimo, maximo)
    return {"rnd_permanencia_salon": rnd, "tiempo_permanencia_salon": permanencia}


def iniciar_atencion_caja(estado: Any, id_cliente: int) -> dict[str, Any]:
    """Pasa un cliente a la caja y programa el fin de atencion."""
    cliente = estado.clientes[id_cliente]
    cliente.estado = "SAC"
    estado.caja.estado = "Ocupada"
    estado.caja.cliente_actual = id_cliente
    estado.caja.hora_inicio_ocupacion = estado.reloj
    estado.estadisticas.ct_clientes_pasan_por_caja += 1

    valores_sorteados = sortear_fin_atencion_caja(estado.generador, estado.reloj, estado.parametros)
    estado.fin_caja = valores_sorteados["fin_caja"]
    return valores_sorteados


def enviar_a_preparacion_o_cola(estado: Any, id_cliente: int, valores_sorteados: dict[str, Any]) -> None:
    """Manda el cliente a un preparador libre o a la cola de mostrador."""
    preparador_libre = next((preparador for preparador in estado.preparadores if preparador.estado == "Libre"), None)
    if preparador_libre is None:
        estado.cola_mostrador.append(id_cliente)
        estado.estadisticas.max_cola_mostrador = max(estado.estadisticas.max_cola_mostrador, len(estado.cola_mostrador))
        return
    valores_sorteados.update(iniciar_preparacion(estado, preparador_libre, id_cliente))


def iniciar_preparacion(estado: Any, preparador: Preparador, id_cliente: int) -> dict[str, Any]:
    """Ocupa un preparador y deja programado el fin de preparacion."""
    cliente = estado.clientes[id_cliente]
    tiempo_espera = estado.reloj - (cliente.hora_inicio_cola_mostrador or estado.reloj)
    estado.estadisticas.ac_tiempo_cola_mostrador += tiempo_espera
    estado.estadisticas.ct_clientes_pasan_por_mostrador += 1

    preparador.estado = "Ocupado"
    preparador.cliente_actual = id_cliente
    preparador.hora_inicio_ocupacion = estado.reloj

    valores_sorteados: dict[str, Any] = {}
    if cliente.tipo_consumo == "local":
        assert cliente.a_preparacion is not None
        tiempo_preparacion = estado.tiempos_rk[cliente.a_preparacion]
        cliente.tiempo_preparacion = tiempo_preparacion
        valores_sorteados["tiempo_preparacion_local"] = tiempo_preparacion
    else:
        valores_sorteados.update(sortear_tiempo_preparacion_llevar(estado.generador, estado.parametros))
        tiempo_preparacion = valores_sorteados["tiempo_preparacion_llevar"]
        cliente.tiempo_preparacion = tiempo_preparacion

    preparador.fin_preparacion_programado = estado.reloj + tiempo_preparacion
    cliente.hora_fin_programada = preparador.fin_preparacion_programado
    valores_sorteados[f"fin_preparacion_{preparador.id}"] = preparador.fin_preparacion_programado
    return valores_sorteados


def entrar_o_esperar_salon(estado: Any, id_cliente: int) -> dict[str, Any]:
    """Hace entrar al cliente a su salon o lo deja en la cola de espera de ese salon."""
    cliente = estado.clientes[id_cliente]
    salon = obtener_salon(estado, cliente.salon_elegido)
    if salon.ocupacion < salon.capacidad:
        return iniciar_permanencia_salon(estado, id_cliente, salon.nombre)

    cliente.estado = "EASR" if salon.nombre == "rojo" else "EASA"
    cliente.hora_inicio_cola_salon = estado.reloj
    salon.cola_entrada.append(id_cliente)
    salon.clientes_que_esperaron_por_capacidad += 1
    if salon.nombre == "rojo":
        estado.estadisticas.ct_esperaron_rojo_lleno += 1
    else:
        estado.estadisticas.ct_esperaron_azul_lleno += 1
    return {}


def iniciar_permanencia_salon(estado: Any, id_cliente: int, nombre_salon: str) -> dict[str, Any]:
    """Hace entrar al cliente al salon y agenda su salida futura."""
    cliente = estado.clientes[id_cliente]
    salon = obtener_salon(estado, nombre_salon)

    salon.ocupacion += 1
    salon.max_ocupacion = max(salon.max_ocupacion, salon.ocupacion)
    cliente.estado = "PSR" if nombre_salon == "rojo" else "PSA"
    cliente.hora_inicio_permanencia = estado.reloj

    valores_sorteados = sortear_tiempo_permanencia_salon(estado.generador, nombre_salon, estado.reloj, estado.parametros)
    tiempo_permanencia = valores_sorteados["tiempo_permanencia_salon"]
    cliente.hora_fin_programada = estado.reloj + tiempo_permanencia
    heapq.heappush(salon.salidas_programadas, (cliente.hora_fin_programada, id_cliente))
    return valores_sorteados


def ejecutar_fin_permanencia_salon(estado: Any, nombre_salon: str, id_cliente: int) -> dict[str, Any]:
    """Libera lugar en el salon y deja entrar al siguiente, si lo hubiera."""
    salon = obtener_salon(estado, nombre_salon)
    if id_cliente in estado.clientes:
        finalizar_cliente(estado, id_cliente)
    salon.ocupacion = max(0, salon.ocupacion - 1)

    valores_sorteados: dict[str, Any] = {}
    if salon.cola_entrada:
        siguiente_cliente = salon.cola_entrada.popleft()
        valores_sorteados.update(iniciar_permanencia_salon(estado, siguiente_cliente, nombre_salon))
    return valores_sorteados


def finalizar_cliente(estado: Any, id_cliente: int) -> None:
    """Retira el cliente del sistema y acumula su permanencia total."""
    cliente = estado.clientes.pop(id_cliente, None)
    if cliente is None:
        return
    estado.estadisticas.ac_tiempo_permanencia_negocio += estado.reloj - cliente.hora_llegada_negocio
    estado.estadisticas.ct_clientes_finalizados += 1


def obtener_salon(estado: Any, nombre_salon: str) -> Salon:
    """Devuelve el salon rojo o azul segun el nombre recibido."""
    assert estado.rojo is not None and estado.azul is not None
    return estado.rojo if nombre_salon == "rojo" else estado.azul

