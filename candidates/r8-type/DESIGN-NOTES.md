# r8-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r6-type, the incumbent. Its decisions hold unless a
section below changes them. Two r7 pieces are ported: the mono ℉/℃ inset
ring and the serif's small-size weight. r7's round-top Rounded 3 and its
degree-gap change are not ported. Every glyph outside those two pieces keeps
r6's outlines in every master and in the built binaries. `checks/drift.py`
proves that; it is new this round.

All rendered measurements are from the specimen renderer at device scale 2, per glyph and
centre-aligned (no string-level xor between fonts). Unless a row says
otherwise, each value is the worst case over four horizontal sub-pixel phases
and four vertical offsets. Before/after images for each item are in
`evidence/`, with numbered callouts explained under each sheet.

## Summary

| Item | Change | r6 → r8 (rendered) | Target | Met |
| --- | --- | --- | --- | --- |
| 1a Mono ℉ ℃ ring | r7's inset ring: the face's own degree sign, scaled to 0.93 of its height, walls 0.97 of its walls, on the cell's left edge; letter r6's, 1.20 px from the ring | Ring outer height 0.67–0.74 → 0.92–0.93 of the typed `°`; ring wall 0.48–0.54 → 0.96–1.02 of the `°` wall; letter height 1.00; ring–letter gap ≥ 1.00 px at 13, 15 and 17 px, 300–700, every phase; no contact | Height ≥ 0.90, wall ±10%, letter 1.00 ± 0.02, gap ≥ 1 px, no contact | Yes |
| 1b Serif 9–13 px | r7's opsz 8 weight: `CAPTION_STEM`, `HAIR` 11, `THIN_GAIN` 26/34, short lines kept in direction | Ink on sheet 05 against r6, 400: 9 px +10.88%, 11 px +10.24%, 13 px +8.89% (r7 +10.78, +10.20, +8.93). Sizes ≥ 24 px: +0.00% | Within ±1 pp of r7 at 9–13 px; ≥ 24 px within ±0.1% of r6 | Yes |
| 2 Outline hygiene | Quadratic splits pinned to r6's (`keep_splits`); `checks/drift.py` | Default glyf changed against r6: serif 0 (r7: 64), mono 2 (the units). gvar changes only in regions that peak at opsz 8 (serif) and in the two units (mono). Sans and Rounded binaries identical to r6 | Changed list = intended list | Yes |
| 3 Mono letter width | Three constructions tried (`inset`, `fit`, `small`) | Best Bold letter width 0.75 / 0.81 of composed F / C (`small`), which shrinks the ring to 0.81 and closes its counter at some sizes; `fit` clears the en dash but its Bold letter is 0.68 / 0.72 | Letter ≥ 0.85, ring ≥ 0.80, wall ±10%, gap ≥ 1 px, Bold ℉ + – or / ≥ 1 px | No construction meets all; item 1's ring is kept (table in section 3) |
| 4 Everything else | None | Sans, Rounded (flat-top 3) and the other serif and mono glyphs identical to r6 in sources and binaries | Byte-identical outlines | Yes |

## 1. Port of r7's ring and small serif

### 1a. Mono ℉ and ℃

**What r6 had.** r6 drew the ring as an ellipse with 0.865 of the degree
sign's counter and half its walls. On the render it measured about
0.67–0.74 of the typed `°` and 0.48–0.54 of its wall, so a ℉ read lighter
and smaller than a composed `°F` beside it.

**The port.** `transforms/mono.py` now carries r7's `temp_unit7` and its
`TEMP_R7` table, with `TEMP_MODE = 'inset'`. The ring is the face's own
degree sign: both contours are scaled about its centre. The outer one goes
to `RING_H` 0.93 of the degree sign's height and `RING_W` (0.82 Light, 0.77
Bold) of its width. The inner one keeps `WALL` 0.97 of the degree sign's
side and top walls. The ring's top stays on the degree sign's top. The Light
ring's ink starts on the cell's left edge (x 0); the Bold ring's at x 37 of
1217. The letter is r6's: the face's C or F at full cap
height, condensed in x and emboldened back to its stems. It sits `GAP` 1.20
px of nearest ink from the ring at 13 px, and may pass the right edge by
`OVER` (0.07 Light, 0.10 Bold of a cell). The advance stays 1217 units.

The ported mono binary is identical to r7's in `uni2103` and `uni2109` (glyf
and gvar); every other mono glyph is r6's.

**Measured on the 13/15/17 px strip** (`℉ °F  ℃ °C  0℉–  ℉/  21℉  21°F`,
300–700, every phase):

| | r6 | r8 | Target |
| --- | ---: | ---: | --- |
| Ring outer height / typed `°` (soft) | 0.67–0.74 | 0.92–0.93 | ≥ 0.90 |
| Ring wall / `°` wall | 0.48–0.54 | 0.96–1.02 | 0.90–1.10 |
| Letter height / mono F, C | 1.00 | 1.00 (0.999–1.001) | 1.00 ± 0.02 |
| Ring–letter gap, worst phase | 0.91–1.50 px | 1.00–1.50 px | ≥ 1 px |
| Ring–letter contact | 0 | 0 | 0 |
| Figure before the unit (`0℉`), nearest ink | ≥ 1.00 px | ≥ 1.00 px | not gated |

**Measured on sheet 09** (mono waterfall, light; the repertoire row
`℉ / °F   ℃ / °C`, 24 px, Regular), in raster px at 2x, each glyph cut at its
own box, ink at coverage ≥ 0.5:

| | r6 | r7 | r8 |
| --- | --- | --- | --- |
| ℉ ring w × h (typed `°` 16 × 16) | 11 × 12 | 13 × 15 | 13 × 15 |
| ℃ ring w × h | 12 × 12 | 13 × 15 | 13 × 15 |
| Ring height / `°` (raster px; soft) | 0.75; 0.73 | 0.94; 0.93 | 0.94; 0.93 |
| Ring walls, left / right (`°`: 4 / 4) | ℉ 2 / 2, ℃ 3 / 2 | 4 / 4 | 4 / 4 |
| Letter height / composed letter | 1.00 | 1.00 | 1.00 |
| Ring–letter blank columns | ℉ 4, ℃ 2 | ℉ 4, ℃ 3 | ℉ 4, ℃ 3 |

The r6 and r7 rows reproduce the council's readings. r8's sheet 09 glyphs
are the same as r7's.

**Side effect (r7's, carried with the port).** The letter overhangs the
right edge, so a mark set directly after a unit comes close:

- `℉–`: r6 0.50 px with contact at 600 and 700. r8: 0.00 px with contact
  at every weight (0.21 px at 300).
- `℃/`: r6 contact at 700 only. r8: 0.00–0.62 px, contact at every weight.
- `℉/` keeps ≥ 1.74 px at every weight.

Item 3 measures constructions that clear these (the `fit` letter clears the
en dash). The brief keeps item 1's ring when no construction meets every
item 3 target, so the inset form ships here. See section 3 and Next steps.

### 1b. Serif at 9–13 px

**The port.** `transforms/serif.py` now carries r7's caption-weight steps,
all on the opsz 8 masters (m00–m02) only:

- `CAPTION_STEM`: after the colour match, the caption masters gain Thin 5,
  Regular 16 and Black 16 units of stroke.
- `HAIR` 8 → 11: hairlines and crossbars gain 11 units a side.
- `THIN_GAIN` Regular 18 → 26, Black 30 → 34 for the steep thin strokes.
- `caption_lines` and `keep_caption_lines` (`CAPTION_LINES`): short lines
  with one smooth end keep their direction through the stroke gain, so the
  gain bends no join.
- `KEEP_DRAWN` keeps the dagger as drawn through the tangency pass, as r7
  did, so it adds no kink.

The opsz 20 and 60 masters are byte-identical to r6's in the sources.

**Measured on sheet 05** (serif waterfall, light; summed coverage per
waterfall row, size labels hidden). The table shows the change against r6:

| Row | r6 | r7 | r8 | r8 − r7 |
| --- | ---: | ---: | ---: | ---: |
| 400 / 9 px | 0 | +10.78% | +10.88% | +0.10 pp |
| 400 / 11 px | 0 | +10.20% | +10.24% | +0.04 pp |
| 400 / 13 px | 0 | +8.93% | +8.89% | −0.04 pp |
| 400 / 15 px | 0 | +6.56% | +6.49% | −0.07 pp |
| 400 / 17 px | 0 | +4.20% | +4.15% | −0.05 pp |
| 600 / 9 px | 0 | +7.69% | +7.74% | +0.05 pp |
| 600 / 11 px | 0 | +7.26% | +7.27% | +0.01 pp |
| 600 / 13 px | 0 | +6.40% | +6.39% | −0.01 pp |
| 600 / 15 px | 0 | +4.82% | +4.80% | −0.02 pp |
| 600 / 17 px | 0 | +3.04% | +3.01% | −0.03 pp |
| 400 / 24 px | 0 | −0.01% | 0.00% (identical sum) | |
| 400 / 32 px | 0 | −0.05% | 0.00% (identical sum) | |
| 600 / 32 px | 0 | −0.03% | 0.00% (identical sum) | |

Each build is measured on its own sheet 05 from `make render`. The r8 − r7
gaps are what `keep_splits` costs: the pinned handle lengths.

Sizes 20–72 px are +0.00% against r6 at both weights (r7: −0.05% to
+0.02%), because the default instance and the opsz 20 and 60 deltas are
r6's numbers (section 2).

The brief quotes r7's gains as +5.6% (9 px) to +2.7% (17 px). The figures
here come from a different measure: the whole row's summed coverage, with
r7 measured on its own sheet the same way. On one method, r8 is within
0.10 pp of r7 at every size from 9 to 17 px.

**Counters at 9 px / 600 on dark.** I set a, e and s alone at 9 px / 600 in
the dark theme's colours, at four sub-pixel phases. For each, I counted the
background pixels (coverage < 0.5) that the glyph encloses, worst phase:

| | a | e | s |
| --- | ---: | ---: | ---: |
| r6 | 14 | 7 | 0 |
| r7 | 14 | 6 | 5 |
| r8 | 14 | 6 | 5 |

The a and e counters stay open (background inside) in all three. The s has
no closed counter, so r6's 0 means both apertures are open. In r7 and r8
one terminal meets the spine at every phase. The counter it traps is still
background, so the s does not fill in, but its aperture closes. r8 carries
this from r7's weight unchanged. Next steps proposes a fix.

## 2. Outline hygiene

**Why r7 drifted.** The compiler converts the cubic masters to quadratics for
all masters at once (tolerance 0.001 em). Each cubic segment gets the number
of quadratic pieces the worst master needs, so every master keeps the same
point structure. r7's heavier caption masters made some segments need more
or fewer pieces in m00–m02. Those segments then changed their point
structure in every master, including the default instance. That gave 64
serif glyphs with a changed default glyf (area ≤ 0.24%, same bounds),
changed deltas in every region, and a changed `maxp`.

**The fix** (`serif.keep_splits`, called from `apply.py`):

1. `apply.py` runs the serif steps twice. The first pass runs inside
   `serif.caption_profile(serif.R6_CAPTION)`, which is r6's caption
   settings. It gives the reference split counts, segment by segment
   (`split_counts`, the same `curves_to_quadratic` call the compiler makes).
2. The second pass runs with r8's settings.
3. Where a segment's count differs from the reference, the caption masters'
   handle lengths move along their own directions, in steps of 0.1 unit, up
   to 40 units. They stop at the smallest move that brings the count back.
   - When a count is too high, all caption masters needing more move together.
   - When a count is too low, the master with the least travel moves alone.
   - A move is kept only if the glyph's kink count does not rise.
4. The counts are recomputed over every glyph at the end. `apply.py` stops
   with an error if any segment still differs.

In this build, 190 segments in 129 glyphs were pinned. The largest handle
travel is 9.8 units (`braceleft.sc`, m02), then 6.7 (`Ze.sc`), 4.9
(`comma`), 4.5 (`numero`) and 4.4 (`y`). No point is added or removed. The
text and display masters are not touched.

**The check** (`checks/drift.py r8-type`, against r6-type):

- Sources: each master's glyph records (points with types and smooth flags,
  components, advance, Unicode values, anchors), compared exactly, plus
  every other source file.
- Built TTF and WOFF2: per glyph, the default glyf entry and its hmtx; every
  gvar tuple by region; and `cmap`, `GSUB`, `GPOS`, `GDEF`, `fvar`, `avar`,
  `STAT`, `HVAR`, `MVAR`, `name`, `OS/2`, `hhea`, `post` and `maxp`, whole.

It fails on any change outside `INTENDED`. Result: **PASS**. The full list of
names is in `evidence/changed-glyphs.txt`.

| Face | Sources (glyphs changed per master) | Built default glyf | hmtx | gvar | Whole tables |
| --- | --- | ---: | ---: | --- | --- |
| Sans | 0 in m00–m08 | 0 | 0 | 0 | identical |
| Rounded | 0 in m00–m08 | 0 | 0 | 0 | identical |
| Serif | 629 of 1509 in each of m00, m01, m02; 0 in m03–m08 | 0 | 0 | 314 glyphs, only in the regions `opsz=-1` (314), `wght=+1,opsz=-1` (285), `wght=-1,opsz=-1` (314) | identical |
| Mono | `uni2103`, `uni2109` in m00 and m01 | 2 (`uni2103`, `uni2109`) | 0 | the same 2 glyphs, region `wght=+1` | identical |

The same check run on r7 fails. It finds:

- serif: default glyf 64 glyphs, `maxp` changed, and text and display
  regions changed in 64 glyphs;
- Rounded: `three` and `three.pnum` changed in every master and region.

**Reproducibility.** Running `apply.py` from the baseline into an empty
folder gives UFO folders identical to `candidates/r8-type/fonts` (`diff -r`
prints nothing).

## 3. Mono letter width

**What the council saw.** On r7's sheet 09 the letter in ℉/℃ is about 25%
narrower than the letter in the composed `°F`/`°C`.

**Constructions built** (`TEMP_R7` in `transforms/mono.py`; build one with
`apply.py mono --temp-mode NAME`, see Rebuild):

- **inset** (r7's, item 1): the ring as above, and the letter at the largest
  horizontal scale that keeps 1.20 px from the ring inside the cell plus
  `OVER`.
- **fit**: the inset ring, `OVER` 0.12 (the letter may end 0.12 of a cell
  past the right edge). The letter is scaled to fit what can
  follow it (`TEMP_FOLLOW`): with an en dash or a slash in the next cell,
  the letter must keep `FIT` 1.20 px of nearest ink at 13 px. The F's middle
  arm alone gives way to the dash (`ARM`, `shorten_arm`), so the stem and
  top bar stay wide. The C has no follower rule: its lower terminal meets a
  following slash's foot at any useful width (153 units apart at Bold even
  at 0.3 scale), so a C fitted to the slash would be too narrow.
- **small**: as fit, with a smaller ring at full wall weight: `RING_H` 0.82,
  `RING_W` 0.72 Light, 0.68 Bold, `WALL` 0.95.

All three keep the 1217-unit advance and the 1.20 px ring–letter gap. Font
units, from the masters (Light / Bold):

| | inset | fit | small |
| --- | --- | --- | --- |
| Ring ink, x | 0–523 / 37–576 | 0–523 / 37–576 | 0–459 / 37–513 |
| Letter F width / face's F | 0.76 / 0.66 | 0.83 / 0.68 | 0.91 / 0.76 |
| Letter C width / face's C | 0.77 / 0.70 | 0.84 / 0.73 | 0.93 / 0.81 |
| F middle arm / top bar | 0.88 / 0.91 | 0.61 / 0.56 | 0.64 / 0.60 |

**Measured on the 13/15/17 px strip** (soft widths, every phase; letter width
is the unit's letter over the composed letter after `°`):

| | Weight | inset (kept) | fit | small | Target |
| --- | --- | ---: | ---: | ---: | --- |
| Letter width F / C | 300 | 0.75 / 0.77 | 0.83 / 0.84 | **0.91 / 0.93** | ≥ 0.85 |
| | 400 | 0.72 / 0.74 | 0.78 / 0.81 | **0.86 / 0.89** | |
| | 500 | 0.70 / 0.72 | 0.74 / 0.77 | 0.82 / **0.86** | |
| | 600 | 0.67 / 0.71 | 0.71 / 0.74 | 0.78 / 0.83 | |
| | 700 | 0.66 / 0.70 | 0.68 / 0.72 | 0.75 / 0.81 | |
| Ring outer height / `°` | all | 0.92–0.93 | 0.92–0.93 | 0.81 | ≥ 0.80 |
| Ring wall / `°` wall | all | 0.96–1.02 | 0.96–1.02 | 0.95–0.98 where open; counter closes at 400/13, 500/13, 600/15, 500/17 | 0.90–1.10 |
| Ring–letter gap | all | ≥ 1.00 px, no contact | ≥ 1.00 px, no contact | ≥ 1.00 px, no contact | ≥ 1 px |
| `℉–` nearest ink | 700 | 0.00 px, contact | **1.00–1.50 px** | **1.00–1.50 px** | ≥ 1 px |
| | 300–600 | 0.00–0.50, contact | ≥ 1.00 | ≥ 1.00 | |
| `℉/` nearest ink | 700 | 1.74–2.19 px | 1.74–2.19 px | 2.19–3.04 px | ≥ 1 px |
| `℃/` nearest ink | 700 | 0.00, contact | 0.00, contact | 0.00, contact | (not a target) |

**Measured on sheet 09** (Regular, 24 px, raster px at 2x; r8's sheet with
the mono face swapped for each construction):

| | inset (r8) | fit | small | Target |
| --- | --- | --- | --- | --- |
| ℉ letter / composed F (px) | 15 / 21 = 0.71 | 17 / 21 = 0.81 | 18 / 21 = 0.86 | ≥ 0.85 |
| ℃ letter / composed C (px) | 16 / 22 = 0.73 | 17 / 22 = 0.77 | 19 / 22 = 0.86 | ≥ 0.85 |
| Soft width F / C | 0.73 / 0.75 | 0.79 / 0.81 | 0.86 / 0.90 | |
| Ring w × h (`°` 16 × 16) | 13 × 15 | 13 × 15 | ℉ 12 × 13, ℃ 11 × 13 | height ≥ 0.80 |
| Ring walls (`°` 4 / 4) | 4 / 4 | 4 / 4 | ℉ 4 / 4, ℃ 3 / 4 (0.88) | ±10% |
| Ring–letter blank columns | 4 / 3 | 4 / 3 | 4 / 3 | |

At Regular on sheet 09, `small` reaches the letter target. But its ℃ ring
wall is 0.88 of the degree sign's, outside ±10%, and its Bold letter misses
(0.75 / 0.81 on the strip).

**Decision.** No construction meets every target.

- The Bold letter stays under 0.85 in all three.
- `small` comes closest. Its Light and Regular letters pass and its ring
  still passes the 0.80 floor. But its Bold letter is 0.75 / 0.81, and its
  smaller counter fills in at some sizes and phases, so the ring reads as a
  dot.
- `fit` keeps the full ring and clears the en dash at every weight. But it
  gains only 0.02–0.08 of letter width, and its F has a short middle arm.

As the brief asks, r8 keeps item 1's ring and letter (`TEMP_MODE =
'inset'`). Next steps names `fit` as the first candidate for the next round.

## 4. Everything else

Unchanged in sources and binaries (section 2): every sans and Rounded master,
including r6's flat-top Rounded 3 (`three`, `three.pnum`), the serif opsz 20
and 60 masters, and every mono glyph except the two units. r7's degree-gap
change is not ported: the sans and Rounded degree glyphs and their kerning
are r6's. Also not taken, as the brief says: unligated `===`/`!==`, the sans
0/O width, sans digit spacing, a slab 1, a heavier mono 9 px stem and
headline wrapping.

## Checks

The final `make build`, `make gate`, `make render` and `make checks` for
`r8-type` all exit 0, with no hard fails. A from-baseline `apply.py` run
reproduces the UFO folders exactly (section 2).

**Gate** (`build/r8-type/gate.md`). Quality status is FAIL with 0 hard
failures, as for r6. The font-checker failures are inherited upstream
findings, and the gate preserves them.

| Face | Pass | Warn | Fail | Error | Core | Interpolation glyphs | WOFF2 bytes (r6) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 92 | 4 | 5 | 1 | 258/258 | 0 | 108328 (108328) |
| Serif | 95 | 5 | 5 | 0 | 258/258 | 3 | 197980 (197716) |
| Mono | 90 | 6 | 5 | 1 | 258/258 | 0 | 47748 (47780) |
| Sans Rounded | 98 | 0 | 2 | 1 | 29/29 | 0 | 74012 (74012) |

The pass, warn, fail and error counts are r6's.

- Name/RFN PASS on all four faces, with no reserved names.
- Icons PASS: 71 icons from the given icon folder, one stroke width (1.875),
  TSX typecheck PASS.
- Tabular figures are equal width and the default; `tnum` and `pnum` are
  present.

**Interpolation.** The gate reports serif `kink` 4 in the same 3 glyphs as
r6 (`dagger`, `daggerdbl`, `f.ligalong`), with the same values (6; 6 and 14;
8), all between m02 and m03. Only the dagger's flagged contour index moves
(1 → 0). Sans, Mono and Rounded report none.

The variable-font kink test (`checks/vfkinks.py`) gives output
byte-identical to r6's: 5 findings, all in the serif ff ligatures, Thin to
Black at opsz 8. There are no new interpolation findings.

**Render** (`make render`, 38 sheets). Blind byte scan PASS. Headline line
contact is clear on light, dark and glass (0 contacts on each).

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
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.500 | 0.657 |
| Rounded | 11 | 0.714 | 0.380 | 0.576 | 0.540 | 0.721 | 0.636 | 0.661 | 0.466 | 0.659 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.517 | 0.691 |

- **Sans, Mono and Rounded** rows are identical to r6's.
- **Serif** rows are r7's, except 3/7 at 13 px (r7 0.664). The heavier
  caption weight lowers the serif pairs by 0.01–0.05 against r6. The lowest
  value overall is serif l/I at 9 px: 0.217 (r6 0.243).

**Skeleton** (`checks/skeleton.py --all`, Rounded against the sans at
opsz 14, largest displaced region beyond 0.012 em in thousandths of an em²,
fail at 4.0): PASS, byte-identical to r6's output.

- Largest at 400: G 3.68, ℉ 3.56, B / E / L 3.51.
- Largest at 900: M 3.37.
- Over 135 glyphs the mean at 400 is 0.41, and the lowest two-way overlap is
  0.953.

**Widths** (`checks/widths.py --all`, Rounded against the sans, 10
locations × 16 strings): largest difference 0.00%, byte-identical to r6's
output. At opsz 14 / 400, in units:

| String | Sans | Rounded |
| --- | ---: | ---: |
| 72° | 3558 | 3558 |
| −3° | 3505 | 3505 |
| 104°F | 6150 | 6150 |
| 18:30 | 6165 | 6165 |
| 80% | 4703 | 4703 |
| 30.16 | 5962 | 5962 |
| 0123456789 | 13400 | 13400 |
| 12:05 | 6165 | 6165 |
| −12°C | 6327 | 6327 |
| 3 PM | 5104 | 5104 |
| 12 mph NNW | 13279 | 13279 |
| 30.16 inHg | 11124 | 11124 |
| Thu | 3780 | 3780 |
| ½ ¼ ¾ | 6384 | 6384 |
| 72℉ 22℃ | 10403 | 10403 |
| Rain, 40%. | 10701 | 10701 |

**`make checks`** (`build/r8-type/checks.md`): PASS.

- Rounded against the sans, ink width at 96 px, Regular (limit 1%): 104°F
  269.578 / 269.578 px, 72° 149.109 / 149.109, 18:30 261.891 / 261.891,
  −3° 144.094 / 144.094, all +0.000%.
- Default shaped figures are tabular at every named instance and every axis
  min, default and max combination:
  - Sans (21 locations), Mono (5) and Rounded (15): PASS.
  - Serif reports INFO, tabular true at 30 locations, as in r6.

**Figure defaults** (`checks/figcheck.py`): PASS.

- Sans: 21 locations, all ten default figures 1332 units, `tnum` equals the
  default, `pnum` varied.
- Serif: 30 locations, 579 units.
- Mono: 5 locations, 1217 units.
- Rounded: 15 locations, 1332 units.

**Outlines** (`checks/outlines.py`). There are 0 gated outliers (kinks,
fold-backs, added points) in the core set of sans, Rounded, serif and mono:
PASS. Reported only:

- Glyphs with only new short segments: sans 1, Rounded 1, serif 16 (r6 14),
  mono 0.
  - In the serif, `M` (m01), `R` (m01, m02) and `t` (m00) each gain one short
    piece in an opsz 8 master, from the heavier caption weight.
  - `braceleft` loses its short pieces.
- Full repertoire, any reason:

  | Face | Text/display masters | Caption masters |
  | --- | ---: | ---: |
  | Sans | 11 | 68 |
  | Rounded | 1 | 0 |
  | Serif | 127 (r6 141) | 2 |
  | Mono | 0 | 0 |

  As in r6, the checker's serif "text/display" column includes the opsz 8
  masters.
- The TrueType default-instance point report is unchanged from r6. Sans 2
  core glyphs and mono 13 core glyphs gain points in the quadratic
  conversion, as in r6; serif 0.

**Binary** (`build/r8-type/*.ttf`, compared with r6 and checked with the
shaper):

- **Tables.** For all four faces, `cmap`, the glyph order, every hmtx entry,
  `GSUB` and `GPOS` are identical to r6. So are `GDEF`, `fvar`, `avar`,
  `STAT`, `HVAR`, `MVAR`, `name`, `OS/2`, `hhea`, `post` and `maxp`
  (`drift.py`).
- **hmtx.** The mono units keep advance 1217 and left side bearing 0, as in
  r6.
- **Features.** Rounded GSUB has `calt case cv08 pnum salt ss09 tnum zero`.
- **Shaping:**
  - `72℉ 22℃` (mono, 300 and 700) → `seven two uni2109 space two two
    uni2103`, every advance 1217.
  - `!==` (mono) → `exclam.spacer equal.spacer exclam_equal_equal.liga`, one
    sign over three cells.
  - `18:30 −3°` (Rounded) → `one eight colon.fig three zero space minus.case
    three degree`.
  - `0` with `zero` (sans) → `zero.slash`.
- **Reserved names.** Inter, Source and Fira appear in no name record of any
  face.

## Evidence

Each sheet has numbered callouts explained under it.

`evidence/item1-mono-ring.png` (r6 before, r8 after):

- **Content.** Mono at Light (top) and Bold: `℉ °F  ℃ °C` at 48 px, then the
  13, 15 and 17 px strips. Each strip reads `℉ °F  0℉–  ℉/  ℃ °C  ℃/  21℉
  21°F`. Under each panel are the 13 px strips at ×6.
- **Callouts.**
  1. The ring against the typed `°` beside it: 0.67–0.74 → 0.92–0.93 of
     its height. Sheet 09: 11 × 12 → 13 × 15 raster px against 16 × 16.
  2. The ring wall: 0.48–0.54 → 0.96–1.02 of the `°` wall. Sheet 09:
     2 → 4 raster px against 4.
  3. The composed form; the letter in the sign stays on the cap height
     (1.00).
  4. The ring–letter gap at 13 px, Bold: ≥ 1.00 px, no contact.
  5. The Bold ring at full wall weight.
  6. The dash after the sign touches the F's arm at 13 px. This came with
     the port; see item 3.
  7. A slash after the sign keeps ≥ 1.74 px.

`evidence/item1-serif-small.png` (r6, r7, r8):

- **Content.** Serif `A quiet sky, 0123456789` at 9, 11, 13 and 24 px, 400
  and 600. Under each panel is the 9 px / 400 row at ×8.
- **Callouts.**
  1. At 9 px / 400, ink +10.78% (r7) and +10.88% (r8) against r6.
  2. At 13 px / 400, +8.93% and +8.89%.
  3. At 24 px, r8 has r6's ink exactly (r7 −0.01%).

`evidence/item2-outline-hygiene.png`:

- **Content.**
  - The default-instance points of serif a, S and s in the built r6, r7
    and r8 fonts, with point counts.
  - `drift.py` on the binaries, r7 and r8 against r6. Red cells are r7
    changes that r8 does not make.
- **Callouts.**
  1. r7's re-converted point structure: S 57 → 58 points, s 57 → 56; a
     keeps 75 points, but its on/off-curve pattern changes and 38 points
     move (up to 256 units).
  2. r8: the same points and coordinates as r6.
  3. r7 against r6: 64 default glyf changes, deltas in every serif region
     and `maxp`; `three`/`three.pnum` changed in Rounded hmtx and every
     region.
  4. r8 against r6: only the intended changes.

`evidence/item3-mono-letter-width.png` (inset = r8, fit, small):

- **Content.** The same layout as item 1, one panel per construction.
- **Callouts.**
  1. Light letter width against the composed letter (inset 0.75, fit 0.83,
     small 0.91 for F).
  2. The ring: 0.92–0.93 of the `°` for inset and fit, 0.81 for small.
     small's counter fills in at some sizes.
  3. The composed reference.
  4. The ring–letter gap at 13 px, Bold: ≥ 1.00 px in all three.
  5. Bold letter width: 0.66 / 0.68 / 0.75 for F. None reaches 0.85.
  6. A dash after the Bold sign: inset touches; fit and small keep ≥ 1.00 px.
  7. A slash after the Bold sign: ≥ 1.74 px in all three.

`evidence/item4-rounded-three.png` (r6, r7, r8):

- **Content.** Rounded and Sans 500 at 96 px (`3 23° −3°`), and Rounded
  at 24 px.
- **Callouts.**
  1. The Rounded 3: r6 and r8 flat top, identical in every master and in the
     binary. r7's round top is not ported.
  2. The Sans 3: the same flat top.

`evidence/changed-glyphs.txt`: every glyph name whose outline differs from
r6, per face and master and per built font, table and gvar region
(`checks/drift.py --list`).

## Rules to keep

r6's rules all hold (see r6-type's notes). Changed or added this round:

- **No outline drift.** A change aimed at some masters must leave every other
  glyph, master and region as the incumbent had it. Run `checks/drift.py`
  against the incumbent and make its INTENDED list match the plan before
  building evidence. A clean source diff is not enough: the quadratic
  conversion shares point structure across masters, so a caption-only change
  can still change the default instance.
- **Pin quadratic splits.** Any serif pass that moves caption-master outlines
  runs after a reference pass with the incumbent's settings, and
  `keep_splits` must bring every segment back to the reference split count.
  `apply.py` stops otherwise. The same applies to any face whose masters are
  changed one optical size at a time.
- **A mono temperature unit** gives up width, never height.
  - The letter is the face's own C or F at cap height.
  - The ring is the face's own degree sign, at least 0.90 of its height,
    with walls within ±10% of its walls.
  - Ring and letter keep ≥ 1 px of nearest ink at 13 px at every weight and
    phase.
  - A new construction must also report the nearest ink to what follows it
    in the next cell (`–`, `/`).
- **Serif caption weight** changes only the opsz 8 masters. Sizes ≥ 20 px
  must render with r6's ink (within ±0.1%).
  - At 9 px / 600 on dark, the a and e counters must keep background pixels
    and the s must not fill in.
  - Report the s's apertures too: r8 closes one, as r7 did.
- **Measure on the render.** Measure per glyph, centre-aligned, over
  sub-pixel phases. For the units, measure parts by contour (ring and
  letter), with the hmtx left side bearing set to the part's xMin. A string
  xor between fonts is never a measurement.

## Next steps

- **Mono unit followers (first).** The inset letter overhangs into the next
  cell, so `℉–` and `℃/` touch at 13 px. These cases need a fix:
  - Build `fit` (`apply.py mono --temp-mode fit`) for ℉. It clears `–` at
    every weight with the full ring, but shortens the F's middle arm to
    0.56–0.61 of the top bar, and that needs a look at reading size.
  - For ℃, the letter can't be fitted to a slash. Use contextual kerning or
    a `calt` rule after ℃ (slash and en dash moved right by about 1.5 px at
    13 px) instead of narrowing the C.
- **Letter width ≥ 0.85 at Bold.** No ring that keeps ≥ 0.80 of the degree
  sign leaves room for this inside one cell at Bold. A two-cell form for ℉/℃
  (letter at full width, ring in its own half-cell), or a per-weight ring
  (Light `small`, Bold `inset`), would be the next constructions to measure.
  Both need the follower rule above.
- **Serif s at 9 px / 600.** r7's caption weight closes one aperture of the
  s on dark (5 trapped background pixels at every phase; r6 open). Holding
  the s's terminals out of `CAPTION_STEM`, or capping the gain on edges that
  face less than 1.5 stems of white (as `thin_small` does), should reopen it
  without losing the ink gain.
- **Serif short pieces.** `keep_splits` changes only handle lengths. The
  r6 short-piece findings (`El.sc`, `Lje.sc`, `ampersand.sc`, `estimated`,
  `five.cap`, `five.lf`, `section`) are unchanged; see r6's notes.
- **Carried over from r6:**
  - the mono figure before ℉/℃ (`0℉` at 700);
  - the Black hero 0;
  - the serif bar `|` thickened by the thin-stroke pass;
  - the r5 items listed in r6's notes.

## Rebuild

From the repository root:

    .venv/bin/python -I candidates/r8-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r8-type/checks/outlines.py r8-type
    make build  CAND=r8-type SUBSET=core ICONS_DIR=<icon folder>
    make gate   CAND=r8-type ICONS_DIR=<icon folder>
    make render CAND=r8-type OUT=<render folder> MAP=<map file> REFS=0 ICONS_DIR=<icon folder>
    make checks CAND=r8-type ICONS_DIR=<icon folder>
    .venv/bin/python -I candidates/r8-type/checks/drift.py r8-type --list candidates/r8-type/evidence/changed-glyphs.txt
    .venv/bin/python -I candidates/r8-type/checks/figcheck.py build/r8-type
    .venv/bin/python -I candidates/r8-type/checks/skeleton.py build/r8-type --all
    .venv/bin/python -I candidates/r8-type/checks/widths.py build/r8-type --all
    .venv/bin/python -I candidates/r8-type/checks/vfkinks.py build/r8-type

To build a unit construction for comparison in a scratch folder (the mono
reads the finished sans masters, so copy them in first):

    mkdir -p <scratch>/fonts && cp -R candidates/r8-type/fonts/sans <scratch>/fonts/sans
    .venv/bin/python -I candidates/r8-type/transforms/apply.py mono --output-dir <scratch> --temp-mode fit
