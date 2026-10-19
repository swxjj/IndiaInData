import os
import json
import re
from typing import Dict, Any, List, Optional
from .connectors.world_bank import INDICATOR_CATALOG, COUNTRY_MAP

class LLMRouter:
    """
    Orquestador de intención en lenguaje natural con Gemini 2.0 Flash / 1.5 Flash.
    Incluye fallback inteligente basado en reglas y catálogo para resiliencia offline.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                # Intentar importar google-genai o google.generativeai
                try:
                    from google import genai
                    self.client = genai.Client(api_key=self.api_key)
                    self.use_new_sdk = True
                except ImportError:
                    import google.generativeai as genai_legacy
                    genai_legacy.configure(api_key=self.api_key)
                    self.client = genai_legacy.GenerativeModel("gemini-3.5-flash-lite")
                    self.use_new_sdk = False
            except Exception as e:
                print(f"Advertencia: No se pudo inicializar cliente de Gemini ({e}). Se usará fallback heurístico.")
                self.client = None

    def parse_query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Interpreta la consulta del usuario y extrae parámetros estructurados.
        """
        if self.client:
            try:
                return self._parse_with_gemini(user_prompt)
            except Exception as e:
                print(f"Error en llamada a Gemini ({e}). Ejecutando fallback de catálogo.")

        return self._parse_heuristic(user_prompt)

    def _parse_with_gemini(self, user_prompt: str) -> Dict[str, Any]:
        """Extrae parámetros usando Gemini Structured Output."""
        prompt = f"""
Eres el orquestador del MacroData Assistant para la cátedra de Desarrollo Económico (UNS).
Tu función es extraer los parámetros de la consulta del usuario y mapearlos a indicadores oficiales del Banco Mundial (WDI).

REGLAS ESTRICTAS:
1. Cero alucinación: Solo usa indicadores macroeconómicos oficiales.
2. Títulos y nombres SIEMPRE en español formal académico.
3. Nombres de variables legibles y pertinentes (NUNCA uses nombres crudos como 'NY.GDP.PCAP.KD', usa 'PIB per cápita (USD constantes 2015)').
4. Si el usuario no especifica años, deja start_year y end_year en null.
5. Si el usuario no especifica fuente, asume 'Banco Mundial (WDI)'.
6. Catálogo de indicadores comunes:
{json.dumps(INDICATOR_CATALOG, ensure_ascii=False, indent=2)}

Consulta del usuario:
"{user_prompt}"

Responde ÚNICAMENTE un objeto JSON válido con esta estructura exacta:
{{
  "source": "Banco Mundial (WDI)",
  "countries": ["India", "China"],
  "indicators": [
    {{
      "code": "NY.GDP.PCAP.KD",
      "name": "PIB per cápita (USD constantes 2015)",
      "column": "pib_per_capita",
      "units": "USD constantes 2015"
    }}
  ],
  "title": "Evolución del PIB per Cápita: India y China",
  "subtitle": "Valores en USD constantes de 2015 (1960–2024)",
  "units": "USD constantes 2015",
  "chart_type": "line",
  "start_year": null,
  "end_year": null
}}

Valores posibles de 'chart_type':
- 'line': series de tiempo estándar.
- 'bar': comparaciones entre países para un año o período puntual, rankings.
- 'scatter': gráficos de dispersión (correlación entre dos indicadores, ej: inversión vs crecimiento).
- 'area': gráfico de línea con sombreado bajo la curva (para enfatizar volumen o porcentajes).
- 'stacked_area': áreas apiladas continuas (para componentes que suman un total, ej: sectores del PIB).
"""
        if self.use_new_sdk:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            raw_text = response.text
        else:
            response = self.client.generate_content(prompt)
            raw_text = response.text

        # Limpiar markdown si viniera formateado
        raw_text = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
        raw_text = re.sub(r"```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

        parsed = json.loads(raw_text)
        return parsed

    def _parse_heuristic(self, user_prompt: str) -> Dict[str, Any]:
        """Fallback basado en reglas y búsqueda léxica sobre el catálogo."""
        p_lower = user_prompt.lower()

        # 1. Detectar países
        found_countries = []
        for c_name, iso in COUNTRY_MAP.items():
            if re.search(r'\b' + re.escape(c_name) + r'\b', p_lower):
                capitalized = c_name.capitalize() if len(c_name) > 3 else c_name.upper()
                if capitalized not in found_countries:
                    found_countries.append(capitalized)

        if not found_countries:
            found_countries = ["India"]  # País eje del repositorio por defecto

        # 2. Detectar indicadores
        found_indicators = []
        for code, meta in INDICATOR_CATALOG.items():
            for kw in meta["keywords"]:
                if kw in p_lower:
                    found_indicators.append({
                        "code": code,
                        "name": meta["name"],
                        "column": meta["column"],
                        "units": meta["units"]
                    })
                    break

        if not found_indicators:
            # Indicador por defecto: PIB per cápita
            meta = INDICATOR_CATALOG["NY.GDP.PCAP.KD"]
            found_indicators.append({
                "code": "NY.GDP.PCAP.KD",
                "name": meta["name"],
                "column": meta["column"],
                "units": meta["units"]
            })

        # 3. Detectar años
        years = re.findall(r'\b(19\d\d|20\d\d)\b', user_prompt)
        start_year = None
        end_year = None
        if len(years) == 1:
            start_year = int(years[0])
        elif len(years) >= 2:
            start_year = int(min(years))
            end_year = int(max(years))

        # 4. Detectar tipo de gráfico
        chart_type = "line"
        scatter_keywords = [
            "dispersion", "dispersión", "scatter", "correlacion", "correlación",
            "relacion", "relación", "tendencia", "linea de tendencia", "línea de tendencia",
            "regresion", "regresión"
        ]
        bar_keywords = ["barra", "barras", "columnas", "ranking", "bar"]
        area_keywords = ["sombreado", "sombra", "sombreada", "relleno", "fill", "area sombreada", "línea sombreada", "linea sombreada"]
        stacked_keywords = ["apilada", "apiladas", "apilado", "stacked", "continuas", "continua", "sectores"]

        if any(sk in p_lower for sk in scatter_keywords) or (" vs " in p_lower and len(found_indicators) >= 2):
            chart_type = "scatter"
        elif any(bk in p_lower for bk in bar_keywords):
            chart_type = "bar"
        elif any(ak in p_lower for ak in area_keywords):
            chart_type = "area"
        elif any(stk in p_lower for stk in stacked_keywords):
            chart_type = "stacked_area"
        else:
            # Si se consultan múltiples sectores de valor agregado (% del PIB) para 1 solo país y no se pidió explícitamente línea
            sector_cols = {"agricultura_va_pct_gdp", "industria_va_pct_gdp", "servicios_va_pct_gdp"}
            found_cols = {ind["column"] for ind in found_indicators}
            if len(found_countries) == 1 and len(sector_cols.intersection(found_cols)) >= 2:
                if "linea" not in p_lower and "línea" not in p_lower:
                    chart_type = "stacked_area"

        # 5. Construir títulos y unidades
        ind_names = [ind["name"] for ind in found_indicators]
        if chart_type == "scatter" and len(found_indicators) >= 2:
            title = f"Relación: {found_indicators[0]['name']} vs {found_indicators[1]['name']}"
            subtitle = f"Dispersión y línea de tendencia ({start_year or 'Inicio'}–{end_year or 'Presente'})"
            units = f"{found_indicators[1]['units']} vs {found_indicators[0]['units']}"
        elif chart_type == "bar":
            title = f"Comparación por Países: {found_indicators[0]['name']}"
            subtitle = f"Valores comparativos ({start_year or end_year or 'Año más reciente'})"
            units = found_indicators[0]["units"]
        elif chart_type == "stacked_area":
            title = f"Evolución de Componentes: {', '.join(found_countries)}"
            subtitle = f"Áreas continuas armonizadas ({start_year or 'Inicio'}–{end_year or 'Presente'})"
            units = "% del PIB" if all("%" in ind.get("units", "") for ind in found_indicators) else "Valores armonizados"
        elif chart_type == "area":
            title = f"{found_indicators[0]['name']}: {', '.join(found_countries)}"
            subtitle = f"Serie temporal con sombreado de magnitud ({start_year or 'Inicio'}–{end_year or 'Presente'})"
            units = found_indicators[0]["units"]
        else:
            title = f"Comparación Macroeconómica: {', '.join(found_countries)}"
            if len(found_indicators) == 1:
                title = f"{found_indicators[0]['name']}: {', '.join(found_countries)}"
            elif len(found_countries) == 1:
                title = f"Evolución Macroeconómica: {found_countries[0]}"
            subtitle = f"Series históricas armonizadas ({start_year or 'Inicio'}–{end_year or 'Presente'})"
            units = found_indicators[0]["units"] if len(found_indicators) == 1 else "% del PIB" if all("%" in ind.get("units", "") for ind in found_indicators) else "Valores armonizados"

        return {
            "source": "Banco Mundial (WDI)",
            "countries": found_countries,
            "indicators": found_indicators,
            "title": title,
            "subtitle": subtitle,
            "units": units,
            "chart_type": chart_type,
            "start_year": start_year,
            "end_year": end_year
        }
