from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


INF = float("inf")


@dataclass
class SimulationParams:
    x_minutes: float = 240.0
    max_iterations: int = 100000
    display_from: int = 1
    display_count: int = 20
    seed: int | None = None

    llegada_media: float = 1.0
    llegada_desvio: float = 0.5
    caja_min: float = 0.25
    caja_max: float = 0.75
    prob_llevar: float = 0.25
    prob_rojo: float = 0.30
    capacidad_rojo: int = 30
    capacidad_azul: int = 40
    preparadores: int = 3
    llevar_min: float = 100.0 / 60.0
    llevar_max: float = 140.0 / 60.0
    a_values: tuple[int, ...] = (2, 3, 4, 5)
    rk_h: float = 0.01
    rk_limit_l: float = 10.0
    rk_minutes_per_unit: float = 10.0
    control_mostrador_interval: float = 15.0
    control_salones_interval: float = 30.0
    rojo_11_min: float = 5.0
    rojo_11_max: float = 35.0
    rojo_12_min: float = 15.0
    rojo_12_max: float = 45.0
    rojo_13_min: float = 20.0
    rojo_13_max: float = 50.0
    rojo_14_min: float = 5.0
    rojo_14_max: float = 35.0
    azul_11_min: float = 15.0
    azul_11_max: float = 45.0
    azul_12_min: float = 25.0
    azul_12_max: float = 55.0
    azul_13_min: float = 35.0
    azul_13_max: float = 55.0
    azul_14_min: float = 20.0
    azul_14_max: float = 50.0


@dataclass
class Cliente:
    id: int
    estado: str
    hora_llegada_negocio: float
    hora_inicio_cola_caja: float | None = None
    hora_inicio_cola_mostrador: float | None = None
    hora_inicio_cola_salon: float | None = None
    tipo_consumo: str = ""
    salon_elegido: str = ""
    preparador_asignado: int | None = None
    a_preparacion: int | None = None
    tiempo_preparacion: float | None = None
    hora_inicio_permanencia: float | None = None
    hora_fin_programada: float | None = None


@dataclass
class Caja:
    estado: str = "Libre"
    cliente_actual: int | None = None
    hora_inicio_ocupacion: float | None = None
    ac_tiempo_ocupada: float = 0.0


@dataclass
class Preparador:
    id: int
    estado: str = "Libre"
    cliente_actual: int | None = None
    hora_inicio_ocupacion: float | None = None
    ac_tiempo_ocupado: float = 0.0
    fin_preparacion_programado: float = INF


@dataclass
class Salon:
    nombre: str
    capacidad: int
    ocupacion: int = 0
    cola_entrada: list[int] = field(default_factory=list)
    ac_ocupacion_tiempo_persona: float = 0.0
    max_ocupacion: int = 0
    clientes_que_esperaron_por_capacidad: int = 0


@dataclass
class Estadisticas:
    ac_tiempo_permanencia_negocio: float = 0.0
    ct_clientes_finalizados: int = 0
    ac_tiempo_cola_caja: float = 0.0
    ct_clientes_pasan_por_caja: int = 0
    ac_tiempo_cola_mostrador: float = 0.0
    ct_clientes_pasan_por_mostrador: int = 0
    max_cola_caja: int = 0
    max_cola_mostrador: int = 0
    ct_esperaron_rojo_lleno: int = 0
    ct_esperaron_azul_lleno: int = 0


@dataclass
class StateRow:
    nro_evento: int
    evento: str
    reloj_min: float
    hora_real: str
    eventos: dict[str, Any]
    objetos_permanentes: dict[str, Any]
    variables_estadisticas: dict[str, Any]
    objetos_temporales: dict[str, Any] = field(default_factory=dict)

    def as_grouped_dict(self) -> dict[str, dict[str, Any]]:
        return {
            "RELOJ_EVENTO": {
                "nro_evento": self.nro_evento,
                "evento": self.evento,
                "reloj_min": self.reloj_min,
                "hora_real": self.hora_real,
            },
            "EVENTOS": self.eventos,
            "OBJETOS_PERMANENTES": self.objetos_permanentes,
            "VARIABLES_ESTADISTICAS": self.variables_estadisticas,
            "OBJETOS_TEMPORALES": self.objetos_temporales,
        }

    def flat_dict(self) -> dict[str, Any]:
        flat: dict[str, Any] = {}
        for _, group in self.as_grouped_dict().items():
            flat.update(group)
        return flat


@dataclass
class SimulationResult:
    rows: list[StateRow]
    last_rows: list[StateRow]
    final_row: StateRow
    metrics: dict[str, float]
    controls_15: list[dict[str, Any]]
    controls_30: list[dict[str, Any]]
    rk4_tables: dict[int, list[dict[str, float]]]
    intermediate_tables: dict[str, list[dict[str, Any]]]
    total_iterations: int
