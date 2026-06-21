from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from .exporter import export_result
from .models import SimulationParams, SimulationResult
from .simulator import simulate


class LomiteriaApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TP5 Simulacion - Lomiteria")
        self.geometry("1200x760")
        self.result: SimulationResult | None = None
        self.inputs: dict[str, tk.StringVar] = {}

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.param_tab = ttk.Frame(self.notebook, padding=10)
        self.vector_tab = ttk.Frame(self.notebook, padding=6)
        self.final_tab = ttk.Frame(self.notebook, padding=6)
        self.metrics_tab = ttk.Frame(self.notebook, padding=6)
        self.control15_tab = ttk.Frame(self.notebook, padding=6)
        self.control30_tab = ttk.Frame(self.notebook, padding=6)
        self.tables_tab = ttk.Frame(self.notebook, padding=6)
        self.rk_tab = ttk.Frame(self.notebook, padding=6)

        for frame, title in [
            (self.param_tab, "Parametros"),
            (self.vector_tab, "Vector"),
            (self.final_tab, "Ultima fila"),
            (self.metrics_tab, "Metricas"),
            (self.control15_tab, "Control 15 min"),
            (self.control30_tab, "Control 30 min"),
            (self.tables_tab, "Tablas"),
            (self.rk_tab, "Runge-Kutta"),
        ]:
            self.notebook.add(frame, text=title)

        self._build_params()
        self.vector_tree = self._tree(self.vector_tab)
        self.final_tree = self._tree(self.final_tab)
        self.metrics_tree = self._tree(self.metrics_tab)
        self.control15_tree = self._tree(self.control15_tab)
        self.control30_tree = self._tree(self.control30_tab)
        self.tables_tree = self._tree(self.tables_tab)
        self.rk_tree = self._tree(self.rk_tab)

    def _build_params(self) -> None:
        defaults = SimulationParams()
        fields = [
            ("x_minutes", "Tiempo X (min)", defaults.x_minutes),
            ("max_iterations", "Max iteraciones", defaults.max_iterations),
            ("display_from", "Mostrar desde j", defaults.display_from),
            ("display_count", "Cantidad i", defaults.display_count),
            ("seed", "Semilla", ""),
            ("llegada_media", "Llegada media", defaults.llegada_media),
            ("llegada_desvio", "Llegada desvio", defaults.llegada_desvio),
            ("caja_min", "Caja min", defaults.caja_min),
            ("caja_max", "Caja max", defaults.caja_max),
            ("prob_llevar", "Prob. llevar", defaults.prob_llevar),
            ("prob_rojo", "Prob. rojo", defaults.prob_rojo),
            ("capacidad_rojo", "Cap. rojo", defaults.capacidad_rojo),
            ("capacidad_azul", "Cap. azul", defaults.capacidad_azul),
            ("preparadores", "Preparadores", defaults.preparadores),
            ("llevar_min", "Prep llevar min", defaults.llevar_min),
            ("llevar_max", "Prep llevar max", defaults.llevar_max),
            ("rk_h", "h RK4", defaults.rk_h),
            ("rk_limit_l", "Limite L", defaults.rk_limit_l),
            ("rk_minutes_per_unit", "Min por t RK", defaults.rk_minutes_per_unit),
            ("control_mostrador_interval", "Control cola", defaults.control_mostrador_interval),
            ("control_salones_interval", "Control salones", defaults.control_salones_interval),
            ("rojo_11_min", "Rojo 11 min", defaults.rojo_11_min),
            ("rojo_11_max", "Rojo 11 max", defaults.rojo_11_max),
            ("rojo_12_min", "Rojo 12 min", defaults.rojo_12_min),
            ("rojo_12_max", "Rojo 12 max", defaults.rojo_12_max),
            ("rojo_13_min", "Rojo 13 min", defaults.rojo_13_min),
            ("rojo_13_max", "Rojo 13 max", defaults.rojo_13_max),
            ("rojo_14_min", "Rojo 14 min", defaults.rojo_14_min),
            ("rojo_14_max", "Rojo 14 max", defaults.rojo_14_max),
            ("azul_11_min", "Azul 11 min", defaults.azul_11_min),
            ("azul_11_max", "Azul 11 max", defaults.azul_11_max),
            ("azul_12_min", "Azul 12 min", defaults.azul_12_min),
            ("azul_12_max", "Azul 12 max", defaults.azul_12_max),
            ("azul_13_min", "Azul 13 min", defaults.azul_13_min),
            ("azul_13_max", "Azul 13 max", defaults.azul_13_max),
            ("azul_14_min", "Azul 14 min", defaults.azul_14_min),
            ("azul_14_max", "Azul 14 max", defaults.azul_14_max),
        ]

        for idx, (name, label, default) in enumerate(fields):
            row = idx // 3
            col = (idx % 3) * 2
            ttk.Label(self.param_tab, text=label).grid(row=row, column=col, sticky="w", padx=4, pady=4)
            var = tk.StringVar(value=str(default))
            self.inputs[name] = var
            ttk.Entry(self.param_tab, textvariable=var, width=16).grid(row=row, column=col + 1, sticky="ew", padx=4, pady=4)

        button_row = (len(fields) + 2) // 3 + 1
        ttk.Button(self.param_tab, text="Simular", command=self._simulate).grid(row=button_row, column=0, padx=4, pady=12, sticky="w")
        ttk.Button(self.param_tab, text="Exportar CSV", command=self._export).grid(row=button_row, column=1, padx=4, pady=12, sticky="w")

    def _simulate(self) -> None:
        try:
            params = self._read_params()
            self.result = simulate(params)
            self._fill_tree(self.vector_tree, [row.flat_dict() for row in self.result.rows])
            self._fill_tree(self.final_tree, [self.result.final_row.flat_dict()])
            self._fill_tree(self.metrics_tree, [{"metrica": key, "valor": value} for key, value in self.result.metrics.items()])
            self._fill_tree(self.control15_tree, self.result.controls_15)
            self._fill_tree(self.control30_tree, self.result.controls_30)
            self._fill_tree(self.tables_tree, self._intermediate_rows(self.result))
            self._fill_tree(self.rk_tree, self._rk_rows(self.result))
            self.notebook.select(self.vector_tab)
        except Exception as exc:
            messagebox.showerror("Error de simulacion", str(exc))

    def _export(self) -> None:
        if self.result is None:
            messagebox.showinfo("Exportar", "Primero ejecute una simulacion.")
            return
        selected = filedialog.askdirectory(title="Carpeta para CSV")
        if not selected:
            return
        paths = export_result(self.result, Path(selected))
        messagebox.showinfo("Exportar", f"Archivos exportados: {len(paths)}")

    def _read_params(self) -> SimulationParams:
        seed_text = self.inputs["seed"].get().strip()
        return SimulationParams(
            x_minutes=float(self.inputs["x_minutes"].get()),
            max_iterations=int(self.inputs["max_iterations"].get()),
            display_from=int(self.inputs["display_from"].get()),
            display_count=int(self.inputs["display_count"].get()),
            seed=int(seed_text) if seed_text else None,
            llegada_media=float(self.inputs["llegada_media"].get()),
            llegada_desvio=float(self.inputs["llegada_desvio"].get()),
            caja_min=float(self.inputs["caja_min"].get()),
            caja_max=float(self.inputs["caja_max"].get()),
            prob_llevar=float(self.inputs["prob_llevar"].get()),
            prob_rojo=float(self.inputs["prob_rojo"].get()),
            capacidad_rojo=int(self.inputs["capacidad_rojo"].get()),
            capacidad_azul=int(self.inputs["capacidad_azul"].get()),
            preparadores=int(self.inputs["preparadores"].get()),
            llevar_min=float(self.inputs["llevar_min"].get()),
            llevar_max=float(self.inputs["llevar_max"].get()),
            rk_h=float(self.inputs["rk_h"].get()),
            rk_limit_l=float(self.inputs["rk_limit_l"].get()),
            rk_minutes_per_unit=float(self.inputs["rk_minutes_per_unit"].get()),
            control_mostrador_interval=float(self.inputs["control_mostrador_interval"].get()),
            control_salones_interval=float(self.inputs["control_salones_interval"].get()),
            rojo_11_min=float(self.inputs["rojo_11_min"].get()),
            rojo_11_max=float(self.inputs["rojo_11_max"].get()),
            rojo_12_min=float(self.inputs["rojo_12_min"].get()),
            rojo_12_max=float(self.inputs["rojo_12_max"].get()),
            rojo_13_min=float(self.inputs["rojo_13_min"].get()),
            rojo_13_max=float(self.inputs["rojo_13_max"].get()),
            rojo_14_min=float(self.inputs["rojo_14_min"].get()),
            rojo_14_max=float(self.inputs["rojo_14_max"].get()),
            azul_11_min=float(self.inputs["azul_11_min"].get()),
            azul_11_max=float(self.inputs["azul_11_max"].get()),
            azul_12_min=float(self.inputs["azul_12_min"].get()),
            azul_12_max=float(self.inputs["azul_12_max"].get()),
            azul_13_min=float(self.inputs["azul_13_min"].get()),
            azul_13_max=float(self.inputs["azul_13_max"].get()),
            azul_14_min=float(self.inputs["azul_14_min"].get()),
            azul_14_max=float(self.inputs["azul_14_max"].get()),
        )

    def _tree(self, parent: ttk.Frame) -> ttk.Treeview:
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, show="headings")
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def _fill_tree(self, tree: ttk.Treeview, rows: list[dict[str, Any]]) -> None:
        tree.delete(*tree.get_children())
        columns = self._columns(rows)
        tree["columns"] = columns
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=130, minwidth=70, stretch=False)
        for row in rows:
            tree.insert("", "end", values=[row.get(column, "") for column in columns])

    def _columns(self, rows: list[dict[str, Any]]) -> list[str]:
        columns: list[str] = []
        for row in rows:
            for key in row:
                if key not in columns:
                    columns.append(key)
        return columns or ["sin_datos"]

    def _intermediate_rows(self, result: SimulationResult) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for table, table_rows in result.intermediate_tables.items():
            for row in table_rows:
                rows.append({"tabla": table, **row})
        return rows

    def _rk_rows(self, result: SimulationResult) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for a_value, rk_rows in result.rk4_tables.items():
            for row in rk_rows:
                rows.append({"tabla": f"A={a_value}", **row})
        return rows


def run_app() -> None:
    app = LomiteriaApp()
    app.mainloop()
