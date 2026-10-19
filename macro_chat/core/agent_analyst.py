"""
Agente Inteligente para Descubrimiento y Conexión de Bases de Datos Económicas.
Utiliza LLM (Google Gemini) para buscar APIs, endpoints, parámetros y generar
conectores de Python cuando el usuario desea incorporar nuevas fuentes de datos.
"""
import os
import json
import re
from typing import Dict, Any, Optional, List
from ..app.config import GEMINI_API_KEY

# Base de conocimiento offline para bases de datos macroeconómicas populares
KNOWN_DATABASES_FALLBACK = {
    "fred": {
        "name": "FRED (Federal Reserve Bank of St. Louis)",
        "description": "Base de datos insignia de la Reserva Federal. Más de 800.000 series de macroeconomía de EE.UU. e internacional.",
        "api_endpoint": "https://api.stlouisfed.org/fred/series/observations",
        "auth_type": "API Key gratuita (registro en research.stlouisfed.org)",
        "suggested_indicators": [
            {"code": "GDP", "name": "Gross Domestic Product (USA)", "units": "Billions of USD"},
            {"code": "CPIAUCSL", "name": "Consumer Price Index for All Urban Consumers", "units": "Index 1982-1984=100"},
            {"code": "FEDFUNDS", "name": "Federal Funds Effective Rate", "units": "%"},
            {"code": "DGS10", "name": "10-Year Treasury Constant Maturity Rate", "units": "%"},
            {"code": "UNRATE", "name": "Unemployment Rate", "units": "%"}
        ],
        "notes": "Para usar la API de FRED se requiere el parámetro `api_key` y `file_type=json`.",
        "connector_code": """import requests
import pandas as pd

def fetch_fred_series(series_id: str, api_key: str) -> pd.DataFrame:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json().get("observations", [])
    df = pd.DataFrame(data)[["date", "value"]]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    return df
"""
    },
    "fmi": {
        "name": "Fondo Monetario Internacional (FMI - API JSON REST)",
        "description": "Estadísticas Financieras Internacionales (IFS), Perspectivas de la Economía Mundial (WEO) y Balanza de Pagos.",
        "api_endpoint": "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData",
        "auth_type": "Acceso Abierto (Sin API Key)",
        "suggested_indicators": [
            {"code": "IFS/M.AR.PMP_IX", "name": "Índice de Precios de Importación", "units": "Índice"},
            {"code": "BOP/A.US.BCA_BP6_USD", "name": "Cuenta Corriente Balanza de Pagos", "units": "USD Millones"}
        ],
        "notes": "Utiliza el estándar SDMX-JSON. Las consultas se estructuran por dataset y dimensión.",
        "connector_code": """import requests
import pandas as pd

def fetch_imf_data(dataset: str, query_key: str) -> pd.DataFrame:
    url = f"http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/{dataset}/{query_key}"
    resp = requests.get(url)
    resp.raise_for_status()
    # Procesar estructura SDMX CompactData
    return resp.json()
"""
    },
    "cepal": {
        "name": "CEPALSTAT (Naciones Unidas - CEPAL)",
        "description": "Portal de datos estadísticos para América Latina y el Caribe.",
        "api_endpoint": "https://api-cepalstat.cepal.org/cepalstat/api/v1",
        "auth_type": "Acceso Abierto (Sin API Key)",
        "suggested_indicators": [
            {"code": "2206", "name": "PIB anual a precios constantes", "units": "Millones de USD"},
            {"code": "2217", "name": "Tasa de inflación acumulada a doce meses", "units": "% anual"}
        ],
        "notes": "Permite consultas en JSON con endpoints /indicator/{id}/records.",
        "connector_code": """import requests
import pandas as pd

def fetch_cepal_indicator(indicator_id: int) -> pd.DataFrame:
    url = f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicator_id}/records?lang=es&format=json"
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.DataFrame(resp.json().get("body", {}).get("records", []))
"""
    },
    "oecd": {
        "name": "OECD Data API",
        "description": "Organización para la Cooperación y el Desarrollo Económicos. Datos de países miembros y economías clave.",
        "api_endpoint": "https://stats.oecd.org/SDMX-JSON/data",
        "auth_type": "Acceso Abierto",
        "suggested_indicators": [
            {"code": "QNA", "name": "Cuentas Nacionales Trimestrales", "units": "Varios"},
            {"code": "KEI", "name": "Indicadores Económicos Clave", "units": "Índices"}
        ],
        "notes": "Formato SDMX-JSON oficial.",
        "connector_code": """import requests

def fetch_oecd_data(dataset: str, filter_str: str):
    url = f"https://stats.oecd.org/SDMX-JSON/data/{dataset}/{filter_str}/all?contentType=csv"
    resp = requests.get(url)
    return resp.text
"""
    }
}

class EconometricAnalystAgent:
    """
    Agente LLM encargado de investigar y generar conectores para nuevas bases de datos económicas.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self.use_new_sdk = True
        self._init_client(self.api_key)

    def _init_client(self, key: str):
        if not key:
            self.client = None
            return
        try:
            from google import genai
            self.client = genai.Client(api_key=key)
            self.use_new_sdk = True
            self.api_key = key
        except Exception:
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=key)
                self.client = genai_legacy.GenerativeModel("gemini-3.5-flash-lite")
                self.use_new_sdk = False
                self.api_key = key
            except Exception as e:
                print(f"Aviso: No se pudo configurar cliente Gemini ({e})")
                self.client = None

    def set_api_key(self, key: str):
        """Actualiza la API Key en tiempo de ejecución."""
        self._init_client(key.strip())

    def search_database_api(self, query: str, custom_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Investiga una base de datos solicitada por el usuario usando LLM.
        Si no hay clave o falla, recurre a la base de conocimiento offline.
        """
        active_client = self.client
        if custom_api_key and custom_api_key.strip():
            try:
                from google import genai
                active_client = genai.Client(api_key=custom_api_key.strip())
            except Exception:
                pass

        # Si tenemos cliente LLM activo, consultamos a Gemini
        if active_client:
            try:
                return self._query_gemini_for_database(active_client, query)
            except Exception as e:
                print(f"Error consultando LLM para base de datos '{query}': {e}. Usando catálogo offline.")

        # Fallback offline inteligente
        return self._offline_database_search(query)

    def _query_gemini_for_database(self, client: Any, query: str) -> Dict[str, Any]:
        prompt = f"""
Eres un Arquitecto de Datos y Econometrista experto. Un usuario desea agregar una nueva base de datos económica a la plataforma académica de Desarrollo Económico (UNS).
La base de datos o tema solicitado es: "{query}".

Investiga los detalles técnicos de la API pública u oficial correspondiente a esa fuente y responde ÚNICAMENTE un objeto JSON válido con la siguiente estructura:
{{
  "name": "Nombre formal de la Base de Datos u Organización",
  "description": "Descripción clara de las series macroeconómicas que ofrece y su cobertura geográfica/temporal",
  "api_endpoint": "URL base o endpoint principal de la API REST",
  "auth_type": "Tipo de autenticación (ej: 'Abierto / Sin clave', 'API Key gratuita con registro', 'OAuth2')",
  "suggested_indicators": [
    {{"code": "CODIGO_O_ID", "name": "Nombre del indicador", "units": "Unidad de medida"}}
  ],
  "connector_code": "Código Python limpio utilizando requests y pandas para descargar una serie de ejemplo y retornarla en DataFrame",
  "notes": "Recomendaciones sobre límites de tasa (rate limits), formato de respuesta (JSON/SDMX) y buenas prácticas"
}}

Asegúrate de que:
1. El código de Python sea ejecutable y no use librerías esotéricas (solo requests, pandas).
2. El JSON sea sintácticamente perfecto sin backticks extras ni comentarios fuera del JSON.
"""

        text_response = ""
        candidate_models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash"]
        last_err = None

        if hasattr(client, "models") and hasattr(client.models, "generate_content"):
            # New google-genai SDK
            for m in candidate_models:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    text_response = res.text
                    break
                except Exception as e:
                    last_err = e
            if not text_response and last_err:
                raise last_err
        else:
            # Legacy google.generativeai
            res = client.generate_content(prompt)
            text_response = res.text

        # Limpiar backticks si los incluyó
        cleaned = text_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        data["success"] = True
        return data

    def _offline_database_search(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        for key, info in KNOWN_DATABASES_FALLBACK.items():
            if key in q_lower or any(word in q_lower for word in info["name"].lower().split()):
                result = dict(info)
                result["success"] = True
                return result

        # Si no se encuentra exactamente, construir una plantilla estructurada
        return {
            "success": True,
            "name": f"Fuente de Datos: {query.title()}",
            "description": f"Conector generado para integrar series de {query}.",
            "api_endpoint": f"https://api.example.org/{query.lower().replace(' ', '_')}/v1",
            "auth_type": "Requiere verificación de API Key o Acceso Abierto",
            "suggested_indicators": [
                {"code": "SERIES_1", "name": f"Indicador principal de {query}", "units": "Nivel o Índice"},
                {"code": "SERIES_2", "name": f"Tasa de variación de {query}", "units": "% anual"}
            ],
            "connector_code": f"""import requests
import pandas as pd

def fetch_{query.lower().replace(' ', '_')}_series(series_code: str) -> pd.DataFrame:
    \"\"\"Descarga datos de {query} y devuelve DataFrame estandarizado.\"\"\"
    url = f"https://api.example.org/data/{{series_code}}?format=json"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    # Transformar a DataFrame
    df = pd.DataFrame(data)
    return df
""",
            "notes": "Para configurar completamente este conector, ingresa una Gemini API Key activa o proporciona la documentación del endpoint."
        }
