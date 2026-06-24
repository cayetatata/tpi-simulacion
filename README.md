# TP5 Simulacion - Lomiteria

Aplicativo en Python para simular por eventos discretos el sistema de la lomiteria.

## Ejecutar

Pruebas:

```powershell
python -m unittest discover -s tests -v
```

Aplicacion web:

```powershell
python main.py
```

Servidor local:

- [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Objetivo del proyecto

El proyecto busca trasladar una simulacion que en cursada suele resolverse en Excel a un codigo Python claro, legible y eficiente en memoria.

Objetivos principales:

1. simular por eventos discretos hasta `X` minutos o hasta `100000` iteraciones;
2. mostrar solo las filas pedidas del vector de estado y las ultimas `10`;
3. dejar trazabilidad de los `RND`, tiempos y decisiones tomadas en cada fila;
4. calcular metricas pedidas por el enunciado y metricas adicionales utiles para defender el modelo.

## Idea general

La simulacion siempre trabaja sobre una sola foto viva del sistema, llamada `EstadoSimulacion`.

Esa foto guarda:

- reloj actual;
- proximos eventos programados;
- caja;
- preparadores;
- salones;
- clientes que siguen dentro del sistema;
- colas;
- acumuladores estadisticos;
- memoria pendiente de Box-Muller.

No se guardan `100000` filas completas en memoria. Se guarda:

- el estado actual;
- las filas pedidas por el usuario;
- las ultimas `10` filas;
- la fila final;
- los controles y tablas necesarias para mostrar resultados.

## Mapa de carpetas

### `lomiteria/modelo/`

Define que existe y que datos guarda cada objeto.

- `objetos.py`
  - `SimulationParams`: todos los parametros editables;
  - `Cliente`: objeto temporal;
  - `Caja`, `Preparador`, `Salon`: objetos permanentes;
  - `Estadisticas`: acumuladores y contadores;
  - `StateRow`: fila del vector;
  - `SimulationResult`: salida final de la corrida.

### `lomiteria/aleatorios/`

Solo formulas y reglas de decision basadas en `RND`.

- `distribuciones.py`
  - `siguiente_rnd(generador)`: toma un `RND` uniforme de Python en `[0,1)`;
  - `uniforme(rnd, minimo, maximo)`: aplica `minimo + rnd * (maximo - minimo)`.
- `box_muller.py`
  - Box-Muller para las llegadas;
  - reutiliza el segundo normal generado para no desperdiciar el par.
- `tablas_probabilidad.py`
  - decide tipo de consumo;
  - decide salon;
  - decide valor `A`;
  - define los rangos horarios de permanencia.

### `lomiteria/calculos/`

Calculos puros, sin manejo de reloj ni colas.

- `runge_kutta_preparacion.py`
  - construye la tabla RK4 por cada valor de `A`;
  - devuelve tambien el tiempo final de preparacion para usar en la simulacion.
- `metricas.py`
  - transforma acumuladores finales en indicadores legibles.

### `lomiteria/eventos/`

Un archivo por cada evento real del vector de estado.

- `llegada_cliente.py`
- `fin_atencion_caja.py`
- `fin_preparacion_mostrador.py`
- `fin_permanencia_rojo.py`
- `fin_permanencia_azul.py`
- `control_cola_mostrador_15min.py`
- `control_salones_30min.py`

Regla:

- si puede aparecer como nombre de fila en la columna `Evento`, va en `eventos/`;
- si es un paso interno compartido, va en `simulacion/`.

### `lomiteria/simulacion/`

Coordina todo el sistema.

- `motor.py`
  - crea el estado inicial;
  - decide el proximo evento;
  - mueve el reloj;
  - ejecuta el evento correcto;
  - guarda solo las filas necesarias.
- `operaciones_estado.py`
  - pasos internos repetidos que usan varios eventos;
  - ejemplo: iniciar atencion, iniciar preparacion, iniciar permanencia.
- `vector_estado.py`
  - arma cada fila como si fuera una fila de Excel.

### `lomiteria/interfaz/`

Conecta la web con la simulacion.

- `servidor_web.py`
  - recibe pedidos HTTP;
  - convierte JSON a `SimulationParams`;
  - llama a `simulate(...)`;
  - devuelve JSON para el frontend.

### `web/`

Frontend HTML/CSS/JS.

- muestra pestañas;
- arma el formulario de parametros;
- hace `fetch("/api/simulate")`;
- renderiza vector, metricas, controles y RK4.

## Flujo simple de la simulacion

Pseudocodigo de alto nivel:

```text
crear estado inicial
construir RK4
programar primera llegada

mientras no llegue a X y no llegue a 100000:
    buscar el menor proximo evento
    mover el reloj hasta ese tiempo
    ejecutar ese evento
    armar la nueva fila del vector

devolver resultados
```

## Flujo tecnico completo

### 1. Entrada desde la web

Archivo:

- `main.py`
- `lomiteria/interfaz/servidor_web.py`

Flujo:

```text
usuario completa formulario
frontend arma JSON
frontend hace POST /api/simulate
backend recibe JSON
backend convierte JSON -> SimulationParams
backend llama simulate(...)
backend convierte SimulationResult -> JSON
frontend dibuja resultados
```

Puntos reales del codigo:

- `params_from_payload(payload)`: convierte texto del form a tipos Python;
- `simulate(parametros)`: corre la simulacion;
- `result_to_payload(result)`: convierte el resultado a JSON para UI.

## Como se comunican frontend y backend

### Request

El frontend envía:

```json
{
  "x_minutes": "240",
  "max_iterations": "100000",
  "display_from": "1",
  "display_count": "20",
  "llegada_media": "1",
  "a_values": "2,3,4,5"
}
```

### Backend

`params_from_payload(...)`:

- convierte `max_iterations`, `display_from`, `preparadores`, capacidades y `seed` a `int`;
- convierte el resto numérico a `float`;
- convierte `a_values` a tupla de enteros.

### Response

El backend devuelve un JSON con:

- `summary`
- `vector_rows`
- `last_rows`
- `final_row`
- `metrics`
- `controls_15`
- `controls_30`
- `rk4_tables`
- `intermediate_tables`

## Motor de simulacion

Archivo:

- `lomiteria/simulacion/motor.py`

### Funcion principal: `simulate(parametros)`

Entradas:

- un objeto `SimulationParams`

Salida:

- un `SimulationResult`

Que hace:

1. construye RK4 y obtiene tiempos de preparacion local;
2. crea `EstadoSimulacion`;
3. genera la primera llegada;
4. entra al `while` principal;
5. en cada iteracion:
   - busca el menor evento;
   - mueve el reloj;
   - ejecuta el evento;
   - arma la fila del vector;
6. al final devuelve resultados y metricas.

### Funcion clave: `_proximo_evento(estado)`

Entrada:

- el estado actual

Salida:

- `(nombre_evento, tiempo_evento, dato_evento)`

Que compara:

- `estado.proxima_llegada`
- `estado.fin_caja`
- `preparador.fin_preparacion_programado` de cada preparador
- proxima salida del salon rojo
- proxima salida del salon azul
- `estado.proximo_control_15`
- `estado.proximo_control_30`

Regla:

- gana el menor tiempo;
- si hay empate, gana la prioridad configurada en la tupla.

### Funcion clave: `_avanzar_reloj(estado, nuevo_reloj)`

Antes de cambiar el reloj:

- suma ocupacion de caja si la caja estaba ocupada;
- suma ocupacion de preparadores si estaban ocupados;
- suma ocupacion-persona de cada salon.

Despues:

- actualiza `estado.reloj = nuevo_reloj`.

### Funcion clave: `_procesar_evento(estado, nombre_evento, dato_evento)`

Despacha al archivo de evento correcto.

Ejemplos:

- `llegada_cliente` -> `eventos/llegada_cliente.py`
- `fin_atencion_caja` -> `eventos/fin_atencion_caja.py`
- `fin_preparacion_mostrador_2` -> `eventos/fin_preparacion_mostrador.py` con `id_preparador = 2`

## Eventos y operaciones de estado

### Que es un evento

Es una fila posible del vector.

Ejemplos:

- `llegada_cliente`
- `fin_atencion_caja`
- `fin_preparacion_mostrador_i`
- `fin_permanencia_rojo`

### Que es una operacion de estado

Es un paso interno reutilizable que no compite en el reloj por si mismo.

Ejemplos:

- `iniciar_atencion_caja(...)`
- `iniciar_preparacion(...)`
- `iniciar_permanencia_salon(...)`

### Relacion entre ambos

Un evento puede llamar una o varias operaciones de estado.

Ejemplo simple:

```text
ocurre llegada_cliente
si la caja esta libre:
    llamar iniciar_atencion_caja(...)
    esa operacion programa fin_caja
```

Importante:

- `iniciar_atencion_caja` no es el evento del reloj;
- deja programado el evento futuro `fin_atencion_caja`.

## Como se modela quien atiende a quien

### Caja

Variables en `Caja`:

- `estado`
- `cliente_actual`
- `hora_inicio_ocupacion`
- `ac_tiempo_ocupada`

Interpretacion:

- `cliente_actual` dice qué cliente está siendo atendido ahora en caja;
- `hora_inicio_ocupacion` y `ac_tiempo_ocupada` sirven para calcular ocupacion.

### Preparador

Variables en `Preparador`:

- `id`
- `estado`
- `cliente_actual`
- `hora_inicio_ocupacion`
- `ac_tiempo_ocupado`
- `fin_preparacion_programado`

Interpretacion:

- `cliente_actual` dice qué cliente está atendiendo ese preparador;
- `fin_preparacion_programado` dice cuándo termina esa preparación.

### Salon

Variables en `Salon`:

- `ocupacion`
- `cola_entrada`
- `salidas_programadas`
- `ac_ocupacion_tiempo_persona`
- `max_ocupacion`
- `clientes_que_esperaron_por_capacidad`

Interpretacion:

- `cola_entrada` guarda IDs de clientes esperando lugar;
- `salidas_programadas` guarda pares `(tiempo_salida, id_cliente)`.

### Cliente

Variables en `Cliente`:

- `estado`
- `hora_llegada_negocio`
- `hora_inicio_cola_caja`
- `hora_inicio_cola_mostrador`
- `hora_inicio_cola_salon`
- `tipo_consumo`
- `salon_elegido`
- `a_preparacion`
- `tiempo_preparacion`
- `hora_inicio_permanencia`
- `hora_fin_programada`

Interpretacion:

- `hora_fin_programada` guarda el fin de la etapa activa actual del cliente;
- si está en preparación, es fin de preparación;
- si está en salón, es fin de permanencia.

## Variables estadisticas y por que existen

### Acumuladores globales en `Estadisticas`

- `ac_tiempo_permanencia_negocio`
- `ct_clientes_finalizados`
- `ac_tiempo_cola_caja`
- `ct_clientes_pasan_por_caja`
- `ac_tiempo_cola_mostrador`
- `ct_clientes_pasan_por_mostrador`
- `max_cola_caja`
- `max_cola_mostrador`
- `ct_esperaron_rojo_lleno`
- `ct_esperaron_azul_lleno`

Sirven para calcular:

- tiempo promedio de permanencia;
- tiempo promedio de cola de caja;
- tiempo promedio de cola de mostrador;
- máximos de cola;
- clientes que esperaron por salón lleno.

### Variables extra agregadas en objetos permanentes

Adicionales al enunciado, necesarias para calcular ocupaciones:

- `caja.ac_tiempo_ocupada`
- `preparador.ac_tiempo_ocupado`
- `salon.ac_ocupacion_tiempo_persona`
- `salon.max_ocupacion`

Estas variables permiten calcular explícitamente cuatro métricas adicionales:

1. `tiempo_promedio_cola_mostrador`
2. `porcentaje_ocupacion_caja`
3. `porcentaje_ocupacion_preparadores`
4. `clientes_esperaron_salon_lleno_total`

## Metricas finales

Archivo:

- `lomiteria/calculos/metricas.py`

### Metricas pedidas por el enunciado

1. `tiempo_promedio_permanencia_negocio`
   - formula: `ac_tiempo_permanencia_negocio / ct_clientes_finalizados`
2. `tiempo_promedio_cola_caja`
   - formula: `ac_tiempo_cola_caja / ct_clientes_pasan_por_caja`
3. `control_15_cola_mostrador`
   - lectura directa de controles cada 15 minutos
4. `control_30_ocupacion_salones`
   - lectura directa de controles cada 30 minutos

### Metricas adicionales explicitas

1. `tiempo_promedio_cola_mostrador`
2. `porcentaje_ocupacion_caja`
3. `porcentaje_ocupacion_preparadores`
4. `clientes_esperaron_salon_lleno_total`

## Vector de estado

Archivo:

- `lomiteria/simulacion/vector_estado.py`

El vector no decide nada. Solo toma el estado actual y lo transforma en una fila legible.

### Funcion principal: `armar_fila_vector(...)`

Entrada:

- `estado`
- `evento`
- `valores_aleatorios`
- `omitir_temporales`

Salida:

- un `StateRow`

### Secciones del vector

- `RELOJ_EVENTO`
- `EVENTOS`
- `OBJETOS_PERMANENTES`
- `VARIABLES_ESTADISTICAS`
- `OBJETOS_TEMPORALES`

### Que muestra cada sección

#### `EVENTOS`

Muestra:

- RND usados;
- valor calculado por cada sorteo;
- próximos eventos programados.

#### `OBJETOS_PERMANENTES`

Muestra:

- estado de la caja;
- cliente actual de la caja;
- colas;
- estado y cliente de cada preparador;
- ocupación y cola de cada salón.

#### `VARIABLES_ESTADISTICAS`

Muestra acumuladores y contadores del estado actual.

#### `OBJETOS_TEMPORALES`

Muestra solo clientes activos. Los que ya salieron del sistema no se muestran.

## Como se guardan las filas

En `motor.py` se guardan tres conjuntos:

1. `filas_visibles`
   - solo desde `j` y durante `i` filas;
   - incluye objetos temporales.
2. `ultimas_filas`
   - solo las ultimas `10`;
   - resumidas.
3. `fila_final`
   - la fila del instante `X` o del límite de iteraciones.

Esto mantiene el uso de memoria acotado.

## Flujo de ida y vuelta entre componentes

Pseudocodigo de comunicación:

```text
frontend
    -> POST /api/simulate con JSON

interfaz
    -> params_from_payload(...)
    -> simulate(...)
    -> result_to_payload(...)

motor
    -> _proximo_evento(...)
    -> _avanzar_reloj(...)
    -> _procesar_evento(...)

evento
    -> puede llamar operaciones_estado(...)
    -> modifica objetos y acumuladores
    -> devuelve rnd y tiempos de esa fila

vector_estado
    -> lee el estado actualizado
    -> arma la fila para mostrar

frontend
    -> renderiza KPI, vector, controles, tablas y RK4
```

## Ejemplo corto de comunicación interna

Caso: llega un cliente y la caja está libre.

```text
motor ejecuta llegada_cliente
llegada_cliente crea cliente nuevo
llegada_cliente llama iniciar_atencion_caja(...)
iniciar_atencion_caja:
    ocupa caja
    marca cliente como SAC
    sortea tiempo de caja
    deja programado fin_caja
motor vuelve
motor arma la fila del vector
mas tarde, si fin_caja es el menor tiempo, motor ejecuta fin_atencion_caja
```

## Que pruebas validan el proyecto

Se ejecutan con:

```powershell
python -m unittest discover -s tests -v
```

Cobertura principal:

- simulacion correcta de flujo base;
- almacenamiento acotado de filas;
- corrida real hasta `100000` iteraciones;
- conversión completa de todos los parametros editables desde la web;
- corrida con todos los parametros modificados;
- serialización JSON del resultado;
- contrato mínimo de la UI.

## Resumen de estudio rapido

Si hay que explicarlo en dos minutos:

1. `modelo` define objetos y atributos;
2. `aleatorios` transforma `RND` en tiempos y decisiones;
3. `calculos` hace RK4 y métricas;
4. `eventos` ejecuta cada evento visible del vector;
5. `simulacion` administra reloj, memoria y vector;
6. `interfaz` conecta web y backend;
7. el motor compara próximos tiempos, ejecuta el menor y arma una nueva fila;
8. el vector solo muestra el estado actual ya calculado.
