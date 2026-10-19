# ==============================================================================
# Script de Reproducibilidad - Cátedra de Desarrollo Económico (UNS)
# Título: PIB per cápita (USD constantes 2015): Argentina
# Fuente de datos: Banco Mundial (WDI)
# ==============================================================================

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. Parámetros de la consulta
INDICATORS = [{'code': 'NY.GDP.PCAP.KD', 'name': 'PIB per cápita (USD constantes 2015)', 'column': 'pib_per_capita', 'units': 'USD constantes 2015'}]
COUNTRIES = ['Argentina']
START_YEAR = 2023
END_YEAR = None
CHART_TYPE = "line"

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

        resp = requests.get(url, timeout=25)
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
indicator_cols = ['pib_per_capita']
indicator_names = ['PIB per cápita (USD constantes 2015)']
countries_unique = df["pais"].unique()

# Modo 1: Dispersión con línea de tendencia
if CHART_TYPE == "scatter" and len(indicator_cols) >= 2:
    import numpy as np
    x_col = indicator_cols[0]
    y_col = indicator_cols[1]
    valid_df = df.dropna(subset=[x_col, y_col])
    color_idx = 0
    for country in countries_unique:
        df_c = valid_df[valid_df["pais"] == country]
        if df_c.empty:
            continue
        ax.scatter(df_c[x_col], df_c[y_col], label=country, color=ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)], s=55, alpha=0.85)
        color_idx += 1
        last_row = df_c.sort_values("anio").iloc[-1]
        ax.annotate(f"{country} ('{str(int(last_row['anio']))[-2:]})", (last_row[x_col], last_row[y_col]), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
    x_all = valid_df[x_col].values
    y_all = valid_df[y_col].values
    if len(x_all) >= 3:
        slope, intercept = np.polyfit(x_all, y_all, 1)
        r_sq = (np.corrcoef(x_all, y_all)[0, 1] ** 2)
        x_seq = np.linspace(x_all.min(), x_all.max(), 100)
        ax.plot(x_seq, slope * x_seq + intercept, color="#8B263E", linestyle="--", linewidth=1.8, label=f"Tendencia (R² = {r_sq:.2f})")
    ax.set_xlabel(indicator_names[0], labelpad=8)
    ax.set_ylabel(indicator_names[1], labelpad=8)

# Modo 2: Gráfico de barras comparativo
elif CHART_TYPE == "bar":
    import numpy as np
    col = indicator_cols[0]
    data_points = []
    for country in countries_unique:
        df_c = df[df["pais"] == country].dropna(subset=[col])
        if not df_c.empty:
            latest = df_c.sort_values("anio").iloc[-1]
            data_points.append({"pais": country, "valor": latest[col], "anio": int(latest["anio"])})
    if data_points:
        df_bar = pd.DataFrame(data_points).sort_values(by="valor", ascending=True)
        y_pos = np.arange(len(df_bar))
        colors = [ACADEMIC_COLORS[i % len(ACADEMIC_COLORS)] for i in range(len(df_bar))]
        bars = ax.barh(y_pos, df_bar["valor"], color=colors, alpha=0.88, height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{r['pais']} ({r['anio']})" for _, r in df_bar.iterrows()])
        ax.bar_label(bars, fmt="%.1f", padding=5, fontsize=9)
        ax.set_xlabel(indicator_names[0], labelpad=8)

# Modo 3: Áreas apiladas continuas
elif CHART_TYPE == "stacked_area" and len(countries_unique) == 1 and len(indicator_cols) > 1:
    country = countries_unique[0]
    df_c = df[df["pais"] == country].dropna(subset=indicator_cols).sort_values("anio")
    if not df_c.empty:
        years = df_c["anio"].values
        y_series = [df_c[col].values for col in indicator_cols]
        colors = [ACADEMIC_COLORS[i % len(ACADEMIC_COLORS)] for i in range(len(indicator_cols))]
        ax.stackplot(years, *y_series, labels=indicator_names, colors=colors, alpha=0.85)

# Modo 4: Líneas con sombreado de área
elif CHART_TYPE == "area":
    color_idx = 0
    for country in countries_unique:
        df_c = df[df["pais"] == country]
        for idx, col in enumerate(indicator_cols):
            if col not in df_c.columns:
                continue
            df_valid = df_c.dropna(subset=[col])
            if df_valid.empty:
                continue
            color = ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)]
            color_idx += 1
            label = country if len(indicator_cols) == 1 else f"{country} - {indicator_names[idx]}"
            ax.plot(df_valid["anio"], df_valid[col], label=label, color=color, linewidth=2.2)
            ax.fill_between(df_valid["anio"], 0, df_valid[col], color=color, alpha=0.22)

# Modo 5: Líneas estándar
else:
    color_idx = 0
    for country in countries_unique:
        df_c = df[df["pais"] == country]
        for idx, col in enumerate(indicator_cols):
            if col not in df_c.columns:
                continue
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

if "USD constantes 2015":
    ax.set_ylabel("USD constantes 2015", labelpad=8)

fig.text(0.125, 0.96, "PIB per cápita (USD constantes 2015): Argentina", fontsize=13, fontweight="bold")
fig.text(0.125, 0.92, "Series históricas armonizadas (2023–Presente)", fontsize=10, color="#4A5568")
fig.text(0.125, 0.02, "Fuente: Banco Mundial (WDI). Cátedra de Desarrollo Económico (UNS).", fontsize=8.5, color="#718096", style="italic")

ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")
plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.90])
plt.savefig("grafico_academico.png", dpi=300)
print("Gráfico 'grafico_academico.png' generado en alta resolución.")
plt.show()
