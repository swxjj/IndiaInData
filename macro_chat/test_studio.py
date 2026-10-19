"""
Test de Integración para MacroData Studio:
- Catálogo API
- Generación de Gráfico con Banco Mundial
- Evaluación de Fórmulas Econométricas
- Agente LLM para búsqueda de Bases de Datos
"""
from fastapi.testclient import TestClient
from macro_chat.app.main import app

client = TestClient(app)

def test_catalog():
    print("\n--- 1. Probando /api/catalog ---")
    resp = client.get("/api/catalog")
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "databases" in data
    assert "categories" in data
    assert "indicators" in data
    assert "countries" in data
    assert "chart_types" in data
    print(f"OK: {len(data['indicators'])} indicadores, {len(data['countries'])} países, {len(data['categories'])} categorías.")

def test_generate_simple():
    print("\n--- 2. Probando /api/generate (Líneas: India vs China) ---")
    payload = {
        "database": "world_bank",
        "variables": ["NY.GDP.PCAP.KD"],
        "countries": ["IND", "CHN"],
        "year_start": 2000,
        "year_end": 2020,
        "chart_type": "line"
    }
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["success"] is True, f"Error en generación: {data.get('error')}"
    assert data["chart_base64"] is not None
    assert data["python_code"] is not None
    assert len(data["data_preview"]) > 0
    print(f"OK: Gráfico generado exitosamente ({len(data['chart_base64'])} chars base64, {data['metadata']['total_rows']} filas).")

def test_generate_with_formula():
    print("\n--- 3. Probando /api/generate con Fórmula Econométrica ---")
    payload = {
        "database": "world_bank",
        "variables": ["pib_per_capita", "log_pib_pc"],
        "countries": ["ARG", "BRA"],
        "year_start": 2000,
        "year_end": 2020,
        "chart_type": "line",
        "formulas": [
            {
                "name": "log_pib_pc",
                "expression": "log(pib_per_capita)",
                "label": "Logaritmo del PIB per cápita",
                "units": "Log USD"
            }
        ]
    }
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["success"] is True, f"Error en generación con fórmula: {data.get('error')}"
    print(f"OK: Fórmula evaluada con éxito! Columnas calculadas y graficadas.")

def test_database_search():
    print("\n--- 4. Probando /api/databases/search con Agente LLM ---")
    resp = client.post("/api/databases/search", json={"query": "FRED"})
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["success"] is True
    assert "FRED" in data["name"]
    assert data["api_endpoint"] is not None
    assert len(data["suggested_indicators"]) > 0
    print(f"OK: Base de datos investigada: {data['name']} -> {data['api_endpoint']}")

if __name__ == "__main__":
    test_catalog()
    test_generate_simple()
    test_generate_with_formula()
    test_database_search()
    print("\n>>> TODOS LOS TESTS PASARON EXITOSAMENTE! <<<")
