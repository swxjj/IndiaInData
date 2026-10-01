import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

def run_regressions():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "tp5_india_stata.csv")
    if not os.path.exists(csv_path):
        csv_path = "TP5/data/processed/tp5_india_stata.csv"
        
    df = pd.read_csv(csv_path)
    df["lnpibpc"] = np.log(df["pib_pc_cte2015"])
    df["lnpibpc_ppp"] = np.log(df["pib_pc_ppp2021"])
    
    print("=" * 80)
    print(f"ANÁLISIS ECONOMÉTRICO TP5: INSTITUCIONES Y DESARROLLO EN INDIA")
    print(f"Muestra: {df['year'].min()} - {df['year'].max()} (N = {len(df)} observaciones anuales)")
    print("=" * 80)
    
    # 1. Regresiones bivariadas y con control de inversión (inv_fbcf)
    dimensions = [
        ("ge", "Eficacia del Gobierno (GE)"),
        ("rq", "Calidad Regulatoria (RQ)"),
        ("pv", "Estabilidad Política (PV)"),
        ("cc", "Control de la Corrupción (CC)"),
        ("va", "Voz y Rendición de Cuentas (VA)"),
        ("rl", "Estado de Derecho (RL)"),
        ("wgi_prom", "Índice Promedio WGI")
    ]
    
    results = {}
    
    print("\n" + "#" * 80)
    print("1. MODELOS INDIVIDUALES: ln(PIBpc) = α + β1(Institución) + β2(Inversión/PIB) + ε")
    print("#" * 80)
    
    summary_rows = []
    
    for code, name in dimensions:
        X = sm.add_constant(df[[code, "inv_fbcf"]])
        y = df["lnpibpc"]
        res = sm.OLS(y, X).fit()
        results[code] = res
        
        coef_inst = res.params[code]
        se_inst = res.bse[code]
        t_inst = res.tvalues[code]
        p_inst = res.pvalues[code]
        
        coef_inv = res.params["inv_fbcf"]
        se_inv = res.bse["inv_fbcf"]
        t_inv = res.tvalues["inv_fbcf"]
        p_inv = res.pvalues["inv_fbcf"]
        
        sig_inst = "***" if p_inst < 0.01 else ("**" if p_inst < 0.05 else ("*" if p_inst < 0.1 else ""))
        sig_inv = "***" if p_inv < 0.01 else ("**" if p_inv < 0.05 else ("*" if p_inv < 0.1 else ""))
        
        summary_rows.append({
            "Dimensión": name,
            "Código": code,
            "β Institución": f"{coef_inst:.4f}{sig_inst}",
            "Std.Err (Inst)": f"({se_inst:.4f})",
            "p-value (Inst)": f"{p_inst:.4f}",
            "β Inversión": f"{coef_inv:.4f}{sig_inv}",
            "Std.Err (Inv)": f"({se_inv:.4f})",
            "R2": f"{res.rsquared:.4f}",
            "R2 Adj": f"{res.rsquared_adj:.4f}",
            "F-stat": f"{res.fvalue:.2f}"
        })
        
    df_summary = pd.DataFrame(summary_rows)
    print(df_summary.to_string(index=False))
    
    # 2. Modelos con controles macroeconómicos adicionales (IED y Apertura Comercial)
    print("\n" + "#" * 80)
    print("2. MODELOS CON CONTROLES ADICIONALES: IED Y APERTURA COMERCIAL")
    print("#" * 80)
    
    # M1: GE base
    m_ge_base = sm.OLS(df["lnpibpc"], sm.add_constant(df[["ge", "inv_fbcf"]])).fit()
    # M2: GE + IED
    m_ge_fdi = sm.OLS(df["lnpibpc"], sm.add_constant(df[["ge", "inv_fbcf", "aper_fin_ied"]])).fit()
    # M3: GE + IED + Comercio
    m_ge_full_ctrl = sm.OLS(df["lnpibpc"], sm.add_constant(df[["ge", "inv_fbcf", "aper_fin_ied", "aper_comerc"]])).fit()
    # M4: WGI Prom + IED + Comercio
    m_prom_full_ctrl = sm.OLS(df["lnpibpc"], sm.add_constant(df[["wgi_prom", "inv_fbcf", "aper_fin_ied", "aper_comerc"]])).fit()
    
    ctrl_models = [
        ("(1) GE Base", m_ge_base),
        ("(2) GE + IED", m_ge_fdi),
        ("(3) GE + IED + Com.", m_ge_full_ctrl),
        ("(4) WGI Prom + IED + Com.", m_prom_full_ctrl)
    ]
    
    for title, mod in ctrl_models:
        print(f"\n--- {title} ---")
        print(mod.summary().tables[1])
        print(f"R2: {mod.rsquared:.4f}, Adj R2: {mod.rsquared_adj:.4f}, F({int(mod.df_model)}, {int(mod.df_resid)}): {mod.fvalue:.2f} (p={mod.f_pvalue:.2e})")

    # 3. Modelo completo con todas las dimensiones institucionales (Multicolinealidad)
    print("\n" + "#" * 80)
    print("3. REGRESIÓN MÚLTIPLE COMPLETA Y DIAGNÓSTICO DE MULTICOLINEALIDAD (VIF)")
    print("#" * 80)
    
    X_all_inst = sm.add_constant(df[["va", "pv", "ge", "rq", "rl", "cc", "inv_fbcf", "aper_fin_ied"]])
    m_full = sm.OLS(df["lnpibpc"], X_all_inst).fit()
    print("\n--- Modelo con las 6 Dimensiones WGI Simultáneas ---")
    print(m_full.summary().tables[1])
    print(f"R2: {m_full.rsquared:.4f}, Adj R2: {m_full.rsquared_adj:.4f}")
    
    vif_list = []
    for i, col in enumerate(X_all_inst.columns):
        if col != "const":
            vif = variance_inflation_factor(X_all_inst.values, i)
            vif_list.append({"Variable": col, "VIF": round(vif, 2), "Condición": "Grave (>10)" if vif > 10 else ("Moderada (5-10)" if vif > 5 else "Aceptable (<5)")})
    df_vif = pd.DataFrame(vif_list)
    print("\nFactores de Inflación de la Varianza (VIF):")
    print(df_vif.to_string(index=False))
    
    # 4. Modelos incorporando Capital Humano (Gasto en educación)
    print("\n" + "#" * 80)
    print("4. MODELOS CON CAPITAL HUMANO (GASTO EN EDUCACIÓN)")
    print("#" * 80)
    
    # Muestra original (con NaNs en gasto_educ)
    df_educ_clean = df.dropna(subset=["gasto_educ"])
    m_educ_orig = sm.OLS(df_educ_clean["lnpibpc"], sm.add_constant(df_educ_clean[["ge", "inv_fbcf", "gasto_educ"]])).fit()
    print(f"\n--- Gasto Educación Original (N = {len(df_educ_clean)}) ---")
    print(m_educ_orig.summary().tables[1])
    print(f"R2: {m_educ_orig.rsquared:.4f}")
    
    # Muestra completa con serie interpolada
    m_educ_interp = sm.OLS(df["lnpibpc"], sm.add_constant(df[["ge", "inv_fbcf", "gasto_educ_interp"]])).fit()
    print(f"\n--- Gasto Educación Interpolado (N = {len(df)}) ---")
    print(m_educ_interp.summary().tables[1])
    print(f"R2: {m_educ_interp.rsquared:.4f}")
    
    # Guardar reporte de regresiones en formato texto y markdown
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "resultados_regresiones_tp5.txt")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("REPORTE DETALLADO DE ESTIMACIONES ECONOMÉTRICAS - TP5 INDIA\n")
        f.write("=" * 80 + "\n\n")
        f.write("1. REGRESIONES POR DIMENSIÓN INSTITUCIONAL INDIVIDUAL CON INVERSIÓN\n")
        f.write("-" * 80 + "\n")
        f.write(df_summary.to_string(index=False) + "\n\n")
        
        f.write("2. MODELOS CON CONTROLES MACROECONÓMICOS Y APERTURA\n")
        f.write("-" * 80 + "\n")
        for title, mod in ctrl_models:
            f.write(f"\n{title}\n")
            f.write(str(mod.summary()) + "\n")
            
        f.write("\n3. MODELO CON TODAS LAS DIMENSIONES INSTITUCIONALES (FULL)\n")
        f.write("-" * 80 + "\n")
        f.write(str(m_full.summary()) + "\n")
        f.write("\nDIAGNÓSTICO VIF:\n")
        f.write(df_vif.to_string(index=False) + "\n\n")
        
        f.write("4. MODELOS CON CAPITAL HUMANO\n")
        f.write("-" * 80 + "\n")
        f.write("Gasto en Educación Original (N=20):\n")
        f.write(str(m_educ_orig.summary()) + "\n\n")
        f.write("Gasto en Educación Interpolado (N=27):\n")
        f.write(str(m_educ_interp.summary()) + "\n")

    print(f"\n[OK] Reporte exportado a: {report_path}")

if __name__ == "__main__":
    run_regressions()
