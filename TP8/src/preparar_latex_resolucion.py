"""Arma el código LaTeX desde la resolución, con la estructura editorial vigente."""
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = ROOT / 'resolucion/bloques.json'
OUT = ROOT / 'latex'


def escape(text):
    mapping = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
               '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
               '‰': r'\textperthousand{}'}
    text = text.replace(chr(0x201c), '``').replace(chr(0x201d), "''")
    return ''.join(mapping.get(c, c) for c in text)


def main():
    blocks = json.loads(BLOCKS.read_text(encoding='utf-8'))
    by_id = {r['i']: r for r in blocks}
    original = {r['i']: r['text'] for r in blocks if 'text' in r}
    edits = {
        11: original[11].replace('tendencia a la emigración', 'tendencia a la migración').replace('masa emigratoria', 'masa migratoria'),
        15: original[15].replace('[TEORIA]', 'la natalidad y la mortalidad se mantienen bajas y el crecimiento natural tiende a estabilizarse en niveles reducidos.'),
        53: original[53].replace('(mmr,', '(razón de mortalidad materna,')
            .replace('(pr_f)', '(participación de mujeres en el parlamento)')
            .replace('(se_f)', '(población femenina con al menos parte de educación secundaria)'),
        54: original[54].replace('dimensión de pr_f', 'dimensión de participación de mujeres en el parlamento'),
    }
    parts = []
    preserved = []

    def p(i):
        text = edits.get(i, original[i])
        parts.append(escape(text) + '\n')
        preserved.append(i)

    def comment(text):
        pass

    def figure(file, caption, label):
        parts.append(r'\begin{figure}[H]' + '\n' + r'\centering' + '\n' +
                     r'\includegraphics[width=0.96\textwidth,height=0.43\textheight,keepaspectratio]{' + file + '}\n' +
                     r'\caption{' + escape(caption) + '}\n' + r'\label{' + label + '}\n' + r'\end{figure}' + '\n')

    parts.append(r'\section{Población}' + '\n')
    parts.append(r'\subsection{Crecimiento poblacional}' + '\n')
    p(8)
    figure('02_crecimiento_poblacional_natural.pdf', 'India: tasa natural de crecimiento poblacional.', 'fig:crecimiento_natural')
    p(10)
    comment('Se conserva la interpretación original. La cercanía entre tasas no identifica por sí sola una compensación de la emigración; la tasa total WDI es exponencial y la natural se obtiene de tasas brutas.')
    p(11)
    figure('03_crecimiento_total_y_natural.pdf', 'India: crecimiento poblacional total y natural.', 'fig:total_natural')
    parts.append(r'\subsection{Transición demográfica}' + '\n')
    figure('05_transicion_demografica_datos_india.pdf', 'India: evolución observada de natalidad, mortalidad y crecimiento natural.', 'fig:transicion_observada')
    comment('El original dice mortalidad dos veces. Se conserva literalmente; verificar si la primera mención debe decir natalidad. La etapa 3 avanzada hacia la 4 es interpretativa, no una clasificación oficial.')
    parts.append('% AGREGADO SOLICITADO: solo se sustituye [TEORIA] por una cláusula breve.\n')
    p(15)
    p(16)
    figure('04_transicion_demografica_esquema.pdf', 'Esquema conceptual de la transición demográfica y ubicación aproximada de India.', 'fig:transicion_esquema')
    parts.append('% Se omiten el boceto manuscrito redundante (image3.png) y su pie; se conserva el esquema limpio que lo reemplaza.\n')
    parts.append(r'\subsection{Índice de dependencia}' + '\n')
    comment('Se conserva la fórmula verbal de la resolución. Los datos del gráfico usan la convención WDI: (población 0--14 + población 65+) / población 15--64. Revisar los límites de edad en la fórmula antes de entregar.')
    parts.append(r'''\[
\text{Índice de dependencia} =
\frac{\text{Población hasta 15 años} + \text{Población de más de 65 años}}
{\text{Población entre 15 y 65 años}}.
\]
''')
    figure('06_indice_dependencia_india.pdf', 'India: índice de dependencia demográfica, expresado como razón.', 'fig:dependencia')
    parts.append(r'\subsection{Bono demográfico}' + '\n')
    for i in [27, 28, 29]:
        p(i)
    parts.append(r'\subsection{Migración neta y remesas}' + '\n')
    for i in [33, 34, 35]:
        p(i)
    comment('El gráfico de Excel original concatenaba India y Estados Unidos como si fueran una sola serie. Se conservan todos sus valores y se muestran en paneles por país con años reales. No se cambió el texto interpretativo.')
    figure('07_remesas_exportaciones_ied.pdf', 'India: remesas, exportaciones e inversión extranjera directa como porcentaje del PIB.', 'fig:remesas')
    comment('Los promedios originales mezclan ambos países: 1,1669%, 10,8821% y 0,9847%. En el XLSX, los promedios de India sola son 2,2620%, 11,7591% y 0,8048%, respectivamente. La serie de India no muestra una caída sostenida de remesas desde los años ochenta. Se conserva el texto para revisión del grupo.')
    p(37)
    comment('Revisar la conclusión sobre la importancia de las remesas: se conserva sin cambios, pero no se desprende de los promedios agregados de ambos países.')
    p(38)
    parts.append('% Se omite el sello decorativo de IA (image4.png).\n')
    comment('La consigna original también incluye un apartado para el país con inmigración neta. La resolución proporcionada no lo desarrolla; no se agregó una respuesta nueva.')
    parts.append(r'\section{Género}' + '\n')
    parts.append(r'\subsection{Evolución de la desigualdad de género}' + '\n')
    figure('08_gii_comparacion_paises.pdf', 'Evolución del índice de desigualdad de género en los cinco países seleccionados.', 'fig:gii')
    comment('La muestra del gráfico tiene cinco países, no representa por sí sola una tendencia global. Se conserva la formulación original.')
    p(48)
    p(49)
    parts.append('% Se omite el símbolo decorativo contra la IA (image5.png).\n')
    parts.append(r'\subsection{Comparación de indicadores}' + '\n')
    parts.append(r'\input{../output/tables/gii_comparacion.tex}' + '\n')
    comment('India no está peor en cada indicador: en natalidad adolescente presenta 14,06 frente a 26,41 de Argentina. Educación secundaria significa haber alcanzado al menos parte del nivel, no necesariamente haberlo terminado. Se conserva el resto del texto original, reemplazando únicamente los tags por nombres legibles.')
    p(53)
    comment('43,77% / 28,22% equivale aproximadamente a 1,55, no casi el doble. Se conserva la comparación original para revisión.')
    p(54)

    table = by_id[51]['rows']
    original_headers = table[0]
    table_rows = {row[0]: row for row in table[1:]}
    labels = {
        'abr': 'Natalidad adolescente (nacimientos por 1.000 mujeres de 15--19 años)',
        'gii': 'Índice de desigualdad de género (GII, de 0 a 1)',
        'gii_rank': 'Posición en el ranking del GII',
        'lfpr_f': r'Participación laboral de mujeres de 15 años o más (\%)',
        'lfpr_m': r'Participación laboral de varones de 15 años o más (\%)',
        'mmr': 'Razón de mortalidad materna (muertes por 100.000 nacidos vivos)',
        'pr_f': r'Bancas parlamentarias ocupadas por mujeres (\%)',
        'pr_m': r'Bancas parlamentarias ocupadas por varones (\%)',
        'se_f': r'Mujeres de 25 años o más con al menos parte de educación secundaria (\%)',
        'se_m': r'Varones de 25 años o más con al menos parte de educación secundaria (\%)',
    }
    tex_table = [r'''% Valores de la tabla del DOCX, sin cambios; se transpone para legibilidad.
\begin{table}[H]
\centering
\small
\caption{GII y componentes en Argentina, India y Estados Unidos.}
\label{tab:gii_comparacion}
\renewcommand{\arraystretch}{1.25}
\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}Xrrr}
\toprule
\textbf{Indicador} & \textbf{Argentina} & \textbf{India} & \textbf{Estados Unidos} \\
\midrule
''']
    for index, tag in enumerate(original_headers[1:], 1):
        values = [table_rows[country][index] for country in ['Argentina', 'India', 'United States']]
        assert all(Decimal(v).is_finite() for v in values)
        values = [str(int(Decimal(v))) if tag == 'gii_rank' else v.replace('.', ',') for v in values]
        tex_table.append(labels[tag] + ' & ' + ' & '.join(values) + r' \\' + '\n')
    tex_table.append(r'''\bottomrule
\end{tabularx}
\end{table}
''')
    tables = ROOT/'output/tables'
    tables.mkdir(parents=True, exist_ok=True)
    (tables/'gii_comparacion.tex').write_text('\n'.join(line for line in ''.join(tex_table).splitlines() if not line.lstrip().startswith('%')) + '\n', encoding='utf-8')

    preamble = r'''\documentclass[11pt, a4paper]{article}

% Preparado para revisión: NO se compiló este proyecto.
% Se conserva la redacción de TP 8 resol.docx. Los comentarios REVISAR no se imprimen.
% Cambios autorizados: limpieza/reemplazo de imágenes, tabla con nombres completos,
% una cláusula de teoría y un comentario breve del paper sobre bono demográfico.
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish, es-nodecimaldot]{babel}
\usepackage{graphicx}
\usepackage[top=2.2cm, bottom=2.5cm, left=2.2cm, right=2.2cm]{geometry}
\usepackage{caption}
\usepackage{float}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{array}
\usepackage{tabularx}
\usepackage{xurl}
\usepackage[colorlinks=true, linkcolor=blue!70!black, urlcolor=blue!70!black, citecolor=blue!70!black]{hyperref}
\graphicspath{{../output/figures/}}
\captionsetup{font=small, labelfont=bf, justification=centering}
\setlength{\emergencystretch}{2em}

\title{\textbf{Trabajo Práctico 8: Población, Género y Desarrollo}\\[0.3em]
\large Evidencia Empírica para la India}
\author{
    \footnotesize \textbf{Mateo Barros} \quad \textbf{Felipe Delgado} \quad \textbf{Santiago González} \quad \textbf{Rodrigo Stremel} \quad \textbf{Santiago Trivellini} \\[0.3em]
    \footnotesize \textit{Desarrollo Económico --- Licenciatura en Economía --- Universidad Nacional del Sur (UNS)}
}
\date{\small Octubre de 2026}

\begin{document}
\maketitle
\vspace{-1em}
\noindent\rule{\textwidth}{0.6pt}
\vspace{0.8em}

'''
    references = '\n' + r'\end{document}' + '\n'
    OUT.mkdir(exist_ok=True)
    document = preamble + '\n'.join(parts) + references
    document = '\n'.join(line.rstrip() for line in document.splitlines() if not line.lstrip().startswith('%')) + '\n'
    (OUT/'main.tex').write_text(document, encoding='utf-8')
    print(OUT/'main.tex')


if __name__ == '__main__':
    main()
