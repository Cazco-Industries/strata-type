# Strata Typeface System (`r12-type`, Release `27.0.0.0`)

Technical and usage reference for the finalized **Strata** variable font family (`candidates/r12-type`, packaged in [`dist/fonts/`](../dist/fonts/) at annual version **`27.0.0.0`**).

> [!NOTE]
> **Status:** Released in `Cazco-Industries/strata-type` at `v27.0.0.0`, locally built, FontBakery-gated (0 errors, 0 metadata/naming/STAT/version failures), and check-verified (`make checks` PASS). **Not yet wired into `strata-weather`** (requires a `DESIGN.md` update).

---

## Family Overview

| Face | Family Name | Shipped Files (`dist/fonts/`) | Core WOFF2 / TTF | Full WOFF2 | Core / Full Glyphs | Core / Full Codepoints | Upstream Fork (OFL 1.1) | Target Strata-Weather Token |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| **Sans** | `Strata Sans` | `StrataSans.{woff2,ttf}` | 106 KB / 273 KB | 386 KB | 753 / 2,985 | 258 / 2,853 | Inter 4.1 | `--font-sans`, `--font-display` |
| **Rounded** | `Strata Sans Rounded` | `StrataSansRounded.{woff2,ttf}` | 73 KB / 146 KB | 73 KB | 141 / 141 | 108 / 108 | Derived from Strata Sans | `--font-numeric` |
| **Serif** | `Strata Serif` | `StrataSerif.{woff2,ttf}` | 282 KB / 643 KB | 634 KB | 564 / 1,482 | 258 / 937 | Source Serif 4 (4.005) | `--font-headline` |
| **Mono** | `Strata Mono` | `StrataMono.{woff2,ttf}` | 47 KB / 104 KB | 118 KB | 677 / 2,166 | 258 / 1,609 | Fira Code 6.2 | `--font-mono` (code/data) |

All four faces are **upright variable TrueType/WOFF2 fonts** stamped with `head.fontRevision = 27.000` and `name` ID 5 = `Version 27.000;27.0.0.0`. All outline and metadata edits are generated deterministically from `candidates/baseline/fonts/` by `candidates/r12-type/transforms/`.

---

## Harmonized Metrics

Measured at each face's default variable location (UPM-normalized values from `make gate`):

| Face | UPM | x-height | Cap height | Typo asc / desc / gap | hhea asc / desc / gap | Win asc / desc | Weight (`wght`) | Optical Size (`opsz`) |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| **Strata Sans** | 2048 | `0.5459` (1118) | `0.7275` (1490) | `0.9688 / −0.2412 / 0` | `0.9688 / −0.2412 / 0` | `1.1260 / 0.3447` | `100–900` (default `400`) | `8–32` (default `14`) |
| **Strata Sans Rounded** | 2048 | `0.5459` (1118) | `0.7275` (1490) | `0.9688 / −0.2412 / 0` | `0.9688 / −0.2412 / 0` | `1.1260 / 0.3447` | `100–900` (default `400`) | `8–32` (default `14`) |
| **Strata Serif** | 1000 | `0.5390` (539) | `0.7300` (730) | `0.9690 / −0.2410 / 0` | `0.9690 / −0.2410 / 0` | `1.1300 / 0.3660` | `200–900` (default `400`) | `8–60` (default `20`) |
| **Strata Mono** | 1950 | `0.5462` (1065) | `0.7144` (1393) | `0.9687 / −0.2410 / 0` | `0.9687 / −0.2410 / 0` | `1.2482 / 0.5200` | `300–700` (default `300`*) | — |

\* `Strata Mono` has its `wght` axis default at `300` (Light); explicitly specify `font-weight: 400` in CSS for standard body/code weight.

**Cross-face alignment guarantees (`make checks` PASS):**
- **Line box parity:** Typographic ascender (`~0.969 em`), descender (`~−0.241 em`), and line gap (`0`) match across all four faces so mixed-face lines stay vertically aligned without shifting line height.
- **Default tabular figures:** All four faces default to **tabular (equal-width) figures** across every tested axis location (`make checks`: Sans 21 locations PASS, Rounded 15 PASS, Mono 5 PASS, Serif 30 tabular INFO).
- **Regular vs. Rounded width parity:** At 96 px / weight 400, `Strata Sans` and `Strata Sans Rounded` match shaped ink width to `+0.000%` on `104°F`, `72°`, `18:30`, and `−3°`.

---

## Face Reference

### 1. Strata Sans

Primary interface, label, body, and UI display typeface.

- **Design character:** Neutral neo-grotesque with subtly squared round forms, axis-cut terminals with open apertures at text sizes, finer strokes and tighter tracking at display sizes (`opsz=32`), and emboldened stems with looser spacing at caption sizes (`opsz=8`).
- **Default disambiguation & weather forms:**
  - **Tabular figures** are the default (`0.6543 em` advance at default Regular); enable `pnum` (`font-variant-numeric: proportional-nums`) for hero temperatures or running prose.
  - **Barred uppercase `I`** and **tailed lowercase `l`** are the defaults (prevents `I`/`l`/`1` confusion in station codes, METARs, and units).
  - **Flat-top `3`**, **open `4`**, **straight-stem `6` and `9`**, **spurred `G`**, and **footed `1`** are the defaults.
  - **Contextual figure punctuation (`calt`):** Between two digits, `:` automatically substitutes a larger, more open, vertically centered `colon.fig` (for times like `18:30`), and `-` substitutes a shorter, x-height-centered `hyphen.fig`.
  - **Weather units:** Sized degree ring `°`, true minus `−` (`U+2212`) matched to figure width and height, composed `℉` (`U+2109`) and `℃` (`U+2103`), arrows, superscripts, and fractions (`¼ ½ ¾`, arbitrary `frac`).
- **Axes:**
  - `opsz`: `8` (Caption) → `14` (Text, default) → `32` (Display)
  - `wght`: `100` (Thin) → `400` (Regular, default) → `900` (Black), with custom ink-balanced `avar` stops (`500→495`, `600→590`, `700→670`, `800→780`)
- **Named instances (18 unique):** 9 Text weights (`Thin`–`Black`, `StrataSans-Thin`..`StrataSans-Black` at `opsz=14`) + 9 Display weights (`Display Thin`, `Display ExtraLight`, `Display Light`, `Display`, `Display Medium`, `Display SemiBold`, `Display Bold`, `Display ExtraBold`, `Display Black`, `StrataSans-Display*` at `opsz=32`). `STAT` table carries 11 axis values (`Text`/`Display` + all 9 weights).
- **OpenType features:**
  - **Default / automatic:** `calt` (figure colon/hyphen), `kern`, `locl`
  - **Figures & math:** `tnum` (default), `pnum` (proportional figures), `zero` (slashed zero), `frac`, `numr`, `dnom`, `sups`, `subs`, `sinf`, `ordn`
  - **Case & spacing:** `case` (all-caps punctuation), `cpsp`
  - **Stylistic sets (`ss*`):**
    - `ss01` — Classic digits · `ss02` — Disambiguation · `ss03` — Round quotes & commas
    - `ss04` — Disambiguation (no slashed zero) · `ss05` — Circled characters · `ss06` — Squared characters
    - `ss07` — Square punctuation · `ss08` — Square quotes · `ss09` — Upper-case `I` without serifs
  - **Character variants (`cv*`):**
    - `cv01` Alternate `1` · `cv02` Closed `4` · `cv03` Curved `6` · `cv04` Curved `9`
    - `cv05` Lowercase `l` without tail · `cv06` Simplified `u` · `cv07` Alternate `ß`
    - `cv08` Uppercase `I` without serif · `cv09` Round-top `3` · `cv10` Capital `G` without spur
    - `cv11` Single-story `a` · `cv12` Compact `f` · `cv13` Compact `t`
  - **Other:** `aalt`, `dlig`, `salt`

---

### 2. Strata Sans Rounded

Dedicated rounded numeric face for standalone temperatures, clock times, gauges, and metric readouts (the role SF Rounded plays in Strata-Weather).

- **Design character:** Built deterministically from the finished `Strata Sans` masters (all 9 masters: Caption/Text/Display × Thin/Regular/Black) using a rounded pen on corners, joins, and terminals, with slightly rounder hero figure bowls (`0–9`, `°`, `%`, `.`, `:`) while keeping **exact advance-width and kerning parity** with `Strata Sans`.
- **Coverage (108 codepoints / 141 glyphs — identical in core and full builds):**
  - Full printable **Basic Latin ASCII** (`U+0020`–`U+007E`: digits, uppercase/lowercase letters, punctuation, operators — supports unit labels like `mph`, `inHg`, `AM`/`PM`, `NNW` alongside numbers without font fallback).
  - **13 weather & typographic extras:** `NBSP` (`U+00A0`), `°` (`U+00B0`), `±` (`U+00B1`), `¼` (`U+00BC`), `½` (`U+00BD`), `¾` (`U+00BE`), figure space (`U+2007`), punctuation space (`U+2008`), thin space (`U+2009`), fraction slash `⁄` (`U+2044`), `℃` (`U+2103`), `℉` (`U+2109`), true minus `−` (`U+2212`).
- **Axes:** `opsz` `8–32` (default `14`), `wght` `100–900` (default `400`).
- **Named instances (9 unique):** `Thin` through `Black` (`StrataSansRounded-Thin`..`StrataSansRounded-Black`) at `opsz=14`. `STAT` table carries 10 axis values (`Text` + all 9 weights).
- **OpenType features:** `calt` (carries `colon.fig` and `hyphen.fig`), `case`, `cv08` (bare `I`), `kern`, `pnum`, `salt`, `ss09` (`Upper-case i without serifs`), `tnum` (default), `zero` (slashed zero).

---

### 3. Strata Serif

Editorial serif for the Today answer line, page titles, Radar answer line, and forecaster ledes (the role New York plays in Strata-Weather).

- **Design character:** Scaled `1.09×` from Source Serif 4 to match `Strata Sans` cap height, with raised x-height, trimmed display ascenders/descenders so 48 px multi-line headlines stay clear of line-contact collisions, stroke color matched to `Strata Sans`, a smooth single-cubic `?`/`¿` hook taper, and strengthened caption hairlines.
- **9–13 px monotonic caption fade (`r12-type`):**
  - Caption masters (`opsz=8`) open right sidebearings by `+149` units so small 9–10 px text keeps ≥ 2 raster px clearance between adjacent characters at 2×.
  - Two sparse glyph-only fade layers (`fade.12` at 12 px / `+11` units, `fade.13` at 13 px / `0` units) guarantee that CSS set width rises monotonically at every whole pixel from 9 to 13 px while keeping `13–60 px` identical to `r11-type`.
- **Axes:** `wght` `200–900` (default `400`), `opsz` `8–60` (default `20`).
- **Named instances (30 unique):** 5 optical bands (`Caption` at `opsz=8`, `SmText` at `opsz=16`, default Text at `opsz=20`, `Subhead` at `opsz=32`, `Display` at `opsz=60`) × 6 weights (`ExtraLight`, `Light`, `Regular`/base, `Semibold`, `Bold`, `Black`). Default binary name is `Strata Serif Regular` (`StrataSerif-Regular`), and `STAT` aligns on `SmText` (all combinations ≤ 31 chars).
- **OpenType features:** `tnum` (default), `pnum`, `lnum` (lining, default), `onum` (oldstyle), `zero`, `frac`, `numr`, `dnom`, `sups`, `subs`, `sinf`, `ordn`, `smcp`, `c2sc`, `case`, `ccmp`, `liga`, `locl`, `aalt`, `kern`, `mark`, `mkmk`.

---

### 4. Strata Mono

Monospace face for code, terminal output, METARs, raw forecaster discussions, and structured numeric tables.

- **Design character:** Squared, technical character (`1217`-unit cell on `1950` UPM, `0.6241 em` advance) matched to `Strata Sans` x-height and vertical metrics, with squared dots, axis-cut terminals, distinct dash lengths (hyphen `609`, minus `913`, en dash `1079`), separate plus glyphs in `++`/`+++`, and closed-ring `@`, conventional `&`, and dotted `0` as defaults.
- **Temperature unit shaping (`ccmp`, default ON):**
  - `℉` (`U+2109`) and `℃` (`U+2103`) decompose in the first `ccmp` lookup into the exact two-cell pair `°F` / `°C`, rendering pixel-identical to typed `°F`/`°C` regardless of ligature settings.
  - Standalone `uni2109`/`uni2103` glyphs remain in the `cmap` and fit cleanly inside one `1217`-unit cell for unshaped text environments.
- **Coding ligatures are opt-in (default OFF):**
  - Unlike upstream Fira Code, multi-character operator ligatures (`===`, `!==`, `=>`, `<=`, `>=`, `->`, etc.) are **off by default** so technical weather/code text stays literal.
  - Enable them explicitly via `font-feature-settings: "dlig" 1, "ss11" 1` (or `font-variant-ligatures: discretionary-ligatures`).
- **Axes:** `wght` `300–700` (default `300`).
- **Named instances (5 unique):** `Light` (`300`), `Regular` (`400`), `Medium` (`500`), `SemiBold` (`600`), `Bold` (`700`), with matching 5-entry `STAT` table.
- **OpenType features:**
  - **Default / automatic:** `ccmp` (includes `℉`/`℃` decomposition), `calt` (contextual positioning), `locl`
  - **Opt-in coding ligatures:** `dlig` and `ss11` (`Operator ligatures`)
  - **Figures & math:** `tnum` (default), `onum`, `zero`, `frac`, `numr`, `dnom`, `sups`, `subs`, `sinf`, `ordn`
  - **Stylistic sets (`ss01`–`ss11`):**
    - `ss01` Sans-serif lowercase `r` · `ss02` Horizontal-bar `<=`/`>=` · `ss03` Et ampersand (`&`)
    - `ss04` Lightweight `$` · `ss05` Open `@` · `ss06` Thin `\` · `ss07` Regex matching operator
    - `ss08` Gaps in `==`/`===` · `ss09` Restore `<<=`/`>>=`/`||=`/`|=` arrows · `ss10` `Tl`/`Fl`/`fi`/`fj`/`fl`/`ft` ligatures
    - `ss11` Operator ligatures
  - **Character variants (`cv01`–`cv32`):** Individual glyph and operator alternates.

---

## Character Coverage

### Core Subset (`dist/fonts/core/`)

**258 codepoints** for Sans, Serif, and Mono (**108 codepoints** for Rounded):
- **Basic Latin (`U+0020`–`U+007E`)** — ASCII letters, digits, punctuation, operators
- **Latin-1 Supplement (`U+00A0`–`U+00FF`)** — accented Latin, `°`, `±`, `¹ ² ³`, `¼ ½ ¾`, `×`, `÷`, currency & punctuation
- **Typographic spaces & punctuation (`U+2000`–`U+200A`, `U+2010`–`U+2015`, `U+2018`–`U+201E`, `U+2022`, `U+2026`, `U+202F`, `U+2030`, `U+2032`–`U+2033`, `U+2044`)**
- **Superscripts (`U+2070`–`U+2079`, excluding unassigned `U+2072`/`U+2073`)**
- **Weather & math symbols (`U+2103` `℃`, `U+2109` `℉`, `U+2212` `−`)**
- **Arrows (`U+2190`–`U+2199`)** — 8 wind/trend arrows (`← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙`)
- **Vulgar fractions (`U+2150`–`U+215E`)**

All OpenType layout features and their substitution glyph closures are preserved in core subsets.

### Full Build (`dist/fonts/full/`)

Ships complete variable WOFF2 builds covering every exported glyph from the UFO masters (Sans: 2,853 codepoints; Serif: 937 codepoints; Mono: 1,609 codepoints; Rounded: 108 codepoints).

---

## CSS & Web Usage

```css
@font-face {
  font-family: "Strata Sans";
  src: url("/fonts/StrataSans.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Strata Sans Rounded";
  src: url("/fonts/StrataSansRounded.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Strata Serif";
  src: url("/fonts/StrataSerif.woff2") format("woff2");
  font-weight: 200 900;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Strata Mono";
  src: url("/fonts/StrataMono.woff2") format("woff2");
  font-weight: 300 700;
  font-style: normal;
  font-display: swap;
}

:root {
  --font-sans: "Strata Sans", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --font-numeric: "Strata Sans Rounded", "Strata Sans", ui-rounded, system-ui, sans-serif;
  --font-headline: "Strata Serif", ui-serif, Georgia, Cambria, serif;
  --font-mono: "Strata Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* Keep automatic optical sizing on so opsz tracks rendered font-size. */
body {
  font-family: var(--font-sans);
  font-optical-sizing: auto;
}

/* Hero readings: proportional figures (tabular is already default everywhere else). */
.hero-temperature {
  font-family: var(--font-numeric);
  font-variant-numeric: proportional-nums;
  font-optical-sizing: auto;
}

/* Code blocks: set weight 400 explicitly (Mono's axis default is 300). */
code, pre {
  font-family: var(--font-mono);
  font-weight: 400;
}

/* Optional: opt-in coding ligatures in Strata Mono. */
code.ligatures {
  font-feature-settings: "dlig" 1, "ss11" 1;
}
```

> [!IMPORTANT]
> **Strata-Weather adoption gate:** `strata-weather/DESIGN.md` currently mandates SF Pro, SF Rounded, and New York with no monospace face. Do not wire these fonts into `strata-weather` until the owner approves the `DESIGN.md` revision.

---

## Verification & Attribution

FontBakery universal results for `27.0.0.0` (`make gate CAND=r12-type`, network skipped):

| Face | Pass | Warn | Fail | Error | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| **Strata Sans** | 95 | 4 | 3 | 0 | Remaining FAILs are inherited upstream outlines/unhinted `prep` only (`nested_components`, `transformed_components`, `smart_dropout`). |
| **Strata Sans Rounded** | 100 | 0 | 1 | 0 | Remaining FAIL is unhinted `prep` only (`smart_dropout`). |
| **Strata Serif** | 98 | 5 | 2 | 0 | Remaining FAILs are inherited `nested_components` and unhinted `prep` (`smart_dropout`). |
| **Strata Mono** | 92 | 6 | 4 | 0 | Remaining FAILs are inherited upstream script tags (`zinh`/`zyyy`), components, and `smart_dropout`. |

When distributing any compiled binary, bundle the verbatim notices in [`dist/licenses/`](../dist/licenses/) (`sans-LICENSE.txt`, `serif-sources-LICENSE.md`, `mono-LICENSE`, and `*-{COPYRIGHT,OFL}.txt`).
