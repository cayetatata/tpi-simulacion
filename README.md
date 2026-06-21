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
5. Revisar vector filtrable por categorias, metricas explicadas, controles, tablas intermedias y Runge-Kutta.

## Estructura

- `lomiteria/models.py`: dataclasses del dominio.
- `lomiteria/tables.py`: tablas intermedias y busquedas por RND.
- `lomiteria/randoms.py`: formulas aleatorias.
- `lomiteria/rk4.py`: tablas Runge-Kutta.
- `lomiteria/simulator.py`: motor de eventos discretos.
- `lomiteria/web_server.py`: servidor HTTP local y API JSON.
- `web/`: interfaz web de presentacion.
- `main.py`: entrada de la aplicacion web.

El motor no guarda todo el vector en memoria. Solo conserva el estado actual, objetos activos, filas pedidas, ultima fila, metricas, controles y tablas auxiliares.
