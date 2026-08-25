"""Coverage for the defensive branches extracted during the refactor."""

import openpyxl
from vhc_screening import dashboard, excel_report, i18n


def test_dashboard_links_cover_versions_with_and_without_full_ticker(report_cases):
    deep_dive = report_cases["evaluations"][0]
    watchlist = report_cases["evaluations"][1]

    assert "investing.com/pro" in dashboard._ticker_link(deep_dive)
    assert dashboard._ticker_link(watchlist) == "<b>BET</b>"


def test_beneish_triggers_alert_and_amber_flag(evaluate_row, make_case):
    row, _, raw, number, percentage = make_case({"Beneish M-Score": -1.0})

    result = evaluate_row(row, raw, number, percentage)

    assert "M-Score" in result["alerts"]
    assert "Beneish M-Score" in result["amber_flags"]


def test_comments_ignore_a_schema_without_columns():
    workbook = openpyxl.Workbook()
    sheet = workbook.worksheets[0]

    excel_report._add_header_comments(sheet, {}, 0, i18n.SPANISH)

    workbook.close()


def test_tab_color_recovers_missing_properties(monkeypatch):
    workbook = openpyxl.Workbook()
    sheet = workbook.worksheets[0]
    monkeypatch.setattr(sheet, "sheet_properties", None)

    excel_report._set_tab_color(sheet, "F59C00")

    properties = sheet.sheet_properties
    assert properties is not None
    assert properties.tabColor is not None
    assert properties.tabColor.rgb == "00F59C00"
    workbook.close()
