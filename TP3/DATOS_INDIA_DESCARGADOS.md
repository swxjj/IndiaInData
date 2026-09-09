# Documentación de Datos Descargados: India (TP3)

## 1. Contexto Académico y Objetivos
- **Materia:** Desarrollo Económico (Licenciatura en Economía - UNS)
- **Tema:** Big Push, Crecimiento Equilibrado (Nurkse) y Crecimiento Desequilibrado (Hirschman).
- **País Analizado:** **India (IND)**.
- **Propósito:** Evaluar si la trayectoria de aceleración del crecimiento de la India a partir de las reformas de 1991 y el posterior despegue de los años 2000 evidencia un proceso coordinado de *Big Push* (salto simultáneo y complementario en inversión e infraestructura básica/redes) o aumentos aislados.

---

## 2. Fuentes de Datos Oficiales y Metodología de Extracción

1. **World Bank - World Development Indicators (WDI):**
   - Extraído vía la API REST oficial en formato JSON/CSV para el código de país `IND`.
   - Cobertura: Series anuales desde 1960 hasta 2025.
   - Indicadores descargados: Crecimiento del PIB per cápita, Formación bruta de capital, Formación bruta de capital fijo, IED neta, acceso a electricidad, agua potable, usuarios de internet, líneas celulares, banda ancha fija, pasajeros aéreos y consumo eléctrico per cápita.

2. **EconStats (Base Histórica WDI India):**
   - URL fuente: `https://www.econstats.com/wdi/wdic_IND.htm`.
   - Extracción y parseo estructurado de **28.798 observaciones históricas** (1960–2009).
   - Categorías clave procesadas:
     - **Transporte (privilegiado en la consigna):** Series de ferrocarril (red en km, tráfico de pasajeros y cargas), red vial (km de rutas y porcentaje pavimentado), transporte aéreo comercial e inversión privada en transporte (PPI).
     - **Energía:** Producción total de electricidad (kWh), matriz por fuentes (carbón, hidroeléctrica, combustibles fósiles) e inversión privada en energía.
     - **Comunicaciones:** Líneas fijas históricas, ratios de inversión sobre ingresos e inversión privada en telecomunicaciones.

---

## 3. Organización en Dos Partes Temáticas

### Parte 1: Tasas de Crecimiento e Inversión
Concentra los indicadores macroeconómicos requeridos para identificar episodios de aceleración sostenida del crecimiento y el comportamiento de la acumulación de capital:

| Columna | Indicador Oficial | Código Fuente | Fuente | Cobertura | Unidad |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `gdp_pcap_growth_pct` | GDP per capita growth (annual %) | `NY.GDP.PCAP.KD.ZG` | World Bank (WDI) | 1961–2025 (n=65) | % anual |
| `gross_capital_formation_pct_gdp` | Gross capital formation (% of GDP) | `NE.GDI.TOTL.ZS` | World Bank (WDI) | 1960–2025 (n=66) | % del PIB |
| `gross_fixed_capital_formation_pct_gdp` | Gross fixed capital formation (% of GDP) | `NE.GDI.FTOT.ZS` | World Bank (WDI) | 1960–2025 (n=66) | % del PIB |
| `fdi_net_inflows_pct_gdp` | Foreign direct investment, net inflows (% of GDP) | `BX.KLT.DINV.WD.GD.ZS` | World Bank (WDI) | 1970–2025 (n=56) | % del PIB |

---

### Parte 2: Infraestructura y Complementariedades
Agrupa variables físicas, de acceso y de redes indispensables para evaluar las indivisibilidades del capital social básico (*Social Overhead Capital*) y la coordinación de inversiones:

#### A. Servicios Básicos y Energía
- `wb_access_electricity_pct_pop`: Acceso a la electricidad (% de la población) [WDI, 1993–2024, n=32].
- `wb_basic_drinking_water_pct_pop`: Personas con acceso a agua potable básica (% pob.) [WDI, 2000–2024, n=25].
- `wb_electric_power_kwh_pc`: Consumo de energía eléctrica per cápita (kWh) [WDI, 1990–2023, n=34].
- `econ_electricity_production_kwh`: Producción total de electricidad (kWh) [EconStats, 1971–2007, n=37].
- `econ_electricity_from_coal_pct`: Electricidad generada a partir de carbón (%) [EconStats, 1971–2007, n=37].
- `econ_electricity_from_hydro_pct`: Electricidad generada por fuentes hidroeléctricas (%) [EconStats, 1971–2007, n=37].
- `econ_fossil_fuel_energy_pct`: Consumo de energía fósil (% del total) [EconStats, 1971–2007, n=37].
- `econ_ppi_energy_usd`: Inversión en energía con participación privada (US$ corrientes) [EconStats, 1991–2008, n=18].

#### B. Comunicaciones y Digitalización
- `wb_internet_users_pct_pop`: Usuarios de Internet (% de la población) [WDI, 1990–2025, n=35].
- `wb_mobile_subscriptions_per_100`: Suscripciones a telefonía celular por cada 100 habitantes [WDI, 1960–2024, n=53].
- `wb_broadband_subscriptions_per_100`: Banda ancha fija por cada 100 habitantes [WDI, 2001–2024, n=24].
- `econ_telephone_lines_per_100`: Líneas de telefonía fija por cada 100 habitantes [EconStats, 1960–2008, n=37].
- `econ_telecom_investment_pct_revenue`: Inversión en telecomunicaciones (% de los ingresos) [EconStats, 1965–2001, n=29].
- `econ_ppi_telecom_usd`: Inversión privada en telecomunicaciones (US$ corrientes) [EconStats, 1994–2008, n=15].

#### C. Transporte (Eje Privilegiado de la Consigna)
- `econ_rail_lines_total_route_km`: Longitud total de líneas de ferrocarril (km de vía) [EconStats, 1980–2008, n=29].
- `econ_railways_passengers_million_km`: Pasajeros transportados por ferrocarril (millones de pasajero-km) [EconStats, 1980–2008, n=29].
- `econ_railways_goods_million_ton_km`: Carga transportada por ferrocarril (millones de ton-km) [EconStats, 1980–2008, n=29].
- `econ_roads_total_network_km`: Red total de carreteras y caminos (km) [EconStats, 1990–2007, n=14].
- `econ_roads_paved_pct`: Rutas y carreteras pavimentadas (% del total) [EconStats, 1991–2002, n=12].
- `wb_air_passengers_carried`: Pasajeros transportados en vuelos comerciales registrados [WDI, 1970–2023, n=54].
- `econ_air_carrier_departures`: Despegues aéreos de transportistas nacionales e internacionales [EconStats, 1970–2008, n=39].
- `econ_air_freight_million_ton_km`: Transporte aéreo de carga (millones de ton-km) [EconStats, 1970–2008, n=39].
- `econ_ppi_transport_usd`: Inversión privada en proyectos de transporte (US$ corrientes) [EconStats, 1990–2008, n=15].

---

## 4. Estructura de Archivos Generados

### A. Archivos en Formato Excel (`.xlsx`)
El archivo principal está disponible con formato profesional, cuadrícula activa y estilos aplicados en:
- `TP3/data/processed/india_tp3_datos.xlsx`
- `TP3/output/india_tp3_datos.xlsx`

**Estructura de hojas:**
1. **`Crecimiento_e_Inversion`:** Panel anual (1960–2025) con PIB per cápita, Formación bruta de capital, Formación bruta fija e IED neta.
2. **`Infraestructura`:** Panel anual con 23 variables de transporte, energía, telecomunicaciones y servicios básicos.
3. **`Panel_Consolidado`:** Unión (*outer join*) de todas las series en un único panel temporal armonizado por año.
4. **`Diccionario_Variables`:** Metadatos completos (código original, nombre en español, nombre en inglés, fuente oficial, cobertura muestral y unidad de medida).

### B. Archivos en Formato CSV (`.csv`)
- **Procesados y armonizados (`TP3/data/processed/`):**
  - `india_crecimiento_inversion.csv`: Parte 1 limpia y pivotada por año.
  - `india_infraestructura.csv`: Parte 2 limpia y pivotada por año.
  - `tp3_panel_india.csv`: Panel consolidado completo de India (1960–2025).
- **Crudos originales (`TP3/data/raw/`):**
  - `wb_india_indicators_raw.csv`: Registros crudos directos de la API del Banco Mundial.
  - `econstats_india_all.csv`: Tabla completa de series de India descargada de EconStats (28.798 obs).
  - `econstats_india_transport.csv`: Subconjunto de series de transporte extraídas de EconStats.
  - `econstats_india_energy.csv`: Subconjunto de series energéticas extraídas de EconStats.
  - `econstats_india_communications.csv`: Subconjunto de series de telecomunicaciones extraídas de EconStats.

### C. Script de Reproducibilidad (`TP3/src/`)
- `download_india_tp3.py`: Script integral y autónomo en Python que automatiza la descarga de APIs, el parseo de HTML de EconStats, la limpieza, el pivoteo y la exportación simultánea a CSV y Excel con formato abierto.

---

## 5. Hallazgos Empíricos Clave para el Análisis Teórico (Big Push en India)

1. **Régimen Pre-Reformas (1960–1990):**
   - El crecimiento del PBI pc rondaba entre 1% y 3.5% anual (el denominado *"Hindu rate of growth"*).
   - La tasa de inversión bruta se ubicaba en niveles modestos (entre 14% y 23% del PIB).
   - La IED era virtualmente nula (<0.1% del PIB) debido a las fuertes restricciones al capital extranjero (*License Raj*).
   - La penetración de telefonía fija no superaba 1 línea por cada 100 habitantes y el consumo eléctrico era inferior a 300 kWh per cápita.

2. **Período de Aceleración Sostenida y Big Push (2003–2011):**
   - **Salto en la Inversión:** La inversión bruta pasó del 24.3% del PIB en 2001 al **40.0% en 2007** y **39.6% en 2011**, manteniéndose por encima del 35% del PIB de forma continuada.
   - **Aceleración del Crecimiento:** El PBI per cápita creció a tasas extraordinarias sostenidas (superiores al 6.5% - 8.5% anual entre 2003 y 2010), cumpliendo el criterio de aceleración sostenida (≥5 años).
   - **Apertura y flujos de capital:** La IED neta saltó desde 0.7% del PIB en 2000 hasta un pico de **3.6% del PIB en 2008**.
   - **Coevolución de Infraestructura y Complementariedades:**
     - La telefonía celular experimentó una difusión masiva: de 0.35 suscripciones por 100 habitantes en 2000 a más de 70 por 100 habitantes hacia 2011, superando el cuello de botella de la infraestructura alámbrica.
     - El transporte aéreo de pasajeros saltó de 13 millones en 2000 a más de 180 millones en 2023.
     - El tráfico de carga ferroviaria se expandió sustancialmente de 300.000 millones de ton-km en los 90 a más de 550.000 millones de ton-km en 2008.
     - El acceso a electricidad avanzó de 50.9% de la población en 1993 a 67.4% en 2005 y 99.9% en la actualidad.

---

## 6. Figuras Académicas Generadas (`TP3/output/figures/`)

Para dar respuesta rigurosa y directa a los puntos 3 y 4 del práctico sin marcas innecesarias (con datos limpios sobre ejes calibrados):

1. **`fig1_india_crecimiento_inversion_historico.png`:**
   - Panel A: Inversión Bruta, Inversión Fija e IED (% del PIB) desde 1960 hasta 2025.
   - Panel B: Crecimiento anual del PIB pc y tendencia de largo plazo (media móvil 5 años).
2. **`fig2_india_transporte_historico.png`:**
   - Panel A: Tráfico ferroviario de cargas (millones ton-km) y pasajeros (millones pas-km) (1980–2008).
   - Panel B: Tráfico aéreo comercial de pasajeros en millones de personas (1970–2023).
3. **`fig3_india_energia_telecomunicaciones_historico.png`:**
   - Panel A: Consumo eléctrico per cápita (kWh) vs. Cobertura de electricidad y agua potable básica (1990–2024).
   - Panel B: Transición de telecomunicaciones – Telefonía fija, telefonía celular, internet y banda ancha (1960–2025).
4. **`fig4_india_big_push_zoom_2000_2015.png` (Zoom al período del Big Push):**
   - Panel A: Detalle anual (2000–2015) del salto en la tasa de inversión (llegando al 42% del PIB) y la aceleración del PIB pc (>6% anual).
   - Panel B: Coevolución sincronizada de redes complementarias indexadas (Base 2000 = 100).
