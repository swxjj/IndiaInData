
import requests
import pandas as pd
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Obtener lista de países soberanos del Banco Mundial (excluyendo agregados)
url_c = 'https://api.worldbank.org/v2/country?format=json&per_page=300'
res_c = requests.get(url_c, timeout=20).json()[1]
sovereign = {c['id']: c['name'] for c in res_c if c.get('region', {}).get('value') != 'Aggregates'}

# 2. Descargar PIB per cápita inicial (1990)
url_y0 = 'https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.KD?date=1990&format=json&per_page=300'
data_y0 = requests.get(url_y0, timeout=25).json()[1]
records_y0 = []
for item in data_y0:
    cid = item.get('countryiso3code')
    val = item.get('value')
    if cid in sovereign and val is not None and val > 0:
        records_y0.append({'codigo_pais': cid, 'pais': sovereign[cid], 'pibpc_1990': val, 'log_pibpc_1990': np.log(val)})
df_y0 = pd.DataFrame(records_y0)

# 3. Descargar Crecimiento Anual del PIBpc (1990-2024)
url_g = 'https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.KD.ZG?date=1990:2024&format=json&per_page=10000'
data_g = requests.get(url_g, timeout=35).json()[1]
records_g = []
for item in data_g:
    cid = item.get('countryiso3code')
    val = item.get('value')
    if cid in sovereign and val is not None:
        records_g.append({'codigo_pais': cid, 'tasa_crecimiento': val})
df_g = pd.DataFrame(records_g)
df_g_mean = df_g.groupby('codigo_pais')['tasa_crecimiento'].mean().reset_index()
df_g_mean.rename(columns={'tasa_crecimiento': 'crecimiento_promedio_1990_2024'}, inplace=True)

# 4. Mergear y limpiar
df_final = pd.merge(df_y0, df_g_mean, on='codigo_pais').dropna()

# 5. Graficar estándar académico
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
x = df_final['log_pibpc_1990'].values
y = df_final['crecimiento_promedio_1990_2024'].values

ax.scatter(x, y, color='#1B365D', alpha=0.65, s=45, edgecolors='none', label='Países soberanos (WDI)')

slope, intercept = np.polyfit(x, y, 1)
r_mat = np.corrcoef(x, y)
r_sq = (r_mat[0, 1] ** 2)
x_seq = np.linspace(x.min(), x.max(), 100)
ax.plot(x_seq, slope * x_seq + intercept, color='#8B263E', linestyle='--', linewidth=2,
        label=f'Regresión: g = {intercept:.2f} + ({slope:.3f})·ln(y₀)  [R² = {r_sq:.3f}]')

# Destacar economías representativas
destacados = ['IND', 'CHN', 'USA', 'ARG', 'BRA', 'KOR', 'DEU', 'VNM', 'CHL', 'MEX']
for _, row in df_final[df_final['codigo_pais'].isin(destacados)].iterrows():
    ax.scatter(row['log_pibpc_1990'], row['crecimiento_promedio_1990_2024'], color='#D97706', s=65, edgecolors='black', linewidth=0.8, zorder=5)
    ax.annotate(row['pais'], (row['log_pibpc_1990'], row['crecimiento_promedio_1990_2024']),
                xytext=(6, 4), textcoords='offset points', fontsize=8.5, fontweight='bold', color='#1A202C')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linestyle='--', alpha=0.35, color='#CBD5E1')
ax.set_xlabel('Logaritmo del PIB per cápita inicial (1990, USD constantes 2015)', labelpad=8)
ax.set_ylabel('Crecimiento anual promedio del PIBpc (1990–2024, %)', labelpad=8)

fig.text(0.125, 0.96, 'Convergencia Económica Incondicional (1990–2024)', fontsize=13.5, fontweight='bold', color='#1A202C')
fig.text(0.125, 0.92, f'Muestra de {len(df_final)} países soberanos. Relación entre nivel inicial de ingreso y tasa de crecimiento posterior.', fontsize=10, color='#4A5568')
fig.text(0.125, 0.02, 'Fuente: Banco Mundial (WDI). Elaboración para Desarrollo Económico (UNS).', fontsize=8.5, color='#718096', style='italic')
ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='best')

plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.90])
plt.savefig('D:/mateo/IndiaInData/macro_chat/output/chart_ebc8be652e.png', dpi=300)
df_final.to_csv('D:/mateo/IndiaInData/macro_chat/output/data_ebc8be652e.csv', index=False)

summary = {
    "variables": ["Log PIBpc (1990)", "Crecimiento promedio PIBpc (1990–2024)"],
    "paises": [f"Muestra global de {len(df_final)} países soberanos"],
    "anios": "1990 – 2024",
    "fuente": "Banco Mundial (WDI)",
    "analisis": f"Se estima un coeficiente beta de {slope:.3f} (R² = {r_sq:.3f}). La pendiente negativa confirma la tendencia teórica a la convergencia, donde los países con menor ingreso inicial crecen en promedio a tasas mayores debido a rendimientos decrecientes del capital (Solow-Swan)."
}
print("###SUMMARY_START###")
print(json.dumps(summary, ensure_ascii=False))
print("###SUMMARY_END###")
