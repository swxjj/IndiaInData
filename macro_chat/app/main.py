import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .config import GEMINI_API_KEY, CLASS_PIN, OUTPUT_DIR, STATIC_DIR
from .schemas import (
    GenerateRequest,
    GenerateResponse,
    DatabaseSearchRequest,
    DatabaseSearchResponse,
    FormulaSpec
)
from ..core.catalog import get_full_catalog, INDICATOR_CATALOG
from ..core.connectors.world_bank import WorldBankConnector
from ..core.formula_engine import FormulaEngine, FormulaEvaluationError
from ..core.academic_theme import AcademicChartRenderer
from ..core.code_generator import PythonCodeGenerator
from ..core.agent_analyst import EconometricAnalystAgent

app = FastAPI(
    title="MacroData Academic Studio API",
    description="Backend para generación determinista de gráficos, fórmulas macroeconómicas y conexión de bases de datos con LLM (UNS)",
    version="2.0.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar conectores y agentes
wb_connector = WorldBankConnector()
analyst_agent = EconometricAnalystAgent(api_key=GEMINI_API_KEY)

# Servir archivos estáticos
if Path(STATIC_DIR).exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class KeyConfigRequest(BaseModel):
    api_key: str
    pin: Optional[str] = None


@app.get("/")
def serve_index():
    index_file = Path(STATIC_DIR) / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "MacroData Studio API activa."}


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_active": bool(analyst_agent.api_key and analyst_agent.client),
        "output_dir": OUTPUT_DIR
    }


@app.get("/api/catalog")
def get_catalog():
    """Retorna el catálogo centralizado de bases de datos, categorías, indicadores, países y gráficos."""
    return get_full_catalog()


@app.post("/api/config/key")
def set_api_key(req: KeyConfigRequest):
    """Guarda y activa la clave de API para el agente de bases de datos."""
    if CLASS_PIN and req.pin != CLASS_PIN:
        raise HTTPException(status_code=401, detail="PIN de acceso incorrecto.")

    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="La API Key no puede estar vacía.")

    analyst_agent.set_api_key(key)
    os.environ["GEMINI_API_KEY"] = key

    # Persistir en macro_chat/.env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    try:
        lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={key}\n")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"GEMINI_API_KEY={key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Advertencia guardando .env: {e}")

    return {
        "success": True,
        "message": "Clave de Gemini guardada y activada exitosamente.",
        "gemini_active": bool(analyst_agent.client)
    }


@app.post("/api/generate", response_model=GenerateResponse)
def generate_chart(req: GenerateRequest):
    """
    Genera el gráfico econométrico determinista, evalúa fórmulas,
    calcula estadísticas y produce el código Python reproducible.
    """
    # 1. Validación de PIN
    if CLASS_PIN and req.pin and req.pin != CLASS_PIN:
        raise HTTPException(status_code=401, detail="PIN de acceso incorrecto.")

    if not req.variables:
        raise HTTPException(status_code=400, detail="Debes seleccionar al menos una variable o fórmula.")
    if not req.countries:
        raise HTTPException(status_code=400, detail="Debes seleccionar al menos un país.")

    session_id = uuid.uuid4().hex[:10]
    out_dir = Path(OUTPUT_DIR).resolve()
    out_dir.mkdir(exist_ok=True)

    # 2. Identificar indicadores a descargar del Banco Mundial
    # Mapear códigos o nombres de columna
    code_by_col = {meta["column"]: code for code, meta in INDICATOR_CATALOG.items()}

    needed_indicators: Dict[str, Dict[str, str]] = {}
    requested_cols: List[str] = []
    formula_cols: List[str] = []

    # Registrar variables de fórmulas
    formula_dicts = []
    if req.formulas:
        for f in req.formulas:
            f_col = f.name.strip().lower().replace(" ", "_")
            formula_cols.append(f_col)
            formula_dicts.append({
                "column": f_col,
                "expression": f.expression,
                "label": f.label or f.name,
                "units": f.units
            })

    # Revisar variables solicitadas
    for var in req.variables:
        clean_var = var.strip()
        if clean_var in INDICATOR_CATALOG:
            meta = INDICATOR_CATALOG[clean_var]
            needed_indicators[clean_var] = {
                "code": clean_var,
                "name": meta["name"],
                "column": meta["column"],
                "units": meta["units"]
            }
            requested_cols.append(meta["column"])
        elif clean_var in code_by_col:
            code = code_by_col[clean_var]
            meta = INDICATOR_CATALOG[code]
            needed_indicators[code] = {
                "code": code,
                "name": meta["name"],
                "column": meta["column"],
                "units": meta["units"]
            }
            requested_cols.append(meta["column"])
        elif clean_var in formula_cols:
            requested_cols.append(clean_var)

    # Si las fórmulas requieren variables que no fueron seleccionadas directamente, identificarlas
    for f in formula_dicts:
        val_res = FormulaEngine.validate_formula(f["expression"], list(code_by_col.keys()))
        for used_var in val_res.get("variables", []):
            if used_var in code_by_col and code_by_col[used_var] not in needed_indicators:
                code = code_by_col[used_var]
                meta = INDICATOR_CATALOG[code]
                needed_indicators[code] = {
                    "code": code,
                    "name": meta["name"],
                    "column": meta["column"],
                    "units": meta["units"]
                }

    try:
        # 3. Descargar datos vía conector
        indicators_list = list(needed_indicators.values())
        if not indicators_list and not formula_cols:
            raise HTTPException(status_code=400, detail="No se especificaron variables válidas para descargar.")

        df = wb_connector.fetch_series(
            indicators=indicators_list,
            countries=req.countries,
            start_year=req.year_start,
            end_year=req.year_end
        )

        if df.empty:
            return GenerateResponse(
                success=False,
                error="No se encontraron datos disponibles para los países e indicadores seleccionados en el rango temporal indicado."
            )

        # 4. Aplicar fórmulas derivadas
        if formula_dicts:
            df = FormulaEngine.apply_formulas(df, formula_dicts)

        # 5. Determinar columnas y nombres a graficar
        plot_cols = []
        plot_names = []

        # Diccionario para nombres de columnas
        col_to_name = {meta["column"]: meta["name"] for meta in INDICATOR_CATALOG.values()}
        for f in formula_dicts:
            col_to_name[f["column"]] = f["label"] or f["column"]

        for c in requested_cols:
            if c in df.columns and c not in plot_cols:
                plot_cols.append(c)
                plot_names.append(col_to_name.get(c, c))

        # Si ninguna columna solicitada está disponible pero hay columnas en df
        if not plot_cols:
            candidate_cols = [c for c in df.columns if c not in ["anio", "pais", "codigo_pais"]]
            if candidate_cols:
                plot_cols = [candidate_cols[0]]
                plot_names = [col_to_name.get(plot_cols[0], plot_cols[0])]
            else:
                return GenerateResponse(
                    success=False,
                    error="No hay series numéricas disponibles para generar el gráfico."
                )

        # 6. Preparar títulos y unidades
        first_ind_meta = indicators_list[0] if indicators_list else {}
        default_title = req.title or (plot_names[0] if len(plot_names) == 1 else "Análisis Macroeconómico Comparado")
        default_subtitle = req.subtitle or f"Período {req.year_start} - {req.year_end} | Países: {', '.join(req.countries[:4])}{'...' if len(req.countries) > 4 else ''}"
        units = first_ind_meta.get("units") if len(plot_cols) == 1 else None

        # 7. Renderizar gráfico determinista con matplotlib
        chart_result = AcademicChartRenderer.render_chart(
            df_wide=df,
            indicator_cols=plot_cols,
            indicator_names=plot_names,
            title=default_title,
            subtitle=default_subtitle,
            units=units,
            chart_type=req.chart_type,
            output_dir=str(out_dir),
            session_id=session_id
        )

        # 8. Exportar datos a CSV
        csv_filename = f"data_{session_id}.csv"
        csv_path = out_dir / csv_filename
        df.to_csv(csv_path, index=False, encoding="utf-8")

        # 9. Generar código Python reproducible
        script_code = PythonCodeGenerator.generate_script(
            indicators=[{"code": c, "column": c, "name": col_to_name.get(c, c)} for c in plot_cols],
            countries=req.countries,
            title=default_title,
            subtitle=default_subtitle,
            units=units,
            chart_type=req.chart_type,
            start_year=req.year_start,
            end_year=req.year_end
        )

        # 10. Calcular estadísticas descriptivas
        stats_summary = {}
        for c in plot_cols:
            series = df[c].dropna()
            if not series.empty:
                stats_summary[c] = {
                    "variable": col_to_name.get(c, c),
                    "min": round(float(series.min()), 2),
                    "max": round(float(series.max()), 2),
                    "mean": round(float(series.mean()), 2),
                    "count": int(series.count())
                }

        # 11. Previsualización de datos (últimos 15 registros)
        preview_records = df.tail(20).fillna("").to_dict(orient="records")

        return GenerateResponse(
            success=True,
            chart_base64=chart_result.get("png_base64") or chart_result.get("image_base64"),
            chart_download_url=f"/api/download/chart/{session_id}",
            svg_download_url=f"/api/download/svg/{session_id}",
            csv_download_url=f"/api/download/csv/{session_id}",
            python_code=script_code,
            data_preview=preview_records,
            statistics=stats_summary,
            metadata={
                "title": default_title,
                "subtitle": default_subtitle,
                "source": chart_result.get("source_note") or "Fuente: Banco Mundial (WDI). Elaboración propia para Desarrollo Económico (UNS).",
                "chart_type": req.chart_type,
                "session_id": session_id,
                "total_rows": len(df)
            }
        )

    except FormulaEvaluationError as fe:
        return GenerateResponse(success=False, error=str(fe))
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return GenerateResponse(success=False, error=f"Error durante el procesamiento: {str(exc)}")


@app.post("/api/databases/search", response_model=DatabaseSearchResponse)
def search_database(req: DatabaseSearchRequest):
    """
    Invoca al agente LLM para buscar y proponer conectores de APIs
    cuando el usuario desea incorporar nuevas bases de datos.
    """
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="La búsqueda no puede estar vacía.")

    try:
        result = analyst_agent.search_database_api(query=q, custom_api_key=req.api_key)
        return DatabaseSearchResponse(
            success=result.get("success", True),
            name=result.get("name", q.title()),
            description=result.get("description", ""),
            api_endpoint=result.get("api_endpoint"),
            auth_type=result.get("auth_type"),
            suggested_indicators=result.get("suggested_indicators", []),
            connector_code=result.get("connector_code"),
            notes=result.get("notes"),
            error=result.get("error")
        )
    except Exception as exc:
        return DatabaseSearchResponse(
            success=False,
            name=q,
            description="No se pudo procesar la solicitud con el agente LLM.",
            error=str(exc)
        )


@app.get("/api/download/csv/{session_id}")
def download_csv(session_id: str):
    csv_file = Path(OUTPUT_DIR) / f"data_{session_id}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="Archivo CSV no encontrado o expirado.")
    return FileResponse(
        csv_file,
        media_type="text/csv",
        filename=f"datos_macro_{session_id}.csv"
    )


@app.get("/api/download/chart/{session_id}")
def download_chart(session_id: str):
    png_file = Path(OUTPUT_DIR) / f"chart_{session_id}.png"
    if not png_file.exists():
        raise HTTPException(status_code=404, detail="Archivo de imagen no encontrado o expirado.")
    return FileResponse(
        png_file,
        media_type="image/png",
        filename=f"grafico_academico_{session_id}.png"
    )


@app.get("/api/download/svg/{session_id}")
def download_svg(session_id: str):
    svg_file = Path(OUTPUT_DIR) / f"chart_{session_id}.svg"
    if not svg_file.exists():
        raise HTTPException(status_code=404, detail="Archivo SVG no encontrado o expirado.")
    return FileResponse(
        svg_file,
        media_type="image/svg+xml",
        filename=f"grafico_academico_{session_id}.svg"
    )
