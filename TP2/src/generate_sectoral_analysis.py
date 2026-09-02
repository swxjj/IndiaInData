import urllib.request
import json
import ssl
import os
import pandas as pd
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TP2_DIR = os.path.dirname(SCRIPT_DIR)

DATA_RAW = os.path.join(TP2_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(TP2_DIR, "data", "processed")

os.makedirs(DATA_RAW, exist_ok=True)
os.makedirs(DATA_PROCESSED, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

indicators = {
    "NV.AGR.TOTL.ZS": "va_agro_pct_gdp",
    "NV.IND.TOTL.ZS": "va_ind_pct_gdp",
    "NV.SRV.TOTL.ZS": "va_serv_pct_gdp",
    "SL.AGR.EMPL.ZS": "emp_agro_pct",
    "SL.IND.EMPL.ZS": "emp_ind_pct",
    "SL.SRV.EMPL.ZS": "emp_serv_pct"
}

countries = ["IND", "CHN"]
all_records = []

print("Descargando indicadores sectoriales de Valor Agregado y Empleo (Banco Mundial)...")
for c in countries:
    for ind_code, col_name in indicators.items():
        url = f"http://api.worldbank.org/v2/country/{c}/indicator/{ind_code}?format=json&per_page=1000"
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    if len(data) > 1 and data[1]:
                        for rec in data[1]:
                            if rec['value'] is not None:
                                all_records.append({
                                    "country_code": rec['countryiso3code'],
                                    "country_name": "India" if rec['countryiso3code'] == "IND" else "China",
                                    "year": int(rec['date']),
                                    "indicator": col_name,
                                    "value": rec['value']
                                })
                break
            except Exception as e:
                time.sleep(1)

df_raw = pd.DataFrame(all_records)
df_pivot = df_raw.pivot(index=["country_code", "country_name", "year"], columns="indicator", values="value").reset_index()
df_pivot = df_pivot.sort_values(["country_code", "year"]).reset_index(drop=True)

# Asignar década
def get_decade(year):
    dec_start = (year // 10) * 10
    return f"{dec_start}s"

df_pivot["decade"] = df_pivot["year"].apply(get_decade)

# Normalización sobre el Valor Agregado Bruto Total (VAB / GVA)
df_pivot["va_total_gva_pct_gdp"] = df_pivot["va_agro_pct_gdp"] + df_pivot["va_ind_pct_gdp"] + df_pivot["va_serv_pct_gdp"]
df_pivot["net_taxes_pct_gdp"] = 100.0 - df_pivot["va_total_gva_pct_gdp"]

df_pivot["va_agro_pct_gva"] = (df_pivot["va_agro_pct_gdp"] / df_pivot["va_total_gva_pct_gdp"]) * 100.0
df_pivot["va_ind_pct_gva"] = (df_pivot["va_ind_pct_gdp"] / df_pivot["va_total_gva_pct_gdp"]) * 100.0
df_pivot["va_serv_pct_gva"] = (df_pivot["va_serv_pct_gdp"] / df_pivot["va_total_gva_pct_gdp"]) * 100.0

# Reordenar columnas estructuradas
cols_order = [
    "country_code", "country_name", "year", "decade",
    # Normalizadas sobre el VAB (Suman 100%)
    "va_agro_pct_gva", "va_ind_pct_gva", "va_serv_pct_gva",
    # Empleo sectorial (Suman 100%)
    "emp_agro_pct", "emp_ind_pct", "emp_serv_pct",
    # Series crudas del Banco Mundial (% del PIB a precios de mercado)
    "va_agro_pct_gdp", "va_ind_pct_gdp", "va_serv_pct_gdp",
    "va_total_gva_pct_gdp", "net_taxes_pct_gdp"
]
df_pivot = df_pivot[cols_order]

# 1. Guardar Serie Anual Sectorial
annual_sectoral_path = os.path.join(DATA_PROCESSED, "sectoral_structure_annual.csv")
df_pivot.to_csv(annual_sectoral_path, index=False)
print(f"Guardado dataset anual sectorial: {annual_sectoral_path}")

# 2. Tabla de Promedios por Década
cols_to_avg = [
    "va_agro_pct_gva", "va_ind_pct_gva", "va_serv_pct_gva",
    "emp_agro_pct", "emp_ind_pct", "emp_serv_pct",
    "va_agro_pct_gdp", "va_ind_pct_gdp", "va_serv_pct_gdp"
]
df_decade_avg = df_pivot.groupby(["country_name", "country_code", "decade"])[cols_to_avg].mean().reset_index()
df_decade_avg = df_decade_avg.round(2)
decade_avg_path = os.path.join(DATA_PROCESSED, "sectoral_structure_decade_averages.csv")
df_decade_avg.to_csv(decade_avg_path, index=False)
print(f"Guardado promedios por década: {decade_avg_path}")

# 3. Tabla de Puntos de Corte Puntuales (Años terminados en 5: 1965, 1975, 1985, 1995, 2005, 2015, y 2024 más reciente)
benchmark_years = [1965, 1975, 1985, 1995, 2005, 2015, 2024]
df_benchmarks = df_pivot[df_pivot["year"].isin(benchmark_years)].copy()
df_benchmarks = df_benchmarks.round(2)
benchmarks_path = os.path.join(DATA_PROCESSED, "sectoral_structure_benchmarks_ending_in_5.csv")
df_benchmarks.to_csv(benchmarks_path, index=False)
print(f"Guardado cortes puntuales por década: {benchmarks_path}")

print("Procesamiento sectorial con normalización sobre VAB completado con éxito.")
