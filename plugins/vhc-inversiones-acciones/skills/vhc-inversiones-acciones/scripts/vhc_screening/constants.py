"""Constants shared across the VHC Inversiones screening."""

from pathlib import Path

SCREENING_VERSION = "v1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSETS = PROJECT_ROOT / "assets"
DEFAULT_SECTORS_FILE = PROJECT_ROOT / "references" / "sectores_excluidos.csv"

# Exact column names produced by the InvestingPro export.
NAME = "Name"
TICKER = "Ticker"
FULL_TICKER = "Full Ticker"
CURRENT_PRICE = "Price, Current"
MARKET_CAP = "Market Cap (Adjusted)"
FAIR_VALUE = "Fair Value"
FAIR_VALUE_LABEL = "Fair Value Label (Analyst Targets)"
HEALTH_LABEL = "Overall Health Label"
EV_EBIT = "EV / EBIT"
FCF_YIELD = "Free Cash Flow Yield"
ROIC = "Return on Invested Capital"
ROIC_5Y = "Avg Return on Invested Capital (5y)"
ROIC_CAGR_5Y = "Return on Invested Capital CAGR (5y)"
ROE = "Return on Equity"
GROSS_MARGIN = "Gross Profit Margin"
EPS_GROWTH = "Avg EPS Growth (5y)"
REVENUE_GROWTH = "Revenue CAGR (5y)"
FCF_NET_INCOME = "FCF / Net Income"
BUYBACK_YIELD = "Buyback Yield"
PIOTROSKI = "Piotroski Score"
ALTMAN = "Altman Z-Score"
BENEISH = "Beneish M-Score"
DEBT_CAPITAL = "Total Debt / Total Capital"
PE_RATIO = "P/E Ratio"
PEG_RATIO = "PEG Ratio Fwd"
BETA = "Beta (5 Year)"

BUCKET_DEEP_DIVE = "Deep Dive"
BUCKET_WATCHLIST = "Watchlist"
BUCKET_NEUTRAL = "Neutral"
BUCKET_DISCARDED = "Descartada"
BUCKETS = (
    BUCKET_DEEP_DIVE,
    BUCKET_WATCHLIST,
    BUCKET_NEUTRAL,
    BUCKET_DISCARDED,
)

QUALITY_EXCELLENT = "EXCELENTE"
QUALITY_GOOD = "BUENA"
QUALITY_WEAK = "DÉBIL"
VERDICT_YES = "Sí"
VERDICT_MEDIUM = "Medio"
VERDICT_NO = "No"
NOT_AVAILABLE = "N/D"

PRICE_VERY_CHEAP = "MUY BARATA"
PRICE_CHEAP = "BARATA"
PRICE_MIXED = "MIXTA"
PRICE_EXPENSIVE = "CARA"

ALERT_VALUE_TRAP = "Posible trampa de valor"
ALERT_TOO_CHEAP = "¿Demasiado barata?"
ALERT_M_SCORE = "M-Score"
ALERT_ALTMAN = "Altman zona de riesgo"
ALERT_WEAK_HEALTH = "Excelente pero salud débil"
ALERT_INSUFFICIENT = "Datos insuficientes"
ALERT_ROIC = "Revisar ROIC/moat"
ALERT_WEAK_IMPROVEMENT = "Mejora débil"

NA_VALUES = frozenset(
    {"-", "NA", "NM", "N/A", "UNAVAILABLE", "NONE", "#RESTRICTED!", ""}
)

ESSENTIAL_COLUMNS = [NAME, TICKER, CURRENT_PRICE]
CORE_COLUMNS = [
    FAIR_VALUE,
    FAIR_VALUE_LABEL,
    HEALTH_LABEL,
    EV_EBIT,
    FCF_YIELD,
    ROIC,
    ROIC_5Y,
    ROE,
    GROSS_MARGIN,
    EPS_GROWTH,
    REVENUE_GROWTH,
    FCF_NET_INCOME,
    BUYBACK_YIELD,
    PIOTROSKI,
    ALTMAN,
    BENEISH,
    DEBT_CAPITAL,
]
OPTIONAL_COLUMNS = [FULL_TICKER, MARKET_CAP, PE_RATIO, PEG_RATIO, BETA]
PERCENTAGE_COLUMNS = [
    ROIC,
    ROIC_5Y,
    ROE,
    GROSS_MARGIN,
    FCF_YIELD,
    EPS_GROWTH,
    REVENUE_GROWTH,
    BUYBACK_YIELD,
    DEBT_CAPITAL,
]
FUND_KEYWORDS = (
    "ETF",
    "FUND",
    "TRUST",
    "ISHARES",
    "SPDR",
    "VANGUARD",
    "INVESCO",
    "INDEX",
)

BUCKET_EMOJI = {
    BUCKET_DEEP_DIVE: "🔬 Deep Dive",
    BUCKET_WATCHLIST: "📋 Watchlist",
    BUCKET_NEUTRAL: "⚪ Neutral",
    BUCKET_DISCARDED: "❌ Descartada",
}
ALERT_PREFIX = {
    ALERT_VALUE_TRAP: "⚠️ ",
    ALERT_TOO_CHEAP: "⚠️ ",
    ALERT_M_SCORE: "⚠️ ",
    ALERT_ALTMAN: "⚠️ ",
    ALERT_WEAK_HEALTH: "⚠️ ",
    ALERT_INSUFFICIENT: "⚠️ ",
    ALERT_ROIC: "🔎 ",
    ALERT_WEAK_IMPROVEMENT: "🔎 ",
}
ALERT_ORDER = [
    ALERT_INSUFFICIENT,
    ALERT_ALTMAN,
    ALERT_M_SCORE,
    ALERT_VALUE_TRAP,
    ALERT_WEAK_HEALTH,
    ALERT_TOO_CHEAP,
    ALERT_WEAK_IMPROVEMENT,
]
