"""Installable package tests and reproducible build."""

import hashlib
import re
import runpy
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts import build_skill


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_zip_is_reproducible_and_only_includes_the_allowlist(project_root, tmp_path):
    first = build_skill.build_skill(tmp_path / "first.zip", project_root)
    second = build_skill.build_skill(tmp_path / "second.zip", project_root)

    assert _sha256(first) == _sha256(second)
    with ZipFile(first) as archive:
        assert archive.namelist() == [
            f"vhc-inversiones-acciones/{path.as_posix()}"
            for path in build_skill.PACKAGE_FILES
        ]
        assert all("tests/" not in name for name in archive.namelist())
        assert all("__pycache__" not in name for name in archive.namelist())


def test_distributable_zip_matches_the_sources(project_root, tmp_path):
    generated = build_skill.build_skill(tmp_path / "candidate.zip", project_root)
    distributed = project_root / "vhc-inversiones-acciones.zip"

    assert distributed.is_file()
    assert _sha256(distributed) == _sha256(generated)


def test_zip_fails_when_a_required_file_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="Faltan archivos obligatorios"):
        build_skill.build_skill(tmp_path / "skill.zip", tmp_path / "raiz-vacia")


def test_main_allows_choosing_the_output(project_root, tmp_path, capsys):
    output = tmp_path / "skill.zip"

    result = build_skill.main(["--output", str(output)])

    assert result == output
    assert output.is_file()
    assert (tmp_path / build_skill.PLUGIN_MANIFEST).is_file()
    assert (tmp_path / build_skill.MARKETPLACE_MANIFEST).is_file()
    assert "Paquete generado" in capsys.readouterr().out


def test_main_allows_choosing_the_plugin_output(tmp_path, capsys):
    output = tmp_path / "zip" / "skill.zip"
    plugin_output = tmp_path / "marketplace"

    result = build_skill.main(
        [
            "--output",
            str(output),
            "--plugin-output",
            str(plugin_output),
        ]
    )

    assert result == output
    assert (plugin_output / build_skill.PLUGIN_MANIFEST).is_file()
    assert "Plugin generado" in capsys.readouterr().out


def test_builder_can_be_imported_without_running(project_root):
    namespace = runpy.run_path(
        str(project_root / "scripts" / "build_skill.py"),
        run_name="build_skill_importado",
    )

    assert callable(namespace["main"])


def test_builder_is_executable_as_a_script(project_root, monkeypatch, tmp_path, capsys):
    output = tmp_path / "ejecutable.zip"
    monkeypatch.setattr(
        sys,
        "argv",
        ["build_skill.py", "--output", str(output)],
    )

    runpy.run_path(
        str(project_root / "scripts" / "build_skill.py"),
        run_name="__main__",
    )

    assert output.is_file()
    assert (tmp_path / build_skill.PLUGIN_MANIFEST).is_file()
    assert "Paquete generado" in capsys.readouterr().out


def test_packaged_sources_are_free_of_carriage_returns(project_root):
    """The ZIP is built from these bytes, so a checkout that rewrites line
    endings would ship a different package. `.gitattributes` pins the working
    tree to LF; this proves the pin holds wherever the suite runs."""
    attributes = (project_root / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in attributes

    binary = {".png", ".webp", ".xlsx", ".zip"}
    for relative in build_skill.PACKAGE_FILES:
        if relative.suffix in binary:
            declared = rf"^\*{re.escape(relative.suffix)}\s+binary$"
            assert re.search(declared, attributes, re.MULTILINE), relative
            continue
        assert b"\r\n" not in (project_root / relative).read_bytes(), relative
