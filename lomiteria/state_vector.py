from __future__ import annotations

from typing import Any

from .models import INF, StateRow


EVENT_COLUMNS = [
    "rnd_llegada_1",
    "rnd_llegada_2",
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


def make_state_row(state: Any, evento: str, randoms: dict[str, Any], omit_temporales: bool = False) -> StateRow:
    eventos = {column: "" for column in EVENT_COLUMNS}
    eventos.update(scheduled_event_values(state))
    eventos.update({key: round_value(value) for key, value in randoms.items() if key in EVENT_COLUMNS})

    return StateRow(
        nro_evento=state.nro_evento,
        evento=evento,
        reloj_min=round_value(state.reloj),
        hora_real=hour_label(state.reloj),
        eventos=eventos,
        objetos_permanentes=permanent_values(state),
        variables_estadisticas=stats_values(state),
        objetos_temporales={} if omit_temporales else temporary_values(state),
    )


def scheduled_event_values(state: Any) -> dict[str, Any]:
    values = {
        "proxima_llegada": event_time(state.proxima_llegada),
        "fin_caja": event_time(state.fin_caja),
        "proximo_control_15": event_time(state.proximo_control_15),
        "proximo_control_30": event_time(state.proximo_control_30),
    }
    for prep in state.preparadores:
        values[f"fin_preparacion_{prep.id}"] = event_time(prep.fin_preparacion_programado)
    values["fin_permanencia_rojo"] = event_time(next_salon_departure(state, "rojo")[0])
    values["fin_permanencia_azul"] = event_time(next_salon_departure(state, "azul")[0])
    return values


def permanent_values(state: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "estado_caja": state.caja.estado,
        "cliente_caja": state.caja.cliente_actual or "",
        "cola_caja": len(state.cola_caja),
        "cola_mostrador": len(state.cola_mostrador),
        "ocupacion_rojo": state.rojo.ocupacion,
        "cola_rojo": len(state.rojo.cola_entrada),
        "ocupacion_azul": state.azul.ocupacion,
        "cola_azul": len(state.azul.cola_entrada),
    }
    for prep in state.preparadores:
        values[f"estado_preparador_{prep.id}"] = prep.estado
        values[f"cliente_preparador_{prep.id}"] = prep.cliente_actual or ""
    return values


def stats_values(state: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "ac_tiempo_permanencia_negocio": round_value(state.stats.ac_tiempo_permanencia_negocio),
        "ct_clientes_finalizados": state.stats.ct_clientes_finalizados,
        "ac_tiempo_cola_caja": round_value(state.stats.ac_tiempo_cola_caja),
        "ct_clientes_pasan_por_caja": state.stats.ct_clientes_pasan_por_caja,
        "ac_tiempo_cola_mostrador": round_value(state.stats.ac_tiempo_cola_mostrador),
        "ct_clientes_pasan_por_mostrador": state.stats.ct_clientes_pasan_por_mostrador,
        "ac_ocupacion_caja": round_value(state.caja.ac_tiempo_ocupada),
        "ac_ocupacion_rojo_tiempo_persona": round_value(state.rojo.ac_ocupacion_tiempo_persona),
        "ac_ocupacion_azul_tiempo_persona": round_value(state.azul.ac_ocupacion_tiempo_persona),
        "max_cola_caja": state.stats.max_cola_caja,
        "max_cola_mostrador": state.stats.max_cola_mostrador,
        "max_ocupacion_rojo": state.rojo.max_ocupacion,
        "max_ocupacion_azul": state.azul.max_ocupacion,
        "ct_esperaron_rojo_lleno": state.stats.ct_esperaron_rojo_lleno,
        "ct_esperaron_azul_lleno": state.stats.ct_esperaron_azul_lleno,
    }
    for prep in state.preparadores:
        values[f"ac_ocupacion_preparador_{prep.id}"] = round_value(prep.ac_tiempo_ocupado)
    return values


def temporary_values(state: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for client in sorted(state.clientes.values(), key=lambda c: c.id):
        prefix = f"cliente_{client.id}"
        values[f"{prefix}_estado"] = client.estado
        values[f"{prefix}_hora_llegada"] = round_value(client.hora_llegada_negocio)
        values[f"{prefix}_tipo_consumo"] = client.tipo_consumo
        values[f"{prefix}_salon"] = client.salon_elegido
        values[f"{prefix}_hora_inicio_cola_caja"] = blank_or_round(client.hora_inicio_cola_caja)
        values[f"{prefix}_hora_inicio_cola_mostrador"] = blank_or_round(client.hora_inicio_cola_mostrador)
        values[f"{prefix}_hora_inicio_cola_salon"] = blank_or_round(client.hora_inicio_cola_salon)
        values[f"{prefix}_preparador_asignado"] = client.preparador_asignado or ""
        values[f"{prefix}_hora_inicio_permanencia"] = blank_or_round(client.hora_inicio_permanencia)
        values[f"{prefix}_fin_programado"] = blank_or_round(client.hora_fin_programada)
    return values


def next_salon_departure(state: Any, salon_name: str) -> tuple[float, int | None]:
    wanted = "PSR" if salon_name == "rojo" else "PSA"
    times = [
        (client.hora_fin_programada or INF, client.id)
        for client in state.clientes.values()
        if client.estado == wanted
    ]
    if not times:
        return INF, None
    return min(times, key=lambda item: item[0])


def hour_label(reloj_min: float) -> str:
    total = 11 * 60 + int(round(reloj_min))
    return f"{total // 60:02d}:{total % 60:02d}"


def event_time(value: float) -> float | str:
    return "" if value == INF else round_value(value)


def blank_or_round(value: float | None) -> float | str:
    return "" if value is None else round_value(value)


def round_value(value: Any) -> Any:
    return round(value, 4) if isinstance(value, float) else value
