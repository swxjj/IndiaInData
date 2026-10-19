import requests
import pandas as pd
from typing import List, Dict, Any, Optional
from .base import BaseDataConnector

COUNTRY_MAP = {
    # Nombres en español / inglés comunes -> ISO3
    "india": "IND",
    "china": "CHN",
    "estados unidos": "USA",
    "eeuu": "USA",
    "ee.uu.": "USA",
    "usa": "USA",
    "argentina": "ARG",
    "brasil": "BRA",
    "brazil": "BRA",
    "chile": "CHL",
    "uruguay": "URY",
    "paraguay": "PRY",
    "bolivia": "BOL",
    "peru": "PER",
    "perú": "PER",
    "ecuador": "ECU",
    "colombia": "COL",
    "venezuela": "VEN",
    "mexico": "MEX",
    "méxico": "MEX",
    "costa rica": "CRI",
    "panama": "PAN",
    "panamá": "PAN",
    "cuba": "CUB",
    "republica dominicana": "DOM",
    "república dominicana": "DOM",
    "dominicana": "DOM",
    "alemania": "DEU",
    "japon": "JPN",
    "japón": "JPN",
    "reino unido": "GBR",
    "uk": "GBR",
    "francia": "FRA",
    "italia": "ITA",
    "espana": "ESP",
    "españa": "ESP",
    "corea del sur": "KOR",
    "corea": "KOR",
    "rusia": "RUS",
    "turquia": "TUR",
    "turquía": "TUR",
    "vietnam": "VNM",
    "indonesia": "IDN",
    "malasia": "MYS",
    "tailandia": "THA",
    "singapur": "SGP",
    "filipinas": "PHL",
    "bangladesh": "BGD",
    "pakistan": "PAK",
    "pakistán": "PAK",
    "sudafrica": "ZAF",
    "sudáfrica": "ZAF",
    "egipto": "EGY",
    "nigeria": "NGA",
    "kenia": "KEN",
    "kenya": "KEN",
    "canada": "CAN",
    "canadá": "CAN",
    "australia": "AUS",
    "noruega": "NOR",
    "suecia": "SWE",
}

INDICATOR_CATALOG = {
    "NY.GDP.PCAP.KD": {
        "name": "PIB per cápita (USD constantes 2015)",
        "column": "pib_per_capita",
        "units": "USD constantes 2015",
        "keywords": ["pib per capita", "pbi per capita", "gdp per capita", "ingreso por habitante"]
    },
    "NY.GDP.PCAP.PP.KD": {
        "name": "PIB per cápita, PPA (USD internacionales constantes 2021)",
        "column": "pib_per_capita_ppa",
        "units": "USD internacionales constantes 2021",
        "keywords": ["ppa", "ppp", "paridad de poder adquisitivo", "pib ppa", "pbi ppa", "gdp ppp"]
    },
    "NY.GDP.PCAP.KD.ZG": {
        "name": "Crecimiento del PIB per cápita (% anual)",
        "column": "crecimiento_pib_pc",
        "units": "% anual",
        "keywords": ["crecimiento pib per capita", "tasa crecimiento per capita"]
    },
    "NY.GDP.MKTP.KD": {
        "name": "PIB total (USD constantes 2015)",
        "column": "pib_total",
        "units": "USD constantes 2015",
        "keywords": ["pib total", "pbi total", "gdp"]
    },
    "NY.GDP.MKTP.KD.ZG": {
        "name": "Crecimiento del PIB (% anual)",
        "column": "crecimiento_pib",
        "units": "% anual",
        "keywords": ["crecimiento", "crecimiento economico", "tasa de crecimiento", "gdp growth"]
    },
    "NE.GDI.FTOT.ZS": {
        "name": "Formación Bruta de Capital Fijo (% del PIB)",
        "column": "fbcf_pct_gdp",
        "units": "% del PIB",
        "keywords": ["fbcf", "inversion", "inversión", "tasa de inversion", "gross fixed capital formation"]
    },
    "NE.GDI.TOTL.ZS": {
        "name": "Formación Bruta de Capital (% del PIB)",
        "column": "formacion_capital_pct_gdp",
        "units": "% del PIB",
        "keywords": ["formacion bruta capital", "capital accumulation"]
    },
    "FP.CPI.TOTL.ZG": {
        "name": "Inflación, precios al consumidor (% anual)",
        "column": "inflacion_ipc",
        "units": "% anual",
        "keywords": ["inflacion", "inflación", "ipc", "cpi", "precios al consumidor"]
    },
    "SL.UEM.TOTL.ZS": {
        "name": "Desempleo total (% de la población activa)",
        "column": "desempleo_pct",
        "units": "% de la fuerza laboral",
        "keywords": ["desempleo", "tasa de desempleo", "paro", "unemployment"]
    },
    "SP.POP.TOTL": {
        "name": "Población total",
        "column": "poblacion_total",
        "units": "Personas",
        "keywords": ["poblacion", "población", "habitantes", "demografia"]
    },
    "NE.EXP.GNFS.ZS": {
        "name": "Exportaciones de bienes y servicios (% del PIB)",
        "column": "exportaciones_pct_gdp",
        "units": "% del PIB",
        "keywords": ["exportaciones", "ventas externas", "exports"]
    },
    "NE.IMP.GNFS.ZS": {
        "name": "Importaciones de bienes y servicios (% del PIB)",
        "column": "importaciones_pct_gdp",
        "units": "% del PIB",
        "keywords": ["importaciones", "compras externas", "imports"]
    },
    "NV.IND.TOTL.ZS": {
        "name": "Industria, valor agregado (% del PIB)",
        "column": "industria_va_pct_gdp",
        "units": "% del PIB",
        "keywords": ["industria", "sector secundario", "manufactura"]
    },
    "NV.AGR.TOTL.ZS": {
        "name": "Agricultura, valor agregado (% del PIB)",
        "column": "agricultura_va_pct_gdp",
        "units": "% del PIB",
        "keywords": ["agricultura", "agro", "agricola", "agrícola", "agropecuario", "campo", "sector primario"]
    },
    "NV.SRV.TOTL.ZS": {
        "name": "Servicios, valor agregado (% del PIB)",
        "column": "servicios_va_pct_gdp",
        "units": "% del PIB",
        "keywords": ["servicios", "sector terciario"]
    },
    "NY.GNS.ICTR.ZS": {
        "name": "Ahorro nacional bruto (% del PIB)",
        "column": "ahorro_bruto_pct_gdp",
        "units": "% del PIB",
        "keywords": ["ahorro", "tasa de ahorro", "ahorro nacional"]
    },
    "SI.POV.GINI": {
        "name": "Índice de Gini (Desigualdad del ingreso)",
        "column": "indice_gini",
        "units": "Índice (0-100)",
        "keywords": ["gini", "desigualdad", "distribucion del ingreso", "coeficiente de gini"]
    },
    "SI.POV.DDAY": {
        "name": "Pobreza extrema ($2.15 diarios, % de la población)",
        "column": "pobreza_extrema_pct",
        "units": "% de la población",
        "keywords": ["pobreza", "pobreza extrema", "poverty", "tasa de pobreza"]
    },
    "SP.DYN.LE00.IN": {
        "name": "Esperanza de vida al nacer (años)",
        "column": "esperanza_vida_anios",
        "units": "Años",
        "keywords": ["esperanza de vida", "expectativa de vida", "longevidad", "life expectancy"]
    },
    "BN.CAB.XOKA.GD.ZS": {
        "name": "Saldo de cuenta corriente (% del PIB)",
        "column": "cuenta_corriente_pct_gdp",
        "units": "% del PIB",
        "keywords": ["cuenta corriente", "balanza de pagos", "current account", "saldo externo"]
    },
    "GC.DOD.TOTL.GD.ZS": {
        "name": "Deuda del gobierno central (% del PIB)",
        "column": "deuda_gobierno_pct_gdp",
        "units": "% del PIB",
        "keywords": ["deuda", "deuda publica", "deuda pública", "deuda del gobierno", "debt"]
    },
}

class WorldBankConnector(BaseDataConnector):
    """Conector para la API oficial y abierta del Banco Mundial (WDI)."""

    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self):
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def normalize_country(self, country: str) -> str:
        """Convierte nombres en español o códigos informales a código ISO-3."""
        c_clean = country.strip().lower()
        if c_clean in COUNTRY_MAP:
            return COUNTRY_MAP[c_clean]
        # Si ya es un código de 3 letras mayúsculas
        if len(c_clean) == 3 and c_clean.isalpha():
            return c_clean.upper()
        return country.upper()

    def search_indicator(self, query: str) -> List[Dict[str, str]]:
        """Busca en el catálogo local de indicadores de desarrollo."""
        q_clean = query.lower()
        results = []
        for code, meta in INDICATOR_CATALOG.items():
            if any(k in q_clean for k in meta["keywords"]) or q_clean in meta["name"].lower():
                results.append({
                    "code": code,
                    "name": meta["name"],
                    "column": meta["column"],
                    "units": meta["units"]
                })
        return results

    def fetch_series(
        self,
        indicators: List[Dict[str, str]],
        countries: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Descarga indicadores desde la API del Banco Mundial y retorna un DataFrame en formato Wide.
        """
        iso_countries = [self.normalize_country(c) for c in countries]
        country_param = ";".join(iso_countries)

        all_records = []

        for ind in indicators:
            ind_code = ind["code"]
            ind_name = ind.get("name") or INDICATOR_CATALOG.get(ind_code, {}).get("name", ind_code)
            ind_col = ind.get("column") or INDICATOR_CATALOG.get(ind_code, {}).get("column", ind_code.lower().replace(".", "_"))

            # Construir URL
            # http://api.worldbank.org/v2/country/{countries}/indicator/{indicator}?format=json&per_page=1000
            date_param = ""
            if start_year and end_year:
                date_param = f"&date={start_year}:{end_year}"
            elif start_year:
                date_param = f"&date={start_year}:2025"

            url = f"{self.BASE_URL}/country/{country_param}/indicator/{ind_code}?format=json&per_page=1000{date_param}"

            try:
                resp = self.session.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                if len(data) < 2 or not data[1]:
                    continue

                for item in data[1]:
                    val = item.get("value")
                    year = item.get("date")
                    c_id = item.get("countryiso3code") or item.get("country", {}).get("id")
                    c_name = item.get("country", {}).get("value")

                    if year and c_id:
                        all_records.append({
                            "anio": int(year),
                            "pais": c_name,
                            "codigo_pais": c_id,
                            "indicador_col": ind_col,
                            "indicador_nombre": ind_name,
                            "valor": float(val) if val is not None else None
                        })
            except Exception as e:
                print(f"Advertencia al descargar {ind_code} para {country_param}: {e}")

        if not all_records:
            return pd.DataFrame()

        df_raw = pd.DataFrame(all_records)

        # Pivotar a Panel Ancho (Wide): anio, pais, codigo_pais, <columna_indicador>
        df_wide = df_raw.pivot_table(
            index=["anio", "pais", "codigo_pais"],
            columns="indicador_col",
            values="valor"
        ).reset_index()

        # Limpiar nombre del índice de columnas si existe
        df_wide.columns.name = None

        # Ordenar por país y año ascendente
        df_wide = df_wide.sort_values(by=["pais", "anio"]).reset_index(drop=True)
        return df_wide
