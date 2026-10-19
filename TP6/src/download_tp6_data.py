"""Descarga fuentes originales del TP6. Ejecutar desde cualquier directorio.

Conserva respuestas, metadatos, fecha UTC y SHA256. No imputa observaciones.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import urllib.request
import time

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / 'data' / 'raw'
INDICATORS = {
    'NY.GDP.PCAP.PP.KD': 'pib_pc_ppa',
    'SI.POV.GINI': 'gini',
    'SI.POV.DDAY': 'pobreza_3usd',
    'SI.POV.NAHC': 'pobreza_nacional',
}
MPI_URL = 'https://hdr.undp.org/sites/default/files/publications/additional-files/2026-10/2026_gMPI_Table1and2.xlsx'

def fetch(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'IndiaInData academic research'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = []
    sources = {'2026_gMPI_Table1and2.xlsx': MPI_URL}
    for code, name in INDICATORS.items():
        sources[f'wdi_{name}.json'] = f'https://api.worldbank.org/v2/country/IND/indicator/{code}?format=json&per_page=1000&date=1990:2026&source=2'
        sources[f'metadata_{name}.json'] = f'https://api.worldbank.org/v2/indicator/{code}?format=json&source=2'
    for filename, url in sources.items():
        content = fetch(url)
        if filename.endswith('.json'):
            data = json.loads(content)
            if not isinstance(data, list) or len(data) < 2 or data[1] is None:
                raise ValueError(f'Respuesta sin datos: {url}')
        elif not content.startswith(b'PK'):
            raise ValueError('El archivo MPI no es un XLSX')
        (RAW / filename).write_bytes(content)
        manifest.append(dict(file=filename, url=url, downloaded_utc=datetime.now(timezone.utc).isoformat(),
                             bytes=len(content), sha256=hashlib.sha256(content).hexdigest()))
        (RAW / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(f'Descargado: {filename} ({len(content)} bytes)', flush=True)

if __name__ == '__main__':
    main()
