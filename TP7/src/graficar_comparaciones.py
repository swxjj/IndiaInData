"""Reproduce las dos comparaciones del TP7 con ejes anuales y diseño simple.

El gasto y la matrícula faltantes se completan con la variación absoluta media anual entre
observaciones vecinas (interpolación lineal interna). No modifica las bases.
"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE = '#3569a6', '#d77b36'


def read(name):
    with (ROOT / 'data/processed' / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def number(value):
    return float(value.replace(',', '.')) if value else float('nan')


def decimal(value, _):
    return f'{value:g}'.replace('.', ',')


plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.left': False,
    'axes.spines.right': False, 'axes.edgecolor': '#cccccc',
    'axes.titleweight': 'bold', 'axes.titlesize': 16,
    'xtick.color': '#626262', 'ytick.color': '#626262',
    'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'pdf.fonttype': 42,
})


def canvas(title):
    fig, left = plt.subplots(figsize=(10.5, 5.8))
    fig.subplots_adjust(left=.10, right=.89, top=.85, bottom=.18)
    right = left.twinx()
    fig.text(.10, .94, title, size=17, weight='bold', ha='left')
    for ax in (left, right):
        ax.tick_params(axis='both', length=0, pad=9)
        ax.yaxis.set_major_formatter(FuncFormatter(decimal))
    left.grid(axis='y', color='#e6e6e6', lw=.7)
    left.set_axisbelow(True)
    left.xaxis.set_major_locator(MultipleLocator(5))
    return fig, left, right


def save(fig, name, handles):
    fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(.09, .045),
               frameon=False, ncol=2, handlelength=2.5, columnspacing=3, fontsize=10)
    for suffix in ('png', 'pdf'):
        fig.savefig(OUT / f'{name}.{suffix}', dpi=220)
    plt.close(fig)


def main():
    rows = [r for r in read('educacion_india_anual.csv') if 1997 <= int(r['anio']) <= 2022]
    years = [int(r['anio']) for r in rows]
    # Guardar explícitamente qué datos se completaron y con qué fórmula.
    observed = {int(r['anio']): number(r['gasto_educativo_pib'])
                for r in rows if r['gasto_educativo_pib']}
    complete = dict(observed)
    audit = []
    for year in years:
        if year not in observed:
            previous = max(y for y in observed if y < year)
            following = min(y for y in observed if y > year)
            increment = (observed[following] - observed[previous]) / (following - previous)
            complete[year] = observed[previous] + (year - previous) * increment
            audit.append({'anio': year, 'gasto_educativo_pib_estimado': complete[year],
                          'anio_anterior': previous, 'anio_siguiente': following,
                          'variacion_media_anual_pp': increment})
    fig, left, right = canvas('Gasto educativo y matrícula primaria')
    enrollment_observed = {int(r['anio']): number(r['matricula_bruta_primaria'])
                           for r in rows if r['matricula_bruta_primaria']}
    enrollment_complete = dict(enrollment_observed)
    enrollment_audit = []
    for year in years:
        if year not in enrollment_observed:
            previous = max(y for y in enrollment_observed if y < year)
            following = min(y for y in enrollment_observed if y > year)
            increment = (enrollment_observed[following] - enrollment_observed[previous]) / (following - previous)
            enrollment_complete[year] = enrollment_observed[previous] + (year - previous) * increment
            enrollment_audit.append({'anio': year, 'matricula_bruta_primaria_estimada': enrollment_complete[year],
                                     'anio_anterior': previous, 'anio_siguiente': following,
                                     'variacion_media_anual_pp': increment})
    for first, last in zip(years[:-1], years[1:]):
        left.plot([first, last], [enrollment_complete[first], enrollment_complete[last]],
                  color=BLUE, lw=2.3,
                  linestyle='-' if first in enrollment_observed and last in enrollment_observed else (0, (2, 2)))
    # Segmentos estimados punteados, incluidos sus extremos observados.
    for first, last in zip(years[:-1], years[1:]):
        right.plot([first, last], [complete[first], complete[last]], color=ORANGE, lw=2.3,
                   linestyle='-' if first in observed and last in observed else (0, (2, 2)))
    from matplotlib.lines import Line2D
    enrollment = Line2D([], [], color=BLUE, lw=2.3, label='Matrícula bruta primaria')
    spending = Line2D([], [], color=ORANGE, lw=2.3, label='Gasto educativo')
    left.set(xlim=(1996.5, 2022.5), ylim=(85, 120))
    left.set_xticks([1997, 2000, 2005, 2010, 2015, 2020, 2022])
    right.set(ylim=(3, 4.8))
    right.yaxis.set_major_locator(MultipleLocator(.3))
    save(fig, '07_gasto_matricula_comparacion', [enrollment, spending])

    pnud = read('complemento_pnud_escolaridad_india.csv')
    years = [int(r['anio']) for r in pnud]
    fig, left, right = canvas('PIB por habitante y años de escolaridad')
    gdp, = left.plot(years, [number(r['pib_pc_usd_2015']) for r in pnud],
                     color=ORANGE, lw=2.3, label='PIB por habitante')
    schooling, = right.plot(years, [number(r['escolaridad_25_pnud']) for r in pnud],
                            color=BLUE, lw=2.3, label='Años de escolaridad')
    left.set(xlim=(1989.5, 2023.5), ylim=(0, 2500))
    left.set_xticks([1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023])
    left.yaxis.set_major_locator(MultipleLocator(500))
    left.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'.replace(',', '.')))
    right.set(ylim=(0, 8))
    right.yaxis.set_major_locator(MultipleLocator(2))
    save(fig, '08_pib_escolaridad_comparacion', [gdp, schooling])
    audit_path = ROOT / 'output' / 'gasto_estimaciones_comparacion.json'
    audit_path.write_text(json.dumps({'metodo': 'Variación absoluta media anual entre observaciones vecinas; interpolación lineal interna',
                                      'unidad_gasto': '% del PIB', 'estimaciones': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'output' / 'matricula_estimaciones_comparacion.json').write_text(
        json.dumps({'metodo': 'Variación absoluta media anual entre observaciones vecinas; interpolación lineal interna',
                    'unidad_matricula': '%', 'estimaciones': enrollment_audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    print('Guardados: 07_gasto_matricula_comparacion y 08_pib_escolaridad_comparacion (PNG y PDF).')


if __name__ == '__main__':
    main()
