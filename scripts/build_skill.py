#!/usr/bin/env python3
"""Builds the skill distributions deterministically."""

import argparse
from pathlib import Path
from stat import S_IMODE
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "vhc-inversiones-acciones"
DEFAULT_OUTPUT = PROJECT_ROOT / f"{PACKAGE_NAME}.zip"
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
PACKAGE_FILES = (
    Path("SKILL.md"),
    Path("requirements.txt"),
    Path("requirements.lock"),
    Path("agents/openai.yaml"),
    Path("assets/vhc-banner.webp"),
    Path("assets/vhc-marca-excel.png"),
    Path("assets/vhc-marca.webp"),
    Path("references/DEEP_DIVE_PDF.md"),
    Path("references/REFERENCE.md"),
    Path("references/sectores_excluidos.csv"),
    Path("scripts/screening_acciones.py"),
    Path("scripts/vhc_screening/__init__.py"),
    Path("scripts/vhc_screening/cli.py"),
    Path("scripts/vhc_screening/constants.py"),
    Path("scripts/vhc_screening/dashboard.py"),
    Path("scripts/vhc_screening/engine.py"),
    Path("scripts/vhc_screening/excel_report.py"),
    Path("scripts/vhc_screening/i18n.py"),
    Path("scripts/vhc_screening/io.py"),
)
PLUGIN_RELATIVE_ROOT = Path("plugins") / PACKAGE_NAME
PLUGIN_SKILL_RELATIVE_ROOT = PLUGIN_RELATIVE_ROOT / "skills" / PACKAGE_NAME
PLUGIN_MANIFEST = PLUGIN_RELATIVE_ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = Path(".agents/plugins/marketplace.json")


def _validate_required_files(root_path: Path, paths: tuple[Path, ...]) -> None:
    missing = [path for path in paths if not (root_path / path).is_file()]
    if missing:
        joined = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Faltan archivos obligatorios del skill: {joined}")


def build_skill(output: str | Path, root: str | Path = PROJECT_ROOT) -> Path:
    """Packages only the public files required to run the skill."""
    root_path = Path(root)
    _validate_required_files(root_path, PACKAGE_FILES)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(
        output_path,
        "w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative_path in PACKAGE_FILES:
            archive_name = f"{PACKAGE_NAME}/{relative_path.as_posix()}"
            info = ZipInfo(archive_name, FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                (root_path / relative_path).read_bytes(),
                compresslevel=9,
            )
    return output_path


def _copy_distribution_file(source: Path, target: Path) -> None:
    """Copies a distribution file, creating its parent directories."""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    target.chmod(S_IMODE(source.stat().st_mode))


def build_plugin(
    output_root: str | Path,
    root: str | Path = PROJECT_ROOT,
) -> Path:
    """Builds the plugin and its marketplace from the canonical sources."""
    root_path = Path(root)
    required = PACKAGE_FILES + (PLUGIN_MANIFEST, MARKETPLACE_MANIFEST)
    _validate_required_files(root_path, required)

    output_root_path = Path(output_root)
    plugin_root = output_root_path / PLUGIN_RELATIVE_ROOT
    skill_root = output_root_path / PLUGIN_SKILL_RELATIVE_ROOT

    for relative_path in PACKAGE_FILES:
        _copy_distribution_file(root_path / relative_path, skill_root / relative_path)
    _copy_distribution_file(
        root_path / PLUGIN_MANIFEST, output_root_path / PLUGIN_MANIFEST
    )
    _copy_distribution_file(
        root_path / MARKETPLACE_MANIFEST, output_root_path / MARKETPLACE_MANIFEST
    )
    return plugin_root


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Construye el ZIP instalable de VHC Inversiones."
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Ruta del ZIP resultante",
    )
    parser.add_argument(
        "--plugin-output",
        help="Raíz donde se construyen plugins/ y .agents/",
    )
    return parser


def main(argv=None) -> Path:
    """Generates the portable ZIP and the plugin distribution."""
    args = _parser().parse_args(argv)
    output_path = build_skill(args.output)
    plugin_output = args.plugin_output or output_path.parent
    plugin_path = build_plugin(plugin_output)
    print(f"Paquete generado: {output_path}")
    print(f"Plugin generado: {plugin_path}")
    return output_path


if __name__ == "__main__":
    main()
