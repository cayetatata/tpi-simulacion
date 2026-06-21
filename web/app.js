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
let activeVectorFilter = "ALL";
let activeRowScope = "requested";

document.addEventListener("DOMContentLoaded", () => {
  buildForm();
  bindNavigation();
  bindVectorFilters();
  bindRowScope();
  document.getElementById("simulateButton").addEventListener("click", runSimulation);
  document.getElementById("resetButton").addEventListener("click", () => setParamValues(defaultParams));
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

function bindVectorFilters() {
  document.querySelectorAll("[data-vector-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveVectorFilter(button.dataset.vectorFilter);
      if (latestPayload) renderVectorTable(currentVectorRows());
    });
  });
}

function setActiveVectorFilter(filter) {
  activeVectorFilter = filter;
  document.querySelectorAll("[data-vector-filter]").forEach((item) => {
    item.classList.toggle("active", item.dataset.vectorFilter === filter);
  });
}

function bindRowScope() {
  document.querySelectorAll("[data-row-scope]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRowScope = button.dataset.rowScope;
      document.querySelectorAll("[data-row-scope]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      if (activeRowScope === "last" && activeVectorFilter === "ALL") {
        setActiveVectorFilter("RELOJ_EVENTO");
      }
      if (latestPayload) renderVectorTable(currentVectorRows());
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
  renderMetrics(payload);
  renderStatisticCards(payload);
  renderVectorTable(currentVectorRows());
  renderTable("finalTable", [payload.final_flat || {}]);
  renderTable("controls15Table", payload.controls_15 || []);
  renderTable("controls30Table", payload.controls_30 || []);
  renderLookupTables(payload.intermediate_tables || {});
  renderRkTables(payload.rk4_tables || {});
}

function currentVectorRows() {
  if (!latestPayload) return [];
  return activeRowScope === "last" ? (latestPayload.last_rows || []) : (latestPayload.vector_rows || []);
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
    if (activeVectorFilter !== "ALL" && activeVectorFilter !== key) return;
    const names = unique(rows.flatMap((row) => Object.keys(row[key] || {})));
    names.forEach((name) => columns.push({ key, name, title, className }));
  });
  if (!columns.length) {
    host.innerHTML = emptyMessage("La categoria seleccionada no tiene columnas para las filas mostradas.");
    return;
  }
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

function renderMetrics(payload) {
  const host = document.getElementById("metricsTable");
  const metrics = payload.metrics || {};
  const definitions = payload.metric_definitions || [];
  if (!definitions.length) {
    host.innerHTML = emptyMessage("No hay definiciones de metricas.");
    return;
  }
  host.innerHTML = definitions.map((definition) => {
    const value = metrics[definition.metrica];
    return `
      <article class="metric-card">
        <div class="metric-card-top">
          <div>
            <p class="metric-key">${definition.metrica}</p>
            <h5>${definition.titulo}</h5>
          </div>
          <strong class="metric-value">${formatMetricValue(value)}</strong>
        </div>
        <div class="metric-type">${definition.tipo || "Metrica"}</div>
        <div class="metric-meta">
          <span>Formula</span>
          <code>${definition.formula}</code>
        </div>
        <div class="metric-meta">
          <span>Variables</span>
          <code>${(definition.variables || []).join(", ")}</code>
        </div>
        <p class="metric-enunciado">${definition.enunciado}</p>
      </article>
    `;
  }).join("");
}

function renderStatisticCards(payload) {
  const host = document.getElementById("statisticsGrid");
  const stats = payload.final_row?.VARIABLES_ESTADISTICAS || {};
  const definitions = payload.statistic_definitions || [];
  const descriptions = Object.fromEntries(definitions.map((item) => [item.variable, item.descripcion]));
  const entries = Object.entries(stats);
  if (!entries.length) {
    host.innerHTML = emptyMessage("No hay variables estadisticas para mostrar.");
    return;
  }
  host.innerHTML = entries.map(([name, value]) => {
    const baseName = name.replace(/_[0-9]+$/, "_i");
    const description = descriptions[name] || descriptions[baseName] || "Variable estadistica usada para lectura del vector y calculo de resultados.";
    return `
      <article class="stat-card">
        <span>${name}</span>
        <strong>${formatCell(value)}</strong>
        <p>${description}</p>
      </article>
    `;
  }).join("");
}

function renderLookupTables(tables) {
  const host = document.getElementById("intermediateTable");
  const entries = Object.entries(tables);
  if (!entries.length) {
    host.innerHTML = emptyMessage("No hay tablas intermedias para mostrar.");
    return;
  }
  host.innerHTML = entries.map(([name, rows]) => `
    <article class="lookup-card">
      <div class="lookup-title">
        <h5>${lookupTitle(name)}</h5>
        <span>${rows.length} rangos</span>
      </div>
      <div class="range-list">
        ${rows.map((row) => renderLookupRow(row)).join("")}
      </div>
    </article>
  `).join("");
}

function renderLookupRow(row) {
  if ("horario" in row && "rojo" in row) {
    return `
      <div class="range-row permanence-row">
        <span class="range-pill">${row.horario}</span>
        <div><strong>Reloj ${row.reloj} min</strong><small>Desde las ${row.horario}</small></div>
        <div><strong>Salon rojo</strong><small>${row.rojo} min</small></div>
        <div><strong>Salon azul</strong><small>${row.azul} min</small></div>
      </div>
    `;
  }
  const desde = row.rnd_desde ?? row.desde ?? 0;
  const hasta = row.rnd_hasta ?? row.hasta ?? 1;
  const valueKey = Object.keys(row).find((key) => !["rnd_desde", "rnd_hasta", "desde", "hasta"].includes(key));
  return `
    <div class="range-row">
      <span class="range-pill">${formatRange(desde)} <= RND < ${formatRange(hasta)}</span>
      <strong>${valueKey}: ${formatCell(row[valueKey])}</strong>
    </div>
  `;
}

function renderRkTables(tables) {
  const host = document.getElementById("rkTable");
  const entries = Object.entries(tables);
  const params = latestPayload?.rk4_parameters || {};
  if (!entries.length) {
    host.innerHTML = emptyMessage("No hay tablas Runge-Kutta calculadas.");
    return;
  }
  host.innerHTML = entries.map(([aValue, rows]) => {
    const last = rows[rows.length - 1] || {};
    return `
      <article class="rk-card">
        <div class="rk-card-head">
          <div>
            <p class="metric-key">${params.ecuacion || "dL/dt = 3A + 6"}</p>
            <h5>A = ${aValue}</h5>
          </div>
          <div class="rk-summary">
            <span>Listo</span>
            <strong>${metricNumber(last.tiempo_min)} min</strong>
          </div>
        </div>
        <div class="rk-facts">
          <span>h = ${formatCell(params.h)}</span>
          <span>L inicial = ${aValue}</span>
          <span>Listo cuando L > ${formatCell(params.limite_l)}</span>
          <span>t = 1 equivale a ${formatCell(params.minutos_por_t)} min</span>
        </div>
        <div class="table-host mini-table">
          ${tableHtml(sampleRkRows(rows))}
        </div>
      </article>
    `;
  }).join("");
}

function renderTable(id, rows) {
  const host = document.getElementById(id);
  if (!rows || !rows.length) {
    host.innerHTML = emptyTable();
    return;
  }
  host.innerHTML = tableHtml(rows);
}

function tableHtml(rows) {
  const columns = unique(rows.flatMap((row) => Object.keys(row)));
  return `
    <table>
      <thead><tr>${columns.map((column) => `<th>${column}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((row) => `<tr>${columns.map((column) => `<td>${formatCell(row[column])}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
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

function formatMetricValue(value) {
  return value === undefined ? "control" : metricNumber(value);
}

function formatRange(value) {
  return Number(value).toFixed(2);
}

function lookupTitle(name) {
  const titles = {
    tipo_consumo: "Tipo de consumo",
    salon: "Salon elegido",
    a_preparacion: "Valor A para Runge-Kutta",
    permanencia: "Permanencia por horario"
  };
  return titles[name] || name;
}

function sampleRkRows(rows) {
  if (rows.length <= 12) return rows;
  return [
    ...rows.slice(0, 6),
    { i: "...", t: "...", l: "...", k1: "...", k2: "...", k3: "...", k4: "...", tiempo_min: "..." },
    ...rows.slice(-5)
  ];
}

function emptyTable() {
  return `<table><tbody><tr><td>Sin datos. Ejecute una simulacion.</td></tr></tbody></table>`;
}

function emptyMessage(message) {
  return `<div class="empty-state">${message}</div>`;
}
