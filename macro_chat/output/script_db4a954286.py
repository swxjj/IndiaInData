# ==============================================================================
# Script de Reproducibilidad - Cátedra de Desarrollo Económico (UNS)
# Título: Comparación Macroeconómica: India
# Fuente de datos: Banco Mundial (WDI)
# ==============================================================================

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. Parámetros de la consulta
INDICATORS = [{'code': 'NV.IND.TOTL.ZS', 'name': 'Industria, valor agregado (% del PIB)', 'column': 'industria_va_pct_gdp', 'units': '% del PIB'}, {'code': 'NV.SRV.TOTL.ZS', 'name': 'Servicios, valor agregado (% del PIB)', 'column': 'servicios_va_pct_gdp', 'units': '% del PIB'}]
COUNTRIES = ['India']
START_YEAR = None
END_YEAR = None

# 2. Descarga de datos oficiales desde la API del Banco Mundial
def fetch_wdi_data(indicators, countries, start=None, end=None):
    base_url = "https://api.worldbank.org/v2"
    country_param = ";".join(countries)
    all_records = []

    for ind in indicators:
        code = ind["code"]
        col = ind.get("column", code.lower().replace(".", "_"))
        name = ind.get("name", code)

        date_param = f"&date={start}:{end}" if start and end else ("&date={start}:2025" if start else "")
        url = f"{base_url}/country/{country_param}/indicator/{code}?format=json&per_page=1000{date_param}"

        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if len(data) >= 2 and data[1]:
            for item in data[1]:
                val = item.get("value")
                year = item.get("date")
                c_name = item.get("country", {}).get("value")
                c_id = item.get("countryiso3code")
                if year and c_id:
                    all_records.append({
                        "anio": int(year),
                        "pais": c_name,
                        "codigo_pais": c_id,
                        "indicador_col": col,
                        "valor": float(val) if val is not None else None
                    })

    df_raw = pd.DataFrame(all_records)
    df_wide = df_raw.pivot_table(
        index=["anio", "pais", "codigo_pais"],
        columns="indicador_col",
        values="valor"
    ).reset_index()
    return df_wide.sort_values(by=["pais", "anio"]).reset_index(drop=True)

# 3. Descarga y exportación a CSV en formato Panel Ancho
print("Descargando datos oficiales...")
df = fetch_wdi_data(INDICATORS, COUNTRIES, START_YEAR, END_YEAR)
df.to_csv("datos_macro.csv", index=False, sep=",", decimal=".")
print("Archivo 'datos_macro.csv' guardado exitosamente.")

# 4. Configuración y Renderizado del Gráfico Académico
ACADEMIC_COLORS = ["#1B365D", "#8B263E", "#2E6F40", "#4A5568", "#D97706", "#6B21A8"]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "figure.dpi": 300
})

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
indicator_cols = ['industria_va_pct_gdp', 'servicios_va_pct_gdp']
indicator_names = ['Industria, valor agregado (% del PIB)', 'Servicios, valor agregado (% del PIB)']
countries_unique = df["pais"].unique()

color_idx = 0
for country in countries_unique:
    df_c = df[df["pais"] == country]
    for idx, col in enumerate(indicator_cols):
        df_valid = df_c.dropna(subset=[col])
        if df_valid.empty:
            continue
        label = country if len(indicator_cols) == 1 else f"{country} - {indicator_names[idx]}"
        ax.plot(
            df_valid["anio"],
            df_valid[col],
            label=label,
            color=ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)],
            linewidth=2.2,
            marker="o",
            markersize=4,
            markevery=max(1, len(df_valid) // 12)
        )
        color_idx += 1

# Estilo académico sobrio
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", linestyle="--", alpha=0.5, color="#CBD5E1")
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))

if "Valores armonizados":
    ax.set_ylabel("Valores armonizados", labelpad=8)

fig.text(0.125, 0.96, "Comparación Macroeconómica: India", fontsize=13, fontweight="bold")
fig.text(0.125, 0.92, "Series históricas armonizadas (Inicio–Presente)", fontsize=10, color="#4A5568")
fig.text(0.125, 0.02, "Fuente: Banco Mundial (WDI). Cátedra de Desarrollo Económico (UNS).", fontsize=8.5, color="#718096", style="italic")

ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")
plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.90])
plt.savefig("grafico_academico.png", dpi=300)
print("Gráfico 'grafico_academico.png' generado en alta resolución.")
plt.show()
