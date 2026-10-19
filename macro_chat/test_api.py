import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Agregar directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from macro_chat.app.main import app

client = TestClient(app)

def test_api():
    print("=== 1. Probando /api/health ===")
    res = client.get("/api/health")
    assert res.status_code == 200
    print("Health response:", res.json())

    print("\n=== 2. Probando /api/catalog ===")
    res_cat = client.get("/api/catalog")
    assert res_cat.status_code == 200
    cat_data = res_cat.json()
    assert "databases" in cat_data
    assert "indicators" in cat_data
    assert "countries" in cat_data
    print(f"Catálogo verificado ({len(cat_data['indicators'])} indicadores, {len(cat_data['countries'])} países)")

    print("\n=== 3. Probando /api/generate con PIN inválido ===")
    res_inv = client.post("/api/generate", json={
        "database": "world_bank",
        "variables": ["NY.GDP.PCAP.KD"],
        "countries": ["IND"],
        "pin": "clave_falsa"
    })
    assert res_inv.status_code == 401
    print("PIN inválido rechazado correctamente (401)")

    print("\n=== 4. Probando /api/generate con PIN válido ===")
    res = client.post("/api/generate", json={
        "database": "world_bank",
        "variables": ["NY.GDP.PCAP.KD"],
        "countries": ["IND", "USA"],
        "year_start": 2019,
        "year_end": 2022,
        "chart_type": "line",
        "pin": "desarrollo2026"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["chart_base64"] is not None
    assert data["csv_download_url"] is not None
    print("Generación exitosa. Filas preview:", len(data["data_preview"]))
    print("Download URL:", data["csv_download_url"])

    print("\n=== 5. Probando descarga de CSV ===")
    csv_url = data["csv_download_url"]
    res_csv = client.get(csv_url)
    assert res_csv.status_code == 200
    assert "anio,pais,codigo_pais" in res_csv.text
    print("Descarga de CSV verificada (longitud:", len(res_csv.text), "bytes)")

    print("\n=== 6. Probando /api/databases/search ===")
    res_db = client.post("/api/databases/search", json={"query": "FRED"})
    assert res_db.status_code == 200
    db_data = res_db.json()
    assert db_data["success"] is True
    print("Búsqueda de BD verificada:", db_data["name"])

    print("\n=== 7. Probando ruta raíz / ===")
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "MacroData Studio" in res_root.text
    print("Ruta raíz index.html servida correctamente")

    print("\n[OK] TODOS LOS TESTS DE API PASARON.")

if __name__ == "__main__":
    test_api()
