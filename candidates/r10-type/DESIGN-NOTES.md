# r10-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r9-type. Its decisions hold unless a section below
changes them. Two faces change:

- the mono ℉/℃ (ring, letter and what follows a unit);
- the Rounded corners (concave turns, the flat-top 3's notch, the outer
  corners of turns, and the text-size bowls).

Item 3 (one sans 3) needed no outline change: one construction already
serves every setting (section 3). Item 4 (serif `?`) is skipped because the
`?` is a component of other glyphs (section 4). Every other glyph keeps r9's
outlines in every master and in the built binaries; `checks/drift.py` proves
it (section 5).

All rendered measurements are per glyph and centre-aligned, never a string
xor between fonts.

- Mono values are from a browser render at device scale 2, worst case over
  16 sub-pixel phases, at 13, 15 and 17 px and weights 300 to 700. Each part
  (ring, letter, follower) is drawn from its own part-only copy of the built
  font at the same position. Sheet-09 values are from the specimen render
  (`make render`, 24 px at 2×).
- Rounded values are from the unhinted greyscale rasteriser, with opsz equal
  to the size in px (as browsers set it).
- The item-3 strip is a browser render (2×, opsz from the px size).

Before/after images are in `evidence/`, with numbered callouts explained under
each image.

## Summary

| Item | Result |
| --- | --- |
| 1. Mono ℉/℃ ring | Done. Sheet 09: wall 2 raster px (r9: 4), counter 57 px (r9: 15–17), aspect 0.992. The C is 0.809 and the F 0.804 of the typed letters. Advance 1217. A contextual en dash and slash follow a unit, and nothing touches at 300–700 and 13/15/17 px. |
| 2. Rounded corners | Done. 0 of 316 corners are under 0.90 of r6 (r9: 26); the worst is R at 0.938. The 3's wedge is gone (0.32 to 1.15 of r6). The 24 px difference from Sans is 94 / 177 (r9: 89 / 170). |
| 3. One sans 3 | No outline change was needed. Every default and tabular setting already draws one flat-top 3 (cause in section 3). Strip: all 280 figure 3s are within xor 0.069 of the reference. |
| 4. Serif `?` | Skipped: the `?` is a component of ¿ and of the double marks. The `s` was checked and needs no change. |
| 5. Everything else | `drift.py` PASS against r9 and r6. Sans and Serif are identical to r9. |

## 1. Mono ℉ and ℃: open ring, readable C, one width rule

### What r9 had
On sheet 09 (24 px at 2×, gray < 140), r9's ring had a 4 raster px wall
and a 15–17 px counter. The C of ℃ was 0.681 of a typed `°C` C, and the F
of ℉ was 0.767 of a typed F, so the two letters followed different rules.

### Construction (`TEMP_MODE = 'round3'`, `temp_unit8`)
- **Ring.** r9's round ring, unchanged in size (`degree_ring`: height 0.74
  of the degree sign at 300 and 0.705 at 700, round outer, aspect 1.00).
  Its walls are thinner: `WALL` is 0.39 of the degree sign's walls in both
  masters (r9: 0.95). The side wall is 49 units at 300, 57 at 400 and 76
  at 700, so the counter opens.
- **Why 0.39 and not r6's weight.** The browser draws the ring about 0.48
  raster px heavier than its outline (the degree sign shows the same
  gain). A soft wall of 1.99 raster px or more becomes a 3 px dark run at
  some sub-pixel phase. A first build at 0.46/0.52 (71 units at 400, close
  to r6's 73) measured 2 and 3 px on sheet 09. 0.39 keeps the soft wall
  near 1.94 px, so no phase gives 3 px. The cost is a ring about a fifth
  lighter than r6's at large sizes.
- **Letter.** It is still the face's own finished C or F, condensed in x
  and emboldened back to its stem (`temp_letter`, square cuts). It now
  follows one rule for both letters: the condensing is found by bisection
  so that the letter's ink width is `WIDTH` = 0.80 of the face's own
  letter.
- **Ring–letter gap.** `GAP` is 1.30 px at 300 and 1.25 px at 700 (at
  13 px), nearest ink.
- **F's middle arm.** The arm alone is shortened (`shorten_arm`) to keep
  1.2 px from the contextual en dash in the next cell. The top bar still
  sets the letter's width.
- **Advance.** 1217 units, as before.

### What follows a unit (contextual forms, item 1's Bold-end option)
The wider C reaches further right. In the lab, at 700, the C came within
0.23 px of a following slash and the F's arm touched a following en dash.
Narrowing the letters again would break the width rule. Instead, two
follower forms start later in their cells:

- `endash.unit`: the en dash's left end moves right by 60 units at 300 and
  120 units at 700 (of 1950), and its right end stays.
- `slash.unit`: the slash's foot moves right by 80 units at 300 and 160
  units at 700, and its top stays, so it stands a little steeper only after
  a unit.

They come from lookup `unit_follow` in `calt`, after `uni2103`/`uni2109`.
The forms are on by default and give one glyph per character (shaping
check below). The comma and the period keep their glyphs, because their
clearance is at least 2 px without a contextual form.

### Results
Sheet 09 (`make render`, 24 px at 2×, gray < 140, `checks/sheet09.py`):

| | r9 | r10 | Goal |
| --- | --- | --- | --- |
| Wall on the middle scanline | 4 raster px | 2 raster px (soft wall 1.98) | ≤ 2.5 |
| Counter | 15–17 px | 57 px | ≥ 38 |
| Ring aspect | round | 0.992 | 1.00 ± 0.05 |
| C of ℃ against a typed `°C` C | 0.681 | 0.809 | ≥ 0.77 |
| F of ℉ against a typed F | 0.767 | 0.804 | within 0.04 of the C (0.005) |

The soft wall is 1.98 px, just under the 1.99 px at which another
sub-pixel phase could give a 3 px run. The sheet is rendered at a fixed
position, so this is what the sheet shows.

Ring outline in the built binary (units of 1950; advance 1217 at every
weight):

| Weight | Outer, r9 and r10 | Counter width r6 / r9 / r10 |
| --- | --- | --- |
| 300 | 458 × 459 | 333 / 218 / 360 |
| 400 | 462 × 463 | 314 / 183 / 348 |
| 700 | 472 × 472 | 268 / 100 / 319 |

The outer ring is r9's, so its height is unchanged.

Browser strip (13/15/17 px, 300–700, 16 sub-pixel phases, each part drawn
from its own part-only font):

- The counter is open in 48 of 48 cases at every weight.
- The raster aspect is 0.85–1.15, because pixel rounding at 13 px moves
  each edge by up to one pixel. The outline aspect is 0.998–1.000.
- Letter width is 0.80–0.81 of the face's own letter. The ring–letter
  gap is 1.00–1.50 px.

Nearest ink after a unit (css px, minimum over sizes and phases):

| Weight | ℉– | ℉/ | ℃– | ℃/ | ℉, | ℃. |
| --- | --- | --- | --- | --- | --- | --- |
| 300 | 1.00 | 3.31 | 3.14 | 1.08 | 4.45 | 2.50 |
| 400 | 1.00 | 3.14 | 2.66 | 1.00 | 3.80 | 2.00 |
| 500 | 1.00 | 3.11 | 2.19 | 0.91 | 3.53 | 2.00 |
| 600 | 1.00 | 2.85 | 2.19 | 0.62 | 3.41 | 2.00 |
| 700 | 1.00 | 2.85 | 1.74 | 0.91 | 3.11 | 1.50 |

No pair touches. Default shaping turns `72℉–75℉` to 7 glyphs for 7
characters, with `endash.unit`; the plain `endash` appears with `calt`
off. `20℃/h` shapes to 5 glyphs, with `slash.unit`. `10–12` and `a/b`
keep the plain forms. Neither follower is in the cmap, and both have
advance 1217.

## 2. Rounded: no filled corners

### Why r9 filled the flat-top 3 and the inner corners
- **The 3's wedge.** r9 raised the Black maximum cut (text 1.10 stems), so
  the notch cap went from 0.9 to 1.0 stem. In the caption Black master,
  that left the bar's underside 14 units short of `MIN_LINE`. The plan
  then made that join a "meets" corner in every master, and the notch
  fillet started mid-bar: in m03 it started at x 517.5, against r6's 675.1.
  The result was the dark wedge between bar and diagonal.
- **Inner corners.** Display turns were 2.00 stems, concentric with the
  3.00 outer pen. At 48 and 96 px they filled the inside of the turns of F,
  P, E, L, B, R, 5, ℉ and G, losing up to 47% of the open area within 1.5
  stems of the corner against r6.

### Changes (`transforms/rounded.py`, `transforms/lib.py`)
- **A `notch` corner kind** (`SOFT_NOTCH` glyphs: `three`, `three.pnum`).
  Its reach is capped so that both lines keep `MIN_LINE` in every master.
  The notch stays a small round instead of a fill.
- **Display turns** are 0.85 stems (Black 0.40), down from 2.00.
- **Outer corners of a turn.** These are found by the same test as the
  turn, from the other side, and take a new radius `R_OUTER` (display 2.20,
  Black 1.40). With a 0.85-stem turn, r9's 3.00 outer corner would neck the
  stroke to 0.6 of a stem across the diagonal; 2.20 keeps it at 0.85.
  Every other outer corner keeps `R_CONVEX` (3.00).
- **Text-size bowls (the push from Regular at 24 px).** The text and
  caption masters now get a share of the display masters' rounder hero
  bowls: `TEXT_BOWL_SHARE` 0.4 of the way to circular, taking the largest
  of 0.4/0.3/0.2/0.1 that adds no kink. Affected glyphs are the figures
  0 2 3 5 6 8 9, % . : and °. The smaller display turns took about 13 px
  (400) and 6 px (700) out of the 24 px difference; the bowls give back
  more than that.

### Results (built Rounded VF; unhinted greyscale, opsz = px)
Concave corners in `0–9 % ° : − ℉ ℃ A–Z a–z` at 48 and 96 px, 400 and
700: 316 corners in 29 glyphs (`1 2 3 4 5 7 B E F G H I K L P R T Y a b d
g k p q r y z ℉`; the others have none). The open area is the background
inside 1.5 stems of each corner, as a share of r6's.

| | corners under 0.90 of r6 | worst |
| --- | --- | --- |
| r9 | 26 of 316 | 3 at 0.320 |
| r10 | 0 of 316 | R at 0.938 |

Worst ten glyphs in r10 (each glyph's worst corner):

| Glyph | Corner | Size, weight | r9 | r10 |
| --- | --- | --- | --- | --- |
| R | inside the bowl, at the stem (top) | 96 px, 400 | 0.526 | 0.938 |
| P | inside the bowl, at the stem (top) | 96 px, 400 | 0.550 | 0.939 |
| ℉ | under the F's top bar, at the stem | 96 px, 400 | 0.706 | 0.972 |
| B | inside the lower bowl, at the stem (foot) | 48 px, 400 | 0.804 | 0.972 |
| E | under the top bar, at the stem | 96 px, 400 | 0.707 | 0.972 |
| F | under the top bar, at the stem | 96 px, 400 | 0.707 | 0.972 |
| G | the spur join | 96 px, 400 | 0.856 | 0.972 |
| L | above the foot, at the stem | 96 px, 400 | 0.573 | 0.973 |
| 5 | where the bowl leaves the upright | 96 px, 700 | 0.909 | 0.974 |
| 7 | under the bar, at the diagonal | 96 px, 400 | 0.996 | 0.996 |

The flat-top 3's bar/diagonal corner (the wedge): r9 0.320 and 0.362 at
96 and 48 px (400), r10 1.147 and 1.175. It is now more open than r6's.

24 px difference between Sans and Rounded (pixels that differ by at least
25%, per glyph, centre-aligned, each glyph counted once):

| | 400 | 700 |
| --- | --- | --- |
| r6 | 73 | 157 |
| r9 | 89 | 170 |
| r10 | 94 | 177 |

| Glyph | r6 400 | r9 400 | r10 400 | r6 700 | r9 700 | r10 700 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 21 | 21 | 30 | 19 | 19 | 26 |
| 3 | 17 | 21 | 20 | 17 | 17 | 16 |
| F | 6 | 12 | 8 | 9 | 17 | 14 |
| P | 6 | 12 | 8 | 6 | 10 | 10 |
| 2 | 2 | 2 | 5 | 6 | 6 | 7 |
| 8 | 0 | 0 | 2 | 6 | 6 | 9 |
| 7 | 4 | 4 | 4 | 6 | 7 | 7 |
| H | 6 | 6 | 6 | 12 | 12 | 12 |
| A | 4 | 4 | 4 | 8 | 8 | 8 |
| M | 2 | 2 | 2 | 20 | 20 | 20 |
| m n h i p g 1 4 Q I ° : (together) | 5 | 5 | 5 | 48 | 48 | 48 |

The total grows from r9 at both weights. Per glyph, F, P and 3 shrink a
little. Their r9 difference was partly the corner fill this item removes,
and the 3's notch is now open, as in Sans. The bowls give the difference
back on 0, 2 and 8.

## 3. One sans 3

No outline changed. Each style already uses one 3 construction in every
default setting, and the binaries show why:

- **No substitution switches the drawing.** In the r6, r9 and r10 Sans
  and Rounded, GSUB has no feature variations. The contextual rules that
  list a 3 either use it only as context (`calt`: `<-` before a figure,
  and the case and figure-height hyphen and colon; `ordn`) or reach the
  fraction forms under `frac`. None of them changes a 3 in default text.
  In Sans, `tnum` maps `three` to `three.tf` and `pnum` maps it to
  `three.pnum`. `three.tf` is a component of `three`, which is a component
  of `three.pnum`, so all three draw the same contour (advances 1340
  tabular and 1303 proportional, unchanged). Rounded has only `three`
  (tabular, its default) and `three.pnum`, which are the same contour at
  the two advances. Weight and optical size only interpolate that one
  contour.
- **The round-top 3 is opt-in only.** `three.1` and its `.pnum`/`.tf`
  forms are reached by `ss01`, `cv09` and `salt`, none of which a browser
  applies by default. `¾` uses `three.numr` (a component of `three.dnom`),
  and `³` is `three.sups`. Both are flat-top. Their round-top forms
  (`.ss01`) are opt-in as well. Rounded has no round-top 3 at all.
- **Sheet 13 sets no feature.** The specimen's headline (`−3°`, 94 px,
  500) and the 24 px rows (`font-variant-numeric: tabular-nums`) use only
  default and tabular figures.

So a round-top 3 cannot appear in any default setting. Our own sheet-13
render (r9 and r10) draws the flat-top 3 in the headline, the tabular rows,
`30.16` and `3:45`. A round-top reading of that sheet must come from
outside the font: a different render, or the flat top's rounded corner
seen at reduced scale.

### Browser strip
The strip is `3 33 −3° 73° 30.16 3:45 ¾` in default and tnum figures, at
300–700 and 13/24/38/96 px (browser at 2×, opsz from the px size). Each 3
is cut out by its own character box and centre-aligned by ink centroid on
its weight's reference 3 (the first 3 of the default line). Values are
soft xor over union.

| Style | Figure 3s | xor to the flat-top reference, max (mean) | xor to the ss01 round-top, min |
| --- | --- | --- | --- |
| Sans | 280 | 0.069 (0.015) | 0.307 |
| Rounded | 280 | 0.076 (0.016) | none (no round-top 3) |

The maximum xor by size is 0.069, 0.055, 0.030 and 0.013 for Sans and
0.076, 0.058, 0.027 and 0.011 for Rounded (13, 24, 38 and 96 px). The
largest values are at 13 px, where a 3 is about 19 raster px tall and the
sub-pixel position alone moves a few edge pixels.

At 13 px the ¾ numerator is only 6 to 9 raster px tall. Neither a scaled
xor nor an edge test separates flat from round reliably at that size. The
proof for ¾ is the binary: it shapes to the one glyph `threequarters` in
default, tnum and pnum, and that glyph is built on `three.numr`, the
flat-top numerator. Crops of its 3 at every size and weight show a flat
top. In Sans, ³ is `three.sups` (flat-top) in every setting except ss01.
Rounded has no ³.

## 4. Serif `?` (skipped)

The uneven taper comes from the baseline: the inner edge of the hook has a
short spike, where a line runs into the bowl stroke and back. It is
inherited, not made by any transform.

The serif `?` is not a stand-alone drawing. `questiondown` (¿) is built
from `questiondown.cap`, which is the `?` rotated as a component, and the
sources' double marks (⁇, ⁈, ⁉) are composites of it as well. Evening out
the taper would therefore change ¿ in every master, and the brief allows
the item to be skipped when it would touch other glyphs. The serif keeps
r9's outlines in every master and in the built binary (section 5).

The `s` was checked against its neighbours on a rendered line (400, ink
per advance × x-height box), so the next round can decide on facts:

| Size | c | s | a | e | o | n | s ÷ mean of the others |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 24 px | 0.289 | 0.350 | 0.360 | 0.342 | 0.323 | 0.338 | 1.060 |
| 96 px | 0.305 | 0.331 | 0.380 | 0.327 | 0.330 | 0.360 | 0.972 |

At 24 px the `s` is 6% darker than the mean of its neighbours, but lighter
than the `a`. At 96 px it is 3% lighter than the mean. It sits inside the
range of `c a e o n` at both sizes, so nothing was changed.

## 5. Everything else

`checks/drift.py` compares the sources (every master) and the built
binaries (glyf, hmtx, gvar per region, whole tables) with a reference. It
now knows the r10 changes (`UNIT_FOLLOW`, `ROUNDED_R10`) and treats
appended glyphs as additions.

Against r9 (`--ref r9-type`): PASS.

- **Sans:** identical in all nine masters and in both binaries.
- **Serif:** identical in all nine masters and in both binaries.
- **Mono:** four glyphs in both masters: `uni2103` and `uni2109`, plus
  the new `endash.unit` and `slash.unit`. `features.fea` and `lib.plist`
  change (the new lookup and the glyph order). In the binary, only the
  glyf and gvar of `uni2103` and `uni2109` change, and hmtx does not.
  GSUB, post and maxp change for the two new glyphs and the lookup.
- **Rounded:** 34 glyphs over the nine masters: `B E F G L P R`,
  `bracketleft(.case) bracketright(.case)`, `colon colon.case colon.fig`,
  `degree degreefarenheit`, `two three five six eight nine zero` (each with
  `.pnum`), `zero.slash zero.pnum.slash`, `percent period`. hmtx is
  unchanged, and no table other than glyf and gvar changes.

Against r6 (`--list evidence/changed-glyphs.txt`): PASS. The full list for
each master is in `evidence/changed-glyphs.txt`. The serif's 629 glyphs in
m00–m02 and the mono `name` table are r9's changes, unchanged here.

## Checks

**Gate** (`make gate`): no hard failures. Every count is the same as r9.

| Face | Pass | Warn | Fail | Error | Interpolation findings |
| --- | ---: | ---: | ---: | ---: | --- |
| Sans | 92 | 4 | 5 | 1 | none |
| Serif | 95 | 5 | 5 | 0 | kink 4 (r9: kink 4) |
| Mono | 90 | 6 | 5 | 1 | none |
| Rounded | 98 | 0 | 2 | 1 | none |

The report's quality status is FAIL, as in r9, because of the inherited
font-quality findings (same counts). Name records, figure gates and icons
PASS. WOFF2 sizes: Mono 47,856 bytes (r9: 47,980), Rounded 74,320 (r9:
74,736). Sans and Serif are unchanged.

**Render** (`make render`): 38 PNGs, blind byte scan PASS. Line contact
is 0: all three headline collision checks are clear.

**Checks** (`make checks`): PASS.

- Rounded/Regular ink width (96 px, 400): `104°F`, `72°`, `18:30` and
  `−3°` are all +0.000%.
- Tabular default: Sans PASS (21 locations), Serif INFO (30), Mono PASS
  (5), Rounded PASS (15).

**Confusables** (`checks/figcheck.py`, xor, fail under 0.20, wght 400):
PASS.

| Face | px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.680 | 0.379 | 0.545 | 0.496 | 0.679 | 0.619 | 0.652 | 0.499 | 0.642 |
| Sans | 13 | 0.735 | 0.407 | 0.595 | 0.541 | 0.738 | 0.655 | 0.519 | 0.520 | 0.670 |
| Serif | 9 | 0.332 | 0.311 | 0.217 | 0.574 | 0.476 | 0.589 | 0.522 | 0.718 | 0.662 |
| Serif | 13 | 0.346 | 0.275 | 0.244 | 0.579 | 0.482 | 0.603 | 0.624 | 0.761 | 0.665 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.520 | 0.467 | 0.613 | 0.817 | 0.357 | 0.639 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.554 | 0.477 | 0.651 | 0.871 | 0.379 | 0.673 |
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.552 | 0.648 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.572 | 0.689 |

The 11 px rows are in the check's output. The lowest value is 0.217
(Serif l/I at 9 px), as in r9. Figure defaults: all four faces PASS (tnum
equals default, ten equal advances, pnum varied where it applies).

**Skeleton** (`checks/skeleton.py --all`, Rounded against the sans at
opsz 14, fail at 4.0): PASS, 0 glyphs at or over 4.0. Over 135 glyphs, the
largest region is 3.80 (400) / 3.63 (900), both G and the same as r9. The
mean is 0.42 at 400 (r9: 0.45), and the overlap minimum is 0.950. The 3
falls from 2.41 to 0.43 and `three.pnum` from 2.44 to 0.44 (400); ℉
stays at 3.68 / 3.34.

**Widths** (`checks/widths.py --all`): Regular against Rounded advances
at 10 locations × 16 strings. The largest difference is 0.00%.

**Interpolation** (`checks/vfkinks.py`): Sans, Mono and Rounded have 0
findings, and the Rounded test PASSES. Serif has 5 (`f_f` ligatures at
opsz 8), inherited unchanged.

**Outlines** (`checks/outlines.py`): 0 core outliers (kinks, fold-backs,
points) in all four faces: PASS.

**Binary and shaping** (default shaping of the built Mono):

- `a === b !== c => d <= e >= f != g -> h` gives 38 glyphs for 38
  characters, with no multi-character cluster, both by default and with
  `calt` off. All 38 are cmap glyphs.
- `dlig` and `ss11` (opt-in, "Operator ligatures") give 38 glyphs with
  spacers, and share no lookup with `calt`.
- cmap: U+2103 maps to `uni2103` and U+2109 to `uni2109`, both with
  advance 1217.
- GSUB has 354 lookups; `calt` has 10.
- No reserved name appears in any face's name table.
- Sans and Rounded have no feature variations. The 3 shaping is in
  section 3.

## Evidence

- `evidence/item1-units.png`: r6 / r9 / r10 mono units at 96 px, and
  `72℉–75℉ 20℃/h ℉, ℃.` at 13 and 17 px, 300 and 700. Callouts 1–4.
- `evidence/item2-rounded.png`: r6 / r9 / r10 Rounded at 96 and 200 px,
  and Sans against Rounded at 24 px. Callouts 1–4.
- `evidence/item3-three.png`: r6 / r9 / r10 Sans and Rounded at 96/500,
  38/400 and 24/400 tnum, and r10 default against ss01. Callouts 1–4.
- `evidence/item4-question.png`: the serif `?` and `¿` in r6 / r9 / r10,
  showing why item 4 is skipped.
- `evidence/changed-glyphs.txt`: drift's list against r6.

The legend under each image explains its callouts.

## Rules to keep

- **Mono units: one width rule.** The letter in ℃/℉ is the face's own
  letter at a fixed share of its ink width (0.80), found by bisection. Never
  narrow one letter alone to make room after it. Clear the follower instead
  (contextual forms), or shorten only the F's middle arm.
- **Measure the ring on the raster.** On sheet 09 at 2×, gray < 140:
  wall ≤ 2.5 raster px and counter ≥ 38 px. The browser adds about 0.48
  raster px to the outline, so keep the side wall at 400 under about 58
  units (1.5 px at 50 px/em). Above that, some sub-pixel phase gives a
  3 px run. Measure the soft wall (summed coverage) as well as the dark
  run: one render's phase can hide a wall that is too heavy.
- **Contextual followers stay one glyph per character** and live in
  `calt` (default on), so a unit followed by an en dash, slash, comma or
  period never touches at 300–700, 13–17 px.
- **Rounded concave corners.** No concave turn or join may lose more than
  10% of r6's open area at 48 and 96 px, Regular and Bold (`corners.py`,
  window 1.5 stems). Display turns stay at or below 0.85 stems. A turn's
  outer corner takes `R_OUTER`, so the stroke keeps at least 0.85 of a stem
  across the diagonal. Acute notches use the `notch` kind, which keeps
  `MIN_LINE` on both lines.
- **Raising a maximum cut must be checked against caption Black.** A cut
  that eats a whole segment there turns a join into "meets" in every master.
- **One drawing per figure.** `three` and `three.tf` are components of
  `three.pnum`, and the numerators, denominators and superiors are the same
  flat-top construction. The only round-top 3 is the opt-in `ss01`. Don't
  add a feature variation or a contextual 3.

## Next steps

- **Mono ring weight at large sizes.** The ring's wall has to suit 24 px
  in the browser, so at 96 px it is about a fifth lighter than r6's. The
  mono has one axis (weight), so a heavier display ring needs either a
  separate form or a wall that is not linear in weight. Test it on
  sheet 09 first.
- **Rounded F, P and 3 at 24 px.** Their per-glyph difference from Sans
  fell from r9, because r9's was partly the corner fill. If the next round
  wants them further from Sans at text size, use a softer outer corner on
  their bars in the text masters. Leave the concave turns as they are.
- **Serif `?`.** Fix the spike on the inner edge of the hook in one
  transform that also checks `questiondown.cap`, `questiondown` and the
  double marks, since they are composites of it.
- **Serif `s`.** At 24 px it is 6% darker than the mean of `c a e o n`
  but inside their range. Change it only if a review flags it.
- **Mono followers.** The comma and the period have no follower form
  because their clearance is at least 2 px. If a later change widens the
  unit letters, add followers for them in the same `calt` lookup.

## Rebuild

    .venv/bin/python -I candidates/r10-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r10-type/checks/outlines.py r10-type
    make build CAND=r10-type SUBSET=core ICONS_DIR=…
    make gate CAND=r10-type ICONS_DIR=…
    make render CAND=r10-type OUT=… MAP=… REFS=0 ICONS_DIR=…
    make checks CAND=r10-type ICONS_DIR=…
    python3 -I candidates/r10-type/checks/sheet09.py <render OUT>/<label>-09.png    # needs numpy, scipy and Pillow
    .venv/bin/python -I candidates/r10-type/checks/drift.py r10-type --list candidates/r10-type/evidence/changed-glyphs.txt
    .venv/bin/python -I candidates/r10-type/checks/drift.py r10-type --ref r9-type
    .venv/bin/python -I candidates/r10-type/checks/figcheck.py build/r10-type
    .venv/bin/python -I candidates/r10-type/checks/skeleton.py build/r10-type --all
    .venv/bin/python -I candidates/r10-type/checks/widths.py build/r10-type --all
    .venv/bin/python -I candidates/r10-type/checks/vfkinks.py build/r10-type
