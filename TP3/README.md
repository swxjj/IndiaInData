# Trabajo Práctico 3: Big Push y Crecimiento Equilibrado vs. Desequilibrado

## Contexto Académico
- **Materia:** Desarrollo Económico (Licenciatura en Economía - UNS)
- **Autor:** Mateo Barros & Grupo de Estudio
- **Bases de datos utilizadas:**
  - **World Bank (World Development Indicators - WDI):** API REST oficial (1960–2025).
  - **EconStats:** Extractor y parser estructurado de series históricas de Argentina (1960–2009).

---

## Estructura del Módulo TP3
```text
TP3/
├── consigna/
│   └── Trabajo Práctico 3.docx                  # Consigna oficial de la cátedra
├── DATOS_INDIA_DESCARGADOS.md                   # Resumen metodológico y estadístico de India
├── data/
│   ├── raw/                                     # Series originales descargadas
│   │   ├── wb_india_indicators_raw.csv          # Series crudas API World Bank para India
│   │   ├── econstats_india_all.csv              # 28.798 observaciones históricas de India
│   │   ├── econstats_india_transport.csv        # Ferrocarril, carreteras, aeropuertos y PPI
│   │   ├── econstats_india_energy.csv           # Electricidad (kWh), carbón, fósil y PPI
│   │   └── econstats_india_communications.csv   # Telefonía, internet, telex e inversión
│   └── processed/                               # Paneles armonizados y normalizados
│       ├── india_crecimiento_inversion.csv      # Parte 1: PIB pc, Inversión bruta y fija, IED
│       ├── india_infraestructura.csv            # Parte 2: Transporte, energía y telecomunicaciones
│       ├── tp3_panel_india.csv                  # Panel consolidado completo (1960–2025)
│       ├── tp3_sector_growth_ind.csv            # Crecimiento sectorial y DE anual (Nurkse vs Hirschman)
│       └── india_tp3_datos.xlsx                 # Libro Excel multi-hoja con formato profesional (5 hojas)
├── output/
│   ├── india_tp3_datos.xlsx                     # Copia directa del Excel para entrega/análisis
│   └── figures/                                 # Gráficos vectoriales / alta resolución (300 DPI)
│       ├── fig1_india_crecimiento_inversion_historico.png
│       ├── fig2_india_transporte_historico.png
│       ├── fig3_india_energia_telecomunicaciones_historico.png
│       ├── fig4_india_big_push_zoom_2000_2015.png
│       ├── fig5_india_crecimiento_sectorial_historico.png
│       └── fig6_india_crecimiento_sectorial_desde_1990.png
├── src/
│   ├── download_india_tp3.py                    # Descarga y exportación CSV/Excel para India
│   ├── plot_india_tp3.py                        # Gráficos académicos de Big Push (India)
│   ├── process_and_plot_growth_india.py         # Pipeline y gráficos de crecimiento sectorial (Parte 2)
│   ├── download_worldbank.py                    # Pipeline general WDI API
│   ├── download_econstats.py                    # Parser general de EconStats
│   ├── process_tp3_data.py                      # Armonización sectorial general
│   └── plot_academic_charts.py                  # Figuras complementarias
└── README.md
```

---

## Ejecución del Pipeline para India

Para reproducir la descarga, exportación y generación de figuras de India:

```powershell
# 1. Descarga oficial (World Bank + EconStats) y exportación a CSV y Excel (Partes 1 y 2)
.\.venv\Scripts\python.exe TP3\src\download_india_tp3.py

# 2. Generación de gráficos académicos de Big Push (históricos y zoom)
.\.venv\Scripts\python.exe TP3\src\plot_india_tp3.py

# 3. Descarga de series sectoriales, cálculo de DE (Nurkse vs Hirschman) y gráficos
.\.venv\Scripts\python.exe TP3\src\process_and_plot_growth_india.py
```
