# Spec de diseno - TP5 Simulacion: Lomiteria

Fecha: 2026-06-21

## 1. Objetivo

Desarrollar un aplicativo que simule por eventos discretos el sistema "Lomiteria" entre las 11:00 y las 15:00, mostrando el vector de estado con el mismo criterio usado en los parciales y soluciones revisadas: reloj, eventos, objetos permanentes, variables estadisticas y objetos temporales.

El aplicativo debe cumplir estrictamente estas pautas:

- Simular hasta 100000 iteraciones del vector de estado o hasta el tiempo `X`, lo que ocurra primero.
- Mostrar `i` iteraciones del vector de estado a partir de una iteracion `j`, ingresadas por parametro.
- Mostrar siempre la ultima fila correspondiente al instante `X`. En esa fila no es necesario mostrar objetos temporales.
- Permitir modificar por usuario todos los parametros del enunciado.
- Mostrar en detalle el estado del sistema y las columnas necesarias para calcular las metricas solicitadas.
- Mostrar el numero aleatorio usado para determinar cada variable aleatoria.
- Permitir conocer, para cualquier fila mostrada, todos los atributos de los objetos presentes en ese instante. No se muestran objetos que ya dejaron el sistema.
- Mostrar las tablas de Runge-Kutta calculadas.

## 2. Enfoque de solucion

Se usara simulacion por eventos discretos. El reloj avanzara al menor de los proximos eventos programados.

El reloj interno estara en minutos:

- `0` equivale a 11:00.
- `240` equivale a 15:00.
- El valor `X` por defecto sera `240`, modificable por el usuario.

El programa no guardara toda la simulacion en memoria. Cada fila se calculara usando solo el estado inmediatamente anterior:

1. Se tiene un `SimulationState` que representa la fila anterior.
2. Se selecciona el proximo evento con el menor tiempo programado.
3. Se actualizan acumuladores por el tiempo transcurrido desde la fila anterior.
4. Se ejecuta la logica del evento.
5. Se genera una `StateRow` nueva.
6. La fila se conserva solo si esta dentro del rango solicitado `j..j+i-1`, o si es la ultima fila de `X`.

Si el proximo evento real supera `X`, no se procesa ese evento: se avanza el reloj hasta `X`, se actualizan acumuladores hasta ese instante y se genera la fila `fin_simulacion`.

## 3. Lenguaje, paradigma y presentacion

Lenguaje: Python.

Paradigma:

- Procedural simple para el flujo principal de simulacion.
- `dataclass` para representar parametros, estado, servidores, salones, clientes, acumuladores y filas.
- Funciones pequenas para generar variables aleatorias, buscar en tablas intermedias, ejecutar eventos, calcular Runge-Kutta y convertir estado a fila de vector.

UI minima:

- `Tkinter`, por ser parte de Python estandar.
- Pantalla de parametros.
- Campos para `X`, maximo de iteraciones, `j` e `i`.
- Boton `Simular`.
- Tabla visual del vector mostrado.
- Panel de metricas.
- Vista o exportacion de tablas de Runge-Kutta.
- Exportacion CSV de vector mostrado, ultima fila, metricas, tablas intermedias y Runge-Kutta.

La UI sera minima e integrada para presentacion. La logica de simulacion quedara separada de la UI para poder probarla por consola.

## 4. Parametros modificables

Todos estos valores deben estar en `SimulationParams` y poder modificarse desde la UI:

- Tiempo final `X` en minutos.
- Maximo de iteraciones, por defecto `100000`.
- Iteracion inicial a mostrar `j`.
- Cantidad de iteraciones a mostrar `i`.
- Media de llegada: `1` minuto.
- Desvio de llegada: `0.5` minutos.
- Tiempo minimo de caja: `0.25` minutos.
- Tiempo maximo de caja: `0.75` minutos.
- Probabilidad de compra para llevar: `0.25`.
- Probabilidad de salon rojo para clientes locales: `0.30`.
- Capacidad salon rojo: `30`.
- Capacidad salon azul: `40`.
- Cantidad de preparadores: `3`.
- Preparacion para llevar minima: `100/60` minutos.
- Preparacion para llevar maxima: `140/60` minutos.
- Valores posibles de `A`: `2, 3, 4, 5`.
- `h` de Runge-Kutta: `0.01`.
- Valor limite de preparacion local: `L > 10`.
- Equivalencia de integracion: `t = 1` equivale a `10` minutos.
- Intervalo de control de cola mostrador: `15` minutos.
- Intervalo de control de salones: `30` minutos.
- Tiempos de permanencia por salon y franja horaria.

## 5. Eventos

Eventos no subindicados:

- `llegada_cliente`
- `fin_atencion_caja`
- `fin_permanencia_rojo`
- `fin_permanencia_azul`
- `control_cola_mostrador_15min`
- `control_salones_30min`
- `fin_simulacion`

Eventos subindicados:

- `fin_preparacion_mostrador_1`
- `fin_preparacion_mostrador_2`
- `fin_preparacion_mostrador_3`

La caja no lleva subindice porque hay una unica caja.

Los preparadores llevan subindice porque son tres servidores paralelos.

## 6. Objetos permanentes

### Caja

Tipo: objeto permanente, servidor.

Estados:

- `Libre`
- `Ocupada`

Atributos:

- `estado`
- `cliente_actual`
- `hora_inicio_ocupacion`
- `ac_tiempo_ocupada`

### Preparador

Tipo: objeto permanente, servidor paralelo.

Cantidad: `3`.

Estados:

- `Libre`
- `Ocupado`

Atributos:

- `id`
- `estado`
- `cliente_actual`
- `hora_inicio_ocupacion`
- `ac_tiempo_ocupado`
- `fin_preparacion_programado`

### Salon

Tipo: objeto permanente, recurso con capacidad.

Salones:

- Salon Rojo, capacidad por defecto `30`.
- Salon Azul, capacidad por defecto `40`.

Estados agregados:

- Ocupacion actual.
- Cola de entrada.

Atributos:

- `nombre`
- `capacidad`
- `ocupacion`
- `cola_entrada`
- `ac_ocupacion_tiempo_persona`
- `max_ocupacion`
- `clientes_que_esperaron_por_capacidad`

## 7. Objetos temporales

### Cliente

Tipo: objeto temporal.

Estados:

- `EAC`: esperando atencion en caja.
- `SAC`: siendo atendido en caja.
- `EPM`: esperando pedido/preparacion en mostrador.
- `EASR`: esperando asiento en salon rojo.
- `EASA`: esperando asiento en salon azul.
- `PSR`: permaneciendo en salon rojo.
- `PSA`: permaneciendo en salon azul.

No existira estado `SPM` en el cliente. Si el pedido esta siendo preparado, eso se representa en el preparador permanente ocupado con `cliente_actual`. El cliente puede seguir figurando como `EPM` hasta que finaliza la preparacion.

Atributos:

- `id`
- `estado`
- `hora_llegada_negocio`
- `hora_inicio_cola_caja`
- `hora_inicio_cola_mostrador`
- `hora_inicio_cola_salon`
- `tipo_consumo`: `llevar` o `local`
- `salon_elegido`: `rojo`, `azul` o vacio
- `preparador_asignado`
- `a_preparacion`
- `tiempo_preparacion`
- `hora_inicio_permanencia`
- `hora_fin_programada`

Cuando el cliente sale del sistema se calculan sus metricas y se elimina de la lista de objetos temporales activos.

## 8. Colas

Todas las colas son FIFO:

- Cola de caja.
- Cola frente al mostrador.
- Cola de entrada al salon rojo.
- Cola de entrada al salon azul.

Regla de capacidad de salones aprobada:

- Si el cliente eligio un salon y el salon esta lleno, espera en la cola de ese mismo salon.
- No cambia al otro salon.
- No se retira por falta de lugar.

## 9. Tablas intermedias

Las decisiones discretas por RND se resolveran mediante tablas intermedias, como en las planillas revisadas.

### Tipo de consumo

| Desde | Hasta | Resultado |
| ---: | ---: | --- |
| 0.00 | 0.249999 | Para llevar |
| 0.25 | 0.999999 | Consume local |

### Salon elegido

| Desde | Hasta | Resultado |
| ---: | ---: | --- |
| 0.00 | 0.299999 | Rojo |
| 0.30 | 0.999999 | Azul |

### A para preparacion local

| Desde | Hasta | A |
| ---: | ---: | ---: |
| 0.00 | 0.249999 | 2 |
| 0.25 | 0.499999 | 3 |
| 0.50 | 0.749999 | 4 |
| 0.75 | 0.999999 | 5 |

### Permanencia por horario

| Horario real | Reloj | Rojo | Azul |
| --- | --- | --- | --- |
| 11 a 12 | 0 a 60 | U(5, 35) | U(15, 45) |
| 12 a 13 | 60 a 120 | U(15, 45) | U(25, 55) |
| 13 a 14 | 120 a 180 | U(20, 50) | U(35, 55) |
| 14 a 15 | 180 a 240 | U(5, 35) | U(20, 50) |

La franja se determina al momento en que el cliente inicia su permanencia en el salon.

## 10. Variables aleatorias y formulas

### Llegada de clientes

Distribucion: normal `N(1, 0.5)` minutos, mayor a cero.

Se usara Box-Muller:

`Z = sqrt(-2 * ln(RND1)) * cos(2 * pi * RND2)`

`tiempo_entre_llegadas = media + desvio * Z`

Si el valor resulta `<= 0`, se descarta y se generan nuevos RND. En el vector se mostraran los RND usados finalmente.

### Caja

Distribucion: uniforme `U(0.25, 0.75)` minutos.

`tiempo_caja = 0.25 + RND * (0.75 - 0.25)`

### Tipo de consumo

Se genera un RND y se busca en la tabla intermedia de tipo de consumo.

### Salon

Solo si el cliente consume en local. Se genera un RND y se busca en la tabla intermedia de salon.

### A de preparacion local

Solo si el cliente consume en local. Se genera un RND y se busca en la tabla intermedia de `A`.

### Preparacion para llevar

Distribucion: uniforme `U(100/60, 140/60)` minutos.

`tiempo_llevar = 100/60 + RND * ((140 - 100) / 60)`

### Permanencia en salon

Se genera un RND al entrar al salon y se aplica la uniforme correspondiente a salon y franja horaria.

Ejemplo:

`permanencia_rojo_11_12 = 5 + RND * (35 - 5)`

## 11. Runge-Kutta para preparacion local

Ecuacion:

`dL/dt - 3A = 6`

Entonces:

`dL/dt = 6 + 3A`

Condiciones:

- `A` uniforme discreta entre `2` y `5`.
- `L0 = A`.
- `h = 0.01`.
- Pedido listo cuando `L > 10`.
- `t = 1` equivale a `10` minutos.

Tablas a mostrar:

- Una tabla para `A = 2`.
- Una tabla para `A = 3`.
- Una tabla para `A = 4`.
- Una tabla para `A = 5`.

Columnas:

- `t`
- `L`
- `k1`
- `k2`
- `k3`
- `k4`
- `L(i+1)`
- `t(i+1)`
- `A`
- `tiempo_min`

Como la derivada no depende de `t` ni de `L`:

- `k1 = 6 + 3A`
- `k2 = 6 + 3A`
- `k3 = 6 + 3A`
- `k4 = 6 + 3A`

Formula general:

`L(i+1) = L(i) + h/6 * (k1 + 2*k2 + 2*k3 + k4)`

`t(i+1) = t(i) + h`

Al encontrar la primera fila donde `L > 10`:

`tiempo_preparacion_local = t * 10`

## 12. Estructura del vector de estado

El vector se separara por categorias, siguiendo el estilo de los XLS.

### RELOJ / EVENTO

- `nro_evento`
- `evento`
- `reloj_min`
- `hora_real`

### EVENTOS

- `rnd_llegada_1`
- `rnd_llegada_2`
- `tiempo_entre_llegadas`
- `proxima_llegada`
- `rnd_caja`
- `tiempo_caja`
- `fin_caja`
- `rnd_tipo_consumo`
- `tipo_consumo`
- `rnd_salon`
- `salon`
- `rnd_a_preparacion`
- `a_preparacion`
- `tiempo_preparacion_local`
- `rnd_preparacion_llevar`
- `tiempo_preparacion_llevar`
- `fin_preparacion_1`
- `fin_preparacion_2`
- `fin_preparacion_3`
- `rnd_permanencia_salon`
- `tiempo_permanencia_salon`
- `fin_permanencia_rojo`
- `fin_permanencia_azul`
- `proximo_control_15`
- `proximo_control_30`

Las columnas de RND se completan solo en la fila en la que se usa esa variable aleatoria. En el resto de filas quedan vacias o con guion, como en los ejemplos.

### OBJETOS PERMANENTES

- `estado_caja`
- `cliente_caja`
- `cola_caja`
- `estado_preparador_1`
- `cliente_preparador_1`
- `estado_preparador_2`
- `cliente_preparador_2`
- `estado_preparador_3`
- `cliente_preparador_3`
- `cola_mostrador`
- `ocupacion_rojo`
- `cola_rojo`
- `ocupacion_azul`
- `cola_azul`

### VARIABLES ESTADISTICAS

- `ac_tiempo_permanencia_negocio`
- `ct_clientes_finalizados`
- `ac_tiempo_cola_caja`
- `ct_clientes_pasan_por_caja`
- `ac_tiempo_cola_mostrador`
- `ct_clientes_pasan_por_mostrador`
- `ac_ocupacion_caja`
- `ac_ocupacion_preparador_1`
- `ac_ocupacion_preparador_2`
- `ac_ocupacion_preparador_3`
- `ac_ocupacion_rojo_tiempo_persona`
- `ac_ocupacion_azul_tiempo_persona`
- `max_cola_caja`
- `max_cola_mostrador`
- `max_ocupacion_rojo`
- `max_ocupacion_azul`
- `ct_esperaron_rojo_lleno`
- `ct_esperaron_azul_lleno`
- `serie_control_cola_mostrador_15min`
- `serie_control_ocupacion_salones_30min`

### OBJETOS TEMPORALES

Para cada cliente activo:

- `cliente_n_estado`
- `cliente_n_hora_llegada`
- `cliente_n_tipo_consumo`
- `cliente_n_salon`
- `cliente_n_hora_inicio_cola_caja`
- `cliente_n_hora_inicio_cola_mostrador`
- `cliente_n_hora_inicio_cola_salon`
- `cliente_n_preparador_asignado`
- `cliente_n_hora_inicio_permanencia`
- `cliente_n_fin_programado`

No se muestran clientes que ya salieron del sistema.

En la fila final `fin_simulacion` no es obligatorio mostrar objetos temporales.

## 13. Logica de eventos

### Inicializacion

En la fila inicial:

- Reloj `0`.
- Caja libre.
- Tres preparadores libres.
- Salones con ocupacion `0`.
- Colas vacias.
- Acumuladores en `0`.
- Se genera la primera llegada.
- Se programan controles:
  - `control_cola_mostrador_15min = 15`.
  - `control_salones_30min = 30`.

### Llegada de cliente

1. Crear cliente temporal.
2. Registrar `hora_llegada_negocio`.
3. Generar proxima llegada.
4. Si caja libre:
   - Cliente pasa a `SAC`.
   - Caja pasa a `Ocupada`.
   - Se genera tiempo de caja.
   - Se programa `fin_atencion_caja`.
5. Si caja ocupada:
   - Cliente pasa a `EAC`.
   - Se registra `hora_inicio_cola_caja`.
   - Se agrega a cola de caja.

### Fin de atencion de caja

1. El cliente deja la caja.
2. Se genera tipo de consumo.
3. Si consume local, se genera salon y valor `A`.
4. El cliente pasa a `EPM`.
5. Se registra `hora_inicio_cola_mostrador`.
6. Si hay preparador libre:
   - Se asigna el cliente al preparador.
   - El preparador pasa a `Ocupado`.
   - Se calcula tiempo de preparacion:
     - Local: tabla Runge-Kutta segun `A`.
     - Llevar: uniforme `U(100/60, 140/60)`.
   - Se programa `fin_preparacion_mostrador_i`.
   - Se acumula tiempo de cola mostrador si corresponde.
7. Si no hay preparador libre:
   - Cliente queda en cola mostrador como `EPM`.
8. Luego se libera la caja o toma el siguiente cliente de cola:
   - Si hay cola caja, el primer cliente pasa de `EAC` a `SAC`.
   - Se acumula su tiempo en cola caja.
   - Se genera tiempo de caja y se programa nuevo fin caja.
   - Si no hay cola, caja queda libre y `fin_caja` queda vacio.

### Fin de preparacion mostrador i

1. Se identifica el cliente del preparador `i`.
2. Si es para llevar:
   - El cliente sale del sistema.
   - Se acumula permanencia en negocio.
   - Se elimina de objetos temporales.
3. Si es local:
   - Se consulta disponibilidad del salon elegido.
   - Si hay lugar:
     - Entra al salon.
     - Cambia a `PSR` o `PSA`.
     - Se incrementa ocupacion del salon.
     - Se genera tiempo de permanencia segun salon y horario.
     - Se programa `fin_permanencia_rojo` o `fin_permanencia_azul`.
   - Si no hay lugar:
     - Cambia a `EASR` o `EASA`.
     - Registra `hora_inicio_cola_salon`.
     - Entra en cola del salon elegido.
     - Se incrementa contador de clientes que esperaron por capacidad.
4. El preparador `i` toma el siguiente cliente de cola mostrador si existe:
   - Se asigna el cliente.
   - Se acumula tiempo de cola mostrador.
   - Se calcula y programa el nuevo fin de preparacion.
5. Si no hay cola mostrador, el preparador queda libre.

### Fin de permanencia rojo

1. Sale un cliente del salon rojo.
2. Se acumula permanencia en negocio.
3. Se elimina el cliente de objetos temporales.
4. Si hay cola del salon rojo:
   - Entra el primer cliente de la cola.
   - Pasa a `PSR`.
   - Se genera tiempo de permanencia segun horario actual.
   - Se programa su fin de permanencia.
5. Si no hay cola, baja la ocupacion y queda libre un lugar.

### Fin de permanencia azul

Misma logica que rojo, aplicada al salon azul.

### Control cola mostrador cada 15 minutos

1. Registrar en la serie estadistica:
   - Hora de control.
   - Cantidad de clientes en cola mostrador.
2. Programar siguiente control sumando `15`, si no supera `X`.

### Control salones cada 30 minutos

1. Registrar en la serie estadistica:
   - Hora de control.
   - Ocupacion salon rojo.
   - Ocupacion salon azul.
2. Programar siguiente control sumando `30`, si no supera `X`.

## 14. Actualizacion de acumuladores por tramo

Antes de procesar cada evento se calcula:

`delta = reloj_nuevo - reloj_anterior`

Con ese delta:

- Si caja ocupada: `ac_ocupacion_caja += delta`.
- Si preparador ocupado: `ac_ocupacion_preparador_i += delta`.
- `ac_ocupacion_rojo_tiempo_persona += ocupacion_rojo * delta`.
- `ac_ocupacion_azul_tiempo_persona += ocupacion_azul * delta`.

Las colas promedio no son obligatorias, pero si se agregan luego se calcularan igual: cantidad en cola por `delta`.

## 15. Metricas

Metricas obligatorias:

- Tiempo promedio de permanencia en negocio:
  `ac_tiempo_permanencia_negocio / ct_clientes_finalizados`
- Tiempo promedio en cola caja:
  `ac_tiempo_cola_caja / ct_clientes_pasan_por_caja`
- Serie cada 15 minutos:
  cantidad de gente en cola frente al mostrador.
- Serie cada 30 minutos:
  cantidad de personas en salon rojo y salon azul por separado.

Metricas adicionales:

- Tiempo promedio en cola mostrador:
  `ac_tiempo_cola_mostrador / ct_clientes_pasan_por_mostrador`
- Porcentaje de ocupacion de caja:
  `ac_ocupacion_caja / reloj_final * 100`
- Porcentaje de ocupacion de preparadores:
  `(ac_prep1 + ac_prep2 + ac_prep3) / (3 * reloj_final) * 100`
- Cantidad y porcentaje de clientes que esperaron por salon lleno:
  - Rojo: `ct_esperaron_rojo_lleno`
  - Azul: `ct_esperaron_azul_lleno`
  - Total sobre clientes locales finalizados si el denominador esta disponible.

## 16. Reglas de memoria

El programa no debe depender del historial completo del vector.

Estructuras permitidas:

- Estado actual del sistema.
- Clientes activos.
- Colas activas.
- Acumuladores.
- Filas seleccionadas para mostrar.
- Ultima fila.
- Series de controles de 15 y 30 minutos.
- Tablas intermedias.
- Tablas Runge-Kutta.

No se guardaran todas las filas si no estan dentro del rango `j..j+i-1`.

## 17. Formato de salida

La salida minima integrada tendra:

- Tabla del vector para las filas pedidas.
- Ultima fila en `X`.
- Tabla de metricas.
- Tabla de controles cada 15 minutos.
- Tabla de controles cada 30 minutos.
- Tablas de Runge-Kutta para `A = 2,3,4,5`.
- Tablas intermedias de tipo, salon, `A` y permanencia.

La exportacion CSV se separara en archivos o secciones:

- `vector_estado.csv`
- `ultima_fila.csv`
- `metricas.csv`
- `controles_15min.csv`
- `controles_30min.csv`
- `runge_kutta_A2.csv`, `runge_kutta_A3.csv`, `runge_kutta_A4.csv`, `runge_kutta_A5.csv`
- `tablas_intermedias.csv`

## 18. Criterios de aceptacion

El aplicativo queda aceptado si:

- Permite simular hasta `100000` iteraciones o hasta `X`.
- Muestra exactamente `i` filas desde `j`, salvo que la simulacion termine antes.
- Muestra siempre la fila final en `X`.
- No guarda todo el vector en memoria.
- Todos los parametros del enunciado son modificables.
- Cada variable aleatoria muestra su RND en la fila donde se usa.
- El vector esta separado en las categorias aprobadas.
- Las filas mostradas permiten reconstruir los atributos de objetos activos.
- No aparecen objetos temporales que ya salieron del sistema.
- La fila final puede omitir objetos temporales.
- Se muestran tablas intermedias y tablas Runge-Kutta.
- Las metricas obligatorias y las cuatro adicionales se calculan desde acumuladores visibles en el vector.
