# r11-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r10-type. Its decisions hold unless a section below
changes them. Three things change:

- the mono ℉/℃: shaped text now draws the typed `°F`/`°C` pair, and the
  standalone signs fit their cell (item 1);
- the serif's caption spacing at 9–12 px (item 2);
- the serif `?` hook, with `¿` and the double marks following (item 3).

Item 4 (mono hyphen clearance) needed no change: every hyphen already keeps
at least 5 raster px to its neighbours in r6, r10 and r11 (section 4).
Everything else keeps r10's outlines, metrics, kerning and features;
`checks/drift.py` proves it (section 5).

All rendered measurements are per glyph and centre-aligned, never a string
xor between fonts.

- Browser strips are headless renders at device scale 2. A strip draws the
  whole string once per character, each time with every other character
  transparent, so each glyph's ink is measured alone at its shaped position.
  Ink is coverage ≥ 0.5 (≥ 0.25 is also reported). A gap is the smallest run
  of non-ink between two neighbours' ink on any row they share, in raster
  (2×) px, worst case over sub-pixel phases: four for the serif (0, ¼, ½,
  ¾ px) and two for the mono (0 and 0.37 px).
- Sheet 09 and sheet 21 values are from the specimen render (`make render`,
  2×).
- The `?` taper is measured on the sources, along the curves.

Before/after images are in `evidence/`, with numbered callouts explained
under each image.

## Summary

| Item | Result |
| --- | --- |
| 1. Mono ℉/℃ | `ccmp` turns ℉/℃ into `degree F`/`degree C`. HarfBuzz gives the same glyphs at the same positions as typed `°F`/`°C` (default, ligatures off and opt-in, 300–700). In the browser, r11 draws `72℉–75℉ 20℃/h` pixel-identical to `72°F–75°F 20°C/h` in all 120 cells (13/15/17/24 px, 300–700, light and terminal, three feature sets). The standalone signs' ink stays inside 0–1217. Every advance is 1217. `endash.unit` and `slash.unit` are retired. |
| 2. Serif 9–10 px | The caption masters open by 128 units per glyph, fading to nothing at 13 px. At 9 px, pairs under 2 raster px (of 30): r6 22, r10 24, r11 0 (smallest gap 2); at 10 px r10 21, r11 0. Set width at 13/15/17 px is within 0.1% of r10, and every advance at 20 px and above equals r10's. |
| 3. Serif `?` | The inner curve of the hook is one cubic. The largest step away from an even taper is 4–12 units (r10: 29–68). It has 32 points (r10: 34). Advances are unchanged, and `¿` and the double marks follow as components. |
| 4. Mono hyphen | No change needed. The smallest hyphen gap is 5 raster px in r6, r10 and r11. |
| 5. Everything else | Drift passes against r10 and against r6. |

## 1. Mono ℉ and ℃: the typed pair wherever text is shaped

### Why
The last review measured r10's ℉ ring at 12 × 12 raster px against 16 × 16 for
the typed `°F`, and r10's ℃ C at 17 px wide against 21 px for the typed C.
The r10 binary shows why no one-cell drawing can match: the typed degree ink
is 637 units wide, F 792 and C 831, and the cell is 1217 (upm 1950). r10's
℉ ink already ran to x = 1287 (Light) and 1381 (Bold), and ℃ to 1264 and
1318, past the advance.

### Change (`transforms/mono.py`)
- **`unit_decompose`.** A multiple substitution (GSUB type 2) in `ccmp`, on
  by default: `uni2103` → `degree C`, `uni2109` → `degree F`. It is the
  first lookup in the feature file, inserted right after the
  `languagesystem` statements, so it is registered for every script and
  language and runs before every `calt`, `liga`, `dlig` and `ss11` lookup.
  A shaped ℉ is therefore the same two glyphs as a typed `°F`, in the same
  two cells, and anything after it sees `F`/`C`, exactly as after the typed
  pair.
- **Followers retired.** `endash.unit` and `slash.unit` (r10's contextual
  forms after a unit) can no longer fire: by the time `calt` runs, no
  `uni2103`/`uni2109` is left in the glyph run. They and their `unit_follow`
  lookup are gone from the sources and the binary; against r6 the glyph
  order is r6's again.
- **Standalone signs (`TEMP_MODE = 'cell'`).** `uni2103`/`uni2109` are still
  in the cmap (where no shaping happens: a raw glyph dump, an old renderer).
  Their ring contours are r10's, point for point (round, height 0.74 of the
  degree sign at 300 and 0.705 at 700, wall `WALL` 0.39). The letter is the
  face's own condensed C or F, one width rule for both letters as in r10,
  but the share is now solved per master (`temp_fit_width`, bisection) so
  that the wider letter, F, ends at 0.97 of the cell (`MARGIN` 0.03): 0.666
  of the face's letter at 300 and 0.574 at 700 (r10: 0.80, overflowing).
  Ink is 0–1180 for ℉ and 0–1157 / 12–1122 for ℃ (300 / 700); every
  advance stays 1217.

### Results
Binary (`StrataMono.ttf` and `.woff2`, read back with fontTools):

- cmap: U+2103 → `uni2103`, U+2109 → `uni2109`. Every non-zero advance is
  1217.
- GSUB lookup 2 is the type-2 decomposition. It is the first lookup of
  `ccmp` (lookups 2, 307, 309) in all 14 language systems, and it comes
  before the first `calt` lookup (113) and every `liga`/`dlig` lookup.
- `endash.unit` and `slash.unit` are not in the glyph order.

HarfBuzz, wght 300, 400, 500, 600 and 700: `72℉–75℉ 20℃/h` and
`72°F–75°F 20°C/h` shape to the same 16 glyphs (`seven two degree F endash
seven five degree F space two zero degree C slash h`) at the same positions,
with default features, with `calt`/`liga`/`dlig` off, and with the opt-in
`dlig` + `ss11`.

Browser (headless, 2×): each font draws `72℉–75℉ 20℃/h` and
`72°F–75°F 20°C/h` in the same cell, and the two images of the same font
are compared pixel by pixel. Cells are 13, 15, 17 and 24 px × wght 300,
400, 500, 600 and 700 × light and terminal, 40 per feature set:

| Font | Features | Cells that differ | Differing px |
| --- | --- | ---: | ---: |
| r6 | default | 40/40 | 155,513 |
| r10 | default | 40/40 | 156,721 |
| r11 | default | 0/40 | 0 |
| r11 | ligatures off | 0/40 | 0 |
| r11 | opt-in (`dlig` + `ss11`) | 0/40 | 0 |

`evidence/item1-units.png` shows the 24 px and 13 px cells and the
difference mask (callouts 1–4), and the standalone signs in their cells
(callouts 5–6).

Sheet 09 (`make render`, 24 px at 2×, `checks/sheet09.py`): the specimen's
`℉ / °F  ℃ / °C` row is shaped, so its ℉ and ℃ are now the typed pair.

| | r10 | r11 | Typed pair |
| --- | --- | --- | --- |
| Ring height against the typed ° | smaller (last review: 12 × 12 vs 16 × 16 px) | 1.001 | 1 |
| Side wall against the typed ° | 2 raster px | 0.995 (℉), 0.999 (℃) | 1 |
| Letter width against the typed letter | F 0.804, C 0.809 | F 0.998, C 1.000 | 1 |
| Counter | 57 raster px | 63 (℉), 64 (℃) | the typed ° |

`sheet09.py` still prints r10's acceptance line, and its "wall ≤ 2.5 raster
px" now reads False: the wall it measures is the typed degree's own (5 and
4 raster px on the middle scanline). That rule was for r10's in-cell ring,
which now shows only where nothing is shaped (see Rules to keep).

Standalone signs (`renders-self` cells in `evidence/item1-units.png`): the
ring is r10's, point for point, so it is as round (outline aspect
0.998–1.000) and as open as r10's. Ink runs from 0 to 1180 (℉) and
0–1157 / 12–1122 (℃, 300 / 700), inside the 1217 cell; r10's ran to 1287
and 1264.

Gate: Mono counts are r10's (90 pass, 6 warn, 5 fail, 1 error) with the
same messages, so there is no new monospace or advance finding.

## 2. Serif 9–10 px: open caption spacing that fades out by 13 px

### Why
At 9 px the last review saw letters touch in `quiet sky`, `minimum`, `rain
returns` and the figures. Measured in the browser at 2× on r10 (per glyph,
each character drawn alone with the others transparent, ink = coverage
≥ 0.5, worst of four sub-pixel phases, weights 400 and 600, light and
dark): 24 of the 30 pairs come under 2 device px, 12 of them at 0
(`ky mi ni um ra ai tu rn ns 34 45 56`). r6 had 22 pairs under 2.

### Calibration
The same r10 strip with CSS letter-spacing stands in for an opening at the
caption master, since an opening of d units there adds
2·d·0.895·9/1000 px at 9 px (0.895 is the caption share at 9 px with the
fade masters). Pairs under 2 device px, worst over everything above:

| Variant | Pairs under 2 px (ink ≥ 0.5) | Smallest gap | Pairs under 2 px (ink ≥ 0.25) |
| --- | ---: | ---: | ---: |
| r6 | 22 | 0 | 25 |
| r10 | 24 | 0 | 26 |
| r10 + 0.25 px | 19 | 0 | 23 |
| r10 + 0.50 px | 12 | 1 | 19 |
| r10 + 0.75 px (46 units) | 1 (`34` = 1) | 1 | 7 |
| r10 + 1.00 px (62 units) | 0 | 2 | 0 |
| r10 + 1.25 px | 0 | 2 | 0 |
| r10 + 1.50 px | 0 | 3 | 0 |
| r10 + 2.00 px | 0 | 4 | 0 |

(30 pairs × weights 400/600 × light/dark = 120 measured pairs per row.)

Letter-spacing 1.0 px (an opening of 62 units) is the first step with no pair under 2;
`CAPTION_OPEN` is 64 (two units of margin), so each caption glyph opens by
128 units, which is 1.03 px (2.06 device px) at 9 px and 1.01 px at 10 px.

### Change (`transforms/serif.py`, `caption_open`, `fade_masters`; `apply.py`)
- **Opening.** In the three caption masters (m00–m02, opsz 8), every glyph
  with ink and an advance of at least 100 units, except marks, gains
  2 × `CAPTION_OPEN` = 128 units on its right sidebearing. The four spaces
  (U+0020, U+00A0, U+2007, U+2008) gain the same, so word spaces keep their
  share of the line. Outlines and anchors don't move, so every kerning
  value and mark position in the masters' own `features.fea` still applies.
- **Fade.** Without another master, the opening would fall off linearly up
  to opsz 20, and 13 px would still carry 0.80 of it. So the r10 design is
  pinned at 13 px: `fade_masters` writes a glyph-only layer `fade.13` into
  each caption master. Each glyph there is r10's interpolation at user
  opsz 13 (design 10.375) between the caption master and the text master
  of the same weight (m00 → m03, m01 → m04, m02 → m05). `add_fade_sources`
  adds the three layers to the designspace as layer sources at that
  location. The opening is then full at 8 px, 0.895 of full at 9 px, 0.789
  at 10 px, 0.579 at 12 px and 0 from 13 px up.
- **Why layers, not masters.** Each serif master carries its own
  hand-written GPOS (kerning and marks) in `features.fea`. A full extra
  master would need its own; with an empty one the variable compile stops
  ("Base master not found"). A glyph-only layer source compiles as a
  sparse master: only glyf, gvar and HVAR gain the region, and GPOS still
  interpolates between the masters' own features, as in r10.
- **Rounding.** Point coordinates and advances in the layers are whole
  units, so between 13 and 20 px an instance can differ from r10 by one
  unit. At 20 px and above it cannot, because the layers don't act there.

### Results
Smallest gap at 9 px (raster px at 2×, ink ≥ 0.5, worst of four phases),
and how many of the 30 pairs come under 2:

| Theme, weight | r6 | r10 | r11 |
| --- | --- | --- | --- |
| light 400 | 1 (12 under 2) | 0 (15) | 2 (0) |
| light 600 | 1 (18) | 0 (22) | 3 (0) |
| dark 400 | 0 (18) | 0 (23) | 2 (0) |
| dark 600 | 0 (24) | 0 (26) | 2 (0) |
| any (distinct pairs under 2) | 22 | 24 | 0 |

At 10 px (r6 not measured):

| Theme, weight | r10 | r11 |
| --- | --- | --- |
| light 400 | 1 (14 under 2) | 2 (0) |
| light 600 | 0 (22) | 2 (0) |
| dark 400 | 0 (19) | 2 (0) |
| dark 600 | 0 (23) | 2 (0) |
| any (distinct pairs under 2) | 21 | 0 |

With ink ≥ 0.25: at 9 px r6 25, r10 26, r11 0 pairs under 2 (r11's
smallest gap 2); at 10 px r10 25, r11 1 (`tu` = 1).
`evidence/item2-serif9.png` shows `ky`, `mi`, `rn` (600 dark) and `34`
(callouts 1–4).

Set width (HarfBuzz advances with kerning, opsz = px, seven strings from
`quiet sky` to a full forecast sentence), largest |r11 / r10 − 1|:

| px | 300 | 400 | 500 | 600 | 700 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9 | 22.1% | 21.9% | 21.8% | 21.5% | 21.4% |
| 10 | 19.6% | 19.4% | 19.2% | 19.0% | 18.9% |
| 12 | 14.4% | 14.2% | 14.1% | 14.0% | 13.9% |
| 13 | 0.016% | 0.000% | 0.021% | 0.003% | 0.007% |
| 15 | 0.005% | 0.097% | 0.013% | 0.057% | 0.021% |
| 17 | 0.004% | 0.011% | 0.014% | 0.004% | 0.000% |
| 20, 24, 48 (400, 600) | | 0.000% | | 0.000% | |

At 9 px 400, `n` goes from 724 to 838 units, `o` from 646 to 760, `zero`
from 591 to 706 and the space from 262 to 376.

Advances at opsz 13–60, wght 200–900: of 40,608 glyph instances, 2,276
differ from r10, all by one unit and all at opsz 13–17 (386 at 13, 815 at
14, 604 at 15, 471 at 17), the rounding described above. At 20 and above
none differ.

## 3. Serif `?` and `¿`: one even taper into the stem

### Why
In r6 and r10 the inside of the hook's turn was two short lines (points 10
and 11) between curve ends that nearly meet points 9 and 12, so at the turn
four on-curve points sit within a few units of each other and the stroke
narrows abruptly, then stays flat, then swells again before the stem.
Measured as the distance from the inner curve to the outer arc, sampled at
21 even steps along the inner curve (`lab/taper.py`):

| Master | r6 | r10 | r11 | r11 thickness, hook → stem (units) |
| --- | ---: | ---: | ---: | --- |
| m00 (8, Light) | 41.1 | 45.7 | 4.8 | 75 → 24 |
| m01 (8, Regular) | 47.8 | 59.4 | 4.2 | 121 → 90 |
| m02 (8, Black) | 31.3 | 44.1 | 8.4 | 177 → 63 |
| m03 (20, Light) | 34.6 | 34.6 | 5.4 | 57 → 19 |
| m04 (20, Regular) | 68.2 | 68.2 | 4.2 | 114 → 42 |
| m05 (20, Black) | 38.5 | 38.5 | 10.0 | 166 → 61 |
| m06 (60, Light) | 28.8 | 28.8 | 8.6 | 41 → 29 |
| m07 (60, Regular) | 58.0 | 58.0 | 5.0 | 84 → 54 |
| m08 (60, Black) | 67.0 | 67.0 | 11.5 | 126 → 71 |

The first three columns are the largest step away from an even taper
(units). In every r6 and r10 master the thickness also rose again along
the curve (1–11 rises of more than 1 unit). In r11 it falls steadily in
seven masters. Two keep a residue:

- m06 (display Light) thins to 30 units, then swells back to 37 before
  falling to 29 at the stem (r10 also swelled, and was 28.8 units off an
  even taper);
- in m08 the last sample, where the curve meets the stem, rises 3 units.

### Change (`transforms/serif.py`, `question_hook`)
- Points 10 and 11 are removed; the inner curve is one cubic from the end
  of the hook's inside to the top of the stem.
- The outer handle leaves the hook at `Q_TANGENT` (15°), and the inner
  curve's two handle lengths are fitted per master (a grid search over
  `Q_HANDLE` 0.25–0.75 of the span in `Q_STEPS` 50 steps) so the thickness
  falls at an even rate from the hook to the stem. Fit rms per master:
  m00 2.7, m01 3.1, m02 4.2, m03 3.3, m04 2.1, m05 5.3, m06 4.5, m07 2.3,
  m08 8.1 units.
- Every master gets the same edit (32 points instead of 34 in each), so the
  masters stay compatible. `questiondown.cap` is `question` turned 180°
  (an upstream component), `questiondown` is that component lowered, and
  `questiondbl`, `questionexclam` and `exclamquestion` place `question` as a
  component, so all five follow without edits of their own. No advance
  changes.

### Results
- Points: 32 in all nine masters (r10: 34), so the masters stay
  compatible. The pair of on-curve points at the turn (10 and 14, under
  40 units apart in r6/r10 m02 and m05) is gone. The other close on-curve
  pairs are r10's own (the stem's foot and the neck, and across the thin
  Light strokes), renumbered.
- Advances: unchanged in every master and in the binary (`question`,
  `questiondown`, `questiondown.cap` in the core build; the double marks
  are components in the sources).
- Sheet 21 (the outline sheet, 2×): one smooth inner curve, no point
  cluster at the turn (`evidence/item3-question.png`, callout 5).
- Browser renders (2×, light), `evidence/item3-question.png`: at 96 px
  400 r10's stroke narrows at the turn, stays flat and swells before the
  stem (callout 3); r11's thins at an even rate (callout 4), and `¿`
  follows. At 48 px 700 and 13 px 400 the string `? ¿ ?? ?! !? Rain?` sets
  at r10's width (advances equal); at 13 px the change is not visible.

## 4. Mono hyphen clearance: measured, no change

`--hourly`, `a-b` and `x--y` at 13, 15 and 17 px, weights 300–700, light
and terminal themes, two sub-pixel phases, with default features,
ligatures off (`calt`, `liga` and `dlig` off) and opt-in (`dlig` and
`ss11`). The table gives the smallest gap from each hyphen to its
neighbour, in raster px (ink ≥ 0.5; ≥ 0.25 gives the same minimum, 5):

| String | Pair | Default (r6 / r10 / r11) | Ligatures off | Opt-in |
| --- | --- | --- | --- | --- |
| `--hourly` | `--` | joined / 8 / 8 | 8 / 8 / 8 | joined / joined / joined |
| `--hourly` | `-h` | 5 / 5 / 5 | 5 / 5 / 5 | 5 / 5 / 5 |
| `a-b` | `a-` | 6 / 6 / 6 | 6 / 6 / 6 | 6 / 6 / 6 |
| `a-b` | `-b` | 5 / 5 / 5 | 5 / 5 / 5 | 5 / 5 / 5 |
| `x--y` | `x-` | 8 / 8 / 8 | 8 / 8 / 8 | 8 / 8 / 8 |
| `x--y` | `--` | joined / 7 / 7 | 7 / 7 / 7 | joined / joined / joined |
| `x--y` | `-y` | 6 / 6 / 6 | 6 / 6 / 6 | 6 / 6 / 6 |

`evidence/item4-hyphen.png` shows `--hourly`, `x--y` and the opt-in
`--hourly` at 17 px 700, and `a-b` at 13 px 300 in the terminal theme
(callouts 1–4).

"joined" means the two hyphens are one ligature glyph (the opt-in `--`, and
in r6 also the default one), so there is no gap to measure. The goal is
2 raster px. Every hyphen in r6, r10 and r11 keeps at least 5, so the hyphen
is r10's. The dashes stay distinct by length: hyphen ink 609 units, minus
913, en dash 1079 (cell 1217, all r10's).

## 5. Everything else

`checks/drift.py` compares the sources (every master and layer) and the
built binaries (glyf, hmtx, gvar per region, whole tables) with a reference.
Its intended list is exactly r10's list plus this round's items 1–4:

- item 1: `uni2103`, `uni2109` in both mono masters, the `ccmp` lookup in
  `features.fea`, and the retired `endash.unit`/`slash.unit`;
- item 2: the new `fade.13` layer in serif m00–m02 (which must have the
  master's glyph set), every glyph of m00–m02 (right sidebearing, advance
  only), the designspace's three layer sources, and in the binary the new
  gvar region at the fade location, the changed caption regions and HVAR;
- item 3: `question` in all nine serif masters;
- item 4: nothing.

Against r10 (`--ref r10-type`): PASS.

- **Sans and Rounded:** identical in all nine masters and in both binaries.
- **Serif:** `question` in m03–m08; 1428–1429 of 1509 glyphs in m00–m02
  (the opening, plus `question`); one new layer in each of m00–m02;
  the designspace and three `layercontents.plist` files. In the binary, the
  default glyf changes only for `question`, and hmtx does not change. gvar
  changes for 555 glyphs, in the caption regions and the new region
  `opsz = −0.802` (13 px). HVAR is the only other table that differs:
  GPOS and GDEF are byte-identical.
- **Mono:** four glyphs in both masters: `uni2103`, `uni2109`, and the
  retired `endash.unit` and `slash.unit`. `features.fea` and `lib.plist`
  change. In the binary only the glyf and gvar of `uni2103` and `uni2109`
  change, and hmtx does not. GSUB, post and maxp change for the new lookup
  and the two retired glyphs.

Against r6 (`--list evidence/changed-glyphs.txt`): PASS. The full list for
each master is in `evidence/changed-glyphs.txt`. The mono glyph order is
r6's again (the r10 followers are gone), so against r6 only `uni2103`,
`uni2109`, GSUB and the `name` table differ. The Rounded changes are r10's.

## Checks

**Gate** (`make gate`): no hard failures. Every count is the same as r10.

| Face | Pass | Warn | Fail | Error | Interpolation findings |
| --- | ---: | ---: | ---: | ---: | --- |
| Sans | 92 | 4 | 5 | 1 | none |
| Serif | 95 | 5 | 5 | 0 | kink 4 (r10: kink 4) |
| Mono | 90 | 6 | 5 | 1 | none |
| Rounded | 98 | 0 | 2 | 1 | none |

The report's quality status is FAIL, as in r10, because of the inherited
font-quality findings (same counts, and the same messages except one).
The serif's interpolation message now lists each `f_f` ligature kink on
two location pairs instead of one. The second pair is new only because
the font has a new location to step through (caption Bold → 13 px Light).
The same test on r10 at those two locations finds the same five kinks
(`f_f f_f_i f_f_j f_f_l f_f_t`, contour 1 point 46), so no new defect.
Name records and figure gates PASS. Icons PASS and are byte-identical to
`build/r10-type/icons` (8,000 bytes; r10's gate report shows 7,828
because it ran before r10's icon rebuild). WOFF2 sizes: Serif 245,128
bytes (r10: 197,980; see Next steps), Mono 47,804 (r10: 47,856). Sans and
Rounded are unchanged.

**Render** (`make render`): 38 PNGs, blind byte scan PASS. Line contact
is 0: all three headline collision checks are clear, and no sheet check
fails.

**Checks** (`make checks`): PASS.

- Rounded/Regular ink width (96 px, 400): `104°F`, `72°`, `18:30` and
  `−3°` are all +0.000%.
- Tabular default: Sans PASS (21 locations), Serif INFO (30, tabular),
  Mono PASS (5), Rounded PASS (15), as in r10.

**Confusables** (`checks/figcheck.py`, xor, fail under 0.20, wght 400):
PASS.

| Face | px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.680 | 0.379 | 0.545 | 0.496 | 0.679 | 0.619 | 0.652 | 0.499 | 0.642 |
| Sans | 13 | 0.735 | 0.407 | 0.595 | 0.541 | 0.738 | 0.655 | 0.519 | 0.520 | 0.670 |
| Serif | 9 | 0.327 | 0.308 | 0.218 | 0.574 | 0.476 | 0.586 | 0.754 | 0.719 | 0.662 |
| Serif | 13 | 0.348 | 0.282 | 0.250 | 0.581 | 0.481 | 0.603 | 0.623 | 0.758 | 0.667 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.520 | 0.467 | 0.613 | 0.817 | 0.357 | 0.639 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.554 | 0.477 | 0.651 | 0.871 | 0.379 | 0.673 |
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.552 | 0.648 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.572 | 0.689 |

The 11 px rows are in the check's output. Sans, Mono and Rounded equal
r10. In the serif, the 9 px `rn/m` rises from 0.522 to 0.754 (the opened
spacing separates `r` from `n`); every other serif value is within 0.007
of r10. The lowest value is 0.218 (Serif l/I at 9 px; r10 0.217). Figure
defaults: all four faces PASS (tnum equals default, ten equal advances,
pnum varied where it applies). The serif's ten figures all gain the same
128 units at opsz 8, so they stay tabular.

**Skeleton** (`checks/skeleton.py --all`, Rounded against the sans at
opsz 14, fail at 4.0): PASS, 0 glyphs at or over 4.0. Over 135 glyphs,
the largest region is 3.80 (400) / 3.63 (900), both G, the mean is 0.42
at 400 and the overlap minimum is 0.950, all as in r10. ℉ stays at
3.68 / 3.34.

**Widths** (`checks/widths.py --all`): Regular against Rounded advances
at 10 locations × 16 strings. The largest difference is 0.00%.

**Interpolation** (`checks/vfkinks.py`): Sans, Mono and Rounded have 0
findings, and the Rounded test PASSES. The serif lists 10, all the
inherited `f_f` kink at opsz 8: the five r10 lines plus the same five
glyphs on the new location pair described under Gate.

**Outlines** (`checks/outlines.py`): 0 core outliers (kinks, fold-backs,
points) in all four faces: PASS.

**Binary and shaping** (built Mono):

- `a === b !== c => d <= e >= f != g -> h` gives 38 glyphs for 38
  characters by default, with no multi-character cluster. With the opt-in
  `dlig` + `ss11` it gives 38 glyphs with the operator ligatures and
  spacers.
- cmap, hmtx and GSUB: see section 1.
- Sans, Rounded and Serif ℉/℃ shape exactly as in r10 (same glyphs and
  positions), and their outlines are unchanged (section 5).
- No reserved name appears in any face's name table (gate names PASS).

## Evidence

- `evidence/item1-units.png`: r6 / r10 / r11 mono, shaped
  `72℉–75℉ 20℃/h` against typed `72°F–75°F 20°C/h` at 24 px 400 (light)
  and 13 px 700 (terminal), with the 24 px pixel difference. Below it are
  the standalone ℉ (300) and ℃ (700) cells with their 1217 advance.
  Callouts 1–6.
- `evidence/item2-serif9.png`: r6 / r10 / r11 serif at 9 px: `quiet sky`,
  `minimum`, `rain returns` and the figures, with the tightest r10 pair of
  each marked and measured. Callouts 1–4.
- `evidence/item3-question.png`: r6 / r10 / r11 `?` outline (text master),
  and `? ¿ ?? ?! !? Rain?` at 96, 48 and 13 px, plus the r11 cell of
  outline sheet 21. Callouts 1–5.
- `evidence/item4-hyphen.png`: r6 / r10 / r11 mono `--hourly`, `x--y` and
  `a-b` with default, opt-in and no ligatures, the measured pair marked.
  Callouts 1–4.
- `evidence/changed-glyphs.txt`: drift's list against r6.

The legend under each image explains its callouts. All crops are 2×
browser renders; zoomed panels use nearest-neighbour scaling.

## Rules to keep

- **Shaped ℉/℃ are the typed pair.** The `ccmp` decomposition must stay the
  first lookup of every language system, ahead of every `calt`, `liga`,
  `dlig` and `ss11` lookup. Never add a contextual form keyed on `uni2103`
  or `uni2109`: by the time `calt` runs they are gone. A follower for a
  unit is a follower for `F`/`C`.
- **The standalone signs stay in the cell.** They only show where nothing
  is shaped, so they need not match the typed pair. They keep r10's ring
  points, and the letter share is solved per master so that the F ends at
  0.97 of the cell. Re-solve it after any change to the mono C or F.
- **Caption spacing lives in the caption masters, on the right
  sidebearing.** Outlines and anchors don't move, so the masters'
  hand-written kerning and mark positions in `features.fea` stay valid.
  Moving the left sidebearing would need every anchor and `pos` in the
  three caption feature files moved with it.
- **The fade layers are generated, never edited.** `fade_masters` rebuilds
  `fade.13` from the current masters as r10's interpolation at 13 px.
  Rebuild them with the transform after any caption or text master change.
  They are glyph-only on purpose: a full UFO master there would need its
  own GPOS, and without one the variable compile stops ("Base master not
  found").
- **Calibrate spacing on the raster.** Use letter-spacing on the reference
  build as a stand-in, convert with the caption share at that size
  (2 × d × share × px / 1000), and keep a margin over the first step that
  clears every pair.
- **One inner cubic in the `?` hook.** Any edit to `question` must keep all
  nine masters at the same point structure (32 points) and recheck
  `questiondown.cap`, `questiondown`, `questiondbl`, `questionexclam` and
  `exclamquestion`, which are built from it.

## Next steps

- **12 → 13 px.** The opening falls from 0.58 of its full value at 12 px to
  0 at 13 px: set width against r10 is +14% at 12 px and +0% at 13 px.
  Check the two sizes side by side in the next review. Moving the fade layer to 14 px would smooth the step, but it
  would open 13 px by about a third of the full amount, far past this
  round's 1% limit there. That needs the owner's call.
- **WOFF2 size.** The new region stores full deltas for the caption glyphs:
  the serif WOFF2 grows from 197,980 to 245,128 bytes (+24%). Subsetting the
  fade layer to the glyphs that actually differ from a straight
  interpolation would not help, because every opened glyph differs.
- **Mono `--` heights.** With default features, `--hourly` draws the
  first hyphen as `hyphen` (ink 576–693) and the second as `hyphen.lc`
  (495–612): `calt` lowers a hyphen next to a lowercase letter, so the
  pair steps by 81 units (0.7 px at 17 px). This is r10's behaviour and
  the clearance is fine. If a review flags the step, lower a hyphen that
  is followed by a lowered hyphen too.
- **Serif `?` in display Light.** In m06 the inner curve thins to 30 units
  and swells back to 37 before the stem (r11 is 8.6 units off an even
  taper there, r10 28.8). One cubic against r10's outer arc cannot do
  better in that master. A fix would also reshape the outer arc in m06
  only.
- **Figure space in the caption masters** is 16 units wider than the
  figures (r9's caption tightening skipped it). r11 keeps r10's difference.
  Fix it with the caption spacing if tabular columns at 9 px are reviewed.
- **Standalone ℃ in Bold.** To fit the cell, its C is 0.574 of the face's C
  at 700. It only shows where nothing is shaped, but it is narrow.

## Rebuild

    .venv/bin/python -I candidates/r11-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r11-type/checks/outlines.py r11-type
    make build CAND=r11-type SUBSET=core ICONS_DIR=…
    make gate CAND=r11-type ICONS_DIR=…
    make render CAND=r11-type OUT=… MAP=… REFS=0 ICONS_DIR=…
    make checks CAND=r11-type ICONS_DIR=…
    python3 -I candidates/r11-type/checks/sheet09.py <render OUT>/<label>-09.png    # needs numpy, scipy and Pillow
    .venv/bin/python -I candidates/r11-type/checks/drift.py r11-type --list candidates/r11-type/evidence/changed-glyphs.txt
    .venv/bin/python -I candidates/r11-type/checks/drift.py r11-type --ref r10-type
    .venv/bin/python -I candidates/r11-type/checks/figcheck.py build/r11-type
    .venv/bin/python -I candidates/r11-type/checks/skeleton.py build/r11-type --all
    .venv/bin/python -I candidates/r11-type/checks/widths.py build/r11-type --all
    .venv/bin/python -I candidates/r11-type/checks/vfkinks.py build/r11-type

Run every build, gate, render and check step as a big step under the
machine rules (the serif compile peaks at about 1 GiB).
