"""Armado de cada fila del vector de estado."""
from __future__ import annotations

import heapq
from typing import Any

from ..modelo.objetos import INF, StateRow


COLUMNAS_EVENTOS = [
    "rnd_llegada_1",
    "rnd_llegada_2",
    "formula_box_muller",
    "origen_box_muller",
    "tiempo_entre_llegadas",
    "proxima_llegada",
    "rnd_caja",
    "tiempo_caja",
    "fin_caja",
    "rnd_tipo_consumo",
    "tipo_consumo",
    "rnd_salon",
    "salon",
    "rnd_a_preparacion",
    "a_preparacion",
    "tiempo_preparacion_local",
    "rnd_preparacion_llevar",
    "tiempo_preparacion_llevar",
    "fin_preparacion_1",
    "fin_preparacion_2",
    "fin_preparacion_3",
    "rnd_permanencia_salon",
    "tiempo_permanencia_salon",
    "fin_permanencia_rojo",
    "fin_permanencia_azul",
    "proximo_control_15",
    "proximo_control_30",
]


def armar_fila_vector(estado: Any, evento: str, valores_aleatorios: dict[str, Any], omitir_temporales: bool = False) -> StateRow:
    """Arma una fila completa del vector como si fuera una fila de Excel."""
    eventos = {columna: "" for columna in COLUMNAS_EVENTOS}
    eventos.update(valores_eventos_programados(estado))
    eventos.update({clave: redondear(valor) for clave, valor in valores_aleatorios.items() if clave in COLUMNAS_EVENTOS})

    return StateRow(
        nro_evento=estado.nro_evento,
        evento=evento,
        reloj_min=redondear(estado.reloj),
        hora_real=hora_reloj(estado.reloj),
        eventos=eventos,
        objetos_permanentes=valores_objetos_permanentes(estado),
        variables_estadisticas=valores_variables_estadisticas(estado),
        objetos_temporales={} if omitir_temporales else valores_objetos_temporales(estado),
    )


def valores_eventos_programados(estado: Any) -> dict[str, Any]:
    valores = {
        "proxima_llegada": tiempo_evento(estado.proxima_llegada),
        "fin_caja": tiempo_evento(estado.fin_caja),
        "proximo_control_15": tiempo_evento(estado.proximo_control_15),
        "proximo_control_30": tiempo_evento(estado.proximo_control_30),
    }
    for preparador in estado.preparadores:
        valores[f"fin_preparacion_{preparador.id}"] = tiempo_evento(preparador.fin_preparacion_programado)
    valores["fin_permanencia_rojo"] = tiempo_evento(proxima_salida_salon(estado, "rojo")[0])
    valores["fin_permanencia_azul"] = tiempo_evento(proxima_salida_salon(estado, "azul")[0])
    return valores


def valores_objetos_permanentes(estado: Any) -> dict[str, Any]:
    valores: dict[str, Any] = {
        "estado_caja": estado.caja.estado,
        "cliente_caja": estado.caja.cliente_actual or "",
        "cola_caja": len(estado.cola_caja),
        "cola_mostrador": len(estado.cola_mostrador),
        "ocupacion_rojo": estado.rojo.ocupacion,
        "cola_rojo": len(estado.rojo.cola_entrada),
        "ocupacion_azul": estado.azul.ocupacion,
        "cola_azul": len(estado.azul.cola_entrada),
    }
    for preparador in estado.preparadores:
        valores[f"estado_preparador_{preparador.id}"] = preparador.estado
        valores[f"cliente_preparador_{preparador.id}"] = preparador.cliente_actual or ""
    return valores


def valores_variables_estadisticas(estado: Any) -> dict[str, Any]:
    valores: dict[str, Any] = {
        "ac_tiempo_permanencia_negocio": redondear(estado.estadisticas.ac_tiempo_permanencia_negocio),
        "ct_clientes_finalizados": estado.estadisticas.ct_clientes_finalizados,
        "ac_tiempo_cola_caja": redondear(estado.estadisticas.ac_tiempo_cola_caja),
        "ct_clientes_pasan_por_caja": estado.estadisticas.ct_clientes_pasan_por_caja,
        "ac_tiempo_cola_mostrador": redondear(estado.estadisticas.ac_tiempo_cola_mostrador),
        "ct_clientes_pasan_por_mostrador": estado.estadisticas.ct_clientes_pasan_por_mostrador,
        "ac_ocupacion_caja": redondear(estado.caja.ac_tiempo_ocupada),
        "ac_ocupacion_rojo_tiempo_persona": redondear(estado.rojo.ac_ocupacion_tiempo_persona),
        "ac_ocupacion_azul_tiempo_persona": redondear(estado.azul.ac_ocupacion_tiempo_persona),
        "max_cola_caja": estado.estadisticas.max_cola_caja,
        "max_cola_mostrador": estado.estadisticas.max_cola_mostrador,
        "max_ocupacion_rojo": estado.rojo.max_ocupacion,
        "max_ocupacion_azul": estado.azul.max_ocupacion,
        "ct_esperaron_rojo_lleno": estado.estadisticas.ct_esperaron_rojo_lleno,
        "ct_esperaron_azul_lleno": estado.estadisticas.ct_esperaron_azul_lleno,
    }
    for preparador in estado.preparadores:
        valores[f"ac_ocupacion_preparador_{preparador.id}"] = redondear(preparador.ac_tiempo_ocupado)
    return valores


def valores_objetos_temporales(estado: Any) -> dict[str, Any]:
    valores: dict[str, Any] = {}
    for cliente in sorted(estado.clientes.values(), key=lambda c: c.id):
        prefijo = f"cliente_{cliente.id}"
        valores[f"{prefijo}_estado"] = cliente.estado
        valores[f"{prefijo}_hora_llegada"] = redondear(cliente.hora_llegada_negocio)
        valores[f"{prefijo}_tipo_consumo"] = cliente.tipo_consumo
        valores[f"{prefijo}_salon"] = cliente.salon_elegido
        valores[f"{prefijo}_hora_inicio_cola_caja"] = blanco_o_redondeado(cliente.hora_inicio_cola_caja)
        valores[f"{prefijo}_hora_inicio_cola_mostrador"] = blanco_o_redondeado(cliente.hora_inicio_cola_mostrador)
        valores[f"{prefijo}_hora_inicio_cola_salon"] = blanco_o_redondeado(cliente.hora_inicio_cola_salon)
        valores[f"{prefijo}_hora_inicio_permanencia"] = blanco_o_redondeado(cliente.hora_inicio_permanencia)
        valores[f"{prefijo}_fin_programado"] = blanco_o_redondeado(cliente.hora_fin_programada)
    return valores


def proxima_salida_salon(estado: Any, nombre_salon: str) -> tuple[float, int | None]:
    """Lee la proxima salida real del salon sin recorrer todos los clientes."""
    estado_buscado = "PSR" if nombre_salon == "rojo" else "PSA"
    salon = estado.rojo if nombre_salon == "rojo" else estado.azul
    while salon.salidas_programadas:
        tiempo_salida, id_cliente = salon.salidas_programadas[0]
        cliente = estado.clientes.get(id_cliente)
        if cliente is not None and cliente.estado == estado_buscado and cliente.hora_fin_programada == tiempo_salida:
            return tiempo_salida, id_cliente
        heapq.heappop(salon.salidas_programadas)
    return INF, None


def hora_reloj(reloj_min: float) -> str:
    total = 11 * 60 + int(round(reloj_min))
    return f"{total // 60:02d}:{total % 60:02d}"


def tiempo_evento(valor: float) -> float | str:
    return "" if valor == INF else redondear(valor)


def blanco_o_redondeado(valor: float | None) -> float | str:
    return "" if valor is None else redondear(valor)


def redondear(valor: Any) -> Any:
    return round(valor, 4) if isinstance(valor, float) else valor
