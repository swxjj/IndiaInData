import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Estilo academico
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.titlesize'] = 14

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, "data", "processed")
    fig_dir = os.path.join(base_dir, "output", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    print("=" * 80)
    print(" GENERANDO GRAFICOS ACADEMICOS PARA TP3 (BIG PUSH Y CRECIMIENTO SECTORIAL)")
    print("=" * 80)
    
    # -------------------------------------------------------------------------
    # FIGURA 1: Crecimiento Sectorial y PIB pc (Argentina, 1990-2025)
    # -------------------------------------------------------------------------
    df_sec_arg = pd.read_csv(os.path.join(proc_dir, "tp3_sector_growth_arg.csv"))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    # Panel superior: Sectores vs PIB pc
    ax1.plot(df_sec_arg['year'], df_sec_arg['agriculture_va_growth_pct'], label='Agricultura, silvicultura y pesca', color='#2ca02c', lw=2, marker='o', ms=4)
    ax1.plot(df_sec_arg['year'], df_sec_arg['industry_va_growth_pct'], label='Industria y construccion', color='#d62728', lw=2, marker='s', ms=4)
    ax1.plot(df_sec_arg['year'], df_sec_arg['services_va_growth_pct'], label='Servicios', color='#1f77b4', lw=2, marker='^', ms=4)
    ax1.plot(df_sec_arg['year'], df_sec_arg['gdp_pcap_growth_annual_pct'], label='PIB per capita (crec. anual %)', color='black', lw=2.5, ls='--', alpha=0.85)
    
    ax1.axhline(0, color='gray', linestyle=':', lw=1)
    ax1.set_title("Argentina: Crecimiento Anual por Sector vs. PIB per Cápita (1990–2025)", fontweight='bold')
    ax1.set_ylabel("Tasa de Crecimiento Anual (%)")
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(True, alpha=0.3)
    
    # Panel inferior: Desviación estándar transversal anual (Nurkse vs Hirschman)
    ax2.bar(df_sec_arg['year'], df_sec_arg['sector_growth_std'], color='#7f7f7f', alpha=0.7, width=0.7, label='Desv. Estándar Sectorial (DE)')
    ax2.axhline(df_sec_arg['sector_growth_std'].mean(), color='crimson', ls='--', lw=1.5, label=f"Media histórica DE ({df_sec_arg['sector_growth_std'].mean():.2f})")
    ax2.set_title("Índice de Desequilibrio Sectorial: Desviación Estándar Transversal entre Sectores", fontweight='bold')
    ax2.set_xlabel("Año")
    ax2.set_ylabel("Desviación Estándar (p.p.)")
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig_path1 = os.path.join(fig_dir, "fig1_argentina_crecimiento_sectorial_desequilibrio.png")
    plt.savefig(fig_path1, dpi=300)
    plt.close()
    print(f"-> Figura 1 guardada: {fig_path1}")
    
    # -------------------------------------------------------------------------
    # FIGURA 2: Big Push - Inversión, IED y Crecimiento en Argentina (1990-2025)
    # -------------------------------------------------------------------------
    df_arg = pd.read_csv(os.path.join(proc_dir, "tp3_panel_argentina.csv"))
    df_arg_sub = df_arg[df_arg['year'] >= 1990]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    l1 = ax1.plot(df_arg_sub['year'], df_arg_sub['gross_capital_formation_pct_gdp'], color='#1f77b4', lw=2.5, marker='o', ms=4, label='Inversión Bruta (% PIB)')
    l2 = ax1.plot(df_arg_sub['year'], df_arg_sub['fdi_net_inflows_pct_gdp'], color='#ff7f0e', lw=2, marker='v', ms=4, label='IED neta (% PIB)')
    l3 = ax2.plot(df_arg_sub['year'], df_arg_sub['gdp_pcap_growth_annual_pct'], color='#2ca02c', lw=2, ls='--', label='Crec. PBI pc (% anual)')
    
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Inversión e IED (% del PIB)", color='#1f77b4')
    ax2.set_ylabel("Crecimiento PBI pc (%)", color='#2ca02c')
    ax2.axhline(0, color='gray', linestyle=':', lw=1)
    
    lines = l1 + l2 + l3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True)
    ax1.set_title("Argentina: Coevolución de Inversión, IED y Crecimiento del PIB pc (1990–2025)", fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig_path2 = os.path.join(fig_dir, "fig2_argentina_big_push_inversion_crecimiento.png")
    plt.savefig(fig_path2, dpi=300)
    plt.close()
    print(f"-> Figura 2 guardada: {fig_path2}")
    
    # -------------------------------------------------------------------------
    # FIGURA 3: Infraestructura y Complementariedad (Electricidad, Internet, Tel)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df_arg_sub['year'], df_arg_sub['access_electricity_pct_pop'], color='#e377c2', lw=2.5, label='Acceso a Electricidad (% pob)')
    ax.plot(df_arg_sub['year'], df_arg_sub['internet_users_pct_pop'], color='#17becf', lw=2.5, marker='s', ms=4, label='Usuarios de Internet (% pob)')
    ax.plot(df_arg_sub['year'], df_arg_sub['mobile_subscriptions_per_100'], color='#bcbd22', lw=2, ls='-.', label='Telefonía móvil (por 100 hab)')
    
    ax.set_title("Argentina: Evolución de Infraestructura y Redes Complementarias (1990–2025)", fontweight='bold')
    ax.set_xlabel("Año")
    ax.set_ylabel("Tasa de Cobertura / Suscripciones")
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig_path3 = os.path.join(fig_dir, "fig3_argentina_infraestructura_complementariedad.png")
    plt.savefig(fig_path3, dpi=300)
    plt.close()
    print(f"-> Figura 3 guardada: {fig_path3}")
    
    print("\nTODOS LOS GRAFICOS FUERON GENERADOS CON CALIDAD VECTORIAL/ALTA RESOLUCION.")

if __name__ == "__main__":
    main()
