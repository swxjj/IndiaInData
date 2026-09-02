# IndiaInData
### Applied Macroeconomics & Economic Development Repository

Automated empirical pipeline, econometric data processing, and academic visualization framework developed for the Economic Development curriculum (Licenciatura en Economía, Universidad Nacional del Sur, Argentina).

---

## Overview

IndiaInData organizes empirical investigations into comparative economic development, structural transformation, and long-run growth dynamics. The repository is structured into modular research units corresponding to dedicated coursework deliverables.

```text
IndiaInData/
├── TP1/                        # Module I: Well-Being, HDI & Growth (India vs. United States)
│   ├── TP1.pdf                 # Final compiled report
│   ├── data/
│   │   ├── raw/                # Primary ingested records (World Bank, UNDP, WHR)
│   │   └── processed/          # Harmonized panel data (1960–2025)
│   ├── latex/
│   │   └── tp1_desarrollo_economico.tex
│   ├── output/
│   │   └── figures/            # High-resolution vector (PDF) and raster (PNG) assets
│   └── src/
│       ├── download_data.py
│       └── plotting/
│           └── generate_academic_charts.py
│
├── TP2/                        # Module II: Capital Accumulation & Convergence (India vs. China)
│   ├── data/
│   │   ├── raw/                # WDI time series (1960–2025)
│   │   └── processed/          # Summary benchmarks and full annual dataset (1967–2025)
│   ├── output/
│   │   └── figures/            # Analytical charts (Lineal, Log, Growth, GFCF, ICOR)
│   └── src/
│       └── generate_india_china_analysis.py
│
├── requirements.txt            # Python dependencies
└── README.md                   # Repository documentation
```

---

## Research Modules

### Module I: Well-Being, HDI & Long-Run Expansion (TP1)
* **Focus:** Multidimensional development, subjective well-being (Cantril Ladder), Human Development Index (HDI), and real per capita GDP comparisons between India and the United States (with extensions for Argentina).
* **Deliverable:** `TP1/TP1.pdf`
* **Core Output:** Visualizations and analytical breakdowns covering 1960–2025 in `TP1/output/figures/`.

### Module II: Capital Accumulation, Investment & Growth Dynamics (TP2)
* **Focus:** Comparative evaluation of capital formation, investment effort (Gross Fixed Capital Formation as % of GDP), Incremental Capital-Output Ratios (ICOR), and real per capita GDP trajectory between India and China across the 1967–2025 horizon.
* **Core Findings:**
  * **Initial Conditions (1967):** India real GDP per capita stood at USD 340.08 (constant 2015 prices) versus China at USD 232.93.
  * **Divergence & Crossover:** Following China's 1978 reforms, economic expansion accelerated, crossing India's trajectory in 1983–1984. By 2025, China's real per capita GDP expanded by 59.2x (USD 13,793.21) compared to India's 7.4x expansion (USD 2,523.44).
  * **Investment Regimes:** China sustained an average Gross Fixed Capital Formation rate of 33.38% of GDP (peaking at 44.1% in 2011) versus India's 25.41% average (peaking at 35.8% in 2007).
  * **Capital Efficiency:** Long-run ICOR averaged 4.03 for China and 4.62 for India over 1967–2025.

---

## Core Datasets & Indicators

| Indicator | Coverage | Primary Source | Reference Code |
| :--- | :---: | :--- | :--- |
| Real GDP per capita (constant 2015 USD) | 1960 – 2025 | World Bank (WDI) | `NY.GDP.PCAP.KD` |
| Real GDP per capita growth (annual %) | 1961 – 2025 | World Bank (WDI) | `NY.GDP.PCAP.KD.ZG` |
| Real GDP (constant 2015 USD) | 1960 – 2025 | World Bank (WDI) | `NY.GDP.MKTP.KD` |
| Real GDP growth (annual %) | 1961 – 2025 | World Bank (WDI) | `NY.GDP.MKTP.KD.ZG` |
| Gross Fixed Capital Formation (% of GDP) | 1960 – 2025 | World Bank (WDI) | `NE.GDI.FTOT.ZS` |
| Gross Capital Formation (% of GDP) | 1960 – 2025 | World Bank (WDI) | `NE.GDI.TOTL.ZS` |
| Total Population | 1960 – 2025 | World Bank (WDI) | `SP.POP.TOTL` |
| Human Development Index (HDI) | 1990 – 2023 | UNDP | HDR Office |
| Subjective Life Satisfaction (Cantril Ladder) | 2011 – 2025 | WHR / Gallup | World Happiness Report |

---

## Reproduction & Execution

### 1. Environment Setup
```bash
git clone https://github.com/swxjj/IndiaInData.git
cd IndiaInData
pip install -r requirements.txt
```

### 2. Module I Pipeline (TP1)
```bash
python TP1/src/download_data.py
python TP1/src/plotting/generate_academic_charts.py
```

### 3. Module II Pipeline (TP2)
```bash
python TP2/src/generate_india_china_analysis.py
```

---

## Academic Information

* **Institution:** Universidad Nacional del Sur (UNS)
* **Department:** Departamento de Economía
* **Program:** Licenciatura en Economía
* **Course:** Desarrollo Económico
* **Authors:** Mateo Barros & Study Group
