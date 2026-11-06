"""Plugin distribution contract for ChatGPT, Codex and Claude."""

import json
from pathlib import Path
from stat import S_IMODE

import pytest

from scripts import build_skill


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_plugin_manifest_declares_the_skill_and_the_brand(project_root):
    manifest_path = project_root / build_skill.PLUGIN_MANIFEST
    manifest = _read_json(manifest_path)
    interface = manifest["interface"]

    assert manifest["name"] == build_skill.PACKAGE_NAME
    # release-please bumps both files. Comparing them, rather than a literal,
    # is what keeps the release pull request from turning CI red.
    released = _read_json(project_root / ".release-please-manifest.json")
    assert manifest["version"] == released["."]
    assert manifest["skills"] == "./skills/"
    assert manifest["author"]["name"] == "VHC Inversiones"
    assert "apps" not in manifest
    assert "mcpServers" not in manifest
    assert interface["displayName"] == "VHC Inversiones — Acciones"
    assert interface["brandColor"] == "#0A1B2D"
    assert 1 <= len(interface["defaultPrompt"]) <= 3


def test_marketplace_points_to_the_repository_plugin(project_root):
    marketplace = _read_json(project_root / build_skill.MARKETPLACE_MANIFEST)

    assert marketplace["name"] == "vhc-inversiones"
    assert marketplace["interface"]["displayName"] == "VHC Inversiones"
    assert marketplace["plugins"] == [
        {
            "name": build_skill.PACKAGE_NAME,
            "source": {
                "source": "local",
                "path": f"./plugins/{build_skill.PACKAGE_NAME}",
            },
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
            "category": "Productivity",
        }
    ]


def test_claude_manifest_declares_the_plugin_and_the_released_version(project_root):
    """The version pins what an installer gets, so one left behind would keep
    every Claude user on an old release with no error anywhere."""
    manifest = _read_json(project_root / build_skill.CLAUDE_PLUGIN_MANIFEST)
    released = _read_json(project_root / ".release-please-manifest.json")
    codex = _read_json(project_root / build_skill.PLUGIN_MANIFEST)

    assert manifest["name"] == build_skill.PACKAGE_NAME
    assert manifest["displayName"] == codex["interface"]["displayName"]
    assert manifest["version"] == released["."]
    assert manifest["description"] == codex["description"]
    assert manifest["license"] == codex["license"]
    assert "mcpServers" not in manifest
    assert "hooks" not in manifest


def test_claude_marketplace_points_to_the_repository_plugin(project_root):
    """Claude reads its own catalog, in its own format: the source is a plain
    relative path and the owner is required."""
    marketplace = _read_json(project_root / build_skill.CLAUDE_MARKETPLACE_MANIFEST)
    entry = marketplace["plugins"][0]

    assert marketplace["name"] == "vhc-inversiones"
    assert marketplace["owner"]["name"] == "VHC Inversiones"
    assert [plugin["name"] for plugin in marketplace["plugins"]] == [
        build_skill.PACKAGE_NAME
    ]
    assert entry["source"] == f"./{build_skill.PLUGIN_RELATIVE_ROOT.as_posix()}"
    assert (project_root / entry["source"] / "skills").is_dir()


def test_plugin_skill_matches_the_canonical_sources(project_root):
    skill_root = project_root / build_skill.PLUGIN_SKILL_RELATIVE_ROOT
    actual_files = {
        path.relative_to(skill_root) for path in skill_root.rglob("*") if path.is_file()
    }

    assert actual_files == set(build_skill.PACKAGE_FILES)
    for relative_path in build_skill.PACKAGE_FILES:
        assert (skill_root / relative_path).read_bytes() == (
            project_root / relative_path
        ).read_bytes()
        assert S_IMODE((skill_root / relative_path).stat().st_mode) == S_IMODE(
            (project_root / relative_path).stat().st_mode
        )


def test_builder_reproduces_a_complete_marketplace(project_root, tmp_path):
    plugin_root = build_skill.build_plugin(tmp_path, project_root)
    skill_root = tmp_path / build_skill.PLUGIN_SKILL_RELATIVE_ROOT

    assert plugin_root == tmp_path / build_skill.PLUGIN_RELATIVE_ROOT
    for relative_path in build_skill.DISTRIBUTION_MANIFESTS:
        assert (tmp_path / relative_path).read_bytes() == (
            project_root / relative_path
        ).read_bytes()
    for relative_path in build_skill.PACKAGE_FILES:
        assert (skill_root / relative_path).read_bytes() == (
            project_root / relative_path
        ).read_bytes()
        assert S_IMODE((skill_root / relative_path).stat().st_mode) == S_IMODE(
            (project_root / relative_path).stat().st_mode
        )


def test_plugin_builder_fails_when_sources_are_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="Faltan archivos obligatorios"):
        build_skill.build_plugin(tmp_path / "salida", tmp_path / "raiz-vacia")
