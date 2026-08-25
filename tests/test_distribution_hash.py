"""Identity of an installed skill tree, for the manual evaluation."""

import os
import shutil

import pytest
from build_skill import PACKAGE_FILES
from hash_distribution_tree import LISTED_EXTRAS, TREES, main, tree_digest


@pytest.fixture
def installed(project_root, tmp_path):
    """A clean copy of what an installation actually contains."""
    tree = tmp_path / "installed"
    source = (
        project_root
        / "plugins"
        / "vhc-inversiones-acciones"
        / "skills"
        / "vhc-inversiones-acciones"
    )
    shutil.copytree(source, tree)
    return tree


def test_the_digest_ignores_everything_except_content_and_path(installed, tmp_path):
    """Two machines must agree, so a timestamp or a permission bit cannot move
    the value — only the bytes and where they sit."""
    twin = tmp_path / "twin"
    shutil.copytree(installed, twin)
    (twin / "SKILL.md").touch()
    (twin / "SKILL.md").chmod(0o600)

    assert tree_digest(twin)[0] == tree_digest(installed)[0]


def test_one_changed_byte_changes_the_digest(installed):
    before = tree_digest(installed)[0]
    (installed / "SKILL.md").write_bytes((installed / "SKILL.md").read_bytes() + b" ")

    assert tree_digest(installed)[0] != before


def test_a_missing_file_stops_instead_of_hashing_a_partial_tree(installed):
    """A half-installed copy that still produced a value would look certified."""
    (installed / PACKAGE_FILES[0]).unlink()

    with pytest.raises(SystemExit, match="Missing:"):
        tree_digest(installed)


def test_unexpected_files_are_reported_without_moving_the_digest(installed):
    """A stale file left by an install that did not replace everything is worth
    seeing, but it does not make the skill a different skill."""
    before = tree_digest(installed)[0]
    (installed / "SKILL.md.orig").write_text("leftover", encoding="utf-8")

    digest, extra = tree_digest(installed)

    assert digest == before
    assert extra == ("SKILL.md.orig",)


def test_the_command_prints_the_digest_and_caps_the_extras(installed, capsys):
    for index in range(LISTED_EXTRAS + 3):
        (installed / f"leftover-{index:03d}.txt").write_text("x", encoding="utf-8")

    digest = main([str(installed)])
    streams = capsys.readouterr()

    assert streams.out == f"{digest}\n", "the digest is the only thing worth piping"
    assert streams.err.count("leftover-") == LISTED_EXTRAS
    assert "y 3 más" in streams.err


def test_a_short_list_of_extras_is_printed_whole(installed, capsys):
    """Below the cap there is nothing to elide, so no tail line is written."""
    (installed / "SKILL.md.orig").write_text("leftover", encoding="utf-8")

    main([str(installed)])
    streams = capsys.readouterr()

    assert "SKILL.md.orig" in streams.err
    assert "más" not in streams.err


def test_the_command_says_nothing_extra_when_the_tree_is_clean(installed, capsys):
    digest = main([str(installed)])

    assert capsys.readouterr().out == f"{digest}\n"


@pytest.fixture
def plugin(project_root, tmp_path):
    """The wrapper a marketplace installs: a manifest plus the skill folder."""
    tree = tmp_path / "plugin"
    shutil.copytree(project_root / "plugins" / "vhc-inversiones-acciones", tree)
    return tree


def test_a_plugin_tree_covers_its_manifest_too(plugin):
    """Two layouts exist and they are not the same package: the plugin adds a
    manifest that decides which version an installer believes it has."""
    digest, _ = tree_digest(plugin, "plugin")
    manifest = plugin / ".codex-plugin" / "plugin.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    assert tree_digest(plugin, "plugin")[0] != digest


def test_pointing_at_the_wrong_layout_says_which_one_was_assumed(plugin):
    """The two roots differ by two directory levels, so the error has to name
    the layout rather than list files that were never expected there."""
    with pytest.raises(SystemExit, match="skill tree"):
        tree_digest(plugin)


def test_strict_refuses_a_tree_carrying_undeclared_files(installed, capsys):
    """A leftover script beside the skill is something the agent can reach. It
    does not change the digest, and for certifying that is not enough.

    Nothing reaches stdout either: a digest on screen from a run that failed is
    a digest somebody copies into a record."""
    (installed / "leftover.py").write_text("print()", encoding="utf-8")

    with pytest.raises(SystemExit, match="no declarados"):
        main([str(installed), "--strict"])

    assert capsys.readouterr().out == ""


def test_the_two_layouts_are_the_ones_the_builder_produces():
    assert set(TREES) == {"skill", "plugin"}


def test_a_declared_file_that_is_a_symlink_is_refused(installed, tmp_path):
    """`is_file()` follows a link, so a declared file replaced by one pointing
    outside would hash through as present. What it points at is not part of the
    tree and can change afterwards without the digest moving."""
    outside = tmp_path / "elsewhere.md"
    outside.write_text("content that lives somewhere else", encoding="utf-8")
    skill = installed / "SKILL.md"
    skill.unlink()
    skill.symlink_to(outside)

    with pytest.raises(SystemExit, match="symlinks"):
        tree_digest(installed)


def test_an_alias_beside_a_declared_file_counts_as_an_extra(installed):
    """Comparing where a link resolves to made an alias disappear: it pointed
    at a declared file, so it matched one and left the tree looking clean while
    carrying an entry nobody declared."""
    before = tree_digest(installed)[0]
    (installed / "alias.md").symlink_to("SKILL.md")

    digest, extra = tree_digest(installed)

    assert extra == ("alias.md",)
    assert digest == before, "an alias is an extra entry, not different content"


def test_a_linked_plugin_manifest_is_refused_too(plugin, tmp_path):
    """The manifest decides which version an installer believes it has, so it
    is exactly the file worth pointing somewhere else."""
    outside = tmp_path / "plugin.json"
    outside.write_text("{}", encoding="utf-8")
    manifest = plugin / ".codex-plugin" / "plugin.json"
    manifest.unlink()
    manifest.symlink_to(outside)

    with pytest.raises(SystemExit, match="symlinks"):
        tree_digest(plugin, "plugin")


def test_a_root_that_is_a_symlink_is_refused(installed, tmp_path):
    """Certifying through a link certifies wherever it points today, and that
    can be repointed afterwards without the digest moving."""
    alias = tmp_path / "alias-root"
    alias.symlink_to(installed)

    with pytest.raises(SystemExit, match="root itself is a symlink"):
        tree_digest(alias)


def test_entries_that_are_not_files_still_count_as_extras(installed):
    """Only regular files and links were being counted, so a socket or a pipe
    left in the tree was invisible while still being reachable."""
    fifo = installed / "pipe"
    try:
        os.mkfifo(fifo)
    except (AttributeError, NotImplementedError, OSError):  # pragma: no cover
        pytest.skip("this platform has no FIFOs")

    assert tree_digest(installed)[1] == ("pipe",)
