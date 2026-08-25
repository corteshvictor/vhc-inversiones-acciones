"""Bilingual catalog for user-facing text.

The engine only ever emits Spanish. Translation happens here, at the presentation
boundary, so the language a report is written in can never reach the classifier
and change a bucket or a score.
"""

from .constants import (
    ALERT_ALTMAN,
    ALERT_INSUFFICIENT,
    ALERT_M_SCORE,
    ALERT_ROIC,
    ALERT_TOO_CHEAP,
    ALERT_VALUE_TRAP,
    ALERT_WEAK_HEALTH,
    ALERT_WEAK_IMPROVEMENT,
    BUCKET_DISCARDED,
    NOT_AVAILABLE,
    PRICE_CHEAP,
    PRICE_EXPENSIVE,
    PRICE_MIXED,
    PRICE_VERY_CHEAP,
    QUALITY_EXCELLENT,
    QUALITY_GOOD,
    QUALITY_WEAK,
    VERDICT_MEDIUM,
    VERDICT_NO,
    VERDICT_YES,
)

SPANISH = "es"
ENGLISH = "en"
LANGUAGES = (SPANISH, ENGLISH)

# Canonical engine values and how each reads in English. Deep Dive, Watchlist
# and Neutral are absent on purpose: they are already the same word.
TERMS = {
    BUCKET_DISCARDED: "Discarded",
    QUALITY_EXCELLENT: "EXCELLENT",
    QUALITY_GOOD: "GOOD",
    QUALITY_WEAK: "WEAK",
    PRICE_VERY_CHEAP: "VERY CHEAP",
    PRICE_CHEAP: "CHEAP",
    PRICE_MIXED: "MIXED",
    PRICE_EXPENSIVE: "EXPENSIVE",
    VERDICT_YES: "Yes",
    VERDICT_MEDIUM: "Medium",
    VERDICT_NO: "No",
    NOT_AVAILABLE: "N/A",
    ALERT_VALUE_TRAP: "Possible value trap",
    ALERT_TOO_CHEAP: "Too cheap?",
    ALERT_M_SCORE: "M-Score",
    ALERT_ALTMAN: "Altman risk zone",
    ALERT_WEAK_HEALTH: "Excellent but weak health",
    ALERT_INSUFFICIENT: "Insufficient data",
    ALERT_ROIC: "Review ROIC/moat",
    ALERT_WEAK_IMPROVEMENT: "Weak improvement",
    "Financiero": "Financials",
    "Utilities": "Utilities",
    # Excel bands, headers and labels.
    "RESULTADO": "RESULT",
    "EMPRESA": "COMPANY",
    "CALIDAD": "QUALITY",
    "PRECIO": "PRICE",
    "SALUD": "HEALTH",
    "Balde": "Bucket",
    "Puntaje (0-10)": "Score (0-10)",
    "Veredicto Calidad": "Quality verdict",
    "Señales de calidad (0-3)": "Quality signals (0-3)",
    "Veredicto Precio": "Price verdict",
    "Señales de precio (0-4)": "Price signals (0-4)",
    "Veredicto Salud financiera": "Financial health verdict",
    "Señales de salud (0-3)": "Health signals (0-3)",
    "Alertas": "Alerts",
    "Método": "Method",
    "Fondo/ETF": "Fund/ETF",
    "Omitida": "Excluded",
    "CALIDAD — ¿es un gran negocio?": "QUALITY — is it a great business?",
    "PRECIO — ¿está barata?": "PRICE — is it cheap?",
    "SALUD FINANCIERA — ¿sólida y limpia?": "FINANCIAL HEALTH — solid and clean?",
    "GUÍA DEL ARCHIVO": "FILE GUIDE",
    "Screening cuantitativo — VHC Inversiones": "Quantitative screening — VHC Inversiones",
    "QUÉ ES ESTA HERRAMIENTA": "WHAT THIS TOOL IS",
    "LAS CATEGORÍAS": "THE CATEGORIES",
    "LOS TRES TRIBUNALES": "THE THREE GATES",
    "EDUCATIVO, NO ASESORÍA": "EDUCATIONAL, NOT ADVICE",
    "Calidad": "Quality",
    "Salud": "Health",
    "Precio": "Price",
    "🔬 DEEP DIVE": "🔬 DEEP DIVE",
    "📋 WATCHLIST": "📋 WATCHLIST",
    "⚪ NEUTRAL": "⚪ NEUTRAL",
    "❌ DESCARTADA": "❌ DISCARDED",
    "⚙️ OMITIDA": "⚙️ EXCLUDED",
    "FONDO / ETF": "FUND / ETF",
    "VHC Inversiones en YouTube": "VHC Inversiones on YouTube",
    "VHC Inversiones en X": "VHC Inversiones on X",
    "VHC Inversiones en Instagram": "VHC Inversiones on Instagram",
}

# Sentences the command line writes. Placeholders keep their names in both.
MESSAGES = {
    "cli_description": (
        "Screening cuantitativo de acciones de VHC Inversiones.",
        "VHC Inversiones quantitative stock screening.",
    ),
    "cli_export_help": (
        "Export .xlsx del screener de InvestingPro",
        "InvestingPro screener .xlsx export",
    ),
    "cli_outdir_help": (
        "Directorio donde se guardan el Excel y el dashboard",
        "Directory where the Excel file and the dashboard are written",
    ),
    "cli_lang_help": (
        "Idioma del informe, el Excel y el dashboard",
        "Language of the report, the Excel file and the dashboard",
    ),
    "missing_core": (
        (
            "ERROR: faltan {missing} de los {total} indicadores núcleo "
            "obligatorios:\n{details}\n"
            "El screening se detuvo antes de clasificar y no generó archivos, "
            "porque el resultado sería incompleto. Agrega las columnas con esos "
            "nombres exactos en InvestingPro y vuelve a exportar."
        ),
        (
            "ERROR: {missing} of the {total} mandatory core indicators are "
            "missing:\n{details}\n"
            "The screening stopped before classifying and wrote no files, because "
            "the result would be incomplete. Add the columns under those exact "
            "names in InvestingPro and export again."
        ),
    ),
    "roic_note": (
        (
            "\nNOTA: '{cagr}' no reemplaza '{avg}': CAGR mide crecimiento; Avg "
            "mide el nivel promedio del ROIC."
        ),
        (
            "\nNOTE: '{cagr}' does not replace '{avg}': CAGR measures growth, "
            "while Avg measures the average level of ROIC."
        ),
    ),
    "warn_full_ticker": (
        (
            'AVISO — falta la columna "Full Ticker": el informe se genera igual, '
            "pero los tickers del dashboard NO quedan enlazados a InvestingPro. "
            "Agrégala al screener para recuperar los enlaces."
        ),
        (
            'WARNING — the "Full Ticker" column is missing: the report is still '
            "generated, but the dashboard tickers are NOT linked to InvestingPro. "
            "Add it in the screener to recover the links."
        ),
    ),
    "warn_scale": (
        (
            "AVISO — estas columnas no parecen venir en decimales: {columns}. Si "
            "InvestingPro cambió el formato del export, los umbrales quedarían mal "
            "calibrados: reporta este aviso antes de usar los resultados."
        ),
        (
            "WARNING — these columns do not look like decimals: {columns}. If "
            "InvestingPro changed the export format, the thresholds would be badly "
            "calibrated: report this warning before using the results."
        ),
    ),
    # Reader and validation errors. They surface as SystemExit, so the user
    # reads them directly.
    "io_no_header": (
        (
            "ERROR: no encontré la fila de encabezados (debe contener 'Name' y "
            "'Ticker'). Verifica que el archivo sea el export del screener de "
            "InvestingPro sin renombrar columnas."
        ),
        (
            "ERROR: the header row was not found (it must contain 'Name' and "
            "'Ticker'). Check that the file is the InvestingPro screener export "
            "with its columns unrenamed."
        ),
    ),
    "io_not_xlsx": (
        "ERROR: el archivo de entrada debe tener extensión .xlsx.",
        "ERROR: the input file must have an .xlsx extension.",
    ),
    "io_not_found": (
        "ERROR: no se encontró el archivo XLSX: {path}",
        "ERROR: the XLSX file was not found: {path}",
    ),
    "io_stat_failed": (
        "ERROR: no se pudo inspeccionar el archivo XLSX ({error}).",
        "ERROR: the XLSX file could not be inspected ({error}).",
    ),
    "io_empty": (
        "ERROR: el archivo XLSX está vacío.",
        "ERROR: the XLSX file is empty.",
    ),
    "io_too_large": (
        "ERROR: el archivo XLSX supera el límite de seguridad de {limit} MiB.",
        "ERROR: the XLSX file exceeds the {limit} MiB safety limit.",
    ),
    "io_too_many_members": (
        (
            "ERROR: el XLSX contiene demasiados archivos internos y fue "
            "rechazado por seguridad."
        ),
        "ERROR: the XLSX holds too many internal files and was rejected for safety.",
    ),
    "io_bad_structure": (
        "ERROR: el archivo no contiene la estructura mínima de un XLSX válido.",
        "ERROR: the file lacks the minimum structure of a valid XLSX.",
    ),
    "io_member_too_large": (
        "ERROR: el XLSX contiene un archivo interno demasiado grande.",
        "ERROR: the XLSX holds an internal file that is too large.",
    ),
    "io_uncompressed_too_large": (
        "ERROR: el contenido descomprimido del XLSX supera el límite de seguridad.",
        "ERROR: the uncompressed XLSX content exceeds the safety limit.",
    ),
    "io_corrupt": (
        "ERROR: el archivo está dañado o no es un XLSX válido.",
        "ERROR: the file is damaged or is not a valid XLSX.",
    ),
    "io_too_many_rows": (
        "ERROR: la hoja supera el límite de {limit} filas.",
        "ERROR: the sheet exceeds the {limit} row limit.",
    ),
    "io_too_many_columns": (
        "ERROR: la hoja supera el límite de {limit} columnas.",
        "ERROR: the sheet exceeds the {limit} column limit.",
    ),
    "io_unreadable": (
        "ERROR: no se pudo leer el XLSX; puede estar dañado o no ser válido ({error}).",
        "ERROR: the XLSX could not be read; it may be damaged or invalid ({error}).",
    ),
    "io_missing_essential": (
        "ERROR: faltan columnas esenciales: {columns}. No se puede correr el filtro.",
        "ERROR: essential columns are missing: {columns}. The filter cannot run.",
    ),
    "io_sector_missing": (
        (
            "ERROR CRITICO: no se encontro la lista de exclusion sectorial en "
            "{path}\nEl screening debe ejecutarse desde la estructura completa "
            "del skill (scripts/ junto a references/ y assets/). Sin ese archivo "
            "las empresas Financieras y de Utilities NO se excluyen y la "
            "clasificacion resultante es invalida."
        ),
        (
            "CRITICAL ERROR: the sector exclusion list was not found at "
            "{path}\nThe screening must run from the complete skill structure "
            "(scripts/ alongside references/ and assets/). Without that file, "
            "financials and utilities are NOT excluded and the resulting "
            "classification is invalid."
        ),
    ),
    "io_sector_unreadable": (
        "ERROR CRITICO: no se pudo leer {path} ({error}). Clasificacion abortada.",
        "CRITICAL ERROR: {path} could not be read ({error}). Classification aborted.",
    ),
    "io_sector_malformed": (
        (
            "ERROR CRITICO: la lista de exclusion sectorial en {path} esta vacia "
            "o mal formada. Clasificacion abortada para no entregar resultados "
            "invalidos."
        ),
        (
            "CRITICAL ERROR: the sector exclusion list at {path} is empty or "
            "malformed. Classification aborted rather than deliver invalid results."
        ),
    ),
    "sector_no_cutoff": (
        (
            "AVISO — la lista de exclusión sectorial no declara una fecha de corte; "
            "revísala antes de confiar en empresas recién listadas o reclasificadas."
        ),
        (
            "WARNING — the sector exclusion list declares no cut-off date; review "
            "it before trusting newly listed or reclassified companies."
        ),
    ),
    "sector_bad_cutoff": (
        (
            "AVISO — la lista de exclusión sectorial declara una fecha de corte "
            "inválida; corrígela antes de actualizar el archivo."
        ),
        (
            "WARNING — the sector exclusion list declares an invalid cut-off date; "
            "fix it before updating the file."
        ),
    ),
    "sector_stale": (
        (
            "AVISO — la lista de exclusión sectorial tiene {days} días de "
            "antigüedad (corte {cutoff}); actualízala para cubrir empresas nuevas "
            "o reclasificadas."
        ),
        (
            "WARNING — the sector exclusion list is {days} days old (cut-off "
            "{cutoff}); update it to cover new or reclassified companies."
        ),
    ),
    "summary_title": (
        "══ INFORME EJECUTIVO · Screening VHC Inversiones ══",
        "══ EXECUTIVE SUMMARY · VHC Inversiones Screening ══",
    ),
    "summary_header": (
        "Export: {export} · Corrida: {run_date} · {version}",
        "Export: {export} · Run: {run_date} · {version}",
    ),
    "summary_funnel": (
        (
            "Embudo: {analyzed} empresas analizadas → {excellent} con calidad "
            "excelente y salud sólida → {deep} en Deep Dive"
        ),
        (
            "Funnel: {analyzed} companies analyzed → {excellent} with excellent "
            "quality and solid health → {deep} in Deep Dive"
        ),
    ),
    "summary_sectors": (
        " · Omitidas por método (Financieras/Utilities) {sectors}",
        " · Excluded by method (financials/utilities) {sectors}",
    ),
    "summary_categories": (
        (
            "Categorías: Deep Dive {deep} · Watchlist {watch} · Neutral {neutral} "
            "· Descartadas {discarded} ({traps} con nota de posible trampa) · "
            "Fondos/ETFs excluidos {funds}{sectors}"
        ),
        (
            "Categories: Deep Dive {deep} · Watchlist {watch} · Neutral {neutral} "
            "· Discarded {discarded} ({traps} flagged as a possible value trap) · "
            "Funds/ETFs excluded {funds}{sectors}"
        ),
    ),
    "deep_dive_header": (
        "── Deep Dive (excelente calidad + salud sana + buen precio) ──",
        "── Deep Dive (excellent quality, sound health and a good price) ──",
    ),
    "deep_dive_row_health": (" · salud ", " · health "),
    "summary_files": (
        "Archivos generados: {excel} · {dashboard}",
        "Files generated: {excel} · {dashboard}",
    ),
    # Excel: header comments, one per indicator.
    "xl_score": (
        (
            "Puntaje = señales de calidad (0-3) + señales de precio a favor (0-4) "
            "+ señales de salud (0-3). Máximo 10."
        ),
        (
            "Score = quality signals (0-3) + price signals in favor (0-4) + "
            "health signals (0-3), capped at ten."
        ),
    ),
    "xl_quality_verdict": (
        (
            "3 lentes: Greenblatt (ROIC), MSCI (ROE+deuda), AQR (4 pilares). "
            "EXCELENTE = 3 lentes en Sí · BUENA = 2 · DÉBIL = 0-1. La calidad es "
            "la puerta: sin EXCELENTE no hay Deep Dive ni Watchlist."
        ),
        (
            "Three lenses: Greenblatt (ROIC), MSCI (ROE+debt), AQR (four "
            "pillars). EXCELLENT = all three say Yes · GOOD = 2 · WEAK = 0-1. "
            "Quality is the gate: without EXCELLENT there is no Deep Dive or "
            "Watchlist."
        ),
    ),
    "xl_price_verdict": (
        (
            "4 jueces: EV/EBIT ≤10 (y positivo) · descuento ≥20% vs Fair Value "
            "· FCF Yield ≥4% · etiqueta de analistas. MUY BARATA = 3-4 a favor · "
            "BARATA = 2 · MIXTA = 1 o empate · CARA = más en contra que a favor. "
            "Veredicto neto, siempre."
        ),
        (
            "Four judges: EV/EBIT ≤10 (and positive) · discount ≥20% vs fair "
            "value · FCF yield ≥4% · analyst label. VERY CHEAP = 3-4 in favor · "
            "CHEAP = 2 · MIXED = 1 or a tie · EXPENSIVE = more against than in "
            "favor. Always a net verdict."
        ),
    ),
    "xl_health_verdict": (
        (
            "3 señales: Piotroski ≥7 · Altman ≥3 · M-Score sin alerta. "
            "EXCELENTE = 3 · MIXTA = 2 · DÉBIL = 0-1 o Altman <1.81. Salud DÉBIL "
            "bloquea Deep Dive y Watchlist."
        ),
        (
            "Three signals: Piotroski ≥7 · Altman ≥3 · M-Score with no alert. "
            "EXCELLENT = 3 · MIXED = 2 · WEAK = 0-1 or Altman below 1.81. WEAK "
            "health excludes a company from Deep Dive and Watchlist."
        ),
    ),
    "xl_piotroski": (
        "Solidez financiera de 0 a 9. ≥7 suma una señal de salud · ≤3 celda roja.",
        "Financial soundness from 0 to 9. ≥7 adds a health signal · ≤3 turns red.",
    ),
    "xl_altman": (
        (
            "Riesgo de quiebra. ≥3 suma señal · entre 1.81 y 3 zona gris · "
            "<1.81 zona de riesgo."
        ),
        (
            "Insolvency risk. ≥3 adds a signal · between 1.81 and 3 is the gray "
            "zone · below 1.81 is the risk zone."
        ),
    ),
    "xl_beneish": (
        (
            "Detector de manipulación contable. > −1.78 genera alerta; no es una "
            "prueba, sino un motivo de revisión."
        ),
        (
            "Accounting manipulation detector. Above −1.78 raises an alert; it "
            "is not proof, only a reason to review."
        ),
    ),
    "xl_roic": (
        "Lente Greenblatt: ≥20% actual y promedio de 5 años = Sí · <10% = celda roja.",
        "Greenblatt lens: ≥20% current and 5-year average = Yes · below 10% turns red.",
    ),
    "xl_roic_5y": (
        (
            "Si el ROIC actual está bajo el promedio de 5 años, se marca para "
            "revisar el moat."
        ),
        (
            "When current ROIC sits below its five-year average, the moat is "
            "flagged for review."
        ),
    ),
    "xl_roe": (
        "Lente MSCI: ≥15% con deuda sana = Sí · <10% = celda roja.",
        "MSCI lens: ≥15% with healthy debt = Yes · below 10% turns red.",
    ),
    "xl_gross_margin": (
        "Pilar rentable del lente AQR: ≥40% cuenta a favor.",
        "Profitability pillar of the AQR lens: ≥40% counts in favor.",
    ),
    "xl_ev_ebit": (
        "Juez de precio: ≤10 y positivo cuenta a favor · ≥20 o negativo cuenta en contra.",
        "Price judge: ≤10 and positive counts in favor · ≥20 or negative counts against.",
    ),
    "xl_fcf_yield": (
        "Juez de precio: ≥4% a favor · ≤2% en contra.",
        "Price judge: ≥4% in favor · ≤2% against.",
    ),
    "xl_fair_value": (
        "Valor justo de InvestingPro. Un descuento ≥20% cuenta a favor.",
        "InvestingPro fair value. A discount of 20% or more counts in favor.",
    ),
    "xl_debt_capital": (
        (
            ">60% tumba el lente MSCI. Bancos y utilities se omiten porque "
            "requieren otro criterio."
        ),
        (
            "Above 60% the MSCI lens fails. Banks and utilities are set aside "
            "because they need different criteria."
        ),
    ),
    # Excel: cells, banner and guide sheet.
    "xl_omitted_cell": (
        "⚙️ Omitida",
        "⚙️ Excluded",
    ),
    "xl_omitted_comment": (
        "{sector} — este método no lo mide bien; analizar aparte",
        "{sector} — this method does not measure it well; analyze it separately",
    ),
    "xl_fund_cell": (
        "Fondo/ETF — fuera del análisis",
        "Fund/ETF — outside the analysis",
    ),
    "xl_missing_banner": (
        (
            "⚠️  FALTAN {count} INDICADORES EN TU EXPORT — agrégalos en el screener "
            "de InvestingPro y vuelve a exportar:  {columns}    |    Las columnas "
            "en rojo llegaron vacías. No cambian la clasificación, pero pierdes "
            "contexto en el análisis."
        ),
        (
            "⚠️  {count} INDICATORS ARE MISSING FROM YOUR EXPORT — add them in the "
            "InvestingPro screener and export again:  {columns}    |    The red "
            "columns arrived empty. They do not change the classification, but you "
            "lose context in the analysis."
        ),
    ),
    "xl_missing_comment": (
        (
            "Esta columna NO venía en tu export. Agrégala con el nombre exacto "
            '"{column}" y vuelve a exportar.'
        ),
        (
            "This column was NOT in your export. Add it under the exact name "
            '"{column}" and export again.'
        ),
    ),
    "dash_core_error": (
        "No se puede generar el dashboard: faltan columnas núcleo: {columns}",
        "The dashboard cannot be generated: core columns are missing: {columns}",
    ),
    "xl_core_error": (
        "No se puede generar el Excel: faltan columnas núcleo: {columns}",
        "The Excel file cannot be generated: core columns are missing: {columns}",
    ),
    "xl_guide_intro": (
        (
            "Un filtro cuantitativo que clasifica cada empresa con tres tribunales: "
            "CALIDAD, SALUD FINANCIERA y PRECIO. Reduce el universo a una lista "
            "corta que merezca análisis cualitativo."
        ),
        (
            "A quantitative filter that puts every company through three gates: "
            "QUALITY, FINANCIAL HEALTH and PRICE. It narrows the universe to a "
            "short list worth analyzing qualitatively."
        ),
    ),
    "xl_guide_run": (
        (
            "En esta corrida: {analyzed} empresas → {excellent} con calidad "
            "excelente y salud sólida → {deep} en Deep Dive · {watch} en Watchlist "
            "· {neutral} en Neutral · {discarded} descartadas ({traps} posibles "
            "trampas) · {funds} fondos/ETFs · {sectors} omitidas por método."
        ),
        (
            "In this run: {analyzed} companies → {excellent} with excellent quality "
            "and solid health → {deep} in Deep Dive · {watch} in Watchlist · "
            "{neutral} in Neutral · {discarded} discarded ({traps} possible traps) "
            "· {funds} funds/ETFs · {sectors} excluded by method."
        ),
    ),
    "xl_cat_deep": (
        "Excelente empresa a precio atractivo. Significa investigar, no comprar.",
        "An excellent company at an attractive price. Research it — it is not a buy.",
    ),
    "xl_cat_watch": (
        "Excelente empresa cuyo precio todavía no es atractivo.",
        "An excellent company whose price is not attractive yet.",
    ),
    "xl_cat_neutral": (
        "Hoy no supera todas las puertas del método.",
        "It does not clear every gate of the method today.",
    ),
    "xl_cat_discarded": (
        "No cumple el método hoy; no es un pronóstico de mercado.",
        "It does not meet the method today; this is not a market forecast.",
    ),
    "xl_cat_omitted": (
        "Financieras y utilities requieren un análisis distinto.",
        "Financials and utilities need a different analysis.",
    ),
    "xl_cat_fund": (
        "No es una empresa y queda fuera de la clasificación.",
        "It is not a company and stays outside the classification.",
    ),
    "xl_gate_quality": (
        (
            "Greenblatt (ROIC), MSCI (ROE y deuda) y AQR (rentabilidad, "
            "crecimiento, seguridad y recompras)."
        ),
        (
            "Greenblatt (ROIC), MSCI (ROE and debt) and AQR (profitability, "
            "growth, safety and buybacks)."
        ),
    ),
    "xl_gate_health": (
        "Piotroski, Altman y Beneish; la salud débil bloquea las listas de acción.",
        (
            "Piotroski, Altman and Beneish; weak financial health excludes a "
            "company from Deep Dive and Watchlist."
        ),
    ),
    "xl_gate_price": (
        "EV/EBIT, descuento frente a Fair Value, FCF Yield y consenso de analistas.",
        "EV/EBIT, discount against fair value, FCF yield and analyst consensus.",
    ),
    "xl_guide_legal": (
        (
            "Esta herramienta es educativa. No constituye asesoría financiera ni "
            "una recomendación de inversión. Deep Dive significa investigar a fondo."
        ),
        (
            "This tool is educational. It is not financial advice nor an investment "
            "recommendation. Deep Dive means it is worth a closer look, nothing more."
        ),
    ),
    "summary_reminder": (
        (
            "Recordatorio: herramienta educativa; Deep Dive = investigar a fondo, "
            "no comprar. Los números son la mitad de la tarea."
        ),
        (
            "Reminder: this is an educational tool; Deep Dive means it is worth a "
            "closer look, not that you should buy. The numbers are half the work."
        ),
    ),
}


def term(value: str, language: str) -> str:
    """Renders a canonical engine value in the requested language."""
    if language == ENGLISH:
        return TERMS.get(value, value)
    return value


def alert(value: str, language: str) -> str:
    """Alerts arrive joined by ' · '; each part is translated separately."""
    if language != ENGLISH:
        return value
    return " · ".join(term(part.strip(), language) for part in value.split("·"))


def text(key: str, language: str, **fields) -> str:
    """Renders a cataloged sentence, filling in its placeholders."""
    spanish, english = MESSAGES[key]
    template = english if language == ENGLISH else spanish
    return template.format(**fields) if fields else template
