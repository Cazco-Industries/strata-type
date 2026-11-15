# r9-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r8-type. Its decisions hold unless a section below
changes them. Four things change: the mono ℉/℃ (ring and letter), the
Rounded corner pen, and the mono operator ligatures, which become opt-in.
Every other glyph keeps r8's outlines in every master and in the built
binaries; `checks/drift.py` proves it (section 5).

All rendered measurements are per glyph and centre-aligned, never a string
xor between fonts.

- Mono values are from a browser render at device scale 2, worst case over
  16 sub-pixel phases (4 horizontal × 4 vertical), at 13, 15, 17 and 24 px
  and weights 300, 400, 500, 600 and 700 (r8's at 13, 15 and 17 px). Each part (ring, letter, follower) is
  drawn from its own part-only copy of the built font set at the same
  position, so a gap is measured between parts, not guessed from a string.
- Rounded values are from the unhinted greyscale rasteriser at 1× and 2×,
  with opsz equal to the size in px (as browsers set it).

Before/after images are in `evidence/`, with numbered callouts explained under
each sheet.

## Summary

| Item | Target | r8 | r9 (built) | Met |
| --- | --- | --- | --- | --- |
| 1. Letter width / mono F, C | ≥ 0.66 | F 0.66–0.77, C 0.70–0.77 | F 0.68–0.81, C 0.67–0.69 | yes |
| 1. C opening / mono C | ≥ 0.85 | 0.96–1.04 | 0.97–1.05 | yes |
| 1. Ring aspect | 0.95–1.05 | 0.86–0.92 | 0.99–1.01 (strip), 0.996–0.997 (file 09) | yes |
| 1. Wall / ° wall | ±10% | — | side 0.93–1.03, top 0.91–1.11 | partly: top 1.108 at 700 / 15 px, one phase of four |
| 1. Ring height / typed ° | 0.70–0.80 | 0.92–0.94 | 0.71–0.75 | yes |
| 1. Ring–letter gap at 13 px | ≥ 1.0 px, no contact | 1.00–1.50 | 1.00 or more, no contact | yes |
| 1. Letter height / mono F, C | 1.00 ± 0.02 | 1.00 | 1.00 | yes |
| 1. Advance | 1217 | 1217 | 1217 | yes |
| 2. Following marks, worst phase | ≥ 0.5 px, aim 1 px, no contact | `℉–` 0.00 (all weights), `℃/` 0.00 (500–700) | no contact; 0.50 px or more everywhere; under 1 px only `℉–` at 700 (0.50) and `℃/` at 400–700 (0.50–0.91) | yes; 1 px aim partly |
| 2. Figures before a unit | ≥ 1 px | 1.00 | 1.00 or more | yes |
| 3. Rounded pixel difference at 24 px | must grow | 91 (400), 179 (700) | 111, 192 | yes |
| 3. Sans Regular | unchanged | — | byte-identical binary | yes |
| 4. Default shaping | one glyph per character | ligatures | 38 chars → 38 cmap glyphs | yes |
| 4. Opt-in | `dlig` + one stylistic set | — | `dlig` and `ss11` "Operator ligatures" | yes |
| 5. Drift | only the intended glyphs | — | PASS against r6 and r8 | yes |

## 1. Mono ℉ and ℃: a round ring, and a letter that reads

**Why.** r8's ring was the degree sign's own contours scaled to 0.93 of its
height but only as wide as the cell allowed. It rendered at an aspect of
0.86–0.92, an oval pressed against the letter. The first r9 build made the
ring round and fitted the letter to what follows it, but the letter came out
too narrow:

- The C was 0.47–0.58 of the mono C. At 500–700 its arms closed up (opening
  0.00–0.09 of the mono C's at 13–17 px), so `22℃` read as `22°(`, also at
  24 px / 400 on render file 09.
- The Bold F was 0.55 of the mono F.

**Order of targets in this revision.** When two conflict, the higher one wins.

1. The letter reads as its letter: width at least 0.66 of the mono F or C,
   and the C's opening (the vertical gap between its arm ends) at least 0.85
   of the mono C's, at 13/15/17/24 px and 300–700.
2. Nothing touches a following mark: 0.5 px or more at the worst phase, aiming
   for 1 px. Figures before a unit keep 1 px.
3. The ring stays round: aspect 0.95–1.05, walls within ±10% of the typed °.
4. Ring outer height 0.70–0.80 of the typed °.
5. Ring–letter gap at least 1.0 px at 13 px, no contact.

**What changed** (`transforms/mono.py`, `TEMP_MODE = 'round2'`, the `round2`
entry of `TEMP_R7`; `round` stays there as the first build):

- The letter's width came from the gap first, then from the ring.
  - **Gap.** 1.40 px at 13 px in Light and 1.35 px in Bold (design), down
    from 1.65. Rendered, the worst phase at 13 px is 1.00 px.
  - **Ring.** 0.74 of the degree sign's height in Light and 0.705 in Bold
    (was 0.80 and 0.77). It is still as wide as it is tall.
  - **Walls.** 0.95 of the degree sign's walls. In Bold the top and bottom
    walls are 0.87: a ring this small renders its top wall heavier at
    13–15 px (a 0.95 top wall measured up to 1.13). `WALL` now takes
    `{'side': .., 'top': ..}`.
  - **Placement.** Unchanged: Light on the cell's left edge, Bold 0.01 of a
    cell inside it.
- **Letter.** Still the face's finished F or C at full cap height, condensed
  in x and emboldened back to its own stem. The fits to what follows are now
  set per letter (section 2). The C's terminal cuts stay vertical (`SQUARE`).
- **The C's terminals were not redrawn.** At 0.67 of the mono C or more, the
  condensed C keeps the mono C's full opening (0.97–1.05), so its shape needed
  no change. Its arms are shorter than the mono C's. It reads as a narrow C,
  not a bracket (`evidence/item1-c-paren.png`).
- **No fallback was needed.** Gap, ring height and aspect all stayed inside
  their targets. None of the permitted fallbacks (gap 0.75 px, ring 0.66,
  aspect 0.92) was used.
- **Advance.** Still 1217 (one cell), with left side bearing 0.

**Measured, render file 09** (sheet 03 light, the `℉ / °F  ℃ / °C` units
row, 24 px, Regular, device scale 2, ink normalised to the text colour):

| Unit | Aspect | Ring / typed ° height | Wall / ° wall (side; top) | Letter height / mono letter | Letter width / mono letter | C opening / mono C | Ring–letter gap |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| ℉ | 0.997 | 0.737 | 0.948; 0.973 | 1.000 | 0.767 | — | 2.00 px |
| ℃ | 0.996 | 0.736 | 0.953; 0.972 | 0.998 | 0.681 | 0.990 | 2.05 px |

First r9 on the same row: letter width 0.608 (F) and 0.543 (C), C opening
1.013, ring 0.80 of the °, gap 2.50 px.

**Measured, letter** (13/15/17/24 px strip, weights 300–700, 16 phases,
range over sizes and phases; r8 at 13/15/17 px):

| Weight | F width, r8 | F, first r9 | **F, r9** | C width, r8 | C, first r9 | **C, r9** | C opening, r8 | C opening, first r9 | **C opening, r9** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300 | 0.75–0.77 | 0.63–0.65 | **0.80–0.81** | 0.77 | 0.57–0.58 | **0.68–0.69** | 0.99–1.03 | 0.98–1.03 | **0.98–1.03** |
| 400 | 0.73–0.74 | 0.60–0.62 | **0.76–0.77** | 0.75 | 0.54–0.55 | **0.68** | 0.97–1.04 | 0.90–1.04 | **0.99–1.04** |
| 500 | 0.70–0.71 | 0.58–0.59 | **0.73–0.74** | 0.73–0.74 | 0.51–0.52 | **0.67–0.68** | 0.98–1.03 | 0.09–1.05 | **0.99–1.04** |
| 600 | 0.68–0.69 | 0.56–0.57 | **0.70–0.71** | 0.71–0.72 | 0.49 | **0.67–0.68** | 0.96–1.04 | 0.00–1.05 | **0.97–1.05** |
| 700 | 0.66–0.67 | 0.55 | **0.68–0.69** | 0.70–0.71 | 0.47 | **0.67** | 0.96–1.04 | 0.00–1.03 | **0.98–1.05** |

Letter height is 1.00 of the mono F and C in every row.

**Measured, ring** (same strip, both units, all weights):

| Size | Aspect | Ring / typed ° height | Side wall / ° | Top wall / ° |
| ---: | ---: | ---: | ---: | ---: |
| 13 | 0.99–1.01 | 0.71–0.75 | 0.95–1.03 | 0.91–1.10 |
| 15 | 0.99–1.00 | 0.71–0.75 | 0.95–0.99 | 0.95–**1.11** |
| 17 | 0.99–1.01 | 0.71–0.75 | 0.94–0.97 | 0.94–1.07 |
| 24 | 0.99–1.01 | 0.71–0.75 | 0.93–0.97 | 0.94–0.99 |

- The counter is open in all 320 rows.
- **One miss.** The top wall reads 1.108 at 700 / 15 px at one of the four
  horizontal phases (4 of 320 rows). Every other row is 0.91–1.10.
  - Thinning the Bold top wall from 0.885 to 0.87 moved that row only from
    1.113 to 1.108, and moved 600 / 13 px from 0.924 to 0.914.
  - Going further would push 600 / 13 px under 0.90. The Bold counter is
    about 1.4 px tall at 15 px, so this measure swings ±0.08 with phase.
- **Ring–letter gap.** 1.00 px at the worst phase at 13 px for both letters
  at every weight; 1.00–2.50 px over 13–24 px. No contact (first r9:
  1.30–2.00 px; r8: 1.00–1.50 px).

## 2. What follows a unit

**Why.** r8's letter overhung the next cell by a fixed share of a cell
(0.07 in Light, 0.10 in Bold), whatever followed it. At 13 px it touched an
en dash after ℉ and a slash after ℃ (0.00 px at 500–700).

**What changed.** The letter's width comes from its overhang, not from the
ring. Each letter is fitted to an en dash and a slash set in the next cell,
and its overhang past the cell's right edge is capped (0.12 of a cell for
the F, 0.10 for the C). The tighter limit sets the width. In this revision
the fits are set per letter, chosen so that the letter keeps its floor
(section 1) first:

| Master | F to dash | F to slash | C to dash and slash |
| --- | ---: | ---: | ---: |
| Light | 1.40 px | 1.40 px | 1.45 px |
| Bold | 1.00 px | 1.10 px | 0.85 px |

(px at 13 px, design; the first r9 build used 1.40 / 1.50 px in Light and
0.75 / 1.35 px in Bold for both letters.)

- **The F.** Its middle arm gives way to the dash alone, so the top bar keeps
  the F's width.
  - The arm keeps at least 0.55 of the top bar in Light and 0.50 in Bold
    (was 0.55), each measured from the stem.
  - With 0.55 in Bold, a 1 px fit to the dash left the F at 0.62 of the mono
    F. With 0.50 it is 0.68 at the same fit.
- **The C** is fitted whole, because its lower terminal meets a slash's
  foot. The Bold C sets the limit: its 0.85 px fit keeps it at 0.67 of the
  mono C, and a 1 px fit would take it under 0.66. So `℃/` keeps 0.50–0.91 px
  at 400–700 rather than 1 px; the floor wins.

**Measured** (worst phase over 16, at 13, 15, 17 and 24 px; the smallest
value is at 13 px in every row; px):

| Weight | `℉–` | `℉/` | `℃–` | `℃/` | `℉,` | `℃.` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 300 | 1.08 | 3.53 | 3.14 | 1.08 | 4.91 | 3.00 |
| 400 | 1.00 | 3.04 | 2.66 | **0.91** | 4.50 | 3.00 |
| 500 | 1.00 | 2.66 | 2.19 | **0.62** | 3.97 | 2.50 |
| 600 | 1.00 | 2.19 | 2.19 | **0.62** | 3.97 | 2.50 |
| 700 | **0.50** | 2.05 | 2.00 | **0.50** | 3.53 | 2.50 |

- No contact at any size, weight or phase, and 0.50 px or more everywhere.
- r8 touched: `℉–` 0.00 at every weight, `℃/` 0.00 at 500–700. The first r9
  had `℉–` at 0.50 px at 500–700 and `℃/` at 1.00 px or more.
- The 1 px aim is not met in two places:
  - `℉–` at 700: 0.50 px at 13 px, 1.00 px from 15 px up.
  - `℃/` at 400–700: 0.50–0.91 px, again at 13 px.
- Figures before a unit keep their space: `0℉`, `0℃`, `7℉` and `7℃` 1.00 px
  or more, `4℉` and `4℃` 2.70 px or more.

## 3. Rounded at 24 px

**Why the r8 Rounded read as the sans at 24 px.** r6–r8 used one pen at
every optical size: outer corners 1.70 stems in Regular and 0.60 in Black,
joins 0.70 and 0.20. In the strip `3 PM 72°F mph inHg 18:30 AQI 41`, almost
every stroke end is 1.43 stems wide or less. Under `TERMINAL` (1.60 stems),
such an end is already a full semicircle, so its radius is half the stroke
and can't grow without thickening the stroke. Only the outer corners (the
F's and P's top left, the E/L/B/R corners, the 7's bar, the flat-top 3's bar
end and the 4's bar) can take a bigger radius.

**What changed** (`transforms/rounded.py`, constants block; `lib.py`
accepts the new radius):

- **Pen per optical size.**
  - The text masters (opsz 14) carry the skeleton gate, which allows only a
    little more rounding: outer corners go from 1.70 to 1.73 stems in
    Regular and from 0.60 to 0.80 in Black, with Thin at 2.00.
  - The display masters (opsz 32) take a much larger pen: outer corners 3.00
    stems in Thin and Regular and 1.40 in Black, reaching up to 3.40 and
    1.80 stems along each side.
  - 24 px text renders at opsz 24, 0.56 of the way to the display masters.
    At 48 px only the display pen applies.
  - The caption masters (opsz 8) follow the text pen.
- **A concentric turn.** A concave corner that faces an outer corner (the
  inside of the F's, P's, E's, L's and B's turns) is now a *turn*. Its radius
  is the outer radius less one stem, so the stroke keeps its width round the
  corner: 0.73 stems in Regular text, 2.00 in Regular display. Any other
  concave corner is a *join* and keeps r8's radius: the H's bar, the F's and
  E's middle arms, and the K's and R's legs.
  - Joins can't take the concentric radius. At 2.0 stems in the display
    masters, it webbed the H's bar and the F's middle arm at 48 px.
  - The turn test: an outer corner that is not a stroke end lies within
    2.5 stems of the concave corner, within 25° of that outer corner's
    bisector.
  - With the turn radius set equal to the join radius, the code gives r8's
    outlines exactly.
- **Limits found by trial** (lab builds, measured with the skeleton gate):
  - Regular text 1.76 puts the G at 4.00, which fails.
  - Black text 0.95 puts the G at 5.45.
  - Display Black with a 2.2-stem reach used up the P's, B's and R's top
    lines. Line ends are planned once for all masters, so the text masters
    lost those lines too (region 5.5).

Advances, kerning, groups, features and the flat-top 3's drawing are
unchanged (asserted when the masters are written). The sans is not touched:
its binaries are byte-identical to r8's and r6's.

**Glyphs touched** (24): B E F G K L P R bracketleft bracketleft.case
bracketright bracketright.case degreefarenheit e five five.pnum g k
onequarter seven seven.pnum three three.pnum threequarters. Not every glyph
changes in every master (`evidence/changed-glyphs.txt`).

**Measured** (the strip, Rounded against the sans, each glyph drawn alone and
centred on its own ink box; difference = pixels whose coverage differs by at
least 25%; r8's Rounded binary is byte-identical to r6's):

| Render | Size / weight | r6 total | r9 total |
| --- | --- | ---: | ---: |
| 1× | 24 / 400 | 91 | **111** |
| 1× | 24 / 700 | 179 | **192** |
| 1× | 48 / 400 | 688 | 803 |
| 1× | 48 / 700 | 910 | 999 |
| 2× | 24 / 400 | 558 | 600 |
| 2× | 24 / 700 | 793 | 845 |
| 2× | 48 / 400 | 2558 | 2842 |
| 2× | 48 / 700 | 3221 | 3478 |

Per glyph, 1×, 24 px, in strip order (r9 changes in bold; every other
glyph is equal at r6 and r9):

| Weight | Version | 3 | P | M | 7 | 2 | ° | F | m | p | h | i | n | H | g | 1 | 8 | : | 3 | 0 | A | Q | I | 4 | 1 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 400 | r6 | 17 | 6 | 2 | 4 | 2 | 0 | 6 | 0 | 0 | 0 | 0 | 1 | 6 | 2 | 1 | 0 | 0 | 17 | 21 | 4 | 1 | 0 | 0 | 1 |
| 400 | r9 | **21** | **12** | 2 | 4 | 2 | 0 | **12** | 0 | 0 | 0 | 0 | 1 | 6 | 2 | 1 | 0 | 0 | **21** | 21 | 4 | 1 | 0 | 0 | 1 |
| 700 | r6 | 17 | 6 | 20 | 6 | 6 | 0 | 9 | 10 | 4 | 5 | 4 | 7 | 12 | 3 | 5 | 6 | 0 | 17 | 19 | 8 | 2 | 0 | 8 | 5 |
| 700 | r9 | 17 | **10** | 20 | **7** | 6 | 0 | **17** | 10 | 4 | 5 | 4 | 7 | 12 | 3 | 5 | 6 | 0 | 17 | 19 | 8 | 2 | 0 | 8 | 5 |

At 700 the 3's count stays 17, but its summed difference grows (12.63 →
13.38 px).

Corner radius in rendered px (8× supersampled; the distance along the
corner's diagonal from the sans corner to the Rounded edge at half coverage,
less the same for the sans, divided by √2 − 1):

| Size / weight | F top left, r6 → r9 | P top left, r6 → r9 |
| --- | --- | --- |
| 24 / 400 | 3.49 → 4.82 | 3.48 → 4.11 |
| 24 / 700 | 2.90 → 4.79 | 2.88 → 4.15 |
| 48 / 400 | 6.49 → 11.10 | 6.49 → 8.58 |
| 48 / 700 | 5.70 → 11.51 | 5.70 → 9.26 |

- Terminal radius is unchanged by design: every stroke end in the strip is a
  full semicircle in r6 and r9, radius half the stroke (0.99, 1.63, 1.88 and
  3.07 px at 24/400, 24/700, 48/400 and 48/700).
- The 7's bar-to-diagonal corner is not a right angle, so the method above
  doesn't apply to it (it reads 1.83 → 1.69 and 3.43 → 2.66 at 400, and
  2.47 → 2.72 and 4.76 → 5.14 at 700). Its fillet grows along the bar only,
  because the diagonal side ends at a point of the diagonal. It reads longer
  and flatter, not rounder.

**Honest reading.** At 48 px the Rounded is clearly distinct (F, P, E, B, 7
and the 3's bar). At 24 px the difference grows (91 → 111, 179 → 192) but
stays small at a glance, because the strip is mostly stroke ends that were
already round, and the text pen is held by the skeleton gate.

**Flaw found.** In display Regular (m03), the 7's fillet handle (at 1249,
1515) passes the corner, so the ink rises 1.2 units above the cap line
(1490). The brackets in m03 bulge 1.4 units past their stem edge. In other
masters the right-hand ink moves at most 4 units. This is under 0.1 px at
140 px and the kink checks pass, but the handle should be clamped (Next
steps).

## 4. Mono ligatures opt-in

**What changed** (`transforms/mono.py`, `opt_in_ligatures`). r8 set the
operator ligatures in `calt`, which is on by default, so `===` or `->` in
code changed shape unasked.

- Every lookup of the ligature family moves out of `calt`:
  - the two- to four-character ligatures (rules that set `.spacer` and
    `.liga` glyphs: `=== !== == != <= >= ++ && :: ...` and the rest);
  - the open-length sequences (`=> ==> <== -> --> <--`, `###`, `___`).
- They move into `dlig` and into stylistic set **`ss11`, named "Operator
  ligatures"** (a `featureNames` UI name in the binary, name ID 266).
  - Both features reference the same lookups in the same order, so either
    one gives r8's ligatures exactly.
  - The glyphs are as drawn.
- `calt` keeps only the contextual forms that leave one glyph per character:
  - the `&&` pair form that `ss03` needs;
  - colons centred between `<` and `>`;
  - the x in `0xFF`;
  - lowered operators between lowercase letters;
  - the raised colon between capitals;
  - the Greek capitals;
  - the two- and three-em dashes.
- Every lookup is still defined once, where the calt block stood, so the
  lookup list and its order are r8's. Only the feature records change.
- `aalt` collects `dlig` right after `calt`, so its alternate sets are r8's.

**Measured on the built binary** (`build/r9-type/StrataMono.ttf`, the
shaper, string `a === b !== c => d <= e >= f != g -> h`, 38 characters):

| Features | Glyphs | Glyphs equal to the cmap glyph |
| --- | ---: | ---: |
| default | 38 | 38 (one glyph per character) |
| `calt` off | 38 | 38 |
| `dlig` on | 38 | 22 (`equal_equal_equal.liga`, `exclam_equal_equal.liga`, `less_equal.liga`, `equal_start.seq` …) |
| `ss11` on | 38 | 22 (same glyphs as `dlig`) |

- GSUB: 352 lookups in r8 and r9. Feature lookups: `calt` 97 → 9, `dlig`
  0 → 88, `ss11` 0 → 88, `aalt` 2 → 2. `calt` and `dlig` share no lookup;
  `dlig` and `ss11` reference the same 88.
- cmap and hmtx: U+2103 → `uni2103`, U+2109 → `uni2109`, `degree`, `F`, `C`,
  all advance 1217.
- Code specimen sheets (render files 18 and 19, light and dark) show every
  operator as separate characters; `&&` keeps its `calt` pair form. In a
  browser, `font-feature-settings: 'dlig' 1` or `'ss11' 1` brings the
  ligatures back (`evidence/item4-ligatures.png`).

## 5. Everything else

`checks/drift.py` compares every master's glyph records and the built TTF
and WOFF2 (default glyf, hmtx, every gvar tuple by region, and cmap, GSUB,
GPOS, fvar, avar, STAT, HVAR and name whole). Its intended list is exactly:

- mono masters m00 and m01: `uni2103` and `uni2109` (items 1–2), plus the
  `features.fea` files (item 4);
- Rounded masters m00–m08: the 24 glyphs listed in section 3;
- serif masters m00–m02 (opsz 8): any glyph, the small-opsz regions r8
  changed.

Output against r6 (`--list evidence/changed-glyphs.txt`): **PASS**.

- Sans: 0 of 2985 in every master; binaries identical.
- Rounded: 21–23 of 141 per master, all inside the list; built TTF glyf 21,
  gvar 24 glyphs, hmtx 0, no whole table changed.
- Serif: m00–m02 629 of 1509 each (r8's change), m03–m05 0; built default
  glyf 0, hmtx 0, gvar only in the opsz −1 regions.
- Mono: m00 and m01 `uni2103` and `uni2109`; built glyf 2, gvar 2, hmtx 0;
  GSUB and name differ whole (item 4 and the `ss11` UI name).

Output against r8 (`--ref r8-type`): **PASS**, with nothing outside the
list. Sans and serif sources and binaries are identical to r8's; Rounded
and mono differ only as above.

## Checks

**Gate** (`make gate`): hard failures 0. Quality status reads FAIL, as in r6
and r8, because the baseline's upstream font-check findings are preserved;
every count is r8's.

| Face | Pass | Warn | Fail | Error | Core present | Interpolation glyphs | WOFF2 bytes (r8) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Strata Sans | 92 | 4 | 5 | 1 | 258/258 | 0 | 108328 (108328) |
| Strata Serif | 95 | 5 | 5 | 0 | 258/258 | 3 | 197980 (197980) |
| Strata Mono | 90 | 6 | 5 | 1 | 258/258 | 0 | 47980 (47748) |
| Strata Sans Rounded | 98 | 0 | 2 | 1 | 29/29 | 0 | 74736 (74012) |

- Name/RFN PASS on all four faces; no reserved names in any name record.
- Interpolation findings: serif `{'kink': 4}` (r8's), all others none.
- Tabular figures equal width on all faces; icons PASS (71, one stroke
  width, TSX typecheck PASS).

**Variable-font kinks** (`checks/vfkinks.py`): 5 findings, all in the serif
ff ligatures, Thin to Black at opsz 8, as in r8. Sans, Mono and Rounded 0.
Rounded interpolation test PASS. No new interpolation findings.

**Render** (`make render`, 38 sheets): blind byte scan PASS. Headline line
contact clear on light, dark and glass (0 contacts on each).

**Review checks** (`make checks`): PASS.

- Rounded / Regular ink width (96 px, 400, limit 1%): 104°F, 72°, 18:30
  and −3° all +0.000%.
- Default cmap and shaped figures tabular at every location: sans 21, mono
  5, Rounded 15 PASS; serif INFO (tabular, 30 locations), as in r8.

**Confusables** (`checks/figcheck.py`, xor/union, fail under 0.20, Regular,
default features): PASS.

| Face | px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.680 | 0.379 | 0.545 | 0.496 | 0.679 | 0.619 | 0.652 | 0.499 | 0.642 |
| Sans | 11 | 0.713 | 0.376 | 0.577 | 0.550 | 0.726 | 0.649 | 0.658 | 0.467 | 0.643 |
| Sans | 13 | 0.735 | 0.407 | 0.595 | 0.541 | 0.738 | 0.655 | 0.519 | 0.520 | 0.670 |
| Serif | 9 | 0.332 | 0.311 | 0.217 | 0.574 | 0.476 | 0.589 | 0.522 | 0.718 | 0.662 |
| Serif | 11 | 0.293 | 0.270 | 0.278 | 0.583 | 0.445 | 0.577 | 0.531 | 0.683 | 0.650 |
| Serif | 13 | 0.346 | 0.275 | 0.244 | 0.579 | 0.482 | 0.603 | 0.624 | 0.761 | 0.665 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.520 | 0.467 | 0.613 | 0.817 | 0.357 | 0.639 |
| Mono | 11 | 0.436 | 0.373 | 0.439 | 0.564 | 0.436 | 0.640 | 0.909 | 0.386 | 0.624 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.554 | 0.477 | 0.651 | 0.871 | 0.379 | 0.673 |
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.500 | 0.661 |
| Rounded | 11 | 0.714 | 0.380 | 0.576 | 0.540 | 0.721 | 0.636 | 0.661 | 0.466 | 0.664 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.517 | 0.695 |

Only Rounded's 3/7 moves (r8 0.657, 0.659, 0.691): the pair grew more
distinct.

**Figures default** (`checks/figcheck.py`): PASS. Sans 21 locations, 1332
units; serif 30, 579; mono 5, 1217; Rounded 15, 1332. All ten equal,
tnum = default, pnum varied (n/a for mono).

**Skeleton** (`checks/skeleton.py --all`, Rounded against the sans at
opsz 14, largest displaced region beyond 0.012 em in thousandths of an em²,
fail at 4.0): PASS, 0 glyphs at or over 4.0. 135 glyphs; largest region
3.80 (400) / 3.63 (900), mean 0.45 (400); overlap minimum 0.950 (400).
r8: 3.68 / 3.37, mean 0.41, overlap minimum 0.953. Every glyph that moved:

| Glyph | r8 400 | r9 400 | r8 900 | r9 900 |
| --- | ---: | ---: | ---: | ---: |
| G | 3.68 | 3.80 | 1.80 | 3.63 |
| B | 3.51 | 3.69 | 1.60 | 3.34 |
| E | 3.51 | 3.69 | 1.60 | 3.31 |
| L | 3.51 | 3.69 | 1.60 | 3.31 |
| degreefarenheit | 3.56 | 3.68 | 1.60 | 3.34 |
| F | 3.43 | 3.62 | 1.51 | 3.23 |
| P | 3.36 | 3.39 | 1.51 | 3.23 |
| R | 3.36 | 3.39 | 1.65 | 3.23 |
| three.pnum | 0.73 | 2.44 | 0.85 | 0.85 |
| three | 0.78 | 2.41 | 0.89 | 0.89 |
| five.pnum | 2.20 | 2.33 | 1.22 | 2.61 |
| five | 2.17 | 2.29 | 1.22 | 2.61 |
| bracketright | 1.65 | 1.65 | 2.14 | 2.98 |
| bracketleft | 1.60 | 1.60 | 2.06 | 2.94 |
| bracketright.case | 1.50 | 1.50 | 1.98 | 2.82 |
| bracketleft.case | 1.46 | 1.46 | 1.86 | 2.72 |
| seven | 0.82 | 0.82 | 1.63 | 2.62 |
| seven.pnum | 0.82 | 0.81 | 1.57 | 2.50 |
| threequarters | 0.18 | 0.18 | 0.79 | 0.90 |
| onequarter | 0.21 | 0.21 | 0.70 | 0.79 |

The 3's jump at 400 is its notch under the flat bar, which is now a turn.

**Rounded widths** (`checks/widths.py --all`): PASS, largest difference over
10 locations × 16 strings 0.00% (every string, every location, equal
advances to the sans).

**Outlines** (`checks/outlines.py`): 0 gated outliers (kinks, fold-backs,
added points) in the core set of sans, Rounded, serif and mono: PASS.
Reported only, all equal to r8: glyphs with only new short segments sans 1,
Rounded 1, serif 16, mono 0; full repertoire, any reason: sans 11 / 68,
Rounded 1 / 0, serif 127 / 2, mono 0 / 0 (text and display / caption). The
TrueType default-instance point report is r8's (sans 2, mono 13 core glyphs).

## Evidence

All images are browser renders at device scale 2, r6, r8 and r9 side by side,
with numbered callouts explained under each sheet.

- `evidence/item1-units.png`: ℉ and ℃ at 24 px / 400 (render file 09's
  units row) and 13/15/17 px at 400 and 700. Callouts: 1 ring aspect,
  2 ring height and walls against the typed °, 3 ring–letter gap, 4 letter
  height, width, C opening and advance.
- `evidence/item1-c-paren.png`: the ℃ letter beside the mono `C` and `(` at
  13/15/17/24 px, 400 and 700, first r9 and this revision, with each row's
  measured width and opening. Callouts: 1 first r9 (`°(`), 2 the revision,
  3 the revision letter alone, 4 mono C, 5 mono (.
- `evidence/item2-follow.png` and `item2-follow-x3.png` (nearest-neighbour
  ×3): `0℉– 7℉/ 2℃– 4℃/ 9℉, 1℃.` at 13/15/17 px and 300/500/700. Callouts
  1–6 are the six following marks with r8 and r9 worst-phase clearance.
- `evidence/item3-rounded.png`: the strip in Sans, Rounded r6 (= r8) and
  Rounded r9 at 24 and 48 px, 400 and 700. Callouts: 1 the 3's notch and bar
  corner, 2 P's radius, 3 the 7's flatter corner, 4 F's radius, 5 stroke ends
  unchanged.
- `evidence/item4-ligatures.png`: r8 default (ligatures), r9 default (one
  glyph per character), r9 with `dlig` and with `ss11` (ligatures).
- `evidence/changed-glyphs.txt`: the drift list against r6.

## Rules to keep

- **Turns and joins.** A concave corner facing an outer corner is a turn,
  radius = outer radius − one stem (concentric). Every other concave corner
  is a join and keeps the small radius; a concentric join webs the H's bar
  and the F's arm at display sizes.
- **The text pen is held by the skeleton gate.** The G sits at 3.80 of 4.0.
  Any more rounding in the text masters needs a construction change, not a
  bigger number.
- **Stroke ends are already round.** Below 1.60 stems an end is a full
  semicircle; its radius can't grow without thickening the stroke. Count
  rounding only on outer corners.
- **A unit's letter must read first.** Keep it at 0.66 of the mono letter
  or more, with the C's opening at 0.85 of the mono C's or more. Take width
  from the ring–letter gap, then the ring, then the followers, in that order.
  Never widen the ring to fill space.
- **Then fit what follows.** Fit the letter to the next cell's en dash and
  slash, cap the overhang, and let the tighter limit win.
- **Measure the built binary.** A lab copy with the same ring bounds read
  the Bold top wall at 1.10; the built font read 1.113 until the wall was
  thinned. Re-measure after every build.
- **Opt-in ligatures.** Operator ligatures live in `dlig` and `ss11` only;
  `calt` may only hold forms that leave one glyph per character.
- **Measure on renders.** Per glyph, centre-aligned, worst phase over 16
  sub-pixel phases, each part from a part-only font; never a string-level
  xor between fonts. Normalise ink to the text colour before reading sizes.
- **Heavy steps.** One heavy step at a time under the lock, the disk floor,
  the pause file and the quiet windows, with a full 60 s after each release.
  Use a wrapper that enforces the gap; doing it by hand missed it twice this
  round.
- **Browser steps** (render, evidence shots) also take the shared suite
  lock, after the heavy lock, and start only in their window. A step paused
  by its guard still holds its browser and both locks, so the wrapper stops
  it at a deadline. Stopping a chain must stop its waiting wrappers too: an
  orphaned one took the lock once this round.

## Next steps

1. **The 1 px aim after units in Bold.** `℉–` at 700 (0.50 px) and `℃/`
   at 400–700 (0.50–0.91 px) keep clear space but not 1 px. The C can't give
   more width without falling under the floor. Options: a two-cell unit
   (advance 2434) at the Bold end of the axis, or contextual forms of the en
   dash and slash after `uni2103` and `uni2109` that start later in their
   cell.
2. **The unit C's arms.** At 0.67 of the mono C the letter keeps the mono
   C's opening and reads as a narrow C, but its arms are shorter. If review
   at 13 px Bold still finds it close to a bracket, the contextual follower
   in step 1 would let the C widen.
3. **Clamp fillet handles to the corner triangle** in `lib.py`. In display
   Regular the 7's handle overshoots the cap line by 1.2 units and the
   brackets bulge 1.4 units past their stems.
4. **The 7's acute corner.** Its fillet grows only along the bar. A fillet
   that follows the diagonal would round it instead of flattening it.
5. **Rounded at 24 px beyond the gate.** The difference grew (91 → 111 at
   400) but stays small at a glance. More needs a construction change in the
   text masters (for example, softer stroke-end shapes on the round letters
   the gate measures less strictly), with the skeleton gate reviewed first.
6. **Carried over from r8:** the serif ff-ligature kinks at opsz 8 and the
   preserved upstream font-check findings.

## Rebuild

From the repository root:

    .venv/bin/python -I candidates/r9-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r9-type/checks/outlines.py r9-type
    make build  CAND=r9-type SUBSET=core ICONS_DIR=<icon folder>
    make gate   CAND=r9-type ICONS_DIR=<icon folder>
    make render CAND=r9-type OUT=<render folder> MAP=<map file> REFS=0 ICONS_DIR=<icon folder>
    make checks CAND=r9-type ICONS_DIR=<icon folder>
    .venv/bin/python -I candidates/r9-type/checks/drift.py r9-type --list candidates/r9-type/evidence/changed-glyphs.txt
    .venv/bin/python -I candidates/r9-type/checks/drift.py r9-type --ref r8-type
    .venv/bin/python -I candidates/r9-type/checks/figcheck.py build/r9-type
    .venv/bin/python -I candidates/r9-type/checks/skeleton.py build/r9-type --all
    .venv/bin/python -I candidates/r9-type/checks/widths.py build/r9-type --all
    .venv/bin/python -I candidates/r9-type/checks/vfkinks.py build/r9-type
