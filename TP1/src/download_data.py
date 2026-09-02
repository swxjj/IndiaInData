import os
import json
import urllib.request
import csv

def fetch_url(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8')

def fetch_world_bank(indicator, countries=["IND", "USA"]):
    countries_str = ";".join(countries)
    url = f"https://api.worldbank.org/v2/country/{countries_str}/indicator/{indicator}?format=json&per_page=2000"
    print(f"Descargando Banco Mundial ({indicator})...")
    raw_text = fetch_url(url)
    data = json.loads(raw_text)
    
    records = []
    if len(data) > 1 and data[1]:
        for item in data[1]:
            if item.get('value') is not None:
                records.append({
                    'country_iso': item['countryiso3code'],
                    'country_name': item['country']['value'],
                    'year': int(item['date']),
                    'indicator_id': indicator,
                    'value': float(item['value'])
                })
    return sorted(records, key=lambda x: (x['country_iso'], x['year']))

def run_pipeline():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tp1_dir = os.path.dirname(script_dir)
    data_raw = os.path.join(tp1_dir, "data", "raw")
    data_processed = os.path.join(tp1_dir, "data", "processed")
    
    os.makedirs(data_raw, exist_ok=True)
    os.makedirs(data_processed, exist_ok=True)
    
    # ==========================================
    # 1. GDP Per Capita (Constant 2015 USD & PPP)
    # ==========================================
    wb_gdp_const = fetch_world_bank("NY.GDP.PCAP.KD", ["IND", "USA"])
    wb_gdp_ppp = fetch_world_bank("NY.GDP.PCAP.PP.KD", ["IND", "USA"])
    
    # Save raw WB data
    with open("data/raw/gdp_per_capita_constant_2015_usd_worldbank.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=['country_iso', 'country_name', 'year', 'indicator_id', 'value'])
        writer.writeheader()
        writer.writerows(wb_gdp_const)
        
    with open("data/raw/gdp_per_capita_ppp_constant_2021_worldbank.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=['country_iso', 'country_name', 'year', 'indicator_id', 'value'])
        writer.writeheader()
        writer.writerows(wb_gdp_ppp)

    # ==========================================
    # 2. Human Development Index (HDI - UNDP)
    # ==========================================
    print("Descargando Human Development Index (UNDP / OWID)...")
    hdi_csv_text = fetch_url("https://ourworldindata.org/grapher/human-development-index.csv")
    with open("data/raw/hdi_undp_raw.csv", "w", encoding="utf-8") as f:
        f.write(hdi_csv_text)
        
    hdi_reader = csv.DictReader(hdi_csv_text.splitlines())
    hdi_records = []
    for row in hdi_reader:
        iso = row.get('Code', '').strip()
        if iso in ['IND', 'USA']:
            val_str = row.get('Human Development Index', '').strip()
            if val_str:
                hdi_records.append({
                    'country_iso': iso,
                    'country_name': row['Entity'],
                    'year': int(row['Year']),
                    'hdi': float(val_str)
                })

    # ==========================================
    # 3. Cantril Ladder Index (Gallup / WHR)
    # ==========================================
    print("Descargando Cantril Ladder Index / Satisfacción de Vida (Gallup / World Happiness Report)...")
    ladder_csv_text = fetch_url("https://ourworldindata.org/grapher/happiness-cantril-ladder.csv")
    with open("data/raw/cantril_ladder_whr_raw.csv", "w", encoding="utf-8") as f:
        f.write(ladder_csv_text)
        
    ladder_reader = csv.DictReader(ladder_csv_text.splitlines())
    ladder_records = []
    for row in ladder_reader:
        iso = row.get('Code', '').strip()
        if iso in ['IND', 'USA']:
            # Column name is 'Self-reported life satisfaction' or Cantril ladder
            val_str = row.get('Self-reported life satisfaction', '').strip()
            if not val_str:
                # search for any value column
                for k, v in row.items():
                    if k not in ['Entity', 'Code', 'Year'] and v.strip():
                        val_str = v.strip()
                        break
            if val_str:
                ladder_records.append({
                    'country_iso': iso,
                    'country_name': row['Entity'],
                    'year': int(row['Year']),
                    'ladder_score': float(val_str)
                })

    # ==========================================
    # 4. Consolidación de Panel de Datos
    # ==========================================
    # Mapping dict
    panel = {}
    for iso, name in [('IND', 'India'), ('USA', 'United States')]:
        for yr in range(1960, 2026):
            panel[(iso, yr)] = {
                'country_iso': iso,
                'country_name': name,
                'year': yr,
                'gdp_pcap_constant_2015_usd': None,
                'gdp_pcap_ppp_constant_2021': None,
                'hdi': None,
                'cantril_ladder': None
            }
            
    for item in wb_gdp_const:
        key = (item['country_iso'], item['year'])
        if key in panel:
            panel[key]['gdp_pcap_constant_2015_usd'] = item['value']

    for item in wb_gdp_ppp:
        key = (item['country_iso'], item['year'])
        if key in panel:
            panel[key]['gdp_pcap_ppp_constant_2021'] = item['value']
            
    for item in hdi_records:
        key = (item['country_iso'], item['year'])
        if key in panel:
            panel[key]['hdi'] = item['hdi']
            
    for item in ladder_records:
        key = (item['country_iso'], item['year'])
        if key in panel:
            panel[key]['cantril_ladder'] = item['ladder_score']
            
    filtered_panel = [v for k, v in sorted(panel.items()) if any(v[col] is not None for col in ['gdp_pcap_constant_2015_usd', 'gdp_pcap_ppp_constant_2021', 'hdi', 'cantril_ladder'])]
    
    # Save panel CSV
    panel_file = "data/processed/macro_panel_india_usa.csv"
    fieldnames = ['country_iso', 'country_name', 'year', 'gdp_pcap_constant_2015_usd', 'gdp_pcap_ppp_constant_2021', 'hdi', 'cantril_ladder']
    with open(panel_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_panel)
        
    # Save separate country files
    for iso, filename in [('IND', 'data/processed/india_macro.csv'), ('USA', 'data/processed/usa_macro.csv')]:
        c_rows = [r for r in filtered_panel if r['country_iso'] == iso]
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(c_rows)
            
    print(f"\nProceso finalizado. Panel guardado en {panel_file}")
    
    # Print formatted summary table
    print("\n" + "="*80)
    print(f"{'País':<8} {'Variable':<28} {'Período':<14} {'Obs':<6} {'Inicial (Año)':<18} {'Reciente (Año)':<18}")
    print("="*80)
    
    for iso in ['IND', 'USA']:
        c_rows = [r for r in filtered_panel if r['country_iso'] == iso]
        for var, var_label in [
            ('gdp_pcap_constant_2015_usd', 'PIB pc const 2015 USD'),
            ('gdp_pcap_ppp_constant_2021', 'PIB pc PPA const 2021 $'),
            ('hdi', 'IDH (HDI)'),
            ('cantril_ladder', 'Cantril Ladder Index')
        ]:
            valid = [(r['year'], r[var]) for r in c_rows if r[var] is not None]
            if valid:
                period = f"{valid[0][0]}-{valid[-1][0]}"
                obs = str(len(valid))
                init_val = f"{valid[0][1]:,.2f} ({valid[0][0]})"
                rec_val = f"{valid[-1][1]:,.2f} ({valid[-1][0]})"
                print(f"{iso:<8} {var_label:<28} {period:<14} {obs:<6} {init_val:<18} {rec_val:<18}")
    print("="*80)

if __name__ == "__main__":
    run_pipeline()
