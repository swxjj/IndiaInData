import os
import csv
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless / script generation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ==============================================================================
# GLOBAL DESIGN SYSTEM (Enfoque A: Identidad Fija por País en Español)
# ==============================================================================
STYLE = {
    'IND': {
        'color': '#C0392B',       # Terracota / Rojo Institucional
        'color_alt': '#78281F',   # Variante oscura para etiquetas
        'marker': 'o',            # Círculo
        'label': 'India'
    },
    'USA': {
        'color': '#1B4F72',       # Azul Marino / Deep Navy
        'color_alt': '#154360',   # Variante oscura para etiquetas
        'marker': 's',            # Cuadrado
        'label': 'Estados Unidos'
    },
    'ARG': {
        'color': '#2980B9',       # Celeste / Acero
        'marker': '^',            # Triángulo
        'label': 'Argentina'
    },
    'NEUTRAL': {
        'grid': '#E5E7E9',
        'subtle_line': '#7F8C8D',
        'complementary': '#2C3E50' # Gris pizarra oscuro para 2da variable
    }
}

def load_data(filepath=None):
    if filepath is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tp1_dir = os.path.dirname(os.path.dirname(script_dir))
        filepath = os.path.join(tp1_dir, "data", "processed", "macro_panel_india_usa.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    ind_data = []
    usa_data = []
    
    for r in rows:
        def parse_val(v):
            return float(v) if v and v.strip() else None
            
        entry = {
            'year': int(r['year']),
            'gdp_const': parse_val(r['gdp_pcap_constant_2015_usd']),
            'gdp_ppp': parse_val(r['gdp_pcap_ppp_constant_2021']),
            'hdi': parse_val(r['hdi']),
            'ladder': parse_val(r['cantril_ladder'])
        }
        if r['country_iso'] == 'IND':
            ind_data.append(entry)
        elif r['country_iso'] == 'USA':
            usa_data.append(entry)
            
    return ind_data, usa_data

def setup_academic_style():
    plt.rcParams.update({
        'font.size': 11,
        'font.family': 'sans-serif',
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'axes.titleweight': 'bold',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 13,
        'figure.dpi': 300,
        'axes.linewidth': 0.8,
        'grid.linewidth': 0.6,
        'grid.alpha': 0.45,
        'grid.linestyle': '--',
        'lines.linewidth': 2.2,
        'lines.markersize': 5.5,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1
    })

def plot_01_hdi_india_vs_usa(ind_data, usa_data, out_dir):
    """
    Gráfico 1: IDH: INDIA VS ESTADOS UNIDOS
    """
    ind_valid = [(d['year'], d['hdi']) for d in ind_data if d['hdi'] is not None]
    usa_valid = [(d['year'], d['hdi']) for d in usa_data if d['hdi'] is not None]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Líneas según el Sistema de Diseño
    ax.plot([x[0] for x in ind_valid], [x[1] for x in ind_valid], 
            color=STYLE['IND']['color'], marker=STYLE['IND']['marker'], 
            label=STYLE['IND']['label'], zorder=4)
            
    ax.plot([x[0] for x in usa_valid], [x[1] for x in usa_valid], 
            color=STYLE['USA']['color'], marker=STYLE['USA']['marker'], 
            label=STYLE['USA']['label'], zorder=4)
    
    # Umbrales metodológicos del PNUD
    ax.axhline(0.80, color='gray', linestyle=':', alpha=0.6, linewidth=0.9, zorder=2)
    ax.text(1990.5, 0.805, 'Desarrollo Humano Muy Alto (0,80)', fontsize=8.5, color='#555555', fontstyle='italic')
    
    ax.axhline(0.55, color='gray', linestyle=':', alpha=0.6, linewidth=0.9, zorder=2)
    ax.text(1990.5, 0.555, 'Desarrollo Humano Medio (0,55)', fontsize=8.5, color='#555555', fontstyle='italic')
    
    # Etiquetas finales
    ax.annotate(f"IND: {ind_valid[-1][1]:.3f}".replace('.', ','), (ind_valid[-1][0], ind_valid[-1][1]),
                xytext=(6, -2), textcoords='offset points', fontweight='bold', color=STYLE['IND']['color'], fontsize=9.5)
    ax.annotate(f"EE.UU.: {usa_valid[-1][1]:.3f}".replace('.', ','), (usa_valid[-1][0], usa_valid[-1][1]),
                xytext=(6, -2), textcoords='offset points', fontweight='bold', color=STYLE['USA']['color'], fontsize=9.5)

    ax.set_title("Índice de Desarrollo Humano (IDH): India vs. Estados Unidos (1990–2023)", pad=14)
    ax.set_xlabel("Año")
    ax.set_ylabel("Índice de Desarrollo Humano (Escala 0 a 1)")
    ax.set_ylim(0.35, 1.0)
    ax.set_xlim(1989, 2026)
    ax.grid(True)
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.figtext(0.12, -0.02, "Fuente: Oficina del Informe sobre Desarrollo Humano del PNUD vía Our World in Data (1990–2023).", 
                fontsize=8.5, color='#555555')
    
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(out_dir, f"01_hdi_india_vs_usa.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Guardado 01_hdi_india_vs_usa (Español)")

def plot_02_gdp_india_vs_usa(ind_data, usa_data, out_dir):
    """
    Gráfico 2: PIB: INDIA VS ESTADOS UNIDOS (Doble Eje con Identidad Fija por País)
    """
    ind_valid = [(d['year'], d['gdp_const']) for d in ind_data if d['gdp_const'] is not None]
    usa_valid = [(d['year'], d['gdp_const']) for d in usa_data if d['gdp_const'] is not None]
    
    fig, ax1 = plt.subplots(figsize=(8.5, 5))
    ax2 = ax1.twinx()  # Eje secundario para India
    
    c_usa = STYLE['USA']['color']
    c_ind = STYLE['IND']['color']
    
    # EE.UU. en Eje Izquierdo
    l1 = ax1.plot([x[0] for x in usa_valid], [x[1] for x in usa_valid], 
                  color=c_usa, marker=STYLE['USA']['marker'], markevery=5,
                  label='Estados Unidos (Eje izquierdo)', zorder=3)
    ax1.set_ylabel("EE.UU.: PIB real per cápita (USD constantes de 2015)", color=c_usa, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=c_usa)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"US$ {x:,.0f}".replace(',', '.')))
    ax1.set_ylim(0, 80000)
    
    # India en Eje Derecho
    l2 = ax2.plot([x[0] for x in ind_valid], [x[1] for x in ind_valid], 
                  color=c_ind, marker=STYLE['IND']['marker'], markevery=5,
                  label='India (Eje derecho)', zorder=4)
    ax2.set_ylabel("India: PIB real per cápita (USD constantes de 2015)", color=c_ind, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=c_ind)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"US$ {x:,.0f}".replace(',', '.')))
    ax2.set_ylim(0, 3000)
    
    ax1.set_title("Trayectorias del PIB Real per Cápita: India vs. Estados Unidos (1960–2025)", pad=14)
    ax1.set_xlabel("Año")
    ax1.set_xlim(1959, 2026)
    ax1.grid(True)
    
    # Leyenda combinada
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.figtext(0.12, -0.02, "Fuente: Banco Mundial WDI (indicador NY.GDP.PCAP.KD). Nota: Se emplea doble eje Y debido a diferencias estructurales de escala.", 
                fontsize=8.5, color='#555555')
    
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(out_dir, f"02_gdp_india_vs_usa.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Guardado 02_gdp_india_vs_usa (Español)")

def plot_03_happiness_india_vs_usa(ind_data, usa_data, out_dir):
    """
    Gráfico 3: FELICIDAD: INDIA VS ESTADOS UNIDOS (Escalera de Cantril)
    """
    ind_valid = [(d['year'], d['ladder']) for d in ind_data if d['ladder'] is not None]
    usa_valid = [(d['year'], d['ladder']) for d in usa_data if d['ladder'] is not None]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    ax.plot([x[0] for x in ind_valid], [x[1] for x in ind_valid], 
            color=STYLE['IND']['color'], marker=STYLE['IND']['marker'], 
            label=STYLE['IND']['label'], zorder=4)
            
    ax.plot([x[0] for x in usa_valid], [x[1] for x in usa_valid], 
            color=STYLE['USA']['color'], marker=STYLE['USA']['marker'], 
            label=STYLE['USA']['label'], zorder=4)
    
    # Anotaciones finales
    if ind_valid:
        ax.annotate(f"IND: {ind_valid[-1][1]:.2f}".replace('.', ','), (ind_valid[-1][0], ind_valid[-1][1]),
                    xytext=(6, -2), textcoords='offset points', fontweight='bold', color=STYLE['IND']['color'], fontsize=9.5)
    if usa_valid:
        ax.annotate(f"EE.UU.: {usa_valid[-1][1]:.2f}".replace('.', ','), (usa_valid[-1][0], usa_valid[-1][1]),
                    xytext=(6, -2), textcoords='offset points', fontweight='bold', color=STYLE['USA']['color'], fontsize=9.5)

    ax.set_title("Satisfacción de Vida Autopercibida: India vs. Estados Unidos (2011–2025)", pad=14)
    ax.set_xlabel("Año")
    ax.set_ylabel("Satisfacción de Vida Autopercibida (Escala 0 a 10)")
    ax.set_ylim(3.0, 8.5)
    ax.set_xlim(2010.5, 2026.5)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.figtext(0.12, -0.02, "Fuente: Encuesta Mundial de Gallup / Informe Mundial de la Felicidad vía Our World in Data (2011–2025).", 
                fontsize=8.5, color='#555555')
    
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(out_dir, f"03_happiness_india_vs_usa.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Guardado 03_happiness_india_vs_usa (Español)")

def plot_04_happiness_india(ind_data, out_dir):
    """
    Gráfico 4: FELICIDAD: INDIA (Serie individual de bienestar subjetivo)
    """
    ind_valid = [(d['year'], d['ladder']) for d in ind_data if d['ladder'] is not None]
    
    years = [x[0] for x in ind_valid]
    scores = [x[1] for x in ind_valid]
    
    fig, ax = plt.subplots(figsize=(8, 4.8))
    
    ax.plot(years, scores, color=STYLE['IND']['color'], marker=STYLE['IND']['marker'], 
            markersize=6.5, label='Satisfacción de vida autopercibida', zorder=4)
        
    for y, s in zip(years, scores):
        if y in [2011, 2015, 2019, 2025]:
            offset_y = -14 if y == 2019 else 7
            score_str = f"{s:.2f}".replace('.', ',')
            ax.annotate(score_str, (y, s), xytext=(0, offset_y), textcoords='offset points', 
                        ha='center', fontsize=9, fontweight='bold', color=STYLE['IND']['color_alt'])
            
    ax.set_title("Evolución del Bienestar Subjetivo en India (2011–2025)", pad=14)
    ax.set_xlabel("Año")
    ax.set_ylabel("Satisfacción de Vida Autopercibida (Escala 0 a 10)")
    ax.set_ylim(3.3, 5.3)
    ax.set_xlim(2010.5, 2025.5)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.figtext(0.12, -0.02, "Fuente: Encuesta Mundial de Gallup / Informe Mundial de la Felicidad (2011–2025). Escala: 0 a 10.", 
                fontsize=8.5, color='#555555')
    
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(out_dir, f"04_happiness_india.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Guardado 04_happiness_india (Español)")

def plot_05_hdi_and_gdp_india(ind_data, out_dir):
    """
    Gráfico 5: IDH Y PIB: INDIA (Doble Eje sobre el período máximo 1960-2025)
    """
    hdi_pts = [(d['year'], d['hdi']) for d in ind_data if d['hdi'] is not None]
    gdp_pts = [(d['year'], d['gdp_const']) for d in ind_data if d['gdp_const'] is not None]
    
    fig, ax1 = plt.subplots(figsize=(8.5, 5))
    ax2 = ax1.twinx()
    
    c_hdi = STYLE['IND']['color']          # Rojo Institucional de India para el IDH
    c_gdp = STYLE['NEUTRAL']['complementary'] # Pizarra Oscuro para la serie monetaria
    
    # Eje Izquierdo: IDH (comienza en 1990)
    l1 = ax1.plot([x[0] for x in hdi_pts], [x[1] for x in hdi_pts], 
                  color=c_hdi, marker=STYLE['IND']['marker'], markersize=4.5, 
                  label='Índice de Desarrollo Humano (Eje izq., 1990–2023)', zorder=4)
    ax1.set_ylabel("Índice de Desarrollo Humano (Escala 0 a 1)", color=c_hdi, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=c_hdi)
    ax1.set_ylim(0.30, 0.75)
    
    # Eje Derecho: PIB per cápita (comienza en 1960)
    l2 = ax2.plot([x[0] for x in gdp_pts], [x[1] for x in gdp_pts], 
                  color=c_gdp, linestyle='--', linewidth=2.0, 
                  label='PIB real per cápita (Eje der., 1960–2025)', zorder=3)
    ax2.set_ylabel("PIB real per cápita (USD constantes de 2015)", color=c_gdp, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=c_gdp)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"US$ {x:,.0f}".replace(',', '.')))
    ax2.set_ylim(0, 3000)
    
    ax1.set_title("Crecimiento Económico y Desarrollo Humano en India (1960–2025)", pad=14)
    ax1.set_xlabel("Año")
    ax1.set_xlim(1959, 2026)
    ax1.grid(True)
    
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
    
    plt.figtext(0.12, -0.02, "Fuentes: Banco Mundial WDI (PIB real per cápita en USD de 2015, 1960–2025) y PNUD (IDH, 1990–2023).", 
                fontsize=8.5, color='#555555')
    
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(out_dir, f"05_hdi_and_gdp_india.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Guardado 05_hdi_and_gdp_india (Español)")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generador académico de gráficos macroeconómicos")
    parser.add_argument(
        "--chart", "-c", nargs="+", default=["all"],
        help="Número o lista de gráficos a generar (1, 2, 3, 4, 5) o 'all' para todos."
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    tp1_dir = os.path.dirname(os.path.dirname(script_dir))
    out_dir = os.path.join(tp1_dir, "output", "figures")
    os.makedirs(out_dir, exist_ok=True)
    setup_academic_style()
    ind_data, usa_data = load_data()
    
    selected = [str(x).lower() for x in args.chart]
    run_all = "all" in selected

    chart_map = {
        "1": ("01_hdi_india_vs_usa", lambda: plot_01_hdi_india_vs_usa(ind_data, usa_data, out_dir)),
        "2": ("02_gdp_india_vs_usa", lambda: plot_02_gdp_india_vs_usa(ind_data, usa_data, out_dir)),
        "3": ("03_happiness_india_vs_usa", lambda: plot_03_happiness_india_vs_usa(ind_data, usa_data, out_dir)),
        "4": ("04_happiness_india", lambda: plot_04_happiness_india(ind_data, out_dir)),
        "5": ("05_hdi_and_gdp_india", lambda: plot_05_hdi_and_gdp_india(ind_data, out_dir))
    }

    if run_all:
        print("Generando TODOS los gráficos académicos en output/figures/...")
        for num, (name, fn) in chart_map.items():
            fn()
    else:
        for num in selected:
            if num in chart_map:
                chart_map[num][1]()
            else:
                print(f"Advertencia: Gráfico '{num}' no reconocido. Opciones válidas: 1, 2, 3, 4, 5 o all.")

if __name__ == "__main__":
    main()
