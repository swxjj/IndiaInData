import os
import re
import csv
import urllib.request

URL_ARG = "https://www.econstats.com/wdi/wdic_ARG.htm"
URL_IND = "https://www.econstats.com/wdi/wdic_IND.htm"

def fetch_html(url):
    print(f"-> Descargando pagina de EconStats: {url} ...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"}
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        content = resp.read().decode('latin-1', errors='replace')
    print(f"Descarga completa ({len(content):,} bytes).")
    return content

def parse_econstats_table(html):
    tables = re.findall(r'<table[^>]*>.*?</table>', html, re.DOTALL | re.I)
    target_table = None
    for t in tables:
        if len(t) > 100000 and "1960" in t and "1970" in t:
            target_table = t
            break
            
    if not target_table:
        print("No se encontro la tabla principal de series temporales en EconStats.")
        return [], []
        
    rows = re.split(r'<tr[^>]*>', target_table, flags=re.I)
    
    # Extraer encabezados de anios de la primera fila
    header_cells = [re.sub(r'<[^<]+?>', '', c).strip() for c in re.split(r'<td[^>]*>', rows[1], flags=re.I)[1:]]
    year_cols = []
    year_indices = []
    for idx, c in enumerate(header_cells):
        if c.isdigit() and len(c) == 4:
            year_cols.append(int(c))
            year_indices.append(idx)
            
    print(f"Detectadas {len(year_cols)} columnas anuales: {year_cols[0]} a {year_cols[-1]}")
    
    parsed_records = []
    for r in rows[2:]:
        cells = [re.sub(r'<[^<]+?>', '', c).strip().replace('\xa0', ' ') for c in re.split(r'<td[^>]*>', r, flags=re.I)[1:]]
        if len(cells) < 5:
            continue
            
        indicator_code = cells[3].strip()
        indicator_name = cells[4].strip()
        iso = cells[1].strip()
        country_name = cells[2].strip()
        
        if not indicator_code or not iso:
            continue
            
        for y_idx, yr in zip(year_indices, year_cols):
            if y_idx < len(cells):
                raw_val = cells[y_idx].replace(',', '').strip()
                if raw_val and raw_val != '..' and raw_val != '-':
                    try:
                        val = float(raw_val)
                        parsed_records.append({
                            'country_iso': iso,
                            'country_name': country_name,
                            'indicator_code': indicator_code,
                            'indicator_name': indicator_name,
                            'year': yr,
                            'value': val
                        })
                    except ValueError:
                        pass
                        
    return parsed_records, year_cols

def filter_category(records, keywords):
    filtered = []
    for r in records:
        name_lower = r['indicator_name'].lower()
        code_lower = r['indicator_code'].lower()
        if any(kw in name_lower or kw in code_lower for kw in keywords):
            filtered.append(r)
    return filtered

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    print("=" * 80)
    print(" INICIANDO EXTRACCION Y NORMALIZACION DE DATOS ECONSTATS")
    print("=" * 80)
    
    # 1. Procesar Argentina
    html_arg = fetch_html(URL_ARG)
    records_arg, years = parse_econstats_table(html_arg)
    print(f"Total de observaciones anuales extraidas para Argentina: {len(records_arg):,}")
    
    # Guardar todas las variables crudas de Argentina
    arg_all_csv = os.path.join(raw_dir, "econstats_argentina_all.csv")
    with open(arg_all_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=['country_iso', 'country_name', 'indicator_code', 'indicator_name', 'year', 'value'])
        writer.writeheader()
        writer.writerows(records_arg)
        
    # Categorías solicitadas en la consigna del TP3
    categories = {
        "transport": ["transport", "rail", "road", "air", "port", "freight", "passenger", "paved", "vehicle", "is.ro", "is.rr", "is.ai"],
        "energy":    ["energy", "electric", "power", "oil", "fuel", "kwh", "eg.use", "eg.elc"],
        "communications": ["telecom", "telephone", "phone", "internet", "broadband", "mobile", "cellular", "it.net", "it.cel", "it.mlt"]
    }
    
    print("\n" + "=" * 80)
    print(" VARIABLES CLAVE DE INFRAESTRUCTURA IDENTIFICADAS (ECONSTATS ARGENTINA)")
    print("=" * 80)
    
    for cat, kws in categories.items():
        cat_records = filter_category(records_arg, kws)
        unique_vars = sorted(list(set((r['indicator_code'], r['indicator_name']) for r in cat_records)))
        print(f"\n[Categoria: {cat.upper()}] - {len(unique_vars)} indicadores encontrados ({len(cat_records)} obs):")
        for code, name in unique_vars[:8]:
            sub = [r for r in cat_records if r['indicator_code'] == code]
            yrs = [r['year'] for r in sub]
            print(f"  * {code:<18} | {name[:50]:<50} ({min(yrs)}-{max(yrs)}, n={len(yrs)})")
        if len(unique_vars) > 8:
            print(f"    ... y {len(unique_vars) - 8} indicadores adicionales en el archivo CSV.")
            
        out_path = os.path.join(raw_dir, f"econstats_argentina_{cat}.csv")
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=['country_iso', 'country_name', 'indicator_code', 'indicator_name', 'year', 'value'])
            writer.writeheader()
            writer.writerows(cat_records)
            
    print("\n" + "=" * 80)
    print(f"Extraccion de EconStats completada con exito. Archivos guardados en: {raw_dir}")

if __name__ == "__main__":
    main()
