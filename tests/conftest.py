"""Shared fixtures for the screening test suite."""

import json
from pathlib import Path

import pytest
from vhc_screening.constants import (
    CORE_COLUMNS,
    DEFAULT_SECTORS_FILE,
    ESSENTIAL_COLUMNS,
    OPTIONAL_COLUMNS,
)
from vhc_screening.engine import evaluate
from vhc_screening.io import load_sector_exclusions, make_accessors

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
EXPECTED = ROOT / "tests" / "expected"


@pytest.fixture(name="project_root", scope="session")
def fixture_project_root():
    return ROOT


@pytest.fixture(name="complete_market_view_path", scope="session")
def fixture_complete_market_view_path():
    return FIXTURES / "screening_market_view_complete.xlsx"


@pytest.fixture(name="incomplete_market_view_path", scope="session")
def fixture_incomplete_market_view_path():
    return FIXTURES / "screening_market_view_incomplete.xlsx"


@pytest.fixture(name="complete_golden", scope="session")
def fixture_complete_golden():
    path = EXPECTED / "evaluation_golden_complete.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(name="incomplete_expected", scope="session")
def fixture_incomplete_expected():
    path = EXPECTED / "export_incomplete_expected.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(name="sector_exclusions", scope="session")
def fixture_sector_exclusions():
    return load_sector_exclusions(DEFAULT_SECTORS_FILE)


@pytest.fixture(name="evaluate_row")
def fixture_evaluate_row(sector_exclusions):
    def apply(row, raw, number, percentage):
        return evaluate(
            row,
            raw,
            number,
            percentage,
            sector_exclusions,
        )

    return apply


@pytest.fixture(name="make_case")
def fixture_make_case():
    """Builds a complete synthetic row using the InvestingPro schema."""
    columns = list(dict.fromkeys(ESSENTIAL_COLUMNS + CORE_COLUMNS + OPTIONAL_COLUMNS))
    defaults = {
        "Name": "Empresa Excelente",
        "Ticker": "TEST",
        "Full Ticker": "nasdaq:TEST",
        "Price, Current": 100.0,
        "Market Cap (Adjusted)": 10_000_000_000.0,
        "Fair Value": 150.0,
        "Fair Value Label (Analyst Targets)": "Undervalued",
        "Overall Health Label": "Great",
        "EV / EBIT": 8.0,
        "Free Cash Flow Yield": 0.05,
        "Return on Invested Capital": 0.25,
        "Avg Return on Invested Capital (5y)": 0.24,
        "Return on Equity": 0.20,
        "Gross Profit Margin": 0.50,
        "Avg EPS Growth (5y)": 0.10,
        "Revenue CAGR (5y)": 0.08,
        "FCF / Net Income": 1.0,
        "Buyback Yield": 0.0,
        "Piotroski Score": 8.0,
        "Altman Z-Score": 3.5,
        "Beneish M-Score": -2.0,
        "Total Debt / Total Capital": 0.30,
        "P/E Ratio": 15.0,
        "PEG Ratio Fwd": 1.2,
        "Beta (5 Year)": 1.0,
    }

    def make(overrides=None):
        values = defaults | (overrides or {})
        header_map = {name: index for index, name in enumerate(columns)}
        row = [values.get(name) for name in columns]
        raw, number, percentage = make_accessors(header_map)
        return row, header_map, raw, number, percentage

    return make


@pytest.fixture(name="report_cases")
def fixture_report_cases(make_case, evaluate_row):
    """Enough cases to exercise all four presentation paths."""

    def evaluated(overrides=None):
        row, header_map, raw, number, percentage = make_case(overrides)
        return row, header_map, evaluate_row(row, raw, number, percentage)

    cases = [
        evaluated({"Name": '<Alpha & Co "Especial">', "Ticker": "ALP"}),
        evaluated(
            {
                "Name": "Beta",
                "Ticker": "BET",
                "Full Ticker": "",
                "Fair Value": 100.0,
                "Fair Value Label (Analyst Targets)": "Fair",
                "EV / EBIT": 15.0,
                "Free Cash Flow Yield": 0.03,
            }
        ),
        evaluated(
            {
                "Name": "Global Index ETF",
                "Ticker": "ETF1",
                "Return on Invested Capital": None,
                "Piotroski Score": None,
            }
        ),
        evaluated({"Name": "Banco", "Ticker": "JPM"}),
    ]
    return {
        "rows": [case[0] for case in cases],
        "hmap": cases[0][1],
        "evaluations": {index: case[2] for index, case in enumerate(cases)},
        "order": list(range(len(cases))),
    }
