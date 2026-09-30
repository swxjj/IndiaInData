* =============================================================================
* IndiaInData - Licenciatura en Economia (UNS) - Desarrollo Economico
* Trabajo Practico 5: Medio Ambiente, Instituciones y Desarrollo
* Script de Analisis Econometrico en Stata
* =============================================================================
* Autor: Mateo Barros & Grupo de Estudio
* Pais analizado: India (1996 - 2025)
* Base de datos: Worldwide Governance Indicators (WGI) y WDI (Banco Mundial)
* =============================================================================

clear all
set more off
capture log close

* -----------------------------------------------------------------------------
* 1. CARGA DE DATOS
* -----------------------------------------------------------------------------
* Si abres el .do desde la carpeta del proyecto, carga directamente el .dta:
capture use "tp5_india_stata.dta", clear
if _rc != 0 {
    * Opcion alternativa: importar el CSV delimitado
    capture import delimited "tp5_india_stata.csv", clear
}

* Inspeccion inicial de variables y tipos
describe
summarize

* -----------------------------------------------------------------------------
* 2. GENERACION DE VARIABLES PARA LA REGRESION
* -----------------------------------------------------------------------------
* La consigna pide estimar: ln(PIBpc) = a + b(institucionales) + b(controles) + e
* Generamos el logaritmo natural del PIB per capita constante 2015 USD:
gen lnpibpc = ln(pib_pc_cte2015)
label var lnpibpc "Logaritmo natural del PIB per capita (cte 2015 USD)"

* Alternativa con PIB per capita a PPA constante 2021 USD:
gen lnpibpc_ppp = ln(pib_pc_ppp2021)
label var lnpibpc_ppp "Logaritmo natural del PIB per capita (PPA cte 2021 USD)"

* -----------------------------------------------------------------------------
* 3. ANALISIS DESCRIPTIVO Y MATRIZ DE CORRELACIONES
* -----------------------------------------------------------------------------
* Resumen estadistico de las variables institucionales y macroeconomicas
summarize lnpibpc va pv ge rq rl cc wgi_prom inv_fbcf aper_fin_ied aper_comerc gasto_educ gasto_educ_interp

* Matriz de correlaciones simples de Pearson
correlate lnpibpc va pv ge rq rl cc wgi_prom inv_fbcf aper_fin_ied aper_comerc gasto_educ gasto_educ_interp

* Matriz con niveles de significatividad estadistica (p-values)
pwcorr lnpibpc va pv ge rq rl cc wgi_prom inv_fbcf aper_fin_ied aper_comerc gasto_educ gasto_educ_interp, sig star(0.05)

* -----------------------------------------------------------------------------
* 4. REGRESIONES INDIVIDUALES POR DIMENSION INSTITUCIONAL (CONTROL: INVERSION)
* -----------------------------------------------------------------------------
* Debido a la alta correlacion mutua entre indicadores WGI (multicolinealidad),
* se recomienda estimar primero el impacto individual de cada institucion
* controlando por la acumulacion de capital fisico (FBCF % PIB):

* Modelo 1: Eficacia del Gobierno (GE) + Inversion
regress lnpibpc ge inv_fbcf
estimates store mod_ge

* Modelo 2: Calidad Regulatoria (RQ) + Inversion
regress lnpibpc rq inv_fbcf
estimates store mod_rq

* Modelo 3: Estabilidad Politica (PV) + Inversion
regress lnpibpc pv inv_fbcf
estimates store mod_pv

* Modelo 4: Control de la Corrupcion (CC) + Inversion
regress lnpibpc cc inv_fbcf
estimates store mod_cc

* Modelo 5: Voz y Rendicion de Cuentas (VA) + Inversion
regress lnpibpc va inv_fbcf
estimates store mod_va

* Modelo 6: Estado de Derecho (RL) + Inversion
regress lnpibpc rl inv_fbcf
estimates store mod_rl

* -----------------------------------------------------------------------------
* 5. REGRESION CON EL INDICE GENERAL DE GOBERNABILIDAD
* -----------------------------------------------------------------------------
* Modelo 7: Indice Promedio WGI (wgi_prom) + Inversion
regress lnpibpc wgi_prom inv_fbcf
estimates store mod_prom

* -----------------------------------------------------------------------------
* 6. INCORPORACION DE APERTURA FINANCIERA Y COMERCIAL
* -----------------------------------------------------------------------------
* Evaluamos la robustez institucional anadiendo controles de integracion internacional:
* aper_fin_ied: Entradas netas de IED (% del PIB)
* aper_comerc: Apertura comercial (X+M % del PIB)

* Modelo 8: Eficacia de Gobierno + Inversion + Apertura Financiera (IED)
regress lnpibpc ge inv_fbcf aper_fin_ied
estimates store mod_ge_fin

* Modelo 9: Eficacia de Gobierno + Inversion + Apertura Financiera + Apertura Comercial
regress lnpibpc ge inv_fbcf aper_fin_ied aper_comerc
estimates store mod_ge_fin_trd

* Modelo 10: Indice Promedio WGI + Inversion + Apertura Financiera + Apertura Comercial
regress lnpibpc wgi_prom inv_fbcf aper_fin_ied aper_comerc
estimates store mod_prom_fin_trd

* -----------------------------------------------------------------------------
* 7. REGRESION MULTIPLE COMPLETA (TODAS LAS DIMENSIONES JUNTAS)
* -----------------------------------------------------------------------------
* Modelo 11: ln(PIBpc) = a + b1(VA) + b2(PV) + b3(GE) + b4(RQ) + b5(RL) + b6(CC) + Controles + e
regress lnpibpc va pv ge rq rl cc inv_fbcf aper_fin_ied
estimates store mod_full

* Diagnostico de Multicolinealidad (Variance Inflation Factor):
* Valores de VIF > 10 alertan sobre fuerte redundancia entre dimensiones.
estat vif

* -----------------------------------------------------------------------------
* 8. MODELOS INCORPORANDO CAPITAL HUMANO (GASTO EN EDUCACION ORIGINAL VS INTERPOLADO)
* -----------------------------------------------------------------------------
* Especificacion A: Usando gasto_educ original de Banco Mundial (N = 20)
regress lnpibpc ge inv_fbcf aper_fin_ied gasto_educ
estimates store mod_ge_educ_orig

regress lnpibpc wgi_prom inv_fbcf aper_fin_ied gasto_educ
estimates store mod_prom_educ_orig

* Especificacion B: Usando gasto_educ_interp lineal (N = 27, muestra completa)
regress lnpibpc ge inv_fbcf aper_fin_ied gasto_educ_interp
estimates store mod_ge_educ_interp

regress lnpibpc wgi_prom inv_fbcf aper_fin_ied gasto_educ_interp
estimates store mod_prom_educ_interp

* -----------------------------------------------------------------------------
* 9. TABLAS COMPARATIVAS DE RESULTADOS
* -----------------------------------------------------------------------------
* Panel A: Modelos institucionales base
estimates table mod_ge mod_rq mod_pv mod_rl mod_prom, b(%9.4f) se stats(N r2 r2_a)

* Panel B: Modelos con controles macroeconomicos y apertura financiera
estimates table mod_ge mod_ge_fin mod_ge_fin_trd mod_prom_fin_trd mod_full, b(%9.4f) se stats(N r2 r2_a)

* Panel C: Comparacion de robustez en Capital Humano (N=20 vs N=27)
estimates table mod_ge_educ_orig mod_ge_educ_interp mod_prom_educ_orig mod_prom_educ_interp, b(%9.4f) se stats(N r2 r2_a)

display "Analisis econometrico finalizado con exito."
* =============================================================================
