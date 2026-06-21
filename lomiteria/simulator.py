from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .models import Caja, Cliente, Estadisticas, INF, Preparador, Salon, SimulationParams, SimulationResult, StateRow
from .distributions import (
    generar_atencion_caja,
    generar_llegada,
    generar_permanencia_salon,
    generar_preparacion_llevar,
    generar_salon,
    generar_tipo_consumo,
    generar_valor_a,
)
from .metrics import calcular_metricas
from .rk4 import construir_tablas_rk4
from .state_vector import armar_fila_vector, proxima_salida_salon
from .tables import tablas_intermedias


@dataclass
class EstadoSimulacion:
    parametros: SimulationParams
    generador: random.Random
    tiempos_rk: dict[int, float]
    reloj: float = 0.0
    nro_evento: int = 0
    proximo_id_cliente: int = 1
    proxima_llegada: float = INF
    fin_caja: float = INF
    proximo_control_15: float = 15.0
    proximo_control_30: float = 30.0
    caja: Caja = field(default_factory=Caja)
    preparadores: list[Preparador] = field(default_factory=list)
    rojo: Salon | None = None
    azul: Salon | None = None
    estadisticas: Estadisticas = field(default_factory=Estadisticas)
    clientes: dict[int, Cliente] = field(default_factory=dict)
    cola_caja: deque[int] = field(default_factory=deque)
    cola_mostrador: deque[int] = field(default_factory=deque)
    controles_15: list[dict[str, Any]] = field(default_factory=list)
    controles_30: list[dict[str, Any]] = field(default_factory=list)


def simulate(parametros: SimulationParams) -> SimulationResult:
    """Ejecuta la simulacion por eventos discretos hasta X o hasta el limite de iteraciones."""
    tablas_rk, tiempos_rk = construir_tablas_rk4(parametros)
    estado = EstadoSimulacion(
        parametros=parametros,
        generador=random.Random(parametros.seed),
        tiempos_rk=tiempos_rk,
        preparadores=[Preparador(id=i) for i in range(1, parametros.preparadores + 1)],
        rojo=Salon(nombre="rojo", capacidad=parametros.capacidad_rojo),
        azul=Salon(nombre="azul", capacidad=parametros.capacidad_azul),
        proximo_control_15=parametros.control_mostrador_interval,
        proximo_control_30=parametros.control_salones_interval,
    )

    filas_visibles: list[StateRow] = []
    ultimas_filas: deque[StateRow] = deque(maxlen=10)
    # Fila 0: inicializa la primera llegada y deja registrados sus RND.
    primera_llegada = _generar_llegada(estado)
    estado.proxima_llegada = primera_llegada["proxima_llegada"]
    fila_inicial = armar_fila_vector(estado, "Inicializacion", primera_llegada)
    _guardar_fila(fila_inicial, filas_visibles, ultimas_filas, parametros)

    fila_final = fila_inicial
    while estado.nro_evento < parametros.max_iterations:
        # Igual que en una planilla: se toma el menor tiempo programado y se avanza una fila.
        nombre_evento, tiempo_evento, dato_evento = _proximo_evento(estado)
        if tiempo_evento == INF or tiempo_evento > parametros.x_minutes:
            _avanzar_reloj(estado, parametros.x_minutes)
            estado.nro_evento += 1
            fila_final = armar_fila_vector(estado, "fin_simulacion", {}, omitir_temporales=True)
            _guardar_fila(fila_final, filas_visibles, ultimas_filas, parametros)
            break

        _avanzar_reloj(estado, tiempo_evento)
        estado.nro_evento += 1
        valores_sorteados = _procesar_evento(estado, nombre_evento, dato_evento)
        fila = armar_fila_vector(estado, nombre_evento, valores_sorteados)
        _guardar_fila(fila, filas_visibles, ultimas_filas, parametros)
        fila_final = fila

    else:
        fila_final = armar_fila_vector(estado, "limite_iteraciones", {}, omitir_temporales=True)
        _guardar_fila(fila_final, filas_visibles, ultimas_filas, parametros)

    return SimulationResult(
        params=parametros,
        rows=filas_visibles[: parametros.display_count],
        last_rows=list(ultimas_filas),
        final_row=fila_final,
        metrics=calcular_metricas(estado),
        controls_15=estado.controles_15,
        controls_30=estado.controles_30,
        rk4_tables=tablas_rk,
        intermediate_tables=tablas_intermedias(parametros),
        total_iterations=estado.nro_evento,
    )


def _guardar_fila(fila: StateRow, filas_visibles: list[StateRow], ultimas_filas: deque[StateRow], parametros: SimulationParams) -> None:
    """Guarda solo las filas necesarias: ventana pedida y ultimas 10."""
    ultimas_filas.append(fila)
    if parametros.display_from <= fila.nro_evento < parametros.display_from + parametros.display_count:
        filas_visibles.append(fila)


def _avanzar_reloj(estado: EstadoSimulacion, nuevo_reloj: float) -> None:
    """Actualiza acumuladores por area desde el reloj anterior hasta el nuevo."""
    diferencia_reloj = max(0.0, nuevo_reloj - estado.reloj)
    if estado.caja.estado == "Ocupada":
        estado.caja.ac_tiempo_ocupada += diferencia_reloj
    for preparador in estado.preparadores:
        if preparador.estado == "Ocupado":
            preparador.ac_tiempo_ocupado += diferencia_reloj
    assert estado.rojo is not None and estado.azul is not None
    estado.rojo.ac_ocupacion_tiempo_persona += estado.rojo.ocupacion * diferencia_reloj
    estado.azul.ac_ocupacion_tiempo_persona += estado.azul.ocupacion * diferencia_reloj
    estado.reloj = nuevo_reloj


def _proximo_evento(estado: EstadoSimulacion) -> tuple[str, float, Any]:
    """Devuelve el evento con menor tiempo programado."""
    candidatos: list[tuple[float, int, str, Any]] = [
        (estado.proxima_llegada, 1, "llegada_cliente", None),
        (estado.fin_caja, 2, "fin_atencion_caja", None),
        (estado.proximo_control_15, 7, "control_cola_mostrador_15min", None),
        (estado.proximo_control_30, 8, "control_salones_30min", None),
    ]
    for preparador in estado.preparadores:
        candidatos.append((preparador.fin_preparacion_programado, 3 + preparador.id, f"fin_preparacion_mostrador_{preparador.id}", preparador.id))

    fin_rojo = proxima_salida_salon(estado, "rojo")
    fin_azul = proxima_salida_salon(estado, "azul")
    candidatos.append((fin_rojo[0], 20, "fin_permanencia_rojo", fin_rojo[1]))
    candidatos.append((fin_azul[0], 21, "fin_permanencia_azul", fin_azul[1]))

    tiempo, _, nombre, dato_evento = min(candidatos, key=lambda item: (item[0], item[1]))
    return nombre, tiempo, dato_evento


def _procesar_evento(estado: EstadoSimulacion, nombre_evento: str, dato_evento: Any) -> dict[str, Any]:
    """Ejecuta el evento y devuelve los RND/valores generados para la fila."""
    if nombre_evento == "llegada_cliente":
        return _evento_llegada_cliente(estado)
    if nombre_evento == "fin_atencion_caja":
        return _evento_fin_atencion_caja(estado)
    if nombre_evento.startswith("fin_preparacion_mostrador_"):
        return _evento_fin_preparacion(estado, int(dato_evento))
    if nombre_evento == "fin_permanencia_rojo":
        return _evento_fin_permanencia_salon(estado, "rojo", int(dato_evento))
    if nombre_evento == "fin_permanencia_azul":
        return _evento_fin_permanencia_salon(estado, "azul", int(dato_evento))
    if nombre_evento == "control_cola_mostrador_15min":
        estado.controles_15.append({"reloj_min": round(estado.reloj, 4), "cola_mostrador": len(estado.cola_mostrador)})
        estado.proximo_control_15 = estado.reloj + estado.parametros.control_mostrador_interval
        return {}
    if nombre_evento == "control_salones_30min":
        assert estado.rojo is not None and estado.azul is not None
        estado.controles_30.append(
            {
                "reloj_min": round(estado.reloj, 4),
                "ocupacion_rojo": estado.rojo.ocupacion,
                "ocupacion_azul": estado.azul.ocupacion,
            }
        )
        estado.proximo_control_30 = estado.reloj + estado.parametros.control_salones_interval
        return {}
    return {}


def _evento_llegada_cliente(estado: EstadoSimulacion) -> dict[str, Any]:
    """Llega un cliente: entra a caja o espera en cola de caja."""
    valores_sorteados = _generar_llegada(estado)
    estado.proxima_llegada = valores_sorteados["proxima_llegada"]

    id_cliente = estado.proximo_id_cliente
    estado.proximo_id_cliente += 1
    cliente = Cliente(id=id_cliente, estado="EAC", hora_llegada_negocio=estado.reloj)
    estado.clientes[id_cliente] = cliente

    if estado.caja.estado == "Libre":
        valores_sorteados.update(_iniciar_atencion_caja(estado, id_cliente))
    else:
        cliente.hora_inicio_cola_caja = estado.reloj
        estado.cola_caja.append(id_cliente)
        estado.estadisticas.max_cola_caja = max(estado.estadisticas.max_cola_caja, len(estado.cola_caja))

    return valores_sorteados


def _evento_fin_atencion_caja(estado: EstadoSimulacion) -> dict[str, Any]:
    """Termina caja: se define tipo de consumo y, si corresponde, salon y valor A."""
    id_cliente = estado.caja.cliente_actual
    valores_sorteados: dict[str, Any] = {}
    if id_cliente is not None and id_cliente in estado.clientes:
        cliente = estado.clientes[id_cliente]
        sorteo_consumo = generar_tipo_consumo(estado.generador, estado.parametros)
        cliente.tipo_consumo = sorteo_consumo["tipo_consumo"]
        valores_sorteados.update(sorteo_consumo)
        if cliente.tipo_consumo == "local":
            salon = generar_salon(estado.generador, estado.parametros)
            sorteo_a = generar_valor_a(estado.generador, estado.parametros)
            cliente.salon_elegido = salon["salon"]
            cliente.a_preparacion = sorteo_a["a_preparacion"]
            valores_sorteados.update(salon)
            valores_sorteados.update(sorteo_a)
        cliente.estado = "EPM"
        cliente.hora_inicio_cola_mostrador = estado.reloj
        _enviar_a_preparacion_o_cola(estado, id_cliente, valores_sorteados)

    if estado.cola_caja:
        siguiente_cliente = estado.cola_caja.popleft()
        tiempo_espera = estado.reloj - (estado.clientes[siguiente_cliente].hora_inicio_cola_caja or estado.reloj)
        estado.estadisticas.ac_tiempo_cola_caja += tiempo_espera
        valores_sorteados.update(_iniciar_atencion_caja(estado, siguiente_cliente))
    else:
        estado.caja.estado = "Libre"
        estado.caja.cliente_actual = None
        estado.caja.hora_inicio_ocupacion = None
        estado.fin_caja = INF

    return valores_sorteados


def _evento_fin_preparacion(estado: EstadoSimulacion, id_preparador: int) -> dict[str, Any]:
    """Termina un preparador: el cliente sale o intenta entrar al salon elegido."""
    preparador = estado.preparadores[id_preparador - 1]
    id_cliente = preparador.cliente_actual
    valores_sorteados: dict[str, Any] = {}

    if id_cliente is not None and id_cliente in estado.clientes:
        cliente = estado.clientes[id_cliente]
        if cliente.tipo_consumo == "llevar":
            _finalizar_cliente(estado, id_cliente)
        else:
            valores_sorteados.update(_entrar_o_esperar_salon(estado, id_cliente))

    if estado.cola_mostrador:
        siguiente_cliente = estado.cola_mostrador.popleft()
        valores_sorteados.update(_iniciar_preparacion(estado, preparador, siguiente_cliente))
    else:
        preparador.estado = "Libre"
        preparador.cliente_actual = None
        preparador.hora_inicio_ocupacion = None
        preparador.fin_preparacion_programado = INF

    return valores_sorteados


def _evento_fin_permanencia_salon(estado: EstadoSimulacion, nombre_salon: str, id_cliente: int) -> dict[str, Any]:
    """Termina la permanencia en salon y se libera un lugar."""
    salon = _salon(estado, nombre_salon)
    if id_cliente in estado.clientes:
        _finalizar_cliente(estado, id_cliente)
    salon.ocupacion = max(0, salon.ocupacion - 1)

    valores_sorteados: dict[str, Any] = {}
    if salon.cola_entrada:
        siguiente_cliente = salon.cola_entrada.pop(0)
        valores_sorteados.update(_iniciar_permanencia_salon(estado, siguiente_cliente, nombre_salon))
    return valores_sorteados


def _generar_llegada(estado: EstadoSimulacion) -> dict[str, Any]:
    return generar_llegada(estado.generador, estado.reloj, estado.parametros)


def _iniciar_atencion_caja(estado: EstadoSimulacion, id_cliente: int) -> dict[str, Any]:
    """Ocupa la caja, suma contador y programa fin de atencion."""
    cliente = estado.clientes[id_cliente]
    cliente.estado = "SAC"
    estado.caja.estado = "Ocupada"
    estado.caja.cliente_actual = id_cliente
    estado.caja.hora_inicio_ocupacion = estado.reloj
    estado.estadisticas.ct_clientes_pasan_por_caja += 1
    valores_sorteados = generar_atencion_caja(estado.generador, estado.reloj, estado.parametros)
    estado.fin_caja = valores_sorteados["fin_caja"]
    return valores_sorteados


def _enviar_a_preparacion_o_cola(estado: EstadoSimulacion, id_cliente: int, valores_sorteados: dict[str, Any]) -> None:
    preparador_libre = next((prep for prep in estado.preparadores if prep.estado == "Libre"), None)
    if preparador_libre is None:
        estado.cola_mostrador.append(id_cliente)
        estado.estadisticas.max_cola_mostrador = max(estado.estadisticas.max_cola_mostrador, len(estado.cola_mostrador))
        return
    valores_sorteados.update(_iniciar_preparacion(estado, preparador_libre, id_cliente))


def _iniciar_preparacion(estado: EstadoSimulacion, preparador: Preparador, id_cliente: int) -> dict[str, Any]:
    """Ocupa un preparador y programa el fin de preparacion."""
    cliente = estado.clientes[id_cliente]
    tiempo_espera = estado.reloj - (cliente.hora_inicio_cola_mostrador or estado.reloj)
    estado.estadisticas.ac_tiempo_cola_mostrador += tiempo_espera
    estado.estadisticas.ct_clientes_pasan_por_mostrador += 1
    cliente.preparador_asignado = preparador.id
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
        valores_sorteados.update(generar_preparacion_llevar(estado.generador, estado.parametros))
        tiempo_preparacion = valores_sorteados["tiempo_preparacion_llevar"]
        cliente.tiempo_preparacion = tiempo_preparacion

    preparador.fin_preparacion_programado = estado.reloj + tiempo_preparacion
    cliente.hora_fin_programada = preparador.fin_preparacion_programado
    valores_sorteados[f"fin_preparacion_{preparador.id}"] = preparador.fin_preparacion_programado
    return valores_sorteados


def _entrar_o_esperar_salon(estado: EstadoSimulacion, id_cliente: int) -> dict[str, Any]:
    """Si hay capacidad entra al salon; si no, espera en la cola de ese salon."""
    cliente = estado.clientes[id_cliente]
    salon = _salon(estado, cliente.salon_elegido)
    if salon.ocupacion < salon.capacidad:
        return _iniciar_permanencia_salon(estado, id_cliente, salon.nombre)

    cliente.estado = "EASR" if salon.nombre == "rojo" else "EASA"
    cliente.hora_inicio_cola_salon = estado.reloj
    salon.cola_entrada.append(id_cliente)
    salon.clientes_que_esperaron_por_capacidad += 1
    if salon.nombre == "rojo":
        estado.estadisticas.ct_esperaron_rojo_lleno += 1
    else:
        estado.estadisticas.ct_esperaron_azul_lleno += 1
    return {}


def _iniciar_permanencia_salon(estado: EstadoSimulacion, id_cliente: int, nombre_salon: str) -> dict[str, Any]:
    cliente = estado.clientes[id_cliente]
    salon = _salon(estado, nombre_salon)
    salon.ocupacion += 1
    salon.max_ocupacion = max(salon.max_ocupacion, salon.ocupacion)
    cliente.estado = "PSR" if nombre_salon == "rojo" else "PSA"
    cliente.hora_inicio_permanencia = estado.reloj
    valores_sorteados = generar_permanencia_salon(estado.generador, nombre_salon, estado.reloj, estado.parametros)
    tiempo_permanencia = valores_sorteados["tiempo_permanencia_salon"]
    cliente.hora_fin_programada = estado.reloj + tiempo_permanencia
    return valores_sorteados


def _finalizar_cliente(estado: EstadoSimulacion, id_cliente: int) -> None:
    """Saca el cliente del sistema y acumula su permanencia total."""
    cliente = estado.clientes.pop(id_cliente, None)
    if cliente is None:
        return
    estado.estadisticas.ac_tiempo_permanencia_negocio += estado.reloj - cliente.hora_llegada_negocio
    estado.estadisticas.ct_clientes_finalizados += 1


def _salon(estado: EstadoSimulacion, nombre_salon: str) -> Salon:
    assert estado.rojo is not None and estado.azul is not None
    return estado.rojo if nombre_salon == "rojo" else estado.azul
