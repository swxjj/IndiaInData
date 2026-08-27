# 📊 IndiaInData: Macroeconomic Data & Development Analytics Hub

Repositorio de procesamiento automatizado, análisis econométrico y visualización académica de series macroeconómicas y de bienestar con foco principal en **India 🇮🇳** y comparación con **Estados Unidos 🇺🇸** (con soporte para extensiones a **Argentina 🇦🇷**).

Diseñado para el desarrollo de actividades y entregas de la materia **Desarrollo Económico** (Licenciatura en Economía - **Universidad Nacional del Sur, UNS**).

---

## 📄 Entregable Oficial: Trabajo Práctico N° 1 (TP1)

* 📄 **Documento Final Compilado:** [`TP1.pdf`](TP1.pdf) *(disponible directamente en la raíz del repositorio)*.
* 📝 **Código Fuente LaTeX:** [`latex/tp1_desarrollo_economico.tex`](latex/tp1_desarrollo_economico.tex).

---

## 🚀 Estructura Limpia del Repositorio

```text
IndiaInData/
├── TP1.pdf                  # Documento final compilado del Trabajo Práctico N° 1
├── data/
│   ├── raw/                 # Datos brutos descargados de APIs oficiales (Banco Mundial, PNUD, WHR)
│   └── processed/           # Paneles consolidados (1960–2025)
│       ├── macro_panel_india_usa.csv
│       ├── india_macro.csv
│       └── usa_macro.csv
├── latex/
│   └── tp1_desarrollo_economico.tex # Código fuente LaTeX listo para compilar
├── output/
│   └── figures/             # Gráficos académicos vectoriales (.pdf) e imágenes (.png 300 DPI)
│       ├── 01_hdi_india_vs_usa.[pdf|png]
│       ├── 02_gdp_india_vs_usa.[pdf|png]
│       ├── 03_happiness_india_vs_usa.[pdf|png]
│       ├── 04_happiness_india.[pdf|png]
│       └── 05_hdi_and_gdp_india.[pdf|png]
├── src/
│   ├── download_data.py     # Pipeline automatizado de descarga e ingesta
│   └── plotting/
│       └── generate_academic_charts.py # Generador de gráficos académicos
├── product.md               # Especificación funcional y de diseño del proyecto
├── requirements.txt         # Dependencias del entorno Python
└── README.md                # Documentación del proyecto
```

---

## 📈 Indicadores y Fuentes de Datos

| Indicador | Cobertura Temporal | Fuente Primaria |
| :--- | :---: | :--- |
| **PIB per cápita (USD Const. 2015)** | 1960 – 2025 | Banco Mundial (*WDI*, cod. `NY.GDP.PCAP.KD`) |
| **PIB per cápita (PPA Const. 2021 $)** | 1990 – 2025 | Banco Mundial (*WDI*, cod. `NY.GDP.PCAP.PP.KD`) |
| **Índice de Desarrollo Humano (IDH)** | 1990 – 2023 | PNUD (*UNDP Human Development Report Office*) |
| **Satisfacción de Vida Autopercibida** | 2011 – 2025 | *Gallup World Poll* / *World Happiness Report* |

---

## ⚙️ Instrucciones de Uso y Reproducción

### 1. Clonar el repositorio
```bash
git clone https://github.com/swxjj/IndiaInData.git
cd IndiaInData
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Descarga y actualización de datos
```bash
python src/download_data.py
```

### 4. Regeneración de gráficos
```bash
python src/plotting/generate_academic_charts.py
```

---

## 🎓 Contexto Académico
* **Institución:** Universidad Nacional del Sur (UNS) -- Departamento de Economía.
* **Materia:** Desarrollo Económico.
* **Carrera:** Licenciatura en Economía.
* **Autor:** Mateo Barros y Grupo de Trabajo.
