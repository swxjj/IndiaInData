# Trabajo Práctico 4: Convergencia y Trampas de Pobreza

## Contexto Académico
- **Materia:** Desarrollo Económico (Licenciatura en Economía -- UNS)
- **Autor:** Mateo Barros & Grupo de Estudio
- **País analizado:** India
- **Bases de datos utilizadas:**
  - **World Bank (World Development Indicators -- WDI):** Indicador `NY.GDP.PCAP.PP.KD` (PIB per cápita a PPA constante 2021 USD), series 1990--2025.

---

## Estructura del Módulo TP4
```text
TP4/
├── consigna/
│   └── Trabajo Práctico 4.docx                  # Consigna original y respuestas de la cátedra
├── data/
│   ├── raw/                                     # Series originales descargadas
│   │   └── wdi_gdp_pcap_ppp_all_raw.csv         # Descarga completa WDI mundial
│   └── processed/                               # Paneles procesados y normalizados
│       ├── convergencia_pbi_1990_2025.csv       # Muestra de 20 países (CSV)
│       ├── convergencia_pbi_1990_2025.xlsx      # Muestra de 20 países (Excel con formato)
│       ├── convergencia_mundial_1990_2025.csv   # Muestra mundial completa (183 países)
│       └── convergencia_mundial_1990_2025.xlsx  # Muestra mundial completa (Excel con formato)
├── output/
│   ├── figures/                                 # Gráficos en alta resolución (300 DPI)
│   │   ├── grafico1_dispersion_logpib90_logpbi25.png     # Parte 2: Nivel 1990 vs 2025 (20 países)
│   │   ├── grafico2_dispersion_logpib90_tasa_promedio.png# Parte 1: Convergencia beta (20 países)
│   │   ├── grafico1_mundial_logpib90_logpbi25.png        # Comparación mundial N=183
│   │   └── grafico2_mundial_logpib90_tasa_promedio.png   # Comparación mundial N=183
│   ├── convergencia_pbi_1990_2025.xlsx
│   └── convergencia_mundial_1990_2025.xlsx
├── src/
│   ├── analisis_convergencia_wdi.py             # Script de procesamiento y gráficos (20 países)
│   └── analisis_convergencia_mundial.py         # Pipeline de análisis mundial (183 países)
├── tp4_india.tex                                # Documento LaTeX listo para compilar
└── README.md
```

---

## Síntesis de Resultados Empíricos

### 1. Muestra de 20 Países (Consigna Principal)
- **Parte 1 (Convergencia $\beta$):**
  - Ecuación estimada: $\hat{y} = -0.0072x + 0.0357$ ($R^2 = 0.3906$, $p = 0.0031$).
  - Pendiente negativa compatible con la hipótesis de convergencia absoluta.
  - India se ubica notablemente por encima de la recta de regresión ($\text{tasa} = 0.0210$ vs. $-0.0072 \times 3.291 + 0.0357 = 0.0120$), siendo la segunda economía de mayor crecimiento del grupo tras Vietnam.
- **Parte 2 (Trampas de Pobreza y Niveles 1990 vs. 2025):**
  - Ecuación estimada: $\hat{y} = 0.7497x + 1.2505$ ($R^2 = 0.8126$).
  - Todos los países están por encima de la recta de 45 grados (mejora en niveles absolutos).
  - India inicia en un nivel bajo ($\log_{10} = 3.29$) cercano a trampas de pobreza previas a 1991, pero despega sostenidamente alcanzando $\log_{10} = 4.03$ en 2025.

### 2. Muestra Mundial ($N = 183$ países)
- Ecuación Gráfico 1: $\hat{y} = 0.8615x + 0.8107$ ($R^2 = 0.7896$).
- Ecuación Gráfico 2: $\hat{y} = -0.0040x + 0.0232$ ($R^2 = 0.0885$, $p = 4.31 \times 10^{-5}$).
