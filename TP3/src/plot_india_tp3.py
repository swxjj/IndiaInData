import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# -----------------------------------------------------------------------------
# CONFIGURACIÓN ESTÉTICA ACADÉMICA LIMPIA
# -----------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, "data", "processed")
    fig_dir = os.path.join(base_dir, "output", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    # Cargar datos
    panel_file = os.path.join(proc_dir, "tp3_panel_india.csv")
    df = pd.read_csv(panel_file).sort_values("year").reset_index(drop=True)
    
    print("=" * 80)
    print(" GENERACIÓN DE GRÁFICOS ACADÉMICOS PARA INDIA - TP3 (BIG PUSH)")
    print("=" * 80)
    
    # =========================================================================
    # GRÁFICO 1: HISTÓRICO COMPLETO DE CRECIMIENTO E INVERSIÓN (1960–2025)
    # =========================================================================
    print("-> Generando Gráfico 1: Histórico de Crecimiento e Inversión (1960–2025)...")
    fig1, (ax1a, ax1b) = plt.subplots(2, 1, figsize=(11, 8), sharex=True, gridspec_kw={'height_ratios': [1.2, 1]})
    
    # Subplot 1: Inversión bruta, inversión fija e IED (% del PIB)
    ax1a.plot(df['year'], df['gross_capital_formation_pct_gdp'], label='Inversión bruta (% del PIB)', color='#1f77b4', lw=2.2)
    ax1a.plot(df['year'], df['gross_fixed_capital_formation_pct_gdp'], label='Inversión fija bruta (% del PIB)', color='#2ca02c', lw=2.0, ls='--')
    ax1a.plot(df['year'], df['fdi_net_inflows_pct_gdp'], label='IED neta (% del PIB)', color='#d62728', lw=1.8)
    ax1a.set_ylabel('% del PIB')
    ax1a.set_ylim(0, 48)
    ax1a.set_title("Panel A: Inversión Bruta, Inversión Fija e Inversión Extranjera Directa (% del PIB)", fontweight='bold')
    ax1a.legend(loc='upper left', frameon=True)
    ax1a.grid(True, linestyle='--', alpha=0.5)
    
    # Subplot 2: Crecimiento del PIB per cápita (% anual)
    ax1b.bar(df['year'], df['gdp_pcap_growth_pct'], width=0.65, color='#4682b4', alpha=0.45, label='Crecimiento anual del PIB pc (%)')
    df['gdp_pc_ma5'] = df['gdp_pcap_growth_pct'].rolling(5, min_periods=3).mean()
    ax1b.plot(df['year'], df['gdp_pc_ma5'], color='#000080', lw=2.2, label='Media móvil de 5 años')
    ax1b.axhline(0, color='gray', linestyle='-', lw=0.9)
    ax1b.set_ylabel('% anual')
    ax1b.set_xlabel('Año')
    ax1b.set_ylim(-8, 12)
    ax1b.set_xlim(1959, 2026)
    ax1b.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax1b.set_title("Panel B: Tasa de Crecimiento del PIB per Cápita Anual y Tendencia (Media Móvil 5 Años)", fontweight='bold')
    ax1b.legend(loc='upper left', frameon=True)
    ax1b.grid(True, linestyle='--', alpha=0.5)
    
    fig1.suptitle("India: Dinámica Histórica de Crecimiento Económico y Acumulación de Capital (1960–2025)", fontweight='bold', y=0.98)
    fig1.tight_layout()
    fig1_path = os.path.join(fig_dir, "fig1_india_crecimiento_inversion_historico.png")
    fig1.savefig(fig1_path, dpi=300)
    plt.close(fig1)
    print(f"   [OK]: {fig1_path}")

    # =========================================================================
    # GRÁFICO 2: HISTÓRICO COMPLETO DE TRANSPORTE (1970–2023)
    # =========================================================================
    print("-> Generando Gráfico 2: Histórico de Infraestructura y Tráfico de Transporte...")
    fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(11, 8))
    
    # Subplot 1: Ferrocarriles (Carga y Pasajeros, 1980–2008)
    sub_rail = df.dropna(subset=['econ_railways_goods_million_ton_km', 'econ_railways_passengers_million_km'])
    ax2a_twin = ax2a.twinx()
    
    l1 = ax2a.plot(sub_rail['year'], sub_rail['econ_railways_goods_million_ton_km'], color='#8c564b', lw=2.2, label='Carga ferroviaria (millones ton-km)')
    l2 = ax2a_twin.plot(sub_rail['year'], sub_rail['econ_railways_passengers_million_km'], color='#1f77b4', lw=2.2, ls='--', label='Pasajeros ferroviarios (millones pas-km)')
    
    ax2a.set_ylabel('Millones de ton-km (Carga)', color='#8c564b')
    ax2a_twin.set_ylabel('Millones de pas-km (Pasajeros)', color='#1f77b4')
    ax2a.set_xlim(1979, 2010)
    ax2a.set_xlabel('Año')
    ax2a.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax2a.set_title("Panel A: Transporte Ferroviario – Tráfico de Carga y Pasajeros (1980–2008)", fontweight='bold')
    
    lines_rail = l1 + l2
    labels_rail = [l.get_label() for l in lines_rail]
    ax2a.legend(lines_rail, labels_rail, loc='upper left', frameon=True)
    ax2a.grid(True, linestyle='--', alpha=0.5)
    
    # Subplot 2: Transporte Aéreo Comercial (Pasajeros y Carga, 1970–2023)
    sub_air = df.dropna(subset=['wb_air_passengers_carried'])
    # Pasajeros en millones
    passengers_millions = sub_air['wb_air_passengers_carried'] / 1e6
    ax2b.plot(sub_air['year'], passengers_millions, color='#2ca02c', lw=2.2, marker='o', ms=3.5, label='Pasajeros aéreos transportados (millones de personas)')
    
    ax2b.set_ylabel('Millones de pasajeros')
    ax2b.set_xlabel('Año')
    ax2b.set_xlim(1969, 2025)
    ax2b.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax2b.set_title("Panel B: Transporte Aéreo Comercial – Pasajeros Transportados (1970–2023)", fontweight='bold')
    ax2b.legend(loc='upper left', frameon=True)
    ax2b.grid(True, linestyle='--', alpha=0.5)
    
    fig2.suptitle("India: Evolución Histórica del Transporte y Movilidad (1970–2023)", fontweight='bold', y=0.98)
    fig2.tight_layout()
    fig2_path = os.path.join(fig_dir, "fig2_india_transporte_historico.png")
    fig2.savefig(fig2_path, dpi=300)
    plt.close(fig2)
    print(f"   [OK]: {fig2_path}")

    # =========================================================================
    # GRÁFICO 3: HISTÓRICO COMPLETO DE ENERGÍA Y TELECOMUNICACIONES (1960–2025)
    # =========================================================================
    print("-> Generando Gráfico 3: Histórico de Energía y Telecomunicaciones...")
    fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(11, 8))
    
    # Subplot 1: Energía y Servicios Básicos
    ax3a_twin = ax3a.twinx()
    
    # Consumo kWh pc
    sub_elec = df.dropna(subset=['wb_electric_power_kwh_pc'])
    l_e1 = ax3a.plot(sub_elec['year'], sub_elec['wb_electric_power_kwh_pc'], color='#d95f02', lw=2.2, label='Consumo eléctrico per cápita (kWh)')
    
    # Acceso a electricidad y agua potable básica (% pob)
    sub_acc = df.dropna(subset=['wb_access_electricity_pct_pop'])
    l_e2 = ax3a_twin.plot(sub_acc['year'], sub_acc['wb_access_electricity_pct_pop'], color='#1f77b4', lw=2.0, ls='-', label='Acceso a electricidad (% población)')
    
    sub_wat = df.dropna(subset=['wb_basic_drinking_water_pct_pop'])
    l_e3 = ax3a_twin.plot(sub_wat['year'], sub_wat['wb_basic_drinking_water_pct_pop'], color='#17becf', lw=2.0, ls='--', label='Acceso a agua potable básica (% población)')
    
    ax3a.set_ylabel('kWh per cápita', color='#d95f02')
    ax3a_twin.set_ylabel('% de la población', color='#1f77b4')
    ax3a_twin.set_ylim(40, 105)
    ax3a.set_xlim(1989, 2026)
    ax3a.set_xlabel('Año')
    ax3a.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax3a.set_title("Panel A: Sector Eléctrico y Servicios Básicos (1990–2024)", fontweight='bold')
    
    lines_energy = l_e1 + l_e2 + l_e3
    labels_energy = [l.get_label() for l in lines_energy]
    ax3a.legend(lines_energy, labels_energy, loc='center left', frameon=True)
    ax3a.grid(True, linestyle='--', alpha=0.5)
    
    # Subplot 2: Telecomunicaciones y Digitalización
    sub_tel = df.dropna(subset=['econ_telephone_lines_per_100'])
    ax3b.plot(sub_tel['year'], sub_tel['econ_telephone_lines_per_100'], color='#7f7f7f', lw=1.8, ls=':', label='Telefonía fija (por 100 hab)')
    
    sub_cel = df.dropna(subset=['wb_mobile_subscriptions_per_100'])
    ax3b.plot(sub_cel['year'], sub_cel['wb_mobile_subscriptions_per_100'], color='#2ca02c', lw=2.2, label='Telefonía celular (por 100 hab)')
    
    sub_net = df.dropna(subset=['wb_internet_users_pct_pop'])
    ax3b.plot(sub_net['year'], sub_net['wb_internet_users_pct_pop'], color='#9467bd', lw=2.0, ls='-', label='Usuarios de Internet (% población)')
    
    sub_bb = df.dropna(subset=['wb_broadband_subscriptions_per_100'])
    ax3b.plot(sub_bb['year'], sub_bb['wb_broadband_subscriptions_per_100'], color='#d62728', lw=1.8, ls='--', label='Banda ancha fija (por 100 hab)')
    
    ax3b.set_ylabel('Suscripciones / % de población')
    ax3b.set_xlabel('Año')
    ax3b.set_xlim(1959, 2026)
    ax3b.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax3b.set_title("Panel B: Telecomunicaciones y Conectividad Digital (1960–2025)", fontweight='bold')
    ax3b.legend(loc='upper left', frameon=True)
    ax3b.grid(True, linestyle='--', alpha=0.5)
    
    fig3.suptitle("India: Infraestructura de Energía y Telecomunicaciones (1960–2025)", fontweight='bold', y=0.98)
    fig3.tight_layout()
    fig3_path = os.path.join(fig_dir, "fig3_india_energia_telecomunicaciones_historico.png")
    fig3.savefig(fig3_path, dpi=300)
    plt.close(fig3)
    print(f"   [OK]: {fig3_path}")

    # =========================================================================
    # GRÁFICO 4: ZOOM AL PERÍODO MÁS RELEVANTE DEL BIG PUSH (2000–2015)
    # =========================================================================
    print("-> Generando Gráfico 4: Zoom al Período Más Relevante del Big Push (2000–2015)...")
    fig4, (ax4a, ax4b) = plt.subplots(2, 1, figsize=(11, 8.5))
    
    df_zoom = df[(df['year'] >= 2000) & (df['year'] <= 2015)].copy()
    
    # Subplot 1: Dinámica de Crecimiento e Inversión
    ax4a_twin = ax4a.twinx()
    
    l_z1 = ax4a.plot(df_zoom['year'], df_zoom['gross_capital_formation_pct_gdp'], color='#1f77b4', lw=2.4, marker='o', ms=4, label='Inversión bruta (% del PIB)')
    l_z2 = ax4a.plot(df_zoom['year'], df_zoom['gross_fixed_capital_formation_pct_gdp'], color='#2ca02c', lw=2.0, ls='--', marker='s', ms=4, label='Inversión fija bruta (% del PIB)')
    
    l_z3 = ax4a_twin.plot(df_zoom['year'], df_zoom['gdp_pcap_growth_pct'], color='#ff7f0e', lw=2.2, marker='^', ms=4.5, label='Crecimiento PIB pc (% anual)')
    l_z4 = ax4a_twin.plot(df_zoom['year'], df_zoom['fdi_net_inflows_pct_gdp'], color='#d62728', lw=1.8, ls=':', marker='d', ms=4, label='IED neta (% del PIB)')
    
    ax4a.set_ylabel('% del PIB (Inversión)')
    ax4a.set_ylim(20, 46)
    ax4a_twin.set_ylabel('% anual (Crecimiento / IED)')
    ax4a_twin.set_ylim(0, 10)
    ax4a.set_xlim(1999.5, 2015.5)
    ax4a.set_xlabel('Año')
    ax4a.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax4a.set_title("Panel A: Inversión Bruta, Inversión Fija, IED y Crecimiento del PIB per Cápita (2000–2015)", fontweight='bold')
    
    lines_z1 = l_z1 + l_z2 + l_z3 + l_z4
    labels_z1 = [l.get_label() for l in lines_z1]
    ax4a.legend(lines_z1, labels_z1, loc='upper left', frameon=True, ncol=2)
    ax4a.grid(True, linestyle='--', alpha=0.5)
    
    # Subplot 2: Coevolución de Redes e Infraestructura Indexadas (Base 2000 = 100)
    base_yr = 2000
    
    def get_index(col_name):
        base_val = df_zoom[df_zoom['year'] == base_yr][col_name].values[0]
        if pd.notna(base_val) and base_val > 0:
            return (df_zoom[col_name] / base_val) * 100
        return pd.Series(index=df_zoom.index, dtype=float)
        
    idx_inv = get_index('gross_capital_formation_pct_gdp')
    idx_air = get_index('wb_air_passengers_carried')
    idx_cel = get_index('wb_mobile_subscriptions_per_100')
    idx_kwh = get_index('wb_electric_power_kwh_pc')
    idx_rail = get_index('econ_railways_goods_million_ton_km')
    
    ax4b.plot(df_zoom['year'], idx_inv, color='#1f77b4', lw=2.2, marker='o', ms=4, label='Inversión bruta (% PIB)')
    ax4b.plot(df_zoom['year'], idx_kwh, color='#d95f02', lw=2.0, marker='s', ms=4, label='Consumo eléctrico pc (kWh)')
    ax4b.plot(df_zoom['year'], idx_rail, color='#8c564b', lw=2.0, ls='--', marker='v', ms=4, label='Carga ferroviaria (ton-km, hasta 2008)')
    ax4b.plot(df_zoom['year'], idx_air, color='#2ca02c', lw=2.2, marker='^', ms=4, label='Pasajeros aéreos transportados')
    
    ax4b.axhline(100, color='gray', linestyle=':', lw=1)
    ax4b.set_ylabel('Índice (Año 2000 = 100)')
    ax4b.set_xlabel('Año')
    ax4b.set_xlim(1999.5, 2015.5)
    ax4b.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax4b.set_title("Panel B: Coevolución de Inversión y Redes Complementarias (Índice Base 2000 = 100)", fontweight='bold')
    ax4b.legend(loc='upper left', frameon=True, ncol=2)
    ax4b.grid(True, linestyle='--', alpha=0.5)
    
    fig4.suptitle("India: Zoom al Período del Big Push y Coevolución de Complementariedades (2000–2015)", fontweight='bold', y=0.98)
    fig4.tight_layout()
    fig4_path = os.path.join(fig_dir, "fig4_india_big_push_zoom_2000_2015.png")
    fig4.savefig(fig4_path, dpi=300)
    plt.close(fig4)
    print(f"   [OK]: {fig4_path}")
    
    print("\n" + "=" * 80)
    print(" ¡TODOS LOS GRÁFICOS FUERON GENERADOS Y GUARDADOS CON ÉXITO EN output/figures/!")
    print("=" * 80)

if __name__ == "__main__":
    main()
