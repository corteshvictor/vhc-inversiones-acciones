# Changelog

All notable changes to this project are documented here. The project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every entry after 1.0.0 is **generated** by
[release-please](https://github.com/googleapis/release-please) from
[Conventional Commits](https://www.conventionalcommits.org) — do not edit those
by hand. They are grouped by change type, in the spirit of
[Keep a Changelog](https://keepachangelog.com).

Keeping at least one version entry in this file is not cosmetic. With none,
release-please rewrites the whole file: it prepends its own title and demotes
every heading above, which pushes this preamble underneath the newest release.

Every version below is the **distribution** version: what the plugin and the
installable ZIP carry. It is not the version of the method. That one lives in
`SCREENING_VERSION`, is printed on every report, and only moves when a
threshold, a lens, a gate or the score itself changes.

<!-- release-please will insert released versions below this line. -->

## 1.0.0 (2026-08-25)

First public release.

### Features

* **screening:** classify an InvestingPro XLSX export into Deep Dive, Watchlist, Neutral and Descartada through quality, then financial health, then price
* **screening:** set apart Financials and Utilities as `Omitida por método` instead of measuring them with thresholds that do not fit them
* **screening:** deliver an enriched Excel workbook and a self-contained interactive dashboard
* **skill:** add the PDF Deep Dive route for Pro Research reports — qualitative only, with no bucket and no score
* **i18n:** emit the report, the Excel workbook and the dashboard in Spanish or English through `--lang`
* **plugin:** distribute the skill as an installable ZIP and as a plugin for Claude, ChatGPT and Codex
