from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .models import Caja, Cliente, Estadisticas, INF, Preparador, Salon, SimulationParams, SimulationResult, StateRow
from .randoms import normal_positive, uniform
from .rk4 import build_rk4_tables
from .tables import intermediate_tables, lookup_a_value, lookup_salon, lookup_tipo_consumo, permanence_range


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


@dataclass
class SimulationState:
    params: SimulationParams
    rng: random.Random
    rk_times: dict[int, float]
    reloj: float = 0.0
    nro_evento: int = 0
    next_client_id: int = 1
    proxima_llegada: float = INF
    fin_caja: float = INF
    proximo_control_15: float = 15.0
    proximo_control_30: float = 30.0
    caja: Caja = field(default_factory=Caja)
    preparadores: list[Preparador] = field(default_factory=list)
    rojo: Salon | None = None
    azul: Salon | None = None
    stats: Estadisticas = field(default_factory=Estadisticas)
    clientes: dict[int, Cliente] = field(default_factory=dict)
    cola_caja: deque[int] = field(default_factory=deque)
    cola_mostrador: deque[int] = field(default_factory=deque)
    controls_15: list[dict[str, Any]] = field(default_factory=list)
    controls_30: list[dict[str, Any]] = field(default_factory=list)


def simulate(params: SimulationParams) -> SimulationResult:
    rk_tables, rk_times = build_rk4_tables(params)
    state = SimulationState(
        params=params,
        rng=random.Random(params.seed),
        rk_times=rk_times,
        preparadores=[Preparador(id=i) for i in range(1, params.preparadores + 1)],
        rojo=Salon(nombre="rojo", capacidad=params.capacidad_rojo),
        azul=Salon(nombre="azul", capacidad=params.capacidad_azul),
        proximo_control_15=params.control_mostrador_interval,
        proximo_control_30=params.control_salones_interval,
    )

    visible_rows: list[StateRow] = []
    first_arrival = _draw_arrival(state)
    state.proxima_llegada = first_arrival["proxima_llegada"]
    initial = _make_row(state, "Inicializacion", first_arrival)
    _store_visible_row(initial, visible_rows, params)

    final_row = initial
    while state.nro_evento < params.max_iterations:
        event_name, event_time, payload = _next_event(state)
        if event_time == INF or event_time > params.x_minutes:
            _advance_time(state, params.x_minutes)
            state.nro_evento += 1
            final_row = _make_row(state, "fin_simulacion", {}, omit_temporales=True)
            break

        _advance_time(state, event_time)
        state.nro_evento += 1
        randoms = _process_event(state, event_name, payload)
        row = _make_row(state, event_name, randoms)
        _store_visible_row(row, visible_rows, params)
        final_row = row

    else:
        final_row = _make_row(state, "limite_iteraciones", {}, omit_temporales=True)

    if final_row.evento == "fin_simulacion":
        _store_visible_row(final_row, visible_rows, params)

    return SimulationResult(
        rows=visible_rows[: params.display_count],
        final_row=final_row,
        metrics=_metrics(state),
        controls_15=state.controls_15,
        controls_30=state.controls_30,
        rk4_tables=rk_tables,
        intermediate_tables=intermediate_tables(params),
        total_iterations=state.nro_evento,
    )


def _store_visible_row(row: StateRow, visible_rows: list[StateRow], params: SimulationParams) -> None:
    if params.display_from <= row.nro_evento < params.display_from + params.display_count:
        visible_rows.append(row)


def _advance_time(state: SimulationState, new_clock: float) -> None:
    delta = max(0.0, new_clock - state.reloj)
    if state.caja.estado == "Ocupada":
        state.caja.ac_tiempo_ocupada += delta
    for preparador in state.preparadores:
        if preparador.estado == "Ocupado":
            preparador.ac_tiempo_ocupado += delta
    assert state.rojo is not None and state.azul is not None
    state.rojo.ac_ocupacion_tiempo_persona += state.rojo.ocupacion * delta
    state.azul.ac_ocupacion_tiempo_persona += state.azul.ocupacion * delta
    state.reloj = new_clock


def _next_event(state: SimulationState) -> tuple[str, float, Any]:
    candidates: list[tuple[float, int, str, Any]] = [
        (state.proxima_llegada, 1, "llegada_cliente", None),
        (state.fin_caja, 2, "fin_atencion_caja", None),
        (state.proximo_control_15, 7, "control_cola_mostrador_15min", None),
        (state.proximo_control_30, 8, "control_salones_30min", None),
    ]
    for preparador in state.preparadores:
        candidates.append((preparador.fin_preparacion_programado, 3 + preparador.id, f"fin_preparacion_mostrador_{preparador.id}", preparador.id))

    rojo_fin = _next_salon_departure(state, "rojo")
    azul_fin = _next_salon_departure(state, "azul")
    candidates.append((rojo_fin[0], 20, "fin_permanencia_rojo", rojo_fin[1]))
    candidates.append((azul_fin[0], 21, "fin_permanencia_azul", azul_fin[1]))

    time, _, name, payload = min(candidates, key=lambda item: (item[0], item[1]))
    return name, time, payload


def _process_event(state: SimulationState, event_name: str, payload: Any) -> dict[str, Any]:
    if event_name == "llegada_cliente":
        return _event_arrival(state)
    if event_name == "fin_atencion_caja":
        return _event_cashier_done(state)
    if event_name.startswith("fin_preparacion_mostrador_"):
        return _event_prep_done(state, int(payload))
    if event_name == "fin_permanencia_rojo":
        return _event_salon_done(state, "rojo", int(payload))
    if event_name == "fin_permanencia_azul":
        return _event_salon_done(state, "azul", int(payload))
    if event_name == "control_cola_mostrador_15min":
        state.controls_15.append({"reloj_min": round(state.reloj, 4), "cola_mostrador": len(state.cola_mostrador)})
        state.proximo_control_15 = state.reloj + state.params.control_mostrador_interval
        return {}
    if event_name == "control_salones_30min":
        assert state.rojo is not None and state.azul is not None
        state.controls_30.append(
            {
                "reloj_min": round(state.reloj, 4),
                "ocupacion_rojo": state.rojo.ocupacion,
                "ocupacion_azul": state.azul.ocupacion,
            }
        )
        state.proximo_control_30 = state.reloj + state.params.control_salones_interval
        return {}
    return {}


def _event_arrival(state: SimulationState) -> dict[str, Any]:
    randoms = _draw_arrival(state)
    state.proxima_llegada = randoms["proxima_llegada"]

    client_id = state.next_client_id
    state.next_client_id += 1
    client = Cliente(id=client_id, estado="EAC", hora_llegada_negocio=state.reloj)
    state.clientes[client_id] = client

    if state.caja.estado == "Libre":
        randoms.update(_start_cashier_service(state, client_id))
    else:
        client.hora_inicio_cola_caja = state.reloj
        state.cola_caja.append(client_id)
        state.stats.max_cola_caja = max(state.stats.max_cola_caja, len(state.cola_caja))

    return randoms


def _event_cashier_done(state: SimulationState) -> dict[str, Any]:
    client_id = state.caja.cliente_actual
    randoms: dict[str, Any] = {}
    if client_id is not None and client_id in state.clientes:
        client = state.clientes[client_id]
        rnd_tipo = state.rng.random()
        client.tipo_consumo = lookup_tipo_consumo(rnd_tipo, state.params)
        randoms["rnd_tipo_consumo"] = rnd_tipo
        randoms["tipo_consumo"] = client.tipo_consumo
        if client.tipo_consumo == "local":
            rnd_salon = state.rng.random()
            rnd_a = state.rng.random()
            client.salon_elegido = lookup_salon(rnd_salon, state.params)
            client.a_preparacion = lookup_a_value(rnd_a, state.params)
            randoms.update({"rnd_salon": rnd_salon, "salon": client.salon_elegido, "rnd_a_preparacion": rnd_a, "a_preparacion": client.a_preparacion})
        client.estado = "EPM"
        client.hora_inicio_cola_mostrador = state.reloj
        _send_to_preparation_or_queue(state, client_id, randoms)

    if state.cola_caja:
        next_client = state.cola_caja.popleft()
        waited = state.reloj - (state.clientes[next_client].hora_inicio_cola_caja or state.reloj)
        state.stats.ac_tiempo_cola_caja += waited
        randoms.update(_start_cashier_service(state, next_client))
    else:
        state.caja.estado = "Libre"
        state.caja.cliente_actual = None
        state.caja.hora_inicio_ocupacion = None
        state.fin_caja = INF

    return randoms


def _event_prep_done(state: SimulationState, prep_id: int) -> dict[str, Any]:
    preparador = state.preparadores[prep_id - 1]
    client_id = preparador.cliente_actual
    randoms: dict[str, Any] = {}

    if client_id is not None and client_id in state.clientes:
        client = state.clientes[client_id]
        if client.tipo_consumo == "llevar":
            _finish_client(state, client_id)
        else:
            randoms.update(_enter_or_queue_salon(state, client_id))

    if state.cola_mostrador:
        next_client = state.cola_mostrador.popleft()
        randoms.update(_start_preparation(state, preparador, next_client))
    else:
        preparador.estado = "Libre"
        preparador.cliente_actual = None
        preparador.hora_inicio_ocupacion = None
        preparador.fin_preparacion_programado = INF

    return randoms


def _event_salon_done(state: SimulationState, salon_name: str, client_id: int) -> dict[str, Any]:
    salon = _salon(state, salon_name)
    if client_id in state.clientes:
        _finish_client(state, client_id)
    salon.ocupacion = max(0, salon.ocupacion - 1)

    randoms: dict[str, Any] = {}
    if salon.cola_entrada:
        next_client = salon.cola_entrada.pop(0)
        randoms.update(_start_salon_stay(state, next_client, salon_name))
    return randoms


def _draw_arrival(state: SimulationState) -> dict[str, Any]:
    draw = normal_positive(state.rng, state.params.llegada_media, state.params.llegada_desvio)
    return {
        "rnd_llegada_1": draw.rnd1,
        "rnd_llegada_2": draw.rnd2,
        "tiempo_entre_llegadas": draw.value,
        "proxima_llegada": state.reloj + draw.value,
    }


def _start_cashier_service(state: SimulationState, client_id: int) -> dict[str, Any]:
    client = state.clientes[client_id]
    client.estado = "SAC"
    state.caja.estado = "Ocupada"
    state.caja.cliente_actual = client_id
    state.caja.hora_inicio_ocupacion = state.reloj
    state.stats.ct_clientes_pasan_por_caja += 1
    rnd = state.rng.random()
    service_time = uniform(rnd, state.params.caja_min, state.params.caja_max)
    state.fin_caja = state.reloj + service_time
    return {"rnd_caja": rnd, "tiempo_caja": service_time, "fin_caja": state.fin_caja}


def _send_to_preparation_or_queue(state: SimulationState, client_id: int, randoms: dict[str, Any]) -> None:
    free = next((prep for prep in state.preparadores if prep.estado == "Libre"), None)
    if free is None:
        state.cola_mostrador.append(client_id)
        state.stats.max_cola_mostrador = max(state.stats.max_cola_mostrador, len(state.cola_mostrador))
        return
    randoms.update(_start_preparation(state, free, client_id))


def _start_preparation(state: SimulationState, preparador: Preparador, client_id: int) -> dict[str, Any]:
    client = state.clientes[client_id]
    waited = state.reloj - (client.hora_inicio_cola_mostrador or state.reloj)
    state.stats.ac_tiempo_cola_mostrador += waited
    state.stats.ct_clientes_pasan_por_mostrador += 1
    client.preparador_asignado = preparador.id
    preparador.estado = "Ocupado"
    preparador.cliente_actual = client_id
    preparador.hora_inicio_ocupacion = state.reloj

    randoms: dict[str, Any] = {}
    if client.tipo_consumo == "local":
        assert client.a_preparacion is not None
        prep_time = state.rk_times[client.a_preparacion]
        client.tiempo_preparacion = prep_time
        randoms["tiempo_preparacion_local"] = prep_time
    else:
        rnd = state.rng.random()
        prep_time = uniform(rnd, state.params.llevar_min, state.params.llevar_max)
        client.tiempo_preparacion = prep_time
        randoms["rnd_preparacion_llevar"] = rnd
        randoms["tiempo_preparacion_llevar"] = prep_time

    preparador.fin_preparacion_programado = state.reloj + prep_time
    client.hora_fin_programada = preparador.fin_preparacion_programado
    randoms[f"fin_preparacion_{preparador.id}"] = preparador.fin_preparacion_programado
    return randoms


def _enter_or_queue_salon(state: SimulationState, client_id: int) -> dict[str, Any]:
    client = state.clientes[client_id]
    salon = _salon(state, client.salon_elegido)
    if salon.ocupacion < salon.capacidad:
        return _start_salon_stay(state, client_id, salon.nombre)

    client.estado = "EASR" if salon.nombre == "rojo" else "EASA"
    client.hora_inicio_cola_salon = state.reloj
    salon.cola_entrada.append(client_id)
    salon.clientes_que_esperaron_por_capacidad += 1
    if salon.nombre == "rojo":
        state.stats.ct_esperaron_rojo_lleno += 1
    else:
        state.stats.ct_esperaron_azul_lleno += 1
    return {}


def _start_salon_stay(state: SimulationState, client_id: int, salon_name: str) -> dict[str, Any]:
    client = state.clientes[client_id]
    salon = _salon(state, salon_name)
    salon.ocupacion += 1
    salon.max_ocupacion = max(salon.max_ocupacion, salon.ocupacion)
    client.estado = "PSR" if salon_name == "rojo" else "PSA"
    client.hora_inicio_permanencia = state.reloj
    rnd = state.rng.random()
    low, high = permanence_range(salon_name, state.reloj, state.params)
    stay = uniform(rnd, low, high)
    client.hora_fin_programada = state.reloj + stay
    return {"rnd_permanencia_salon": rnd, "tiempo_permanencia_salon": stay}


def _finish_client(state: SimulationState, client_id: int) -> None:
    client = state.clientes.pop(client_id, None)
    if client is None:
        return
    state.stats.ac_tiempo_permanencia_negocio += state.reloj - client.hora_llegada_negocio
    state.stats.ct_clientes_finalizados += 1


def _next_salon_departure(state: SimulationState, salon_name: str) -> tuple[float, int | None]:
    wanted = "PSR" if salon_name == "rojo" else "PSA"
    times = [
        (client.hora_fin_programada or INF, client.id)
        for client in state.clientes.values()
        if client.estado == wanted
    ]
    if not times:
        return INF, None
    return min(times, key=lambda item: item[0])


def _salon(state: SimulationState, salon_name: str) -> Salon:
    assert state.rojo is not None and state.azul is not None
    return state.rojo if salon_name == "rojo" else state.azul


def _make_row(state: SimulationState, evento: str, randoms: dict[str, Any], omit_temporales: bool = False) -> StateRow:
    eventos = {column: "" for column in EVENT_COLUMNS}
    eventos.update(_scheduled_event_values(state))
    eventos.update({key: _round(value) for key, value in randoms.items() if key in EVENT_COLUMNS})

    return StateRow(
        nro_evento=state.nro_evento,
        evento=evento,
        reloj_min=_round(state.reloj),
        hora_real=_hour_label(state.reloj),
        eventos=eventos,
        objetos_permanentes=_permanent_values(state),
        variables_estadisticas=_stats_values(state),
        objetos_temporales={} if omit_temporales else _temporary_values(state),
    )


def _scheduled_event_values(state: SimulationState) -> dict[str, Any]:
    values = {
        "proxima_llegada": _event_time(state.proxima_llegada),
        "fin_caja": _event_time(state.fin_caja),
        "proximo_control_15": _event_time(state.proximo_control_15),
        "proximo_control_30": _event_time(state.proximo_control_30),
    }
    for prep in state.preparadores:
        values[f"fin_preparacion_{prep.id}"] = _event_time(prep.fin_preparacion_programado)
    values["fin_permanencia_rojo"] = _event_time(_next_salon_departure(state, "rojo")[0])
    values["fin_permanencia_azul"] = _event_time(_next_salon_departure(state, "azul")[0])
    return values


def _permanent_values(state: SimulationState) -> dict[str, Any]:
    assert state.rojo is not None and state.azul is not None
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


def _stats_values(state: SimulationState) -> dict[str, Any]:
    assert state.rojo is not None and state.azul is not None
    values: dict[str, Any] = {
        "ac_tiempo_permanencia_negocio": _round(state.stats.ac_tiempo_permanencia_negocio),
        "ct_clientes_finalizados": state.stats.ct_clientes_finalizados,
        "ac_tiempo_cola_caja": _round(state.stats.ac_tiempo_cola_caja),
        "ct_clientes_pasan_por_caja": state.stats.ct_clientes_pasan_por_caja,
        "ac_tiempo_cola_mostrador": _round(state.stats.ac_tiempo_cola_mostrador),
        "ct_clientes_pasan_por_mostrador": state.stats.ct_clientes_pasan_por_mostrador,
        "ac_ocupacion_caja": _round(state.caja.ac_tiempo_ocupada),
        "ac_ocupacion_rojo_tiempo_persona": _round(state.rojo.ac_ocupacion_tiempo_persona),
        "ac_ocupacion_azul_tiempo_persona": _round(state.azul.ac_ocupacion_tiempo_persona),
        "max_cola_caja": state.stats.max_cola_caja,
        "max_cola_mostrador": state.stats.max_cola_mostrador,
        "max_ocupacion_rojo": state.rojo.max_ocupacion,
        "max_ocupacion_azul": state.azul.max_ocupacion,
        "ct_esperaron_rojo_lleno": state.stats.ct_esperaron_rojo_lleno,
        "ct_esperaron_azul_lleno": state.stats.ct_esperaron_azul_lleno,
    }
    for prep in state.preparadores:
        values[f"ac_ocupacion_preparador_{prep.id}"] = _round(prep.ac_tiempo_ocupado)
    return values


def _temporary_values(state: SimulationState) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for client in sorted(state.clientes.values(), key=lambda c: c.id):
        prefix = f"cliente_{client.id}"
        values[f"{prefix}_estado"] = client.estado
        values[f"{prefix}_hora_llegada"] = _round(client.hora_llegada_negocio)
        values[f"{prefix}_tipo_consumo"] = client.tipo_consumo
        values[f"{prefix}_salon"] = client.salon_elegido
        values[f"{prefix}_hora_inicio_cola_caja"] = _blank_or_round(client.hora_inicio_cola_caja)
        values[f"{prefix}_hora_inicio_cola_mostrador"] = _blank_or_round(client.hora_inicio_cola_mostrador)
        values[f"{prefix}_hora_inicio_cola_salon"] = _blank_or_round(client.hora_inicio_cola_salon)
        values[f"{prefix}_preparador_asignado"] = client.preparador_asignado or ""
        values[f"{prefix}_hora_inicio_permanencia"] = _blank_or_round(client.hora_inicio_permanencia)
        values[f"{prefix}_fin_programado"] = _blank_or_round(client.hora_fin_programada)
    return values


def _metrics(state: SimulationState) -> dict[str, float]:
    assert state.rojo is not None and state.azul is not None
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


def _safe_div(numerator: float, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _hour_label(reloj_min: float) -> str:
    total = 11 * 60 + int(round(reloj_min))
    return f"{total // 60:02d}:{total % 60:02d}"


def _event_time(value: float) -> float | str:
    return "" if value == INF else _round(value)


def _blank_or_round(value: float | None) -> float | str:
    return "" if value is None else _round(value)


def _round(value: Any) -> Any:
    return round(value, 4) if isinstance(value, float) else value
