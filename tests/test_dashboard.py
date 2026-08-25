"""HTML dashboard tests."""

import re
from collections import Counter
from pathlib import Path

import pytest
from vhc_screening import dashboard
from vhc_screening.dashboard import generate_dashboard


def _dashboard_counts(evaluations):
    return Counter(item["bucket"] for item in evaluations.values() if not item["fund"])


def test_dashboard_renders_categories_links_and_html_escaping(report_cases, tmp_path):
    output = tmp_path / "dashboard.html"
    counts = _dashboard_counts(report_cases["evaluations"])

    generate_dashboard(
        report_cases["evaluations"],
        report_cases["order"],
        output,
        "fixture.xlsx",
        "2026-08-11",
        counts,
        1,
        2,
        0,
        3,
    )

    html = output.read_text(encoding="utf-8")
    assert "&lt;Alpha &amp; Co &quot;" in html
    assert "ALP" in html
    assert "BET" in html
    assert "Omitidas por método" in html
    assert "https://www.youtube.com/@VHCInversiones" in html
    assert "https://x.com/VHCInversiones" in html
    assert "https://www.instagram.com/vhcinversiones" in html
    assert "fonts.googleapis.com" not in html


def test_dashboard_warns_only_for_optional_columns(tmp_path):
    output = tmp_path / "opcional.html"
    counts = Counter()

    generate_dashboard(
        {},
        [],
        output,
        "fixture.xlsx",
        "2026-08-13",
        counts,
        0,
        0,
        0,
        0,
        missing=["Full Ticker"],
    )

    html = output.read_text(encoding="utf-8")
    assert "Faltan 1 indicadores" in html
    assert "No cambian la clasificación" in html


def test_dashboard_rejects_missing_core_columns(tmp_path):
    output = tmp_path / "invalido.html"
    counts = Counter()

    with pytest.raises(ValueError, match="Beneish M-Score"):
        generate_dashboard(
            {},
            [],
            output,
            "fixture.xlsx",
            "2026-08-13",
            counts,
            0,
            0,
            0,
            0,
            missing=["Beneish M-Score"],
        )

    assert not output.exists()


def test_dashboard_flags_declining_roic(evaluate_row, make_case, tmp_path):
    row, _, raw, num, pctv = make_case(
        {
            "Name": "Moat & Co",
            "Ticker": "MOAT",
            "Return on Invested Capital": 0.23,
            "Avg Return on Invested Capital (5y)": 0.24,
            "Fair Value": 130.0,
            "Fair Value Label (Analyst Targets)": "Fair",
            "Free Cash Flow Yield": 0.03,
        }
    )
    result = evaluate_row(row, raw, num, pctv)
    output = tmp_path / "moat.html"
    counts = Counter({"Deep Dive": 1, "Watchlist": 0, "Neutral": 0, "Descartada": 0})

    generate_dashboard(
        {0: result},
        [0],
        output,
        "moat.xlsx",
        "2026-08-11",
        counts,
        0,
        1,
        0,
        1,
    )

    assert "revisar moat" in output.read_text(encoding="utf-8")


def test_dashboard_still_works_without_brand_image(tmp_path):
    output = tmp_path / "sin-logo.html"
    counts = Counter({"Deep Dive": 0, "Watchlist": 0, "Neutral": 0, "Descartada": 0})

    generate_dashboard(
        {},
        [],
        output,
        "fixture.xlsx",
        "2026-08-11",
        counts,
        0,
        0,
        0,
        0,
        assets_dir=tmp_path / "sin-assets",
    )

    assert output.exists()
    assert 'src="data:image/webp;base64,"' in output.read_text(encoding="utf-8")


def test_presentation_cells_cover_their_branches():
    assert dashboard._tone(None) == "flat"
    assert dashboard._tone(0.2) == "pos"
    assert dashboard._tone(-0.2) == "neg"
    assert dashboard._tone(0.0) == "flat"
    assert dashboard._upside_cell(None) == (
        '<div class="r__up r__up--flat" data-en="N/A">N/D</div>'
    )
    assert dashboard._alert_en("M-Score · ¿Demasiado barata?") == (
        "M-Score · Too cheap?"
    )
    assert "r__up nx r__up--pos" in dashboard._upside_cell(0.2)
    assert "r__up nx r__up--neg" in dashboard._upside_cell(-0.2)
    assert "r__up nx r__up--flat" in dashboard._upside_cell(0.0)
    assert dashboard._alert_cell("—") == '<div class="r__none">—</div>'
    assert "chip chip--risk" in dashboard._alert_cell("M-Score")
    assert "chip chip--neutral" in dashboard._alert_cell("Mejora débil")


def test_watchlist_sorts_by_market_cap_and_tolerates_its_absence():
    with_cap = {"metrics": {"mcap": 2.0}}
    without_cap = {"metrics": {}}

    assert dashboard._by_market_cap(with_cap) == (0, -2.0)
    assert dashboard._by_market_cap(without_cap) == (1, 0.0)


def test_every_visible_label_ships_with_its_english(report_cases, tmp_path):
    """No user-visible string may lack its English counterpart."""
    output = tmp_path / "en.html"
    generate_dashboard(
        report_cases["evaluations"],
        report_cases["order"],
        output,
        "fixture.xlsx",
        "2026-08-22",
        _dashboard_counts(report_cases["evaluations"]),
        1,
        2,
        0,
        3,
        missing=["Full Ticker"],
    )
    html = output.read_text(encoding="utf-8")

    tags = re.findall(r'(<[a-z][^>]*aria-label="([^"]*)"[^>]*>)', html)
    assert tags
    for tag, label in tags:
        assert label == "Idioma / Language" or "data-en-al=" in tag, tag

    assert re.search(r'placeholder="[^"]*"[^>]*data-en-ph=', html)
    assert 'class="warn" data-en=' in html
    for spanish, english in (
        ("Calidad · ", "Quality · "),
        ("Salud · ", "Health · "),
        ("Precio · ", "Price · "),
    ):
        assert f'content:"{spanish}"' in html
        assert f'content:"{english}"' in html


def _class_is_used(name: str, source: str) -> bool:
    """A class counts as used when written out or composed by interpolation."""
    if re.search(rf"\b{re.escape(name)}\b", source):
        return True
    separator = max(name.rfind("--"), name.rfind("__"))
    if separator == -1:
        return False
    prefix = name[: separator + 2]
    return f"{prefix}{{" in source


def _css_and_source():
    source = Path(dashboard.__file__).read_text(encoding="utf-8")
    match = re.search(r'DASH_CSS\s*=\s*r?"""(.*?)"""', source, re.DOTALL)
    assert match is not None, "DASH_CSS block not found"
    css = match.group(1)
    return css, source.replace(css, "")


def test_no_orphan_css_classes_or_variables():
    """Every class and custom property must be defined and used."""
    css, rest = _css_and_source()

    declared = set(re.findall(r"\.([a-zA-Z][\w-]*)", css))
    unused = [name for name in sorted(declared) if not _class_is_used(name, rest)]
    assert not unused, f"CSS classes nobody uses: {unused}"

    valid = re.compile(r"^[a-zA-Z][\w-]*$")
    written = {
        token
        for value in re.findall(r'class="([^"{]*)"', rest)
        for token in value.split()
        if valid.match(token)
    }
    assert not written - declared, (
        f"classes with no CSS rule: {sorted(written - declared)}"
    )

    defined = set(re.findall(r"(--[\w-]+)\s*:", css))
    used = set(re.findall(r"var\((--[\w-]+)", css + rest))
    assert not used - defined, f"undefined custom properties: {sorted(used - defined)}"
    assert not defined - used, (
        f"custom properties nobody uses: {sorted(defined - used)}"
    )
