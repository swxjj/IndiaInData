import sys
from pathlib import Path

# Agregar directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from macro_chat.core.llm_router import LLMRouter
from macro_chat.core.connectors.world_bank import WorldBankConnector
from macro_chat.core.academic_theme import AcademicChartRenderer
from macro_chat.core.code_generator import PythonCodeGenerator

def test_all_chart_types():
    router = LLMRouter()
    conn = WorldBankConnector()
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)

    test_queries = [
        ("1. Barras", "Gráfico de barras comparando la inversión de Argentina, Brasil, Chile y México en 2022", "bar"),
        ("2. Dispersión con tendencia", "Gráfico de dispersión con línea de tendencia entre inversión y crecimiento del PIB para India, China y Estados Unidos", "scatter"),
        ("3. Línea sombreada", "Gráfico de línea con sombreado del ahorro nacional bruto de India desde 1990", "area"),
        ("4. Áreas continuas", "Gráfico de áreas continuas del valor agregado de industria, agro y servicios de India desde 1970", "stacked_area"),
    ]

    for label, q, expected_type in test_queries:
        print(f"\n=== {label} ===")
        parsed = router.parse_query(q)
        print("  Query:", q)
        print("  Parsed chart_type:", parsed["chart_type"])
        assert parsed["chart_type"] == expected_type, f"Expected {expected_type}, got {parsed['chart_type']}"

        df = conn.fetch_series(parsed["indicators"], parsed["countries"], parsed.get("start_year"), parsed.get("end_year"))
        assert not df.empty, f"DF empty for {label}"

        valid_cols = [c for c in [ind["column"] for ind in parsed["indicators"]] if c in df.columns]
        valid_names = [ind["name"] for ind in parsed["indicators"] if ind["column"] in valid_cols]

        res = AcademicChartRenderer.render_chart(
            df_wide=df,
            indicator_cols=valid_cols,
            indicator_names=valid_names,
            title=parsed["title"],
            subtitle=parsed["subtitle"],
            units=parsed["units"],
            chart_type=parsed["chart_type"],
            output_dir=str(out_dir),
            session_id=f"test_{expected_type}"
        )
        assert Path(res["png_path"]).exists()
        print(f"  [OK] Figura generada: {res['png_path']}")

        # Probar generación de script
        script = PythonCodeGenerator.generate_script(
            indicators=[ind for ind in parsed["indicators"] if ind["column"] in valid_cols],
            countries=parsed["countries"],
            title=parsed["title"],
            subtitle=parsed["subtitle"],
            units=parsed["units"],
            chart_type=parsed["chart_type"],
            start_year=parsed.get("start_year"),
            end_year=parsed.get("end_year")
        )
        assert len(script) > 500
        print(f"  [OK] Script reproducible generado ({len(script)} caracteres)")

    print("\n[SUCCESS] ¡TODOS LOS TIPOS DE GRÁFICO FUNCIONAN CORRECTAMENTE!")

if __name__ == "__main__":
    test_all_chart_types()
