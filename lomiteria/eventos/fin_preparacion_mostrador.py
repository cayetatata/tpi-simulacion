"""Evento fin_preparacion_mostrador_i."""
from __future__ import annotations

from typing import Any

from ..modelo.objetos import INF
from ..simulacion.operaciones_estado import entrar_o_esperar_salon, finalizar_cliente, iniciar_preparacion


def ejecutar_fin_preparacion_mostrador(estado: Any, id_preparador: int) -> dict[str, Any]:
    """Procesa el fin de preparacion del preparador indicado."""
    preparador = estado.preparadores[id_preparador - 1]
    id_cliente = preparador.cliente_actual
    valores_sorteados: dict[str, Any] = {}

    if id_cliente is not None and id_cliente in estado.clientes:
        cliente = estado.clientes[id_cliente]
        if cliente.tipo_consumo == "llevar":
            finalizar_cliente(estado, id_cliente)
        else:
            valores_sorteados.update(entrar_o_esperar_salon(estado, id_cliente))

    if estado.cola_mostrador:
        siguiente_cliente = estado.cola_mostrador.popleft()
        valores_sorteados.update(iniciar_preparacion(estado, preparador, siguiente_cliente))
        return valores_sorteados

    preparador.estado = "Libre"
    preparador.cliente_actual = None
    preparador.hora_inicio_ocupacion = None
    preparador.fin_preparacion_programado = INF
    return valores_sorteados

