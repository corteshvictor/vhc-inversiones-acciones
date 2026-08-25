"""Command-line interface orchestration."""

import argparse
from datetime import UTC, datetime
from functools import partial
from pathlib import Path

from . import i18n
from .constants import (
    BUCKET_DEEP_DIVE,
    BUCKET_DISCARDED,
    BUCKET_NEUTRAL,
    BUCKET_WATCHLIST,
    CORE_COLUMNS,
    DEFAULT_SECTORS_FILE,
    FULL_TICKER,
    OPTIONAL_COLUMNS,
    ROIC_5Y,
    ROIC_CAGR_5Y,
    SCREENING_VERSION,
)
from .dashboard import generate_dashboard
from .engine import evaluate
from .excel_report import generate_excel
from .io import (
    load_sector_exclusions,
    make_accessors,
    read_export,
    sector_list_age_warning,
    verify_percentage_scale,
)


def _bilingual(key: str) -> str:
    """Help text carries both languages: the CLI has no language yet."""
    return f"{i18n.text(key, i18n.SPANISH)} / {i18n.text(key, i18n.ENGLISH)}"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=_bilingual("cli_description"))
    parser.add_argument("export", help=_bilingual("cli_export_help"))
    parser.add_argument(
        "--outdir",
        default="outputs",
        help=_bilingual("cli_outdir_help"),
    )
    parser.add_argument(
        "--lang",
        choices=i18n.LANGUAGES,
        default=i18n.SPANISH,
        help=_bilingual("cli_lang_help"),
    )
    return parser


def _sort_key(evaluation: dict):
    if evaluation["fund"]:
        return 9, 0, ""
    bucket_order = {
        BUCKET_DEEP_DIVE: 0,
        BUCKET_WATCHLIST: 1,
        BUCKET_NEUTRAL: 2,
        BUCKET_DISCARDED: 3,
    }
    return (
        bucket_order[evaluation["bucket"]],
        -evaluation["score"],
        evaluation["ticker"],
    )


def _output_paths(output_dir: Path, started_at: datetime) -> tuple[str, Path, Path]:
    run_date = started_at.strftime("%Y-%m-%dT%H:%M:%S")
    stamp = started_at.strftime("%Y-%m-%d_%H%M%S")
    sequence = 1
    while True:
        suffix = "" if sequence == 1 else f"_{sequence}"
        excel_path = output_dir / f"Screening_VHC_{stamp}{suffix}.xlsx"
        dashboard_path = output_dir / f"Dashboard_VHC_{stamp}{suffix}.html"
        if not excel_path.exists() and not dashboard_path.exists():
            return run_date, excel_path, dashboard_path
        sequence += 1


def _require_core_columns(
    missing_core: list[str], header_map: dict[str, int], language: str
) -> None:
    """Stops a run that cannot apply the complete method."""
    if not missing_core:
        return

    details = "\n".join(f"  - {column}" for column in missing_core)
    message = i18n.text(
        "missing_core",
        language,
        missing=len(missing_core),
        total=len(CORE_COLUMNS),
        details=details,
    )
    if ROIC_5Y in missing_core and ROIC_CAGR_5Y in header_map:
        message += i18n.text("roic_note", language, cagr=ROIC_CAGR_5Y, avg=ROIC_5Y)
    raise SystemExit(message)


def _print_warnings(header_map, suspicious, language) -> None:
    if FULL_TICKER not in header_map:
        print(i18n.text("warn_full_ticker", language))
    if suspicious:
        print(i18n.text("warn_scale", language, columns=", ".join(suspicious)))


def _print_deep_dive(evaluations, order, language) -> None:
    candidates = [
        evaluations[key]
        for key in order
        if not evaluations[key]["fund"]
        and evaluations[key]["bucket"] == BUCKET_DEEP_DIVE
    ]
    print(i18n.text("deep_dive_header", language))
    health_label = i18n.text("deep_dive_row_health", language)
    for position, evaluation in enumerate(candidates, 1):
        alerts = evaluation["alerts"]
        note = f" · {i18n.alert(alerts, language)}" if alerts != "—" else ""
        print(
            f"{position:2d}. {evaluation['ticker']:6s} "
            f"{evaluation['name'][:30]:30s} {evaluation['score']}/10 · "
            f"{i18n.term(evaluation['price'], language)}{health_label}"
            f"{i18n.term(evaluation['health'], language)}{note}"
        )


def _print_summary(
    export_name,
    run_date,
    counts,
    funds,
    sectors,
    excellent,
    traps,
    analyzed,
    evaluations,
    order,
    excel_path,
    dashboard_path,
    language,
) -> None:
    print(i18n.text("summary_title", language))
    print(
        i18n.text(
            "summary_header",
            language,
            export=export_name,
            run_date=run_date,
            version=SCREENING_VERSION,
        )
    )
    print(
        i18n.text(
            "summary_funnel",
            language,
            analyzed=analyzed,
            excellent=excellent,
            deep=counts[BUCKET_DEEP_DIVE],
        )
    )
    sector_text = (
        i18n.text("summary_sectors", language, sectors=sectors) if sectors else ""
    )
    print(
        i18n.text(
            "summary_categories",
            language,
            deep=counts[BUCKET_DEEP_DIVE],
            watch=counts[BUCKET_WATCHLIST],
            neutral=counts[BUCKET_NEUTRAL],
            discarded=counts[BUCKET_DISCARDED],
            traps=traps,
            funds=funds,
            sectors=sector_text,
        )
    )
    _print_deep_dive(evaluations, order, language)
    print(
        i18n.text("summary_files", language, excel=excel_path, dashboard=dashboard_path)
    )
    print(i18n.text("summary_reminder", language))


def run(
    read_export,
    verify_scale,
    make_accessors,
    evaluate_row,
    excel_writer,
    dashboard_writer,
    argv=None,
) -> None:
    """Runs the full flow with injectable dependencies for testing."""
    args = _parser().parse_args(argv)
    export_name = Path(args.export).name
    output_dir = Path(args.outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(UTC).astimezone()
    run_date, excel_path, dashboard_path = _output_paths(output_dir, started_at)

    rows, header_map, missing_core = read_export(args.export, args.lang)
    _require_core_columns(missing_core, header_map, args.lang)
    suspicious = verify_scale(rows, header_map)
    missing_columns = [
        column for column in CORE_COLUMNS + OPTIONAL_COLUMNS if column not in header_map
    ]
    raw, number, percentage = make_accessors(header_map)
    evaluations = {
        key: evaluate_row(row, raw, number, percentage) for key, row in enumerate(rows)
    }
    order = sorted(evaluations, key=lambda key: _sort_key(evaluations[key]))

    summary = excel_writer(
        rows,
        header_map,
        evaluations,
        order,
        excel_path,
        export_name,
        run_date,
        language=args.lang,
    )
    counts, funds, sectors, excellent, traps, analyzed = summary
    dashboard_writer(
        evaluations,
        order,
        dashboard_path,
        export_name,
        run_date,
        counts,
        funds,
        excellent,
        traps,
        analyzed,
        missing=missing_columns,
        language=args.lang,
    )

    _print_warnings(header_map, suspicious, args.lang)
    _print_summary(
        export_name,
        run_date,
        counts,
        funds,
        sectors,
        excellent,
        traps,
        analyzed,
        evaluations,
        order,
        excel_path,
        dashboard_path,
        args.lang,
    )


def _requested_language(argv) -> str:
    """Reads --lang before the run starts, so early warnings honour it too."""
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument("--lang", choices=i18n.LANGUAGES, default=i18n.SPANISH)
    return probe.parse_known_args(argv)[0].lang


def main(argv=None) -> None:
    """Runs the screening with the package's official dependencies."""
    language = _requested_language(argv)
    sector_exclusions = load_sector_exclusions(DEFAULT_SECTORS_FILE, language=language)
    age_warning = sector_list_age_warning(DEFAULT_SECTORS_FILE, language=language)
    if age_warning:
        print(age_warning)
    evaluator = partial(evaluate, sector_exclusions=sector_exclusions)
    run(
        read_export=read_export,
        verify_scale=verify_percentage_scale,
        make_accessors=make_accessors,
        evaluate_row=evaluator,
        excel_writer=generate_excel,
        dashboard_writer=generate_dashboard,
        argv=argv,
    )
