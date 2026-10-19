"""
Catálogo Centralizado de Indicadores, Países y Bases de Datos
para el Laboratorio de Macroeconomía Empírica y Desarrollo Económico (UNS).
"""
from typing import Dict, List, Any
from .connectors.world_bank import INDICATOR_CATALOG, COUNTRY_MAP

# Banderas y nombres formales de países
COUNTRY_DETAILS = {
    "ARG": {"name": "Argentina", "flag": "🇦🇷", "region": "América Latina"},
    "BOL": {"name": "Bolivia", "flag": "🇧🇴", "region": "América Latina"},
    "BRA": {"name": "Brasil", "flag": "🇧🇷", "region": "América Latina"},
    "CHL": {"name": "Chile", "flag": "🇨🇱", "region": "América Latina"},
    "COL": {"name": "Colombia", "flag": "🇨🇴", "region": "América Latina"},
    "CRI": {"name": "Costa Rica", "flag": "🇨🇷", "region": "América Latina"},
    "CUB": {"name": "Cuba", "flag": "🇨🇺", "region": "América Latina"},
    "ECU": {"name": "Ecuador", "flag": "🇪🇨", "region": "América Latina"},
    "MEX": {"name": "México", "flag": "🇲🇽", "region": "América Latina"},
    "PAN": {"name": "Panamá", "flag": "🇵🇦", "region": "América Latina"},
    "PER": {"name": "Perú", "flag": "🇵🇪", "region": "América Latina"},
    "PRY": {"name": "Paraguay", "flag": "🇵🇾", "region": "América Latina"},
    "DOM": {"name": "República Dominicana", "flag": "🇩🇴", "region": "América Latina"},
    "URY": {"name": "Uruguay", "flag": "🇺🇾", "region": "América Latina"},
    "VEN": {"name": "Venezuela", "flag": "🇻🇪", "region": "América Latina"},

    "USA": {"name": "Estados Unidos", "flag": "🇺🇸", "region": "G7 / Desarrollados"},
    "DEU": {"name": "Alemania", "flag": "🇩🇪", "region": "G7 / Desarrollados"},
    "JPN": {"name": "Japón", "flag": "🇯🇵", "region": "G7 / Desarrollados"},
    "GBR": {"name": "Reino Unido", "flag": "🇬🇧", "region": "G7 / Desarrollados"},
    "FRA": {"name": "Francia", "flag": "🇫🇷", "region": "G7 / Desarrollados"},
    "ITA": {"name": "Italia", "flag": "🇮🇹", "region": "G7 / Desarrollados"},
    "CAN": {"name": "Canadá", "flag": "🇨🇦", "region": "G7 / Desarrollados"},
    "ESP": {"name": "España", "flag": "🇪🇸", "region": "G7 / Desarrollados"},
    "AUS": {"name": "Australia", "flag": "🇦🇺", "region": "G7 / Desarrollados"},
    "NOR": {"name": "Noruega", "flag": "🇳🇴", "region": "G7 / Desarrollados"},
    "SWE": {"name": "Suecia", "flag": "🇸🇪", "region": "G7 / Desarrollados"},

    "CHN": {"name": "China", "flag": "🇨🇳", "region": "BRICS & Emergentes"},
    "IND": {"name": "India", "flag": "🇮🇳", "region": "BRICS & Emergentes"},
    "RUS": {"name": "Rusia", "flag": "🇷🇺", "region": "BRICS & Emergentes"},
    "ZAF": {"name": "Sudáfrica", "flag": "🇿🇦", "region": "BRICS & Emergentes"},
    "TUR": {"name": "Turquía", "flag": "🇹🇷", "region": "BRICS & Emergentes"},
    "IDN": {"name": "Indonesia", "flag": "🇮🇩", "region": "BRICS & Emergentes"},

    "KOR": {"name": "Corea del Sur", "flag": "🇰🇷", "region": "Sudeste Asiático & Asia"},
    "VNM": {"name": "Vietnam", "flag": "🇻🇳", "region": "Sudeste Asiático & Asia"},
    "MYS": {"name": "Malasia", "flag": "🇲🇾", "region": "Sudeste Asiático & Asia"},
    "THA": {"name": "Tailandia", "flag": "🇹🇭", "region": "Sudeste Asiático & Asia"},
    "SGP": {"name": "Singapur", "flag": "🇸🇬", "region": "Sudeste Asiático & Asia"},
    "PHL": {"name": "Filipinas", "flag": "🇵🇭", "region": "Sudeste Asiático & Asia"},
    "BGD": {"name": "Bangladesh", "flag": "🇧🇩", "region": "Sudeste Asiático & Asia"},
    "PAK": {"name": "Pakistán", "flag": "🇵🇰", "region": "Sudeste Asiático & Asia"},

    "EGY": {"name": "Egipto", "flag": "🇪🇬", "region": "África & Medio Oriente"},
    "NGA": {"name": "Nigeria", "flag": "🇳🇬", "region": "África & Medio Oriente"},
    "KEN": {"name": "Kenia", "flag": "🇰🇪", "region": "África & Medio Oriente"}
}

# Categorización formal para la cátedra de Desarrollo Económico
CATEGORIES = [
    {
        "id": "crecimiento",
        "name": "Crecimiento y Nivel de Ingreso",
        "icon": "trending-up",
        "indicators": [
            "NY.GDP.PCAP.KD",
            "NY.GDP.PCAP.PP.KD",
            "NY.GDP.PCAP.KD.ZG",
            "NY.GDP.MKTP.KD",
            "NY.GDP.MKTP.KD.ZG"
        ]
    },
    {
        "id": "inversion",
        "name": "Inversión y Acumulación de Capital",
        "icon": "layers",
        "indicators": [
            "NE.GDI.FTOT.ZS",
            "NE.GDI.TOTL.ZS",
            "NY.GNS.ICTR.ZS"
        ]
    },
    {
        "id": "desigualdad",
        "name": "Desigualdad, Pobreza y Bienestar",
        "icon": "users",
        "indicators": [
            "SI.POV.GINI",
            "SI.POV.DDAY",
            "SP.DYN.LE00.IN"
        ]
    },
    {
        "id": "estructura",
        "name": "Estructura Productiva (Cambio Estructural)",
        "icon": "pie-chart",
        "indicators": [
            "NV.AGR.TOTL.ZS",
            "NV.IND.TOTL.ZS",
            "NV.SRV.TOTL.ZS"
        ]
    },
    {
        "id": "precios",
        "name": "Precios y Empleo",
        "icon": "activity",
        "indicators": [
            "FP.CPI.TOTL.ZG",
            "SL.UEM.TOTL.ZS"
        ]
    },
    {
        "id": "externo",
        "name": "Sector Externo y Deuda Pública",
        "icon": "globe",
        "indicators": [
            "NE.EXP.GNFS.ZS",
            "NE.IMP.GNFS.ZS",
            "BN.CAB.XOKA.GD.ZS",
            "GC.DOD.TOTL.GD.ZS"
        ]
    },
    {
        "id": "demografia",
        "name": "Demografía",
        "icon": "user-check",
        "indicators": [
            "SP.POP.TOTL"
        ]
    }
]

# Tipos de gráficos soportados con metadata
CHART_TYPES = [
    {
        "id": "line",
        "name": "Series Temporales (Líneas)",
        "icon": "📈",
        "description": "Evolución cronológica de 1 o más indicadores por país."
    },
    {
        "id": "bar",
        "name": "Comparación Transversal (Barras)",
        "icon": "📊",
        "description": "Ranking comparativo del valor más reciente entre países."
    },
    {
        "id": "scatter",
        "name": "Dispersión y Correlación (Scatter)",
        "icon": "📉",
        "description": "Relación entre 2 indicadores con regresión OLS y R²."
    },
    {
        "id": "area",
        "name": "Líneas con Área Sombreada",
        "icon": "🏔️",
        "description": "Énfasis visual en magnitud y tendencia acumulada."
    },
    {
        "id": "stacked_area",
        "name": "Áreas Apiladas (Composición)",
        "icon": "🥞",
        "description": "Distribución porcentual de sectores productivos (un país)."
    }
]

# Bases de datos disponibles inicialmente
DATABASES = [
    {
        "id": "world_bank",
        "name": "Banco Mundial (WDI)",
        "description": "World Development Indicators. Base abierta oficial con más de 1.400 indicadores mundiales.",
        "status": "active",
        "requires_key": False
    },
    {
        "id": "fred",
        "name": "FRED (Federal Reserve Bank of St. Louis)",
        "description": "Series de macroeconomía global, tasas de interés, tipo de cambio e inflación.",
        "status": "connector_available",
        "requires_key": True
    },
    {
        "id": "imf",
        "name": "Fondo Monetario Internacional (FMI - IFS)",
        "description": "International Financial Statistics. Cuentas nacionales, balanza de pagos y reservas.",
        "status": "connector_available",
        "requires_key": False
    },
    {
        "id": "cepal",
        "name": "CEPALSTAT (Naciones Unidas)",
        "description": "Estadísticas económicas, sociales y ambientales de América Latina y el Caribe.",
        "status": "connector_available",
        "requires_key": False
    }
]

def get_full_catalog() -> Dict[str, Any]:
    """Retorna el catálogo completo estructurado para el selector del frontend."""
    # Lista aplanada de indicadores enriquecidos con su categoría
    enriched_indicators = []

    # Mapeo rápido de código a categoría
    code_to_cat = {}
    for cat in CATEGORIES:
        for code in cat["indicators"]:
            code_to_cat[code] = {"id": cat["id"], "name": cat["name"]}

    for code, meta in INDICATOR_CATALOG.items():
        cat_info = code_to_cat.get(code, {"id": "otros", "name": "Otros Indicadores"})
        enriched_indicators.append({
            "code": code,
            "column": meta["column"],
            "name": meta["name"],
            "units": meta["units"],
            "category_id": cat_info["id"],
            "category_name": cat_info["name"],
            "keywords": meta.get("keywords", [])
        })

    # Lista estructurada de países
    countries_list = []
    for iso3, det in COUNTRY_DETAILS.items():
        countries_list.append({
            "code": iso3,
            "name": det["name"],
            "flag": det["flag"],
            "region": det["region"]
        })

    # Ordenar alfabéticamente por nombre
    countries_list.sort(key=lambda x: x["name"])

    return {
        "databases": DATABASES,
        "categories": CATEGORIES,
        "indicators": enriched_indicators,
        "countries": countries_list,
        "chart_types": CHART_TYPES
    }
