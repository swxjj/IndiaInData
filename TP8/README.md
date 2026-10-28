# TP8 — Población, género y desarrollo

Bases descargadas el **27 de octubre de 2026** para preparar el práctico.
El **28 de octubre de 2026** se agregó la tasa de crecimiento poblacional total
WDI `SP.POP.GROW`, en porcentaje anual, con datos de 1961–2025 en ambos países.
País principal: **India (`IND`)**. Comparación inicial: **Estados Unidos (`USA`)**,
siguiendo el TP1. La consigna pide dos países, pero no fija el segundo.
El archivo global del PNUD permite elegir otro comparador más adelante.

La preparación incluye descargas, metadatos, organización y controles. El 28 de
octubre se agregó el cálculo de crecimiento natural y tres gráficos de India
para compararlo con el crecimiento total. La resolución final está en
[output/pdf/TP8.pdf](output/pdf/TP8.pdf), con su código en [latex/main.tex](latex/main.tex).

## Organización

```text
TP8/
  consigna/         Consigna original y texto extraído, incluida la fórmula
  data/raw/         Respuestas oficiales, tablas PNUD y manifiesto de descargas
  data/processed/
    main_punto_1.csv  Base principal de demografía y dependencia
    main_punto_2.csv  Base principal de migración y divisas
    apoyo/            Panel completo, diccionario, cobertura y datos auxiliares
    genero/           Bases del punto 3 sobre desigualdad de género
  resolucion/       Word original y extracción usada para generar el LaTeX
  latex/            Código principal de la entrega
  output/           PDF final, figuras y tabla
  src/              Scripts de descarga, gráficos y preparación reproducible
  requirements.txt  Dependencia para leer los XLSX oficiales
```

El DOCX de la consigna se copió a `consigna/TP 8.docx` y se verificó por SHA256.
La resolución Word original se conserva en `resolucion/`. Se eliminaron las copias
duplicadas de la raíz y se conserva un único PDF final en `output/pdf/TP8.pdf`.

## Qué descargar según la consigna

| Parte | Datos preparados | Fuentes |
|---|---|---|
| Crecimiento y transición demográfica | Natalidad, mortalidad, población total, grupos de edad, dependencia total/joven/mayor, fecundidad y esperanza de vida | Banco Mundial, WDI |
| Migración | Migración neta anual de los dos países | Banco Mundial, WDI, a partir de Naciones Unidas |
| Remesas y entradas de divisas | Remesas recibidas, PIB, formación bruta de capital fijo, exportaciones, IED, deuda y ayuda oficial al desarrollo recibida | WDI e International Debt Statistics |
| Género | GII, mortalidad materna, natalidad adolescente, bancas parlamentarias, educación secundaria y participación laboral por sexo | PNUD, HDR 2025 |

Se descargaron **25 indicadores del Banco Mundial**: 23 de WDI (fuente API 2)
y dos de International Debt Statistics (fuente API 6). Para PNUD se conservan el CSV
global, el libro de metadatos, la Tabla 5 oficial y las notas técnicas.

## Archivos listos para usar

Las dos bases principales están directamente en `data/processed/`, con una fila
por país y año. Ambas tienen 132 filas: India y Estados Unidos, de 1960 a 2025,
con faltantes preservados según la cobertura de cada variable.

- [main_punto_1.csv](data/processed/main_punto_1.csv): 13 variables de demografía
  y dependencia, además de país, nombre del país y año. Incluye natalidad,
  mortalidad, población total y por edades, crecimiento poblacional total y natural, las tres razones de dependencia,
  fecundidad y esperanza de vida.
- [main_punto_2.csv](data/processed/main_punto_2.csv): 13 variables de migración
  y divisas, además de país, nombre del país y año. Incluye migración neta,
  remesas, PIB, FBKF, exportaciones, IED, flujos de deuda y ayuda al desarrollo.

La migración corresponde al punto 2. Los indicadores de género corresponden al
punto 3 y se conservan aparte. Los archivos auxiliares quedan organizados así:

| Archivo | Uso |
|---|---|
| `apoyo/panel_anual.csv` | Las 25 variables del Banco Mundial más el crecimiento natural calculado |
| `apoyo/series_largas.csv` | Datos en formato largo, con código, unidad, estado, actualización y archivo de origen |
| `apoyo/diccionario_variables.csv` | Códigos, punto de la consigna, definiciones y unidades |
| `apoyo/cobertura_fuentes.csv` | Observaciones efectivas y primeros/últimos años por país y variable |
| `apoyo/ids_valores_fuera_periodo_historico.csv` | Desembolsos de 2025–2032 separados de la base histórica |
| `genero/gii_evolucion.csv` | GII de India y Estados Unidos, 1990–2023 |
| `genero/gii_componentes_panel.csv` | GII y ocho componentes por país y año |
| `genero/gii_componentes_largo.csv` | Componentes con unidad, dimensión y año de referencia |
| `genero/gii_tabla5_comparacion.csv` | Tabla 5 con años, notas y ubicación de cada celda |
| `genero/diccionario_gii.csv` y `genero/cobertura_gii.csv` | Definiciones, unidades y cobertura del PNUD |
| `genero/gii_tabla_publicada_celdas.json` | Tabla original completa, incluidos encabezados y notas |

Los CSV usan **punto y coma entre columnas, coma decimal y UTF-8 con BOM**, sin
separador de miles. Un dato faltante es una celda vacía; nunca se transforma en cero.
En Python: `pd.read_csv(ruta, sep=';', decimal=',')`.

## Cobertura efectiva

| Bloque | India | Estados Unidos |
|---|---|---|
| Natalidad, mortalidad, fecundidad y esperanza de vida | 1960–2024 | 1960–2024 |
| Población, edades y dependencia | 1960–2025 | 1960–2025 |
| Crecimiento poblacional total, % anual | 1961–2025 | 1961–2025 |
| Crecimiento poblacional natural, % anual | 1960–2024 | 1960–2024 |
| Migración neta | 1960–2025 | 1960–2025 |
| Remesas recibidas | 1975–2025 | 1977–2025 |
| PIB en dólares corrientes | 1960–2025 | 1960–2025 |
| FBKF y exportaciones | 1960–2025 | 1970–2024 |
| IED recibida | 1970–2025 | 1970–2025 |
| Deuda externa, flujo neto y desembolsos de largo plazo | 1970–2024 | Fuera de cobertura IDS |
| Ayuda oficial al desarrollo neta recibida | 1960–2023 | Sin datos de recepción |
| GII y componentes | 1990–2023 | 1990–2023 |

Los años extremos describen la descarga actual; consultar los archivos de cobertura
para conocer cuántos valores hay y elegir una ventana común. Los vacíos de Estados
Unidos en deuda IDS y ayuda recibida no significan ausencia de deuda o un flujo cero.

## Aclaraciones para usar las bases

**Población.** Natalidad y mortalidad están expresadas por mil habitantes. Su
diferencia conserva esa unidad; para expresarla en porcentaje se divide por diez.
La columna `crecimiento_poblacional_pct_anual` contiene la tasa total publicada por
el Banco Mundial: variación exponencial anual de la población a mitad de año,
`100 × ln(P_t / P_(t-1))`. Incluye el efecto de la migración; no es la tasa natural
calculada como natalidad menos mortalidad. El año 1960 queda vacío en esta serie.
La columna `crecimiento_natural_pct_anual` se calcula como `(natalidad_por_mil -
mortalidad_por_mil) / 10`, sin interpolar faltantes. Ambas tasas están en % anual.
La tasa total WDI es exponencial y la natural se construye con tasas brutas; su
diferencia no es una medida exacta del aporte migratorio.
Los grupos de edad descargados son 0–14, 15–64 y 65+, sin superposición. Son la
convención WDI para calcular dependencia y evitan la ambigüedad de los límites de
edad de la fórmula de la consigna. Se incluyen las razones WDI como referencia para
comprobar el cálculo posterior. Una razón demográfica no mide dependencia económica
real: la población en edad de trabajar no equivale al número de ocupados.

**Migración.** `SM.POP.NETM` es inmigración menos emigración durante el periodo;
la descarga actual tiene periodicidad anual. Conservar el signo. No es el stock de
migrantes ni una tasa por mil, y no debe tratarse como una suma quinquenal por usar
versiones antiguas de la base.

**Divisas.** Los montos se conservan en US$ corrientes para permitir comparaciones
dentro de un mismo año. También se descargaron los porcentajes oficiales del PIB
cuando existen. La FBKF en dólares permite calcular remesas/FBKF más adelante.
No confundir flujos anuales con stocks, ni dólares corrientes con constantes.
Las exportaciones son de bienes y servicios; la IED corresponde a entradas netas;
la ayuda es neta recibida. La deuda se guarda en dos conceptos: flujo neto total y
desembolsos brutos de largo plazo. No son intercambiables. Estas partidas no deben
sumarse sin revisar solapamientos, como los préstamos concesionales de la ayuda.

**Deuda.** La ruta usual de indicadores no devolvía estas series. Se utilizó la API
avanzada de IDS y se seleccionó `Counterpart-Area=WLD` (todos los acreedores), sin
sumar agregados y países acreedores. La edición consultada de IDS fue actualizada
el 3 de diciembre de 2025 y su periodo histórico termina en 2024. La fuente también
devuelve desembolsos para 2025–2032: se conservan aparte, sin tratarlos como datos
históricos observados y sin incorporarlos al panel general.

**Género.** La publicación oficial disponible sigue siendo HDR 2025, con GII hasta
2023. El GII va de 0 a 1: valores menores indican menor desigualdad. Sus tres
dimensiones son salud reproductiva, empoderamiento y mercado laboral. Los archivos
por componentes contienen indicadores, no índices de dimensión calculados por
nosotros. La mortalidad materna del GII 2023 corresponde a **2020**: los metadatos
indican que 2021–2023 repiten ese dato. La Tabla 5 explicita también notas y periodos
de referencia; no atribuir automáticamente todos sus valores a 2023. La educación
secundaria significa haber alcanzado al menos parte de ese nivel, no necesariamente
haberlo terminado. Esta selección corresponde al **GII**, no al índice GDI.

## Fuentes y trazabilidad

- [Banco Mundial WDI](https://databank.worldbank.org/source/world-development-indicators).
- [Banco Mundial IDS y API avanzada](https://worldbank.github.io/debt-data/api-guide/ids-api-guide-r-1.html).
- [PNUD GII](https://hdr.undp.org/data-center/thematic-composite-indices/gender-inequality-index).
- [PNUD descargas y documentación](https://hdr.undp.org/data-center/documentation-and-downloads).

`data/raw/manifest.json` registra las 54 descargas: URL solicitada y final, fecha UTC,
tipo de contenido, tamaño y SHA256. Las respuestas originales se guardan sin alterar.
No se reutilizaron como actuales las descargas del TP7 ni se modificaron sus bases.

## Reproducción

Se requiere Python 3 y `openpyxl` para **leer** los libros oficiales del PNUD:

```powershell
pip install -r TP8/requirements.txt
python TP8/src/descargar_bases.py
```

Para regenerar las bases sin descargar nuevamente:

```powershell
python TP8/src/descargar_bases.py --offline
```

Los faltantes no se interpolan ni se extrapolan. El script verifica integridad de
las fuentes, paginación completa, códigos, países y duplicados. Los controles de
preparación contrastan el formato largo contra el panel y la extracción contra la
Tabla 5 original. Una nueva consulta puede incorporar revisiones oficiales.

## Gráficos de crecimiento poblacional

Tres figuras de India, en PNG y PDF, con escala común de 0 a 3% anual, sin subtítulos
ni notas al pie. El gráfico conjunto usa los años con ambas tasas, 1961–2024.
Los datos de Estados Unidos se conservan en el CSV principal.

- Crecimiento total, 1961–2025: [PNG](output/figures/01_crecimiento_poblacional_total.png) y [PDF](output/figures/01_crecimiento_poblacional_total.pdf).
- Crecimiento natural, 1960–2024: [PNG](output/figures/02_crecimiento_poblacional_natural.png) y [PDF](output/figures/02_crecimiento_poblacional_natural.pdf).
- Comparación de ambas tasas: [PNG](output/figures/03_crecimiento_total_y_natural.png) y [PDF](output/figures/03_crecimiento_total_y_natural.pdf).

```powershell
python TP8/src/graficar_crecimiento.py
```

## Transición demográfica

- [Esquema estilizado de cuatro etapas](output/figures/04_transicion_demografica_esquema.png), también en [PDF](output/figures/04_transicion_demografica_esquema.pdf).
- [Evolución observada de India, 1960–2024](output/figures/05_transicion_demografica_datos_india.png), también en [PDF](output/figures/05_transicion_demografica_datos_india.pdf).

El esquema es conceptual: las curvas no son datos ni proyecciones, y el eje horizontal
no representa años. La ubicación de India en una etapa 3 avanzada hacia la 4 es una
interpretación en el modelo de cuatro etapas, no una clasificación oficial ni un corte
temporal universal. Hay diferencias demográficas importantes entre regiones del país.

La referencia empírica es 2024, último año con natalidad y mortalidad en la base:
natalidad 15,981‰, mortalidad 6,587‰, crecimiento natural 9,394‰ (0,9394%) y fecundidad
1,962 hijos por mujer. En el gráfico observado las tres curvas comparten unidad, por
mil habitantes. La curva azul representa crecimiento natural, no tamaño poblacional
ni la tasa total que incorpora migración. La ubicación esquemática no demuestra por
sí sola la existencia de un bono demográfico económico.

Referencias conceptuales: [ONU, Global Population Growth and Sustainable Development](https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2022_global_population_growth.pdf)
y [UNFPA India, Reimagining Family Planning in India](https://india.unfpa.org/en/publications/reimagining-family-planning-india-new-pathways).
Los valores utilizados se registran en `output/transicion_demografica_notas.json`.

```powershell
python TP8/src/graficar_transicion_demografica.py
```

## Resolución en LaTeX

El archivo de entrada es [latex/main.tex](latex/main.tex) y el resultado compilado
está en [output/pdf/TP8.pdf](output/pdf/TP8.pdf), con seis páginas.
Se revisó visualmente el PDF.

La estructura tiene dos secciones principales, Población y Género, con subtítulos
por punto. Se omitieron las consignas, las imágenes decorativas, la mención de IA,
el agregado del paper, las referencias y los comentarios del código LaTeX.
El gráfico de remesas, exportaciones e IED incluye solamente India.
La tabla mantiene los valores del Word y usa nombres completos de indicadores.

La resolución original se conserva en [resolucion/TP 8 resol.docx](resolucion/TP%208%20resol.docx).
Las figuras y la tabla están en `output/figures/` y `output/tables/`.

Para regenerar el código y compilar desde la carpeta del proyecto:

```powershell
python TP8/src/preparar_latex_resolucion.py
Set-Location TP8/latex
tectonic main.tex
Move-Item -LiteralPath main.pdf -Destination ../output/pdf/TP8.pdf -Force
```

Los temporales de extracción, las vistas de revisión y el registro auxiliar de
revisión se eliminaron. Las fuentes y metadatos se conservan por práctico para
mantener reproducibles las descargas; los PNG sirven de vista previa y los PDF
de las figuras se usan en LaTeX.
