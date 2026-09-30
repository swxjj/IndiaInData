# Trabajo Práctico 5: Medio Ambiente, Instituciones y Desarrollo

## Contexto Académico
- **Materia:** Desarrollo Económico (Licenciatura en Economía -- Universidad Nacional del Sur, UNS)
- **Autor:** Mateo Barros & Grupo de Estudio
- **País Analizado:** India 🇮🇳
- **Bases de Datos Oficiales Utilizadas:**
  1. **Worldwide Governance Indicators (WGI - Banco Mundial):** Los 6 indicadores agregados de gobernabilidad en versión *estimate* (escala estandarizada de aprox. $-2.5$ a $+2.5$), período 1996–2025:
     - Voz y Rendición de Cuentas (`voice_accountability` / `GOV_WGI_VA.EST`)
     - Estabilidad Política y Ausencia de Violencia (`political_stability` / `GOV_WGI_PV.EST`)
     - Eficacia del Gobierno (`government_effectiveness` / `GOV_WGI_GE.EST`)
     - Calidad Regulatoria (`regulatory_quality` / `GOV_WGI_RQ.EST`)
     - Estado de Derecho (`rule_of_law` / `GOV_WGI_RL.EST`)
     - Control de la Corrupción (`control_of_corruption` / `GOV_WGI_CC.EST`)
  2. **World Development Indicators (WDI - Banco Mundial):**
     - PIB per cápita a PPA constante 2021 USD (`NY.GDP.PCAP.PP.KD`) y constante 2015 USD (`NY.GDP.PCAP.KD`)
     - Logaritmo natural del PIB per cápita: $\ln(\text{PIBpc})$
     - Inversión / Formación Bruta de Capital Fijo (% del PIB) (`NE.GDI.FTOT.ZS`)
     - Inversión Bruta Total (% del PIB) (`NE.GDI.TOTL.ZS`)
     - Gasto público en educación (% del PIB) (`SE.XPD.TOTL.GD.ZS`) original UNESCO/WB y versión interpolada linealmente (`gasto_educ_interp`) para preservar los 27 años sin pérdida muestral
     - Apertura Financiera: IED neta entradas (% del PIB) (`BX.KLT.DINV.WD.GD.ZS`) y flujos totales brutos (`aper_fin_tot`)
     - Apertura Comercial (% del PIB) (`NE.TRD.GNFS.ZS`)
  3. **Global Footprint Network (National Footprint and Biocapacity Accounts):**
     - Huella Ecológica de Consumo per cápita (*Total Ecological Footprint of Consumption*, gha/persona) y sus 6 componentes (Carbono, Cultivos, Pastizales, Bosques, Pesca, Urbano).
     - Biocapacidad per cápita (*Total Biocapacity*, gha/persona) y componentes biofísicos.
     - Balance Ecológico ($\text{Biocapacidad} - \text{Huella Ecológica}$) y Ratio Huella/Biocapacidad (1961–2025).

---

## Estructura del Módulo TP5

```text
TP5/
├── consigna/
│   └── TP 5.docx                               # Consigna oficial de la cátedra
├── data/
│   ├── raw/                                    # Descargas primarias de APIs oficiales
│   │   ├── wgi_india_raw.csv                   # WGI 6 dimensiones en formato largo
│   │   ├── wdi_india_raw.csv                   # WDI series macroeconómicas de control
│   │   └── footprint_india_raw.csv             # GFN series completas 1961-2025
│   └── processed/                              # Paneles normalizados y homogeneizados
│       ├── tp5_india_instituciones_desarrollo.csv  # Panel WGI + WDI + ln(PIBpc)
│       ├── tp5_india_instituciones_desarrollo.xlsx # Versión Excel formateada
│       ├── tp5_india_medio_ambiente.csv            # Panel Footprint + Balance ecológico
│       ├── tp5_india_medio_ambiente.xlsx           # Versión Excel formateada
│       ├── tp5_india_dataset_completo.csv          # Panel maestro integrado (1961-2025)
│       ├── tp5_india_dataset_completo.xlsx         # Versión Excel formateada
│       ├── tp5_india_stata.csv                     # Dataset listo para Stata (niveles brutos)
│       └── tp5_india_stata.dta                     # Dataset nativo Stata con etiquetas
├── output/
│   ├── figures/                                # Figuras académicas en alta resolución (300 DPI y PDF)
│   │   ├── grafico1_wgi_series_temporales.png           # Evolución 6 dimensiones WGI (1996-2025)
│   │   ├── grafico1_wgi_series_temporales.pdf
│   │   ├── grafico2_pib_vs_gobernabilidad_promedio.png   # ln(PIBpc) vs Índice WGI Promedio
│   │   ├── grafico2_pib_vs_gobernabilidad_promedio.pdf
│   │   ├── grafico3_matriz_correlaciones_pearson.png     # Heatmap de correlaciones bivariadas
│   │   ├── grafico3_matriz_correlaciones_pearson.pdf
│   │   ├── grafico4_panel_dispersion_instituciones_pib.png# Panel 2x3 de dispersión bivariada
│   │   ├── grafico4_panel_dispersion_instituciones_pib.pdf
│   │   ├── grafico5_huella_ecologica_vs_biocapacidad.png # Huella vs Biocapacidad y déficit
│   │   ├── grafico5_huella_ecologica_vs_biocapacidad.pdf
│   │   ├── grafico6_composicion_huella_ecologica.png     # Descomposición de huella por componentes
│   │   └── grafico6_composicion_huella_ecologica.pdf
│   ├── tp5_india_instituciones_desarrollo.xlsx
│   ├── tp5_india_medio_ambiente.xlsx
│   ├── tp5_india_dataset_completo.xlsx
│   ├── tp5_india_stata.csv
│   ├── tp5_india_stata.dta
│   └── tp5_india_analisis.do                   # Script de análisis econométrico en Stata
├── src/
│   ├── download_tp5_data.py                    # Pipeline de ingesta, armonización y guardado
│   ├── export_stata_dataset.py                 # Pipeline de exportación limpia y etiquetado Stata
│   ├── plot_tp5_graficos.py                    # Pipeline gráfico y estadístico descriptivo
│   └── tp5_india_analisis.do                   # Script Stata reproducible con controles
└── README.md
```

---

## Síntesis del Análisis Gráfico y Correlaciones

### Parte 1: Instituciones y Desarrollo Económico en India (1996–2025)

1. **Jerarquía de Correlaciones con el PIB per cápita ($\ln(\text{PIBpc})$):**
   * **Eficacia del Gobierno (`government_effectiveness`):** $r = +0.950$ ($p < 0.001$). Es la dimensión con mayor correlación positiva. El fortalecimiento de la capacidad burocrática del Estado, la digitalización de servicios públicos (*India Stack*, Aadhaar, UPI) y la entrega de transferencias directas acompañaron estrechamente el despegue económico.
   * **Calidad Regulatoria (`regulatory_quality`):** $r = +0.794$ ($p < 0.001$). Fuerte correlación positiva, reflejando el impacto de la desregulación industrial, la simplificación tributaria (reforma del GST) y la apertura comercial tras las reformas pro-mercado iniciadas en los años noventa.
   * **Estabilidad Política (`political_stability`):** $r = +0.655$ ($p < 0.001$). Correlación positiva moderada-alta. Pese a que India mantiene un puntaje negativo en niveles absolutos por tensiones geopolíticas regionales, la estabilidad de las coaliciones de gobierno y la consolidación parlamentaria reciente favorecieron el crecimiento.
   * **Control de la Corrupción (`control_of_corruption`):** $r = +0.189$ ($p = 0.344$, no significativa en análisis bivariado simple). Presenta oscilaciones cíclicas sin un patrón lineal definido frente al PIB per cápita.
   * **Voz y Rendición de Cuentas (`voice_accountability`):** $r = -0.389$ ($p = 0.045$). Correlación moderadamente negativa. Mientras India expandió su PIB a tasas superiores al $6\%$ anual, los índices internacionales registraron erosiones relativas en libertad de prensa, espacio cívico y pluralismo institucional.
   * **Estado de Derecho (`rule_of_law`):** $r = -0.661$ ($p < 0.001$). Fuerte correlación negativa contraintuitiva. La congestión judicial crónica (más de 40 millones de causas acumuladas en tribunales indios), la complejidad en la ejecución de contratos y los conflictos en derechos de propiedad sobre la tierra se agravaron proporcionalmente a la masa crítica de la actividad económica mercantil.

---

### Parte 2: Medio Ambiente y Balance Ecológico (1961–2025)

1. **Condición Ecológica Estructural:**
   * India se encuentra en **condición deficitaria ininterrumpida durante los 65 años de la serie (1961–2025)** ($\text{Huella Ecológica} > \text{Biocapacidad}$).
2. **Profundización del Déficit Ecológico:**
   * **1961:** Huella ecológica de $0.54\text{ gha/hab}$ frente a una biocapacidad de $0.42\text{ gha/hab}$ (Déficit de $-0.12\text{ gha/hab}$, ratio $1.30\times$).
   * **2025:** Huella ecológica de $1.13\text{ gha/hab}$ frente a una biocapacidad de $0.38\text{ gha/hab}$ (Déficit de $-0.75\text{ gha/hab}$, ratio $2.97\times$).
   * India consume hoy casi **tres veces su biocapacidad doméstica regenerativa**.
3. **Causas del Deterioro:**
   * **Expansión de la Huella de Carbono:** De representar $0.09\text{ gha/hab}$ en 1961 pasó a más de $0.67\text{ gha/hab}$ en 2025, explicando más del $60\%$ del incremento total de la huella ecológica debido a la matriz energética basada en carbón y la rápida industrialización.
   * **Presión Demográfica:** La población india se triplicó holgadamente (de 450 millones en 1961 a más de 1.440 millones en 2025), provocando que la biocapacidad *per cápita* cayera por efecto de dilución poblacional, a pesar de las ganancias de rendimiento agrario logradas por la Revolución Verde.
