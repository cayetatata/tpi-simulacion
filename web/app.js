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
    title: "Alcance de la simulacion y filas a mostrar",
    fields: [
      ["x_minutes", "Tiempo final de simulacion X (min)"],
      ["max_iterations", "Maximo de iteraciones del vector"],
      ["display_from", "Fila inicial j a mostrar"],
      ["display_count", "Cantidad de filas i a mostrar"],
      ["seed", "Semilla opcional"]
    ]
  },
  {
    title: "Llegadas de clientes y atencion en caja",
    fields: [
      ["llegada_media", "Media entre llegadas (min)"],
      ["llegada_desvio", "Desvio entre llegadas (min)"],
      ["caja_min", "Tiempo minimo de atencion en caja (min)"],
      ["caja_max", "Tiempo maximo de atencion en caja (min)"]
    ]
  },
  {
    title: "Decisiones del cliente y preparacion del pedido",
    fields: [
      ["prob_llevar", "Probabilidad de compra para llevar"],
      ["prob_rojo", "Probabilidad de elegir Salon Rojo"],
      ["preparadores", "Cantidad de preparadores en mostrador"],
      ["llevar_min", "Tiempo minimo para pedido para llevar (min)"],
      ["llevar_max", "Tiempo maximo para pedido para llevar (min)"],
      ["a_values", "Valores posibles de A para pedidos en local"],
      ["rk_h", "Paso h de Runge-Kutta"],
      ["rk_limit_l", "Valor de L para pedido listo"],
      ["rk_minutes_per_unit", "Minutos reales por cada unidad t"]
    ]
  },
  {
    title: "Capacidad de salones y eventos de control",
    fields: [
      ["capacidad_rojo", "Capacidad del Salon Rojo"],
      ["capacidad_azul", "Capacidad del Salon Azul"],
      ["control_mostrador_interval", "Cada cuantos minutos controlar cola de mostrador"],
      ["control_salones_interval", "Cada cuantos minutos controlar ocupacion de salones"]
    ]
  },
  {
    title: "Tiempo de permanencia en Salon Rojo",
    fields: [
      ["rojo_11_min", "Minimo entre 11 y 12 hs"],
      ["rojo_11_max", "Maximo entre 11 y 12 hs"],
      ["rojo_12_min", "Minimo entre 12 y 13 hs"],
      ["rojo_12_max", "Maximo entre 12 y 13 hs"],
      ["rojo_13_min", "Minimo entre 13 y 14 hs"],
      ["rojo_13_max", "Maximo entre 13 y 14 hs"],
      ["rojo_14_min", "Minimo entre 14 y 15 hs"],
      ["rojo_14_max", "Maximo entre 14 y 15 hs"]
    ]
  },
  {
    title: "Tiempo de permanencia en Salon Azul",
    fields: [
      ["azul_11_min", "Minimo entre 11 y 12 hs"],
      ["azul_11_max", "Maximo entre 11 y 12 hs"],
      ["azul_12_min", "Minimo entre 12 y 13 hs"],
      ["azul_12_max", "Maximo entre 12 y 13 hs"],
      ["azul_13_min", "Minimo entre 13 y 14 hs"],
      ["azul_13_max", "Maximo entre 13 y 14 hs"],
      ["azul_14_min", "Minimo entre 14 y 15 hs"],
      ["azul_14_max", "Maximo entre 14 y 15 hs"]
    ]
  }
];

const vectorCategories = [
  ["RELOJ_EVENTO", "Reloj / evento", "cat-reloj"],
  ["EVENTOS", "Eventos", "cat-eventos"],
  ["OBJETOS_PERMANENTES", "Objetos permanentes", "cat-permanentes"],
  ["VARIABLES_ESTADISTICAS", "Variables estadisticas", "cat-estadisticas"],
  ["OBJETOS_TEMPORALES", "Objetos temporales", "cat-temporales"]
];

const vectorGroupDefinitions = {
  RELOJ_EVENTO: [
    { title: "Fila simulada", columns: ["nro_evento", "evento", "reloj_min", "hora_real"] }
  ],
  EVENTOS: [
    { title: "Llegada clientes", columns: ["rnd_llegada_1", "rnd_llegada_2", "formula_box_muller", "origen_box_muller", "tiempo_entre_llegadas", "proxima_llegada"] },
    { title: "Caja", columns: ["rnd_caja", "tiempo_caja", "fin_caja"] },
    { title: "Tipo de consumo", columns: ["rnd_tipo_consumo", "tipo_consumo"] },
    { title: "Salon elegido", columns: ["rnd_salon", "salon"] },
    { title: "Preparacion local RK4", columns: ["rnd_a_preparacion", "a_preparacion", "tiempo_preparacion_local"] },
    { title: "Preparacion para llevar", columns: ["rnd_preparacion_llevar", "tiempo_preparacion_llevar"] },
    { title: "Fin mostrador", columns: ["fin_preparacion_1", "fin_preparacion_2", "fin_preparacion_3"] },
    { title: "Permanencia salon", columns: ["rnd_permanencia_salon", "tiempo_permanencia_salon", "fin_permanencia_rojo", "fin_permanencia_azul"] },
    { title: "Controles", columns: ["proximo_control_15", "proximo_control_30"] }
  ],
  OBJETOS_PERMANENTES: [
    { title: "Caja", columns: ["estado_caja", "cliente_caja", "cola_caja"] },
    { title: "Cola mostrador", columns: ["cola_mostrador"] },
    { title: "Preparador 1", columns: ["estado_preparador_1", "cliente_preparador_1"] },
    { title: "Preparador 2", columns: ["estado_preparador_2", "cliente_preparador_2"] },
    { title: "Preparador 3", columns: ["estado_preparador_3", "cliente_preparador_3"] },
    { title: "Salon rojo", columns: ["ocupacion_rojo", "cola_rojo"] },
    { title: "Salon azul", columns: ["ocupacion_azul", "cola_azul"] }
  ],
  VARIABLES_ESTADISTICAS: [
    { title: "Permanencia negocio", columns: ["ac_tiempo_permanencia_negocio", "ct_clientes_finalizados"] },
    { title: "Cola caja", columns: ["ac_tiempo_cola_caja", "ct_clientes_pasan_por_caja", "max_cola_caja"] },
    { title: "Cola mostrador", columns: ["ac_tiempo_cola_mostrador", "ct_clientes_pasan_por_mostrador", "max_cola_mostrador"] },
    { title: "Ocupacion recursos", columns: ["ac_ocupacion_caja", "ac_ocupacion_preparador_1", "ac_ocupacion_preparador_2", "ac_ocupacion_preparador_3"] },
    { title: "Salon rojo estadisticas", columns: ["ac_ocupacion_rojo_tiempo_persona", "max_ocupacion_rojo", "ct_esperaron_rojo_lleno"] },
    { title: "Salon azul estadisticas", columns: ["ac_ocupacion_azul_tiempo_persona", "max_ocupacion_azul", "ct_esperaron_azul_lleno"] }
  ]
};

const scheduledEventColumns = [
  "proxima_llegada",
  "fin_caja",
  "fin_preparacion_1",
  "fin_preparacion_2",
  "fin_preparacion_3",
  "fin_permanencia_rojo",
  "fin_permanencia_azul",
  "proximo_control_15",
  "proximo_control_30"
];

const metricDefinitions = [
  {
    metrica: "tiempo_promedio_permanencia_negocio",
    orden: 1,
    titulo: "Tiempo promedio de permanencia en el negocio",
    tipo: "Pedida por el enunciado",
    formula: "ac_tiempo_permanencia_negocio / ct_clientes_finalizados",
    variables: ["ac_tiempo_permanencia_negocio", "ct_clientes_finalizados"],
    enunciado: "Tiempo de permanencia en el negocio."
  },
  {
    metrica: "tiempo_promedio_cola_caja",
    orden: 2,
    titulo: "Tiempo promedio en cola de caja",
    tipo: "Pedida por el enunciado",
    formula: "ac_tiempo_cola_caja / ct_clientes_pasan_por_caja",
    variables: ["ac_tiempo_cola_caja", "ct_clientes_pasan_por_caja"],
    enunciado: "Tiempo en cola en la caja."
  },
  {
    metrica: "control_15_cola_mostrador",
    orden: 3,
    titulo: "Control cada 15 minutos de la cola del mostrador",
    tipo: "Pedida por el enunciado",
    formula: "Lectura directa de la cantidad de clientes en cola al dispararse cada control de 15 minutos",
    variables: ["cantidad_controles_15", "primer_control_cola_mostrador", "ultimo_control_cola_mostrador"],
    enunciado: "Cada 15 minutos, cantidad de gente en cola frente al mostrador."
  },
  {
    metrica: "control_30_ocupacion_salones",
    orden: 4,
    titulo: "Control cada 30 minutos de ocupacion de salones",
    tipo: "Pedida por el enunciado",
    formula: "Lectura directa de ocupacion del Salon Rojo y del Salon Azul al dispararse cada control de 30 minutos",
    variables: ["cantidad_controles_30", "ultima_ocupacion_rojo", "ultima_ocupacion_azul"],
    enunciado: "Cada 30 minutos, cantidad de personas en Salon Rojo y Salon Azul."
  },
  {
    metrica: "tiempo_promedio_cola_mostrador",
    orden: 1,
    titulo: "Tiempo promedio en cola frente al mostrador",
    tipo: "Metrica adicional",
    formula: "ac_tiempo_cola_mostrador / ct_clientes_pasan_por_mostrador",
    variables: ["ac_tiempo_cola_mostrador", "ct_clientes_pasan_por_mostrador"],
    enunciado: "Demora promedio antes de que un pedido empiece a prepararse."
  },
  {
    metrica: "porcentaje_ocupacion_caja",
    orden: 2,
    titulo: "Porcentaje de ocupacion de la caja",
    tipo: "Metrica adicional",
    formula: "ac_ocupacion_caja / reloj_min * 100",
    variables: ["ac_ocupacion_caja", "reloj_min"],
    enunciado: "Utilizacion de la caja durante toda la simulacion."
  },
  {
    metrica: "porcentaje_ocupacion_preparadores",
    orden: 3,
    titulo: "Porcentaje de ocupacion de los preparadores",
    tipo: "Metrica adicional",
    formula: "sum(ac_ocupacion_preparador_i) / (preparadores * reloj_min) * 100",
    variables: ["ac_ocupacion_preparador_i", "preparadores", "reloj_min"],
    enunciado: "Utilizacion conjunta del mostrador de preparacion."
  },
  {
    metrica: "clientes_esperaron_salon_lleno_total",
    orden: 4,
    titulo: "Clientes que esperaron por salon lleno",
    tipo: "Metrica adicional",
    formula: "ct_esperaron_rojo_lleno + ct_esperaron_azul_lleno",
    variables: ["ct_esperaron_rojo_lleno", "ct_esperaron_azul_lleno"],
    enunciado: "Cantidad total de clientes que no pudieron entrar de inmediato al salon elegido."
  }
];

const rk4Texts = {
  ecuacion: "dL/dt = 3A + 6",
  reglaInicial: "L inicial = A",
  minutosPorT: "t = 1 equivale a"
};

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
  const columns = buildVectorColumns(rows);
  if (!columns.length) {
    host.innerHTML = emptyMessage("La categoria seleccionada no tiene columnas para las filas mostradas.");
    return;
  }
  const categoryGroups = adjacentGroups(columns, "title");
  const conceptGroups = adjacentGroups(columns, "groupTitle");
  host.innerHTML = `
    <table class="vector-table">
      <thead>
        <tr class="vector-category-row">
          ${categoryGroups.map((group) => `<th class="${group.className}" colspan="${group.colspan}">${group.label}</th>`).join("")}
        </tr>
        <tr class="vector-concept-row">
          ${conceptGroups.map((group) => `<th class="${group.className}" colspan="${group.colspan}">${group.label}</th>`).join("")}
        </tr>
        <tr class="vector-column-row">
          ${columns.map((column) => `<th class="${column.className}">${column.name}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${rows.map((row) => renderVectorRow(row, columns)).join("")}
      </tbody>
    </table>
  `;
}

function buildVectorColumns(rows) {
  const columns = [];
  vectorCategories.forEach(([key, title, className]) => {
    if (activeVectorFilter !== "ALL" && activeVectorFilter !== key) return;
    const names = unique(rows.flatMap((row) => Object.keys(row[key] || {})));
    orderedVectorNames(key, names).forEach((name) => {
      columns.push({
        key,
        name,
        title,
        className,
        groupTitle: vectorGroupTitle(key, name)
      });
    });
  });
  return columns;
}

function orderedVectorNames(category, names) {
  if (category === "OBJETOS_TEMPORALES") {
    return [...names].sort(compareTemporaryObjectColumns);
  }
  const definitions = vectorGroupDefinitions[category] || [];
  const ordered = [];
  const nameSet = new Set(names);
  definitions.forEach((group) => {
    group.columns.forEach((column) => {
      if (nameSet.has(column)) ordered.push(column);
    });
  });
  names.forEach((name) => {
    if (!ordered.includes(name)) ordered.push(name);
  });
  return ordered;
}

function vectorGroupTitle(category, name) {
  if (category === "OBJETOS_TEMPORALES") {
    const match = name.match(/^cliente_([0-9]+)_/);
    return match ? `Cliente ${match[1]}` : "Clientes activos";
  }
  if (category === "EVENTOS" && name.match(/^fin_preparacion_[0-9]+$/)) return "Fin mostrador";
  if (category === "OBJETOS_PERMANENTES" && name.match(/^(estado|cliente)_preparador_[0-9]+$/)) {
    const id = name.match(/_preparador_([0-9]+)$/)[1];
    return `Preparador ${id}`;
  }
  if (category === "VARIABLES_ESTADISTICAS" && name.match(/^ac_ocupacion_preparador_[0-9]+$/)) return "Ocupacion recursos";
  if (category === "VARIABLES_ESTADISTICAS" && ["ac_ocupacion_rojo_tiempo_persona", "max_ocupacion_rojo", "ct_esperaron_rojo_lleno"].includes(name)) return "Salon rojo estadisticas";
  if (category === "VARIABLES_ESTADISTICAS" && ["ac_ocupacion_azul_tiempo_persona", "max_ocupacion_azul", "ct_esperaron_azul_lleno"].includes(name)) return "Salon azul estadisticas";
  const definitions = vectorGroupDefinitions[category] || [];
  const found = definitions.find((group) => group.columns.includes(name));
  return found ? found.title : "Otros";
}

function compareTemporaryObjectColumns(left, right) {
  const leftParts = temporaryObjectParts(left);
  const rightParts = temporaryObjectParts(right);
  if (leftParts.clientId !== rightParts.clientId) return leftParts.clientId - rightParts.clientId;
  return leftParts.attributeIndex - rightParts.attributeIndex;
}

function temporaryObjectParts(name) {
  const order = [
    "estado",
    "hora_llegada",
    "tipo_consumo",
    "salon",
    "hora_inicio_cola_caja",
    "hora_inicio_cola_mostrador",
    "hora_inicio_cola_salon",
    "hora_inicio_permanencia",
    "fin_programado"
  ];
  const match = name.match(/^cliente_([0-9]+)_(.*)$/);
  if (!match) return { clientId: 999999, attributeIndex: 999999 };
  const attributeIndex = order.indexOf(match[2]);
  return {
    clientId: Number(match[1]),
    attributeIndex: attributeIndex === -1 ? 999999 : attributeIndex
  };
}

function adjacentGroups(columns, field) {
  const groups = [];
  columns.forEach((column) => {
    const last = groups[groups.length - 1];
    const label = column[field];
    if (last && last.label === label && last.className === column.className) {
      last.colspan += 1;
    } else {
      groups.push({ label, className: column.className, colspan: 1 });
    }
  });
  return groups;
}

function renderVectorRow(row, columns) {
  const nextEventColumns = nextEventMinimumColumns(row);
  const cells = columns.map((column) => {
    const isNextEvent = column.key === "EVENTOS" && nextEventColumns.has(column.name);
    const cellClass = isNextEvent ? "next-event-cell" : "";
    return `<td class="${cellClass}">${formatCell(row[column.key]?.[column.name])}</td>`;
  });
  return `<tr>${cells.join("")}</tr>`;
}

function nextEventMinimumColumns(row) {
  const eventValues = row.EVENTOS || {};
  const currentClock = Number(row.RELOJ_EVENTO?.reloj_min ?? 0);
  let minimum = Infinity;
  const columns = [];
  Object.keys(eventValues).filter(isScheduledEventColumn).forEach((column) => {
    const value = Number(eventValues[column]);
    if (!Number.isFinite(value) || value < currentClock - 0.0001) return;
    if (value < minimum - 0.0001) {
      minimum = value;
      columns.length = 0;
      columns.push(column);
      return;
    }
    if (Math.abs(value - minimum) <= 0.0001) columns.push(column);
  });
  return new Set(columns);
}

function isScheduledEventColumn(column) {
  return scheduledEventColumns.includes(column) || column.match(/^fin_preparacion_[0-9]+$/);
}

function renderMetrics(payload) {
  const host = document.getElementById("metricsTable");
  const metrics = payload.metrics || {};
  const definitions = metricDefinitions;
  if (!definitions.length) {
    host.innerHTML = emptyMessage("No hay definiciones de metricas.");
    return;
  }
  host.innerHTML = definitions.map((definition) => {
    const value = metrics[definition.metrica];
    return `
      <details class="metric-card">
        <summary class="metric-card-top">
          <div>
            <p class="metric-key">${metricHeader(definition)}</p>
            <h5>${definition.titulo}</h5>
          </div>
          <strong class="metric-value">${metricDisplayValue(definition, value, payload)}</strong>
        </summary>
        <div class="metric-detail">
          <div class="metric-type">${definition.tipo || "Metrica"}</div>
          <div class="metric-meta">
            <span>Formula</span>
            <code>${definition.formula}</code>
          </div>
          <div class="metric-detail-values">
            ${metricCalculationRows(definition, payload).map((item) => `
              <div>
                <span>${item.label}</span>
                <strong>${formatCell(item.value)}</strong>
              </div>
            `).join("")}
          </div>
          <p class="metric-enunciado">${definition.enunciado}</p>
        </div>
      </details>
    `;
  }).join("");
}

function metricHeader(definition) {
  const order = definition.orden || "";
  return order ? `${order}. ${definition.tipo}` : definition.tipo || "Metrica";
}

function metricDisplayValue(definition, value, payload) {
  if (definition.metrica === "control_15_cola_mostrador") return `${payload.controls_15?.length || 0} lecturas`;
  if (definition.metrica === "control_30_ocupacion_salones") return `${payload.controls_30?.length || 0} lecturas`;
  return formatMetricValue(value);
}

function metricCalculationRows(definition, payload) {
  if (definition.metrica === "control_15_cola_mostrador") {
    return [
      { label: "cantidad_controles_15", value: payload.controls_15?.length || 0 },
      { label: "primer_control_cola_mostrador", value: payload.controls_15?.[0]?.cola_mostrador ?? "" },
      { label: "ultimo_control_cola_mostrador", value: lastItem(payload.controls_15)?.cola_mostrador ?? "" }
    ];
  }
  if (definition.metrica === "control_30_ocupacion_salones") {
    const last = lastItem(payload.controls_30) || {};
    return [
      { label: "cantidad_controles_30", value: payload.controls_30?.length || 0 },
      { label: "ultima_ocupacion_rojo", value: last.ocupacion_rojo ?? "" },
      { label: "ultima_ocupacion_azul", value: last.ocupacion_azul ?? "" }
    ];
  }
  if (definition.metrica === "porcentaje_ocupacion_preparadores") {
    const finalValues = payload.final_flat || {};
    const prepValues = Object.entries(finalValues)
      .filter(([key]) => key.match(/^ac_ocupacion_preparador_[0-9]+$/))
      .map(([key, value]) => ({ label: key, value }));
    const total = prepValues.reduce((sum, item) => sum + Number(item.value || 0), 0);
    return [
      ...prepValues,
      { label: "sum_ac_ocupacion_preparadores", value: total },
      { label: "preparadores", value: prepValues.length },
      { label: "reloj_min", value: finalValues.reloj_min }
    ];
  }
  return (definition.variables || []).map((variable) => ({
    label: variable,
    value: metricVariableValue(variable, payload)
  }));
}

function metricVariableValue(variable, payload) {
  const finalValues = payload.final_flat || {};
  if (variable === "reloj_min") return payload.summary?.final_clock ?? finalValues.reloj_min;
  if (variable === "preparadores") {
    return Object.keys(finalValues).filter((key) => key.match(/^ac_ocupacion_preparador_[0-9]+$/)).length;
  }
  if (variable === "ac_ocupacion_preparador_i") {
    return Object.entries(finalValues)
      .filter(([key]) => key.match(/^ac_ocupacion_preparador_[0-9]+$/))
      .map(([key, value]) => `${key}=${formatCell(value)}`)
      .join(" | ");
  }
  return finalValues[variable] ?? payload.metrics?.[variable] ?? "";
}

function lastItem(items) {
  return items && items.length ? items[items.length - 1] : null;
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
            <p class="metric-key">${rk4Texts.ecuacion}</p>
            <h5>A = ${aValue}</h5>
          </div>
          <div class="rk-summary">
            <span>Listo</span>
            <strong>${metricNumber(last.tiempo_min)} min</strong>
          </div>
        </div>
        <div class="rk-facts">
          <span>h = ${formatCell(params.h)}</span>
          <span>${rk4Texts.reglaInicial.replace("A", aValue)}</span>
          <span>Listo cuando L > ${formatCell(params.limite_l)}</span>
          <span>${rk4Texts.minutosPorT} ${formatCell(params.minutos_por_t)} min</span>
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
