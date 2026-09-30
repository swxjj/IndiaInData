"""
=============================================================================
IndiaInData - Trabajo Práctico 5: Medio Ambiente, Instituciones y Desarrollo
Script de descarga y procesamiento de datos oficiales
=============================================================================
Fuentes:
1. Banco Mundial - Worldwide Governance Indicators (WGI)
   - Voice and Accountability (VA.EST)
   - Political Stability and Absence of Violence (PV.EST)
   - Government Effectiveness (GE.EST)
   - Regulatory Quality (RQ.EST)
   - Rule of Law (RL.EST)
   - Control of Corruption (CC.EST)
2. Banco Mundial - World Development Indicators (WDI)
   - PIB per cápita PPA cte 2021 USD (NY.GDP.PCAP.PP.KD)
   - PIB per cápita cte 2015 USD (NY.GDP.PCAP.KD)
   - Inversión / FBCF % PIB (NE.GDI.FTOT.ZS)
   - Formación Bruta de Capital Total % PIB (NE.GDI.TOTL.ZS)
   - Gasto público en educación % PIB (SE.XPD.TOTL.GD.ZS)
3. Global Footprint Network - National Footprint and Biocapacity Accounts
   - Huella Ecológica per cápita (gha/persona) y componentes
   - Biocapacidad per cápita (gha/persona) y componentes
   - Déficit / Superávit ecológico (gha/persona)
=============================================================================
"""

import os
import json
import urllib.request
import numpy as np
import pandas as pd

def fetch_json(url, headers=None, timeout=20):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))

def download_wgi_india():
    """Descarga los 6 indicadores WGI en versión estimate para India."""
    indicators = {
        'GOV_WGI_VA.EST': 'voice_accountability',
        'GOV_WGI_PV.EST': 'political_stability',
        'GOV_WGI_GE.EST': 'government_effectiveness',
        'GOV_WGI_RQ.EST': 'regulatory_quality',
        'GOV_WGI_RL.EST': 'rule_of_law',
        'GOV_WGI_CC.EST': 'control_of_corruption'
    }
    records = []
    print("Descargando World Governance Indicators (WGI)...")
    for ind_id, ind_name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/IND/indicator/{ind_id}?format=json&per_page=100"
        data = fetch_json(url)
        if len(data) > 1 and data[1]:
            for row in data[1]:
                if row.get('value') is not None:
                    records.append({
                        'country_iso': 'IND',
                        'country_name': 'India',
                        'year': int(row['date']),
                        'indicator_id': ind_id,
                        'indicator_name': ind_name,
                        'value': float(row['value'])
                    })
    return pd.DataFrame(records)

def download_wdi_india():
    """Descarga variables macroeconómicas de control y PIB pc para India."""
    indicators = {
        'NY.GDP.PCAP.PP.KD': 'pib_pc_ppp_cte2021',
        'NY.GDP.PCAP.KD': 'pib_pc_cte2015_usd',
        'NE.GDI.FTOT.ZS': 'inversion_fbcf_pct_pib',
        'NE.GDI.TOTL.ZS': 'inversion_total_pct_pib',
        'SE.XPD.TOTL.GD.ZS': 'gasto_educacion_pct_pib',
        'BX.KLT.DINV.WD.GD.ZS': 'apertura_fin_ied_in_pct_pib',
        'BM.KLT.DINV.WD.GD.ZS': 'apertura_fin_ied_out_pct_pib',
        'NE.TRD.GNFS.ZS': 'apertura_comercial_pct_pib'
    }
    records = []
    print("Descargando World Development Indicators (WDI)...")
    for ind_id, ind_name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/IND/indicator/{ind_id}?format=json&per_page=100"
        try:
            data = fetch_json(url)
            if len(data) > 1 and data[1]:
                for row in data[1]:
                    if row.get('value') is not None:
                        records.append({
                            'country_iso': 'IND',
                            'country_name': 'India',
                            'year': int(row['date']),
                            'indicator_id': ind_id,
                            'indicator_name': ind_name,
                            'value': float(row['value'])
                        })
        except Exception as e:
            print(f"Error descargando {ind_id}: {e}")
    return pd.DataFrame(records)

def download_footprint_india():
    """Descarga series de Huella Ecológica y Biocapacidad de Global Footprint Network."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Origin': 'https://data.footprintnetwork.org',
        'Referer': 'https://data.footprintnetwork.org/',
        'Accept': 'application/json, text/plain, */*'
    }
    print("Descargando datos de Global Footprint Network (India)...")
    url_pc = "https://api.footprintnetwork.org/v1/data/100/all/BCpc,EFCpc"
    data_pc = fetch_json(url_pc, headers=headers)
    
    records = []
    for item in data_pc:
        records.append({
            'country_iso': 'IND',
            'country_name': 'India',
            'year': int(item['year']),
            'record_type': item.get('record'),
            'crop_land': item.get('cropLand'),
            'grazing_land': item.get('grazingLand'),
            'forest_land': item.get('forestLand'),
            'fishing_ground': item.get('fishingGround'),
            'builtup_land': item.get('builtupLand'),
            'carbon': item.get('carbon'),
            'total_gha_per_person': item.get('value')
        })
    return pd.DataFrame(records)

def save_styled_excel(df, file_path, sheet_name="Datos"):
    """Guarda un DataFrame en Excel con formato académico y anchos automáticos."""
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        
        # Ajustar ancho de columnas
        for col in worksheet.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                val = str(cell.value or '')
                max_len = max(max_len, len(val))
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    proc_dir = os.path.join(base_dir, "data", "processed")
    out_dir = os.path.join(base_dir, "output")
    fig_dir = os.path.join(out_dir, "figures")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # 1. DESCARGA Y GUARDADO RAW
    # -------------------------------------------------------------------------
    df_wgi_raw = download_wgi_india()
    df_wdi_raw = download_wdi_india()
    df_footprint_raw = download_footprint_india()
    
    df_wgi_raw.to_csv(os.path.join(raw_dir, "wgi_india_raw.csv"), index=False, encoding="utf-8")
    df_wdi_raw.to_csv(os.path.join(raw_dir, "wdi_india_raw.csv"), index=False, encoding="utf-8")
    df_footprint_raw.to_csv(os.path.join(raw_dir, "footprint_india_raw.csv"), index=False, encoding="utf-8")
    print("-> Datos crudos guardados en data/raw/")
    
    # -------------------------------------------------------------------------
    # 2. PROCESAMIENTO PARTE 1: INSTITUCIONES Y DESARROLLO
    # -------------------------------------------------------------------------
    # Pivotear WGI
    wgi_pivot = df_wgi_raw.pivot(index='year', columns='indicator_name', values='value').reset_index()
    
    # Pivotear WDI
    wdi_pivot = df_wdi_raw.pivot(index='year', columns='indicator_name', values='value').reset_index()
    
    # Unir WGI y WDI
    df_inst = pd.merge(wgi_pivot, wdi_pivot, on='year', how='inner').sort_values('year').reset_index(drop=True)
    
    # Crear variables analíticas
    df_inst['ln_pib_pc_ppp'] = np.log(df_inst['pib_pc_ppp_cte2021'])
    df_inst['ln_pib_pc_cte2015'] = np.log(df_inst['pib_pc_cte2015_usd'])
    
    # Promedio simple de gobernabilidad WGI (6 dimensiones)
    wgi_cols = [
        'voice_accountability', 'political_stability', 'government_effectiveness',
        'regulatory_quality', 'rule_of_law', 'control_of_corruption'
    ]
    df_inst['wgi_promedio'] = df_inst[wgi_cols].mean(axis=1)
    
    # Variables de apertura económica y financiera
    if 'apertura_fin_ied_in_pct_pib' in df_inst.columns and 'apertura_fin_ied_out_pct_pib' in df_inst.columns:
        df_inst['apertura_fin_ied_tot_pct_pib'] = df_inst['apertura_fin_ied_in_pct_pib'] + df_inst['apertura_fin_ied_out_pct_pib']
    
    # Gasto en educación interpolado (para evitar pérdida de observaciones en econometría)
    if 'gasto_educacion_pct_pib' in df_inst.columns:
        df_inst['gasto_educacion_interp_pct_pib'] = (
            df_inst['gasto_educacion_pct_pib']
            .interpolate(method='linear')
            .bfill()
            .ffill()
        )
    
    # Reordenar columnas de forma clara
    col_order = [
        'year', 'pib_pc_ppp_cte2021', 'ln_pib_pc_ppp', 'pib_pc_cte2015_usd', 'ln_pib_pc_cte2015',
        'voice_accountability', 'political_stability', 'government_effectiveness',
        'regulatory_quality', 'rule_of_law', 'control_of_corruption', 'wgi_promedio',
        'inversion_fbcf_pct_pib', 'inversion_total_pct_pib',
        'gasto_educacion_pct_pib', 'gasto_educacion_interp_pct_pib',
        'apertura_fin_ied_in_pct_pib', 'apertura_fin_ied_out_pct_pib', 'apertura_fin_ied_tot_pct_pib',
        'apertura_comercial_pct_pib'
    ]
    df_inst = df_inst[[c for c in col_order if c in df_inst.columns]]
    
    # Guardar Parte 1
    inst_csv_proc = os.path.join(proc_dir, "tp5_india_instituciones_desarrollo.csv")
    inst_xlsx_proc = os.path.join(proc_dir, "tp5_india_instituciones_desarrollo.xlsx")
    inst_xlsx_out = os.path.join(out_dir, "tp5_india_instituciones_desarrollo.xlsx")
    
    df_inst.to_csv(inst_csv_proc, index=False, encoding="utf-8")
    save_styled_excel(df_inst, inst_xlsx_proc, sheet_name="Instituciones_Desarrollo")
    save_styled_excel(df_inst, inst_xlsx_out, sheet_name="Instituciones_Desarrollo")
    print(f"-> Panel de Instituciones guardado: {df_inst.shape[0]} años ({df_inst['year'].min()}-{df_inst['year'].max()})")
    
    # -------------------------------------------------------------------------
    # 3. PROCESAMIENTO PARTE 2: MEDIO AMBIENTE (FOOTPRINT NETWORK)
    # -------------------------------------------------------------------------
    df_ef = df_footprint_raw[df_footprint_raw['record_type'] == 'EFConsPerCap'].copy()
    df_bc = df_footprint_raw[df_footprint_raw['record_type'] == 'BiocapPerCap'].copy()
    
    rename_ef = {
        'total_gha_per_person': 'huella_ecologica_total_gha_pc',
        'carbon': 'huella_carbono_gha_pc',
        'crop_land': 'huella_cultivos_gha_pc',
        'grazing_land': 'huella_pastoreo_gha_pc',
        'forest_land': 'huella_bosques_gha_pc',
        'fishing_ground': 'huella_pesca_gha_pc',
        'builtup_land': 'huella_urbana_gha_pc'
    }
    rename_bc = {
        'total_gha_per_person': 'biocapacidad_total_gha_pc',
        'crop_land': 'biocapacidad_cultivos_gha_pc',
        'grazing_land': 'biocapacidad_pastoreo_gha_pc',
        'forest_land': 'biocapacidad_bosques_gha_pc',
        'fishing_ground': 'biocapacidad_pesca_gha_pc',
        'builtup_land': 'biocapacidad_urbana_gha_pc'
    }
    
    df_ef = df_ef.rename(columns=rename_ef)[['year'] + list(rename_ef.values())]
    df_bc = df_bc.rename(columns=rename_bc)[['year'] + list(rename_bc.values())]
    
    df_env = pd.merge(df_ef, df_bc, on='year', how='inner').sort_values('year').reset_index(drop=True)
    
    # Balance ecológico: Biocapacidad - Huella (si es negativo, hay déficit)
    df_env['balance_ecologico_gha_pc'] = df_env['biocapacidad_total_gha_pc'] - df_env['huella_ecologica_total_gha_pc']
    df_env['condicion_ecologica'] = df_env['balance_ecologico_gha_pc'].apply(lambda x: 'Déficit' if x < 0 else 'Superávit')
    df_env['ratio_huella_biocapacidad'] = df_env['huella_ecologica_total_gha_pc'] / df_env['biocapacidad_total_gha_pc']
    
    # Guardar Parte 2
    env_csv_proc = os.path.join(proc_dir, "tp5_india_medio_ambiente.csv")
    env_xlsx_proc = os.path.join(proc_dir, "tp5_india_medio_ambiente.xlsx")
    env_xlsx_out = os.path.join(out_dir, "tp5_india_medio_ambiente.xlsx")
    
    df_env.to_csv(env_csv_proc, index=False, encoding="utf-8")
    save_styled_excel(df_env, env_xlsx_proc, sheet_name="Medio_Ambiente")
    save_styled_excel(df_env, env_xlsx_out, sheet_name="Medio_Ambiente")
    print(f"-> Panel de Medio Ambiente guardado: {df_env.shape[0]} años ({df_env['year'].min()}-{df_env['year'].max()})")
    
    # -------------------------------------------------------------------------
    # 4. DATASET MAESTRO COMBINADO (1961 - 2025)
    # -------------------------------------------------------------------------
    df_master = pd.merge(df_env, df_inst, on='year', how='left').sort_values('year').reset_index(drop=True)
    master_csv = os.path.join(proc_dir, "tp5_india_dataset_completo.csv")
    master_xlsx = os.path.join(proc_dir, "tp5_india_dataset_completo.xlsx")
    master_out_xlsx = os.path.join(out_dir, "tp5_india_dataset_completo.xlsx")
    
    df_master.to_csv(master_csv, index=False, encoding="utf-8")
    save_styled_excel(df_master, master_xlsx, sheet_name="India_TP5_Completo")
    save_styled_excel(df_master, master_out_xlsx, sheet_name="India_TP5_Completo")
    print(f"-> Dataset maestro completo guardado: {df_master.shape[0]} años ({df_master['year'].min()}-{df_master['year'].max()})")
    print("\nProceso de ingesta y homogeneización finalizado exitosamente.")

if __name__ == "__main__":
    main()
