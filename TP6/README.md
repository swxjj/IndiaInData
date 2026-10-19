# TP6 — Desigualdad y pobreza en India

Primera etapa: fuentes descargadas, datos preparados, controles y gráficos exploratorios.
Consulta: 14 de octubre de 2026. La entrega final en LaTeX queda para la siguiente etapa.

## Organización y forma de trabajo

Se sigue el esquema de TP3–TP5: `consigna/`, `data/raw/`, `data/processed/`, `src/` y `output/figures/`.
La consigna original se conserva en `consigna/`. Las respuestas de las fuentes se guardan
sin transformar, con URL, fecha UTC, tamaño y SHA256 en `data/raw/manifest.json`.
Los CSV se regeneran desde esas descargas. Los gráficos se exportan en PNG y PDF.

La revisión del repositorio muestra módulos por práctico, scripts Python para ingesta y gráficos,
informes LaTeX en TP1/TP3/TP4 y una extensión a Stata en TP5. `macro_chat/` agrega una aplicación
FastAPI para explorar indicadores y generar gráficos. El historial concentra los cambios por TP.
El README de la raíz incluye un índice de los seis prácticos y la aplicación.
Esta revisión es de estructura y flujo de trabajo,
no una auditoría exhaustiva de todos los resultados previos.

## Fuentes y cobertura efectiva

| Variable | Código / fuente | Cobertura | Observaciones |
|---|---|---|---:|
| PIB per cápita PPA, dólares internacionales constantes de 2021 | WDI `NY.GDP.PCAP.PP.KD` | 1990–2025 | 36 |
| Gini | WDI `SI.POV.GINI` | 1993–2023 | 6 |
| Pobreza a USD 3 diarios, PPA 2021 | WDI `SI.POV.DDAY` | 1993–2023 | 6 |
| Pobreza según línea nacional | WDI `SI.POV.NAHC` | 1993–2011 | 4 |
| IPM y dimensiones | PNUD, IPM 2026, Tabla 1 | Encuesta 2019–2021 | 1 |
| Evolución armonizada y diez indicadores | PNUD, IPM 2026, Tabla 2 | 2005–2006, 2015–2016, 2019–2021 | 3 |

- [PNUD: publicación y archivos del IPM 2026](https://hdr.undp.org/content/2026-global-multidimensional-poverty-index).
- [XLSX original, tablas 1 y 2](https://hdr.undp.org/sites/default/files/publications/additional-files/2026-10/2026_gMPI_Table1and2.xlsx).
- [WDI: Gini de India](https://api.worldbank.org/v2/country/IND/indicator/SI.POV.GINI?format=json&source=2).
- [Banco Mundial: metodología de pobreza y desigualdad de India](https://documents1.worldbank.org/curated/en/099060325033540333/pdf/P180633-e1a59178-dc78-4b14-8928-1c88d02240f3.pdf).

Los metadatos WDI descargados indican actualización al 8 de octubre de 2026.
No se interpolan ni extrapolan las series. Los años faltantes permanecen vacíos.

## Primeros hallazgos

### Ingreso, desigualdad y Kuznets

El PIB per cápita pasa de 2.139,83 en 1990 a 10.039,07 en 2025 (aproximadamente 4,69 veces),
en dólares internacionales constantes de 2021. El Gini disponible es:

| Año WDI | Gini |
|---|---:|
| 1993 | 26,1 |
| 2004 | 27,7 |
| 2009 | 27,8 |
| 2011 | 28,8 |
| 2022 | 25,5 |
| 2023 | 23,0 |

La dispersión muestra un ascenso inicial y una caída posterior, visualmente compatibles con
una U invertida. Seis observaciones espaciadas no prueban la hipótesis de Kuznets ni identifican
un efecto causal del desarrollo. Antes de una conclusión fuerte debe revisarse la comparabilidad
entre encuestas. El Gini de India se basa en consumo: no equivale a desigualdad de ingresos o
riqueza. El PIB per cápita tampoco representa el ingreso observado de cada hogar.

### Pobreza multidimensional y monetaria

En la Tabla 1, fila 30, el IPM es 0,06881, su incidencia 16,39% y su intensidad 41,98%.
La pobreza severa afecta al 4,25% y la vulnerabilidad al 18,69%. Son resultados de la encuesta
2019–2021, aunque la edición sea 2026.

La tabla del PNUD informa 5,3% bajo USD 3 diarios y deja la línea nacional sin dato (`..`).
El 5,3% coincide con el valor WDI de 2022; la descarga actual de WDI agrega 2,6% para 2023.
La fuente monetaria de la tabla PNUD fue consultada el 10 de agosto de 2026.
El último valor WDI de pobreza nacional es 21,9% en 2011, fuera de la ventana 2014–2025
indicada en la Tabla 1. Debe presentarse como antecedente histórico, no como dato contemporáneo.

Por tanto, 16,39% es numéricamente mayor que 5,3% y menor que 21,9%, pero las diferencias
mezclan conceptos y años. No permiten medir cuántas personas son pobres por un criterio y no
por otro: eso requiere microdatos conjuntos. Para el ejercicio se conserva el 5,3% publicado
por PNUD, y el 2,6% se informa por separado como actualización WDI.

La serie armonizada del PNUD muestra una caída de la incidencia de 55,07% en 2005–2006
a 27,68% en 2015–2016 y 16,39% en 2019–2021.

### Dimensiones e indicadores

| Dimensión | Contribución al IPM |
|---|---:|
| Nivel de vida | 39,67% |
| Salud | 32,16% |
| Educación | 28,17% |

El mayor indicador individual es nutrición (28,58%), seguido por años de escolaridad (18,71%),
combustible para cocinar (11,22%) y vivienda (10,99%).
La Tabla 2 publica incidencias censuradas: población simultáneamente pobre y privada en cada
indicador, como porcentaje de la población total. No son contribuciones directas al IPM.
Se calcula `contribución (%) = peso × incidencia censurada (%) / IPM`.
Cada indicador de salud y educación pesa 1/6; cada indicador de nivel de vida pesa 1/18.
La suma de las diez contribuciones da 100% y sus agregados coinciden con la Tabla 1.

Como interpretación preliminar, las transferencias pueden aliviar restricciones monetarias,
pero deben complementarse con nutrición, acceso educativo, vivienda, saneamiento y energía
limpia. Estos porcentajes no permiten evaluar eficiencia: faltan costos, focalización y efectos
causales de programas. Tampoco debe confundirse mayor contribución con mayor rendimiento
de cada peso de gasto público.

## Archivos para continuar

- `data/raw/2026_gMPI_Table1and2.xlsx`: libro oficial completo.
- `data/raw/wdi_*.json` y `metadata_*.json`: series y definiciones originales.
- `data/processed/wdi_india_1990_ultimo.csv`: panel anual, con faltantes preservados.
- `data/processed/india_kuznets_observaciones.csv`: seis años emparejados.
- `data/processed/mpi_india_tabla1.csv`: resultados actuales del IPM.
- `data/processed/mpi_india_tendencia_armonizada.csv`: tres encuestas comparables.
- `data/processed/mpi_india_contribuciones.csv`: diez indicadores, pesos y contribuciones por encuesta.
- `data/processed/cobertura_wdi.csv`: cobertura efectiva por variable.
- `data/processed/notas_fuente_mpi.txt`: notas y definiciones extraídas del libro.
- `output/figures/`: evolución temporal, dispersión de Kuznets y contribuciones al IPM, en PNG/PDF.
- `output/tp6_punto2_completo.csv`: todos los datos necesarios para el 2a y 2b, con fuentes,
  períodos y aclaraciones. Separador punto y coma, decimales con coma y UTF-8 para abrir en Excel.

## Reproducción

Desde la raíz, con el entorno del proyecto:

```powershell
.venv/Scripts/python.exe TP6/src/download_tp6_data.py
.venv/Scripts/python.exe TP6/src/process_tp6_data.py
.venv/Scripts/python.exe TP6/src/export_punto2.py
```

La descarga usa la biblioteca estándar. El procesamiento requiere pandas, openpyxl y matplotlib
(ver `TP6/requirements.txt`). Ejecutar solo el segundo comando reproduce los resultados desde
la descarga conservada. El primero actualiza las fuentes y puede cambiar los resultados.
El tercer comando reúne el punto 2 en un único CSV de 22 filas y verifica su contenido.

Validaciones realizadas: respuestas completas de la API, claves únicas, rango del Gini,
identidad IPM = incidencia × intensidad, contribuciones que suman 100% y coincidencia con
las dimensiones oficiales. Los tres gráficos fueron revisados visualmente.

Próxima etapa: desarrollar las respuestas de la consigna, revisar los cambios metodológicos
de las encuestas de consumo y trasladar tablas y gráficos al informe LaTeX.
