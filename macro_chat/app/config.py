import os
from pathlib import Path

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Intentar cargar macro_chat/.env o el .env del directorio raíz
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(BASE_DIR.parent / ".env")
except ImportError:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de Entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CLASS_PIN = os.getenv("CLASS_PIN", "desarrollo2026")  # PIN de acceso simple para las clases
OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(BASE_DIR / "output"))
STATIC_DIR = os.getenv("STATIC_DIR", str(BASE_DIR / "static"))

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)
