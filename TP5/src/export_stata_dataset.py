"""
=============================================================================
IndiaInData - TP5: Medio Ambiente, Instituciones y Desarrollo
Exportación de dataset limpio para Stata (.csv y .dta nativo)
=============================================================================
Genera un archivo con el PIB per cápita constante 2015 en niveles brutos (sin logaritmo),
los 6 indicadores de gobernabilidad WGI y las variables de control macroeconómico.
=============================================================================
"""

import os
import pandas as pd

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, "data", "processed")
    out_dir = os.path.join(base_dir, "output")
    
    # Cargar panel procesado de instituciones
    csv_in = os.path.join(proc_dir, "tp5_india_instituciones_desarrollo.csv")
    df = pd.read_csv(csv_in)
    
    # Seleccionar y renombrar variables con nomenclatura estándar de Stata (minúsculas, <= 32 caracteres)
    stata_rename = {
        'year': 'year',
        'pib_pc_cte2015_usd': 'pib_pc_cte2015',
        'pib_pc_ppp_cte2021': 'pib_pc_ppp2021',
        'voice_accountability': 'va',
        'political_stability': 'pv',
        'government_effectiveness': 'ge',
        'regulatory_quality': 'rq',
        'rule_of_law': 'rl',
        'control_of_corruption': 'cc',
        'wgi_promedio': 'wgi_prom',
        'inversion_fbcf_pct_pib': 'inv_fbcf',
        'inversion_total_pct_pib': 'inv_tot',
        'gasto_educacion_pct_pib': 'gasto_educ',
        'gasto_educacion_interp_pct_pib': 'gasto_educ_interp',
        'apertura_fin_ied_in_pct_pib': 'aper_fin_ied',
        'apertura_fin_ied_tot_pct_pib': 'aper_fin_tot',
        'apertura_comercial_pct_pib': 'aper_comerc'
    }
    
    cols_to_keep = [k for k in stata_rename.keys() if k in df.columns]
    df_stata = df[cols_to_keep].rename(columns=stata_rename)
    
    # Etiquetas de variables para Stata
    var_labels = {
        'year': 'Ano de observacion (1996-2025)',
        'pib_pc_cte2015': 'PIB per capita bruto (cte 2015 USD)',
        'pib_pc_ppp2021': 'PIB per capita PPA bruto (cte 2021 USD)',
        'va': 'Voz y Rendicion de Cuentas (WGI Estimate)',
        'pv': 'Estabilidad Politica y Ausencia Violencia (WGI Estimate)',
        'ge': 'Eficacia del Gobierno (WGI Estimate)',
        'rq': 'Calidad Regulatoria (WGI Estimate)',
        'rl': 'Estado de Derecho (WGI Estimate)',
        'cc': 'Control de la Corrupcion (WGI Estimate)',
        'wgi_prom': 'Indice Promedio Simple WGI (6 dimensiones)',
        'inv_fbcf': 'Inversion FBCF (% del PIB)',
        'inv_tot': 'Inversion Bruta Total (% del PIB)',
        'gasto_educ': 'Gasto publico en educacion (% PIB) [Original WB]',
        'gasto_educ_interp': 'Gasto publico educacion (% PIB) [Interpolada]',
        'aper_fin_ied': 'Apertura financiera: IED neta entradas (% PIB)',
        'aper_fin_tot': 'Apertura financiera: IED bruta total (% PIB)',
        'aper_comerc': 'Apertura comercial: Exportaciones+Importaciones (% PIB)'
    }
    
    # Destinos
    csv_proc = os.path.join(proc_dir, "tp5_india_stata.csv")
    dta_proc = os.path.join(proc_dir, "tp5_india_stata.dta")
    csv_out = os.path.join(out_dir, "tp5_india_stata.csv")
    dta_out = os.path.join(out_dir, "tp5_india_stata.dta")
    
    # Guardar CSV limpio (coma separador, punto decimal, sin índice)
    df_stata.to_csv(csv_proc, index=False, encoding="utf-8")
    df_stata.to_csv(csv_out, index=False, encoding="utf-8")
    
    # Guardar DTA nativo con etiquetas
    df_stata.to_stata(dta_proc, write_index=False, variable_labels=var_labels, version=117)
    df_stata.to_stata(dta_out, write_index=False, variable_labels=var_labels, version=117)
    
    print("Dataset exportado exitosamente para Stata:")
    print(f" - CSV: {csv_proc}")
    print(f" - DTA: {dta_proc}")
    print(f"Dimensiones: {df_stata.shape[0]} filas x {df_stata.shape[1]} columnas.")
    print("Primeras filas:")
    print(df_stata[['year', 'pib_pc_cte2015', 'ge', 'rq', 'rl', 'inv_fbcf']].head())

if __name__ == "__main__":
    main()
