"""Procesa las descargas locales y genera los primeros gráficos del TP6.

Requiere pandas, openpyxl y matplotlib. No realiza descargas ni imputaciones.
"""
from pathlib import Path
import json
import math
import pandas as pd
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from download_tp6_data import INDICATORS

BASE = Path(__file__).resolve().parents[1]
RAW, OUT = BASE / 'data/raw', BASE / 'data/processed'
FIG = BASE / 'output/figures'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    records, coverage = [], []
    for code, name in INDICATORS.items():
        payload = json.loads((RAW / f'wdi_{name}.json').read_text())
        assert payload[0]['pages'] == 1, 'Faltan paginas de la API'
        valid = [r for r in payload[1] if r['value'] is not None]
        coverage.append(dict(variable=name, codigo=code, n=len(valid),
                             primer_anio=min(int(r['date']) for r in valid),
                             ultimo_anio=max(int(r['date']) for r in valid),
                             actualizacion_wdi=payload[0]['lastupdated']))
        for r in payload[1]:
            records.append(dict(pais='IND', anio=int(r['date']), variable=name, valor=r['value']))
    long = pd.DataFrame(records)
    assert not long.duplicated(['pais', 'anio', 'variable']).any()
    panel = long.pivot(index='anio', columns='variable', values='valor').sort_index()
    panel.to_csv(OUT / 'wdi_india_1990_ultimo.csv', encoding='utf-8-sig')
    pd.DataFrame(coverage).to_csv(OUT / 'cobertura_wdi.csv', index=False)
    paired = panel.dropna(subset=['pib_pc_ppa', 'gini'])
    paired.to_csv(OUT / 'india_kuznets_observaciones.csv')
    assert panel['gini'].dropna().between(0, 100).all()

    book = openpyxl.load_workbook(RAW / '2026_gMPI_Table1and2.xlsx', data_only=True)
    s1, s2 = book['gMPI2026_Table1'], book['gMPI2026_Table2']
    rows1 = [r for r in s1 if r[0].value == 'India']
    assert len(rows1) == 1
    r = rows1[0]
    mapping = {'B':'encuesta','D':'ipm','F':'incidencia_pct','L':'intensidad_pct',
               'P':'pobreza_severa_pct','R':'vulnerabilidad_pct','T':'salud_contrib_pct',
               'V':'educacion_contrib_pct','X':'nivel_vida_contrib_pct',
               'Z':'pobreza_nacional_pct','AB':'pobreza_3usd_pct'}
    latest = {name:s1[f'{col}{r[0].row}'].value for col,name in mapping.items()}
    latest.update(edicion=2026, fila_fuente=r[0].row)
    if latest['pobreza_nacional_pct'] == '..':
        latest['pobreza_nacional_pct'] = None
    assert math.isclose(latest['ipm'], latest['incidencia_pct']*latest['intensidad_pct']/10000, abs_tol=1e-8)
    pd.DataFrame([latest]).to_csv(OUT / 'mpi_india_tabla1.csv', index=False)
    dimensions = [('Salud','salud_contrib_pct'),('Educación','educacion_contrib_pct'),('Nivel de vida','nivel_vida_contrib_pct')]
    indicators = [('M','Nutrición','Salud',1/6),('O','Mortalidad infantil','Salud',1/6),
                  ('Q','Años de escolaridad','Educación',1/6),('S','Asistencia escolar','Educación',1/6),
                  ('U','Combustible para cocinar','Nivel de vida',1/18),('W','Saneamiento','Nivel de vida',1/18),
                  ('Y','Agua potable','Nivel de vida',1/18),('AA','Electricidad','Nivel de vida',1/18),
                  ('AC','Vivienda','Nivel de vida',1/18),('AE','Activos','Nivel de vida',1/18)]
    contributions, trends = [], []
    for row in s2:
        if row[0].value != 'India':
            continue
        n = row[0].row
        survey, mpi = s2[f'C{n}'].value, s2[f'E{n}'].value
        trends.append(dict(encuesta=survey, ipm=mpi, incidencia_pct=s2[f'G{n}'].value,
                           intensidad_pct=s2[f'K{n}'].value, fila_fuente=n))
        for col, name, dimension, weight in indicators:
            censored = s2[f'{col}{n}'].value
            contributions.append(dict(encuesta=survey, indicador=name, dimension=dimension,
                incidencia_censurada_pct=censored, peso=weight, contribucion_pct=weight*censored/mpi,
                celda_fuente=f'{col}{n}'))
    c = pd.DataFrame(contributions)
    assert all(abs(v-100)<0.001 for v in c.groupby('encuesta').contribucion_pct.sum())
    current = c[c.encuesta == latest['encuesta']]
    for name, key in dimensions:
        assert abs(current.loc[current.dimension==name,'contribucion_pct'].sum()-latest[key]) < 0.001
    c.to_csv(OUT / 'mpi_india_contribuciones.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(trends).to_csv(OUT / 'mpi_india_tendencia_armonizada.csv', index=False)
    # Guardar notas completas: la Tabla 2 contiene incidencias censuradas, no contribuciones.
    notes = []
    for sheet in book:
        for row in sheet:
            if any(isinstance(cell.value,str) and len(cell.value)>120 for cell in row):
                notes.append(f'{sheet.title}, fila {row[0].row}: ' + ' '.join(str(cell.value) for cell in row if cell.value is not None))
    (OUT / 'notas_fuente_mpi.txt').write_text('\n'.join(notes),encoding='utf-8')

    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,
                         'axes.grid':True,'grid.alpha':0.2,'font.size':10})
    def save(fig, name, note):
        fig.text(.06,.02,note,fontsize=8,color='#4b5563')
        fig.tight_layout(rect=(0,.07,1,.96))
        for ext in ['png','pdf']:
            fig.savefig(FIG / f'{name}.{ext}',dpi=220)
        plt.close(fig)
    fig, axes = plt.subplots(2,1,figsize=(9,7),sharex=True)
    axes[0].plot(panel.index,panel.pib_pc_ppa,color='#184e77')
    axes[0].set(ylabel='Dólares internacionales de 2021',title='India: PIB per cápita PPA y desigualdad del consumo')
    axes[1].scatter(paired.index,paired.gini,color='#b45309',s=45)
    axes[1].set(ylabel='Gini (0–100)',xlabel='Año',ylim=(20,32))
    save(fig,'01_evolucion_pib_gini','Fuente: WDI. Gini: solo años disponibles, sin interpolar. Descarga: ver manifest.json.')
    fig, ax = plt.subplots(figsize=(8,5))
    ax.scatter(paired.pib_pc_ppa,paired.gini,color='#b45309',s=55)
    for year, row in paired.iterrows():
        ax.annotate(str(year),(row.pib_pc_ppa,row.gini),xytext=(6,6),textcoords='offset points')
    ax.set(xlabel='PIB per cápita PPA (dólares internacionales de 2021)',ylabel='Gini (0–100)',
           title=f'India: ingreso medio y desigualdad ({len(paired)} observaciones)',ylim=(21,31))
    save(fig,'02_dispersion_kuznets','Fuente: WDI. Años emparejados; asociación descriptiva, sin interpretación causal.')
    fig, ax = plt.subplots(figsize=(9,6))
    ordered=current.sort_values('contribucion_pct')
    colors={'Salud':'#184e77','Educación':'#b45309','Nivel de vida':'#3b7a57'}
    ax.barh(ordered.indicador,ordered.contribucion_pct,color=[colors[d] for d in ordered.dimension])
    for i,v in enumerate(ordered.contribucion_pct): ax.text(v+.3,i,f'{v:.1f}%',va='center')
    ax.set(xlabel='Contribución al IPM (%)',title='India: privaciones que explican el IPM (encuesta 2019–2021)',xlim=(0,33))
    save(fig,'03_contribuciones_ipm','Fuente: PNUD, IPM 2026, Tabla 2. Cálculo: peso × incidencia censurada (%) / IPM.')
    print(pd.DataFrame(coverage).to_string(index=False))
    print(current[['indicador','contribucion_pct']].to_string(index=False))
    print('Validado: claves únicas; IPM = H × A; contribuciones suman 100% y coinciden con Tabla 1.')

if __name__ == '__main__':
    main()
