"""Tres gráficos simples del crecimiento total y natural de India."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/figures'
BLUE, ORANGE = '#3569a6', '#d77b36'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (ROOT / 'data/processed/main_punto_1.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = [r for r in csv.DictReader(f, delimiter=';') if r['pais'] == 'IND']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.spines.left': False, 'axes.edgecolor': '#cccccc',
                         'xtick.color': '#626262', 'ytick.color': '#626262',
                         'figure.facecolor': 'white', 'savefig.facecolor': 'white', 'pdf.fonttype': 42})
    total, natural = 'crecimiento_poblacional_pct_anual', 'crecimiento_natural_pct_anual'
    charts = [
        ('01_crecimiento_poblacional_total', 'India · Crecimiento poblacional total', [(total, 'Total', BLUE)]),
        ('02_crecimiento_poblacional_natural', 'India · Crecimiento poblacional natural', [(natural, 'Natural', ORANGE)]),
        ('03_crecimiento_total_y_natural', 'India · Crecimiento poblacional total y natural',
         [(total, 'Crecimiento total', BLUE), (natural, 'Crecimiento natural', ORANGE)]),
    ]
    for name, title, series in charts:
        fig, ax = plt.subplots(figsize=(10.5, 5.8))
        fig.subplots_adjust(left=.10, right=.95, top=.85, bottom=.18 if len(series) == 2 else .12)
        fig.text(.10, .94, title, size=16, weight='bold', ha='left')
        # En el gráfico conjunto se usa solo la ventana común, 1961–2024.
        selected = [r for r in rows if all(r[key] for key, _, _ in series)]
        for key, label, color in series:
            ax.plot([int(r['anio']) for r in selected], [float(r[key].replace(',', '.')) for r in selected],
                    lw=2.3, color=color, label=label)
        ax.set(xlim=(1960, 2025), ylim=(0, 3), ylabel='Tasa anual (%)')
        ax.set_xticks([1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025])
        ax.yaxis.set_major_locator(MultipleLocator(.5))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{value:g}'.replace('.', ',')))
        ax.tick_params(axis='both', length=0, pad=9)
        ax.grid(axis='y', color='#e6e6e6', lw=.7)
        ax.set_axisbelow(True)
        if len(series) == 2:
            fig.legend(loc='lower left', bbox_to_anchor=(.09, .045), frameon=False,
                       ncol=2, handlelength=2.5, columnspacing=3)
        for extension in ['png', 'pdf']:
            fig.savefig(OUT / f'{name}.{extension}', dpi=220)
        plt.close(fig)
        print(f'{name}: {selected[0]["anio"]}–{selected[-1]["anio"]}, {len(selected)} observaciones')


if __name__ == '__main__':
    main()
