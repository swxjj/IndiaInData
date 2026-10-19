from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class FormulaSpec(BaseModel):
    name: str = Field(..., description="Nombre o identificador de la variable calculada (ej: salario_real)")
    expression: str = Field(..., description="Expresión matemática econométrica (ej: salario_nominal / inflacion_ipc * 100)")
    label: Optional[str] = Field(None, description="Etiqueta visible legible")
    units: Optional[str] = Field(None, description="Unidad de medida resultante")

class GenerateRequest(BaseModel):
    database: str = Field(default="world_bank", description="Identificador de la base de datos seleccionada")
    variables: List[str] = Field(..., min_items=1, description="Lista de códigos o columnas de variables")
    countries: List[str] = Field(..., min_items=1, description="Lista de países o códigos ISO-3")
    year_start: Optional[int] = Field(default=1990, description="Año inicial de la muestra")
    year_end: Optional[int] = Field(default=2024, description="Año final de la muestra")
    chart_type: str = Field(default="line", description="Tipo de gráfico: line, bar, scatter, area, stacked_area")
    formulas: Optional[List[FormulaSpec]] = Field(default_factory=list, description="Fórmulas derivadas de usuario")
    title: Optional[str] = Field(None, description="Título personalizado para el gráfico")
    subtitle: Optional[str] = Field(None, description="Subtítulo descriptivo")
    pin: Optional[str] = Field(None, description="PIN opcional de la cátedra")

class GenerateResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    chart_base64: Optional[str] = None
    chart_download_url: Optional[str] = None
    svg_download_url: Optional[str] = None
    csv_download_url: Optional[str] = None
    python_code: Optional[str] = None
    data_preview: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DatabaseSearchRequest(BaseModel):
    query: str = Field(..., description="Nombre o descripción de la base de datos a conectar")
    api_key: Optional[str] = Field(None, description="Clave API de Gemini opcional")

class DatabaseSearchResponse(BaseModel):
    success: bool
    name: str
    description: str
    api_endpoint: Optional[str] = None
    auth_type: Optional[str] = None
    suggested_indicators: List[Dict[str, str]] = Field(default_factory=list)
    connector_code: Optional[str] = None
    notes: Optional[str] = None
    error: Optional[str] = None
