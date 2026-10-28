"""Reemplaza tres gráficos de Excel de la resolución sin editar sus bases."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/figures'


def number(v):
    return float(v.replace(',', '.')) if v else float('nan')


def style(ax, unit):
    ax.set_ylabel(unit)
    ax.grid(axis='y', color='#e6e6e6', lw=.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:g}'.replace('.', ',')))


def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=220, facecolor='white')
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.spines.left': False, 'axes.edgecolor': '#cccccc',
                         'figure.facecolor': 'white', 'pdf.fonttype': 42})
    # La captura original muestra una razón (no el porcentaje WDI).
    with (ROOT/'data/processed/main_punto_1.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = [r for r in csv.DictReader(f, delimiter=';') if r['pais'] == 'IND']
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    fig.subplots_adjust(left=.10, right=.96, top=.83, bottom=.13)
    fig.text(.10, .94, 'India · Índice de dependencia demográfica', size=17, weight='bold')
    values = [number(r['dependencia_total_wdi']) / 100 for r in rows]
    ax.plot([int(r['anio']) for r in rows], values, color='#3569a6', lw=2.4)
    ax.set(xlim=(1960, 2025), ylim=(0, .9))
    ax.set_xticks([1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025])
    ax.yaxis.set_major_locator(MultipleLocator(.1))
    style(ax, 'Dependientes por persona de 15–64 años')
    save(fig, '06_indice_dependencia_india')

    # El gráfico de remesas utiliza únicamente las observaciones de India.
    wb = load_workbook(ROOT/'data/processed/punto2 exc.xlsx', read_only=True, data_only=True)
    data = list(wb.active.values)
    rows = [dict(zip(data[0], row)) for row in data[1:] if row[0]]
    wb.close()
    specs = [('remesas_recibidas_pct_pib_wdi', 'Remesas recibidas', '#3569a6'),
             ('exportaciones_pct_pib_wdi', 'Exportaciones de bienes y servicios', '#d77b36'),
             ('ied_entrada_neta_pct_pib_wdi', 'Inversión extranjera directa recibida', '#737b83')]
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    fig.subplots_adjust(left=.10, right=.96, top=.82, bottom=.22)
    fig.text(.10, .94, 'India · Remesas, exportaciones e inversión extranjera directa', size=15, weight='bold')
    subset = [r for r in rows if r['pais'] == 'IND']
    for key, label, color in specs:
        ax.plot([int(r['anio']) for r in subset],
                [float(r[key]) if isinstance(r[key], (int, float)) else float('nan') for r in subset],
                lw=2.1, color=color, label=label)
    ax.set(xlim=(1960, 2025), ylim=(-2, 30))
    ax.set_xticks([1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025])
    style(ax, '% del PIB')
    fig.legend(*ax.get_legend_handles_labels(), loc='lower left', bbox_to_anchor=(.09, .045),
               ncol=3, frameon=False, fontsize=8, columnspacing=1.3)
    save(fig, '07_remesas_exportaciones_ied')

    payload = (ROOT/'data/raw/HDR25_Composite_indices_complete_time_series.csv').read_bytes()
    try:
        text = payload.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = payload.decode('cp1252')
    countries = {r['iso3']: r for r in csv.DictReader(text.splitlines())}
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    fig.subplots_adjust(left=.10, right=.96, top=.83, bottom=.20)
    fig.text(.10, .94, 'Evolución del índice de desigualdad de género', size=17, weight='bold')
    for code, name, color in [('ARG', 'Argentina', '#57a2c6'), ('IND', 'India', '#d77b36'),
                               ('PAK', 'Pakistán', '#888888'), ('SWE', 'Suecia', '#b7a531'),
                               ('USA', 'Estados Unidos', '#3569a6')]:
        ax.plot(range(1990, 2024), [number(countries[code].get(f'gii_{y}', '')) for y in range(1990, 2024)],
                lw=2.4 if code == 'IND' else 1.9, label=name, color=color)
    ax.set(xlim=(1990, 2023), ylim=(0, .9))
    ax.set_xticks([1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023])
    style(ax, 'GII (0–1)')
    fig.legend(loc='lower left', bbox_to_anchor=(.09, .045), ncol=5, frameon=False,
               fontsize=9, columnspacing=1.8)
    save(fig, '08_gii_comparacion_paises')
    print('Generadas las tres figuras faltantes en PNG y PDF.')


if __name__ == '__main__':
    main()
