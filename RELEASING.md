# Releasing

`CHANGELOG.md`, the plugin version, the tag and the GitHub Release are generated
by [release-please](https://github.com/googleapis/release-please) from the
Conventional Commits that land on `main`. None of them is edited by hand, with
the one closed exception recorded below.

## The cycle

1. A pull request merges with a Conventional Commit title.
2. `release.yml` opens a pull request titled `chore: release X.Y.Z` — the title
   pattern is pinned in `release-please-config.json`, not left to the default —
   carrying the
   `CHANGELOG.md` entry and the version bumps.
3. That pull request is reviewed like any other and runs the same CI.
4. Merging it creates the `vX.Y.Z` tag and the GitHub Release, with
   `vhc-inversiones-acciones.zip` attached.

The commit type decides the bump, and the rule is blunter than it looks: a `!`
or a `BREAKING CHANGE:` footer raises the major, `feat` raises the minor, and
**every other type raises the patch**.

What decides whether a release happens at all is visibility, not the type.
release-please skips the release pull request when the changelog entry would
come out empty, so a run of hidden types — `style`, `test`, `chore`, `ci` —
publishes nothing. One visible commit is enough to cut a patch, even when no
packaged file changed.

That pull request is not exempt from the checks. Its title is a Conventional
Commit, and its header and footer are overridden in `release-please-config.json`
because the defaults carry a `:robot:` shortcode and the phrase "generated with"
— both rejected by the `commits` job, which would otherwise block the release from
merging. A test keeps those two strings clear of the pattern. What it does skip
is the pull request template: its body is the changelog entry, which describes
the change better than a form would.

## How pull requests are merged

**Rebase and merge**, set in GitHub's repository settings and stated in
`AGENTS.md`. The reason is the changelog.

A regular merge writes an extra commit whose message is the pull request title.
release-please reads that message like any other, so the pull request appears in
the changelog *alongside* the commits it summarizes — one feature, listed twice,
in slightly different words. A squash has the opposite problem: it collapses the
atomic commits this repository deliberately keeps. Rebasing keeps every semantic
commit and writes no extra message for release-please to read.

## Two versions that are not the same

| | What it is | Where it lives | When it moves |
|---|---|---|---|
| Distribution | What a user installs | `plugin.json` and `.release-please-manifest.json` | Every release, automatically |
| Method | The thresholds, lenses, gates and score | `SCREENING_VERSION` in `constants.py` | Only when the method changes. By hand, on purpose |

`SCREENING_VERSION` is printed on every report so two runs months apart stay
comparable. Raising it without changing the method breaks that promise. It has
not moved since the first commit.

A test compares `plugin.json` against `.release-please-manifest.json`, so the
two cannot drift apart.

## The one rule the automation depends on

**`CHANGELOG.md` must always hold at least one version entry**, and a test
enforces it. With none, release-please stops appending and rewrites instead: it
prepends its own title and demotes every heading above, pushing the preamble
underneath the newest release.

## No `bootstrap-sha`

`bootstrap-sha` tells release-please to look at nothing older than a given
commit. It is read **only while no release exists at all**, and the repository
opens with `v1.0.0` already tagged and released on its first commit, so there is
nothing older for it to skip. The key is absent on purpose; a test asserts it
stays absent, because a stale SHA silently drops every commit before it out of
the changelog.

## The secret to create once

`release.yml` uses `secrets.RELEASE_PLEASE_TOKEN`: a dedicated token with write
access to contents and pull requests. **Without it the workflow fails.**

The default `GITHUB_TOKEN` will not do: a pull request opened with it does not
trigger CI, so the release pull request would sit unverified.

Fine-grained tokens expire. When that happens `release.yml` fails with an
authentication error: regenerate the token and replace the secret, keeping the
same name. No workflow changes.

`ci.yml` and `pr-title.yml` need no secret.
