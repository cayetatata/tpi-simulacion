# TP5 Simulacion - Lomiteria

Aplicativo en Python para simular por eventos discretos el sistema de la lomiteria.

## Ejecutar pruebas

```powershell
python -m unittest discover -s tests -v
```

## Ejecutar la aplicacion

```powershell
python main.py
```

La aplicacion abre una interfaz Tkinter con pestanas:

- Parametros
- Vector
- Ultima fila
- Metricas
- Control 15 min
- Control 30 min
- Tablas
- Runge-Kutta

## Uso

1. Configurar parametros en la pestana `Parametros`.
2. Indicar `Tiempo X`, `Max iteraciones`, `Mostrar desde j` y `Cantidad i`.
3. Presionar `Simular`.
4. Revisar vector, metricas, controles, tablas intermedias y Runge-Kutta.
5. Presionar `Exportar CSV` para guardar los resultados.

## Estructura

- `lomiteria/models.py`: dataclasses del dominio.
- `lomiteria/tables.py`: tablas intermedias y busquedas por RND.
- `lomiteria/randoms.py`: formulas aleatorias.
- `lomiteria/rk4.py`: tablas Runge-Kutta.
- `lomiteria/simulator.py`: motor de eventos discretos.
- `lomiteria/exporter.py`: exportacion CSV.
- `lomiteria/ui.py`: interfaz Tkinter.
- `main.py`: entrada de la aplicacion.

El motor no guarda todo el vector en memoria. Solo conserva el estado actual, objetos activos, filas pedidas, ultima fila, metricas, controles y tablas auxiliares.
