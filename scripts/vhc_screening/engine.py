"""Canonical quantitative classification core."""

from typing import Any

from .constants import (
    ALERT_ALTMAN,
    ALERT_INSUFFICIENT,
    ALERT_M_SCORE,
    ALERT_ORDER,
    ALERT_TOO_CHEAP,
    ALERT_VALUE_TRAP,
    ALERT_WEAK_HEALTH,
    ALERT_WEAK_IMPROVEMENT,
    ALTMAN,
    BENEISH,
    BUCKET_DEEP_DIVE,
    BUCKET_DISCARDED,
    BUCKET_NEUTRAL,
    BUCKET_WATCHLIST,
    BUYBACK_YIELD,
    CURRENT_PRICE,
    DEBT_CAPITAL,
    EPS_GROWTH,
    EV_EBIT,
    FAIR_VALUE,
    FAIR_VALUE_LABEL,
    FCF_NET_INCOME,
    FCF_YIELD,
    FULL_TICKER,
    FUND_KEYWORDS,
    GROSS_MARGIN,
    HEALTH_LABEL,
    MARKET_CAP,
    NAME,
    NOT_AVAILABLE,
    PIOTROSKI,
    PRICE_CHEAP,
    PRICE_EXPENSIVE,
    PRICE_MIXED,
    PRICE_VERY_CHEAP,
    QUALITY_EXCELLENT,
    QUALITY_GOOD,
    QUALITY_WEAK,
    REVENUE_GROWTH,
    ROE,
    ROIC,
    ROIC_5Y,
    TICKER,
    VERDICT_MEDIUM,
    VERDICT_NO,
    VERDICT_YES,
)
from .io import Accessor, Row


def _greenblatt(roic: float | None, roic_5y: float | None) -> str:
    if roic is None:
        if roic_5y is None:
            return NOT_AVAILABLE
        return VERDICT_NO if roic_5y < 10 else VERDICT_MEDIUM
    if roic_5y is None:
        return VERDICT_NO if roic < 10 else VERDICT_MEDIUM
    if roic >= 20 and roic_5y >= 20:
        return VERDICT_YES
    return VERDICT_NO if roic < 10 or roic_5y < 10 else VERDICT_MEDIUM


def _msci(roe: float | None, debt: float | None, altman: float | None) -> str:
    leveraged = (debt is not None and debt > 60) or (
        debt is None and altman is not None and altman < 1.81
    )
    if roe is None:
        return NOT_AVAILABLE
    if roe >= 15 and not leveraged:
        return VERDICT_YES
    return VERDICT_NO if roe < 10 or leveraged else VERDICT_MEDIUM


def _growth_pillar(eps_growth: float | None, revenue_growth: float | None) -> str:
    if eps_growth is None:
        if revenue_growth is None:
            return "i"
        growth = revenue_growth
    elif revenue_growth is None:
        growth = eps_growth
    else:
        if eps_growth > 0 and revenue_growth > 0:
            return "v"
        return "x" if eps_growth < 0 or revenue_growth < 0 else "i"
    if growth > 0:
        return "v"
    if growth < 0:
        return "x"
    return "i"


def _safety_pillar(altman: float | None, health_label: str) -> str:
    if altman is None:
        return "i"
    if altman >= 3:
        return "v"
    if altman < 1.81:
        return "x"
    return "v" if health_label in {"good", "great", "excellent"} else "i"


def _payout_pillar(buyback: float | None) -> str:
    if buyback is None:
        return "i"
    if buyback >= 0:
        return "v"
    return "x" if buyback < -2 else "i"


def _aqr(metrics: dict[str, Any]) -> tuple[str, bool]:
    conversion = (
        metrics["fcfni"] is not None
        and metrics["fcfni"] >= 0.8
        and metrics["fcfy"] is not None
        and metrics["fcfy"] > 0
    )
    profitable_signals = (
        metrics["roe"] is not None and metrics["roe"] >= 15,
        metrics["gm"] is not None and metrics["gm"] >= 40,
        conversion,
    )
    profitable = "v" if sum(profitable_signals) >= 2 else "i"
    pillars = [
        profitable,
        _growth_pillar(metrics["epsg"], metrics["revg"]),
        _safety_pillar(metrics["alt"], metrics["health"]),
        _payout_pillar(metrics["bb"]),
    ]
    if pillars.count("v") >= 3 and pillars.count("x") == 0:
        return VERDICT_YES, conversion
    verdict = VERDICT_NO if pillars.count("x") >= 2 else VERDICT_MEDIUM
    return verdict, conversion


def _quality(metrics: dict[str, Any]) -> tuple[list[str], int, str, bool]:
    aqr, conversion = _aqr(metrics)
    lenses = [
        _greenblatt(metrics["roic"], metrics["roic5"]),
        _msci(metrics["roe"], metrics["dc"], metrics["alt"]),
        aqr,
    ]
    positive = lenses.count(VERDICT_YES)
    if positive == 3:
        quality = QUALITY_EXCELLENT
    elif positive == 2:
        quality = QUALITY_GOOD
    else:
        quality = QUALITY_WEAK
    return lenses, positive, quality, conversion


def _fair_value_upside(metrics: dict[str, Any]) -> float | None:
    fair_value = metrics["fv"]
    current_price = metrics["price"]
    if fair_value is None or not current_price or current_price <= 0:
        return None
    return (fair_value - current_price) / current_price


def _price_signal_counts(
    metrics: dict[str, Any], upside: float | None
) -> tuple[int, int]:
    favorable = sum(
        (
            metrics["evebit"] is not None and 0 < metrics["evebit"] <= 10,
            upside is not None and upside >= 0.20,
            metrics["fcfy"] is not None and metrics["fcfy"] >= 4,
            metrics["lbl"] in {"bargain", "undervalued"},
        )
    )
    contrary = sum(
        (
            upside is not None and upside <= -0.10,
            metrics["evebit"] is not None
            and (metrics["evebit"] >= 20 or metrics["evebit"] < 0),
            metrics["fcfy"] is not None and metrics["fcfy"] <= 2,
            metrics["lbl"] == "overvalued",
        )
    )
    return favorable, contrary


def _price_verdict(favorable: int, contrary: int) -> str:
    if contrary >= 2 and contrary > favorable:
        return PRICE_EXPENSIVE
    if favorable >= 3 and favorable > contrary:
        return PRICE_VERY_CHEAP
    if favorable == 2 and favorable > contrary:
        return PRICE_CHEAP
    return PRICE_MIXED


def _price(metrics: dict[str, Any]) -> tuple[str, int, int, float | None]:
    upside = _fair_value_upside(metrics)
    favorable, contrary = _price_signal_counts(metrics, upside)
    return _price_verdict(favorable, contrary), favorable, contrary, upside


def _health(metrics: dict[str, Any]) -> tuple[str, int]:
    positive = sum(
        (
            metrics["pio"] is not None and metrics["pio"] >= 7,
            metrics["alt"] is not None and metrics["alt"] >= 3,
            metrics["m"] is not None and metrics["m"] <= -1.78,
        )
    )
    if (metrics["alt"] is not None and metrics["alt"] < 1.81) or positive <= 1:
        return QUALITY_WEAK, positive
    return (QUALITY_EXCELLENT if positive == 3 else PRICE_MIXED), positive


def _bucket(quality: str, health: str, price: str, insufficient: bool) -> str:
    if insufficient:
        return BUCKET_DISCARDED
    if quality == QUALITY_EXCELLENT and health != QUALITY_WEAK:
        if price in {PRICE_VERY_CHEAP, PRICE_CHEAP}:
            return BUCKET_DEEP_DIVE
        return BUCKET_WATCHLIST
    if quality in {QUALITY_EXCELLENT, QUALITY_GOOD}:
        return BUCKET_NEUTRAL
    return BUCKET_DISCARDED


def _is_value_trap(quality: str, price: str) -> bool:
    return quality == QUALITY_WEAK and price in {PRICE_VERY_CHEAP, PRICE_CHEAP}


def _is_too_cheap(metrics: dict[str, Any], quality: str, favorable: int) -> bool:
    large_upside = metrics["upside"] is not None and metrics["upside"] >= 0.40
    return quality == QUALITY_EXCELLENT and (large_upside or favorable >= 3)


def _has_m_score_alert(metrics: dict[str, Any]) -> bool:
    return metrics["m"] is not None and metrics["m"] > -1.78


def _has_weak_improvement_alert(metrics: dict[str, Any], quality: str) -> bool:
    weak_improvement = metrics["pio"] is not None and metrics["pio"] <= 3
    return quality == QUALITY_EXCELLENT and weak_improvement


def _has_altman_alert(metrics: dict[str, Any]) -> bool:
    return metrics["alt"] is not None and metrics["alt"] < 1.81


def _alert_checks(
    metrics: dict[str, Any],
    quality: str,
    health: str,
    price: str,
    favorable: int,
    insufficient: bool,
) -> tuple[tuple[str, bool], ...]:
    return (
        (ALERT_VALUE_TRAP, _is_value_trap(quality, price)),
        (ALERT_TOO_CHEAP, _is_too_cheap(metrics, quality, favorable)),
        (ALERT_M_SCORE, _has_m_score_alert(metrics)),
        (
            ALERT_WEAK_IMPROVEMENT,
            _has_weak_improvement_alert(metrics, quality),
        ),
        (ALERT_ALTMAN, _has_altman_alert(metrics)),
        (ALERT_WEAK_HEALTH, quality == QUALITY_EXCELLENT and health == QUALITY_WEAK),
        (ALERT_INSUFFICIENT, insufficient),
    )


def _alerts(
    metrics: dict[str, Any],
    quality: str,
    health: str,
    price: str,
    favorable: int,
    insufficient: bool,
) -> str:
    checks = _alert_checks(metrics, quality, health, price, favorable, insufficient)
    alerts = [alert for alert, active in checks if active]
    alerts.sort(key=lambda alert: ALERT_ORDER.index(alert))
    return " · ".join(alerts[:3]) if alerts else "—"


def _is_below(metrics: dict[str, Any], key: str, threshold: float) -> bool:
    value = metrics[key]
    return value is not None and value < threshold


def _is_at_most(metrics: dict[str, Any], key: str, threshold: float) -> bool:
    value = metrics[key]
    return value is not None and value <= threshold


def _is_above(metrics: dict[str, Any], key: str, threshold: float) -> bool:
    value = metrics[key]
    return value is not None and value > threshold


def _failed_fcf_conversion(metrics: dict[str, Any], conversion: bool) -> bool:
    if metrics["fcfni"] is None or conversion:
        return False
    non_positive_yield = metrics["fcfy"] is not None and metrics["fcfy"] <= 0
    return metrics["fcfni"] < 0.8 or non_positive_yield


def _risky_ev_ebit(metrics: dict[str, Any]) -> bool:
    value = metrics["evebit"]
    return value is not None and (value >= 20 or value < 0)


def _red_risk_flags(metrics: dict[str, Any], conversion: bool) -> set[str]:
    checks = (
        (ROIC, _is_below(metrics, "roic", 10)),
        (ROIC_5Y, _is_below(metrics, "roic5", 10)),
        (ROE, _is_below(metrics, "roe", 10)),
        (EPS_GROWTH, _is_below(metrics, "epsg", 0)),
        (REVENUE_GROWTH, _is_below(metrics, "revg", 0)),
        (FCF_NET_INCOME, _failed_fcf_conversion(metrics, conversion)),
        (BUYBACK_YIELD, _is_below(metrics, "bb", -2)),
        (DEBT_CAPITAL, _is_above(metrics, "dc", 60)),
        (PIOTROSKI, _is_at_most(metrics, "pio", 3)),
        (FCF_YIELD, _is_at_most(metrics, "fcfy", 2)),
        (EV_EBIT, _risky_ev_ebit(metrics)),
    )
    return {column for column, failed in checks if failed}


def _altman_risk_flags(value: float | None) -> tuple[set[str], set[str]]:
    if value is None or value >= 3:
        return set(), set()
    if value < 1.81:
        return {ALTMAN}, set()
    return set(), {ALTMAN}


def _risk_flags(metrics: dict[str, Any], conversion: bool) -> tuple[set[str], set[str]]:
    red = _red_risk_flags(metrics, conversion)
    altman_red, amber = _altman_risk_flags(metrics["alt"])
    red.update(altman_red)
    if _has_m_score_alert(metrics):
        amber.add(BENEISH)
    return red, amber


def _read_metrics(
    row: Row, raw: Accessor, number: Accessor, percentage: Accessor
) -> dict[str, Any]:
    return {
        "mcap": number(row, MARKET_CAP),
        "roic": percentage(row, ROIC),
        "roic5": percentage(row, ROIC_5Y),
        "roe": percentage(row, ROE),
        "gm": percentage(row, GROSS_MARGIN),
        "fcfy": percentage(row, FCF_YIELD),
        "evebit": number(row, EV_EBIT),
        "pio": number(row, PIOTROSKI),
        "alt": number(row, ALTMAN),
        "m": number(row, BENEISH),
        "dc": percentage(row, DEBT_CAPITAL),
        "fv": number(row, FAIR_VALUE),
        "price": number(row, CURRENT_PRICE),
        "epsg": percentage(row, EPS_GROWTH),
        "revg": percentage(row, REVENUE_GROWTH),
        "fcfni": number(row, FCF_NET_INCOME),
        "bb": percentage(row, BUYBACK_YIELD),
        "lbl": str(raw(row, FAIR_VALUE_LABEL) or "").strip().lower(),
        "ft": str(raw(row, FULL_TICKER) or ""),
        "health": str(raw(row, HEALTH_LABEL) or "").strip().lower(),
    }


def _has_insufficient_data(metrics: dict[str, Any]) -> bool:
    core = (
        metrics["roic"],
        metrics["roic5"],
        metrics["roe"],
        metrics["gm"],
        metrics["epsg"],
        metrics["revg"],
        metrics["fcfni"],
        metrics["bb"],
        metrics["evebit"],
        metrics["fcfy"],
        metrics["fv"],
        metrics["pio"],
    )
    return sum(value is None for value in core) >= 5


def evaluate(
    row: Row,
    raw: Accessor,
    number: Accessor,
    percentage: Accessor,
    sector_exclusions: dict[str, str],
) -> dict[str, Any]:
    """Classifies one row with no side effects."""
    name = str(raw(row, NAME) or "")
    ticker = str(raw(row, TICKER) or "")
    piotroski = number(row, PIOTROSKI)
    roic = percentage(row, ROIC)
    looks_like_fund = any(keyword in name.upper() for keyword in FUND_KEYWORDS)
    if looks_like_fund and (piotroski is None or roic is None):
        return {"fund": True, "name": name, "ticker": ticker}

    normalized_ticker = ticker.strip()
    if normalized_ticker in sector_exclusions:
        return {
            "fund": True,
            "excluded_sector": sector_exclusions[normalized_ticker],
            "name": name,
            "ticker": normalized_ticker,
        }

    metrics = _read_metrics(row, raw, number, percentage)
    lenses, quality_count, quality, conversion = _quality(metrics)
    price, price_count, contrary_count, upside = _price(metrics)
    health, health_count = _health(metrics)
    metrics["upside"] = upside
    insufficient = _has_insufficient_data(metrics)
    bucket = _bucket(quality, health, price, insufficient)
    alerts = _alerts(metrics, quality, health, price, price_count, insufficient)
    red, amber = _risk_flags(metrics, conversion)
    metrics.pop("health")
    metrics.pop("upside")

    return {
        "fund": False,
        "name": name,
        "ticker": ticker,
        "bucket": bucket,
        "score": quality_count + price_count + health_count,
        "lenses": lenses,
        "quality": quality,
        "quality_count": quality_count,
        "price": price,
        "price_count": price_count,
        "contrary_count": contrary_count,
        "upside": upside,
        "health": health,
        "health_count": health_count,
        "alerts": alerts,
        "red_flags": red,
        "amber_flags": amber,
        "upside_red": upside is not None and upside <= -0.10,
        "metrics": metrics,
    }
