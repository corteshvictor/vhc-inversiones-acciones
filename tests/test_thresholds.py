"""Explicit tests for thresholds, conversions and presentation."""

import pytest
from vhc_screening.dashboard import _thousands_es as miles
from vhc_screening.dashboard import chip_class, escape_html, format_metric
from vhc_screening.io import make_accessors, normalize


def evaluate(evaluate_row, make_case, overrides=None):
    row, _, raw, num, pctv = make_case(overrides)
    return evaluate_row(row, raw, num, pctv)


@pytest.mark.parametrize(
    ("roic", "roic_5y", "expected"),
    [
        (0.20, 0.20, "Sí"),
        (0.10, 0.10, "Medio"),
        (0.0999, 0.20, "No"),
        (None, 0.25, "Medio"),
        (None, 0.05, "No"),
        (None, None, "N/D"),
        (0.15, None, "Medio"),
        (0.05, None, "No"),
    ],
)
def test_greenblatt_lens_boundaries(evaluate_row, make_case, roic, roic_5y, expected):
    result = evaluate(
        evaluate_row,
        make_case,
        {
            "Return on Invested Capital": roic,
            "Avg Return on Invested Capital (5y)": roic_5y,
        },
    )
    assert result["lenses"][0] == expected


@pytest.mark.parametrize(
    ("altman", "expected_health", "red", "amber"),
    [
        (3.0, "EXCELENTE", False, False),
        (1.81, "MIXTA", False, True),
        (1.80, "DÉBIL", True, False),
    ],
)
def test_altman_boundaries(
    evaluate_row, make_case, altman, expected_health, red, amber
):
    result = evaluate(evaluate_row, make_case, {"Altman Z-Score": altman})
    assert result["health"] == expected_health
    assert ("Altman Z-Score" in result["red_flags"]) is red
    assert ("Altman Z-Score" in result["amber_flags"]) is amber


@pytest.mark.parametrize("price", [None, 0.0, -1.0])
def test_invalid_current_price_yields_no_upside(evaluate_row, make_case, price):
    result = evaluate(
        evaluate_row,
        make_case,
        {"Price, Current": price},
    )

    assert result["upside"] is None


def test_accessors_normalize_na_and_percentages():
    hmap = {"A": 0, "B": 1, "C": 2}
    raw, num, pctv = make_accessors(hmap)
    row = [" N/A ", 0.478, "texto"]

    assert raw(row, "A") is None
    assert raw(row, "Z") is None
    assert num(row, "B") == pytest.approx(0.478)
    assert pctv(row, "B") == pytest.approx(47.8)
    assert num(row, "C") is None


def test_presentation_helpers():
    assert normalize("  Fair\n Value ") == "Fair Value"
    assert escape_html('A&B <C> "D"') == "A&amp;B &lt;C&gt; &quot;D&quot;"
    assert format_metric(None) == "N/D"
    assert format_metric(12.345, "pct") == "12,3 %"
    assert format_metric(0.125, "up") == "+12,5 %"
    assert format_metric(8.9, "int") == "8"
    assert format_metric(8.9) == "8,90"
    assert chip_class("EXCELENTE") == "chip--quality"
    assert chip_class("MUY BARATA") == "chip--price"
    assert chip_class("Sí") == "chip--quality"
    assert chip_class("valor desconocido") == "chip--neutral"
    assert miles(1000) == "1.000"
    assert miles(0) == "0"
