from __future__ import annotations


OBJECT_DEFINITIONS = [
    {
        "tipo": "Objeto permanente",
        "nombre": "Caja",
        "cantidad": "1",
        "atributos": ["estado", "cliente_actual", "hora_inicio_ocupacion", "ac_tiempo_ocupada"],
        "rol": "Servidor unico donde el cliente pide y paga.",
    },
    {
        "tipo": "Objeto permanente",
        "nombre": "Preparador",
        "cantidad": "parametro preparadores, por defecto 3",
        "atributos": ["id", "estado", "cliente_actual", "hora_inicio_ocupacion", "ac_tiempo_ocupado", "fin_preparacion_programado"],
        "rol": "Servidor del mostrador que prepara pedidos locales o para llevar.",
    },
    {
        "tipo": "Objeto permanente",
        "nombre": "Salon rojo",
        "cantidad": "1",
        "atributos": ["capacidad", "ocupacion", "cola_entrada", "ac_ocupacion_tiempo_persona", "max_ocupacion"],
        "rol": "Recurso de capacidad limitada para clientes que consumen en planta baja.",
    },
    {
        "tipo": "Objeto permanente",
        "nombre": "Salon azul",
        "cantidad": "1",
        "atributos": ["capacidad", "ocupacion", "cola_entrada", "ac_ocupacion_tiempo_persona", "max_ocupacion"],
        "rol": "Recurso de capacidad limitada para clientes que consumen en primer piso.",
    },
    {
        "tipo": "Objeto temporal",
        "nombre": "Cliente",
        "cantidad": "variable, solo clientes presentes en el sistema",
        "atributos": [
            "id",
            "estado",
            "hora_llegada_negocio",
            "hora_inicio_cola_caja",
            "hora_inicio_cola_mostrador",
            "hora_inicio_cola_salon",
            "tipo_consumo",
            "salon_elegido",
            "preparador_asignado",
            "a_preparacion",
            "tiempo_preparacion",
            "hora_inicio_permanencia",
            "hora_fin_programada",
        ],
        "rol": "Entidad que recorre caja, mostrador, salon o salida.",
    },
]


STATE_DEFINITIONS = [
    {"estado": "EAC", "descripcion": "Espera atencion en caja."},
    {"estado": "SAC", "descripcion": "Siendo atendido en caja."},
    {"estado": "EPM", "descripcion": "Espera preparacion en mostrador."},
    {"estado": "EASR", "descripcion": "Espera acceso al salon rojo por capacidad completa."},
    {"estado": "EASA", "descripcion": "Espera acceso al salon azul por capacidad completa."},
    {"estado": "PSR", "descripcion": "Permanece en salon rojo."},
    {"estado": "PSA", "descripcion": "Permanece en salon azul."},
]


STATISTIC_VARIABLE_DEFINITIONS = [
    {"variable": "ac_tiempo_permanencia_negocio", "descripcion": "Acumulador de tiempo total en el negocio de clientes finalizados."},
    {"variable": "ct_clientes_finalizados", "descripcion": "Cantidad de clientes que salieron del sistema."},
    {"variable": "ac_tiempo_cola_caja", "descripcion": "Acumulador de espera en cola de caja."},
    {"variable": "ct_clientes_pasan_por_caja", "descripcion": "Cantidad de clientes que inician atencion en caja."},
    {"variable": "ac_tiempo_cola_mostrador", "descripcion": "Acumulador de espera frente al mostrador."},
    {"variable": "ct_clientes_pasan_por_mostrador", "descripcion": "Cantidad de clientes que inician preparacion."},
    {"variable": "ac_ocupacion_caja", "descripcion": "Tiempo acumulado con la caja ocupada."},
    {"variable": "ac_ocupacion_preparador_i", "descripcion": "Tiempo acumulado ocupado por cada preparador."},
    {"variable": "ac_ocupacion_rojo_tiempo_persona", "descripcion": "Area bajo la curva de ocupacion del salon rojo."},
    {"variable": "ac_ocupacion_azul_tiempo_persona", "descripcion": "Area bajo la curva de ocupacion del salon azul."},
    {"variable": "max_cola_caja", "descripcion": "Mayor cantidad observada en cola de caja."},
    {"variable": "max_cola_mostrador", "descripcion": "Mayor cantidad observada en cola de mostrador."},
    {"variable": "max_ocupacion_rojo", "descripcion": "Mayor ocupacion observada en salon rojo."},
    {"variable": "max_ocupacion_azul", "descripcion": "Mayor ocupacion observada en salon azul."},
    {"variable": "ct_esperaron_rojo_lleno", "descripcion": "Clientes que debieron esperar porque el salon rojo estaba lleno."},
    {"variable": "ct_esperaron_azul_lleno", "descripcion": "Clientes que debieron esperar porque el salon azul estaba lleno."},
]
