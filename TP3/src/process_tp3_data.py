import os
import pandas as pd
import numpy as np

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    proc_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    
    print("=" * 80)
    print(" PROCESAMIENTO Y ARMONIZACION DE DATOS - TP3 DESARROLLO ECONOMICO")
    print("=" * 80)
    
    # 1. Cargar datos del World Bank
    wb_file = os.path.join(raw_dir, "world_bank_all_indicators_raw.csv")
    df_wb = pd.read_csv(wb_file)
    
    # Pivotear World Bank para tener columnas por indicador
    df_wb_pivot = df_wb.pivot_table(
        index=['country_iso', 'country_name', 'year'],
        columns='indicator_name',
        values='value'
    ).reset_index()
    
    # 2. Cargar indicadores clave de EconStats para Argentina
    es_arg_file = os.path.join(raw_dir, "econstats_argentina_all.csv")
    df_es = pd.read_csv(es_arg_file)
    
    # Seleccionar series de infraestructura complementarias de EconStats
    econstats_vars = {
        'EG.USE.ELEC.KH.PC': 'es_electric_power_consumption_kwh_pc',
        'EG.EGY.PROD.KT.OE': 'es_energy_production_kt_oil_eq',
        'IT.MLT.MAIN.P2':    'es_telephone_lines_per_100',
        'IS.AIR.PSGR':       'es_air_transport_passengers',
        'IS.AIR.GOOD.MT.K1': 'es_air_freight_million_ton_km',
        'IS.RRS.TOTL.KM':    'es_rail_lines_total_km',
        'IS.ROD.PAVE.ZS':    'es_paved_roads_pct_total'
    }
    
    df_es_selected = df_es[df_es['indicator_code'].isin(econstats_vars.keys())].copy()
    df_es_selected['var_name'] = df_es_selected['indicator_code'].map(econstats_vars)
    df_es_pivot = df_es_selected.pivot_table(
        index=['country_iso', 'country_name', 'year'],
        columns='var_name',
        values='value'
    ).reset_index()
    
    # 3. Mergear WB + EconStats para Argentina
    df_arg_wb = df_wb_pivot[df_wb_pivot['country_iso'] == 'ARG'].copy()
    df_arg_merged = pd.merge(df_arg_wb, df_es_pivot.drop(columns=['country_name']), on=['country_iso', 'year'], how='left')
    
    # 4. Guardar panel general de Argentina
    arg_panel_path = os.path.join(proc_dir, "tp3_panel_argentina.csv")
    df_arg_merged.to_csv(arg_panel_path, index=False)
    print(f"-> Panel consolidado de Argentina guardado: {arg_panel_path} ({len(df_arg_merged)} anios)")
    
    # 5. Panel general de India (comparativa)
    df_ind_wb = df_wb_pivot[df_wb_pivot['country_iso'] == 'IND'].copy()
    ind_panel_path = os.path.join(proc_dir, "tp3_panel_india.csv")
    df_ind_wb.to_csv(ind_panel_path, index=False)
    print(f"-> Panel consolidado de India guardado: {ind_panel_path} ({len(df_ind_wb)} anios)")
    
    # =========================================================================
    # PARTE 2: CRECIMIENTO EQUILIBRADO VS DESEQUILIBRADO
    # =========================================================================
    print("\n" + "=" * 80)
    print(" CALCULANDO DESVIACION ESTANDAR SECTORIAL ANUAL (NURKSE VS HIRSCHMAN)")
    print("=" * 80)
    
    for iso, df_c in [('ARG', df_arg_merged), ('IND', df_ind_wb)]:
        country_name = "Argentina" if iso == 'ARG' else "India"
        sec_cols = ['agriculture_va_growth_pct', 'industry_va_growth_pct', 'services_va_growth_pct']
        
        # Filtrar desde 1990 segun consigna
        df_sec = df_c[df_c['year'] >= 1990][['country_iso', 'year', 'gdp_pcap_growth_annual_pct'] + sec_cols].copy()
        
        # Desviación estándar transversal entre los 3 sectores para cada año
        df_sec['sector_growth_std'] = df_sec[sec_cols].std(axis=1, ddof=1)
        df_sec['sector_growth_mean'] = df_sec[sec_cols].mean(axis=1)
        
        # Determinar que sector lidera cada anio
        def get_leader(row):
            vals = {s.replace('_va_growth_pct', '').capitalize(): row[s] for s in sec_cols if pd.notnull(row[s])}
            if not vals:
                return 'N/A'
            return max(vals, key=vals.get)
            
        df_sec['leading_sector'] = df_sec.apply(get_leader, axis=1)
        
        out_sec_path = os.path.join(proc_dir, f"tp3_sector_growth_{iso.lower()}.csv")
        df_sec.to_csv(out_sec_path, index=False)
        print(f"\nResultados sectoriales para {country_name} (1990-2025):")
        print(f"{'Anio':<6} {'PBI pc %':<10} {'Agric %':<10} {'Ind %':<10} {'Serv %':<10} {'Desv.Est (DE)':<14} {'Lider':<12}")
        print("-" * 75)
        for _, r in df_sec.tail(15).iterrows():
            de_str = f"{r['sector_growth_std']:.2f}" if pd.notnull(r['sector_growth_std']) else "N/A"
            pbi_str = f"{r['gdp_pcap_growth_annual_pct']:.2f}" if pd.notnull(r['gdp_pcap_growth_annual_pct']) else "N/A"
            agr_str = f"{r['agriculture_va_growth_pct']:.2f}" if pd.notnull(r['agriculture_va_growth_pct']) else "N/A"
            ind_str = f"{r['industry_va_growth_pct']:.2f}" if pd.notnull(r['industry_va_growth_pct']) else "N/A"
            srv_str = f"{r['services_va_growth_pct']:.2f}" if pd.notnull(r['services_va_growth_pct']) else "N/A"
            print(f"{int(r['year']):<6} {pbi_str:<10} {agr_str:<10} {ind_str:<10} {srv_str:<10} {de_str:<14} {r['leading_sector']:<12}")
            
    print("\n" + "=" * 80)
    print("PROCESAMIENTO COMPLETADO EXITOSAMENTE.")
    print("=" * 80)

if __name__ == "__main__":
    main()
