"""Motor principal de simulacion por eventos discretos."""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from ..aleatorios.box_muller import EstadoBoxMuller
from ..aleatorios.tablas_probabilidad import tablas_intermedias
from ..calculos.metricas import calcular_metricas
from ..calculos.runge_kutta_preparacion import construir_tablas_rk4
from ..eventos.control_cola_mostrador_15min import ejecutar_control_cola_mostrador_15min
from ..eventos.control_salones_30min import ejecutar_control_salones_30min
from ..eventos.fin_atencion_caja import ejecutar_fin_atencion_caja
from ..eventos.fin_permanencia_azul import ejecutar_fin_permanencia_azul
from ..eventos.fin_permanencia_rojo import ejecutar_fin_permanencia_rojo
from ..eventos.fin_preparacion_mostrador import ejecutar_fin_preparacion_mostrador
from ..eventos.llegada_cliente import ejecutar_llegada_cliente, generar_proxima_llegada
from ..modelo.objetos import Caja, Cliente, Estadisticas, INF, Preparador, Salon, SimulationParams, SimulationResult, StateRow
from .vector_estado import armar_fila_vector, proxima_salida_salon


@dataclass
class EstadoSimulacion:
    """Estado vivo de la simulacion.

    Reemplaza a la idea de "tener toda la planilla en memoria":
    aqui se guarda solo la fila actual expandida en objetos, colas,
    eventos programados y acumuladores.
    """
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
    box_muller: EstadoBoxMuller = field(default_factory=EstadoBoxMuller)


def simulate(parametros: SimulationParams) -> SimulationResult:
    """Ejecuta la simulacion por eventos discretos hasta X o hasta el limite de iteraciones.

    Secuencia principal:
    1. Crear estado inicial.
    2. Programar primera llegada.
    3. Repetir:
       - buscar el menor proximo evento;
       - mover el reloj a ese instante;
       - ejecutar el evento;
       - armar la nueva fila del vector.
    """
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
    primera_llegada = generar_proxima_llegada(estado.box_muller, estado.generador, estado.reloj, estado.parametros)
    estado.proxima_llegada = primera_llegada["proxima_llegada"]
    fila_inicial = _registrar_fila_actual(estado, "Inicializacion", primera_llegada, filas_visibles, ultimas_filas, parametros)

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
        fila = _registrar_fila_actual(estado, nombre_evento, valores_sorteados, filas_visibles, ultimas_filas, parametros)
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


def _registrar_fila_actual(
    estado: EstadoSimulacion,
    evento: str,
    valores_sorteados: dict[str, Any],
    filas_visibles: list[StateRow],
    ultimas_filas: deque[StateRow],
    parametros: SimulationParams,
) -> StateRow:
    """Arma detalle completo solo para j/i y deja una version resumida para las ultimas filas.

    Esta es una de las claves de memoria del proyecto:
    no todas las filas cargan todos los clientes activos.
    """
    fila_resumida = armar_fila_vector(estado, evento, valores_sorteados, omitir_temporales=True)
    ultimas_filas.append(fila_resumida)
    if _fila_esta_en_ventana_pedida(estado.nro_evento, parametros):
        fila_visible = armar_fila_vector(estado, evento, valores_sorteados, omitir_temporales=False)
        filas_visibles.append(fila_visible)
        return fila_visible
    return fila_resumida


def _fila_esta_en_ventana_pedida(nro_evento: int, parametros: SimulationParams) -> bool:
    return parametros.display_from <= nro_evento < parametros.display_from + parametros.display_count


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
        return ejecutar_llegada_cliente(estado)
    if nombre_evento == "fin_atencion_caja":
        return ejecutar_fin_atencion_caja(estado)
    if nombre_evento.startswith("fin_preparacion_mostrador_"):
        return ejecutar_fin_preparacion_mostrador(estado, int(dato_evento))
    if nombre_evento == "fin_permanencia_rojo":
        return ejecutar_fin_permanencia_rojo(estado, int(dato_evento))
    if nombre_evento == "fin_permanencia_azul":
        return ejecutar_fin_permanencia_azul(estado, int(dato_evento))
    if nombre_evento == "control_cola_mostrador_15min":
        return ejecutar_control_cola_mostrador_15min(estado)
    if nombre_evento == "control_salones_30min":
        return ejecutar_control_salones_30min(estado)
    return {}
