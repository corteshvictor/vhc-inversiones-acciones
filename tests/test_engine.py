"""Financial core tests and full-reference regression."""

import hashlib
import json
from collections import Counter

import openpyxl
from vhc_screening.io import make_accessors, read_export


def evaluate(evaluate_row, make_case, overrides=None):
    row, _, raw, num, pctv = make_case(overrides)
    return evaluate_row(row, raw, num, pctv)


def test_excellent_and_cheap_company_enters_deep_dive(evaluate_row, make_case):
    result = evaluate(evaluate_row, make_case)

    assert result["fund"] is False
    assert result["bucket"] == "Deep Dive"
    assert result["score"] == 10
    assert result["lenses"] == ["Sí", "Sí", "Sí"]
    assert result["quality"] == "EXCELENTE"
    assert result["price"] == "MUY BARATA"
    assert result["health"] == "EXCELENTE"


def test_excellent_company_without_attractive_price_goes_to_watchlist(
    evaluate_row, make_case
):
    result = evaluate(
        evaluate_row,
        make_case,
        {
            "Fair Value": 100.0,
            "Fair Value Label (Analyst Targets)": "Fair",
            "EV / EBIT": 15.0,
            "Free Cash Flow Yield": 0.03,
        },
    )

    assert result["bucket"] == "Watchlist"
    assert result["price"] == "MIXTA"
    assert result["price_count"] == 0


def test_good_quality_does_not_pass_the_gate(evaluate_row, make_case):
    result = evaluate(
        evaluate_row,
        make_case,
        {
            "Return on Invested Capital": 0.15,
            "Avg Return on Invested Capital (5y)": 0.15,
        },
    )

    assert result["lenses"][0] == "Medio"
    assert result["quality"] == "BUENA"
    assert result["bucket"] == "Neutral"


def test_weak_and_cheap_company_is_a_possible_trap(evaluate_row, make_case):
    result = evaluate(
        evaluate_row,
        make_case,
        {
            "Return on Invested Capital": 0.05,
            "Avg Return on Invested Capital (5y)": 0.05,
            "Return on Equity": 0.05,
            "Gross Profit Margin": 0.10,
            "Avg EPS Growth (5y)": -0.01,
            "Revenue CAGR (5y)": -0.01,
            "FCF / Net Income": 0.5,
            "Buyback Yield": -0.03,
            "Total Debt / Total Capital": 0.70,
        },
    )

    assert result["quality"] == "DÉBIL"
    assert result["bucket"] == "Descartada"
    assert "Posible trampa de valor" in result["alerts"]
    assert "Return on Invested Capital" in result["red_flags"]
    assert "Total Debt / Total Capital" in result["red_flags"]


def test_weak_health_blocks_an_excellent_company(evaluate_row, make_case):
    result = evaluate(
        evaluate_row,
        make_case,
        {
            "Piotroski Score": 3.0,
            "Altman Z-Score": None,
        },
    )

    assert result["quality"] == "EXCELENTE"
    assert result["health"] == "DÉBIL"
    assert result["bucket"] == "Neutral"
    assert "Excelente pero salud débil" in result["alerts"]
    assert "Mejora débil" in result["alerts"]


def test_insufficient_data_discards_the_company(evaluate_row, make_case):
    result = evaluate(
        evaluate_row,
        make_case,
        {
            "Return on Invested Capital": None,
            "Avg Return on Invested Capital (5y)": None,
            "Gross Profit Margin": None,
            "Avg EPS Growth (5y)": None,
            "Revenue CAGR (5y)": None,
            "FCF / Net Income": None,
        },
    )

    assert result["bucket"] == "Descartada"
    assert "Datos insuficientes" in result["alerts"]


def test_company_without_metrics_is_not_mistaken_for_a_fund(evaluate_row, make_case):
    missing_metrics = {
        "Return on Invested Capital": None,
        "Avg Return on Invested Capital (5y)": None,
        "Return on Equity": None,
        "Gross Profit Margin": None,
        "Avg EPS Growth (5y)": None,
        "Revenue CAGR (5y)": None,
        "FCF / Net Income": None,
        "Buyback Yield": None,
        "Piotroski Score": None,
        "Altman Z-Score": None,
        "Beneish M-Score": None,
        "Total Debt / Total Capital": None,
    }

    result = evaluate(evaluate_row, make_case, missing_metrics)

    assert result["fund"] is False
    assert result["bucket"] == "Descartada"
    assert "Datos insuficientes" in result["alerts"]


def test_fund_and_excluded_sector_are_not_classified(evaluate_row, make_case):
    fund = evaluate(
        evaluate_row,
        make_case,
        {
            "Name": "Global Index ETF",
            "Ticker": "ETF1",
            "Return on Invested Capital": None,
            "Piotroski Score": None,
        },
    )
    sector = evaluate(evaluate_row, make_case, {"Ticker": "JPM"})

    assert fund == {"fund": True, "name": "Global Index ETF", "ticker": "ETF1"}
    assert sector["fund"] is True
    assert sector["excluded_sector"] == "Financiero"


def test_missing_buyback_is_informational(evaluate_row, make_case):
    result = evaluate(evaluate_row, make_case, {"Buyback Yield": None})

    assert result["lenses"][2] == "Sí"
    assert result["metrics"]["bb"] is None


def test_xlsx_regression_with_complete_core_schema(evaluate_row, make_case, tmp_path):
    source_row, header_map, _, _, _ = make_case()
    headers = [
        header
        for header, _index in sorted(header_map.items(), key=lambda item: item[1])
    ]
    path = tmp_path / "screening_completo.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.worksheets[0]
    sheet.append(headers)
    sheet.append(source_row)
    workbook.save(path)
    workbook.close()

    rows, parsed_map, missing = read_export(path)
    raw, number, percentage = make_accessors(parsed_map)
    result = evaluate_row(rows[0], raw, number, percentage)

    assert missing == []
    assert result["fund"] is False
    assert result["bucket"] == "Deep Dive"
    assert result["score"] == 10


def test_incomplete_real_export_declares_missing_columns(
    incomplete_market_view_path, incomplete_expected
):
    assert incomplete_market_view_path.exists(), "Missing the reference real export"
    rows, hmap, missing = read_export(incomplete_market_view_path)

    assert incomplete_market_view_path.name == incomplete_expected["source_file"]
    assert len(rows) == incomplete_expected["rows"]
    assert len(hmap) == incomplete_expected["columns"]
    assert missing == incomplete_expected["missing_core"]


def test_full_regression_of_the_real_market_view(
    evaluate_row, complete_market_view_path, complete_golden
):
    assert complete_market_view_path.exists(), "Missing the complete real export"
    rows, hmap, missing = read_export(complete_market_view_path)
    raw, num, pctv = make_accessors(hmap)
    evaluations = [evaluate_row(row, raw, num, pctv) for row in rows]

    def normalize(value):
        if isinstance(value, set):
            return sorted(value)
        raise TypeError(f"Non-serializable type: {type(value)!r}")

    payload = json.dumps(
        evaluations,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=normalize,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    buckets = Counter(
        "sector"
        if item.get("excluded_sector")
        else "fund"
        if item["fund"]
        else item["bucket"]
        for item in evaluations
    )

    assert complete_market_view_path.name == complete_golden["source_file"]
    assert len(rows) == complete_golden["rows"]
    assert len(hmap) == complete_golden["columns"]
    assert missing == complete_golden["missing_core"]
    assert buckets == complete_golden["buckets"]
    assert digest == complete_golden["sha256"]
