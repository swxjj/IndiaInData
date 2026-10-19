# MacroData Academic Studio (`macro_chat`)

Plataforma analítica y entorno interactivo para la cátedra de **Desarrollo Económico (UNS)**.
Permite a estudiantes e investigadores seleccionar variables macroeconómicas mediante un **dashboard estructurado**, construir variables derivadas con un **motor de fórmulas econométricas**, y generar de forma instantánea:

1. **Gráfico Académico:** Renderizado determinista con estética sobria (*Journal of Economic Perspectives* / NBER), en alta resolución (300 DPI), formato PNG/SVG, con títulos en español y nota de fuente obligatoria.
2. **Dataset en CSV:** Formato Panel Ancho (*Wide Panel*) directamente importable en Stata, R, pandas o Excel (`anio, pais, [variables]`).
3. **Código Python Reproducible:** Script autosuficiente con código de descarga y ploteo para incluir en las entregas de los TPs.
4. **Conexión de Nuevas APIs:** Agente LLM (Google Gemini) que investiga endpoints, documentación y genera conectores cuando se necesita incorporar nuevas bases (FRED, FMI, CEPAL, etc.).

---

## 🚀 Ejecución Local

### 1. Requisitos Previos
Asegúrate de tener Python 3.10+ y las dependencias instaladas en el entorno virtual:

```bash
cd d:/mateo/IndiaInData
.venv\Scripts\pip install -r macro_chat/requirements.txt
```

### 2. Configurar Variables de Entorno (Opcional)
Copia el archivo `.env.example` a `.env`:
```bash
cp macro_chat/.env.example macro_chat/.env
```
* `GEMINI_API_KEY`: Tu clave de [Google AI Studio](https://aistudio.google.com). *(Si no se proporciona, el sistema opera con catálogo heurístico y base de conocimiento offline).*
* `CLASS_PIN`: Clave de acceso simple para las clases (por defecto `desarrollo2026`).

### 3. Iniciar el Servidor
```bash
.venv\Scripts\python.exe -m uvicorn macro_chat.app.main:app --reload --port 8000
```
Accede desde tu navegador a: **`http://localhost:8000`**.

---

## 🏛️ Arquitectura del Sistema

```text
macro_chat/
├── app/
│   ├── main.py              # Endpoints FastAPI (/api/catalog, /api/generate, /api/databases/search)
│   ├── schemas.py           # Modelos Pydantic v2
│   └── config.py            # Variables de entorno y rutas
├── core/
│   ├── catalog.py           # Catálogo centralizado: 20+ indicadores, 40+ países, categorías
│   ├── formula_engine.py    # Evaluación segura de fórmulas (AST, whitelist matemático)
│   ├── academic_theme.py    # Renderizador Matplotlib (NBER / JEP, paleta académica sobria)
│   ├── code_generator.py    # Generador de scripts Python reproducibles
│   ├── agent_analyst.py     # Agente LLM para investigación de nuevas bases de datos
│   └── connectors/
│       ├── base.py          # Interfaz abstracta para conectores
│       └── world_bank.py    # Conector oficial Banco Mundial (WDI API)
├── static/
│   ├── index.html           # Dashboard Studio UI
│   ├── style.css            # Estética académica moderna con CSS Grid
│   └── app.js               # Lógica reactiva de selección, fórmulas y visualización
├── test_studio.py           # Test suite de integración de MacroData Studio
└── test_api.py              # Tests de endpoints REST
```

---

## 📐 Endpoints Principales

| Endpoint | Método | Descripción |
|---|---|---|
| `GET /api/catalog` | GET | Retorna catálogo de indicadores agrupados por categoría, países y tipos de gráfico. |
| `POST /api/generate` | POST | Recibe variables, países, años, tipo de gráfico y fórmulas. Descarga datos, computa fórmulas y devuelve gráfico base64 + enlaces. |
| `POST /api/databases/search` | POST | Consulta al agente LLM para buscar endpoints y documentación de nuevas APIs. |
| `GET /api/download/csv/{id}` | GET | Descarga el dataset generado en formato CSV Panel Ancho. |
| `GET /api/download/chart/{id}` | GET | Descarga la figura en alta resolución (PNG 300 DPI). |
| `GET /api/download/svg/{id}` | GET | Descarga la figura en formato vectorial SVG. |

---

## 🌐 Despliegue Aislado (Scale-to-Zero)

Dado que el uso se concentra los días de clase (**miércoles**), la aplicación puede desplegarse en **Google Cloud Run** o **Fly.io** con `min-instances 0` para costo $0 en días de inactividad:

```bash
gcloud run deploy macro-studio \
  --source . \
  --dockerfile macro_chat/Dockerfile \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars GEMINI_API_KEY="AIzaSy...",CLASS_PIN="desarrollo2026"
```
