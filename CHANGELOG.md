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

## [1.1.0](https://github.com/corteshvictor/vhc-inversiones-acciones/compare/v1.0.0...v1.1.0) (2026-08-25)


### Features

* **dashboard:** open the Neutral rows and cite where the method comes from ([6a7246d](https://github.com/corteshvictor/vhc-inversiones-acciones/commit/6a7246d083ae0198ee718d580a9f18df0ce09797))
* **io:** accept a universe wider than a single export ([49c7715](https://github.com/corteshvictor/vhc-inversiones-acciones/commit/49c7715168de6efc87398e8bed716ee343ba2416))
* **tools:** merge several exports and verify their continuity ([2a905e4](https://github.com/corteshvictor/vhc-inversiones-acciones/commit/2a905e45c7b4b1d99a2445d9b4769166d573b0a0))


### Bug Fixes

* **dashboard:** keep long alerts inside their column ([7014cf5](https://github.com/corteshvictor/vhc-inversiones-acciones/commit/7014cf5b5503b0af49eeca3896b64c4d016b9fc3))


### Documentation

* explain how to cover a universe wider than one export ([5b649f7](https://github.com/corteshvictor/vhc-inversiones-acciones/commit/5b649f7b972a267a39ef3bf3a39080f28daafd08))

## 1.0.0 (2026-08-25)

First public release.

### Features

* **screening:** classify an InvestingPro XLSX export into Deep Dive, Watchlist, Neutral and Descartada through quality, then financial health, then price
* **screening:** set apart Financials and Utilities as `Omitida por método` instead of measuring them with thresholds that do not fit them
* **screening:** deliver an enriched Excel workbook and a self-contained interactive dashboard
* **skill:** add the PDF Deep Dive route for Pro Research reports — qualitative only, with no bucket and no score
* **i18n:** emit the report, the Excel workbook and the dashboard in Spanish or English through `--lang`
* **plugin:** distribute the skill as an installable ZIP and as a plugin for Claude, ChatGPT and Codex
