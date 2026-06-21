# TP5 Simulacion - Lomiteria

Aplicativo en Python para simular por eventos discretos el sistema de la lomiteria.

## Ejecutar pruebas

```powershell
python -m unittest discover -s tests -v
```

## Ejecutar la aplicacion web

```powershell
python main.py
```

El comando levanta un servidor local y abre la interfaz web en el navegador:

- Modelo
- Configuracion
- Resultados
- Vector estado
- Controles
- Tablas y RK4

## Uso

1. Revisar el planteo en la pestana `Modelo`.
2. Configurar parametros en la pestana `Configuracion`.
3. Indicar `Tiempo X`, `Max iteraciones`, `Mostrar desde j` y `Cantidad i`.
4. Presionar `Simular`.
5. Revisar vector filtrable por categorias, ultimas 10 filas, metricas explicadas, variables estadisticas, controles, tablas intermedias y Runge-Kutta.

## Estructura

- `lomiteria/models.py`: dataclasses del dominio y estructura del resultado.
- `lomiteria/object_definitions.py`: catalogo explicativo de objetos permanentes, temporales, estados y variables estadisticas.
- `lomiteria/randoms.py`: formulas matematicas base para uniforme y normal positiva.
- `lomiteria/distributions.py`: generacion de cada variable aleatoria, RND usado y formula aplicada.
- `lomiteria/tables.py`: tablas intermedias y busquedas por RND.
- `lomiteria/rk4.py`: tablas Runge-Kutta.
- `lomiteria/metrics.py`: calculo de metricas y definicion de que punto del enunciado responde cada una.
- `lomiteria/state_vector.py`: columnas y armado del vector de estado por categorias.
- `lomiteria/simulator.py`: motor de eventos discretos; avanza desde la fila inmediata anterior.
- `lomiteria/web_server.py`: servidor HTTP local y API JSON.
- `web/`: interfaz web de presentacion.
- `main.py`: entrada de la aplicacion web.

El motor no guarda todo el vector en memoria. Solo conserva el estado actual, objetos activos, filas pedidas por `j/i`, las ultimas 10 filas, la ultima fila en X, metricas, controles y tablas auxiliares.
