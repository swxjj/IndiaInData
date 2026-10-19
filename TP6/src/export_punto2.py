"""Reúne el punto 2 en un CSV para Excel en configuración regional española."""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'data/processed'

def read(name):
    with (DATA / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def number(value):
    return '' if value in ('', None) else format(float(value), '.10g').replace('.', ',')

def main():
    mpi = read('mpi_india_tabla1.csv')[0]
    panel = read('wdi_india_1990_ultimo.csv')
    rows = []
    url = 'https://hdr.undp.org/sites/default/files/publications/additional-files/2026-10/2026_gMPI_Table1and2.xlsx'
    def add(part, kind, label, value, unit, period, ref, note='', dimension='', censored='', weight='', source=url):
        rows.append(dict(apartado=part,tipo=kind,indicador=label,dimension=dimension,
                         valor=number(value),unidad=unit,periodo=period,
                         estado='Sin dato' if value in ('',None) else 'Disponible',
                         incidencia_censurada_pct=number(censored),peso=number(weight),
                         fuente=source,referencia=ref,aclaracion=note))
    add('2a','Comparación','Pobreza multidimensional: incidencia',mpi['incidencia_pct'],'% de población','2019–2021','Tabla 1, F30',
        'Encuesta 2019–2021; edición 2026. Comparar incidencias, no el valor del IPM, con las tasas monetarias.')
    add('2a','Comparación','Pobreza monetaria: USD 3 diarios PPA 2021',mpi['pobreza_3usd_pct'],'% de población','2022 (año identificado en WDI)','Tabla 1, AB30',
        'Valor publicado por PNUD para resolver la consigna. No es contemporáneo con la encuesta del IPM.')
    add('2a','Comparación','Pobreza monetaria: línea nacional en PNUD','','% de población','Sin dato en ventana 2014–2025','Tabla 1, Z30',
        'La fuente indica ..; no significa cero.')
    for variable, label, kind, note in [
        ('pobreza_nacional','Pobreza monetaria: línea nacional WDI','Antecedente histórico','Último dato disponible. Es de 2011: no permite una comparación contemporánea con el IPM.'),
        ('pobreza_3usd','Pobreza monetaria: USD 3 diarios WDI actualizado','Actualización complementaria','Dato posterior al 5,3% publicado en la tabla PNUD; no reemplazar silenciosamente el valor de la consigna.')]:
        record=max((r for r in panel if r[variable]),key=lambda r:int(r['anio']))
        code='SI.POV.NAHC' if variable=='pobreza_nacional' else 'SI.POV.DDAY'
        add('2a',kind,label,record[variable],'% de población',record['anio'],code,note,
            source=f'https://api.worldbank.org/v2/country/IND/indicator/{code}?format=json&source=2')
    for key,label,unit,col in [
        ('ipm','Índice de pobreza multidimensional','Índice 0–1','D'),
        ('intensidad_pct','Intensidad de las privaciones','% de privaciones ponderadas entre pobres','L'),
        ('pobreza_severa_pct','Pobreza multidimensional severa','% de población','P'),
        ('vulnerabilidad_pct','Vulnerabilidad a pobreza multidimensional','% de población','R')]:
        add('2a','Contexto',label,mpi[key],unit,'2019–2021',f'Tabla 1, {col}30',
            'Las tasas agregadas no identifican el solapamiento de personas pobres ni la eficiencia de las transferencias. Esta requiere costos y efectos causales.')
    for key,label,col in [('salud_contrib_pct','Salud','T'),('educacion_contrib_pct','Educación','V'),('nivel_vida_contrib_pct','Nivel de vida','X')]:
        add('2b','Contribución por dimensión',label,mpi[key],'% del IPM','2019–2021',f'Tabla 1, {col}30',
            'Las tres dimensiones suman 100%. Nivel de vida tiene la mayor contribución.',dimension=label)
    contributions=[r for r in read('mpi_india_contribuciones.csv') if r['encuesta']==mpi['encuesta']]
    for r in contributions:
        add('2b','Contribución por indicador',r['indicador'],r['contribucion_pct'],'% del IPM','2019–2021',
            'Tabla 2, '+r['celda_fuente'],
            'Cálculo: peso × incidencia censurada (%) / IPM. Incidencia censurada: % de población simultáneamente pobre y privada en el indicador. Mayor contribución no prueba mayor eficiencia del gasto.',
            dimension=r['dimension'],censored=r['incidencia_censurada_pct'],weight=r['peso'])
    assert len(rows)==22
    assert abs(sum(float(r['contribucion_pct']) for r in contributions)-100)<.001
    target=BASE/'output/tp6_punto2_completo.csv'
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
    with target.open(encoding='utf-8-sig',newline='') as f:
        saved=list(csv.DictReader(f,delimiter=';'))
    assert len(saved)==22 and sum(r['estado']=='Sin dato' for r in saved)==1
    print(f'{target}: {len(saved)} filas verificadas.')

if __name__=='__main__':
    main()
