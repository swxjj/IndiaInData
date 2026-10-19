import sys
from pathlib import Path

# Agregar directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from macro_chat.core.connectors.world_bank import WorldBankConnector
from macro_chat.core.academic_theme import AcademicChartRenderer
from macro_chat.core.code_generator import PythonCodeGenerator
from macro_chat.core.llm_router import LLMRouter

def test_full_pipeline():
    print("=== 1. Probando LLMRouter (Heurístico / Lenguaje Natural) ===")
    router = LLMRouter()
    query = "Armame un gráfico de inversión y PIB per cápita para India y China desde 2015 a 2022"
    parsed = router.parse_query(query)
    print("Parsed Query:", parsed)
    assert len(parsed["countries"]) >= 2
    assert len(parsed["indicators"]) >= 1

    print("\n=== 2. Probando WorldBankConnector (Descarga en vivo de API WDI) ===")
    connector = WorldBankConnector()
    df_wide = connector.fetch_series(
        indicators=parsed["indicators"],
        countries=parsed["countries"],
        start_year=2018,
        end_year=2022
    )
    print("DataFrame descargado (primeras filas):")
    print(df_wide.head())
    assert not df_wide.empty
    assert "anio" in df_wide.columns
    assert "pais" in df_wide.columns

    print("\n=== 3. Probando AcademicChartRenderer (Renderizado y CSV Wide) ===")
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)

    indicator_cols = [ind.get("column", ind["code"].lower().replace(".", "_")) for ind in parsed["indicators"]]
    indicator_names = [ind.get("name", ind["code"]) for ind in parsed["indicators"]]

    result = AcademicChartRenderer.render_chart(
        df_wide=df_wide,
        indicator_cols=indicator_cols,
        indicator_names=indicator_names,
        title="Test: Inversión y PIB per Cápita",
        subtitle="Series 2018-2022",
        source_note="Fuente: Banco Mundial (WDI). Test Automatizado.",
        units=parsed.get("units"),
        output_dir=str(out_dir),
        session_id="test_session"
    )
    print("Chart Base64 length:", len(result["png_base64"]))
    assert Path(result["png_path"]).exists()
    assert Path(result["svg_path"]).exists()
    assert Path(result["csv_path"]).exists()
    print("Archivos generados con éxito:", result["png_path"], result["csv_path"])

    print("\n=== 4. Probando PythonCodeGenerator ===")
    script = PythonCodeGenerator.generate_script(
        indicators=parsed["indicators"],
        countries=parsed["countries"],
        title="Test: Inversión y PIB per Cápita",
        subtitle="Series 2018-2022",
        units=parsed.get("units"),
        start_year=2018,
        end_year=2022
    )
    assert "fetch_wdi_data" in script
    assert "plt.savefig" in script
    print("Script Python generado correctamente (longitud:", len(script), "caracteres)")

    print("\n[OK] TODOS LOS TESTS PASARON EXITOSAMENTE.")

if __name__ == "__main__":
    test_full_pipeline()
