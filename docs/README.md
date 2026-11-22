# Strata Type & Icon System Documentation

Reference documentation, versioning specification, and naming review for the **Strata** typeface family and icon library (**Release `27.0.0.0`**).

## Release `27.0.0.0` Summary

The blind council hill-climb concluded on **2026-11-22**. By owner decision, release **`27.0.0.0`** ships the finalized `r12-type` variable fonts together with the finalized `r15-icons` 71-icon library, packaged under [`dist/`](../dist/) with all P0 OpenType metadata, versioning, and `STAT` table defects resolved (zero outline or shaping drift against `r12-type`).

| Deliverable | Source Set | Canonical Source in Repo | Release Output (`dist/`) | Status |
| --- | --- | --- | --- | --- |
| **Typefaces** (4 variable faces) | `r12-type` | `candidates/r12-type/transforms/` | `dist/fonts/{core,full}/` | Released (`v27.0.0.0`), gate-checked, not yet wired into Strata-Weather |
| **Icons** (71 SVGs + React + WOFF2) | `r15-icons` | `candidates/r12-type/icons/` | `dist/icons/{svg,react,StrataIcons.woff2}` | Released (`v27.0.0.0`), validated & TSX-typechecked, not yet wired into Strata-Weather |

> [!NOTE]
> **Bookmarked future work (on hold until owner approval):**
> - **Strata Math** font face
> - Noto multi-script coverage merge & Nerd Font patching for `Strata Mono`
> - Windows hinting (`prep` smart dropout)
> - Integration into `strata-weather` (requires a `DESIGN.md` update)

## Annual Versioning (`27.xx.xx.xx`)

Strata Type uses an **annual 4-part version scheme** (`YY.minor.patch.build`), anchored to the target release year series (`27` for the 2027 series):

| Artifact | Format | `27.0.0.0` Value |
| --- | --- | --- |
| [`VERSION`](../VERSION), [`dist/release.json`](../dist/release.json), `build.json`, `icons/manifest.json` | `YY.minor.patch.build` | `27.0.0.0` |
| Git tag | `vYY.minor.patch.build` | `v27.0.0.0` |
| Python [`pyproject.toml`](../pyproject.toml) (PEP 440) | `YY.minor.patch.build` | `27.0.0.0` |
| Node [`package.json`](../package.json) (SemVer) | `YY.minor.patch` | `27.0.0` |
| OpenType `head.fontRevision` (16.16 Fixed) | `YY.mmP` (`minor` 00–99, `patch` 0–9) | `27.000` |
| OpenType `name` ID 5 (`Version`) | `Version YY.mmP;YY.minor.patch.build` | `Version 27.000;27.0.0.0` |
| OpenType `name` ID 3 (`Unique ID`) | `<PostScriptName>;YY.minor.patch.build` | `StrataSans-Regular;27.0.0.0` |

## System Overview

| Name | Role | Upstream Base | License | Core WOFF2 | Full WOFF2 |
| --- | --- | --- | --- | ---: | ---: |
| **Strata Sans** | UI reading, labels, headlines, body | Inter 4.1 | SIL OFL 1.1 | 106 KB | 386 KB |
| **Strata Sans Rounded** | Standalone numbers & weather readouts | Derived from Strata Sans | SIL OFL 1.1 | 73 KB | 73 KB |
| **Strata Serif** | Answer line & editorial headlines | Source Serif 4 (4.005) | SIL OFL 1.1 | 282 KB | 634 KB |
| **Strata Mono** | Code, terminal, technical data | Fira Code 6.2 | SIL OFL 1.1 | 47 KB | 118 KB |
| **Strata Icons** | Weather & UI icon library (71 icons) | Original + Lucide (ISC) + Hugeicons Free (MIT) | ISC & MIT | 8 KB (font) / 71 SVGs | — |

All four faces share harmonized vertical metrics (`typoAsc ≈ 0.969`, `typoDesc ≈ −0.241`), aligned x-height/cap-height proportions, default tabular figures, and weather-first typography (`°`, `−`, `℉`, `℃`, fractions, arrows).

## Documents

| Document | Contents |
| --- | --- |
| [fonts.md](fonts.md) | Complete specification and usage guide for `Strata Sans`, `Strata Sans Rounded`, `Strata Serif`, and `Strata Mono`: metrics, axes, named instances, defaults, OpenType features, character coverage, and CSS recipes. |
| [icons.md](icons.md) | Complete specification and 71-icon catalog for `Strata Icons` (`r15-icons`): grid/stroke contract, delivery formats (SVG, React TSX, WOFF2), `data-layer` multi-tone tinting, Strata-Weather mapping, and extension rules. |
| [naming-review.md](naming-review.md) | Full audit of font family names, OpenType binary metadata (`name`/`fvar`/`STAT` — P0 items resolved in `27.0.0.0`), OpenType feature labels, all 71 icon stems, React exports, `data-layer` tokens, and naming rules going forward. |

Related repository files:
- [DESIGN-BRIEF.md](../DESIGN-BRIEF.md) — Original design direction and license hygiene rules.
- [README.md](../README.md) — Build, gate, check, release packaging, and local specimen site instructions.
- [licenses/RFN.md](../licenses/RFN.md) — Reserved Font Name policy and required license notices.
- [candidates/r12-type/DESIGN-NOTES.md](../candidates/r12-type/DESIGN-NOTES.md) — Engineering and measurement notes for the finalized type build.

## Rebuilding & Packaging a Release

```sh
# 1. Regenerate r12-type UFO masters deterministically from candidates/baseline/fonts/
.venv/bin/python -I candidates/r12-type/transforms/apply.py

# 2. Build core fonts + r15-icons (from candidates/r12-type/icons/), gate, and verify
make build  CAND=r12-type SUBSET=core
make gate   CAND=r12-type
make checks CAND=r12-type

# 3. Emit dist/ (core WOFF2+TTF, full WOFF2, SVGs, React TSX, StrataIcons.woff2, release.json)
make dist   CAND=r12-type
```

## Licensing Summary

- **Fonts (SIL OFL 1.1):** Zero upstream Reserved Font Names (`Inter`, `Source`, `Fira`) appear in any compiled binary `name` table. Bundled verbatim upstream licenses and copyright notices in `licenses/` and `dist/licenses/` must accompany every distribution.
- **Icons (ISC & MIT):** Retain the Lucide ISC notice (including its embedded Feather MIT notice) and Hugeicons Free Stroke Rounded MIT notice (`licenses/lucide-LICENSE`, `licenses/hugeicons-free-LICENSE.md`, and `candidates/r12-type/icons/LICENSES.md`).
- **Proprietary references:** SF Pro, SF Rounded, New York, SF Symbols, Berkeley Mono, and Hugeicons Pro were never copied, traced, exported, or included as assets.
