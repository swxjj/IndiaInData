"""Esquema conceptual de cuatro etapas y evolución observada de India.

La posición de India es interpretativa, no una clasificación oficial ni una
datación de las etapas. Las curvas del esquema no son datos ni proyecciones.
"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/figures'
BIRTH, DEATH, NATURAL = '#d77b36', '#318276', '#3569a6'
INK, GRAY = '#262d35', '#737b83'


def save(fig, name):
    for extension in ['png', 'pdf']:
        fig.savefig(OUT / f'{name}.{extension}', dpi=220, facecolor='white')
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (ROOT / 'data/processed/main_punto_1.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = [r for r in csv.DictReader(f, delimiter=';') if r['pais'] == 'IND'
                and r['natalidad_por_mil'] and r['mortalidad_por_mil']]
    latest = max(rows, key=lambda r: int(r['anio']))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'xtick.color': GRAY, 'ytick.color': GRAY,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.facecolor': 'white', 'pdf.fonttype': 42})

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.subplots_adjust(left=.07, right=.97, top=.76, bottom=.23)
    fig.text(.07, .94, 'Transición demográfica y ubicación de India', fontsize=20, weight='bold')
    labels = [
        ('Etapa 1', 'Tasas altas', '#f1f2f4'),
        ('Etapa 2', 'Desciende la mortalidad', '#eaf1f8'),
        ('Etapa 3', 'Desciende la natalidad', '#eaf4ef'),
        ('Etapa 4', 'Tasas bajas', '#fbf1e8'),
    ]
    for i, (title, description, color) in enumerate(labels):
        ax.axvspan(i, i + 1, color=color, zorder=0)
        ax.text((i + .5)/4, 1.15, title, transform=ax.transAxes,
                ha='center', fontsize=13, weight='bold')
        ax.text((i + .5)/4, 1.075, description, transform=ax.transAxes,
                ha='center', fontsize=10, color=GRAY)
        if i:
            ax.axvline(i, color='#bbc3c9', ls=(0, (2, 4)), lw=1, zorder=1)
    x = np.linspace(0, 4, 700)
    birth = .19 + .76/(1 + np.exp(2.8*(x - 2.35)))
    death = .145 + .77/(1 + np.exp(4.0*(x - 1.22)))
    natural = birth - death
    ax.plot(x, birth, color=BIRTH, lw=3, label='Natalidad')
    ax.plot(x, death, color=DEATH, lw=3, label='Mortalidad')
    ax.plot(x, natural, color=NATURAL, lw=3, label='Crecimiento natural')
    ax.set(xlim=(0, 4), ylim=(0, 1.03), xticks=[], yticks=[])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.annotate('', xy=(4.04, -.015), xytext=(0, -.015),
                arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.2), annotation_clip=False)
    ax.text(4.02, -.075, 'Avance de la transición', ha='right', fontsize=9, color=GRAY)
    ax.text(0, -.075, 'Esquema conceptual · sin escala temporal', fontsize=9, color=GRAY)
    # Franja de ubicación aproximada, deliberadamente sin fecha de corte de etapa.
    ax.axvspan(2.72, 3.08, facecolor='#bfc9ce', alpha=.20, zorder=1)
    ax.annotate('India\nEtapa 3 avanzada → 4', xy=(2.90, .25), xytext=(3.38, .62),
                ha='center', fontsize=12, weight='bold',
                arrowprops=dict(arrowstyle='->', color=INK, lw=1.2, connectionstyle='arc3,rad=.12'))
    fig.legend(loc='lower left', bbox_to_anchor=(.06, .08), ncol=3,
               frameon=False, handlelength=2.6, columnspacing=2.6)
    fig.text(.07, .035, 'Ubicación aproximada en el modelo de cuatro etapas; existen diferencias entre regiones de India.',
             fontsize=9, color=GRAY)
    save(fig, '04_transicion_demografica_esquema')

    # Evidencia observada: las tres tasas se expresan por mil y comparten eje.
    years = [int(r['anio']) for r in rows]
    birth_data = [float(r['natalidad_por_mil'].replace(',', '.')) for r in rows]
    death_data = [float(r['mortalidad_por_mil'].replace(',', '.')) for r in rows]
    natural_data = [b - d for b, d in zip(birth_data, death_data)]
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.subplots_adjust(left=.10, right=.87, top=.84, bottom=.18)
    fig.text(.10, .94, 'India · Transición demográfica observada', fontsize=18, weight='bold')
    for values, label, color in [(birth_data, 'Natalidad', BIRTH), (death_data, 'Mortalidad', DEATH),
                                  (natural_data, 'Crecimiento natural', NATURAL)]:
        ax.plot(years, values, color=color, lw=2.4, label=label)
        ax.scatter(years[-1], values[-1], color=color, s=20, zorder=5)
        ax.annotate(f'{values[-1]:.1f}‰'.replace('.', ','), (years[-1], values[-1]),
                    xytext=(8, 0), textcoords='offset points', va='center', color=color, fontsize=10)
    ax.set(xlim=(1960, 2025), ylim=(0, 45), ylabel='Tasa anual por 1.000 habitantes')
    ax.set_xticks([1960, 1970, 1980, 1990, 2000, 2010, 2020, 2024])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{value:g}'.replace('.', ',')))
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    ax.tick_params(length=0, pad=8)
    ax.grid(axis='y', color='#e6e6e6', lw=.7)
    ax.set_axisbelow(True)
    fig.legend(loc='lower left', bbox_to_anchor=(.09, .045), ncol=3, frameon=False,
               handlelength=2.6, columnspacing=2.5)
    save(fig, '05_transicion_demografica_datos_india')
    evidence = dict(anio=int(latest['anio']), natalidad_por_mil=birth_data[-1],
                    mortalidad_por_mil=death_data[-1], crecimiento_natural_por_mil=natural_data[-1],
                    fecundidad=float(latest['fecundidad'].replace(',', '.')),
                    interpretacion='Etapa 3 avanzada hacia etapa 4, en un esquema de cuatro etapas; no es una clasificación oficial',
                    esquema='Curvas ilustrativas sin escala temporal; no son observaciones ni proyecciones',
                    datos='Banco Mundial, WDI; main_punto_1.csv',
                    referencias=[
                        'https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2022_global_population_growth.pdf',
                        'https://india.unfpa.org/en/publications/reimagining-family-planning-india-new-pathways'])
    (ROOT / 'output/transicion_demografica_notas.json').write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
