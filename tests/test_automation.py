"""The automation files. A malformed workflow does not fail: it never runs."""

import json
import re
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(".github/workflows")

# The evaluation matrix and how many independent runs each case needs. Three
# where a failure would be serious or has already happened, one where a single
# observation settles it. Pinned here so the guide cannot shrink unnoticed.
# The surfaces the matrix claims to cover, by product, distribution kind and the
# token that reaches the skill there. This table has already carried four
# errors on one branch — two surfaces missing, two chat modes merged into one
# row, and an install path that belonged to a different surface — with the whole
# suite green, so its shape is pinned. Menu wording and prose are not: those
# should be free to improve.
EVALUATION_SURFACES = {
    # product, surface marker, distribution, tokens, cases that do not apply
    "S01": ("Claude", "Chat", "zip", {"/vhc"}, {"C09a", "C09b"}),
    "S02": ("Claude", "Cowork", "zip", {"/vhc"}, {"C09a", "C09b"}),
    "S03": ("Claude", "Code", "local", set(), {"C08"}),
    "S04": ("ChatGPT", "web", "zip", {"@vhc"}, {"C09a", "C09b"}),
    "S05": ("ChatGPT", "modo Chat", "marketplace", {"@vhc"}, {"C09a", "C09b"}),
    "S06": ("ChatGPT", "Work", "marketplace", {"/vhc", "@vhc"}, {"C09a", "C09b"}),
    "S07": (
        "Codex",
        "app de ChatGPT",
        "marketplace",
        {"/vhc", "@vhc"},
        {"C09a", "C09b"},
    ),
    "S08": ("Codex", "CLI", "local", {"$vhc-inversiones-acciones"}, {"C09a", "C09b"}),
    "S09": (
        "Codex",
        "CLI",
        "marketplace",
        {"$vhc-inversiones-acciones"},
        {"C09a", "C09b"},
    ),
}

EVALUATION_CASES = {
    "C01": 3,
    "C02": 2,
    "C03": 3,
    "C04": 3,
    "C05a": 3,
    "C05b": 3,
    "C06": 3,
    "C07": 3,
    "C08": 1,
    "C09a": 1,
    "C09b": 1,
    "C10": 3,
    "C11": 1,
    "C12": 1,
    "C13": 3,
    "C14": 1,
    "C15": 3,
    "C16": 3,
    "C17": 3,
    "C18": 3,
    "C19": 1,
}


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("name", "jobs"),
    [
        ("ci.yml", {"gate", "windows", "packaging", "commits"}),
        ("pr-title.yml", {"lint-title"}),
        ("release.yml", {"release-please", "attach-skill"}),
    ],
)
def test_each_workflow_parses_and_keeps_its_jobs(project_root, name, jobs):
    document = _load(project_root / WORKFLOWS / name)

    assert set(document["jobs"]) == jobs
    for job in document["jobs"].values():
        assert job["runs-on"]
        assert job["steps"]


def test_every_action_is_pinned_to_a_sha(project_root):
    """A moving tag would let a third party change what CI runs."""
    for path in sorted((project_root / WORKFLOWS).glob("*.yml")):
        for used in re.findall(r"uses:\s*(\S+)", path.read_text(encoding="utf-8")):
            _repository, _, reference = used.partition("@")
            assert re.fullmatch(r"[0-9a-f]{40}", reference), f"{path.name}: {used}"


def test_dependabot_covers_what_the_project_consumes(project_root):
    document = _load(project_root / ".github" / "dependabot.yml")
    ecosystems = {entry["package-ecosystem"] for entry in document["updates"]}

    assert ecosystems == {"pip", "github-actions"}
    # Its pull requests must survive the commits job, which rejects anything
    # that is not a Conventional Commit. And a runtime bump must use a visible
    # type, or release-please would publish nothing and leave a security fix
    # stranded in the repository.
    prefixes = {
        entry["package-ecosystem"]: entry["commit-message"]["prefix"]
        for entry in document["updates"]
    }
    assert prefixes["pip"] == "fix(deps)"
    assert prefixes["github-actions"] == "ci(deps)"
    conventional = re.compile(r"^(feat|fix|ci|build)(\([a-z0-9 ._-]+\))?$")
    for prefix in prefixes.values():
        assert conventional.fullmatch(prefix), prefix


def test_release_please_starts_from_the_declared_commit(project_root):
    """Without a bootstrap point the first changelog replays the whole history."""
    config = json.loads(
        (project_root / "release-please-config.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (project_root / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    plugin = json.loads(
        (
            project_root
            / "plugins"
            / "vhc-inversiones-acciones"
            / ".codex-plugin"
            / "plugin.json"
        ).read_text(encoding="utf-8")
    )

    # bootstrap-sha tells release-please to look at nothing older than the SHA
    # it names, and is read only while no release exists at all. This repository
    # opens with v1.0.0 already tagged and released on its first commit, so
    # there is nothing older to skip and the key must stay absent: a stale SHA
    # is still a valid 40-character string, and it silently drops every commit
    # before it out of every changelog it writes.
    assert "bootstrap-sha" not in config
    assert config["packages"]["."]["extra-files"][0]["jsonpath"] == "$.version"
    assert manifest["."] == plugin["version"]


def test_the_release_pull_request_survives_its_own_ci(project_root):
    """release-please signs its pull request by default; the commits job rejects
    that signature. Left alone, the release would block itself."""
    config = json.loads(
        (project_root / "release-please-config.json").read_text(encoding="utf-8")
    )
    workflow = (project_root / WORKFLOWS / "ci.yml").read_text(encoding="utf-8")

    declared = re.search(r"signature='([^']+)'", workflow)
    assert declared is not None, "the commits job no longer declares a signature"
    forbidden = re.compile(declared.group(1), re.IGNORECASE)

    for key in ("pull-request-header", "pull-request-footer"):
        text = config[key]
        assert text, f"{key} must override the default, which carries a signature"
        assert not forbidden.search(text), f"{key} would fail the commits job"

    # The title has to survive pr-title.yml and still carry the version. Both
    # patterns are declared because a grouped run reads the group one, and a
    # title without ${version} — the default grouped shape is "release main" —
    # would pass CI and then leave nothing to cut a tag from.
    rule = re.search(
        r"pattern='([^']+)'",
        (project_root / WORKFLOWS / "pr-title.yml").read_text(encoding="utf-8"),
    )
    assert rule is not None, "pr-title.yml no longer declares a pattern"

    patterns = ("pull-request-title-pattern", "group-pull-request-title-pattern")
    for key in patterns:
        assert "${version}" in config[key], f"{key} must carry the version"
        title = config[key].replace("${version}", "1.2.0")
        assert re.match(rule.group(1), title), title
        assert "1.2.0" in title

    # Both shapes must agree: which one release-please picks depends on whether
    # the run is grouped, and the documented title cannot depend on that.
    assert config[patterns[0]] == config[patterns[1]]


def test_the_changelog_keeps_its_preamble_above_the_entries(project_root):
    """A changelog holding no version entry is rewritten, not appended to:
    release-please prepends its own title and demotes every heading above it,
    which buries the preamble under the newest release. One entry prevents it."""
    changelog = (project_root / "CHANGELOG.md").read_text(encoding="utf-8")

    # DEFAULT_VERSION_HEADER_REGEX, from src/updaters/changelog.ts. Everything
    # before the first match is carried over untouched; with no match, nothing
    # is, and adjustHeaders() turns every `# ` above into `## `.
    first_entry = re.search(r"\n###? v?[0-9[]", changelog)
    assert first_entry, "CHANGELOG.md needs a version entry to stay append-only"

    # Asserting the entry exists is not enough: a rewritten file still has one.
    # What separates the two is where the preamble sits, so read the text above
    # the first entry and require the whole preamble to be in it.
    preamble = changelog[: first_entry.start()]
    assert preamble.startswith("# Changelog\n")
    for phrase in ("Semantic Versioning", "release-please", "SCREENING_VERSION"):
        assert phrase in preamble, f"the preamble no longer sits above {phrase!r}"


def test_the_changelog_records_the_version_being_distributed(project_root):
    """Shipping a version with no entry leaves a reader unable to tell what
    changed in it. release-please writes both in the same commit, so the only
    way they drift apart is a hand-written entry that was never added."""
    manifest = json.loads(
        (project_root / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    changelog = (project_root / "CHANGELOG.md").read_text(encoding="utf-8")

    # Both shapes release-please emits: `## [1.1.0](compare-link)` once there is
    # a previous tag, and a bare `## 1.0.0` for the very first release.
    entry = rf"^## \[?{re.escape(manifest['.'])}[\]( ]"
    assert re.search(entry, changelog, re.MULTILINE), manifest["."]


def test_the_release_can_actually_be_tagged(project_root):
    """The release aborts after its pull request has already merged when the
    config declares a package name. release-please compares the release
    branch's component against the one it derives from the config, and
    getBranchComponent() ignores include-component-in-tag while getComponent()
    honors it. With separate pull requests off the branch is
    `release-please--branches--main`, which carries no component, so any
    package name here is a mismatch and no tag is ever cut."""
    config = json.loads(
        (project_root / "release-please-config.json").read_text(encoding="utf-8")
    )

    assert config["include-component-in-tag"] is False
    assert config["separate-pull-requests"] is False
    assert "package-name" not in config["packages"]["."]


def test_development_bumps_do_not_cut_a_release(project_root):
    """release-please raises the patch for every type that is not `feat`, and
    opens a release pull request unless the changelog entry comes out empty. A
    development bump changes nothing a user installs, so a visible type would
    publish a version carrying a byte-identical package — once a week, forever.
    Grouping them keeps that traffic to one pull request instead of one per
    tool; runtime bumps stay ungrouped so a security fix travels alone."""
    document = _load(project_root / ".github" / "dependabot.yml")
    config = json.loads(
        (project_root / "release-please-config.json").read_text(encoding="utf-8")
    )
    hidden = {
        section["type"]
        for section in config["changelog-sections"]
        if section.get("hidden")
    }

    development = [
        entry["commit-message"]["prefix-development"]
        for entry in document["updates"]
        if "prefix-development" in entry["commit-message"]
    ]
    assert development, "no development prefix is configured"
    for prefix in development:
        assert prefix.partition("(")[0] in hidden, prefix

    grouped = [
        group["dependency-type"]
        for entry in document["updates"]
        for group in entry.get("groups", {}).values()
        if "dependency-type" in group
    ]
    assert "development" in grouped


def test_every_evaluation_case_is_a_row_of_its_table(project_root):
    """A blank line ends a Markdown table, so four cases added after one were
    rendering as loose text rather than as part of the matrix — obligatory in
    the prose, invisible in the table a reader actually scans. This parses the
    rows the way a renderer would, so the count and the table cannot drift."""
    guide = (project_root / "tests" / "evals" / "README.md").read_text(encoding="utf-8")

    block = max(re.findall(r"(?:^\|.*$\n?)+", guide, re.MULTILINE), key=len)
    ids = re.findall(r"^\| (C\d+[ab]?) \|", block, re.MULTILINE)

    assert ids == sorted(ids), "the cases are out of order"
    assert len(ids) == len(set(ids)), "an identifier is repeated"
    # Every identifier the guide mentions in prose has to exist as a row.
    for mentioned in sorted(set(re.findall(r"\bC\d+[ab]?\b", guide))):
        assert mentioned in ids, f"{mentioned} is named but is not a row"

    # Checking only what the guide mentions lets a case be deleted whole — row
    # and mentions together — and the suite stays green while the matrix
    # quietly covers less. The set is pinned instead, so dropping one is a
    # decision somebody makes here rather than an edit nobody notices.
    assert ids == list(EVALUATION_CASES), "the matrix no longer covers the same cases"
    runs = dict(re.findall(r"^\| (C\d+[ab]?) \| (\d+) \|", block, re.MULTILINE))
    assert {case: int(count) for case, count in runs.items()} == EVALUATION_CASES, (
        "a case changed how many independent runs it needs"
    )


def test_the_matrix_covers_the_surfaces_it_claims(project_root):
    """A case is only certified where it was run, so the list of surfaces is
    part of the promise. Checking the product and one token left too much
    loose: two rows could collapse into the same surface, a token could
    disappear, or a case could be excluded where it does apply, all with the
    suite green. Menu wording stays free to improve; what is fixed is which
    surface, how the candidate is installed, what reaches it, and where a case
    genuinely cannot mean anything."""
    guide = (project_root / "tests" / "evals" / "README.md").read_text(encoding="utf-8")
    rows = re.findall(
        r"^\| (S\d\d) \| (\w+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$",
        guide,
        re.MULTILINE,
    )

    assert [row[0] for row in rows] == list(EVALUATION_SURFACES)
    for identifier, product, surface, distribution, invocation, applicable in rows:
        expected = EVALUATION_SURFACES[identifier]
        assert product == expected[0], identifier
        assert expected[1] in surface, f"{identifier} is no longer that surface"

        # Classify on the mechanism, not on a path that happens to name one:
        # `.agents/plugins/marketplace.json` contains the word "marketplace"
        # while describing a ZIP upload, and that read the wrong way once.
        mechanism = re.sub(r"`[^`]*`", "", distribution)
        kind = (
            "marketplace"
            if "marketplace" in mechanism
            else "zip"
            if "ZIP" in mechanism
            else "local"
        )
        assert kind == expected[2], f"{identifier} installs another way now"
        assert set(re.findall(r"`([^`]+)`", invocation)) == expected[3], identifier
        assert set(re.findall(r"\bC\d+[ab]?\b", applicable)) == expected[4], identifier

    # Only discovery and installation can be inapplicable somewhere; a behavior
    # case that stops running on a surface is that surface losing coverage.
    excluded = set().union(*(surface[4] for surface in EVALUATION_SURFACES.values()))
    assert excluded == {"C08", "C09a", "C09b"}


def test_the_guide_gives_the_command_that_certifies(project_root):
    """The bare command assumes a skill folder and no strict check, so an
    evaluator pointing at a marketplace copy gets a layout error, and one whose
    installation carries leftovers gets a digest and a zero exit. Both are
    written out, because a protocol is only followed as literally as it reads."""
    guide = (project_root / "tests" / "evals" / "README.md").read_text(encoding="utf-8")

    for kind in ("skill", "plugin"):
        assert f"--kind {kind} --strict" in guide, f"the {kind} command is missing"
