# Lomiteria Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a simple Python/Tkinter simulator for TP5 Lomiteria that follows the approved vector-state spec and stays memory efficient for 100000 iterations.

**Architecture:** The simulation engine is independent from the UI. The engine stores only the current state, active temporary objects, requested visible rows, the final row, metrics, control series, intermediate tables, and RK4 tables. Tkinter reads parameters, calls the engine, and displays results in tabs.

**Tech Stack:** Python standard library only: `dataclasses`, `random`, `math`, `csv`, `tkinter`, `unittest`.

---

### Task 1: Domain Model And Tables

**Files:**
- Create: `lomiteria/__init__.py`
- Create: `lomiteria/models.py`
- Create: `lomiteria/tables.py`
- Test: `tests/test_tables.py`

- [ ] **Step 1: Write failing tests for table lookups and defaults**

```python
from lomiteria.models import SimulationParams
from lomiteria.tables import lookup_a_value, lookup_salon, lookup_tipo_consumo, permanence_range


def test_tipo_consumo_table_boundaries():
    params = SimulationParams()
    assert lookup_tipo_consumo(0.0, params) == "llevar"
    assert lookup_tipo_consumo(0.249, params) == "llevar"
    assert lookup_tipo_consumo(0.25, params) == "local"
    assert lookup_tipo_consumo(0.99, params) == "local"


def test_salon_table_boundaries():
    params = SimulationParams()
    assert lookup_salon(0.0, params) == "rojo"
    assert lookup_salon(0.299, params) == "rojo"
    assert lookup_salon(0.30, params) == "azul"
    assert lookup_salon(0.99, params) == "azul"


def test_a_value_uses_four_equal_intervals():
    params = SimulationParams()
    assert lookup_a_value(0.00, params) == 2
    assert lookup_a_value(0.26, params) == 3
    assert lookup_a_value(0.50, params) == 4
    assert lookup_a_value(0.99, params) == 5


def test_permanence_range_uses_clock_minute_band():
    assert permanence_range("rojo", 0) == (5.0, 35.0)
    assert permanence_range("rojo", 60) == (15.0, 45.0)
    assert permanence_range("azul", 120) == (35.0, 55.0)
    assert permanence_range("azul", 180) == (20.0, 50.0)
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_tables -v`

Expected: fails because `lomiteria` modules do not exist.

- [ ] **Step 3: Implement models and tables**

Create focused dataclasses for params, clients, permanent objects, metrics, rows, and results. Implement lookup helpers and display tables.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `python -m unittest tests.test_tables -v`

Expected: all table tests pass.

### Task 2: Random Generators And RK4

**Files:**
- Create: `lomiteria/randoms.py`
- Create: `lomiteria/rk4.py`
- Test: `tests/test_randoms_rk4.py`

- [ ] **Step 1: Write failing tests for deterministic formulas**

```python
from lomiteria.models import SimulationParams
from lomiteria.randoms import uniform
from lomiteria.rk4 import build_rk4_tables


def test_uniform_formula():
    assert uniform(0.5, 10.0, 20.0) == 15.0


def test_rk4_tables_cover_all_a_values_and_finish_over_limit():
    params = SimulationParams()
    tables, times = build_rk4_tables(params)
    assert sorted(tables) == [2, 3, 4, 5]
    assert all(times[a] > 0 for a in [2, 3, 4, 5])
    assert tables[2][-1]["L"] > params.rk_limit_l
    assert tables[5][-1]["L"] > params.rk_limit_l


def test_rk4_time_for_a_2_is_about_5_34_minutes():
    params = SimulationParams()
    _, times = build_rk4_tables(params)
    assert abs(times[2] - 5.34) < 0.02
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_randoms_rk4 -v`

Expected: fails because modules do not exist.

- [ ] **Step 3: Implement random formulas and RK4 tables**

Implement uniform, normal-positive Box-Muller generator with returned RND values, and RK4 table generation for A values.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `python -m unittest tests.test_randoms_rk4 -v`

Expected: tests pass.

### Task 3: Simulation Engine

**Files:**
- Create: `lomiteria/simulator.py`
- Modify: `lomiteria/models.py`
- Test: `tests/test_simulator.py`

- [ ] **Step 1: Write failing tests for required engine behavior**

```python
from lomiteria.models import SimulationParams
from lomiteria.simulator import simulate


def test_simulation_keeps_requested_rows_and_final_row():
    params = SimulationParams(x_minutes=20.0, max_iterations=1000, display_from=2, display_count=5, seed=123)
    result = simulate(params)
    assert len(result.rows) == 5
    assert result.final_row.evento == "fin_simulacion"
    assert result.final_row.reloj_min == 20.0
    assert result.total_iterations <= 1000


def test_simulation_exposes_controls_and_metrics():
    params = SimulationParams(x_minutes=45.0, max_iterations=1000, display_from=1, display_count=3, seed=321)
    result = simulate(params)
    assert result.controls_15
    assert result.controls_30
    assert "tiempo_promedio_permanencia_negocio" in result.metrics
    assert "porcentaje_ocupacion_caja" in result.metrics


def test_vector_rows_are_categorized_and_include_random_columns():
    params = SimulationParams(x_minutes=10.0, max_iterations=1000, display_from=1, display_count=2, seed=44)
    result = simulate(params)
    row = result.rows[0]
    grouped = row.as_grouped_dict()
    assert set(grouped) == {"RELOJ_EVENTO", "EVENTOS", "OBJETOS_PERMANENTES", "VARIABLES_ESTADISTICAS", "OBJETOS_TEMPORALES"}
    assert "rnd_llegada_1" in grouped["EVENTOS"]
    assert "estado_caja" in grouped["OBJETOS_PERMANENTES"]
```

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest tests.test_simulator -v`

Expected: fails because simulator does not exist.

- [ ] **Step 3: Implement event engine**

Implement current-state-only event loop, queues, row creation, metrics, 15/30 minute controls, and final row at X.

- [ ] **Step 4: Run simulator tests to verify GREEN**

Run: `python -m unittest tests.test_simulator -v`

Expected: tests pass.

### Task 4: CSV Export And UI

**Files:**
- Create: `lomiteria/exporter.py`
- Create: `lomiteria/ui.py`
- Create: `main.py`
- Test: `tests/test_exporter.py`

- [ ] **Step 1: Write failing exporter test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from lomiteria.exporter import export_result
from lomiteria.models import SimulationParams
from lomiteria.simulator import simulate


def test_export_result_writes_required_csv_files():
    result = simulate(SimulationParams(x_minutes=5.0, display_from=1, display_count=2, seed=12))
    with TemporaryDirectory() as tmp:
        paths = export_result(result, Path(tmp))
        names = {path.name for path in paths}
        assert "vector_estado.csv" in names
        assert "ultima_fila.csv" in names
        assert "metricas.csv" in names
        assert "controles_15min.csv" in names
        assert "controles_30min.csv" in names
        assert "runge_kutta_A2.csv" in names
        assert "tablas_intermedias.csv" in names
```

- [ ] **Step 2: Run exporter test to verify RED**

Run: `python -m unittest tests.test_exporter -v`

Expected: fails because exporter does not exist.

- [ ] **Step 3: Implement exporter and Tkinter UI**

Implement CSV export and a tabbed Tkinter app: Parametros, Vector, Ultima fila, Metricas, Controles 15, Controles 30, Tablas, Runge-Kutta.

- [ ] **Step 4: Run exporter test to verify GREEN**

Run: `python -m unittest tests.test_exporter -v`

Expected: tests pass.

### Task 5: Verification

**Files:**
- Create: `README.md`

- [ ] **Step 1: Add run instructions**

Document commands:

```powershell
python -m unittest -v
python main.py
```

- [ ] **Step 2: Run all tests**

Run: `python -m unittest -v`

Expected: all tests pass.

- [ ] **Step 3: Smoke-test 100000 iteration cap by command line engine**

Run a short Python command that simulates with `max_iterations=100000` and prints total iterations/final clock.

Expected: process exits successfully without retaining all rows.
