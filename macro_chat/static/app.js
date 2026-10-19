/**
 * MacroData Studio - Frontend Logic
 * Universidad Nacional del Sur (UNS) - Cátedra de Desarrollo Económico
 */

// Estado Global de la Aplicación
const state = {
  catalog: null,
  selectedCountries: new Set(),
  selectedVariables: new Set(),
  selectedChartType: "line",
  formulas: [],
  selectedFormulas: new Set(),
  activeDatabase: "world_bank",
  lastGeneratedData: null
};

// ============================================================================
// Inicialización
// ============================================================================
document.addEventListener("DOMContentLoaded", async () => {
  loadStoredSettings();
  loadStoredFormulas();
  setupKeyboardShortcuts();
  await fetchCatalog();
});

// Configuración de atajos de teclado (Ctrl + Enter para generar)
function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      triggerGenerate();
    }
  });
}

// ============================================================================
// Carga de Catálogo y Renderizado de Selectores
// ============================================================================
async function fetchCatalog() {
  try {
    const res = await fetch("/api/catalog");
    if (!res.ok) throw new Error("Error al obtener catálogo.");
    const data = await res.json();
    state.catalog = data;

    renderDatabases(data.databases);
    renderCountries(data.countries);
    renderCategories(data.categories, data.indicators);
    renderChartTypes(data.chart_types);
  } catch (err) {
    showToast("Error conectando con el backend: " + err.message, "danger");
  }
}

// 1. Renderizar Bases de Datos
function renderDatabases(databases) {
  const select = document.getElementById("databaseSelect");
  select.innerHTML = "";
  databases.forEach((db) => {
    const opt = document.createElement("option");
    opt.value = db.id;
    opt.textContent = `${db.name} ${db.requires_key ? '(Requiere Key)' : '(Abierto)'}`;
    if (db.id === state.activeDatabase) opt.selected = true;
    select.appendChild(opt);
  });

  select.addEventListener("change", (e) => {
    state.activeDatabase = e.target.value;
    const dbObj = databases.find(d => d.id === e.target.value);
    if (dbObj) {
      document.querySelector("#activeDbPill .db-label").textContent = dbObj.name;
    }
  });
}

// 2. Renderizar Países
function renderCountries(countries) {
  const container = document.getElementById("countriesListContainer");
  container.innerHTML = "";

  countries.forEach((c) => {
    const item = document.createElement("label");
    item.className = "check-item";
    item.dataset.code = c.code;
    item.dataset.name = c.name.toLowerCase();
    item.dataset.region = c.region;

    item.innerHTML = `
      <input type="checkbox" value="${c.code}" ${state.selectedCountries.has(c.code) ? "checked" : ""}>
      <span class="check-item-flag">${c.flag}</span>
      <span class="check-item-name">${c.name}</span>
      <span class="check-item-code">${c.code}</span>
    `;

    const chk = item.querySelector("input");
    chk.addEventListener("change", (e) => {
      if (e.target.checked) {
        state.selectedCountries.add(c.code);
      } else {
        state.selectedCountries.delete(c.code);
      }
      updateCountryCount();
    });

    container.appendChild(item);
  });

  // Filtro de búsqueda de países
  const searchInput = document.getElementById("countrySearchInput");
  searchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    const items = container.querySelectorAll(".check-item");
    items.forEach((it) => {
      const match = it.dataset.name.includes(q) || it.dataset.code.toLowerCase().includes(q);
      it.style.display = match ? "flex" : "none";
    });
  });

  updateCountryCount();
}

function updateCountryCount() {
  const badge = document.getElementById("selectedCountriesBadge");
  badge.textContent = `${state.selectedCountries.size} seleccionados`;
}

function filterCountriesByRegion(regionName) {
  if (!state.catalog) return;
  state.selectedCountries.clear();
  state.catalog.countries.forEach((c) => {
    if (c.region === regionName) {
      state.selectedCountries.add(c.code);
    }
  });
  // Actualizar checkboxes
  document.querySelectorAll("#countriesListContainer .check-item input").forEach((chk) => {
    chk.checked = state.selectedCountries.has(chk.value);
  });
  updateCountryCount();
}

function clearCountries() {
  state.selectedCountries.clear();
  document.querySelectorAll("#countriesListContainer .check-item input").forEach((chk) => {
    chk.checked = false;
  });
  updateCountryCount();
}

// 3. Renderizar Categorías y Variables
function renderCategories(categories, indicators) {
  const accordion = document.getElementById("categoriesAccordion");
  accordion.innerHTML = "";

  // Agrupar indicadores por categoría
  const byCategory = {};
  indicators.forEach((ind) => {
    if (!byCategory[ind.category_id]) byCategory[ind.category_id] = [];
    byCategory[ind.category_id].push(ind);
  });

  categories.forEach((cat, idx) => {
    const catInds = byCategory[cat.id] || [];
    if (catInds.length === 0) return;

    const group = document.createElement("div");
    group.className = `category-group ${idx === 0 ? 'open' : ''}`;

    group.innerHTML = `
      <div class="category-header">
        <div class="category-title-group">
          <span>${cat.name}</span>
          <span class="category-count">(${catInds.length})</span>
        </div>
        <svg class="category-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </div>
      <div class="category-items"></div>
    `;

    const itemsContainer = group.querySelector(".category-items");
    catInds.forEach((ind) => {
      const varItem = document.createElement("label");
      varItem.className = "variable-item";
      varItem.dataset.code = ind.code;
      varItem.dataset.col = ind.column;
      varItem.dataset.search = (ind.name + " " + ind.code + " " + (ind.keywords || []).join(" ")).toLowerCase();

      varItem.innerHTML = `
        <div class="variable-item-main">
          <input type="checkbox" value="${ind.code}" ${state.selectedVariables.has(ind.code) ? "checked" : ""}>
          <span class="variable-name">${ind.name}</span>
        </div>
        <div class="variable-meta">
          <span class="variable-units-badge">${ind.units}</span>
          <span class="variable-units-badge">${ind.code}</span>
        </div>
      `;

      const chk = varItem.querySelector("input");
      chk.addEventListener("change", (e) => {
        if (e.target.checked) {
          state.selectedVariables.add(ind.code);
        } else {
          state.selectedVariables.delete(ind.code);
        }
        updateVariableCount();
      });

      itemsContainer.appendChild(varItem);
    });

    // Toggle acordeón
    group.querySelector(".category-header").addEventListener("click", () => {
      group.classList.toggle("open");
    });

    accordion.appendChild(group);
  });

  // Filtro de búsqueda de variables
  const searchInput = document.getElementById("variableSearchInput");
  searchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    const groups = accordion.querySelectorAll(".category-group");
    groups.forEach((grp) => {
      let hasVisible = false;
      const vars = grp.querySelectorAll(".variable-item");
      vars.forEach((v) => {
        const match = !q || v.dataset.search.includes(q);
        v.style.display = match ? "flex" : "none";
        if (match) hasVisible = true;
      });
      if (q) {
        grp.style.display = hasVisible ? "block" : "none";
        if (hasVisible) grp.classList.add("open");
      } else {
        grp.style.display = "block";
      }
    });
  });

  updateVariableCount();
}

function updateVariableCount() {
  const badge = document.getElementById("selectedVariablesBadge");
  const total = state.selectedVariables.size + state.selectedFormulas.size;
  badge.textContent = `${total} seleccionadas`;
}

// 4. Renderizar Tipos de Gráficos
function renderChartTypes(chartTypes) {
  const grid = document.getElementById("chartTypesGrid");
  grid.innerHTML = "";

  chartTypes.forEach((ct) => {
    const card = document.createElement("div");
    card.className = `chart-type-card ${ct.id === state.selectedChartType ? 'selected' : ''}`;
    card.dataset.id = ct.id;
    card.title = ct.description;

    card.innerHTML = `
      <span class="chart-type-icon">${ct.icon}</span>
      <div class="chart-type-info">
        <span class="chart-type-name">${ct.name}</span>
      </div>
    `;

    card.addEventListener("click", () => {
      document.querySelectorAll(".chart-type-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      state.selectedChartType = ct.id;
    });

    grid.appendChild(card);
  });
}

// ============================================================================
// Constructor y Almacenamiento de Fórmulas (localStorage)
// ============================================================================
const FORMULAS_STORAGE_KEY = "macrodata_formulas_v1";

function loadStoredFormulas() {
  try {
    const raw = localStorage.getItem(FORMULAS_STORAGE_KEY);
    if (raw) {
      state.formulas = JSON.parse(raw);
    } else {
      // Fórmulas de ejemplo predeterminadas
      state.formulas = [
        {
          name: "crecimiento_pib_pc_ma3",
          expression: "ma(crecimiento_pib_pc, 3)",
          label: "Crecimiento PIB pc (Promedio Móvil 3 años)",
          units: "% anual"
        }
      ];
      saveFormulasToStorage();
    }
  } catch (e) {
    state.formulas = [];
  }
  renderSavedFormulas();
}

function saveFormulasToStorage() {
  try {
    localStorage.setItem(FORMULAS_STORAGE_KEY, JSON.stringify(state.formulas));
  } catch (e) {
    console.error("Error guardando fórmulas en localStorage:", e);
  }
}

function renderSavedFormulas() {
  const container = document.getElementById("savedFormulasList");
  container.innerHTML = "";

  if (state.formulas.length === 0) {
    container.innerHTML = `<div style="font-size: 11.5px; color: var(--text-dim); text-align: center; padding: 6px;">No hay fórmulas guardadas. Haz clic en "Nueva Fórmula".</div>`;
    return;
  }

  state.formulas.forEach((f, idx) => {
    const item = document.createElement("div");
    item.className = "saved-formula-item";

    const isChecked = state.selectedFormulas.has(f.name);

    item.innerHTML = `
      <div class="saved-formula-main">
        <input type="checkbox" value="${f.name}" ${isChecked ? "checked" : ""}>
        <div>
          <span class="formula-code-name">${f.label || f.name}</span>
          <div class="formula-expr-preview">${f.expression}</div>
        </div>
      </div>
      <button class="formula-delete-btn" title="Eliminar fórmula" onclick="deleteFormula(${idx})">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    `;

    const chk = item.querySelector("input");
    chk.addEventListener("change", (e) => {
      if (e.target.checked) {
        state.selectedFormulas.add(f.name);
      } else {
        state.selectedFormulas.delete(f.name);
      }
      updateVariableCount();
    });

    container.appendChild(item);
  });
}

// Botón "Nueva Fórmula"
document.getElementById("toggleFormulaFormBtn").addEventListener("click", () => {
  const card = document.getElementById("formulaBuilderCard");
  const isHidden = card.style.display === "none";
  card.style.display = isHidden ? "block" : "none";
  if (isHidden) {
    document.getElementById("formulaNameInput").focus();
  }
});

function cancelFormulaForm() {
  document.getElementById("formulaBuilderCard").style.display = "none";
  document.getElementById("formulaNameInput").value = "";
  document.getElementById("formulaExprInput").value = "";
  document.getElementById("formulaLabelInput").value = "";
}

function insertFormulaHelper(text) {
  const input = document.getElementById("formulaExprInput");
  const start = input.selectionStart || input.value.length;
  const end = input.selectionEnd || input.value.length;
  const val = input.value;
  input.value = val.substring(0, start) + text + val.substring(end);
  input.focus();
  const nextPos = start + text.length;
  input.setSelectionRange(nextPos, nextPos);
}

function saveFormula() {
  const name = document.getElementById("formulaNameInput").value.trim().toLowerCase().replace(/\s+/g, "_");
  const expression = document.getElementById("formulaExprInput").value.trim();
  const label = document.getElementById("formulaLabelInput").value.trim() || name;

  if (!name) {
    showToast("Debes ingresar un nombre o identificador para la variable.", "warning");
    return;
  }
  if (!expression) {
    showToast("Debes ingresar una expresión matemática para la fórmula.", "warning");
    return;
  }

  // Verificar si ya existe
  const existingIdx = state.formulas.findIndex(f => f.name === name);
  const newFormula = { name, expression, label, units: "Calculado" };

  if (existingIdx >= 0) {
    state.formulas[existingIdx] = newFormula;
  } else {
    state.formulas.push(newFormula);
  }

  // Seleccionar automáticamente la fórmula creada
  state.selectedFormulas.add(name);

  saveFormulasToStorage();
  renderSavedFormulas();
  cancelFormulaForm();
  updateVariableCount();
  showToast(`Fórmula '${name}' guardada en localStorage.`, "success");
}

function deleteFormula(idx) {
  const f = state.formulas[idx];
  if (f) {
    state.selectedFormulas.delete(f.name);
    state.formulas.splice(idx, 1);
    saveFormulasToStorage();
    renderSavedFormulas();
    updateVariableCount();
    showToast("Fórmula eliminada.", "info");
  }
}

// ============================================================================
// Rango de Años
// ============================================================================
function setYearRange(start, end) {
  document.getElementById("yearStartInput").value = start;
  document.getElementById("yearEndInput").value = end;
}

// ============================================================================
// Generación de Gráficos y Consulta Backend (/api/generate)
// ============================================================================
async function triggerGenerate() {
  const countries = Array.from(state.selectedCountries);
  const vars = Array.from(state.selectedVariables);
  const formulaNames = Array.from(state.selectedFormulas);

  if (countries.length === 0) {
    showToast("Por favor selecciona al menos un país en la sección 2.", "warning");
    return;
  }

  if (vars.length === 0 && formulaNames.length === 0) {
    showToast("Por favor selecciona al menos una variable o fórmula en las secciones 3 y 4.", "warning");
    return;
  }

  const yearStart = parseInt(document.getElementById("yearStartInput").value) || 1990;
  const yearEnd = parseInt(document.getElementById("yearEndInput").value) || 2024;

  if (yearStart >= yearEnd) {
    showToast("El año inicial debe ser menor al año final.", "warning");
    return;
  }

  // Fórmulas seleccionadas
  const activeFormulas = state.formulas.filter(f => state.selectedFormulas.has(f.name));

  // Combinar variables + fórmulas seleccionadas
  const allRequestedVars = [...vars, ...formulaNames];

  const payload = {
    database: state.activeDatabase,
    variables: allRequestedVars,
    countries: countries,
    year_start: yearStart,
    year_end: yearEnd,
    chart_type: state.selectedChartType,
    formulas: activeFormulas,
    pin: localStorage.getItem("macrodata_pin") || "desarrollo2026"
  };

  // Mostrar estado de carga
  document.getElementById("workspaceEmpty").style.display = "none";
  document.getElementById("workspaceResults").style.display = "none";
  document.getElementById("workspaceLoading").style.display = "block";
  document.getElementById("loadingStatusText").textContent = "Descargando datos del Banco Mundial y procesando...";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    document.getElementById("workspaceLoading").style.display = "none";

    if (!data.success) {
      showToast(data.error || "Error al procesar los datos.", "danger");
      document.getElementById("workspaceEmpty").style.display = "block";
      return;
    }

    // Éxito: renderizar resultados
    renderResults(data);
  } catch (err) {
    document.getElementById("workspaceLoading").style.display = "none";
    document.getElementById("workspaceEmpty").style.display = "block";
    showToast("Error en la solicitud: " + err.message, "danger");
  }
}

// Renderizar Resultados en el Workspace Central
function renderResults(data) {
  state.lastGeneratedData = data;
  const resultsCard = document.getElementById("workspaceResults");
  resultsCard.style.display = "flex";

  // Título y subtítulo
  document.getElementById("resultTitle").textContent = data.metadata.title || "Gráfico Macroeconómico";
  document.getElementById("resultSubtitle").textContent = data.metadata.subtitle || "";
  document.getElementById("chartSourceFooter").textContent = data.metadata.source || "Fuente: Banco Mundial (WDI).";

  // Imagen del gráfico (Base64)
  const chartImg = document.getElementById("renderedChartImg");
  chartImg.src = `data:image/png;base64,${data.chart_base64}`;

  // Botones de descarga
  document.getElementById("downloadPngBtn").href = data.chart_download_url;
  document.getElementById("downloadSvgBtn").href = data.svg_download_url;
  document.getElementById("downloadCsvBtn").href = data.csv_download_url;

  // Estadísticas descriptivas
  renderStatistics(data.statistics);

  // Código Python
  document.getElementById("pythonCodeContent").textContent = data.python_code || "# No se pudo generar el script.";

  // Tabla de datos preview
  renderDataTable(data.data_preview);

  // Desplazar suavemente a la visualización
  resultsCard.scrollIntoView({ behavior: "smooth" });
}

function renderStatistics(stats) {
  const grid = document.getElementById("statsSummaryGrid");
  grid.innerHTML = "";

  const entries = Object.entries(stats);
  if (entries.length === 0) {
    grid.style.display = "none";
    return;
  }
  grid.style.display = "grid";

  entries.forEach(([col, s]) => {
    const card = document.createElement("div");
    card.className = "stat-card";
    card.innerHTML = `
      <div class="stat-card-title">${s.variable}</div>
      <div class="stat-card-values">
        <div>
          <span class="stat-main-num">${s.mean}</span>
          <span class="stat-secondary">(Media)</span>
        </div>
        <div class="stat-secondary">
          <span>Min: ${s.min}</span> | <span>Max: ${s.max}</span>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function renderDataTable(records) {
  const container = document.getElementById("dataTableContainer");
  container.innerHTML = "";

  if (!records || records.length === 0) {
    container.innerHTML = `<div style="padding: 16px; color: var(--text-dim); text-align: center;">No hay datos para mostrar.</div>`;
    return;
  }

  const headers = Object.keys(records[0]);
  const table = document.createElement("table");
  table.className = "data-table";

  let html = "<thead><tr>";
  headers.forEach(h => {
    html += `<th>${h}</th>`;
  });
  html += "</tr></thead><tbody>";

  records.forEach(row => {
    html += "<tr>";
    headers.forEach(h => {
      const val = row[h];
      const displayVal = (typeof val === "number") ? val.toLocaleString(undefined, { maximumFractionDigits: 2 }) : (val ?? "");
      html += `<td>${displayVal}</td>`;
    });
    html += "</tr>";
  });

  html += "</tbody>";
  table.innerHTML = html;
  container.appendChild(table);
}

// ============================================================================
// Pestañas de Inspección (Código vs Datos)
// ============================================================================
function switchTab(tabName) {
  document.querySelectorAll(".inspector-tabs .tab-btn").forEach((btn, idx) => {
    btn.classList.toggle("active", (tabName === "code" && idx === 0) || (tabName === "data" && idx === 1));
  });
  document.getElementById("codePanel").classList.toggle("active", tabName === "code");
  document.getElementById("dataPanel").classList.toggle("active", tabName === "data");
}

function copyPythonCode() {
  const code = document.getElementById("pythonCodeContent").textContent;
  navigator.clipboard.writeText(code).then(() => {
    const textSpan = document.getElementById("copyCodeText");
    const orig = textSpan.textContent;
    textSpan.textContent = "¡Copiado!";
    setTimeout(() => { textSpan.textContent = orig; }, 2000);
    showToast("Código copiado al portapapeles.", "success");
  });
}

// ============================================================================
// Demos Preconfigurados (Un Clic)
// ============================================================================
function loadPresetDemo(type) {
  state.selectedCountries.clear();
  state.selectedVariables.clear();
  state.selectedFormulas.clear();

  if (type === "pib_pc_brics") {
    state.selectedCountries.add("IND");
    state.selectedCountries.add("CHN");
    state.selectedVariables.add("NY.GDP.PCAP.KD");
    state.selectedChartType = "line";
    setYearRange(1990, 2024);
  } else if (type === "inversion_latam") {
    state.selectedCountries.add("ARG");
    state.selectedCountries.add("BRA");
    state.selectedCountries.add("CHL");
    state.selectedCountries.add("URY");
    state.selectedCountries.add("MEX");
    state.selectedVariables.add("NE.GDI.FTOT.ZS");
    state.selectedChartType = "bar";
    setYearRange(2010, 2024);
  } else if (type === "dispersion_crecimiento") {
    state.selectedCountries.add("IND");
    state.selectedCountries.add("CHN");
    state.selectedCountries.add("BRA");
    state.selectedCountries.add("USA");
    state.selectedVariables.add("NE.GDI.FTOT.ZS");
    state.selectedVariables.add("NY.GDP.MKTP.KD.ZG");
    state.selectedChartType = "scatter";
    setYearRange(1995, 2024);
  } else if (type === "sectores_india") {
    state.selectedCountries.add("IND");
    state.selectedVariables.add("NV.AGR.TOTL.ZS");
    state.selectedVariables.add("NV.IND.TOTL.ZS");
    state.selectedVariables.add("NV.SRV.TOTL.ZS");
    state.selectedChartType = "stacked_area";
    setYearRange(1980, 2024);
  }

  // Sincronizar UI
  syncSelectionsToUI();
  triggerGenerate();
}

function syncSelectionsToUI() {
  // Países
  document.querySelectorAll("#countriesListContainer .check-item input").forEach(chk => {
    chk.checked = state.selectedCountries.has(chk.value);
  });
  updateCountryCount();

  // Variables
  document.querySelectorAll("#categoriesAccordion .variable-item input").forEach(chk => {
    chk.checked = state.selectedVariables.has(chk.value);
  });
  updateVariableCount();

  // Tipo de Gráfico
  document.querySelectorAll(".chart-type-card").forEach(card => {
    card.classList.toggle("selected", card.dataset.id === state.selectedChartType);
  });
}

// ============================================================================
// Descubrimiento de Bases de Datos con IA (LLM Agent Modal)
// ============================================================================
const dbModal = document.getElementById("databaseModal");
document.getElementById("openDbModalBtn").addEventListener("click", () => {
  dbModal.style.display = "flex";
  document.getElementById("dbQueryInput").focus();
});

function closeDbModal() {
  dbModal.style.display = "none";
}

let currentDiscoveredDatabase = null;

async function searchDatabaseWithLLM() {
  const query = document.getElementById("dbQueryInput").value.trim();
  if (!query) {
    showToast("Escribe el nombre de la base o institución que deseas investigar.", "warning");
    return;
  }

  const loading = document.getElementById("dbSearchLoading");
  const resultBox = document.getElementById("dbSearchResult");
  loading.style.display = "flex";
  resultBox.style.display = "none";

  try {
    const res = await fetch("/api/databases/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        api_key: localStorage.getItem("macrodata_api_key") || null
      })
    });

    const data = await res.json();
    loading.style.display = "none";

    if (!data.success && data.error) {
      showToast(data.error, "danger");
      return;
    }

    currentDiscoveredDatabase = data;
    renderDiscoveredDatabase(data);
  } catch (err) {
    loading.style.display = "none";
    showToast("Error al consultar el agente de bases de datos: " + err.message, "danger");
  }
}

function renderDiscoveredDatabase(data) {
  const resultBox = document.getElementById("dbSearchResult");
  resultBox.style.display = "block";

  document.getElementById("discoveredDbName").textContent = data.name;
  document.getElementById("discoveredDbAuth").textContent = data.auth_type || "Acceso API";
  document.getElementById("discoveredDbDesc").textContent = data.description || "";
  document.getElementById("discoveredDbEndpoint").textContent = data.api_endpoint || "No especificado";

  const indContainer = document.getElementById("discoveredIndicatorsList");
  indContainer.innerHTML = "";
  (data.suggested_indicators || []).forEach(ind => {
    const tag = document.createElement("span");
    tag.className = "ind-tag";
    tag.textContent = `${ind.name} (${ind.code})`;
    indContainer.appendChild(tag);
  });

  document.getElementById("discoveredConnectorCode").textContent = data.connector_code || "# Código no disponible";
}

function activateDiscoveredDatabase() {
  if (!currentDiscoveredDatabase) return;
  const select = document.getElementById("databaseSelect");
  const id = currentDiscoveredDatabase.name.toLowerCase().replace(/[^a-z0-9]/g, "_");

  // Agregar al selector si no existe
  let opt = select.querySelector(`option[value="${id}"]`);
  if (!opt) {
    opt = document.createElement("option");
    opt.value = id;
    opt.textContent = `${currentDiscoveredDatabase.name} (Conectada con IA)`;
    select.appendChild(opt);
  }
  opt.selected = true;
  state.activeDatabase = id;
  document.querySelector("#activeDbPill .db-label").textContent = currentDiscoveredDatabase.name;

  closeDbModal();
  showToast(`Base de datos '${currentDiscoveredDatabase.name}' conectada y seleccionada.`, "success");
}

// ============================================================================
// Modal de Zoom de Gráfico
// ============================================================================
const zoomModal = document.getElementById("chartZoomModal");
function openChartZoom() {
  const mainImg = document.getElementById("renderedChartImg");
  if (!mainImg.src) return;
  document.getElementById("zoomedChartImg").src = mainImg.src;
  zoomModal.style.display = "flex";
}
function closeChartZoom() {
  zoomModal.style.display = "none";
}

// ============================================================================
// Configuración y PIN
// ============================================================================
const configModal = document.getElementById("configModal");
document.getElementById("openConfigBtn").addEventListener("click", () => {
  configModal.style.display = "flex";
  document.getElementById("pinInput").value = localStorage.getItem("macrodata_pin") || "desarrollo2026";
  document.getElementById("apiKeyInput").value = localStorage.getItem("macrodata_api_key") || "";
});

function closeConfigModal() {
  configModal.style.display = "none";
}

function loadStoredSettings() {
  const pin = localStorage.getItem("macrodata_pin");
  if (!pin) localStorage.setItem("macrodata_pin", "desarrollo2026");
}

async function saveConfigSettings() {
  const pin = document.getElementById("pinInput").value.trim();
  const apiKey = document.getElementById("apiKeyInput").value.trim();

  localStorage.setItem("macrodata_pin", pin);
  if (apiKey) {
    localStorage.setItem("macrodata_api_key", apiKey);
    try {
      await fetch("/api/config/key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey, pin: pin })
      });
    } catch (e) {
      console.warn("No se pudo persistir en backend la API key");
    }
  }

  closeConfigModal();
  showToast("Configuración guardada exitosamente.", "success");
}

// ============================================================================
// Notificaciones Toast
// ============================================================================
function showToast(message, type = "info") {
  const toast = document.getElementById("toastNotification");
  toast.textContent = message;
  toast.style.display = "block";

  if (type === "warning") {
    toast.style.borderColor = "var(--warning)";
  } else if (type === "danger") {
    toast.style.borderColor = "var(--danger)";
  } else if (type === "success") {
    toast.style.borderColor = "var(--accent)";
  } else {
    toast.style.borderColor = "var(--border-focus)";
  }

  setTimeout(() => {
    toast.style.display = "none";
  }, 4000);
}
