import os
import json
import csv
import urllib.request
import urllib.error

# Indicadores solicitados en la consigna TP3
INDICATORS = {
    # --- Parte 1: Big Push e Inversion ---
    "NY.GDP.PCAP.KD.ZG": "gdp_pcap_growth_annual_pct",         # Tasa de crecimiento del PBI per cápita
    "NE.GDI.TOTL.ZS":    "gross_capital_formation_pct_gdp",     # Inversión bruta (% del PIB)
    "NE.GDI.FTOT.ZS":    "gross_fixed_capital_formation_pct_gdp",# Inversión fija bruta (% del PIB)
    "BX.KLT.DINV.WD.GD.ZS": "fdi_net_inflows_pct_gdp",          # IED neta (% del PIB)
    
    # --- Parte 1: Variables de Infraestructura y Complementariedad ---
    "EG.ELC.ACCS.ZS":    "access_electricity_pct_pop",          # Acceso a electricidad (% población)
    "SH.H2O.BASW.ZS":    "basic_drinking_water_pct_pop",        # Agua potable básica (% población)
    "IT.NET.USER.ZS":    "internet_users_pct_pop",              # Usuarios de Internet (% población)
    "IT.CEL.SETS.P2":    "mobile_subscriptions_per_100",        # Telefonía celular (por 100 hab)
    "IT.NET.BBND.P2":    "broadband_subscriptions_per_100",     # Banda ancha fija (por 100 hab)
    
    # --- Parte 2: Crecimiento Equilibrado vs Desequilibrado ---
    "NV.AGR.TOTL.KD.ZG": "agriculture_va_growth_pct",           # VA Agricultura (% crec. anual)
    "NV.IND.TOTL.KD.ZG": "industry_va_growth_pct",              # VA Industria (% crec. anual)
    "NV.SRV.TOTL.KD.ZG": "services_va_growth_pct",              # VA Servicios (% crec. anual)
}

COUNTRIES = ["ARG", "IND"]

def fetch_indicator(indicator_code, countries):
    country_str = ";".join(countries)
    url = f"https://api.worldbank.org/v2/country/{country_str}/indicator/{indicator_code}?format=json&per_page=3000"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            records = []
            if len(data) > 1 and data[1]:
                for row in data[1]:
                    if row.get('value') is not None:
                        records.append({
                            'country_iso': row['countryiso3code'],
                            'country_name': row['country']['value'],
                            'year': int(row['date']),
                            'indicator_id': indicator_code,
                            'indicator_name': INDICATORS.get(indicator_code, indicator_code),
                            'value': float(row['value'])
                        })
            return sorted(records, key=lambda x: (x['country_iso'], x['year']))
    except Exception as e:
        print(f"Error descargando {indicator_code}: {e}")
        return []

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    print("=" * 80)
    print(" INICIANDO DESCARGA WORLD DEVELOPMENT INDICATORS (WORLD BANK API)")
    print(f" Paises objetivo: {', '.join(COUNTRIES)}")
    print(f" Indicadores seleccionados: {len(INDICATORS)}")
    print("=" * 80)
    
    all_records = []
    
    for code, var_name in INDICATORS.items():
        print(f"-> Descargando {code:<25} ({var_name})...", end=" ", flush=True)
        records = fetch_indicator(code, COUNTRIES)
        print(f"OK: {len(records)} registros")
        
        # Guardar archivo raw individual
        raw_path = os.path.join(raw_dir, f"wb_{var_name}.csv")
        with open(raw_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=['country_iso', 'country_name', 'year', 'indicator_id', 'indicator_name', 'value'])
            writer.writeheader()
            writer.writerows(records)
            
        all_records.extend(records)
        
    # Guardar archivo consolidado de todas las series WB crudas
    combined_path = os.path.join(raw_dir, "world_bank_all_indicators_raw.csv")
    with open(combined_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=['country_iso', 'country_name', 'year', 'indicator_id', 'indicator_name', 'value'])
        writer.writeheader()
        writer.writerows(all_records)
        
    print("\n" + "=" * 80)
    print(" RESUMEN ACADEMICO DE OBSERVACIONES DESCARGADAS (WORLD BANK)")
    print("=" * 80)
    print(f"{'Pais':<6} {'Variable':<35} {'Periodo':<12} {'Obs':<6} {'Min':<10} {'Max':<10} {'Reciente':<10}")
    print("-" * 80)
    
    for iso in COUNTRIES:
        for code, var_name in INDICATORS.items():
            sub = [r for r in all_records if r['country_iso'] == iso and r['indicator_id'] == code]
            if sub:
                sub = sorted(sub, key=lambda x: x['year'])
                vals = [r['value'] for r in sub]
                period = f"{sub[0]['year']}-{sub[-1]['year']}"
                obs = len(sub)
                min_v = f"{min(vals):.2f}"
                max_v = f"{max(vals):.2f}"
                recent = f"{vals[-1]:.2f} ({sub[-1]['year']})"
                print(f"{iso:<6} {var_name:<35} {period:<12} {obs:<6} {min_v:<10} {max_v:<10} {recent:<10}")
            else:
                print(f"{iso:<6} {var_name:<35} {'Sin datos':<12} {'0':<6}")
    print("=" * 80)
    print(f"Descargas finalizadas con exito en: {raw_dir}")

if __name__ == "__main__":
    main()
