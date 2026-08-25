"""Command-line interface tests."""

import runpy
import sys
from collections import Counter
from datetime import UTC, datetime

import openpyxl
import pytest
from vhc_screening import cli, i18n
from vhc_screening.io import make_accessors


def test_output_paths_do_not_overwrite_runs_within_the_same_second(tmp_path):
    started_at = datetime(2026, 8, 12, 14, 30, 45, tzinfo=UTC)

    run_date, first_excel, first_dashboard = cli._output_paths(tmp_path, started_at)
    first_excel.touch()
    first_dashboard.touch()
    _, second_excel, second_dashboard = cli._output_paths(tmp_path, started_at)

    assert run_date == "2026-08-12T14:30:45"
    assert first_excel.name == "Screening_VHC_2026-08-12_143045.xlsx"
    assert first_dashboard.name == "Dashboard_VHC_2026-08-12_143045.html"
    assert second_excel.name == "Screening_VHC_2026-08-12_143045_2.xlsx"
    assert second_dashboard.name == "Dashboard_VHC_2026-08-12_143045_2.html"


def test_main_relays_the_sector_age_warning(monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_sector_exclusions", lambda _path, language: {})
    monkeypatch.setattr(
        cli,
        "sector_list_age_warning",
        lambda _path, language: f"[{language}] lista sectorial desactualizada",
    )
    monkeypatch.setattr(cli, "run", lambda **_kwargs: None)

    cli.main([])

    assert "[es] lista sectorial desactualizada" in capsys.readouterr().out


def test_main_rejects_incomplete_real_export_without_writing_outputs(
    incomplete_market_view_path, tmp_path
):
    with pytest.raises(SystemExit) as captured:
        cli.main([str(incomplete_market_view_path), "--outdir", str(tmp_path)])

    message = str(captured.value)
    assert "faltan 2 de los 17 indicadores núcleo obligatorios" in message
    assert "Avg Return on Invested Capital (5y)" in message
    assert "Beneish M-Score" in message
    assert "CAGR mide crecimiento; Avg mide el nivel promedio" in message
    assert not list(tmp_path.glob("Screening_VHC_*.xlsx"))
    assert not list(tmp_path.glob("Dashboard_VHC_*.html"))


def test_core_validator_omits_the_roic_note_when_not_applicable():
    with pytest.raises(SystemExit) as captured:
        cli._require_core_columns(["Beneish M-Score"], {}, i18n.SPANISH)

    assert "CAGR mide crecimiento" not in str(captured.value)


def test_main_processes_complete_real_export_and_writes_both_outputs(
    complete_market_view_path, capsys, tmp_path
):
    output_dir = tmp_path / "salidas"

    cli.main([str(complete_market_view_path), "--outdir", str(output_dir)])

    stdout = capsys.readouterr().out
    xlsx_files = list(output_dir.glob("Screening_VHC_*.xlsx"))
    html_files = list(output_dir.glob("Dashboard_VHC_*.html"))
    assert "empresas analizadas" in stdout
    assert "Deep Dive 0" not in stdout
    assert len(xlsx_files) == 1
    assert len(html_files) == 1

    workbook = openpyxl.load_workbook(xlsx_files[0], read_only=False, data_only=False)
    assert workbook.sheetnames == ["Screening", "Instructivo"]
    workbook.close()

    dashboard = html_files[0].read_text(encoding="utf-8")
    assert "VHC Inversiones" in dashboard
    assert 'class="warn"' not in dashboard


def test_run_shows_optional_warnings_and_lists_deep_dive(
    make_case, evaluate_row, capsys, tmp_path
):
    row, header_map, _, _, _ = make_case()
    header_map = dict(header_map)
    header_map.pop("Full Ticker")

    def excel_writer(*_args, **_kwargs):
        return (
            Counter(
                {
                    "Deep Dive": 1,
                    "Watchlist": 0,
                    "Neutral": 0,
                    "Descartada": 0,
                }
            ),
            0,
            0,
            1,
            0,
            1,
        )

    cli.run(
        read_export=lambda _path, _language: ([row], header_map, []),
        verify_scale=lambda _rows, _header_map: ["Return on Equity"],
        make_accessors=make_accessors,
        evaluate_row=evaluate_row,
        excel_writer=excel_writer,
        dashboard_writer=lambda *_args, **_kwargs: None,
        argv=["fixture.xlsx", "--outdir", str(tmp_path)],
    )

    stdout = capsys.readouterr().out
    assert 'falta la columna "Full Ticker"' in stdout
    assert "no parecen venir en decimales" in stdout
    assert "TEST" in stdout
    assert "Omitidas por método" not in stdout


def test_file_is_executable_as_a_script(
    project_root, complete_market_view_path, monkeypatch, capsys, tmp_path
):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "screening_acciones.py",
            str(complete_market_view_path),
            "--outdir",
            str(tmp_path),
        ],
    )

    runpy.run_path(
        str(project_root / "scripts" / "screening_acciones.py"),
        run_name="__main__",
    )

    assert "Archivos generados" in capsys.readouterr().out


def test_early_warning_follows_the_requested_language(monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_sector_exclusions", lambda _path, language: {})
    monkeypatch.setattr(
        cli,
        "sector_list_age_warning",
        lambda _path, language: f"[{language}] stale sector list",
    )
    monkeypatch.setattr(cli, "run", lambda **_kwargs: None)

    cli.main(["export.xlsx", "--lang", "en"])

    assert "[en] stale sector list" in capsys.readouterr().out
