import os
import json
import shutil
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from adjustText import adjust_text

# -----------------------------------------------------------------------------
# 1. DESCARGA Y CLASIFICACIÓN DE TODOS LOS PAÍSES (WORLD BANK WDI)
# -----------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_dir = os.path.join(base_dir, "data", "raw")
out_dir = os.path.join(base_dir, "output")
fig_dir = os.path.join(out_dir, "figures")
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(fig_dir, exist_ok=True)

print("-> Consultando metadatos de países del Banco Mundial...")
url_countries = "https://api.worldbank.org/v2/country?per_page=400&format=json"
req_c = urllib.request.Request(url_countries, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req_c, timeout=20) as r:
    countries_raw = json.loads(r.read().decode("utf-8"))[1]

# Filtrar agregados regionales (region.id == 'NA') y conservar solo países soberanos/reales
actual_countries = {}
advanced_isos = {"USA", "CAN", "JPN", "KOR", "SGP", "AUS", "NZL", "ISR"}

def classify_region(iso, region, income):
    if "Latin America" in region:
        return "Latam"
    if iso in advanced_isos or "North America" in region or ("Europe" in region and income == "High income"):
        return "Primer Mundo"
    if "Sub-Saharan Africa" in region or iso in {"EGY", "MAR", "DZA", "TUN", "LBY", "SDN"}:
        return "África"
    return "Asia"

for c in countries_raw:
    if c["region"]["id"] != "NA":
        iso = c["id"]
        reg_name = c["region"]["value"].strip()
        inc_name = c["incomeLevel"]["value"].strip()
        actual_countries[iso] = {
            "name": c["name"],
            "region_wdi": reg_name,
            "income": inc_name,
            "group": classify_region(iso, reg_name, inc_name)
        }

print(f"   Paises reales identificados: {len(actual_countries)}")

# -----------------------------------------------------------------------------
# 2. DESCARGA DE LA SERIE DE PIB PER CÁPITA CONSTANTE PPA (NY.GDP.PCAP.PP.KD)
# -----------------------------------------------------------------------------
print("-> Descargando indicador NY.GDP.PCAP.PP.KD (1990-2025) para todos los países...")
url_gdp = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.KD?date=1990:2025&format=json&per_page=16000"
req_g = urllib.request.Request(url_gdp, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req_g, timeout=45) as r:
    gdp_raw = json.loads(r.read().decode("utf-8"))[1]

records = []
for d in gdp_raw:
    iso = d.get("countryiso3code")
    if iso in actual_countries and d.get("value") is not None:
        records.append({
            "iso": iso,
            "country": actual_countries[iso]["name"],
            "group": actual_countries[iso]["group"],
            "year": int(d["date"]),
            "gdp_pc_ppp": float(d["value"])
        })

df_all = pd.DataFrame(records)
# Guardar copia cruda
df_all.to_csv(os.path.join(raw_dir, "wdi_gdp_pcap_ppp_all_raw.csv"), index=False, encoding="utf-8")

# Pivotear por año
piv = df_all.pivot(index=["iso", "country", "group"], columns="year", values="gdp_pc_ppp").reset_index()

# -----------------------------------------------------------------------------
# 3. FILTRADO: PAÍSES CON 1990 Y 2025 (O 2024, NUNCA MENOS)
# -----------------------------------------------------------------------------
# Países con 1990 y al menos 2024
valid = piv[piv[1990].notna() & (piv[2025].notna() | piv[2024].notna())].copy()

valid["end_year"] = np.where(valid[2025].notna(), 2025, 2024)
valid["gdp_end"] = np.where(valid[2025].notna(), valid[2025], valid[2024])
valid["years_elapsed"] = valid["end_year"] - 1990

# Logaritmos en base 10 (misma convención que los datos originales)
valid["logpib90"] = np.log10(valid[1990])
valid["logpbi_end"] = np.log10(valid["gdp_end"])

# Tasa como resta directa de logs sobre años transcurridos
valid["tasa_promedio"] = (valid["logpbi_end"] - valid["logpib90"]) / valid["years_elapsed"]

# Ordenar por grupo y país
valid = valid.sort_values(by=["group", "country"]).reset_index(drop=True)

print(f"-> Países totales con datos en 1990 y 2025/2024: {len(valid)}")
print(valid["group"].value_counts())

# Exportar tabla completa limpia
csv_out = os.path.join(out_dir, "convergencia_mundial_1990_2025.csv")
xlsx_out = os.path.join(out_dir, "convergencia_mundial_1990_2025.xlsx")
valid[["iso", "country", "group", "end_year", 1990, "gdp_end", "logpib90", "logpbi_end", "tasa_promedio"]].to_csv(csv_out, index=False, encoding="utf-8")
valid[["iso", "country", "group", "end_year", 1990, "gdp_end", "logpib90", "logpbi_end", "tasa_promedio"]].to_excel(xlsx_out, index=False)
print(f"   Tabla guardada en CSV: {csv_out}")
print(f"   Tabla guardada en Excel: {xlsx_out}")

# -----------------------------------------------------------------------------
# 4. REGRESIONES LINEALES
# -----------------------------------------------------------------------------
reg1 = stats.linregress(valid["logpib90"], valid["logpbi_end"])
reg2 = stats.linregress(valid["logpib90"], valid["tasa_promedio"])

print("\n--- RESULTADOS DE REGRESIÓN (MUESTRA MUNDIAL N = {}) ---".format(len(valid)))
print(f"Gráfico 1: Y = {reg1.slope:.4f} * X + {reg1.intercept:.4f}  | R2 = {reg1.rvalue**2:.4f}, p = {reg1.pvalue:.2e}")
print(f"Gráfico 2: Y = {reg2.slope:.4f} * X + {reg2.intercept:.4f} | R2 = {reg2.rvalue**2:.4f}, p = {reg2.pvalue:.2e}")

# -----------------------------------------------------------------------------
# 5. CONFIGURACIÓN VISUAL Y GRÁFICOS (SIMPLEZA PURA)
# -----------------------------------------------------------------------------
color_map = {
    "Primer Mundo": "#2563eb",  # Azul
    "Latam": "#7c3aed",         # Violeta
    "África": "#b45309",        # Marrón / Ocre
    "Asia": "#16a34a"           # Verde
}
india_color = "#ea580c"         # Naranja vivo destacado

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10

x_min = valid["logpib90"].min() - 0.1
x_max = valid["logpib90"].max() + 0.1
x_line = np.linspace(x_min, x_max, 100)

# Limpiar nombres para etiquetas compactas y legibles
def clean_label(name):
    # Nombres comunes y compactos
    n = name.split(",")[0].replace("Republic", "Rep.").replace("Federation", "Fed.").replace("Democratic", "Dem.")
    translations = {
        "United States": "EE.UU.",
        "United Kingdom": "Reino Unido",
        "Russian Fed.": "Rusia",
        "South Africa": "Sudáfrica",
        "Germany": "Alemania",
        "France": "Francia",
        "Italy": "Italia",
        "Spain": "España",
        "Japan": "Japón",
        "Brazil": "Brasil",
        "Mexico": "México",
        "Egypt": "Egipto",
        "Morocco": "Marruecos",
        "Algeria": "Argelia",
        "Cameroon": "Camerún",
        "Ethiopia": "Etiopía",
        "Kenya": "Kenia",
        "Pakistan": "Pakistán",
        "Philippines": "Filipinas",
        "Norway": "Noruega",
        "Canada": "Canadá",
        "Saudi Arabia": "Arabia Saudita",
        "United Arab Emirates": "Emiratos Árabes",
        "Korea": "Corea del Sur"
    }
    return translations.get(n, n)

valid["short_name"] = valid["country"].apply(clean_label)

# =============================================================================
# GRÁFICO 1: MUNDIAL (PIB 1990 vs PIB FINAL)
# =============================================================================
print("-> Generando Gráfico 1 Mundial...")
fig1, ax1 = plt.subplots(figsize=(15, 10.5), dpi=300)

# Puntos por grupo
for group, color in color_map.items():
    sub = valid[(valid["group"] == group) & (valid["iso"] != "IND")]
    ax1.scatter(sub["logpib90"], sub["logpbi_end"], c=color, s=40, alpha=0.75, edgecolors="white", linewidths=0.5, zorder=3)

# India destacada
ind_row = valid[valid["iso"] == "IND"].iloc[0]
ax1.scatter(ind_row["logpib90"], ind_row["logpbi_end"], c=india_color, s=170, edgecolors="#7c2d12", linewidths=2.5, zorder=5)

# Recta de tendencia
y_trend1 = reg1.intercept + reg1.slope * x_line
ax1.plot(x_line, y_trend1, color="#dc2626", linewidth=2.2, zorder=4)

# Ecuación en texto directo
ax1.text(0.70, 0.10, f"y = {reg1.slope:.4f}x + {reg1.intercept:.4f}",
         transform=ax1.transAxes, fontsize=14, fontweight="bold", color="#dc2626")

# Etiquetas de países
texts1 = []
for _, r in valid.iterrows():
    is_ind = r["iso"] == "IND"
    t = ax1.text(r["logpib90"], r["logpbi_end"], f" {r['short_name']}",
                 fontsize=7.5 if not is_ind else 12,
                 fontweight="bold" if is_ind else "normal",
                 color=india_color if is_ind else "#374151")
    texts1.append(t)

adjust_text(texts1, x=valid["logpib90"].values, y=valid["logpbi_end"].values, ax=ax1,
            arrowprops=dict(arrowstyle="-", color="#d1d5db", lw=0.4),
            expand=(1.05, 1.1), time_lim=8.0)

ax1.set_title("PIB per cápita 1990 vs. PIB per cápita 2024/2025 (183 Países)", fontsize=14, fontweight="bold", pad=12)
ax1.set_xlabel("Log PIB per cápita (1990)", fontsize=12, fontweight="bold")
ax1.set_ylabel("Log PIB per cápita (2024/2025)", fontsize=12, fontweight="bold")
fig1.tight_layout()

fig1_path = os.path.join(fig_dir, "grafico1_mundial_logpib90_logpbi25.png")
fig1.savefig(fig1_path, dpi=300, bbox_inches="tight")
plt.close(fig1)
print(f"   Gráfico 1 guardado: {fig1_path}")

# =============================================================================
# GRÁFICO 2: MUNDIAL (PIB 1990 vs TASA PROMEDIO)
# =============================================================================
print("-> Generando Gráfico 2 Mundial...")
fig2, ax2 = plt.subplots(figsize=(15, 10.5), dpi=300)

for group, color in color_map.items():
    sub = valid[(valid["group"] == group) & (valid["iso"] != "IND")]
    ax2.scatter(sub["logpib90"], sub["tasa_promedio"], c=color, s=40, alpha=0.75, edgecolors="white", linewidths=0.5, zorder=3)

ax2.scatter(ind_row["logpib90"], ind_row["tasa_promedio"], c=india_color, s=170, edgecolors="#7c2d12", linewidths=2.5, zorder=5)

y_trend2 = reg2.intercept + reg2.slope * x_line
ax2.plot(x_line, y_trend2, color="#dc2626", linewidth=2.2, zorder=4)

ax2.text(0.70, 0.90, f"y = {reg2.slope:.4f}x + {reg2.intercept:.4f}",
         transform=ax2.transAxes, fontsize=14, fontweight="bold", color="#dc2626")

texts2 = []
for _, r in valid.iterrows():
    is_ind = r["iso"] == "IND"
    t = ax2.text(r["logpib90"], r["tasa_promedio"], f" {r['short_name']}",
                 fontsize=7.5 if not is_ind else 12,
                 fontweight="bold" if is_ind else "normal",
                 color=india_color if is_ind else "#374151")
    texts2.append(t)

adjust_text(texts2, x=valid["logpib90"].values, y=valid["tasa_promedio"].values, ax=ax2,
            arrowprops=dict(arrowstyle="-", color="#d1d5db", lw=0.4),
            expand=(1.05, 1.1), time_lim=8.0)

ax2.set_title("PIB per cápita 1990 vs. Tasa de crecimiento promedio (183 Países)", fontsize=14, fontweight="bold", pad=12)
ax2.set_xlabel("Log PIB per cápita (1990)", fontsize=12, fontweight="bold")
ax2.set_ylabel("Tasa de crecimiento promedio anual", fontsize=12, fontweight="bold")
fig2.tight_layout()

fig2_path = os.path.join(fig_dir, "grafico2_mundial_logpib90_tasa_promedio.png")
fig2.savefig(fig2_path, dpi=300, bbox_inches="tight")
plt.close(fig2)
print(f"   Gráfico 2 guardado: {fig2_path}")

# =============================================================================
# COPIAR A ARTIFACTS
# =============================================================================
artifact_dir = r"C:\Users\USER\.gemini\antigravity-ide\brain\fce23e34-19b1-4072-b485-54c2d0172897"
if os.path.isdir(artifact_dir):
    for f in ["grafico1_mundial_logpib90_logpbi25.png", "grafico2_mundial_logpib90_tasa_promedio.png"]:
        shutil.copy2(os.path.join(fig_dir, f), os.path.join(artifact_dir, f))
    print("   Copiados a directorio de artefactos para visualización.")

print("\n--- ANÁLISIS MUNDIAL COMPLETADO EXITOSAMENTE ---")
