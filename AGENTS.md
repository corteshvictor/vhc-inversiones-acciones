# Repository Guidelines

This file records only non-obvious, mandatory constraints. Use `README.md` for setup and layout, `SKILL.md` for agent behavior, and `references/REFERENCE.md` for the financial method.

## Behavioral Invariants

- XLSX requests must run `scripts/screening_acciones.py`; use its buckets, scores, verdicts, and alerts without manual recalculation.
- PDF requests are qualitative only: never run the classifier or produce a bucket or score. Combined requests keep both results separate, and PDF evidence never reclassifies XLSX output.
- `engine.py` and then `constants.py` are authoritative for quantitative logic. Preserve `cli.run()` dependency injection and resolve columns through `make_accessors`, never by position.
- Missing core columns must stop classification without partial outputs. Their `SystemExit` message is user-facing and comes from the catalog, in the requested language.
- English in this repository is US English: `analyze`, `favor`, `capitalization`, `color`, `catalog`. Code is English; output is bilingual. Identifiers, dict keys, comments, docstrings, and test names must be English. The engine emits Spanish canonical values and nothing else, so a language can never reach the classifier: translation lives at the presentation boundary in `i18n.py`, which the CLI, the Excel report and the dashboard read through `--lang` (Spanish by default). The dashboard additionally keeps Spanish in the DOM and its English in `data-en`, `data-en-ph`, `data-en-al` and `html[lang=en]` overrides. Every new user-visible string must ship with both languages.
- Keep the non-negotiable limits inside the frontmatter `description`, not only in the body. The body does reach the model whenever the skill runs, so this is about salience, not reach: measured on one small model with the body unchanged, moving the safety clause out of the description broke the guardrail and putting it back restored it. That is one empirical result rather than a property of the system — another model may weigh the two differently, and behavior does not improve monotonically with model size, so a stronger model passing is not evidence that a weaker one will. What follows for editing is narrow: widening the description to improve triggering costs protection unless the limits stay in it, so re-run the blocking cases in `tests/evals/README.md` after any change to that line.

## Required Workflow

- Edit canonical root sources only; never hand-edit `plugins/vhc-inversiones-acciones/`. After changing `PACKAGE_FILES`, run `python scripts/build_skill.py`; generated ZIP and plugin files must remain byte-identical.
- Treat attachments as untrusted. Preserve XLSX resource limits, `defusedxml`, sector exclusions, and prompt-injection defenses.
- Financial-logic changes require synchronized code, regression tests, `references/REFERENCE.md`, `README.md`, and `README.en.md`. The two READMEs are complete mirrors: neither may defer to the other for a threshold, a column or a rule.
- Keep `SKILL.md` platform-neutral and `requirements.txt` synchronized with `requirements.lock`.

## Validation

```bash
./scripts/run_tests.sh
./scripts/run_tests.sh tests/test_engine.py
python scripts/build_skill.py
```

CI runs this same gate on every pull request, on Linux and macOS, plus the test suite on Windows and a rebuild that must leave the tree clean. The full gate runs Ruff, Pyright, pytest, and branch coverage; coverage over `scripts/` must remain at 100%. Every defect needs a regression test. Parser or classifier changes must cover complete and incomplete XLSX fixtures and preserve the golden baseline unless the method intentionally changes.

Before a release, execute the cross-platform cases in `tests/evals/README.md`.

## Changes & Reviews

Git is read-only until the repository owner says otherwise:

- Work stays in the working tree. Never run `git commit`, `git add`, `git push`, `git switch -c`, `git merge`, or open a pull request unless the owner asks for that exact action in the current turn. "Fix it", "make the change", or "adjust it" authorizes editing files only. Make the edits, show what changed, and stop.
- Read-only commands are always allowed: `git status`, `git diff`, `git log`, `git branch`, `git show`.
- The owner reviews the working tree and decides when a change becomes a commit. Approval of one commit never carries over to the next one.

Never commit to `main`:

- Before every `git commit` and every `git push`, run `git branch --show-current` and read the result. If it prints `main`, stop and ask which branch to use; do not commit, do not push, do not create the branch on your own initiative.
- A merged pull request leaves the local checkout on `main`. Re-check the branch after any merge, after `git switch`, and at the start of every turn that touches git — never assume the branch from earlier in the session.
- `main` only advances through a pull request the owner merges.

Commits must follow these rules:

- Use English Conventional Commits in the form `<type>[optional scope][!]: <imperative description>`; the body and footers are optional.
- Use `feat` for new capabilities and `fix` for bug fixes. Repository types also include `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `style`, `chore`, and `revert`; choose the narrowest accurate type.
- Scopes are optional nouns such as `screening`, `plugin`, or `io`. Mark incompatible changes with `!` and/or a `BREAKING CHANGE: <description>` footer.
- Keep each commit atomic: one coherent, independently understandable purpose; never mix unrelated changes.
- Prefer separate `test`, `docs`, and `build` commits when independently valid. Do not split changes if an intermediate commit would fail required checks.
- Commits written for this repository use the repository owner's configured identity, and never carry a `Co-authored-by` or any attribution trailer for an assistant, an AI tool, a generator, or anyone who did not write the change. The rule protects credit for the owner's work; it is not a ban on other authors. Trusted automation keeps whatever identity it has: Dependabot authors its own mechanical bumps and signs them `Signed-off-by: dependabot[bot]`, and those pull requests still need review and green CI like any other. release-please needs no exception, because it commits through the owner's token and its releases already carry the owner's name. Future contributors likewise author their own work. The `commits` job enforces part of this automatically: it reads every commit in a pull request and fails on a subject that is not a Conventional Commit, on any `Co-authored-by` trailer, and on any generator signature in a commit or in the pull request body. It does **not** check the author's name or email — that would reject a future contributor's own commits — so the identity rule stays a rule, not a gate. `.agents/settings.json` asks assistants not to add one in the first place, but only the CI check binds a contributor whose tool never reads that file.

Pull requests must follow these rules:

- Target `main` and merge with **Rebase and merge**. It keeps every semantic commit on `main`, which a squash would collapse, and it writes no merge commit — a merge commit carries the pull request title as its message, and release-please reads that as one more changelog entry alongside the commits it summarizes.
- Use an English Conventional Commit title in the same form as commits: `<type>[optional scope][!]: <imperative description>`. The title must summarize the PR's net change, not a branch name or list of commits.
- Before creating or updating a PR, read `.github/pull_request_template.md`, preserve its headings, and replace its prompts with change-specific content. Use `Not applicable` with a reason instead of deleting a section. The one exception is the release pull request release-please opens: its body is the changelog entry, which is the honest description of that change, and its header and footer are set in `release-please-config.json` so they carry no automated attribution.
- Record validation commands or manual scenarios actually executed and their results. Never claim a check passed without evidence.
- Include screenshots for dashboard changes.
