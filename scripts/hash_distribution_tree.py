"""Identify an installed copy of the skill by digest.

The manual evaluation has to name what actually ran, and on the surfaces that
install from a marketplace that is not the ZIP: the application loads its own
extracted copy, so a correct archive digest proves nothing about the files the
agent read. This walks an installed tree and produces one value for it.

The digest has to mean the same thing on every machine, so it covers file
contents and relative paths and nothing else — not timestamps, not permissions,
not the order the filesystem happens to return. Paths are normalized to forward
slashes and sorted, so macOS, Linux and Windows agree.

    python scripts/hash_distribution_tree.py <skill-root> --kind skill --strict
    python scripts/hash_distribution_tree.py <plugin-root> --kind plugin --strict
"""

import argparse
import hashlib
import sys
from pathlib import Path

from build_skill import PACKAGE_FILES, PACKAGE_NAME

DEVELOPMENT_ONLY = "not packaged: this identifies a package, it does not ship in one"
LISTED_EXTRAS = 20

# What a tree is expected to contain depends on which one it is. A skill folder
# holds the package files at its root; a plugin wraps that folder and adds its
# own manifest, and pointing at the wrong one is easy enough that the error has
# to name which layout was assumed.
TREES = {
    "skill": PACKAGE_FILES,
    "plugin": (Path(".codex-plugin") / "plugin.json",)
    + tuple(Path("skills") / PACKAGE_NAME / name for name in PACKAGE_FILES),
}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: str | Path, kind: str = "skill") -> tuple[str, tuple[str, ...]]:
    """Digest the expected files under `root`, and report anything unexpected.

    Returns the digest and the extra files found. Extras do not change the
    value — a copy carrying a stray editor backup is still the same skill — but
    the evaluator should see them, because they can also be a stale file left
    by an install that did not replace everything.
    """
    root_path = Path(root)
    if root_path.is_symlink():
        raise SystemExit(
            "ERROR: the root itself is a symlink, so the tree being certified is "
            "somewhere else and can be repointed after the fact."
        )
    expected_files = TREES[kind]

    # A symlink is not the file it points at. `is_file()` follows one, so a
    # declared file replaced by a link to somewhere outside would pass as
    # present and be hashed through — certifying content that lives elsewhere
    # and can change afterwards without the digest moving.
    missing, linked = [], []
    for name in expected_files:
        candidate = root_path / name
        if candidate.is_symlink():
            linked.append(str(name))
        elif not candidate.is_file():
            missing.append(str(name))
    if missing:
        raise SystemExit(
            f"ERROR: this does not look like a {kind} tree. Missing: "
            + ", ".join(sorted(missing))
        )
    if linked:
        raise SystemExit(
            "ERROR: these are symlinks, so what they point at is not part of "
            "the tree and could change after it was certified: "
            + ", ".join(sorted(linked))
        )

    lines = sorted(
        f"{_digest(root_path / name)}  {name.as_posix()}" for name in expected_files
    )
    manifest = "\n".join(lines) + "\n"

    # Anything that is not a plain directory counts, not only regular files: a
    # socket or a FIFO left in the tree is reachable too, and was passing as
    # invisible. Compared by relative path, not by where a link resolves to: an alias
    # beside a declared file resolves to the same target and would otherwise
    # vanish from this list, so a strict run would call the tree clean while it
    # carries an entry nobody declared.
    expected = {name.as_posix() for name in expected_files}
    extra = tuple(
        sorted(
            found.relative_to(root_path).as_posix()
            for found in root_path.rglob("*")
            if not (found.is_dir() and not found.is_symlink())
            and found.relative_to(root_path).as_posix() not in expected
        )
    )
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest(), extra


def main(argv=None) -> str:
    parser = argparse.ArgumentParser(
        description="Identify an installed copy of the skill by digest."
    )
    parser.add_argument("root", help="Directory holding the installed copy")
    parser.add_argument(
        "--kind",
        choices=sorted(TREES),
        default="skill",
        help="Which layout the directory is: a skill folder or a plugin wrapping one",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Exit non-zero when the tree holds files the package does not declare. "
            "Use it to certify: a leftover script beside the skill is part of what "
            "the agent can reach, even though it does not change the digest."
        ),
    )
    arguments = parser.parse_args(argv)

    digest, extra = tree_digest(arguments.root, arguments.kind)
    if extra:
        # Diagnostics go to stderr so a caller can pipe the digest straight into
        # a record, and a strict run stops before printing anything: a hash on
        # screen from a run that failed is a hash somebody will copy.
        report = [f"Archivos ajenos al paquete ({len(extra)}), no entran en el hash:"]
        report += [f"  {name}" for name in extra[:LISTED_EXTRAS]]
        if len(extra) > LISTED_EXTRAS:
            report.append(f"  … y {len(extra) - LISTED_EXTRAS} más")
        print("\n".join(report), file=sys.stderr)
        if arguments.strict:
            raise SystemExit("ERROR: --strict y el árbol trae archivos no declarados.")
    print(digest)
    return digest


if __name__ == "__main__":  # pragma: no cover
    main()
