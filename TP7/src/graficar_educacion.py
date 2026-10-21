"""Gráficos exploratorios del ejercicio 1, a partir de los CSV locales."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
D = pd.read_csv(ROOT / 'data/processed/educacion_india_anual.csv', sep=';', decimal=',').set_index('anio')
P = pd.read_csv(ROOT / 'data/processed/complemento_pnud_escolaridad_india.csv', sep=';', decimal=',').set_index('anio')
BLUE, ORANGE, GREEN = '#245c83', '#bc602e', '#318276'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.titleweight': 'bold', 'axes.labelcolor': '#333333',
                     'axes.titlesize': 11, 'figure.facecolor': 'white',
                     'savefig.facecolor': 'white', 'pdf.fonttype': 42})
FILES = []


def style(ax, ylabel):
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Año')
    ax.grid(axis='y', alpha=.18)
    ax.set_axisbelow(True)


def series(ax, data, key, label=None, color=BLUE):
    # Los NaN cortan la línea: no unir tramos separados por años sin datos.
    ax.plot(data.index, data[key], color=color, lw=1.8, marker='o', ms=3, label=label)


def save(fig, name, title, note, source='Banco Mundial, WDI y EdStats. Descarga: 21/10/2026.'):
    fig.suptitle(title, x=.07, ha='left', fontsize=16, weight='bold', y=.98)
    fig.text(.07, .075, note, fontsize=9, color='#444444', va='top')
    fig.text(.07, .025, 'Fuente: ' + source, fontsize=8, color='#666666')
    fig.tight_layout(rect=(.025, .14, .99, .90), w_pad=3)
    for ext in ['png', 'pdf']:
        fig.savefig(OUT / f'{name}.{ext}', dpi=180)
    FILES.append(OUT / f'{name}.png')
    plt.close(fig)


fig, ax = plt.subplots(1, 2, figsize=(12, 5))
series(ax[0], D, 'pib_pc_usd_2015')
style(ax[0], 'US$ constantes de 2015')
ax[0].set_title('PIB por habitante · 1960–2025')
s = D.escolaridad_25_total.dropna()
ax[1].scatter(s.index, s, color=ORANGE, s=65)
for y, v in s.items():
    ax[1].annotate(f'{y}: {v:.2f}', (y, v), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=9)
ax[1].set(xlim=(1960, 2025), ylim=(0, 6.5), title='Escolaridad EdStats · variable de la consigna')
style(ax[1], 'Años completados · población de 25+')
save(fig, '01_pib_escolaridad_edstats', 'India | PIB y escolaridad solicitada',
     'Escolaridad: solo 1971, 1981 y 2011. Se muestran puntos sin interpolar los años faltantes.')

fig, ax = plt.subplots(1, 3, figsize=(15, 5.2))
series(ax[0], P, 'pib_pc_usd_2015')
style(ax[0], 'US$ constantes de 2015')
ax[0].set_title('PIB por habitante')
series(ax[1], P, 'escolaridad_25_pnud', color=ORANGE)
style(ax[1], 'Años completados · población de 25+')
ax[1].set_title('Escolaridad · complemento PNUD')
ax[2].scatter(P.escolaridad_25_pnud, P.pib_pc_usd_2015, c=P.index, cmap='viridis', s=28)
for year, offset in [(1990, (6, -8)), (2000, (6, -8)), (2010, (6, -8)), (2023, (-36, 6))]:
    row = P.loc[year]
    ax[2].annotate(str(year), (row.escolaridad_25_pnud, row.pib_pc_usd_2015), xytext=offset,
                   textcoords='offset points', fontsize=9)
style(ax[2], 'PIB por habitante · US$ de 2015')
ax[2].set_xlabel('Escolaridad media · años')
ax[2].set_title('Asociación entre ambas series')
ax[2].margins(.13)
save(fig, '02_pib_escolaridad_pnud', 'India | PIB y escolaridad · 1990–2023',
     'PNUD se presenta por separado de EdStats. La tendencia temporal conjunta no identifica un efecto causal.',
     'Banco Mundial (PIB) y PNUD, HDR 2025 (mys). Descarga: 21/10/2026.')

fig, ax = plt.subplots(1, 2, figsize=(12, 5.3))
series(ax[0], D.loc[1997:2022], 'gasto_educativo_pib')
style(ax[0], '% del PIB')
ax[0].set_title('Gasto público total en educación')
for key, name, color in [('primaria', 'Primaria', BLUE), ('secundaria', 'Secundaria', ORANGE), ('terciaria', 'Terciaria', GREEN)]:
    series(ax[1], D.loc[1999:2013], 'gasto_alumno_' + key, name, color)
style(ax[1], '% del PIB por habitante')
ax[1].set_title('Gasto público por estudiante')
ax[1].legend(frameon=False)
save(fig, '03_gasto_educativo', 'India | Gasto público educativo',
     'Las unidades de los paneles son diferentes. Los huecos interrumpen las líneas; cada punto es un dato disponible.')

fig, ax = plt.subplots(1, 2, figsize=(12, 5.3))
for key, label, color in [('matricula_neta_primaria', 'Total', BLUE),
                           ('matricula_neta_primaria_mujeres', 'Mujeres', ORANGE),
                           ('matricula_neta_primaria_varones', 'Varones', GREEN)]:
    series(ax[0], D.loc[1971:2013], key, label, color)
style(ax[0], '% de población en edad oficial de primaria')
ax[0].set_title('Primaria · 13 observaciones por serie')
ax[0].legend(frameon=False)
vals = [D.loc[2013, 'matricula_neta_secundaria' + suffix] for suffix in ['', '_mujeres', '_varones']]
ax[1].bar(['Total', 'Mujeres', 'Varones'], vals, color=[BLUE, ORANGE, GREEN], width=.55)
for i, v in enumerate(vals):
    ax[1].text(i, v + 1, f'{v:.1f}%', ha='center')
ax[1].set_ylim(0, 100)
ax[1].set_title('Secundaria · único año disponible: 2013')
style(ax[1], '% de población en edad oficial de secundaria')
ax[1].set_xlabel('')
save(fig, '04_matricula_neta', 'India | Acceso educativo · matrícula neta',
     'La secundaria neta no permite evaluar evolución temporal. No se completan ni se unen años sin observaciones.')

fig, ax = plt.subplots(figsize=(11, 5.3))
for key, name, color in [('primaria', 'Primaria', BLUE), ('secundaria', 'Secundaria', ORANGE), ('terciaria', 'Terciaria', GREEN)]:
    series(ax, D.loc[1971:2025], 'matricula_bruta_' + key, name, color)
style(ax, '% respecto de población en edad oficial del nivel')
ax.legend(frameon=False, ncol=3, loc='upper left')
ax.axhline(100, color='#777777', ls=':', lw=1)
save(fig, '05_matricula_bruta', 'India | Matrícula bruta por nivel · 1971–2025',
     'Incluye alumnos fuera de la edad oficial y puede superar 100%. No equivale a matrícula neta ni la reemplaza.')

fig, ax = plt.subplots(2, 1, figsize=(11, 6.3), sharex=True)
subset = D.loc[1997:2013]
series(ax[0], subset, 'gasto_educativo_pib')
style(ax[0], 'Gasto público\n(% del PIB)')
series(ax[1], subset, 'matricula_neta_primaria', color=ORANGE)
style(ax[1], 'Matrícula neta\nprimaria (%)')
ax[0].set_xlabel('')
save(fig, '06_gasto_y_acceso_primaria', 'India | Gasto y acceso a primaria · 1997–2013',
     'Ventana compartida de las series. Los huecos limitan las comparaciones; este gráfico no estima efectos del gasto.')

# Vista conjunta para inspección y consulta rápida.
tiles = []
for path in FILES:
    with Image.open(path) as img:
        tile = ImageOps.contain(img.convert('RGB'), (900, 460))
        canvas = Image.new('RGB', (920, 490), 'white')
        canvas.paste(tile, ((920 - tile.width)//2, (490 - tile.height)//2))
        tiles.append(canvas)
sheet = Image.new('RGB', (1840, 1470), '#e8ebed')
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i % 2)*920, (i // 2)*490))
sheet.save(OUT / '00_vista_general.png')
for path in FILES:
    print(path.name)
print('PNUD extremos:', P.iloc[[0, -1]][['escolaridad_25_pnud', 'pib_pc_usd_2015']].to_dict('index'))
for key in ['gasto_educativo_pib', 'matricula_neta_primaria', 'matricula_bruta_secundaria']:
    values = D[key].dropna()
    print(key, 'primero/último:', values.iloc[[0, -1]].to_dict())
