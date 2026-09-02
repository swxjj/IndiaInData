import urllib.request
import json
import ssl
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configurar rutas relativas al directorio de TP2
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TP2_DIR = os.path.dirname(SCRIPT_DIR)

DATA_RAW = os.path.join(TP2_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(TP2_DIR, "data", "processed")
OUTPUT_FIGS = os.path.join(TP2_DIR, "output", "figures")

os.makedirs(DATA_RAW, exist_ok=True)
os.makedirs(DATA_PROCESSED, exist_ok=True)
os.makedirs(OUTPUT_FIGS, exist_ok=True)

# Limpiar figuras previas en output/figures
for old_fig in glob.glob(os.path.join(OUTPUT_FIGS, "*.png")):
    try:
        os.remove(old_fig)
    except Exception:
        pass

# Contexto SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Solo India y China
countries = ["IND", "CHN"]
c_str = ";".join(countries)

indicators = {
    "NY.GDP.PCAP.KD": "gdp_pc_const_2015_usd",
    "NY.GDP.PCAP.CD": "gdp_pc_curr_usd",
    "NY.GDP.PCAP.KD.ZG": "gdp_pc_growth_annual_pct",
    "NY.GDP.MKTP.KD": "gdp_const_2015_usd",
    "NY.GDP.MKTP.CD": "gdp_curr_usd",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_annual_pct",
    "SP.POP.TOTL": "population_total",
    "NE.GDI.FTOT.ZS": "gfcf_pct_gdp",
    "NE.GDI.FTOT.KD": "gfcf_const_2015_usd",
    "NE.GDI.FTOT.CD": "gfcf_curr_usd",
    "NE.GDI.TOTL.ZS": "gcf_pct_gdp",
    "NE.GDI.TOTL.KD": "gcf_const_2015_usd",
    "NE.GDI.TOTL.CD": "gcf_curr_usd"
}

print("Descargando datos del Banco Mundial para India y China...")
all_records = []

for ind_code, col_name in indicators.items():
    url = f"http://api.worldbank.org/v2/country/{c_str}/indicator/{ind_code}?format=json&per_page=1000"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if len(data) > 1 and data[1]:
                    for rec in data[1]:
                        all_records.append({
                            "country_code": rec['countryiso3code'],
                            "country_name": rec['country']['value'],
                            "year": int(rec['date']),
                            "indicator": col_name,
                            "value": rec['value']
                        })
            break
        except Exception as e:
            if attempt == 2:
                print(f"Error en {ind_code}: {e}")

df_raw = pd.DataFrame(all_records)
df_pivot = df_raw.pivot(index=["country_code", "country_name", "year"], columns="indicator", values="value").reset_index()
df_pivot = df_pivot.sort_values(["country_code", "year"]).reset_index(drop=True)

# Guardar RAW (Solo IND y CHN)
raw_path = os.path.join(DATA_RAW, "wdi_raw_indicators_1960_2025.csv")
df_pivot.to_csv(raw_path, index=False)
print(f"Datos brutos guardados en: {raw_path}")

# Filtrar desde 1967
df_1967 = df_pivot[df_pivot["year"] >= 1967].copy()

# Métricas derivadas
df_1967["delta_gdp_const_2015_usd"] = df_1967.groupby("country_code")["gdp_const_2015_usd"].diff()
df_1967["icor_gfcf_annual"] = df_1967["gfcf_pct_gdp"] / df_1967["gdp_growth_annual_pct"]
df_1967["icor_gcf_annual"] = df_1967["gcf_pct_gdp"] / df_1967["gdp_growth_annual_pct"]
df_1967["icor_marginal_annual"] = df_1967["gfcf_const_2015_usd"] / df_1967["delta_gdp_const_2015_usd"]

# Medias móviles de 5 años
df_1967["gdp_growth_5yr_ma"] = df_1967.groupby("country_code")["gdp_growth_annual_pct"].transform(lambda x: x.rolling(5, min_periods=3).mean())
df_1967["gdp_pc_growth_5yr_ma"] = df_1967.groupby("country_code")["gdp_pc_growth_annual_pct"].transform(lambda x: x.rolling(5, min_periods=3).mean())
df_1967["gfcf_pct_5yr_ma"] = df_1967.groupby("country_code")["gfcf_pct_gdp"].transform(lambda x: x.rolling(5, min_periods=3).mean())
df_1967["icor_gfcf_5yr_smoothed"] = df_1967["gfcf_pct_5yr_ma"] / df_1967["gdp_growth_5yr_ma"]

# Guardar Anual Procesado
annual_path = os.path.join(DATA_PROCESSED, "wdi_macro_annual_1967_2025.csv")
df_1967.to_csv(annual_path, index=False)
print(f"Datos anuales procesados guardados en: {annual_path}")

# ==========================================
# GENERAR CSV RESUMEN
# ==========================================
summary_rows = []
country_map = {"IND": "India", "CHN": "China"}

for c_code in ["IND", "CHN"]:
    c_name = country_map[c_code]
    sub = df_1967[df_1967["country_code"] == c_code].copy()
    
    r_1967 = sub[sub["year"] == 1967].iloc[0]
    r_latest = sub.dropna(subset=["gdp_const_2015_usd"]).iloc[-1]
    latest_yr = int(r_latest["year"])
    
    # 1967
    summary_rows.append({
        "country": c_name,
        "country_code": c_code,
        "corte_o_periodo": "Año 1967 (Punto de partida)",
        "año_referencia": "1967",
        "pib_pc_real_usd2015": round(r_1967["gdp_pc_const_2015_usd"], 2),
        "crec_pib_pc_real_pct": round(r_1967["gdp_pc_growth_annual_pct"], 2),
        "crec_pib_real_pct": round(r_1967["gdp_growth_annual_pct"], 2),
        "tasa_inversion_fija_gfcf_pct": round(r_1967["gfcf_pct_gdp"], 2),
        "tasa_inversion_total_gcf_pct": round(r_1967["gcf_pct_gdp"], 2),
        "icor_anual": round(r_1967["icor_gfcf_annual"], 2),
        "pib_real_usd2015_billones": round(r_1967["gdp_const_2015_usd"] / 1e12, 3),
        "poblacion_millones": round(r_1967["population_total"] / 1e6, 1)
    })
    
    # Latest
    gfcf_latest_val = sub.dropna(subset=["gfcf_pct_gdp"]).iloc[-1]["gfcf_pct_gdp"]
    gcf_latest_val = sub.dropna(subset=["gcf_pct_gdp"]).iloc[-1]["gcf_pct_gdp"]
    summary_rows.append({
        "country": c_name,
        "country_code": c_code,
        "corte_o_periodo": f"Año {latest_yr} (Más reciente)",
        "año_referencia": str(latest_yr),
        "pib_pc_real_usd2015": round(r_latest["gdp_pc_const_2015_usd"], 2),
        "crec_pib_pc_real_pct": round(r_latest["gdp_pc_growth_annual_pct"], 2),
        "crec_pib_real_pct": round(r_latest["gdp_growth_annual_pct"], 2),
        "tasa_inversion_fija_gfcf_pct": round(gfcf_latest_val, 2),
        "tasa_inversion_total_gcf_pct": round(gcf_latest_val, 2),
        "icor_anual": round(gfcf_latest_val / r_latest["gdp_growth_annual_pct"], 2),
        "pib_real_usd2015_billones": round(r_latest["gdp_const_2015_usd"] / 1e12, 3),
        "poblacion_millones": round(r_latest["population_total"] / 1e6, 1)
    })
    
    # Period 1967-2025
    n_years = latest_yr - 1967
    gdp_pc_start = r_1967["gdp_pc_const_2015_usd"]
    gdp_pc_end = r_latest["gdp_pc_const_2015_usd"]
    cagr_pib_pc = ((gdp_pc_end / gdp_pc_start) ** (1 / n_years) - 1) * 100
    
    gdp_start = r_1967["gdp_const_2015_usd"]
    gdp_end = r_latest["gdp_const_2015_usd"]
    cagr_pib = ((gdp_end / gdp_start) ** (1 / n_years) - 1) * 100
    
    mean_gfcf = sub["gfcf_pct_gdp"].mean()
    mean_gcf = sub["gcf_pct_gdp"].mean()
    mean_gdp_growth = sub["gdp_growth_annual_pct"].mean()
    icor_period = mean_gfcf / mean_gdp_growth if mean_gdp_growth > 0 else np.nan
    
    summary_rows.append({
        "country": c_name,
        "country_code": c_code,
        "corte_o_periodo": f"Promedio Período 1967-{latest_yr}",
        "año_referencia": f"1967-{latest_yr}",
        "pib_pc_real_usd2015": None,
        "crec_pib_pc_real_pct": round(cagr_pib_pc, 2),
        "crec_pib_real_pct": round(cagr_pib, 2),
        "tasa_inversion_fija_gfcf_pct": round(mean_gfcf, 2),
        "tasa_inversion_total_gcf_pct": round(mean_gcf, 2),
        "icor_anual": round(icor_period, 2),
        "pib_real_usd2015_billones": None,
        "poblacion_millones": None
    })

df_summary = pd.DataFrame(summary_rows)
summary_path = os.path.join(DATA_PROCESSED, "wdi_macro_summary_1967_latest.csv")
df_summary.to_csv(summary_path, index=False)
print(f"Resumen guardado en: {summary_path}")

# ==========================================
# GENERAR GRÁFICOS SEPARADOS (PNG 300 DPI)
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
colors = {'IND': '#E67E22', 'CHN': '#C0392B'}
labels = {'IND': 'India', 'CHN': 'China'}

# -------------------------------------------------------------------------
# GRÁFICO 1: PIB per Cápita Real - ESCALA NORMAL (LINEAL)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
for c in ['IND', 'CHN']:
    sub = df_1967[df_1967['country_code'] == c]
    ax.plot(sub['year'], sub['gdp_pc_const_2015_usd'], label=labels[c], color=colors[c], linewidth=3)

ax.set_title('Evolución del PIB per cápita Real (Escala Lineal, 1967–2025)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Año', fontsize=11)
ax.set_ylabel('PIB per cápita (US$ constantes de 2015)', fontsize=11)
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=11, loc='upper left')

# Anotaciones finales
ax.annotate(f'China 2025: $13,793\n(59.2x vs 1967)', xy=(2025, 13793), xytext=(2014, 12000),
            arrowprops=dict(facecolor='#C0392B', arrowstyle="->", lw=1.5), fontsize=9.5, fontweight='bold', color='#C0392B')
ax.annotate(f'India 2025: $2,523\n(7.4x vs 1967)', xy=(2025, 2523), xytext=(2014, 4200),
            arrowprops=dict(facecolor='#E67E22', arrowstyle="->", lw=1.5), fontsize=9.5, fontweight='bold', color='#E67E22')

plt.tight_layout()
fig1_path = os.path.join(OUTPUT_FIGS, "01_pib_pc_real_lineal.png")
plt.savefig(fig1_path, bbox_inches='tight')
plt.close()
print(f"Gráfico 1 (Lineal) guardado en: {fig1_path}")

# -------------------------------------------------------------------------
# GRÁFICO 2: PIB per Cápita Real - ESCALA LOGARÍTMICA
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
for c in ['IND', 'CHN']:
    sub = df_1967[df_1967['country_code'] == c]
    ax.plot(sub['year'], sub['gdp_pc_const_2015_usd'], label=labels[c], color=colors[c], linewidth=3)

ax.set_title('Evolución del PIB per cápita Real (Escala Logarítmica: Punto de Partida y Despegue)', fontsize=13, fontweight='bold', pad=12)
ax.set_yscale('log')
ax.set_xlabel('Año', fontsize=11)
ax.set_ylabel('PIB per cápita (US$ constantes 2015, Escala Log)', fontsize=11)
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=11, loc='upper left')

# Hitos y cruce
ax.axvline(1978, color='#C0392B', linestyle=':', alpha=0.8, linewidth=1.5)
ax.text(1979, 450, '1978: Reformas de\nDeng Xiaoping (China)', color='#C0392B', fontsize=9, fontweight='bold')

ax.axvline(1991, color='#E67E22', linestyle=':', alpha=0.8, linewidth=1.5)
ax.text(1992, 1150, '1991: Reformas de\nApertura (India)', color='#E67E22', fontsize=9, fontweight='bold')

ax.annotate('1967: India ($340) > China ($233)', xy=(1967, 280), xytext=(1968, 200),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2), fontsize=9)
ax.annotate('Cruce ~1983-1984', xy=(1984, 520), xytext=(1985, 320),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2), fontsize=9)

plt.tight_layout()
fig2_path = os.path.join(OUTPUT_FIGS, "02_pib_pc_real_log.png")
plt.savefig(fig2_path, bbox_inches='tight')
plt.close()
print(f"Gráfico 2 (Log) guardado en: {fig2_path}")

# -------------------------------------------------------------------------
# GRÁFICO 3: TASAS DE CRECIMIENTO ANUAL DEL PIB REAL Y MEDIA MÓVIL
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), dpi=300, sharex=True)

# Panel 1: Crecimiento Anual Bruto
for c in ['IND', 'CHN']:
    sub = df_1967[df_1967['country_code'] == c]
    ax1.plot(sub['year'], sub['gdp_growth_annual_pct'], label=f"{labels[c]} (Anual)", color=colors[c], alpha=0.45, linewidth=1.5)
    ax1.plot(sub['year'], sub['gdp_growth_5yr_ma'], label=f"{labels[c]} (Media Móvil 5 años)", color=colors[c], linewidth=2.8)

ax1.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)
ax1.set_title('A. Crecimiento del PIB Real Total (% anual)', fontsize=12, fontweight='bold', pad=8)
ax1.set_ylabel('Crecimiento PIB (%)', fontsize=10.5)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5, loc='upper right')

# Panel 2: Crecimiento del PIB per Cápita Real
for c in ['IND', 'CHN']:
    sub = df_1967[df_1967['country_code'] == c]
    ax2.plot(sub['year'], sub['gdp_pc_growth_annual_pct'], label=f"{labels[c]} (Anual)", color=colors[c], alpha=0.45, linewidth=1.5)
    ax2.plot(sub['year'], sub['gdp_pc_growth_5yr_ma'], label=f"{labels[c]} (Media Móvil 5 años)", color=colors[c], linewidth=2.8)

ax2.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)
ax2.set_title('B. Crecimiento del PIB per cápita Real (% anual)', fontsize=12, fontweight='bold', pad=8)
ax2.set_xlabel('Año', fontsize=11)
ax2.set_ylabel('Crecimiento PIB pc (%)', fontsize=10.5)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5, loc='upper right')

plt.tight_layout()
fig3_path = os.path.join(OUTPUT_FIGS, "03_tasas_crecimiento_pib.png")
plt.savefig(fig3_path, bbox_inches='tight')
plt.close()
print(f"Gráfico 3 (Tasas de Crecimiento) guardado en: {fig3_path}")

# -------------------------------------------------------------------------
# GRÁFICO 4: TASA DE INVERSIÓN BRUTA FIJA (FBCF % DEL PIB)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
for c in ['IND', 'CHN']:
    sub = df_1967[df_1967['country_code'] == c].dropna(subset=['gfcf_pct_gdp'])
    ax.plot(sub['year'], sub['gfcf_pct_gdp'], label=labels[c], color=colors[c], linewidth=3)
    mean_val = df_1967[df_1967['country_code'] == c]['gfcf_pct_gdp'].mean()
    ax.axhline(mean_val, color=colors[c], linestyle='--', alpha=0.5, label=f'Promedio {labels[c]} ({mean_val:.1f}%)')

ax.set_title('Tasa de Inversión Fija: Formación Bruta de Capital Fijo (% del PIB, 1967–2025)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Año', fontsize=11)
ax.set_ylabel('FBCF (% del PIB a precios corrientes)', fontsize=11)
ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10, loc='upper left')

ax.annotate('Pico de inversión China: 44.1% (2011)', xy=(2011, 44.1), xytext=(1998, 45.5),
            arrowprops=dict(facecolor='#C0392B', arrowstyle="->", lw=1.5), fontsize=9.5, fontweight='bold', color='#C0392B')
ax.annotate('Pico de inversión India: 35.8% (2007)', xy=(2007, 35.8), xytext=(2005, 23.0),
            arrowprops=dict(facecolor='#E67E22', arrowstyle="->", lw=1.5), fontsize=9.5, fontweight='bold', color='#E67E22')

plt.tight_layout()
fig4_path = os.path.join(OUTPUT_FIGS, "04_tasa_inversion_fbcf.png")
plt.savefig(fig4_path, bbox_inches='tight')
plt.close()
print(f"Gráfico 4 (Inversión FBCF) guardado en: {fig4_path}")

# -------------------------------------------------------------------------
# GRÁFICO 5: ICOR Y EFICIENCIA DEL CAPITAL
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

for c in ['IND', 'CHN']:
    sub = df_1967[df_1967['country_code'] == c].dropna(subset=['icor_gfcf_5yr_smoothed'])
    sub_clean = sub[(sub['icor_gfcf_5yr_smoothed'] > 0) & (sub['icor_gfcf_5yr_smoothed'] < 15)]
    ax1.plot(sub_clean['year'], sub_clean['icor_gfcf_5yr_smoothed'], label=f"{labels[c]} (Suavizado 5a)", color=colors[c], linewidth=2.8)

ax1.set_title('A. Trayectoria del ICOR (Suavizado 5 años)', fontsize=12, fontweight='bold', pad=10)
ax1.set_xlabel('Año', fontsize=11)
ax1.set_ylabel('ICOR = (FBCF % PIB) / (Crecimiento PIB %)', fontsize=11)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

# Panel 2: Comparativa de Métricas de Período
period_df = df_summary[df_summary['corte_o_periodo'].str.contains('Promedio')].copy()
x = np.arange(len(period_df))
width = 0.35

ax2_twin = ax2.twinx()
bars1 = ax2.bar(x - width/2, period_df['crec_pib_real_pct'], width, label='Crecimiento PIB Real CAGR (%)', color='#2ECC71', alpha=0.85)
bars2 = ax2_twin.bar(x + width/2, period_df['tasa_inversion_fija_gfcf_pct'], width, label='Tasa Inversión FBCF Promedio (%)', color='#34495E', alpha=0.85)

ax2.set_title('B. Crecimiento vs. Inversión Promedio (1967–2025)', fontsize=12, fontweight='bold', pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(period_df['country'], fontsize=11, fontweight='bold')
ax2.set_ylabel('Crecimiento Real CAGR (%)', fontsize=11, color='#27AE60')
ax2_twin.set_ylabel('Tasa Inversión FBCF Promedio (%)', fontsize=11, color='#2C3E50')
ax2.grid(True, linestyle='--', alpha=0.6)

for bar in bars1:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f'{yval:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1E8449')

for bar in bars2:
    yval = bar.get_height()
    ax2_twin.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f'{yval:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1C2833')

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)

plt.tight_layout()
fig5_path = os.path.join(OUTPUT_FIGS, "05_icor_eficiencia_capital.png")
plt.savefig(fig5_path, bbox_inches='tight')
plt.close()
print(f"Gráfico 5 (ICOR) guardado en: {fig5_path}")

print("\n¡Todo generado con éxito! USA eliminado de datasets y gráficos.")
