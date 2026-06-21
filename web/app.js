const defaultParams = {
  x_minutes: 240,
  max_iterations: 100000,
  display_from: 1,
  display_count: 20,
  seed: "",
  llegada_media: 1,
  llegada_desvio: 0.5,
  caja_min: 0.25,
  caja_max: 0.75,
  prob_llevar: 0.25,
  prob_rojo: 0.3,
  capacidad_rojo: 30,
  capacidad_azul: 40,
  preparadores: 3,
  llevar_min: 1.6667,
  llevar_max: 2.3333,
  a_values: "2,3,4,5",
  rk_h: 0.01,
  rk_limit_l: 10,
  rk_minutes_per_unit: 10,
  control_mostrador_interval: 15,
  control_salones_interval: 30,
  rojo_11_min: 5,
  rojo_11_max: 35,
  rojo_12_min: 15,
  rojo_12_max: 45,
  rojo_13_min: 20,
  rojo_13_max: 50,
  rojo_14_min: 5,
  rojo_14_max: 35,
  azul_11_min: 15,
  azul_11_max: 45,
  azul_12_min: 25,
  azul_12_max: 55,
  azul_13_min: 35,
  azul_13_max: 55,
  azul_14_min: 20,
  azul_14_max: 50
};

const groups = [
  {
    title: "Simulacion y vista",
    fields: [
      ["x_minutes", "Tiempo X (min)"],
      ["max_iterations", "Max iteraciones"],
      ["display_from", "Mostrar desde j"],
      ["display_count", "Cantidad i"],
      ["seed", "Semilla"]
    ]
  },
  {
    title: "Llegada y caja",
    fields: [
      ["llegada_media", "Llegada media"],
      ["llegada_desvio", "Llegada desvio"],
      ["caja_min", "Caja min"],
      ["caja_max", "Caja max"]
    ]
  },
  {
    title: "Consumo y preparacion",
    fields: [
      ["prob_llevar", "Prob. llevar"],
      ["prob_rojo", "Prob. rojo"],
      ["preparadores", "Preparadores"],
      ["llevar_min", "Llevar min"],
      ["llevar_max", "Llevar max"],
      ["a_values", "Valores A"],
      ["rk_h", "h RK4"],
      ["rk_limit_l", "Limite L"],
      ["rk_minutes_per_unit", "Min por t RK"]
    ]
  },
  {
    title: "Capacidad y controles",
    fields: [
      ["capacidad_rojo", "Cap. rojo"],
      ["capacidad_azul", "Cap. azul"],
      ["control_mostrador_interval", "Control cola"],
      ["control_salones_interval", "Control salones"]
    ]
  },
  {
    title: "Salon rojo permanencia",
    fields: [
      ["rojo_11_min", "11-12 min"],
      ["rojo_11_max", "11-12 max"],
      ["rojo_12_min", "12-13 min"],
      ["rojo_12_max", "12-13 max"],
      ["rojo_13_min", "13-14 min"],
      ["rojo_13_max", "13-14 max"],
      ["rojo_14_min", "14-15 min"],
      ["rojo_14_max", "14-15 max"]
    ]
  },
  {
    title: "Salon azul permanencia",
    fields: [
      ["azul_11_min", "11-12 min"],
      ["azul_11_max", "11-12 max"],
      ["azul_12_min", "12-13 min"],
      ["azul_12_max", "12-13 max"],
      ["azul_13_min", "13-14 min"],
      ["azul_13_max", "13-14 max"],
      ["azul_14_min", "14-15 min"],
      ["azul_14_max", "14-15 max"]
    ]
  }
];

let latestPayload = null;

document.addEventListener("DOMContentLoaded", () => {
  buildForm();
  bindNavigation();
  document.getElementById("simulateButton").addEventListener("click", runSimulation);
  document.getElementById("quickDemoButton").addEventListener("click", () => {
    setParamValues({ seed: 2026, display_from: 20, display_count: 25 });
    runSimulation();
  });
  document.getElementById("resetButton").addEventListener("click", () => setParamValues(defaultParams));
  document.getElementById("downloadVector").addEventListener("click", () => downloadCsv("vector_estado.csv", latestPayload?.vector_flat || []));
  document.getElementById("downloadMetrics").addEventListener("click", () => downloadCsv("metricas.csv", metricRows()));
  document.getElementById("downloadTables").addEventListener("click", () => downloadCsv("tablas_y_rk4.csv", [...intermediateRows(), ...rkRows()]));
});

function buildForm() {
  const form = document.getElementById("paramsForm");
  form.innerHTML = "";
  groups.forEach((group) => {
    const section = document.createElement("section");
    section.className = "field-group";
    section.innerHTML = `<h4>${group.title}</h4>`;
    const grid = document.createElement("div");
    grid.className = "field-grid";
    group.fields.forEach(([name, label]) => {
      const field = document.createElement("div");
      field.className = "field";
      field.innerHTML = `
        <label for="${name}">${label}</label>
        <input id="${name}" name="${name}" value="${defaultParams[name]}" inputmode="decimal">
      `;
      grid.appendChild(field);
    });
    section.appendChild(grid);
    form.appendChild(section);
  });
}

function bindNavigation() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(`view-${button.dataset.view}`).classList.add("active");
    });
  });
}

function setParamValues(values) {
  Object.entries(values).forEach(([key, value]) => {
    const input = document.getElementById(key);
    if (input) input.value = value;
  });
}

function readParams() {
  const params = {};
  Object.keys(defaultParams).forEach((key) => {
    const value = document.getElementById(key)?.value ?? "";
    params[key] = value;
  });
  return params;
}

async function runSimulation() {
  const banner = document.getElementById("statusBanner");
  banner.className = "status-banner";
  banner.textContent = "Simulando...";
  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readParams())
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "No se pudo simular.");
    latestPayload = payload;
    renderPayload(payload);
    banner.className = "status-banner ready";
    banner.textContent = `Simulacion finalizada: ${payload.summary.iterations} iteraciones, reloj ${payload.summary.final_clock} min, ultima hora ${payload.summary.final_hour}.`;
    activateView("resultados");
  } catch (error) {
    banner.className = "status-banner error";
    banner.textContent = error.message;
    activateView("resultados");
  }
}

function activateView(name) {
  document.querySelector(`.nav-item[data-view="${name}"]`)?.click();
}

function renderPayload(payload) {
  renderKpis(payload);
  renderTable("metricsTable", metricRows());
  renderVectorTable(payload.vector_rows || []);
  renderTable("finalTable", [payload.final_flat || {}]);
  renderTable("controls15Table", payload.controls_15 || []);
  renderTable("controls30Table", payload.controls_30 || []);
  renderTable("intermediateTable", intermediateRows());
  renderTable("rkTable", rkRows());
}

function renderKpis(payload) {
  const metrics = payload.metrics || {};
  const items = [
    ["Iteraciones", payload.summary.iterations],
    ["Reloj final", `${payload.summary.final_clock} min`],
    ["Clientes finalizados", metricNumber(metrics.ct_clientes_finalizados ?? payload.final_flat?.ct_clientes_finalizados)],
    ["Ocupacion caja", `${metricNumber(metrics.porcentaje_ocupacion_caja)}%`],
    ["Ocup. preparadores", `${metricNumber(metrics.porcentaje_ocupacion_preparadores)}%`],
    ["Prom. cola caja", `${metricNumber(metrics.tiempo_promedio_cola_caja)} min`],
    ["Controles 15", payload.summary.controls_15],
    ["Controles 30", payload.summary.controls_30]
  ];
  document.getElementById("kpiGrid").innerHTML = items.map(([label, value]) => `
    <article class="kpi-card">
      <div class="kpi-label">${label}</div>
      <div class="kpi-value">${value ?? "-"}</div>
    </article>
  `).join("");
}

function renderVectorTable(rows) {
  const host = document.getElementById("vectorTable");
  if (!rows.length) {
    host.innerHTML = emptyTable();
    return;
  }
  const categories = [
    ["RELOJ_EVENTO", "Reloj / Evento", "cat-reloj"],
    ["EVENTOS", "Eventos", "cat-eventos"],
    ["OBJETOS_PERMANENTES", "Permanentes", "cat-permanentes"],
    ["VARIABLES_ESTADISTICAS", "Estadisticas", "cat-estadisticas"],
    ["OBJETOS_TEMPORALES", "Temporales", "cat-temporales"]
  ];
  const columns = [];
  categories.forEach(([key, title, className]) => {
    const names = unique(rows.flatMap((row) => Object.keys(row[key] || {})));
    names.forEach((name) => columns.push({ key, name, title, className }));
  });
  host.innerHTML = `
    <table>
      <thead>
        <tr>${columns.map((column) => `<th class="${column.className}">${column.title}<br>${column.name}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${rows.map((row) => `<tr>${columns.map((column) => `<td>${formatCell(row[column.key]?.[column.name])}</td>`).join("")}</tr>`).join("")}
      </tbody>
    </table>
  `;
}

function renderTable(id, rows) {
  const host = document.getElementById(id);
  if (!rows || !rows.length) {
    host.innerHTML = emptyTable();
    return;
  }
  const columns = unique(rows.flatMap((row) => Object.keys(row)));
  host.innerHTML = `
    <table>
      <thead><tr>${columns.map((column) => `<th>${column}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((row) => `<tr>${columns.map((column) => `<td>${formatCell(row[column])}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
}

function metricRows() {
  if (!latestPayload) return [];
  return Object.entries(latestPayload.metrics || {}).map(([metrica, valor]) => ({ metrica, valor: metricNumber(valor) }));
}

function intermediateRows() {
  if (!latestPayload) return [];
  const rows = [];
  Object.entries(latestPayload.intermediate_tables || {}).forEach(([tabla, values]) => {
    values.forEach((value) => rows.push({ tabla, ...value }));
  });
  return rows;
}

function rkRows() {
  if (!latestPayload) return [];
  const rows = [];
  Object.entries(latestPayload.rk4_tables || {}).forEach(([aValue, values]) => {
    values.forEach((value) => rows.push({ tabla: `A=${aValue}`, ...value }));
  });
  return rows;
}

function downloadCsv(filename, rows) {
  if (!rows.length) return;
  const columns = unique(rows.flatMap((row) => Object.keys(row)));
  const csv = [
    columns.join(","),
    ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(","))
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function unique(values) {
  return [...new Set(values)];
}

function metricNumber(value) {
  if (value === undefined || value === null || value === "") return "-";
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(2) : value;
}

function formatCell(value) {
  if (typeof value === "number") return Number.isInteger(value) ? value : value.toFixed(4);
  return value ?? "";
}

function emptyTable() {
  return `<table><tbody><tr><td>Sin datos. Ejecute una simulacion.</td></tr></tbody></table>`;
}
