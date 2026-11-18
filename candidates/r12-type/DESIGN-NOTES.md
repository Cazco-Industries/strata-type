# r12-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r11-type, and r11's decisions hold. One thing changes:
the serif's caption spacing between 9 and 13 px. r11 opened the caption
masters and let the opening fall in one straight line to nothing at 13 px.
Because the axis gives 12 to 13 px far more design room than any px below it,
most of that fall came in the last px, and 12 px text set wider than 13 px
text. r12 fades the opening in two steps instead of one:

- 9 px keeps r11's opening (every advance within 1 unit);
- 10 px keeps 80 units per glyph (r11: 101), 2 over the smallest opening
  that keeps every neighbour pair of the gap strings 2 raster px apart;
- 11 px keeps 45.5 units, about half of r11's 87.6;
- 12 px keeps 11 units (r11: 74), and 13 px and up are r11's to the unit.

Sans, Rounded and Mono are untouched: their sources are byte-identical to
r11's, and their built TTF and WOFF2 files are byte- and table-identical
(Checks: binary and shaping). In the serif only the three caption masters' advances change
(+21 units on the glyphs that open), plus one new glyph-only layer per
caption master; r11's 13 px layer is kept byte for byte.

Measurement methods are r11's:

- Set widths are HarfBuzz advances with kerning and default features, with
  opsz = px, in CSS px (units × px / 1000), over seven strings: `quiet sky`,
  `minimum`, `rain returns`, `0123456789`, `Rain returns after 4 pm; winds
  ease to 9 mph overnight.`, `The quick brown fox jumps over the lazy dog`
  and `Feels like 72°F. Humidity 64%. Sunrise 7:41.`
- Gaps are measured on headless browser renders at device scale 2. Each
  character is drawn alone at its shaped position (the others transparent),
  ink is coverage ≥ 0.5 between the theme background and text colours, and a
  gap is the smallest run of non-ink between two neighbours' ink on any row
  they share, in raster (2×) px, worst case over the sub-pixel phases 0, ¼, ½
  and ¾ px. The strings are `quiet sky`, `minimum`, `rain returns` and the
  figures (30 pairs), at 400 and 600, light and dark. The browser sets opsz
  from the font size (`font-optical-sizing: auto`).

The before/after image is `evidence/item-fade.png`. Its legend explains the
numbered callouts (see Evidence).

## Summary

| Brief item | Result |
| --- | --- |
| 1. 9 px unchanged | Every serif advance at opsz 9 (wght 200–900 in steps of 50, 1,482 glyphs) is within 1 unit of r11's (largest difference 1). 9 px gap table: 0 pairs under 2 raster px in all four cells, smallest gap 2, as r11 (r10: 24 distinct pairs). |
| 2. 10 px stays open | 80 units per glyph (r11: 101). The smallest opening that clears every pair at 10 px is 78 (calibrated); 10 px gap table: 0 pairs under 2 raster px in all four cells, smallest gap 2 (r10: 21 distinct pairs). |
| 3. 11 px about half | The 11 px set-width increase over r10 is 0.511–0.526 of r11's over all seven strings and weights 300–700 (target 0.45–0.55). |
| 4. Smooth fade | For every string and weight, CSS set width rises with every whole px from 9 to 13 (smallest step +1.40 px) and width per px never rises (smallest drop 139 units). 13–60 px: no advance differs from r11 at any of 15 weights; set widths at 13/15/17 px differ from r11 by 0.000 %, and are identical at 20/24/48 px. |
| 5. Size | Serif WOFF2: r10 197,980, r11 245,128, r12 288,968 bytes (+43,840 over r11). The fade needs one more glyph-only layer than r11, which costs about 44 KB (section 2, "Size"). |
| 6. Drift | `checks/drift.py` PASS against r11 and r6. INTENDED is r11's plus the new `fade.12` layer of each caption master (section 4). |

## 1. Why

r11's opening was 0.895 of the caption opening at 9 px, 0.789 at 10, 0.684
at 11, 0.579 at 12 and 0 at 13 px. The axis maps 8–12 px onto design opsz
8–9 (0.25 per px) and 12–13 px onto 9–10.375 (1.375), and r11's opening fell
linearly in design opsz, so it lost 74 units per glyph between 12 and 13 px
and 13 to 14 units for each px below. Text at 12 px therefore set wider than
the same text at 13 px: the sentence above at 400 is 400.76 px wide at 12 px
and 378.14 px at 13 px. Two council seats also found 11 px too loose and
asked for about half of r11's 11 px tracking, keeping the 9 px boost.

## 2. Change (`transforms/serif.py`: `FADE_STEPS`, `fade_masters`, `caption_open`, `add_fade_sources`; `apply.py`: `r12_serif`)

`fade_masters` now makes one glyph-only layer per step of `FADE_STEPS`
(user px, opening in units per glyph). Each layer is the exact
interpolation of its caption and text masters' glyphs at that step's
design opsz (outlines, components, anchors, advances), plus the step's
opening on every glyph that opens. The opening is piecewise linear in design
opsz between the caption master and the steps, and 0 from the last step up.
`caption_open` then opens the caption masters themselves by `CAPTION_TOTAL`,
solved from the first step so that 9 px keeps r11's opening (114.5 units).
As in r11, all of it goes on the right sidebearing, outlines and anchors do
not move, and kerning and mark positions keep interpolating between the
masters' own `features.fea`.

r12's steps are `((12, 11), (13, 0))`, so `CAPTION_TOTAL` is 149 (r11: 128).
The 13 px step is r11's `fade.13` layer, regenerated by the same code and
byte-identical to r11's.

| px | 8 | 9 | 10 | 11 | 12 | 13 and up |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| design opsz | 8 | 8.25 | 8.5 | 8.75 | 9 | 10.375 + |
| r11 opening (units per glyph) | 128 | 114.5 | 101.1 | 87.6 | 74.1 | 0 |
| r12 opening | 149 | 114.5 | 80 | 45.5 | 11 | 0 |

**Why these steps.** With 9 px fixed, the line from the caption master
through 9 px gives 10 px = 2 × 114.5 − C and 11 px = 3 × 114.5 − 2C. For
11 px to keep 45–55 % of r11's opening (39–48 units), C must be 148–152, so
10 px gets 77.7–81.4 units. The calibration put the smallest opening that
clears every pair at 10 px at 78 units, so one straight line from 8 to 12 px
meets items 2 and 3 together. r12 takes C = 149 (80 units at 10 px, the 78
floor plus the 2-unit margin r11 also kept) and stops the line at 12 px,
where it reaches 11 units. From there it falls to 0 at r11's 13 px layer.
That last px loses 11 units instead of r11's 74.

**Why keep r11's 13 px layer.** A single layer can do the whole fade: the
same line, ending at zero at 12.05 px with C = 149. It was built and measured
(lab variant). Its WOFF2 is 242,932 bytes, under r11's. But every size from
13 px up then interpolates from a different layer, and each advance rounds
on its own. About a quarter of the advances at 13 px move by ±1 unit. In the
tabular figures, ten equal glyphs move together: `0123456789` is 0.17 % off
r11 at 14 px (400) and 17 px (700), over item 4's 0.1 %. (r10 and r11 differ
from each other by the same rounding.) Keeping `fade.13` as the zero step
makes 13 px and up r11's to the unit.

**Size.** The compiler's variation model orders the opsz layers by
distance from the default (the text master), so each caption-side layer
is modelled before the caption master. Each one is a region with full
outline deltas, even though its outlines are an exact interpolation: r11's
one layer cost 47 KB of WOFF2, and r12's second costs about 44 KB more.
Lab builds of the alternatives (same compiler, core subset, WOFF2):

| Construction | Layers per caption master | 13 px and up | Serif WOFF2 |
| --- | ---: | --- | ---: |
| r11 | 1 (13 px) | — | 245,128 |
| one step, zero at 12.05 px | 1 | ±1 unit rounding, figures 0.17 % | 242,932 |
| r12: 12 px (11 units) + r11's 13 px | 2 | identical to r11 | 288,968 |
| 10 px (92) + zero at 11.84 px | 2 | ±1 unit rounding, figures 0.18 % | 287,448 |
| 10 px (101) + 11 px (47) + zero at 12.3 px | 3 | ±1 unit rounding, figures 0.18 % | 327,468 |

### Calibration (10 px)

r10 with CSS letter-spacing L px at 10 px stands in for an opening of
100 × L units (the opening is uniform over the opened glyphs, and kerning
does not change). Pairs under 2 raster px (of 30, per cell), worst of four
phases:

| letter-spacing (px) | light 400 | light 600 | dark 400 | dark 600 | distinct pairs under 2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 (r10) | 14 | 22 | 19 | 23 | 21 |
| 0.40 | 1 | 5 | 6 | 11 | 11 |
| 0.52 | 1 | 2 | 4 | 7 | 7 |
| 0.56 | 0 | 0 | 0 | 3 | 3 |
| 0.60 | 0 | 1 | 1 | 6 | 6 |
| 0.64 | 0 | 1 | 2 | 2 | 3 |
| 0.68 | 0 | 0 | 1 | 1 | 2 |
| 0.72 | 0 | 0 | 0 | 0 | 0 |
| 0.76 | 0 | 0 | 0 | 1 | 1 (`34`) |
| 0.78 – 1.02 (every 0.02) | 0 | 0 | 0 | 0 | 0 |

The count does not fall evenly, because sub-pixel phases snap differently at
each spacing; 0.72 clears by luck of phase and 0.76 does not. From 0.78 px
up, every tested value clears, so the floor is 78 units.

## 3. Results

All numbers are from the built core fonts (`build/<cand>/StrataSerif.ttf`)
unless a row says "full" (the build's cached full-coverage font, 1,482
glyphs).

### Set widths

The sentence at weights 300–700, CSS px, r10 / r11 / r12 (HarfBuzz, kerning
on, opsz = px). The full tables for all seven strings are in
`evidence/set-widths.txt`.

| wght | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 17 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300 | 264.70 / 320.41 / 320.32 | 293.62 / 348.16 / 336.81 | 322.46 / 374.24 / 349.26 | 351.07 / 399.05 / 358.06 | 376.35 / 376.40 / 376.40 | 401.28 / 401.17 / 401.17 | 425.46 / 425.46 / 425.46 | 472.31 / 472.29 / 472.29 |
| 400 | 266.17 / 321.69 / 321.74 | 295.21 / 349.73 / 338.30 | 324.16 / 375.91 / 350.89 | 352.78 / 400.76 / 359.90 | 378.14 / 378.14 / 378.14 | 403.06 / 402.86 / 402.86 | 427.27 / 426.99 / 426.99 | 473.79 / 473.84 / 473.84 |
| 500 | 268.87 / 324.55 / 324.53 | 298.15 / 352.63 / 341.34 | 327.35 / 379.39 / 354.33 | 356.44 / 404.45 / 363.48 | 382.11 / 382.13 / 382.13 | 407.06 / 406.99 / 406.99 | 431.48 / 431.44 / 431.44 | 478.40 / 478.40 / 478.40 |
| 600 | 271.52 / 327.26 / 327.26 | 301.11 / 355.65 / 344.35 | 330.64 / 382.71 / 357.58 | 360.05 / 408.07 / 367.08 | 385.93 / 385.94 / 385.94 | 411.21 / 411.22 / 411.22 | 435.84 / 435.82 / 435.82 | 483.07 / 483.09 / 483.09 |
| 700 | 272.83 / 328.46 / 328.48 | 302.54 / 357.10 / 345.67 | 332.12 / 384.20 / 359.11 | 361.58 / 409.66 / 368.70 | 387.65 / 387.67 / 387.67 | 413.04 / 413.06 / 413.06 | 437.76 / 437.83 / 437.83 | 485.32 / 485.32 / 485.32 |

Over all seven strings and weights 300–700:

- every whole px from 9 to 13 sets wider than the one before; the smallest
  step is +1.40 px (`quiet sky`, 300, 11 → 12 px). r11 fell between 12 and
  13 px in every string and weight;
- width per px never rises; the smallest drop is 139 units (`minimum`, 300,
  12 → 13 px);
- 13, 15 and 17 px differ from r11 by 0.0000 %, and no string differs at
  20, 24 or 48 px;
- at 9 px the largest string difference is 10 units over 55 characters
  (the sentence, 300), from ±1-unit rounding.

### 11 px

The increase over r10 at 11 px as a share of r11's (target 0.45–0.55):

| String | 400 | 300–700 |
| --- | ---: | ---: |
| `quiet sky` | 0.517 | 0.517–0.519 |
| `minimum` | 0.526 | 0.519–0.526 |
| `rain returns` | 0.516 | 0.516–0.519 |
| `0123456789` | 0.511 | 0.511–0.523 |
| sentence | 0.516 | 0.516–0.518 |
| `The quick brown fox…` | 0.517 | 0.517–0.519 |
| `Feels like 72°F…` | 0.517 | 0.517–0.520 |

The model value is 45.5 / 87.6 = 0.519; strings differ only by how many of
their glyphs open and by rounding.

### Advances (HarfBuzz, HVAR applied, r12 against r11)

| opsz | core (564 glyphs) | full (1,482 glyphs) |
| --- | --- | --- |
| 9, wght 200–900 every 50 | largest difference 1 unit (802 differences of 1) | 1 unit (2,270 differences of 1) |
| 8 (300/400/700) | +21 on every opened glyph | +21 |
| 10 | −20 to −22 | −20 to −22 |
| 11 | −41 to −43 | −41 to −43 |
| 12 | −64 to +1 | −64 to +1 |
| 13, 14, 15, 17 | 0 differences | 0 differences |
| 20, 24, 30, 36, 48, 60 × 15 weights | 0 differences | 0 differences |

The default instance's `hmtx` is unchanged.

### Gaps

Each cell shows the smallest gap and, in brackets, the number of the 30
pairs under 2 raster px (worst of four phases, ink ≥ 0.5). The last column
counts the distinct pairs under 2 over all four cells. Per-pair rows are in
`evidence/gaps-9-10px.txt`.

| Build | px | light 400 | light 600 | dark 400 | dark 600 | Pairs under 2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| r10 | 9 | 0 (15) | 0 (22) | 0 (23) | 0 (26) | 24 |
| r11 | 9 | 2 (0) | 3 (0) | 2 (0) | 2 (0) | 0 |
| r12 | 9 | 2 (0) | 3 (0) | 2 (0) | 2 (0) | 0 |
| r10 | 10 | 1 (14) | 0 (22) | 0 (19) | 0 (23) | 21 |
| r11 | 10 | 2 (0) | 2 (0) | 2 (0) | 2 (0) | 0 |
| r12 | 10 | 2 (0) | 2 (0) | 2 (0) | 2 (0) | 0 |

- 9 px: r12's per-pair gaps equal r11's in 116 of 120 cell-pairs. The
  other 4 move by 1 raster px (±1-unit advance rounding), and none falls
  under 2.
- 10 px: every r12 gap is r11's or 1 raster px less (mean −0.43), and the
  smallest is still 2. The real r12 font matches the calibration's
  stand-in (r10 with 0.80 px letter-spacing) in 118 of 120 cell-pairs. The
  other 2 are 1 raster px smaller in r12 and still at least 2. That
  confirms the letter-spacing stand-in.

`evidence/item-fade.png` puts its end-of-row markers at the HarfBuzz set
widths, and they land on the browser's row ends (callouts 1–4).

### Size

| Serif | Core TTF | Core WOFF2 | Full TTF |
| --- | ---: | ---: | ---: |
| r10 | 440,036 | 197,980 | 1,207,108 |
| r11 | 556,532 | 245,128 | 1,501,120 |
| r12 | 658,716 | 288,968 | 1,757,604 |

r12 is 43,840 bytes of WOFF2 over r11, the cost of the second fade layer
(section 2, "Size"). Sans, Rounded and Mono are byte-identical to r11.

## 4. Drift

`checks/drift.py` takes INTENDED from r11 and adds one thing:
`FADE_LAYERS = ('fade.12', 'fade.13')`, so each caption master may carry
both layers. It now also compares a layer that both fonts have, the way it
compares a master. A layer that r11 had and r12 drops would be flagged
(none is). Nothing else in INTENDED changed: the caption masters' advance
changes were already intended in r11.

Against r11 (`--ref r11-type`): PASS.

- Sans, Rounded and Mono masters: identical (2985, 141 and 2166 glyphs).
- Serif m03–m08: identical. m00/m01/m02: 1428/1429/1429 of 1509 glyphs
  differ, all in the advance only (+21; outlines, anchors, components and
  glyph libs are unchanged).
- Serif `fade.13` in m00–m02: identical to r11's. `fade.12`: added layer
  (1509 glyphs, the master's glyph set).
- Other serif source files differing: the three caption masters'
  `layercontents.plist` and the designspace.
- Binaries: Sans, Rounded and Mono have no differences. Serif `glyf` and
  `hmtx` have no differences, and HVAR differs. gvar differs in the caption
  regions (opsz −1.000: 555 glyphs) and the new 12 px regions (opsz −0.917:
  554). The 13 px regions (opsz −0.802) are unchanged.

Against r6 (`--list evidence/changed-glyphs.txt`): PASS. The r6 list is
r11's, plus the `fade.12` layers and the caption masters' larger opening.

## Checks

**Build** (`make build`, core subset): the serif is rebuilt, and Sans, Mono
and Rounded come from the cache built from r11's sources.

**Gate** (`make gate`): no hard failures. Every check count is the same as
in r11.

| Face | Pass | Warn | Fail | Error | Interpolation findings |
| --- | ---: | ---: | ---: | ---: | --- |
| Sans | 92 | 4 | 5 | 1 | none |
| Serif | 95 | 5 | 5 | 0 | kink 5 (r11: kink 4) |
| Mono | 90 | 6 | 5 | 1 | none |
| Rounded | 98 | 0 | 2 | 1 | none |

The quality status is FAIL, as in r11, because of the inherited
font-quality findings. Every fontbakery check has the same result as in
r11. Only three messages differ: the build path, the hinting size line, and
the serif's interpolation warning.

The serif's one extra interpolation finding is not a new defect:

- The source-level test steps through the designspace sources in order
  and compares each one with the next. r12's layer sources make one new
  neighbouring pair: `fade.12` of the Bold caption master (900, 12 px)
  next to `fade.13` of the Light one (200, 13 px). On that pair the test
  reports `f.ligalong` contour 1, value 8. That is the same contour and
  value as the inherited finding on caption Bold against text Light,
  which r11 also has.
- The compiled-font warning (fontbakery) lists the same `f_f` kink
  (`f_f f_f_i f_f_j f_f_l f_f_t`, contour 1 point 46) on four location
  pairs instead of r11's two. The new pairs are (900, 8 px) → (200, 12 px)
  and (200, 12 px) → (900, 12 px). r11's (900, 8 px) → (200, 13 px) is now
  (900, 12 px) → (200, 13 px). The test steps through them because the font
  has a new location, 12 px. (The warning prints design opsz with the
  fraction dropped, so 12 px, design 8.9998 after quantising, shows as
  `opsz=8`.)
- At each of the three pairs that involve 12 px, the same test (run on the
  full fonts with `checks/pairkink.py`, outlines drawn at the two
  locations) finds the same five `f_f` kinks in r10, r11 and r12:
  contour 1, value 46, in every build. The
  only other difference is in r12 alone: `eng` on (200, 12 px) → (900,
  12 px), and that glyph is outside the shipped subset (see
  Interpolation). The shipped fonts show nothing new.

**Render** (`make render`): 38 PNGs, blind byte scan PASS. Line contact
is 0: all three headline collision checks (light, dark, glass) are clear
with no touching components, and all 38 sheet checks PASS, as in r11. Sheet
09 (`checks/sheet09.py`, the mono unit signs) gives r11's numbers: ring/°
1.001, side walls 0.995 (℉) and 0.999 (℃), letter widths F 0.998 and
C 1.000, counters 63 and 64 raster px. Its stale r10 line "wall ≤ 2.5
raster px" still reads False, for the reason r11 gives. The mono binary is
byte-identical to r11's.

**Checks** (`make checks`): PASS. The report equals r11's except the
serif's figure advances at its six opsz 8 locations: each is 21 units wider,
and all ten figures stay equal (e.g. 728 at 200 against r11's 707).

- Rounded/Regular ink width (96 px, 400): `104°F`, `72°`, `18:30` and
  `−3°` are all +0.000%.
- Tabular default: Sans PASS (21 locations), Serif INFO (30, tabular),
  Mono PASS (5), Rounded PASS (15), as in r11.

**Confusables** (`checks/figcheck.py`, xor, fail under 0.20, wght 400):
PASS. Sans, Mono and Rounded equal r11. Serif:

| px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9 | 0.329 | 0.311 | 0.218 | 0.574 | 0.476 | 0.587 | 0.753 | 0.718 | 0.662 |
| 11 | 0.293 | 0.264 | 0.276 | 0.582 | 0.444 | 0.578 | 0.604 | 0.680 | 0.649 |
| 13 | 0.348 | 0.282 | 0.250 | 0.581 | 0.481 | 0.603 | 0.623 | 0.758 | 0.667 |

9 px is within 0.003 of r11 and 13 px is equal. At 11 px, `rn/m` falls
from r11's 0.713 to 0.604, because `r` and `n` sit closer again. r10 had
0.522 at 9 px, so this is still well clear of the 0.20 floor. Every other
11 px value is within 0.006 of r11's. The lowest value is still 0.218
(l/I, 9 px). Figure defaults: all four faces PASS. The serif's ten figures
all gain the same 149 units at opsz 8 (728 against r11's 707), so they
stay tabular.

**Skeleton** (`checks/skeleton.py --all`): PASS, output identical to r11
(0 glyphs at or over 4.0; largest region 3.80 / 3.63, mean 0.42, overlap
minimum 0.950).

**Widths** (`checks/widths.py --all`): identical to r11. The largest
difference is 0.00 %.

**Interpolation** (`checks/vfkinks.py`): Sans, Mono and Rounded have 0
findings, and the Rounded test PASSES. The serif lists 20, all the
inherited `f_f` kink on the four location pairs described under Gate (r11:
10 on two pairs). The same test on the full fonts adds `marcaregistrada`
and `uni0418` (both are in r11's full font too). It also adds one glyph
that r11's full font does not have: `eng`, contour 2, between (200, 12 px)
and (900, 12 px). At (900, 12 px), its point 18 turns 4.0° over an
11.8-unit handle, against 1.15° in r11. That comes from rounding the new
layer's points to whole units: about 0.01 px at 12 px. `eng` is not in the
core subset, so no shipped binary has it.

**Outlines** (`checks/outlines.py r12-type`): 0 core outliers (kinks,
fold-backs, points) in all four faces: PASS.

**Binary and shaping** (`checks/bincheck.py`, built fonts against r11):

- Sans, Rounded and Mono TTF and WOFF2: same sha256, and all 19 tables
  equal byte for byte.
- Serif: same table set and glyph order, and the same default-instance
  `hmtx`. HVAR, gvar and `head` (`checkSumAdjustment` only) differ.
- Mono: `a === b !== c => d <= e >= f != g -> h` gives 38 glyphs for 38
  characters by default. `72℉–75℉ 20℃/h` shapes to exactly the glyphs and
  positions of `72°F–75°F 20°C/h` at wght 300–700, with default features,
  ligatures off and the opt-in set.

## Evidence

- `evidence/item-fade.png`: the before/after waterfall and chart.
  - Top: r10 / r11 / r12 serif at 9–13 px, 400, light, as 2× browser crops
    (the sentence, then `quiet sky  minimum  rain returns  0123456789`).
  - Bottom: the sentence's HarfBuzz set width at 8–17 px, in CSS px and in
    em (width per px).
  - Callouts: 1, r11's 12 px row is wider than its 13 px row; 2–4, r12's
    rows at 12, 11 and 13 px; 5, r11's drop between 12 and 13 px; 6, r12's
    width per px stepping down. The legend under the image gives the
    numbers and the gap-table result.
- `evidence/set-widths.txt`: the set-width tables. They cover r10 / r11 /
  r12, all seven strings, weights 300–700, at 9, 10, 11, 12, 13, 14, 15 and
  17 px, with the item 3 and 4 checks.
- `evidence/gaps-9-10px.txt`: the 9 and 10 px gap tables for r10 / r11 /
  r12, per cell and per pair.
- `evidence/changed-glyphs.txt`: drift's list against r6.

## Rules to keep

- **Caption spacing lives in the caption masters and their fade layers,
  on the right sidebearing.** Outlines and anchors don't move, so the
  masters' hand-written kerning and mark positions in `features.fea` stay
  valid.
- **The fade layers are generated, never edited.** `fade_masters` rebuilds
  every `fade.<px>` layer from the current masters as the exact
  interpolation at its size plus its step's opening. Rebuild them with the
  transform after any caption or text master change. They are glyph-only on
  purpose: a full UFO master there would need its own GPOS, and without one
  the variable compile stops ("Base master not found").
- **Keep a zero step at exactly 13 px.** Any fade layer that is not at 13 px
  changes how sizes above it round, and that moves tabular figures by up to
  0.18 %. With `fade.13` as the last step, nothing from 13 px up can drift.
- **9 px is pinned.** `CAPTION_TOTAL` is solved from the first step so that
  9 px keeps r11's 114.5 units. Change a step and the caption opening (and
  8 px) follows; 9 px does not.
- **Check the fade on whole px, not just the steps.** Every px from 9 to 13
  must set wider than the px before and no wider per px. 12 → 13 px allows
  at most about 38 units per glyph at 12 px, and 9 → 10 at least about 50 at
  10 px, because r10's own width per px is almost flat at 8–12 px.
- **Calibrate on the raster, with a margin.** Use letter-spacing on the
  reference build as the stand-in and keep a margin over the first value
  from which every larger one clears.

## Next steps

- **Size.** r12's second fade layer costs about 44 KB of serif WOFF2 over
  r11. If size matters more than exact identity from 13 px up, the
  one-step construction in section 2 (zero at 12.05 px, C = 149) gives the
  same 9 to 12 px spacing at 242,932 bytes, under r11, and misses only
  item 4's 0.1 % on the tabular figures (0.17 %). A cheaper route that
  keeps both is unmeasured: re-encode the serif's variations with the
  caption master modelled before the fade layers, so that a layer's outline
  deltas are zero and only its advance deltas remain. That needs a
  post-compile step, because the compiler's model order can't be set.
  Measure it before adopting it.
- **10 px margin.** 10 px keeps 2 units over the measured floor. Phase
  snapping made the counts uneven below 0.78 px of letter-spacing, so
  don't take more off without measuring again on the same four phases.
- **Other browsers.** All gap measurements are from one headless engine
  with `font-optical-sizing: auto`. A WebKit pass at 9 to 13 px would show
  whether its opsz mapping and sub-pixel snapping agree.
- **Fade-layer rounding.** The compiler rounds each fade layer's
  interpolated points to whole units. On short handles that can bend a
  smooth point: `eng` at (900, 12 px) turns 4.0° instead of 1.15°. That is
  about 0.01 px, and `eng` is outside the core subset. If the full font
  ships, round the layers in `fade_masters` so that each smooth point's
  handles stay on one line: pick among the floor and ceiling candidates
  the one that turns least. Then rerun the full-font kink test against
  r11.
- **More steps are possible but not needed.** A step at 10 or 11 px would
  let 10 px and 11 px move separately. The line through 9 px already gives
  both what the brief asks, and each step costs about 44 KB.

## Rebuild

    .venv/bin/python -I candidates/r12-type/transforms/apply.py serif    # sans masters are r11's, unchanged
    .venv/bin/python -I candidates/r12-type/checks/outlines.py r12-type
    make build CAND=r12-type SUBSET=core ICONS_DIR=…
    make gate CAND=r12-type ICONS_DIR=…
    make render CAND=r12-type OUT=… MAP=… REFS=0 ICONS_DIR=…
    make checks CAND=r12-type ICONS_DIR=…
    python3 -I candidates/r12-type/checks/sheet09.py <render OUT>/<label>-09.png    # needs numpy, scipy and Pillow
    .venv/bin/python -I candidates/r12-type/checks/drift.py r12-type --list candidates/r12-type/evidence/changed-glyphs.txt
    .venv/bin/python -I candidates/r12-type/checks/drift.py r12-type --ref r11-type
    .venv/bin/python -I candidates/r12-type/checks/figcheck.py build/r12-type
    .venv/bin/python -I candidates/r12-type/checks/skeleton.py build/r12-type --all
    .venv/bin/python -I candidates/r12-type/checks/widths.py build/r12-type --all
    .venv/bin/python -I candidates/r12-type/checks/vfkinks.py build/r12-type
    .venv/bin/python -I candidates/r12-type/checks/bincheck.py r12-type r11-type
    .venv/bin/python -I candidates/r12-type/checks/pairkink.py 'wght=200,opsz=12' 'wght=900,opsz=12' r11=<r11 full TTF> r12=<r12 full TTF>    # full TTF: build/<cand>/build.json faces.serif.full_ttf

Run every build, gate, render and check step as a big step under the
machine rules (the serif compile peaks at about 1 GiB).
