"""
=============================================================================
IndiaInData - Trabajo Práctico 5: Medio Ambiente, Instituciones y Desarrollo
Script de Compilación y Visualización Gráfica Académica
=============================================================================
Este script genera los análisis gráficos requeridos por la consigna:
1. Evolución temporal de las 6 dimensiones de Gobernabilidad (WGI).
2. Co-evolución temporal de ln(PIBpc) y el Índice Promedio de Gobernabilidad.
3. Matriz de correlaciones de Pearson (Heatmap) entre dimensiones institucionales,
   variables de control y PIB per cápita.
4. Panel comparativo de dispersión bivariada (6 dimensiones vs ln(PIBpc)) con
   coeficientes de correlación r sin estimar regresiones ni betas.
5. Huella Ecológica vs. Biocapacidad per cápita (1961–2025) y déficit ecológico.
6. Descomposición estructural de la Huella Ecológica por componentes.
=============================================================================
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def setup_academic_style():
    """Configura el estilo visual académico estandarizado de IndiaInData."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 10.5
    plt.rcParams["axes.labelweight"] = "bold"
    plt.rcParams["xtick.labelsize"] = 9.5
    plt.rcParams["ytick.labelsize"] = 9.5
    plt.rcParams["legend.fontsize"] = 9
    plt.rcParams["figure.titlesize"] = 13.5
    plt.rcParams["figure.titleweight"] = "bold"
    plt.rcParams["axes.edgecolor"] = "#374151"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#e5e7eb"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.alpha"] = 0.7

def main():
    setup_academic_style()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, "data", "processed")
    fig_dir = os.path.join(base_dir, "output", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    # Cargar datos procesados
    inst_path = os.path.join(proc_dir, "tp5_india_instituciones_desarrollo.csv")
    env_path = os.path.join(proc_dir, "tp5_india_medio_ambiente.csv")
    
    df_inst = pd.read_csv(inst_path)
    df_env = pd.read_csv(env_path)
    
    # Paleta de colores académica
    colors = {
        'india_saffron': '#ea580c',
        'navy': '#1e3a8a',
        'blue': '#2563eb',
        'emerald': '#059669',
        'green': '#16a34a',
        'crimson': '#dc2626',
        'purple': '#7c3aed',
        'amber': '#d97706',
        'cyan': '#0891b2',
        'gray': '#6b7280',
        'dark': '#111827'
    }
    
    # =========================================================================
    # GRÁFICO 1: EVOLUCIÓN TEMPORAL DE LAS 6 DIMENSIONES WGI (1996 - 2025)
    # =========================================================================
    print("Generando Gráfico 1: Series temporales WGI...")
    fig1, ax1 = plt.subplots(figsize=(10.5, 6.5), dpi=300)
    
    wgi_dims = [
        ('government_effectiveness', 'Eficacia del Gobierno (GE)', colors['emerald'], 'o', '-'),
        ('regulatory_quality', 'Calidad Regulatoria (RQ)', colors['blue'], 's', '-'),
        ('political_stability', 'Estabilidad Política (PV)', colors['purple'], '^', '--'),
        ('control_of_corruption', 'Control de la Corrupción (CC)', colors['amber'], 'D', '-.'),
        ('voice_accountability', 'Voz y Rendición de Cuentas (VA)', colors['india_saffron'], 'v', '-'),
        ('rule_of_law', 'Estado de Derecho (RL)', colors['crimson'], 'p', '--')
    ]
    
    for col, label, c, m, ls in wgi_dims:
        ax1.plot(df_inst['year'], df_inst[col], color=c, marker=m, markersize=5,
                 linewidth=2.0, linestyle=ls, label=label, alpha=0.9)
    
    # Línea neutral de referencia
    ax1.axhline(0, color='#4b5563', linestyle=':', linewidth=1.5, alpha=0.8, zorder=2)
    ax1.text(df_inst['year'].min(), 0.03, ' Media mundial estandarizada (0.0)',
             color='#4b5563', fontsize=8.5, fontstyle='italic')
    
    ax1.set_title("India: Evolución de las 6 Dimensiones de Gobernabilidad (WGI 1996–2025)", pad=15)
    ax1.set_xlabel("Año", labelpad=8)
    ax1.set_ylabel("Puntaje Estimado de Gobernabilidad (aprox. -2.5 a +2.5)", labelpad=8)
    ax1.set_xlim(1995, 2026)
    ax1.set_xticks([1996, 1998, 2000] + list(range(2002, 2026, 3)) + [2025])
    ax1.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9, edgecolor='#d1d5db')
    
    fig1.tight_layout()
    fig1.savefig(os.path.join(fig_dir, "grafico1_wgi_series_temporales.png"), dpi=300)
    fig1.savefig(os.path.join(fig_dir, "grafico1_wgi_series_temporales.pdf"))
    plt.close(fig1)
    
    # =========================================================================
    # GRÁFICO 2: CO-EVOLUCIÓN PIB PER CÁPITA VS GOBERNABILIDAD PROMEDIO
    # =========================================================================
    print("Generando Gráfico 2: PIB per cápita vs Gobernabilidad promedio...")
    fig2, ax2_left = plt.subplots(figsize=(10, 6), dpi=300)
    ax2_right = ax2_left.twinx()
    
    # Serie izquierda: ln(PIBpc PPA)
    line1 = ax2_left.plot(df_inst['year'], df_inst['ln_pib_pc_ppp'], color=colors['india_saffron'],
                          linewidth=2.6, marker='o', markersize=5, label='ln(PIB per cápita PPA cte 2021 USD)')
    # Serie derecha: WGI promedio
    line2 = ax2_right.plot(df_inst['year'], df_inst['wgi_promedio'], color=colors['blue'],
                           linewidth=2.2, linestyle='--', marker='s', markersize=5, label='Índice Promedio WGI (6 dimensiones)')
    
    ax2_left.set_title("India: Dinámica de Crecimiento del PIB per cápita y Gobernabilidad Promedio (1996–2025)", pad=15)
    ax2_left.set_xlabel("Año", labelpad=8)
    ax2_left.set_ylabel("Logaritmo del PIB per cápita (PPA cte 2021 USD)", color='black', labelpad=8)
    ax2_right.set_ylabel("Puntaje Promedio WGI", color='black', labelpad=8)
    
    ax2_left.tick_params(axis='y', labelcolor='black')
    ax2_right.tick_params(axis='y', labelcolor='black')
    ax2_left.set_xticks([1996, 1998, 2000] + list(range(2002, 2026, 3)) + [2025])
    
    # Unir leyendas
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2_left.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', framealpha=0.9, edgecolor='#d1d5db')
    
    fig2.tight_layout()
    fig2.savefig(os.path.join(fig_dir, "grafico2_pib_vs_gobernabilidad_promedio.png"), dpi=300)
    fig2.savefig(os.path.join(fig_dir, "grafico2_pib_vs_gobernabilidad_promedio.pdf"))
    plt.close(fig2)
    
    # =========================================================================
    # GRÁFICO 3: MATRIZ DE CORRELACIONES DE PEARSON (HEATMAP)
    # =========================================================================
    print("Generando Gráfico 3: Matriz de correlaciones (Heatmap)...")
    corr_cols = [
        ('ln_pib_pc_ppp', 'ln(PIBpc PPA)'),
        ('government_effectiveness', 'Eficacia Gob. (GE)'),
        ('regulatory_quality', 'Calidad Reg. (RQ)'),
        ('political_stability', 'Estab. Política (PV)'),
        ('control_of_corruption', 'Control Corrup. (CC)'),
        ('voice_accountability', 'Voz y Rend. (VA)'),
        ('rule_of_law', 'Estado Derecho (RL)'),
        ('inversion_fbcf_pct_pib', 'Inversión FBCF (% PIB)'),
        ('gasto_educacion_pct_pib', 'Educación (% PIB)')
    ]
    
    corr_df = df_inst[[c[0] for c in corr_cols if c[0] in df_inst.columns]].copy()
    labels = [c[1] for c in corr_cols if c[0] in df_inst.columns]
    corr_matrix = corr_df.corr(method='pearson')
    
    fig3, ax3 = plt.subplots(figsize=(9.5, 8), dpi=300)
    ax3.grid(False)
    cax = ax3.matshow(corr_matrix, cmap='coolwarm', vmin=-1.0, vmax=1.0)

    
    fig3.colorbar(cax, ax=ax3, fraction=0.046, pad=0.04, label="Coeficiente de Correlación de Pearson (r)")
    
    ax3.set_xticks(range(len(labels)))
    ax3.set_yticks(range(len(labels)))
    ax3.set_xticklabels(labels, rotation=45, ha='left', fontsize=9.5)
    ax3.set_yticklabels(labels, fontsize=9.5)
    
    # Anotar valores numéricos
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr_matrix.iloc[i, j]
            if pd.notna(val):
                text_color = 'white' if abs(val) > 0.45 else '#111827'
                ax3.text(j, i, f"{val:.2f}", ha='center', va='center',
                         color=text_color, fontweight='bold', fontsize=9.5)
    
    ax3.set_title("India: Matriz de Correlación de Pearson entre Gobernabilidad, Inversión y PIBpc",
                  pad=40, fontsize=12)
    fig3.tight_layout()
    fig3.savefig(os.path.join(fig_dir, "grafico3_matriz_correlaciones_pearson.png"), dpi=300)
    fig3.savefig(os.path.join(fig_dir, "grafico3_matriz_correlaciones_pearson.pdf"))
    plt.close(fig3)
    
    # =========================================================================
    # GRÁFICO 4: PANEL DE DISPERSIÓN BIVARIADA (6 DIMENSIONES VS ln(PIBpc))
    # Sin trazar rectas de regresión ni estimar betas (enfoque descriptivo)
    # =========================================================================
    print("Generando Gráfico 4: Panel de dispersión bivariada...")
    fig4, axes = plt.subplots(2, 3, figsize=(14, 9), dpi=300)
    axes = axes.flatten()
    
    wgi_panel = [
        ('government_effectiveness', 'Eficacia del Gobierno (GE)', colors['emerald']),
        ('regulatory_quality', 'Calidad Regulatoria (RQ)', colors['blue']),
        ('political_stability', 'Estabilidad Política (PV)', colors['purple']),
        ('control_of_corruption', 'Control de la Corrupción (CC)', colors['amber']),
        ('voice_accountability', 'Voz y Rendición de Cuentas (VA)', colors['india_saffron']),
        ('rule_of_law', 'Estado de Derecho (RL)', colors['crimson'])
    ]
    
    # Colorear puntos por década temporal para observar la trayectoria histórica
    years = df_inst['year'].values
    period_colors = []
    for y in years:
        if y < 2005:
            period_colors.append('#93c5fd')  # Celeste claro (1996-2004)
        elif y < 2015:
            period_colors.append('#3b82f6')  # Azul medio (2005-2014)
        else:
            period_colors.append('#1e3a8a')  # Azul oscuro / marino (2015-2025)
    
    for idx, (col, title, color_theme) in enumerate(wgi_panel):
        ax = axes[idx]
        x_vals = df_inst[col]
        y_vals = df_inst['ln_pib_pc_ppp']
        
        # Calcular correlación r y p-value
        valid_mask = x_vals.notna() & y_vals.notna()
        r_val, p_val = stats.pearsonr(x_vals[valid_mask], y_vals[valid_mask])
        
        # Dispersión con borde temático
        scatter = ax.scatter(x_vals, y_vals, c=period_colors, s=70, edgecolors=color_theme,
                             linewidths=1.5, alpha=0.9, zorder=3)
        
        # Conectar cronológicamente los puntos de forma sutil
        ax.plot(x_vals, y_vals, color='#cbd5e1', linewidth=0.8, linestyle=':', zorder=2)
        
        # Etiquetar años emblemáticos: inicio (1996), quiebre (2014) y cierre (2025)
        for target_yr in [1996, 2014, 2025]:
            row_yr = df_inst[df_inst['year'] == target_yr]
            if not row_yr.empty:
                x_p = row_yr[col].values[0]
                y_p = row_yr['ln_pib_pc_ppp'].values[0]
                ax.annotate(str(target_yr), (x_p, y_p),
                            textcoords="offset points", xytext=(5, 5),
                            fontsize=8, fontweight='bold', color=colors['dark'])
        
        # Recuadro con coeficiente r y significatividad
        sig_stars = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else " (ns)"))
        stat_box = f"r = {r_val:+.3f}{sig_stars}\np = {p_val:.4f}"
        box_c = colors['emerald'] if r_val > 0.4 else (colors['crimson'] if r_val < -0.4 else '#4b5563')
        ax.text(0.05, 0.92, stat_box, transform=ax.transAxes, fontsize=9.5, fontweight='bold',
                color=box_c, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor=box_c, alpha=0.9))
        
        ax.set_title(title, fontsize=11, color=color_theme)
        ax.set_xlabel("Puntaje WGI", fontsize=9.5)
        ax.set_ylabel("ln(PIBpc PPA)", fontsize=9.5)
    
    # Leyenda compartida para los períodos
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='1996 – 2004 (Primeras Reformas)',
               markerfacecolor='#93c5fd', markeredgecolor='#1e3a8a', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='2005 – 2014 (Boom de Crecimiento)',
               markerfacecolor='#3b82f6', markeredgecolor='#1e3a8a', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='2015 – 2025 (Fase Reciente)',
               markerfacecolor='#1e3a8a', markeredgecolor='#1e3a8a', markersize=8)
    ]
    fig4.legend(handles=legend_elements, loc='lower center', ncol=3, frameon=True,
                facecolor='white', framealpha=0.95, edgecolor='#d1d5db', bbox_to_anchor=(0.5, -0.02))
    
    fig4.suptitle("India: Dispersión y Correlación entre Dimensiones de Gobernabilidad y PIB per cápita",
                  fontsize=13.5, y=0.99)
    fig4.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig4.savefig(os.path.join(fig_dir, "grafico4_panel_dispersion_instituciones_pib.png"), dpi=300, bbox_inches='tight')
    fig4.savefig(os.path.join(fig_dir, "grafico4_panel_dispersion_instituciones_pib.pdf"), bbox_inches='tight')
    plt.close(fig4)
    
    # =========================================================================
    # GRÁFICO 5: HUELLA ECOLÓGICA TOTAL VS BIOCAPACIDAD TOTAL (1961 - 2025)
    # =========================================================================
    print("Generando Gráfico 5: Huella Ecológica Total vs Biocapacidad Total con Déficit...")
    fig5, ax5 = plt.subplots(figsize=(11, 6.2), dpi=300)
    
    ef_series = df_env['huella_ecologica_total_gha_pc']
    bc_series = df_env['biocapacidad_total_gha_pc']
    years_env = df_env['year']
    
    # Líneas principales
    ax5.plot(years_env, ef_series, color='#dc2626', linewidth=2.8,
             label='Huella Ecológica Total (gha per cápita)', zorder=4)
    ax5.plot(years_env, bc_series, color='#15803d', linewidth=2.8,
             label='Biocapacidad Total (gha per cápita)', zorder=4)
    
    # Sombreado coloreado del Déficit Ecológico entre ambas líneas
    ax5.fill_between(years_env, bc_series, ef_series, where=(ef_series >= bc_series),
                     color='#f87171', alpha=0.38, interpolate=True, zorder=3,
                     label='Déficit Ecológico (Huella > Biocapacidad)')
    
    ax5.set_title("India: Huella Ecológica Total vs. Biocapacidad Total per cápita (1961–2025)", pad=15)
    ax5.set_xlabel("Año", labelpad=8)
    ax5.set_ylabel("Hectáreas Globales per cápita (gha/persona)", labelpad=8)
    ax5.set_xlim(1960, 2027)
    ax5.set_ylim(0.2, 1.35)
    ax5.set_xticks(range(1965, 2030, 10))
    ax5.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#d1d5db')
    
    fig5.tight_layout()
    fig5.savefig(os.path.join(fig_dir, "grafico5_huella_ecologica_vs_biocapacidad.png"), dpi=300)
    fig5.savefig(os.path.join(fig_dir, "grafico5_huella_ecologica_vs_biocapacidad.pdf"))
    plt.close(fig5)
    
    # =========================================================================
    # GRÁFICO 6: COMPOSICIÓN DE LA HUELLA ECOLÓGICA DE INDIA (1961 - 2025)
    # =========================================================================
    print("Generando Gráfico 6: Composición de la Huella Ecológica...")
    fig6, ax6 = plt.subplots(figsize=(10.5, 6), dpi=300)
    
    components = [
        ('huella_carbono_gha_pc', 'Huella de Carbono', '#475569'),      # Gris carbón
        ('huella_cultivos_gha_pc', 'Tierras de Cultivo', '#16a34a'),     # Verde campo
        ('huella_bosques_gha_pc', 'Productos Forestales', '#059669'),    # Verde bosque
        ('huella_pastoreo_gha_pc', 'Tierras de Pastoreo', '#d97706'),    # Ocre
        ('huella_pesca_gha_pc', 'Zonas de Pesca', '#0284c7'),            # Azul agua
        ('huella_urbana_gha_pc', 'Suelo Urbanizado', '#9333ea')          # Violeta
    ]
    
    stack_data = [df_env[c[0]] for c in components]
    stack_labels = [c[1] for c in components]
    stack_colors = [c[2] for c in components]
    
    ax6.stackplot(df_env['year'], stack_data, labels=stack_labels, colors=stack_colors, alpha=0.88)
    
    # Línea negra de huella total para referencia nítida
    ax6.plot(df_env['year'], df_env['huella_ecologica_total_gha_pc'], color='#0f172a',
             linewidth=2.0, linestyle='-', label='Huella Ecológica Total')
    
    ax6.set_title("India: Descomposición de la Huella Ecológica de Consumo (1961–2025)", pad=15)
    ax6.set_xlabel("Año", labelpad=8)
    ax6.set_ylabel("Hectáreas Globales per cápita (gha/persona)", labelpad=8)
    ax6.set_xlim(1961, 2025)
    ax6.set_ylim(0, 1.35)
    ax6.set_xticks(range(1965, 2030, 10))
    ax6.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.92, edgecolor='#d1d5db')
    
    fig6.tight_layout()
    fig6.savefig(os.path.join(fig_dir, "grafico6_composicion_huella_ecologica.png"), dpi=300)
    fig6.savefig(os.path.join(fig_dir, "grafico6_composicion_huella_ecologica.pdf"))
    plt.close(fig6)
    
    print("\nTodos los gráficos fueron compilados exitosamente en output/figures/ (PNG y PDF).")

if __name__ == "__main__":
    main()
