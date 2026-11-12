# Strata type and icon system: design brief

Working family name: **Strata** (rename is cheap until release). Consumer: the
Strata-Weather app, which takes built WOFF2 and SVG/React output from this repo.

## The four deliverables

| Deliverable | Fork base (licence) | Direction |
| --- | --- | --- |
| **Strata Sans** | Inter 4.x (OFL 1.1, RFN "Inter") | Interface reading face. Traits to reach toward, by eye only: SF Pro's optical sizing (text sizes open and loose, display sizes tight and finer), calm neutral grotesque shapes, excellent numerals. A **Rounded** style for standalone numbers (the role SF Rounded plays today). Noto merged in later for script coverage. |
| **Strata Serif** | Source Serif 4 (OFL 1.1, RFN "Source") | Answer line and headline face. Traits to reach toward, by eye only: New York's optical sizing and crisp, contemporary display serif. |
| **Strata Mono** | Fira Code (OFL 1.1; rename regardless) | Code and data face, shipped also as a Nerd Font build. Keep Fira's ligatures and legibility; reach toward Berkeley Mono's precise, squared, technical character, by eye only. |
| **Strata Icons** | Lucide (ISC) and Hugeicons free stroke-rounded (MIT) | One complete library: every UI icon the app uses plus a full weather set (every condition the app shows, day and night, intensities, wind, alerts, UV, air quality, tides, moon phases). 24 px grid, round caps and joins, Lucide's clarity with Hugeicons' softer rounded geometry. Traits to reach toward from SF Symbols, by eye only: weights that match the text weights, optical balance between symbols, and layered weather symbols whose parts (cloud, sun, rain) can take separate tones. Monochrome by default (`currentColor`), with an optional toned weather variant. |

## System rules (all four)

- **One family.** The three faces share vertical metrics, x-height and cap-height
  relationships, weight steps and numeral design so they mix on one line. Icon
  stroke weights track the sans weights at 16, 20 and 24 px.
- **Weather text is first-class:** tabular and proportional figures, degree sign,
  ℉ and ℃, a true minus, fractions, arrows, superscripts, and unit setting such as
  "30.16 inHg", "12 mph", "−3°".
- **Legibility at the smallest size** (11–13 px) on light, dark, sky, glass and
  map backgrounds beats display beauty.
- Sentence case everywhere; nothing depends on uppercase.

## Licence hygiene (hard rules)

- Never copy, trace, import, export or decompile SF Pro, SF Rounded, New York,
  SF Symbols or Berkeley Mono outlines or files. Never export SVGs from the
  SF Symbols app. They may appear only as **rendered reference images**
  for review, produced from fonts already installed on this Mac.
- Never use Hugeicons Pro. Free stroke-rounded set only.
- Every fork is renamed in all name-table records and file names, keeps its
  upstream copyright lines, and ships under the OFL 1.1. Icon output keeps the
  ISC and MIT notices.

## Out of scope until a later round

Noto coverage merge, the Nerd Font patch, hinting for Windows, and wiring the
fonts and icons into Strata-Weather (which also needs a DESIGN.md revision by
the owner).
