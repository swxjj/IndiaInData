# 📊 IndiaInData: Macroeconomic Data & Development Analytics Hub

Repositorio de procesamiento automatizado, análisis econométrico y visualización académica de series macroeconómicas y de bienestar con foco principal en **India 🇮🇳** y comparación con **Estados Unidos 🇺🇸** (y futuras extensiones para **Argentina 🇦🇷**).

Diseñado para la generación de insumos empíricos, tablas y figuras para las actividades de la materia **Desarrollo Económico** (Licenciatura en Economía - **Universidad Nacional del Sur, UNS**).

---

## 🚀 Estructura del Proyecto

```text
IndiaInData/
├── data/
│   ├── raw/                 # Datos brutos descargados de APIs oficiales
│   │   ├── cantril_ladder_whr_raw.csv
│   │   ├── gdp_per_capita_constant_2015_usd_worldbank.csv
│   │   ├── gdp_per_capita_ppp_constant_2021_worldbank.csv
│   │   └── hdi_undp_raw.csv
│   └── processed/           # Paneles consolidados y limpios
│       ├── macro_panel_india_usa.csv
│       ├── india_macro.csv
│       └── usa_macro.csv
├── output/
│   └── figures/             # Gráficos de calidad académica (.pdf y .png a 300 DPI)
│       ├── 01_hdi_india_vs_usa.[pdf|png]
│       ├── 02_gdp_india_vs_usa.[pdf|png]
│       ├── 03_happiness_india_vs_usa.[pdf|png]
│       ├── 04_happiness_india.[pdf|png]
│       └── 05_hdi_and_gdp_india.[pdf|png]
├── src/
│   ├── download_data.py     # Pipeline de descarga e ingesta de datos
│   └── plotting/
│       └── generate_academic_charts.py # Generador de figuras con estilo paper
├── product.md               # Especificación funcional y técnica
├── requirements.txt         # Dependencias del entorno
└── README.md                # Documentación del proyecto
```

---

## 📈 Indicadores y Fuentes de Datos

| Indicador | Cobertura Temporal | Fuente Primaria |
| :--- | :---: | :--- |
| **PIB per cápita (USD Const. 2015)** | 1960 – 2025 | Banco Mundial (*WDI*, cod. `NY.GDP.PCAP.KD`) |
| **PIB per cápita (PPA Const. 2021 $)** | 1990 – 2025 | Banco Mundial (*WDI*, cod. `NY.GDP.PCAP.PP.KD`) |
| **Índice de Desarrollo Humano (IDH)** | 1990 – 2023 | PNUD (*UNDP Human Development Report Office*) |
| **Escalera de Cantril (Satisfacción de Vida)** | 2011 – 2025 | *Gallup World Poll* / *World Happiness Report* |

---

## 🎨 Sistema de Diseño Visual (Enfoque A: Identidad por País)

Todos los gráficos cumplen con estándares editoriales para *papers* y publicaciones académicas:
* **India 🇮🇳:** Color Terracota (`#C0392B`), marcador circular (`●`), línea sólida.
* **Estados Unidos 🇺🇸:** Color Azul Marino (`#1B4F72`), marcador cuadrado (`■`), línea sólida.
* **Doble Eje (`twinx`):** Aplicado en comparaciones con diferente orden de magnitud (PIB per cápita) o distinta dimensión teórica (IDH vs. PIB monetario).
* **Formatos de Salida:** Vectorial `.pdf` para inclusión directa en LaTeX (sin pixelado) e imágenes `.png` a 300 DPI.

---

## ⚙️ Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/swxjj/IndiaInData.git
cd IndiaInData
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar descarga y actualización de datos
```bash
python src/download_data.py
```

### 4. Regenerar todos los gráficos
```bash
python src/plotting/generate_academic_charts.py
```

---

## 📑 Inclusión de Figuras en LaTeX

Para incluir cualquiera de las figuras vectoriales generadas en un documento LaTeX de la materia:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.85\textwidth]{output/figures/05_hdi_and_gdp_india.pdf}
    \caption{Crecimiento Económico y Desarrollo Humano en India (1960--2025)}
    \label{fig:hdi_gdp_india}
\end{figure}
```

---

## 🎓 Contexto Académico
* **Institución:** Universidad Nacional del Sur (UNS) - Departamento de Economía.
* **Materia:** Desarrollo Económico.
* **Carrera:** Licenciatura en Economía.
