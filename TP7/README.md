# TP7 — Educación, trabajo y desarrollo

## Alcance de esta etapa

Bases para el ejercicio 1, **Educación y desarrollo**, para India (`IND`).
Descarga del 21 de octubre de 2026. Se conserva la consigna original y se sigue
la organización de TP3–TP6. Incluye bases y gráficos exploratorios del ejercicio 1.
Para el ejercicio 2 incluye una selección breve de indicadores laborales en Word.
El relevamiento de sus valores y la redacción de respuestas finales quedan pendientes.

## Organización

- `consigna/`: consigna original y texto extraído.
- `data/raw/`: fuentes originales y registro de descargas.
- `data/processed/`: seis bases CSV con coma decimal.
- `src/`: scripts de descarga, gráficos y generación del Word.
- `output/figures/`: seis gráficos en PNG/PDF y una vista conjunta.
- `output/tp7_punto2_indicadores.docx`: selección de indicadores laborales.

## Archivos para empezar

| Archivo en `data/processed/` | Contenido |
|---|---|
| `educacion_india_anual.csv` | Base principal: un año por fila y las 17 series del Banco Mundial en columnas |
| `educacion_india_largo.csv` | Los mismos datos, con código, unidad, fuente y estado de observación por registro |
| `pib_escolaridad_anios_comunes.csv` | PIB y variable exacta de escolaridad, solo en los tres años comunes |
| `complemento_pnud_escolaridad_india.csv` | Escolaridad PNUD HDR 2025 y PIB WDI, como complemento separado |
| `diccionario_variables.csv` | Códigos, nombres originales, definiciones, unidades y organismo productor |
| `cobertura.csv` | Cantidad de datos, primer y último año, años disponibles y faltantes internos de cada serie BM |

Los CSV procesados usan UTF-8 con BOM, separador punto y coma (`;`) y coma decimal,
para abrirlos en Excel con configuración regional española/argentina. No llevan
separador de miles: por ejemplo, `312,777847829868` significa aproximadamente
US$312,78, no un valor de billones. En Python: `pd.read_csv(ruta, sep=';', decimal=',')`.
Los archivos originales en `data/raw/` conservan el formato de la fuente. Los faltantes son
celdas vacías. Las bases principal y larga abarcan 1960–2025, desde el primer
hasta el último año con algún dato efectivo. Los JSON originales conservan también
las filas vacías que la API devuelve fuera de ese intervalo.

## Fuentes y cobertura efectiva

| Variable | Fuente y código | Datos no vacíos | Años extremos |
|---|---|---:|---|
| PIB por habitante, US$ constantes de 2015 | WDI `NY.GDP.PCAP.KD` | 66 | 1960–2025 |
| Escolaridad media, población 25+, ambos sexos | EdStats `UIS.EA.MEAN.1T6.AG25T99` | 3 | 1971, 1981, 2011 |
| Escolaridad media, mujeres y varones | EdStats, sufijos `.F` y `.M` | 3 por sexo | 1971, 1981, 2011 |
| Gasto público educativo, % PIB | WDI `SE.XPD.TOTL.GD.ZS` | 22 | 1997–2022 |
| Gasto por alumno de primaria, % PIB por habitante | WDI `SE.XPD.PRIM.PC.ZS` | 9 | 1999–2013 |
| Gasto por alumno de secundaria, % PIB por habitante | WDI `SE.XPD.SECO.PC.ZS` | 12 | 1999–2013 |
| Gasto por alumno de terciaria, % PIB por habitante | WDI `SE.XPD.TERT.PC.ZS` | 10 | 2000–2013 |
| Matrícula neta primaria, total y por sexo | WDI `SE.PRM.NENR`, `.FE`, `.MA` | 13 por serie | 1971–2013 |
| Matrícula neta secundaria, total y por sexo | WDI `SE.SEC.NENR`, `.FE`, `.MA` | 1 por serie | 2013 |
| Matrícula bruta primaria | WDI `SE.PRM.ENRR` | 52 | 1971–2025 |
| Matrícula bruta secundaria | WDI `SE.SEC.ENRR` | 48 | 1971–2025 |
| Matrícula bruta terciaria | WDI `SE.TER.ENRR` | 47 | 1971–2025 |

Los extremos no implican continuidad: consultar `cobertura.csv` antes de elegir
ventanas para comparar gasto y matrícula.

- [Banco Mundial, World Development Indicators](https://databank.worldbank.org/source/world-development-indicators), fuente API `2`.
- [Banco Mundial, Education Statistics](https://databank.worldbank.org/source/education-statistics-%5E-all-indicators), fuente API `12`.
- [PNUD, documentación y descargas](https://hdr.undp.org/data-center/documentation-and-downloads): HDR 2025, series 1990–2023 y libro oficial de metadatos.

## Precauciones para el próximo paso

La escolaridad EdStats es exactamente la variable solicitada: años completados
de educación ISCED 1 o superior, población de 25 años o más, excluyendo repetición.
Solo permite emparejar tres observaciones con el PIB. El complemento PNUD usa
la variable `mys` de HDR 2025 y se mantiene aparte: no se empalman fuentes ni se
rellenan los huecos de EdStats. Tiene 34 datos anuales, de 1990 a 2023.
Una serie anual publicada por PNUD puede contener
estimaciones del organismo; no debe presentarse como observaciones censales anuales.

El gasto por estudiante descargado está expresado como porcentaje del PIB por
habitante, **no en dólares ni como porcentaje del PIB total**. Se conserva esa
unidad original. Si después se calcula un equivalente usando el PIB por habitante,
habrá que identificarlo como una transformación derivada y revisar comparabilidad.

La matrícula neta mide alumnos de la edad oficial del nivel respecto de la población
de esa edad. La matrícula bruta incluye estudiantes de otras edades y puede superar
100%. Las series brutas complementan la descarga, pero no sustituyen la tasa neta
pedida para evaluar acceso. La secundaria neta solo tiene 2013, por lo que no permite
analizar su evolución temporal con esta descarga.

## Conservación y reproducción

`consigna/` conserva el DOCX original y su texto extraído; se eliminó el duplicado
idéntico de la raíz. `data/raw/` guarda las respuestas JSON originales de series y
metadatos del Banco Mundial, el CSV completo del PNUD y su libro de metadatos.
`manifest.json` registra URL, fecha UTC, tamaño y SHA256 de las descargas.

El script usa solo la biblioteca estándar de Python 3:

```powershell
python TP7/src/descargar_educacion.py
```

Para regenerar las bases desde los originales guardados, sin red:

```powershell
python TP7/src/descargar_educacion.py --offline
```

Se controlan país, código, registros duplicados por año y respuestas completas de
la API. Los valores se conservan sin redondear, interpolar, extrapolar o imputar.
Una nueva descarga puede cambiar por revisiones de los organismos.

Verificación realizada: integridad SHA256 de los 36 archivos fuente, coincidencia
entre formatos largo y anual, y reproducción idéntica de los seis CSV sin red.

## Gráficos exploratorios

Cada figura se guarda en PNG y PDF en `output/figures/`.

| Figura | PNG | PDF |
|---|---|---|
| PIB y escolaridad exacta de EdStats | [Ver](output/figures/01_pib_escolaridad_edstats.png) | [Descargar](output/figures/01_pib_escolaridad_edstats.pdf) |
| PIB y escolaridad PNUD, 1990–2023: evolución y dispersión | [Ver](output/figures/02_pib_escolaridad_pnud.png) | [Descargar](output/figures/02_pib_escolaridad_pnud.pdf) |
| Gasto educativo total y por estudiante | [Ver](output/figures/03_gasto_educativo.png) | [Descargar](output/figures/03_gasto_educativo.pdf) |
| Matrícula neta primaria y secundaria, total y por sexo | [Ver](output/figures/04_matricula_neta.png) | [Descargar](output/figures/04_matricula_neta.pdf) |
| Matrícula bruta por nivel | [Ver](output/figures/05_matricula_bruta.png) | [Descargar](output/figures/05_matricula_bruta.pdf) |
| Gasto y matrícula neta primaria, ventana 1997–2013 | [Ver](output/figures/06_gasto_y_acceso_primaria.png) | [Descargar](output/figures/06_gasto_y_acceso_primaria.pdf) |

[Vista conjunta de las seis figuras](output/figures/00_vista_general.png).
Se revisó visualmente la vista conjunta: títulos, unidades, fuentes, leyendas y etiquetas.
Los NaN interrumpen las líneas y los puntos aislados permanecen visibles.

Para regenerarlas con las dependencias de `TP7/requirements.txt`:

```powershell
python TP7/src/graficar_educacion.py
```

Lectura preliminar: en el complemento PNUD la escolaridad pasa de 2,78 a 6,88 años
entre 1990 y 2023, mientras el PIB por habitante pasa de US$537,87 a US$2.229,71
constantes de 2015. La asociación es positiva y ambas series tienen tendencia,
lo que impide inferir causalidad a partir de la dispersión. La matrícula neta
primaria pasa de 61,04% en 1971 a 92,26% en 2013, con muchos años intermedios sin
datos. No se atribuye ese cambio al gasto público: las ventanas y la información
disponible no permiten identificar su efecto.

## Revisión del repositorio

Se revisaron la estructura local, los README de la raíz y del TP6, la especificación
del proyecto, el historial reciente y la raíz remota de `swxjj/IndiaInData` en GitHub
(rama predeterminada `master`). Los módulos existentes usan fuentes originales,
bases procesadas y scripts por TP. El TP7 sigue esa estructura.

## Punto 2 Indicadores laborales

[Word con seis indicadores y una justificación breve](output/tp7_punto2_indicadores.docx).
Incluye participación laboral, relación ocupación/población, desempleo, informalidad,
jóvenes NEET y pobreza laboral. Es una selección conceptual, sin tabla de valores.
Fuentes enlazadas en el documento: perfil de India en ILOSTAT y documentación OIT
sobre informalidad. Se revisó la presentación del Word en una página.

Para regenerar el contenido editable:

```powershell
python TP7/src/crear_word_indicadores.py
```
