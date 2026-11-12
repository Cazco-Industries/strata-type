# lumen-146 design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1.

## Strata Sans

The aim is a calmer, more engineered interface sans whose figures carry
weather data well: open and even at text sizes, tight at display sizes.

**Identity**

- **Capital G has a spur by default.** The spurred and spurless G were already
  drawn as pairs; their contents are swapped, so the spurred form is default
  and `cv10` now gives the spurless one. The spur makes G firmer and less
  geometric-round at display sizes, and separates it from C and O at text
  sizes.
- **The t has a slanted top.** On the shared t part, the top-left corner
  drops by 0.35 of a stem and the top-right corner rises by 0.08 of a stem.
  This turns a flat-cut t into a drawn one and gives text a little more
  rhythm.
- **The display Regular is a touch finer.** The opsz 32 Regular master moves
  5% toward the opsz 32 Thin master, so large text gets the lighter, crisper
  colour of a display cut.

**Spacing (optical size)**

- At opsz 14 (text) each side gains 6 units. At opsz 32 (display) each side
  loses 10 units. Text opens up and headlines close up, and the axis
  interpolates between them.
- Period, comma, colon and semicolon keep their spacing at display size, so
  "30.16" and "3:45" don't jam when headlines tighten.
- Marks, zero-width glyphs and the fixed-width spaces are not tracked.
  Composites built from side-by-side parts (℃, ℉, IJ, Lj and so on) move each
  part, so their internal spacing follows the tracking.

**Figures**

- The round figures are widened while keeping stem weight: zero 4%, six and
  nine 3.5%, eight 3%, three 2.5%, five and two 2%. This compensates for their
  narrow, oval look next to the straight figures. Scaling is stem-compensated
  between master pairs, so stems keep their thickness.
- **Tabular figures (`tnum`)** share a single cell, the widened tabular zero
  (0.654 em). The tabular one has no foot. Instead its flag is lengthened 35%
  along its own outer edge and the glyph is centred on its area centroid, so
  "10", "11" and "21:11" fill their cells instead of leaving a thin stroke
  floating in a gap. The figure space equals the tabular cell, and the
  punctuation space equals the tabular period.
- **Math signs sit on the figures.** Plus, minus, equals, times, divide,
  plus-minus, less, greater, less-or-equal, greater-or-equal, not-equal,
  almost-equal and logical-not are raised to the figure centre (where the
  capital-height forms used to be) and centred in the tabular cell. Their
  default, capital and tabular forms are now identical. The minus is figure
  width and centred on figures, so "−3°" balances and minus signs align in
  columns.
- **New degree sign.** A true ring, drawn from two ellipses per master. Its
  diameter grows with weight (520 + 140 × weight fraction units, 14 smaller
  at display), its top and bottom are slightly thinner than its sides, and
  its top sits on the figure top. The right sidebearing is generous, so
  "72°" ends cleanly and "104°F" doesn't crowd at display sizes.
- ℃ and ℉ are composed from the degree sign and C or F, 40 units closer than
  plain spacing.

**Coverage and metrics**

- The soft hyphen (U+00AD) is mapped to the hyphen. Core coverage is now
  258/258.
- The line metrics are written explicitly (typo and hhea 0.969 / −0.241 em,
  no gap) and the win values cover the outlines of every master. This fixes
  the baseline's win-metric failure.
- Upstream product names left in the designspace are replaced.

## Strata Sans Rounded (numeric style)

- Glyphs: figures (tabular by default, with proportional figures under
  `pnum`), space, figure space, punctuation space, thin space, period,
  colon, comma (with proportional forms), percent, degree, ℃, ℉, minus,
  plus, hyphen, plus-minus, slash, fraction, C and F.
- **How it is made.** `transforms/rounded.py` takes the sans Thin, Regular and
  Black text masters, decomposes each glyph, and classifies every corner once,
  on the Regular master: convex or concave, plus stroke ends (a short straight
  between two convex corners, at most 1.7 stems long). Then, in every master:
  - Convex corners get a circular fillet of 0.46 × that master's stem.
  - Concave corners get 0.14 × stem.
  - Stroke ends become full semicircles.

  The fillet uses the corner's true tangents. Its cut length is
  r·tan(θ/2), its handles are (4/3)·tan(θ/4)·r, and cuts are capped so
  neighbouring corners never cross. Every master gets the same edits, so the
  masters stay compatible.
- It has its own designspace in `fonts/sans-rounded/`, with the same weight
  axis map and the same named weights (Thin to Black) as the sans. The main
  build takes one designspace per face folder, so this style is compiled by
  `transforms/build_rounded.py` to `build/lumen-146/rounded/`
  (StrataSansRounded.ttf and .woff2), with the same naming and licence
  handling as the main build. The standard render sheets do not show it.
  Review it on the self-review pages (see below).

## Strata Serif

- **Matched to the sans cap height.** The whole design (outlines, kerning,
  anchors, mark positions, BASE values and font info) is scaled by 1.09.
  The cap height becomes 0.730 em (sans 0.728) and the x-height 0.518 em,
  a natural serif proportion under the sans's 0.546. Outline points keep two
  decimals, because integer rounding after a scale bends smooth points and
  showed up as new interpolation kinks.
- **Shared line metrics.** The typo and hhea values match the sans, the
  USE_TYPO_METRICS flag is now set, and the win values cover all masters.
  This face's features file carries its own OS/2 block, which overrides the
  UFO info at compile time, so the transform rewrites that block too (x-height,
  cap height, typo and win values).
- **Weight steps aligned by ink colour.** Each user weight is remapped so the
  serif is as dark, relative to Strata Sans at the same weight, as Regular is.
  Darkness is the ink area per em² of a lowercase sample, measured on
  outlines interpolated at each candidate location and solved by bisection.
  Matching stem width alone would leave a contrasted serif pale at Bold,
  because its thin strokes add little ink. New map: 300→249, 500→508,
  600→618, 700→724, 800→848 (baseline 700→823). Named instances move with the
  map, so they keep their user weights.
- **New glyphs:**
  - En and em quads (U+2000, U+2001) and the punctuation space (U+2008).
  - Non-breaking hyphen.
  - High reversed-9 quote, drawn as a turned outline (no flipped components).
  - ℃ and ℉.
  - Vulgar fractions ⅐ ⅑ ⅒ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚, built and spaced like the existing
    fractions in each master.
  - ↔ and ↕, built from each master's own right-arrow head. The double arrow
    holds two full heads plus a shaft of at least 0.6 of a head, and the
    shaft keeps the tail thickness at the middle.

  Core coverage is now 258/258 (baseline 240).
- Upstream product names left in the features are removed: the trademark
  record (it names a reserved font name), the PostScript-name comment and a
  class name.

## Strata Mono

- **Interpolation fixed.** The Bold master listed the parts of five
  bar-bar ligature glyphs right to left. They are now in the Light master's
  order, which clears all five baseline interpolation findings.
- **Squarer and more precise.** Every curve's handles are pushed 20% further
  toward their corner (only where both handles point at the tangent
  intersection). Bowls, the o and the counters become squarer
  (superellipse-like) without changing structure. All ligatures and
  contextual features are untouched and shape as before.
- **Matched x-height.** Scaled by 1.0138 so the x-height equals the sans
  (0.546 em). The cell grows from 1200 to 1217 units.
- **Weight steps aligned by stem.** Mono is monoline, so stems are the right
  measure. The Bold master is re-mixed (73% of the way from Light to the old
  Bold), so 700 matches the sans Bold at the same Light-to-sans ratio. The
  axis map and instance locations follow.
- **New glyphs:**
  - The remaining spaces (U+2000–2006, 2009, 200A, 202F) at cell width.
  - Hyphen (U+2010) and non-breaking hyphen.
  - High reversed-9 quote.
  - Prime and double prime: the straight quote leaned like a slash.
  - Superscript i, sized and placed like the superior figures, with
    stem-compensated scaling.
  - ℃ and ℉ fitted into one cell: a small ring plus a narrowed C or F.
  - ⅐ ⅑ ⅒.

  Core coverage is now 258/258 (baseline 237).
- Shared line metrics and win values, as for the other faces. This fixes the
  baseline's win-metric failure.

## Icons

- **Stroke 1.75 → 1.9.** At 13–17 px that is 1.03–1.35 px, just under a
  Strata Sans Regular stem (1.2–1.6 px), so icons stop reading thin and grey
  next to labels while counters stay open. All geometry rules (live area,
  keylines, 3.0-unit clearance) still hold. The visible gap between parallel
  strokes is now 1.1 units.
- **Plain layer groups.** The icon contract allows no custom attributes, so
  the weather layer groups are plain `<g>`. The group order is written to
  `icon-layers.json` beside the icon folder, so a renderer can still tint
  layers by name.

## Gate versus baseline

Universal-profile counts are pass / warn / fail / error.

| Face | Baseline | This candidate | Core coverage | Interpolation findings |
| --- | --- | --- | --- | --- |
| Sans | 91 / 4 / 6 / 1 | 91 / 5 / 5 / 1 | 257 → 258 | none, as baseline |
| Serif | 94 / 5 / 6 / 0 | 95 / 5 / 5 / 0 | 240 → 258 | 5 kinks, the same 5 as baseline |
| Mono | 88 / 7 / 6 / 1 | 90 / 6 / 5 / 1 | 237 → 258 | 5 → 0 |

- Fixed: the sans and mono win-metric failures, the serif empty-records
  failure and the mono interpolation findings.
- The sans gains one warning: the soft hyphen now in the core set.
- No hard failures and no reserved font names in any binary, including
  Strata Sans Rounded.
- Icons pass: 28 icons at stroke 1.9, and the TSX typecheck passes.
- The remaining failures and errors are upstream structure, listed under
  next steps.

## Rules to keep

- Make every outline change as a transform from the baseline. Re-run
  `apply.py`; never patch a built UFO.
- Classify once and apply the same plan to every master (corners on Regular
  for Rounded; flag points, figure moves and spacing per glyph). Masters must
  stay compatible: the interpolation check must not gain findings.
- Scale with sub-unit precision, and let the compiler round once.
- Write flipped or rotated constructions as outlines, never as transformed
  components.
- The tabular cell is the tabular zero's width. Figure space, math signs and
  the tabular forms of every figure-related glyph use it. The minus is figure
  width and centred on the figures.
- Separators (. , : ;) are never tightened at display size.
- Line metrics are shared across faces: typo and hhea 0.96875 / −0.24121 em,
  gap 0, USE_TYPO_METRICS on, win from the real outline extremes. In the
  serif, change the features' OS/2 block along with the info.
- Align serif weights by ink colour and mono weights by stem, both relative to
  the sans at Regular. Named instances move with the map.
- Rounded radii: 0.46 stem convex, 0.14 stem concave, stroke ends ≤ 1.7 stems
  become semicircles.
- Icons: one 1.9 stroke, no custom attributes, layer order recorded in the
  manifest.

## Next steps

1. Let the build take a second designspace per face (or a `rounded` face) so
   Rounded is built, gated and rendered with the others. Then extend it with
   the letters weather units need (mph, km/h, inHg, hPa, AM/PM).
2. At 17 px, the sans figures set about 5% wider than the system reference.
   The next figure lever is a narrower tabular cell with matching
   proportional figures, which would also need a fresh look at the widened
   zero.
3. Mono figures stand at 0.734 em against the sans's 0.747. A small figure
   lift in mono would align numbers when the faces mix.
4. Optical sizes: the serif scale is uniform across its optical masters.
   Check the caption and display cuts against the sans at the sizes they
   would actually be used.
5. The remaining universal-profile failures are upstream structure:
   - nested and transformed components
   - smart dropout
   - fvar/STAT consistency
   - name lengths
   - mono script tags

   They need build-pipeline fixes, not outline work.

## Open questions

- Footless tabular 1 (with a long flag) versus the upstream footed one. The
  footless form is calmer and matches the proportional figures. The footed
  one is more explicit in dense tables.
- Bold weights are lighter than the baseline: serif 700 → 724 (was 823) and
  mono Bold re-mixed to 73%. This is deliberate alignment, but a heavier
  serif bold may be wanted for editorial contrast.
- The serif is now 9% larger at the same font size. Layouts that already use
  it will set longer lines.
- Math signs are centred on figures, not on the x-height, so "a < b" in
  lowercase prose sits higher than before.

## Round 0 pipeline handoff

Rounded now lives at `fonts/sans-rounded/` and the standard build, gate and
render commands include it. Earlier supplemental paths and timing tables above
describe designer self-review only. The review set uses the unchanged finished
icon input, preserved in `review-icons/`; the external work folder remains
read-only. Generated font masters are ignored and rebuilt from baseline by
the transforms. No outline design was changed during pipeline integration.

Rebuild from the repo root with the isolated interpreter and resource guard:

    .venv/bin/python -I scripts/resource_guard.py -- .venv/bin/python -I candidates/lumen-146/transforms/apply.py

    make build CAND=lumen-146 SUBSET=core ICONS_DIR=candidates/lumen-146/review-icons
    make gate CAND=lumen-146 ICONS_DIR=candidates/lumen-146/review-icons

Both transform entry points accept `--output-dir` for reproduction in a temporary
directory. The baseline always comes from this checkout.
