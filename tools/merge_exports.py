#!/usr/bin/env python3
"""Combines several InvestingPro exports into one sheet, verifying continuity.

InvestingPro hands out at most 1,000 rows per export, so a wider universe is
assembled by lowering the market capitalization filter and downloading again.
When that filter is rounded up, the last company of one export reappears as the
first of the next. That duplicate is not a defect: it is the proof that nothing
was skipped between them. A boundary that arrives without one means companies
were lost, and nothing else in the file records their absence.

This tool treats those duplicates as a positive control: it orders the exports
by capitalization, checks every boundary for its overlap, reports the range that
went missing when one is absent, and only then merges and drops the repeats.

Usage:
    python tools/merge_exports.py "~/Downloads/Untitled Screener*.xlsx"
    python tools/merge_exports.py ~/Downloads/Untitled*.xlsx
"""

from __future__ import annotations

import argparse
import glob
import itertools
import math
import os
import sys
from dataclasses import dataclass

import openpyxl
from openpyxl import Workbook

TICKER = "Ticker"
NAME = "Name"
MARKET_CAP = "Market Cap (Adjusted)"
MILLION = 1_000_000


def _text(value: object) -> str:
    """Collapses the whitespace and line breaks a cell may carry."""
    return " ".join(str(value).split()) if value is not None else ""


def _number(value: object) -> float | None:
    """Returns the value as a float only when it is genuinely numeric."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


@dataclass
class Batch:
    """One downloaded export, read and indexed by column name."""

    path: str
    header: list[str]
    rows: list[list[object]]
    tickers: list[str]
    caps: list[float]

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def top(self) -> float:
        return max(self.caps, default=0.0)

    @property
    def bottom(self) -> float:
        return min(self.caps, default=0.0)


@dataclass(frozen=True)
class Gap:
    """A boundary that arrived with no overlap, and the range it lost."""

    after: str
    before: str
    lost_from: float
    lost_to: float

    @property
    def resume_at(self) -> float:
        """The filter that recovers the range, in millions, rounded up.

        Rounding up is what guarantees the overlap; rounding down is what opens
        the gap, because the boundary company then falls outside both exports.
        """
        return math.ceil(self.lost_to / MILLION * 100) / 100


def _read_sheet(path: str) -> list[list[object]]:
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = book.active
    if sheet is None:
        raise SystemExit(f"ERROR: {os.path.basename(path)} no trae ninguna hoja")
    rows: list[list[object]] = [list(row) for row in sheet.iter_rows(values_only=True)]
    book.close()
    return rows


def _find_header(rows: list[list[object]], path: str) -> int:
    """Locates the header row wherever it sits, by its labels."""
    for index, row in enumerate(rows):
        labels = {_text(cell) for cell in row}
        if NAME in labels and TICKER in labels:
            return index
    raise SystemExit(f"ERROR: {os.path.basename(path)} no trae fila de encabezados")


def _cell(row: list[object], index: int | None) -> object:
    if index is None or index >= len(row):
        return None
    return row[index]


def read_batch(path: str) -> Batch:
    """Reads one export and pulls out its tickers and capitalizations."""
    rows = _read_sheet(path)
    header_at = _find_header(rows, path)
    columns = {_text(v): j for j, v in enumerate(rows[header_at]) if _text(v)}
    name_at, ticker_at = columns[NAME], columns[TICKER]
    cap_at = columns.get(MARKET_CAP)

    data: list[list[object]] = []
    tickers: list[str] = []
    caps: list[float] = []
    for row in rows[header_at + 1 :]:
        if not row or not _text(_cell(row, name_at)):
            continue
        data.append(list(row))
        tickers.append(_text(_cell(row, ticker_at)))
        capitalization = _number(_cell(row, cap_at))
        if capitalization is not None:
            caps.append(capitalization)

    header = [_text(cell) for cell in rows[header_at]]
    return Batch(path=path, header=header, rows=data, tickers=tickers, caps=caps)


def find_gaps(batches: list[Batch]) -> list[Gap]:
    """Every boundary must repeat a company. Its absence is a gap."""
    gaps: list[Gap] = []
    for current, following in itertools.pairwise(batches):
        if set(current.tickers) & set(following.tickers):
            continue
        gaps.append(
            Gap(
                after=current.name,
                before=following.name,
                lost_from=following.top,
                lost_to=current.bottom,
            )
        )
    return gaps


def merge(batches: list[Batch]) -> tuple[list[str], list[list[object]], list[str]]:
    """Merges the rows, keeping the first appearance of every ticker."""
    seen: set[str] = set()
    merged: list[list[object]] = []
    repeated: list[str] = []
    for batch in batches:
        for ticker, row in zip(batch.tickers, batch.rows):
            if ticker and ticker in seen:
                repeated.append(ticker)
                continue
            if ticker:
                seen.add(ticker)
            merged.append(row)
    return batches[0].header, merged, repeated


def write_sheet(header: list[str], rows: list[list[object]], output: str) -> None:
    """Writes the merged universe under a single header row."""
    book = Workbook()
    sheet = book.active
    if sheet is None:  # pragma: no cover - a fresh workbook always has a sheet
        raise SystemExit("ERROR: no se pudo crear la hoja de salida")
    sheet.title = "Universo"
    sheet.append(header)
    for row in rows:
        sheet.append(row)
    book.save(output)


def _print_batches(batches: list[Batch]) -> None:
    print("== TANDAS, ordenadas por capitalización ==")
    for batch in batches:
        first = batch.tickers[0] if batch.tickers else ""
        last = batch.tickers[-1] if batch.tickers else ""
        print(
            f"  {len(batch.rows):>5,} filas · "
            f"{batch.top / MILLION:>14,.2f} M -> {batch.bottom / MILLION:>12,.2f} M · "
            f"{first:>6} .. {last:<6} · {batch.name}"
        )


def _print_continuity(batches: list[Batch], gaps: list[Gap]) -> None:
    # A single export has no boundary to check, so there is nothing to claim
    # about it either way.
    if len(batches) < 2:
        return
    print("\n== CONTINUIDAD ENTRE TANDAS ==")
    lost = {gap.after for gap in gaps}
    for current, following in itertools.pairwise(batches):
        if current.name in lost:
            print(
                f"  HUECO entre {following.top / MILLION:,.2f} M y "
                f"{current.bottom / MILLION:,.2f} M  <-- faltan empresas"
            )
            continue
        shared = sorted(set(current.tickers) & set(following.tickers))
        print(
            f"  OK   {current.bottom / MILLION:>12,.2f} M  ->  "
            f"solape: {', '.join(shared[:3])}"
        )


def _print_next_step(batches: list[Batch], rows_per_export: int = 1000) -> None:
    """Says what to type next, so the smallest batch need not be read by eye."""
    smallest = batches[-1]
    if len(smallest.rows) < rows_per_export:
        print(
            f"\nÚltima tanda con {len(smallest.rows):,} filas "
            f"(menos de {rows_per_export:,}): el universo está completo."
        )
        return
    following = math.ceil(smallest.bottom / MILLION * 100) / 100
    print(
        f"\n== SIGUIENTE TANDA ==\n"
        f"  La última descargada acaba en {smallest.tickers[-1]}, "
        f"{smallest.bottom / MILLION:,.2f} M. Para la siguiente:\n"
        f"      Market Cap (Adjusted) · less than or equal to · "
        f"{following} · million\n"
        f"  Si {following} ya está por debajo del tamaño que te interesa, "
        f"has terminado: deja de descargar."
    )


def _print_summary(
    batches: list[Batch], merged: list[list[object]], repeated: list[str], output: str
) -> None:
    unique = list(dict.fromkeys(repeated))
    print("\n== FUSIÓN ==")
    print(f"  filas leídas    : {sum(len(b.rows) for b in batches):,}")
    print(f"  duplicados      : {len(repeated)}  {unique[:12] if unique else ''}")
    print(f"  empresas únicas : {len(merged):,}")
    print(f"  archivo         : {output}")


def _print_gaps(gaps: list[Gap], boundaries: int) -> None:
    if boundaries == 0:
        return
    if not gaps:
        print("\nSin huecos: cada frontera trae su solape.")
        return
    print("\n== HUECOS QUE HAY QUE CERRAR ==")
    for gap in gaps:
        print(
            f"  - {gap.after} -> {gap.before}: sin solape. "
            f"Se perdió todo entre {gap.lost_from / MILLION:,.2f} M "
            f"y {gap.lost_to / MILLION:,.2f} M. Vuelve a descargar con:"
        )
        # The web filter lets the user pick the unit; the API only speaks
        # millions. Both are printed so neither workflow has to convert.
        print(
            f"      en la web  ->  Market Cap (Adjusted) · menor o igual que · "
            f"{gap.resume_at} · million"
        )
        print(f'      en el curl ->  "marketcap_adj": {{"$lte": {gap.resume_at}}}')


def resolve_paths(patterns: list[str]) -> list[str]:
    """Resolves the arguments, whether the shell expanded the wildcard or not.

    Quoting the pattern hands this one string with a `*` in it; leaving it
    unquoted hands one argument per file. Both are accepted so the command
    works either way, and duplicates are dropped in case the two forms overlap.
    """
    found: list[str] = []
    for pattern in patterns:
        expanded = os.path.expanduser(pattern)
        found.extend(glob.glob(expanded) if glob.has_magic(expanded) else [expanded])
    unique = dict.fromkeys(p for p in found if not os.path.basename(p).startswith("~$"))
    return sorted(unique)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "patterns",
        nargs="+",
        metavar="EXPORT",
        help="Rutas o comodín de los exports a fusionar",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Archivo de salida. Por omisión, universe.xlsx junto a los exports",
    )
    args = parser.parse_args(argv)

    paths = resolve_paths(args.patterns)
    if not paths:
        raise SystemExit(
            f"ERROR: ningún archivo coincide con {' '.join(args.patterns)}"
        )

    # Largest capitalization first: the real download order, not the file names.
    batches = sorted((read_batch(p) for p in paths), key=lambda b: b.top, reverse=True)

    _print_batches(batches)
    gaps = find_gaps(batches)
    _print_continuity(batches, gaps)

    header, merged, repeated = merge(batches)
    # Written next to the exports it merged, not into whatever directory the
    # command happened to run from: the result belongs with its sources.
    output = (
        os.path.expanduser(args.output)
        if args.output
        else os.path.join(os.path.dirname(paths[0]), "universe.xlsx")
    )
    write_sheet(header, merged, output)

    _print_summary(batches, merged, repeated, output)
    _print_gaps(gaps, len(batches) - 1)
    _print_next_step(batches)
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
