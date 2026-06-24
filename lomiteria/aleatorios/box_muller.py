"""Box-Muller para las llegadas, con memoria de un solo valor pendiente."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .distribuciones import siguiente_rnd


@dataclass(frozen=True)
class ValorNormalPendiente:
    """Segundo normal generado por Box-Muller y reservado para la proxima llamada."""

    rnd1: float
    rnd2: float
    normal_estandar: float
    formula_usada: str


@dataclass(frozen=True)
class SorteoNormalBoxMuller:
    """Resultado listo para usar en la simulacion de llegadas."""

    rnd1: float
    rnd2: float
    normal_estandar: float
    valor: float
    formula_usada: str
    origen: str


@dataclass
class EstadoBoxMuller:
    """Estado minimo necesario: solo guarda si quedo un normal pendiente por usar."""

    valor_pendiente: ValorNormalPendiente | None = None


def normal_positiva_con_memoria(
    estado_box_muller: EstadoBoxMuller,
    generador: random.Random,
    media: float,
    desviacion: float,
) -> SorteoNormalBoxMuller:
    """Devuelve un valor normal positivo.

    Pregunta principal:
    - Si ya habia un normal pendiente, se usa ese.
    - Si no habia ninguno, se generan dos normales nuevos con Box-Muller.
    """

    while True:
        normal_estandar, rnd1, rnd2, formula_usada, origen = _obtener_normal_estandar(
            estado_box_muller,
            generador,
        )
        valor = media + desviacion * normal_estandar
        if valor > 0:
            return SorteoNormalBoxMuller(
                rnd1=rnd1,
                rnd2=rnd2,
                normal_estandar=normal_estandar,
                valor=valor,
                formula_usada=formula_usada,
                origen=origen,
            )


def _obtener_normal_estandar(
    estado_box_muller: EstadoBoxMuller,
    generador: random.Random,
) -> tuple[float, float, float, str, str]:
    """Devuelve un normal estandar y resuelve toda la memoria de Box-Muller.

    Condicion que se evalua:
    - Si `valor_pendiente` existe: usarlo.
    - Si `valor_pendiente` no existe: generar dos nuevos y guardar uno.
    """

    if estado_box_muller.valor_pendiente is not None:
        pendiente = estado_box_muller.valor_pendiente
        estado_box_muller.valor_pendiente = None
        return (
            pendiente.normal_estandar,
            pendiente.rnd1,
            pendiente.rnd2,
            pendiente.formula_usada,
            "memoria",
        )

    rnd1 = _siguiente_rnd_no_cero(generador)
    rnd2 = siguiente_rnd(generador)
    factor = _modulo_box_muller(rnd1)
    normal_coseno = factor * math.cos(2.0 * math.pi * rnd2)
    normal_seno = factor * math.sin(2.0 * math.pi * rnd2)

    estado_box_muller.valor_pendiente = ValorNormalPendiente(
        rnd1=rnd1,
        rnd2=rnd2,
        normal_estandar=normal_seno,
        formula_usada="seno",
    )
    return normal_coseno, rnd1, rnd2, "coseno", "par_nuevo"


def _siguiente_rnd_no_cero(generador: random.Random) -> float:
    """Box-Muller necesita que el primer RND no sea cero porque usa ln(rnd1)."""

    return max(siguiente_rnd(generador), 1e-12)


def _modulo_box_muller(rnd1: float) -> float:
    """Parte comun de las dos formulas de Box-Muller."""

    return math.sqrt(-2.0 * math.log(rnd1))
