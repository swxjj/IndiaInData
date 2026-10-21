"""Descarga y organiza fuentes oficiales del ejercicio 1; no estima ni interpola."""
import argparse
import csv
import hashlib
import json
import io
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from time import sleep

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data' / 'processed'
# alias, código, fuente BM, unidad, función en la consigna
SERIES = [
    ('pib_pc_usd_2015', 'NY.GDP.PCAP.KD', 2, 'US$ constantes de 2015', 'PIB por habitante'),
    ('escolaridad_25_total', 'UIS.EA.MEAN.1T6.AG25T99', 12, 'años', 'Escolaridad media 25+ ambos sexos, variable exacta de la consigna'),
    ('escolaridad_25_mujeres', 'UIS.EA.MEAN.1T6.AG25T99.F', 12, 'años', 'Escolaridad media 25+ mujeres'),
    ('escolaridad_25_varones', 'UIS.EA.MEAN.1T6.AG25T99.M', 12, 'años', 'Escolaridad media 25+ varones'),
    ('gasto_educativo_pib', 'SE.XPD.TOTL.GD.ZS', 2, '% del PIB', 'Gasto público total en educación'),
    ('gasto_alumno_primaria', 'SE.XPD.PRIM.PC.ZS', 2, '% del PIB por habitante', 'Gasto público por estudiante de primaria'),
    ('gasto_alumno_secundaria', 'SE.XPD.SECO.PC.ZS', 2, '% del PIB por habitante', 'Gasto público por estudiante de secundaria'),
    ('gasto_alumno_terciaria', 'SE.XPD.TERT.PC.ZS', 2, '% del PIB por habitante', 'Gasto público por estudiante de educación terciaria'),
    ('matricula_neta_primaria', 'SE.PRM.NENR', 2, '% población en edad oficial del nivel', 'Acceso: matrícula neta primaria'),
    ('matricula_neta_secundaria', 'SE.SEC.NENR', 2, '% población en edad oficial del nivel', 'Acceso: matrícula neta secundaria'),
    ('matricula_neta_primaria_mujeres', 'SE.PRM.NENR.FE', 2, '% población femenina en edad oficial del nivel', 'Acceso: matrícula neta primaria mujeres'),
    ('matricula_neta_primaria_varones', 'SE.PRM.NENR.MA', 2, '% población masculina en edad oficial del nivel', 'Acceso: matrícula neta primaria varones'),
    ('matricula_neta_secundaria_mujeres', 'SE.SEC.NENR.FE', 2, '% población femenina en edad oficial del nivel', 'Acceso: matrícula neta secundaria mujeres'),
    ('matricula_neta_secundaria_varones', 'SE.SEC.NENR.MA', 2, '% población masculina en edad oficial del nivel', 'Acceso: matrícula neta secundaria varones'),
    ('matricula_bruta_primaria', 'SE.PRM.ENRR', 2, '%', 'Complemento: matrícula bruta primaria'),
    ('matricula_bruta_secundaria', 'SE.SEC.ENRR', 2, '%', 'Complemento: matrícula bruta secundaria'),
    ('matricula_bruta_terciaria', 'SE.TER.ENRR', 2, '%', 'Complemento: matrícula bruta terciaria'),
]
UNDP_BASE = 'https://hdr.undp.org/sites/default/files/2025_HDR/'
UNDP_FILES = ['HDR25_Composite_indices_complete_time_series.csv', 'HDR25_Composite_indices_metadata.xlsx']


def undp_complement(offline):
    entries = []
    for filename in UNDP_FILES:
        if not offline:
            request = Request(UNDP_BASE + filename, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(request, timeout=90) as response:
                payload = response.read()
                final_url = response.url
            if filename.endswith('.xlsx'):
                assert payload.startswith(b'PK'), 'Metadatos PNUD: formato inesperado'
            else:
                assert b'mys_1990' in payload, 'PNUD: columnas esperadas ausentes'
            (RAW / filename).write_bytes(payload)
            entries.append(dict(file=filename, url=UNDP_BASE + filename, resolved_url=final_url,
                                downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
                                bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()))
    payload = (RAW / UNDP_FILES[0]).read_bytes()
    try:
        text = payload.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = payload.decode('cp1252')
    india = [r for r in csv.DictReader(io.StringIO(text)) if r['iso3'] == 'IND']
    assert len(india) == 1
    row = india[0]
    gdp = json.loads((RAW / 's2_NY.GDP.PCAP.KD.json').read_bytes())
    gdp = {int(r['date']): r['value'] for r in gdp[1]}
    records = []
    for key, value in row.items():
        if key.startswith('mys_') and key[4:].isdigit():
            year = int(key[4:])
            records.append(dict(pais='IND', anio=year, escolaridad_25_pnud=float(value) if value.strip() else None,
                                pib_pc_usd_2015=gdp.get(year), fuente_escolaridad='PNUD HDR 2025; mys',
                                unidad_escolaridad='años; población 25+', url=UNDP_BASE + UNDP_FILES[0]))
    records.sort(key=lambda r: r['anio'])
    assert records
    save_csv('complemento_pnud_escolaridad_india.csv', records, list(records[0]))
    print(f'Complemento PNUD: {len(records)} años ({records[0]["anio"]}-{records[-1]["anio"]})')
    return entries


def save_csv(name, rows, fields):
    with (OUT / name).open('w', newline='', encoding='utf-8-sig') as f:
        # Excel en español: coma decimal y punto y coma entre columnas.
        # Solo transformar números, sin alterar códigos, textos ni URLs.
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=';')
        writer.writeheader()
        writer.writerows({key: str(value).replace('.', ',') if isinstance(value, float) else value
                          for key, value in row.items()} for row in rows)


def download(url, filename):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=90) as response:
                payload = response.read()
                final_url = response.url
            doc = json.loads(payload)
            if not isinstance(doc, list) or len(doc) != 2 or not isinstance(doc[1], list):
                raise ValueError(f'Respuesta inválida: {url}: {str(doc)[:300]}')
            if int(doc[0].get('pages', 1)) != 1:
                raise ValueError('La respuesta requiere paginación; descarga incompleta')
            (RAW / filename).write_bytes(payload)
            return doc, dict(file=filename, url=url, resolved_url=final_url,
                             downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
                             bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(),
                             lastupdated=doc[0].get('lastupdated'))
        except Exception:
            if attempt == 2:
                raise
            sleep(2 * (attempt + 1))


def fetch_series(spec):
    alias, code, source, unit, purpose = spec
    base = 'https://api.worldbank.org/v2'
    data, data_entry = download(
        f'{base}/country/IND/indicator/{code}?source={source}&format=json&per_page=20000',
        f's{source}_{code}.json')
    meta, meta_entry = download(
        f'{base}/indicator/{code}?source={source}&format=json&per_page=20000',
        f'metadata_s{source}_{code}.json')
    return spec, data, meta, [data_entry, meta_entry]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Regenerar CSV desde JSON guardados')
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.offline:
        results = [(s, json.loads((RAW / f's{s[2]}_{s[1]}.json').read_bytes()),
                    json.loads((RAW / f'metadata_s{s[2]}_{s[1]}.json').read_bytes()), []) for s in SERIES]
    else:
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(fetch_series, SERIES))
        entries = [e for result in results for e in result[3]]
        (RAW / 'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    extra_entries = undp_complement(args.offline)
    if not args.offline:
        (RAW / 'manifest.json').write_text(json.dumps(entries + extra_entries, ensure_ascii=False, indent=2), encoding='utf-8')

    long, dictionary, coverage, by_alias = [], [], [], {}
    for spec, data, metadata, _ in results:
        alias, code, source, unit, purpose = spec
        assert len(metadata[1]) == 1 and metadata[1][0]['id'] == code
        meta = metadata[1][0]
        values = {}
        for row in data[1]:
            assert row['countryiso3code'] == 'IND' and row['indicator']['id'] == code
            year = int(row['date'])
            assert year not in values, (alias, year)
            value = row['value']
            assert value is None or isinstance(value, (int, float))
            values[year] = value
            long.append(dict(pais='IND', anio=year, variable=alias, codigo=code, fuente_id=source,
                             valor=value, unidad=unit, obs_status=row.get('obs_status', ''),
                             decimal_fuente=row.get('decimal', ''),
                             url=f'https://api.worldbank.org/v2/country/IND/indicator/{code}?source={source}&format=json'))
        by_alias[alias] = values
        observed = sorted(y for y, v in values.items() if v is not None)
        gaps = [y for y in range(observed[0], observed[-1] + 1) if values.get(y) is None] if observed else []
        coverage.append(dict(variable=alias, codigo=code, fuente_id=source, n_observaciones=len(observed),
                             primer_anio=min(observed) if observed else '', ultimo_anio=max(observed) if observed else '',
                             anios_disponibles=';'.join(map(str, observed)), faltantes_internos=';'.join(map(str, gaps))))
        dictionary.append(dict(variable=alias, codigo=code, fuente_id=source, unidad=unit, uso=purpose,
                               nombre_original=meta['name'], definicion=meta.get('sourceNote', ''),
                               organizacion=meta.get('sourceOrganization', ''),
                               archivo_original=f'data/raw/s{source}_{code}.json'))
    observed_years = [r['anio'] for r in long if r['valor'] is not None]
    years = list(range(min(observed_years), max(observed_years) + 1))
    long = [r for r in long if years[0] <= r['anio'] <= years[-1]]
    long.sort(key=lambda r: (r['variable'], r['anio']))
    save_csv('educacion_india_largo.csv', long, list(long[0]))
    save_csv('diccionario_variables.csv', dictionary, list(dictionary[0]))
    save_csv('cobertura.csv', coverage, list(coverage[0]))
    panel = [dict(pais='IND', anio=y, **{a: v.get(y) for a, v in by_alias.items()}) for y in years]
    save_csv('educacion_india_anual.csv', panel, ['pais', 'anio'] + list(by_alias))
    pairs = [dict(pais='IND', anio=y, pib_pc_usd_2015=by_alias['pib_pc_usd_2015'][y],
                  escolaridad_25_total=by_alias['escolaridad_25_total'][y])
             for y in years if by_alias['pib_pc_usd_2015'].get(y) is not None
             and by_alias['escolaridad_25_total'].get(y) is not None]
    save_csv('pib_escolaridad_anios_comunes.csv', pairs, ['pais', 'anio', 'pib_pc_usd_2015', 'escolaridad_25_total'])
    for row in coverage:
        print(f"{row['variable']}: {row['n_observaciones']} datos ({row['primer_anio']}-{row['ultimo_anio']})")
    print(f'Años comunes PIB/escolaridad: {len(pairs)}')


if __name__ == '__main__':
    main()
