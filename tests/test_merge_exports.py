"""Tests for the tool that joins several exports into one universe.

The behaviour worth guarding is not the merging — any script concatenates rows —
but the continuity check. An export series assembled by lowering the market
capitalization filter loses companies silently when the filter is rounded down,
and no later reader of the file can tell. These tests pin the rule that catches
it: every boundary must repeat a company, and the resume value always rounds up.
"""

import os
import runpy
import sys
from unittest import mock

import openpyxl
import pytest
from merge_exports import (
    MARKET_CAP,
    NAME,
    TICKER,
    Batch,
    Gap,
    _number,
    _text,
    find_gaps,
    main,
    merge,
    read_batch,
    resolve_paths,
    write_sheet,
)

HEADER = [NAME, TICKER, MARKET_CAP]


def _export(path, rows, *, header=None, preamble=0):
    """Writes a sheet shaped like an InvestingPro export."""
    book = openpyxl.Workbook()
    sheet = book.active
    assert sheet is not None
    for _ in range(preamble):
        sheet.append(["Untitled Screener"])
    sheet.append(header if header is not None else HEADER)
    for row in rows:
        sheet.append(list(row))
    book.save(path)
    return path


def _slice(tmp_path, name, tickers, caps, **kwargs):
    rows = [(f"{t} Inc", t, c) for t, c in zip(tickers, caps, strict=True)]
    return _export(tmp_path / name, rows, **kwargs)


def test_text_collapses_whitespace_and_survives_empty_cells():
    assert _text("  Deckers   Outdoor \n Corp ") == "Deckers Outdoor Corp"
    assert _text(None) == ""


def test_number_accepts_only_real_numbers():
    assert _number(292_394_410) == 292_394_410.0
    assert _number(1.5) == 1.5
    assert _number("292394410") is None
    assert _number(None) is None
    # A bool is an int in Python, and a market cap of True would sort as 1.0.
    assert _number(True) is None


def test_read_batch_finds_the_header_below_a_preamble(tmp_path):
    path = _slice(tmp_path, "a.xlsx", ["NVDA", "AAPL"], [5e12, 4e12], preamble=7)
    batch = read_batch(str(path))

    assert batch.tickers == ["NVDA", "AAPL"]
    assert batch.top == 5e12
    assert batch.bottom == 4e12
    assert batch.name == "a.xlsx"


def test_read_batch_skips_rows_with_no_company_name(tmp_path):
    path = _export(tmp_path / "a.xlsx", [("NVDA Inc", "NVDA", 5e12), (None, "", None)])
    assert len(read_batch(str(path)).rows) == 1


def test_read_batch_tolerates_a_missing_capitalization_column(tmp_path):
    path = _export(tmp_path / "a.xlsx", [("NVDA Inc", "NVDA")], header=[NAME, TICKER])
    batch = read_batch(str(path))

    assert batch.tickers == ["NVDA"]
    assert batch.caps == []
    assert batch.top == 0.0
    assert batch.bottom == 0.0


def test_read_batch_refuses_a_file_with_no_header_row(tmp_path):
    path = _export(tmp_path / "a.xlsx", [], header=["Something", "Else"])
    with pytest.raises(SystemExit, match="fila de encabezados"):
        read_batch(str(path))


def test_read_batch_refuses_a_workbook_with_no_sheet(tmp_path, monkeypatch):
    path = _slice(tmp_path, "a.xlsx", ["NVDA"], [5e12])

    class Sheetless:
        active = None

        def close(self):
            return None

    monkeypatch.setattr(openpyxl, "load_workbook", lambda *a, **k: Sheetless())
    with pytest.raises(SystemExit, match="ninguna hoja"):
        read_batch(str(path))


def test_a_boundary_that_repeats_a_company_reports_no_gap(tmp_path):
    first = read_batch(str(_slice(tmp_path, "a.xlsx", ["NVDA", "PTCT"], [5e12, 5.9e9])))
    second = read_batch(
        str(_slice(tmp_path, "b.xlsx", ["PTCT", "UVE"], [5.9e9, 1.2e9]))
    )

    assert find_gaps([first, second]) == []


def test_a_boundary_with_no_overlap_names_the_range_that_was_lost(tmp_path):
    first = read_batch(
        str(_slice(tmp_path, "a.xlsx", ["NVDA", "UVE"], [5e12, 1_213_403_478]))
    )
    second = read_batch(
        str(_slice(tmp_path, "b.xlsx", ["ODTX", "RCMT"], [1_205_149_243, 2.9e8]))
    )

    gaps = find_gaps([first, second])

    assert len(gaps) == 1
    assert gaps[0].after == "a.xlsx"
    assert gaps[0].before == "b.xlsx"
    assert gaps[0].lost_from == 1_205_149_243
    assert gaps[0].lost_to == 1_213_403_478


def test_the_resume_value_always_rounds_up():
    """Rounding down is what opens the gap: the boundary company then falls
    outside both exports, and nothing in the file records its absence."""
    gap = Gap(after="a", before="b", lost_from=1_205_149_243, lost_to=1_213_403_478)

    assert gap.resume_at == 1213.41  # 1,213.403478 M, never 1213.40
    assert gap.resume_at * 1e6 > gap.lost_to

    exact = Gap(after="a", before="b", lost_from=0.0, lost_to=100_000_000)
    assert exact.resume_at == 100.0


def test_merge_keeps_the_first_appearance_of_every_ticker(tmp_path):
    first = read_batch(str(_slice(tmp_path, "a.xlsx", ["NVDA", "PTCT"], [5e12, 5.9e9])))
    second = read_batch(
        str(_slice(tmp_path, "b.xlsx", ["PTCT", "UVE"], [5.9e9, 1.2e9]))
    )

    header, rows, repeated = merge([first, second])

    assert header == HEADER
    assert [row[1] for row in rows] == ["NVDA", "PTCT", "UVE"]
    assert repeated == ["PTCT"]


def test_merge_keeps_rows_that_carry_no_ticker(tmp_path):
    path = _export(tmp_path / "a.xlsx", [("Sin ticker", None, 1e9)])
    _, rows, repeated = merge([read_batch(str(path))])

    assert len(rows) == 1
    assert repeated == []


def test_write_sheet_puts_one_header_above_the_rows(tmp_path):
    output = tmp_path / "universe.xlsx"
    write_sheet(HEADER, [["NVDA Inc", "NVDA", 5e12]], str(output))

    book = openpyxl.load_workbook(output)
    sheet = book.active
    assert sheet is not None
    assert [cell.value for cell in sheet[1]] == HEADER
    assert sheet.max_row == 2
    book.close()


def test_resolve_paths_expands_a_pattern_and_drops_excel_lock_files(tmp_path):
    _slice(tmp_path, "one.xlsx", ["A"], [1e9])
    _slice(tmp_path, "two.xlsx", ["B"], [2e9])
    (tmp_path / "~$one.xlsx").write_bytes(b"lock")

    found = resolve_paths([str(tmp_path / "*.xlsx")])

    # os.path.basename, not a split on "/": Windows separates with a backslash.
    assert [os.path.basename(p) for p in found] == ["one.xlsx", "two.xlsx"]


def test_resolve_paths_takes_the_list_a_shell_already_expanded(tmp_path):
    """Quoting the pattern hands one string; leaving it unquoted hands one
    argument per file. Both forms have to work, and overlap must not duplicate."""
    first = str(_slice(tmp_path, "one.xlsx", ["A"], [1e9]))
    second = str(_slice(tmp_path, "two.xlsx", ["B"], [2e9]))

    assert resolve_paths([first, second]) == sorted([first, second])
    assert resolve_paths([first, str(tmp_path / "*.xlsx")]) == sorted([first, second])


def test_main_merges_orders_by_capitalization_and_reports_no_gaps(tmp_path, capsys):
    # Named so the alphabetical order contradicts the real one: only the data
    # settles the sequence.
    _slice(tmp_path, "z-first.xlsx", ["NVDA", "PTCT"], [5e12, 5.9e9])
    _slice(tmp_path, "a-second.xlsx", ["PTCT", "UVE"], [5.9e9, 1.2e9])
    output = tmp_path / "universe.xlsx"

    code = main([str(tmp_path / "*.xlsx"), "-o", str(output)])
    printed = capsys.readouterr().out

    assert code == 0
    assert "Sin huecos" in printed
    assert printed.index("z-first.xlsx") < printed.index("a-second.xlsx")
    assert "empresas únicas : 3" in printed
    assert output.exists()


def test_main_reports_a_gap_and_exits_non_zero(tmp_path, capsys):
    _slice(tmp_path, "a.xlsx", ["NVDA", "UVE"], [5e12, 1_213_403_478])
    _slice(tmp_path, "b.xlsx", ["ODTX", "RCMT"], [1_205_149_243, 2.9e8])

    code = main([str(tmp_path / "*.xlsx"), "-o", str(tmp_path / "u.xlsx")])
    printed = capsys.readouterr().out

    assert code == 1
    assert "HUECO" in printed
    assert "1213.41" in printed
    assert "million" in printed  # the four boxes of the web filter
    assert '"$lte": 1213.41' in printed  # the API form


def test_main_writes_beside_the_exports_when_no_output_is_given(tmp_path, capsys):
    """The result belongs with its sources, not in whatever directory the
    command happened to run from."""
    _slice(tmp_path, "a.xlsx", ["NVDA"], [5e12])

    main([str(tmp_path / "*.xlsx")])
    capsys.readouterr()

    assert (tmp_path / "universe.xlsx").exists()


def test_main_says_nothing_about_continuity_for_a_single_export(tmp_path, capsys):
    """One export has no boundary, so there is nothing to claim either way."""
    _slice(tmp_path, "a.xlsx", ["NVDA", "PTCT"], [5e12, 5.9e9])

    code = main([str(tmp_path / "*.xlsx"), "-o", str(tmp_path / "u.xlsx")])
    printed = capsys.readouterr().out

    assert code == 0
    assert "CONTINUIDAD" not in printed
    assert "Sin huecos" not in printed


def test_main_tells_the_user_what_to_type_for_the_next_export(tmp_path, capsys):
    caps = [5e12 - index for index in range(1000)]
    _slice(tmp_path, "a.xlsx", [f"T{i}" for i in range(1000)], caps)

    main([str(tmp_path / "*.xlsx"), "-o", str(tmp_path / "u.xlsx")])
    printed = capsys.readouterr().out

    assert "SIGUIENTE TANDA" in printed
    assert "less than or equal to" in printed


def test_main_stops_asking_once_an_export_comes_back_short(tmp_path, capsys):
    _slice(tmp_path, "a.xlsx", ["NVDA", "PTCT"], [5e12, 5.9e9])

    main([str(tmp_path / "*.xlsx"), "-o", str(tmp_path / "u.xlsx")])
    printed = capsys.readouterr().out

    assert "universo está completo" in printed
    assert "SIGUIENTE TANDA" not in printed


def test_main_refuses_a_pattern_that_matches_nothing(tmp_path):
    with pytest.raises(SystemExit, match="ningún archivo coincide"):
        main([str(tmp_path / "nada-*.xlsx")])


def test_batch_reports_no_ticker_for_a_row_shorter_than_the_header():
    batch = Batch(path="a.xlsx", header=HEADER, rows=[], tickers=[], caps=[])
    assert batch.top == 0.0
    assert batch.bottom == 0.0


def test_the_tool_runs_as_a_command(project_root, tmp_path, capsys):
    """The `if __name__` guard: executed directly the tool must exit with the
    code it returns, so a gap makes a shell script or a CI step fail."""
    _slice(tmp_path, "a.xlsx", ["NVDA", "PTCT"], [5e12, 5.9e9])
    argv = [
        "merge_exports.py",
        str(tmp_path / "*.xlsx"),
        "-o",
        str(tmp_path / "u.xlsx"),
    ]

    with (
        mock.patch.object(sys, "argv", argv),
        pytest.raises(SystemExit) as exit_info,
    ):
        runpy.run_path(
            str(project_root / "tools" / "merge_exports.py"), run_name="__main__"
        )

    capsys.readouterr()
    assert exit_info.value.code == 0
