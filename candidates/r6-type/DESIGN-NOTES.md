# r6-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r5-type, and r5's decisions hold unless a section
below changes them. The following are kept as r5 left them and re-checked
on the r6 binary:

- the barred default I;
- Rounded width parity (0.00%);
- open 9 px figures;
- the minus kerning in `−3°`;
- the larger figure colon;
- the minus distinct from the hyphen;
- tabular figures by default;
- `zero`;
- `!==` as one ligature.

Four items were worked. Before/after images for each are in `evidence/`, with
numbered callouts explained under each sheet.

## Summary

All measurements are from the built fonts in `build/r6-type` and
`build/r5-type`, at Regular (wght 400) unless a row says otherwise.

| Item | Change | r5 → r6 | Target |
| --- | --- | --- | --- |
| 1 Mono ℉ ℃ | Letter at full cap height. Ring on the cell's left edge, raised to the degree sign's top so the letter tucks under it | Letter height 0.82 → 1.00 of the face's F/C. Counter 0.863 × 0.867 of the `°` counter. Gap at 13 px: ℉ 0.20 → 1.05 px, ℃ 0.81 → 1.05 px | Height 1.00 ± 0.02, counter ≥ 0.85, gap ≥ 1 px: met at 300, 400 and 700 |
| 2 Serif at 9–13 px | Steep thin strokes thickened in the opsz 8 masters only | Thin stroke / n stem at 9 px, median: 400 0.546 → 0.734; 600 0.476 → 0.540. Unchanged at opsz 20 and 60 | Met. a, e and s counters stay open at 9 px / 600 |
| 3 Rounded hero figures | Display masters: bowls drawn on circular curves; dots and % rings round. All sizes: the 3's notch closed to one join | Mean xor/union against the sans, `0–9 ° % . :`: 32 px 0.023 → 0.118, 24 px 0.028 → 0.078. Width difference 0.00% | Shows at 32 px with width parity: met |
| 4 Mono 0 at 9 px | None (measured only) | Dotted and slashed counters keep background pixels at 400 and 700 | Counter open: no change |

## 1. Mono ℉ and ℃

**What r5 did.** r5 drew each unit as a ring plus the face's C or F scaled to
0.82 of its height, with a fixed gap, centred in one cell. The counter met
its target (0.86 of the `°` counter), but the letter was short, and at 13 px
the F sat 0.20 px from the ring, so it read as touching.

**What r6 does** (`mono.temp_units`, `TEMP_MODE` = `'hangtuck'`):

- **Letter.** The face's finished C or F at full cap height.
  - It is condensed in x only, by the largest scale that keeps it inside
    the cell.
  - It is then emboldened back by the stem width it lost (`temp_letter`).
  - Heights and horizontal bars are untouched.
- **Ring.** It keeps the degree sign's counter (`TEMP_COUNTER` 0.865 of its
  width and height).
  - Its walls are `TEMP_WALL_TUCK` 0.50 of the degree sign's walls.
  - Its left ink sits on the cell's left edge.
  - Its top sits at the degree sign's own top (1518 units at Regular;
    r5 1420).
- **Gap.** Ring and letter are set `TEMP_GAP_PX` 1.05 px of nearest ink
  apart at 13 px.
  - The gap is measured as the shortest distance in any direction, so the
    C's round top may pass under the ring.
  - The letter ends flush with the cell's right edge.

**Four constructions compared.** They differ in two settings:

- where the pair sits in the cell: inside a 0.02 cell margin, or the full
  cell with the ring on its left edge;
- where the ring's top sits: on the figures' top, or at the degree sign's
  top, so a round letter can tuck under it.

Each construction was built and measured as a separate font. All four meet
the height, counter and gap targets at Regular: height 1.000, counter
0.863–0.867, gap 1.05 px at 13 px. They differ in how wide the letter can
stay.

| Construction | Cell use | Ring top | Walls | ℉ letter width / F | ℃ letter width / C |
| --- | --- | --- | ---: | ---: | ---: |
| side | 0.02 margin | figure top | 0.60 | 0.635 | 0.659 |
| hang | full cell | figure top | 0.60 | 0.695 | 0.718 |
| tuck | 0.02 margin | degree top | 0.50 | 0.672 | 0.728 |
| **hangtuck** (kept) | full cell | degree top | 0.50 | **0.730** | **0.787** |

`hangtuck` is kept because it gives the least condensed letter. Its cost is
the ring's walls, which are half the degree sign's (r5 0.60). See next steps.

r3's form, for reference, had a full-height letter (1.000) and a closed ring
(counter 0.554).

**Measured on the built font**, r5 → r6, at 13 px for the gaps:

| Weight | Glyph | Height / F or C | Width / F or C | Counter / ° counter | Ring–letter gap | `72℉`: 2 to ring |
| ---: | --- | --- | --- | --- | --- | --- |
| 300 | ℉ | 0.821 → 1.000 | 0.840 → 0.758 | 0.863 × 0.868 | 0.20 → 1.05 px | 1.73 → 1.61 px |
| 300 | ℃ | 0.823 → 1.000 | 0.822 → 0.801 | 0.863 × 0.868 | 0.82 → 1.05 px | 1.67 → 1.61 px |
| 400 | ℉ | 0.821 → 1.000 | 0.810 → 0.730 | 0.863 × 0.867 | 0.20 → 1.05 px | 1.58 → 1.46 px |
| 400 | ℃ | 0.824 → 1.000 | 0.798 → 0.788 | 0.863 × 0.867 | 0.81 → 1.05 px | 1.54 → 1.46 px |
| 700 | ℉ | 0.822 → 1.000 | 0.745 → 0.672 | 0.865 × 0.866 | 0.20 → 1.05 px | 1.20 → 1.12 px |
| 700 | ℃ | 0.826 → 1.000 | 0.742 → 0.758 | 0.865 × 0.866 | 0.78 → 1.05 px | 1.21 → 1.12 px |

All three targets are met at every weight. Because the ring now starts at
the cell's edge, a figure before it sits a little closer: in `72℉` the 2 is
0.08–0.12 px nearer the ring than in r5. In `0℉` at 700 the 0 is 0.79 px
from the ring (r5 0.87).

The advance stays one cell (1217). Only the left side bearings change in
`hmtx`: ℃ 10 → 0 and ℉ 19 → 0 at the default instance.

`evidence/item1-mono-temperature.png` shows `℉ ℃  °F °C  72℉ 72°F` at 13, 15
and 17 px, Light, Regular and Bold. Each row has r6 beside r5's form and the
composed `°F` / `°C`.

## 2. Serif at text sizes

The opsz 8 (caption) masters serve about 9–13 px. In opsz user units the
axis maps 8 → 8, 12 → 9 and 20 → 20, so 9–13 px resolves to design opsz
8.25–9.9.

r5 strengthened their horizontal hairlines (`sturdy_small`). It did not
touch the steep thin strokes:

- the light side of v, w, x, y, A, K and k;
- the thin verticals of N and M;
- the hairline joins.

At Regular these strokes were about 0.55 of the n stem and broke up at 9 px.

`serif.thin_small` (new in r6):

- **Which strokes.** Every steep segment (within `STEEP` of vertical) whose
  stroke, measured across from its middle, is thinner than `THIN_HI` 0.85 of
  the master's n stem.
- **The move.** The segment moves outward in x, so the stroke gains up to
  `THIN_GAIN` units. The gain is full at `THIN_LO` 0.60 of a stem and fades
  to none at 0.85.
- **The gain per caption master.** Thin 0, Regular 18, Black 30 units. wght
  600 falls between Regular and Black. Small forms take 0.6 of the gain.
- **Counters.** An edge that faces less than `THIN_WHITE` 1.5 stems of white
  stays where it is, so counters keep their room.
- **Smooth joins.** Off-curve points move with their on-curve point, so
  smooth joins stay smooth.

Only the three opsz 8 masters change. The text and display masters (opsz 20
and 60) are untouched. The change applied to 488 glyphs.

Steep thin strokes against the n stem, measured on the built font
perpendicular to the stroke at mid-height. Median over v w y A V N M K and
the other measured glyphs (lowest in brackets):

| wght | opsz (px) | r5 | r6 |
| ---: | ---: | --- | --- |
| 400 | 9 | 0.546 (0.476) | 0.734 (0.645) |
| 400 | 11 | 0.546 | 0.729 |
| 400 | 13 | 0.537 | 0.690 |
| 600 | 9 | 0.476 (0.315) | 0.540 (0.412) |
| 600 | 11 | 0.475 | 0.536 |
| 600 | 13 | 0.466 | 0.510 |
| 400 | 20 | 0.487 | 0.487 |
| 400 | 60 | 0.484 | 0.484 |

Examples at opsz 9 / 400, in units: v's thin arm 43 → 58, A's thin leg
43 → 51, N's thin vertical 43 → 58. The horizontal hairline against the stem
is unchanged: 0.980 at opsz 9 / 400 and 0.629 at opsz 9 / 600.

**Counters at 9 px.** For each glyph rendered alone, the table gives:

- open: interior pixels under half coverage;
- lightest: the lightest interior pixel, from 0 (background) to 255.

| wght | a open / lightest | e open / lightest | s open / lightest |
| ---: | --- | --- | --- |
| 400, r5 → r6 | 10 / 0 → 10 / 0 | 5 / 0 → 5 / 0 | 5 / 0 → 5 / 2 |
| 600, r5 → r6 | 5 / 0 → 5 / 0 | 4 / 0 → 4 / 0 | 5 / 10 → 5 / 14 |

The same counts hold on dark, where the coverage is only drawn inverted. The
a, e and s keep every open pixel they had. The s's lightest interior pixel
darkens by 4 of 255 at 600.

`evidence/item2-serif-text-sizes.png` shows two lines at 9, 11 and 13 px, 400
and 600, light and dark, r5 above r6. It also has opsz 9 overlays at 160 px
(r5 red, r6 blue) and the opsz 32 overlay, where r5 and r6 coincide.

## 3. Rounded hero figures

r5's Rounded was the sans with a round pen. From 24 px up, the mean xor/union
against the sans over `0–9 ° % . :` was 0.021–0.028, so at hero sizes it read
as the sans. r6 makes three changes. None of them touches an advance.

**(a) Circular bowls at display size** (`rounded.hero_bowls`, `HERO`,
`BOWL_K`, `BOWL_SHARE`, `BOWL_TURN`, `BOWL_LEG`). This runs on the display
masters only (opsz 32: Thin, Regular and Black), on the `HERO` set:

- the figures, tabular and proportional;
- `zero.slash`;
- `° % . :` and the case and figure colons.

The sans draws its bowls squarish, with handle tension 0.70–0.80. For each
curve segment that turns 80–100° and has both legs at least 0.5 stem long,
the handles move toward circular tension (`BOWL_K` 0.5523) and keep their
directions. So the extremes and the tangents at them stay, and the
shoulders move in.

A share of the way to circular is tried in steps of 1.0, 0.75, 0.5 and 0.25.
It is kept only if the glyph gains no kink and no roughness. Every hero
glyph took the full share, 1.00. The degree sign was already circular
(0.552), so it does not change.

The text (opsz 14) and caption (opsz 8) masters do not get this pass. At
24 px the optical size sits 0.56 of the way from 14 to 32, so the change
shows at about half strength there.

**(b) Round dots and % rings.** The same pass rounds the square-ish dots of
`.` and `:` and the rings of `%` in the display masters.

**(c) The 3's upper turn** (`rounded.merge_notch`, `SOFT_NOTCH`,
`NOTCH_CUT`). This applies at all sizes.

- **The problem.** The flat-top 3 has a short step under its bar where the
  diagonal meets it: two lines turning a concave corner of more than 90°,
  with a step shorter than `MICRO` stems between them. The pen filleted each
  of the two small corners, so the turn kept a sharp notch.
- **The step.** `merge_notch` closes the step to one join in every master.
  It moves the step's first point to where the two lines meet and removes
  the second.
- **The fillet.** The join then takes the soft fillet. Its reach is capped
  at `NOTCH_CUT` 1.0 stem, because the pen's full 1.8-stem cut filled the
  turn so much that it read as a dark spot at 96 px.

Per-glyph xor/union of Rounded against the sans, each glyph centred alone,
with opsz equal to the pixel size, Regular:

| px | build | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | ° | % | . | : | mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | r5 | 0.000 | 0.030 | 0.020 | 0.067 | 0.036 | 0.083 | 0.009 | 0.115 | 0.000 | 0.014 | 0.000 | 0.013 | 0.000 | 0.002 | 0.028 |
| 24 | r6 | 0.147 | 0.030 | 0.059 | 0.146 | 0.036 | 0.124 | 0.106 | 0.115 | 0.082 | 0.109 | 0.000 | 0.073 | 0.036 | 0.034 | 0.078 |
| 32 | r5 | 0.000 | 0.025 | 0.020 | 0.039 | 0.031 | 0.077 | 0.007 | 0.103 | 0.000 | 0.008 | 0.000 | 0.010 | 0.000 | 0.000 | 0.023 |
| 32 | r6 | 0.285 | 0.025 | 0.096 | 0.180 | 0.031 | 0.149 | 0.190 | 0.103 | 0.153 | 0.190 | 0.000 | 0.115 | 0.070 | 0.070 | 0.118 |
| 48 | r5 | 0.000 | 0.024 | 0.018 | 0.037 | 0.030 | 0.075 | 0.008 | 0.099 | 0.000 | 0.009 | 0.000 | 0.012 | 0.000 | 0.000 | 0.022 |
| 48 | r6 | 0.287 | 0.024 | 0.095 | 0.179 | 0.030 | 0.149 | 0.193 | 0.099 | 0.153 | 0.192 | 0.000 | 0.114 | 0.072 | 0.072 | 0.119 |
| 96 | r5 | 0.000 | 0.023 | 0.017 | 0.034 | 0.028 | 0.075 | 0.007 | 0.099 | 0.000 | 0.007 | 0.000 | 0.009 | 0.000 | 0.000 | 0.021 |
| 96 | r6 | 0.282 | 0.023 | 0.094 | 0.177 | 0.028 | 0.148 | 0.190 | 0.099 | 0.153 | 0.190 | 0.000 | 0.112 | 0.070 | 0.070 | 0.117 |

Black (wght 900):

| px | build | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | ° | % | . | : | mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | r5 | 0.000 | 0.048 | 0.034 | 0.040 | 0.066 | 0.067 | 0.015 | 0.071 | 0.000 | 0.020 | 0.000 | 0.013 | 0.000 | 0.002 | 0.027 |
| 24 | r6 | 0.080 | 0.048 | 0.055 | 0.084 | 0.066 | 0.086 | 0.065 | 0.071 | 0.047 | 0.067 | 0.000 | 0.048 | 0.035 | 0.034 | 0.056 |
| 32 | r5 | 0.000 | 0.044 | 0.030 | 0.037 | 0.060 | 0.056 | 0.015 | 0.072 | 0.000 | 0.015 | 0.000 | 0.010 | 0.000 | 0.000 | 0.024 |
| 32 | r6 | 0.160 | 0.044 | 0.073 | 0.116 | 0.060 | 0.094 | 0.112 | 0.072 | 0.091 | 0.112 | 0.000 | 0.077 | 0.069 | 0.069 | 0.082 |
| 48 | r5 | 0.000 | 0.044 | 0.029 | 0.036 | 0.059 | 0.055 | 0.016 | 0.073 | 0.000 | 0.016 | 0.000 | 0.011 | 0.000 | 0.000 | 0.024 |
| 48 | r6 | 0.162 | 0.044 | 0.073 | 0.115 | 0.059 | 0.093 | 0.113 | 0.073 | 0.090 | 0.112 | 0.000 | 0.073 | 0.067 | 0.068 | 0.081 |
| 96 | r5 | 0.000 | 0.042 | 0.028 | 0.036 | 0.057 | 0.053 | 0.014 | 0.070 | 0.000 | 0.014 | 0.000 | 0.010 | 0.000 | 0.000 | 0.023 |
| 96 | r6 | 0.159 | 0.042 | 0.071 | 0.114 | 0.057 | 0.091 | 0.111 | 0.070 | 0.090 | 0.111 | 0.000 | 0.073 | 0.068 | 0.068 | 0.080 |

Reading the tables:

- **At 32 px and up** the difference is the bowls (0, 6, 8, 9, 2, 3, 5), the
  dots and the % rings. 1, 4 and 7 have no qualifying bowl and keep r5's
  values. ° stays identical to the sans.
- **At 24 px** Rounded now shows too (mean 0.078 against 0.028), through the
  optical-size interpolation alone. Nothing was changed for 24 px itself.
- **Widths.** Advances are unchanged, so width parity holds: the largest
  difference on the width table is 0.00%, and the 96 px ink widths in
  `make checks` match the sans exactly.

**Skeleton at text size.** This is the gated check, at opsz 14, where the
display pass does not apply. Only the 3 moves, through the notch merge:

| Glyph | 400 | 900 |
| --- | --- | --- |
| three | 0.18 → 0.78 | 0.58 → 0.89 |
| three.pnum | 0.15 → 0.73 | 0.60 → 0.85 |

The largest region is still G at 3.68, against the 4.0 limit.

**Skeleton at display size.** This reference is not gated. It uses the same
metric on instances at opsz 32, made from the built fonts, in thousandths
of an em²:

| Glyph | 400 r5 | 400 r6 | 900 r5 | 900 r6 |
| --- | ---: | ---: | ---: | ---: |
| zero, zero.slash | 0.00 | 3.42 | 0.00 | 4.87 |
| two | 0.09 | 2.06 | 0.55 | 2.82 |
| three | 0.12 | 2.85 | 0.58 | 3.27 |
| five | 1.98 | 2.08 | 0.93 | 1.97 |
| six | 0.15 | 2.69 | 1.14 | 3.54 |
| seven | 0.56 | 0.56 | 1.13 | 1.13 |
| eight | 0.00 | 0.79 | 0.00 | 1.43 |
| nine | 0.15 | 2.66 | 1.19 | 3.52 |
| percent, period, colon, degree | 0.11, 0, 0, 0 | 0.11, 0, 0, 0 | 0.34, 0, 0, 0 | 0.34, 0, 0, 0 |

The Black 0 at display size (4.87) would be over 4.0 if the text-size limit
applied there. It does not, by design: the skeleton rule protects the
sans's construction at the sizes where Rounded reads as the sans. The
display change is the visible difference item 3 asked for. The dots and %
rings change by less than the metric's 0.012 em reach, so they score 0 here,
although their xor is 0.07–0.12.

`evidence/item3-rounded-hero.png` contains:

- `72° 18:30 −3°` at 32 px, ×3 and ×1, in Regular, r5 Rounded and r6
  Rounded;
- 96 px overlays against the sans (sans red, Rounded blue), r5 and r6;
- the 24 px strip;
- the 3 at 260 px, Regular and Black.

## 4. Mono 0 at 9 px

Measured only. The dotted default 0 and the slashed `zero` 0 are unchanged
from r5. Their outlines and variations are identical in the binary, and so
is the coverage grid at 9 px.

| wght | Dotted 0: lightest counter pixel | Slashed 0: lightest pixel each side of the slash |
| ---: | --- | --- |
| 400 | 0 above the dot, 0 below | 1 upper left, 0 lower right |
| 700 | 0 above the dot, 5 below | 2 upper left, 39 lower right |

Coverage runs from 0 (background) to 255. The counter does not close at
either weight, so per the brief nothing was changed.
`evidence/item4-mono-zero.png` shows `0 O 10 0.5` at 9 px, ×14, dotted and
slashed, 400 and 700, light and dark.

## Checks

The final `make build`, `make gate`, `make render` and `make checks` for
`r6-type` all exit 0. No hard fails.

**Gate** (`build/r6-type/gate.md`). Quality status is FAIL with 0 hard
failures, as for r5. The font-checker failures are inherited upstream
findings, and the gate preserves them.

| Face | Pass | Warn | Fail | Error | Core | Interpolation glyphs | WOFF2 bytes (r5) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 92 | 4 | 5 | 1 | 258/258 | 0 | 108328 (108328) |
| Serif | 95 | 5 | 5 | 0 | 258/258 | 3 | 197716 (197836) |
| Mono | 90 | 6 | 5 | 1 | 258/258 | 0 | 47780 (47804) |
| Sans Rounded | 98 | 0 | 2 | 1 | 29/29 | 0 | 74012 (73640) |

Pass, warn, fail and error counts are r5's.

- Name/RFN PASS on all four faces, with no reserved names.
- Icons PASS: 71 icons from the current icon folder, one stroke width
  (1.875), TSX typecheck PASS.
- Tabular figures are equal width and the default; `tnum` and `pnum` are
  present.

**Interpolation.** The gate reports serif `kink`: 4 in the same 3 glyphs as
r5 (`dagger`, `daggerdbl`, `f.ligalong`). Sans, Mono and Rounded report none.

The variable-font kink test (`checks/vfkinks.py`) finds the same 5 as r5,
all in the serif ff ligatures (`f_f`, `f_f_i`, `f_f_j`, `f_f_l`, `f_f_t`, Thin
to Black at opsz 8). Its output for r5 and r6 is byte-identical. Sans, Mono
and Rounded: 0. There are no new interpolation findings.

**Render** (`make render`, 38 sheets). Blind byte scan PASS. Headline line
contact is clear on light, dark and glass (0 contacts).

**Confusables** (`checks/figcheck.py`, xor/union, fail under 0.20, Regular,
default features): PASS.

| Face | px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.680 | 0.379 | 0.545 | 0.496 | 0.679 | 0.619 | 0.652 | 0.499 | 0.642 |
| Sans | 11 | 0.713 | 0.376 | 0.577 | 0.550 | 0.726 | 0.649 | 0.658 | 0.467 | 0.643 |
| Sans | 13 | 0.735 | 0.407 | 0.595 | 0.541 | 0.738 | 0.655 | 0.519 | 0.520 | 0.670 |
| Serif | 9 | 0.354 | 0.323 | 0.243 | 0.620 | 0.518 | 0.625 | 0.523 | 0.730 | 0.665 |
| Serif | 11 | 0.305 | 0.277 | 0.296 | 0.620 | 0.484 | 0.614 | 0.550 | 0.693 | 0.655 |
| Serif | 13 | 0.370 | 0.296 | 0.265 | 0.608 | 0.504 | 0.627 | 0.644 | 0.775 | 0.676 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.520 | 0.467 | 0.613 | 0.817 | 0.357 | 0.639 |
| Mono | 11 | 0.436 | 0.373 | 0.439 | 0.564 | 0.436 | 0.640 | 0.909 | 0.386 | 0.624 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.554 | 0.477 | 0.651 | 0.871 | 0.379 | 0.673 |
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.500 | 0.657 |
| Rounded | 11 | 0.714 | 0.380 | 0.576 | 0.540 | 0.721 | 0.636 | 0.661 | 0.466 | 0.659 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.517 | 0.691 |

Changes from r5:

- **Serif.** The thin-stroke pass thickens the bar `|` too (52 → 64 units
  wide at opsz 9 / 400; I, l and 1 are unchanged), so serif `I/|`, `l/|` and
  `1/|` drop by 0.04–0.07 (`I/|` at 9 px 0.676 → 0.620).
  The lowest of them, `l/|` at 11 px, is 0.484.
- **Rounded.** The 3's notch moves `3/7` up by 0.005–0.009.

Sans and Mono are identical to r5. The lowest value overall is still serif
l/I at 9 px, 0.243, unchanged.

**Skeleton** (`checks/skeleton.py`, Rounded against the sans at opsz 14,
largest displaced region beyond 0.012 em in thousandths of an em², fail at
4.0): PASS.

- Largest regions at 400: G 3.68, ℉ 3.56, B / E / L 3.51, F 3.43.
- Largest at 900: M 3.37.
- Over 135 glyphs the mean at 400 is 0.41, and the lowest two-way overlap
  is 0.953.
- Only three and three.pnum differ from r5 (section 3). A few bowls show
  blurred-IoU rounding of 0.001.

**Widths** (`checks/widths.py --all`, Rounded against the sans, 10 locations
× 16 strings): largest difference 0.00%. Every value is identical to r5's.
At opsz 14 / 400, in units:

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

**`make checks`** (`build/r6-type/checks.md`): PASS, identical to r5's
report. Rounded against the sans, ink width at 96 px, Regular (limit 1%):

| String | Sans | Rounded | Difference |
| --- | ---: | ---: | ---: |
| 104°F | 269.578 px | 269.578 px | +0.000% |
| 72° | 149.109 px | 149.109 px | +0.000% |
| 18:30 | 261.891 px | 261.891 px | +0.000% |
| −3° | 144.094 px | 144.094 px | +0.000% |

The hero-bowl pass keeps every extreme, so ink widths do not move.

Default shaped figures are tabular at every named instance and every axis
min, default and max combination:

- Sans (21 locations), Mono (5) and Rounded (15): PASS.
- Serif reports INFO, tabular true at 30 locations, as in r5.

**Figure defaults** (`checks/figcheck.py`): PASS.

- Sans: 21 locations, all ten default figures 1332 units, `tnum` equals the
  default, `pnum` varied.
- Serif: 30 locations, 579 units.
- Mono: 5 locations, 1217 units.
- Rounded: 15 locations, 1332 units.

**Outlines** (`checks/outlines.py`). There are 0 gated outliers (kinks,
fold-backs, added points) in the core set of sans, Rounded, serif and mono.
Reported only:

- Glyphs with only new short segments: sans 1, Rounded 1, serif 14 (r5 15),
  mono 0.
- Full repertoire, any reason:

  | Face | Text/display masters | Caption masters |
  | --- | ---: | ---: |
  | Sans | 11 | 68 |
  | Rounded | 1 | 0 |
  | Serif | 141 (r5 135) | 2 |
  | Mono | 0 | 0 |

  The checker's "caption masters" column means the sans's emboldened m06–m08.
  The serif's opsz 8 masters (m00–m02) are counted under text/display. So
  the serif's +6 comes from `thin_small`:

  - It leaves one or two new short pieces (under 5.9 units) in seven glyphs
    outside the core set, in the Regular or Black opsz 8 master. These are
    `El.sc`, `Lje.sc`, `ampersand.sc`, `estimated`, `five.cap`, `five.lf` and
    `section`.
  - `at` loses its one.
  - The later short-piece pass (`spread_short`) could not lengthen them
    within its 1 unit² limit.

**Binary** (`build/r6-type/*.ttf`, compared with r5 and checked with the
shaper):

- **Tables.** For all four faces, `cmap`, the glyph order and every advance
  are identical to r5. So are `GSUB`, `GPOS`, `GDEF`, `fvar`, `avar`, `STAT`,
  `OS/2`, `hhea`, `name` and `post`, byte for byte.
- **`hmtx`.** Identical except two mono left side bearings: `uni2103`
  10 → 0 and `uni2109` 19 → 0. Their advance stays 1217.
- **Features.** Rounded GSUB has `calt case cv08 pnum salt ss09 tnum zero`.
  The sans features are as in r5.
- **Shaping:**
  - `72℉ 22℃` (mono) → `seven two uni2109 space two two uni2103`, every
    advance 1217.
  - `18:30 −3°` (Rounded) → `… colon.fig … minus.case three degree`.
  - `0` with `zero` → `zero.slash`.
  - `!==` (mono) → one ligature over three cells, as in r5.
- **Reserved names.** None appear in any name record.

## Evidence

Each sheet has numbered callouts explained under it.

`evidence/item1-mono-temperature.png`:

- **Content.** `℉ ℃  °F °C  72℉ 72°F` at 13, 15 and 17 px, Light, Regular
  and Bold. r6 sits beside r5's form, with the composed `°F` / `°C` for
  comparison.
- **Callouts.**
  1. The letter's top on the cap height.
  2. The ring with the degree sign's counter.
  3. The ring–letter gap.
  4. The 13/15/17 px strip, with r5's form above.

`evidence/item2-serif-text-sizes.png`:

- **Content.**
  - Two lines at 9, 11 and 13 px, 400 and 600, light and dark, r5 above r6.
  - Overlays at opsz 9, 160 px, 400 and 600 (r5 red, r6 blue).
  - The opsz 32 overlay, unchanged.
- **Callouts.**
  1. The thin diagonals of v and w.
  2. The thin legs and verticals of A and N.
  3. The 9 px / 600 dark counters.
  4. The display size, unchanged.

`evidence/item3-rounded-hero.png`:

- **Content.**
  - `72° 18:30 −3°` at 32 px in Regular, r5 Rounded and r6 Rounded.
  - 96 px overlays against the sans, r5 and r6.
  - The 24 px strip.
  - The 3 at 260 px, Regular and Black.
- **Callouts.**
  1. Circular bowls.
  2. Round dots of the colon and period.
  3. % rings.
  4. The 3's closed notch.

`evidence/item4-mono-zero.png`:

- **Content.** `0 O 10 0.5` at 9 px, ×14, dotted and slashed, 400 and 700,
  light and dark.
- **Callout.** 1. The counter keeps background pixels beside the slash.

## Rules to keep

- Every outline change is a script in `transforms/`, run from the
  baseline sources by `apply.py`. Masters stay point-compatible.
- Default glyphs must pass the confusable check (`checks/figcheck.py`) at
  9, 11 and 13 px, in every face. No pair may fall under 0.20 xor among
  `1 l I |`, `rn m`, `0 O` and `3 7`.
- Rounded, at text and caption sizes, is the sans plus a round pen and
  nothing else.
  - Every Rounded master, display included, is made from the sans master of
    the same name. A change to a sans glyph changes Rounded through the same
    pen; never draw Rounded by itself.
  - `checks/skeleton.py` must pass at opsz 14: the largest displaced region
    must stay under 4.0 thousandths of an em² at 400 and 900.
- Rounded's display masters (opsz 32) may also carry the hero-bowl pass.
  - It applies only to the `HERO` set.
  - It moves handles toward circular tension and keeps extremes, tangent
    directions and advances.
  - It is accepted per glyph only if it adds no kink or roughness.
  - The display skeleton is reported (Black 0 4.87), not gated. A new
    construction for Rounded belongs in the display masters, never in the
    text masters, and must keep exact width parity.
- A short concave step in a Rounded corner is closed to one join in every
  master (`merge_notch`) before it is filleted, and its fillet reach is
  capped (`NOTCH_CUT` 1.0 stem). Filleting the two corners of the step
  leaves a notch, and the full cut reads as a dark spot at 96 px.
- Rounded widths equal the sans widths (`checks/widths.py`, under 1%), and
  tabular figures stay the default.
- Figure punctuation is fitted by pair kerning and figure-context glyphs,
  never by changing a figure's advance.
- The minus sits from a figure's ink at the median ink gap between tabular
  figures (`72 30 10 18 69`), per master. The nearest-ink limit is a floor,
  never the target.
- A mono temperature unit gives up width, never height.
  - The letter is the face's own C or F at cap height, condensed in x and
    emboldened back to its stem.
  - The ring keeps at least 0.85 of the degree sign's counter.
  - Ring and letter keep at least 1 px of nearest ink apart at 13 px, at
    every weight.
- Serif caption strength changes only the opsz 8 masters.
  - A thin-stroke gain never moves an edge that faces less than 1.5 stems of
    white, so counters keep their room.
  - The a, e and s counters must stay open at 9 px / 600 on dark.
- Every transform that moves points records the upstream drawing it starts
  from (`com.strata.source`). `checks/outlines.py` must report 0 gated
  outliers, and the gated set includes the case, tabular and figure-context
  forms.
- A pass that moves edges keeps smooth line-curve joins tangent. A pass that
  lengthens short pieces is kept only where the filled outline changes by
  less than 1 unit².
- A mono ligature that spans cells must read as one sign, with its own
  strokes (`!==`).
- Any measurement quoted here is taken from the built binary, never from a
  master or a note.

## Next steps

- **Mono ring weight.** The ℉/℃ ring's walls are 0.50 of the degree sign's
  walls, so at 13 px Bold the ring reads lighter than the letter. Two ways
  to restore 0.60 walls:
  - accept a narrower letter (the `hang` construction, letter 0.695 / 0.718
    of F/C);
  - let the ring's counter drop toward the 0.85 floor.
- **Mono figure before ℉/℃.** The ring now starts on the cell's edge. In
  `0℉` at 700 the 0 sits 0.79 px from the ring at 13 px (r5 0.87). A kern or
  a small side bearing on the unit would restore it without touching the
  ring–letter gap.
- **Black hero 0.** At display size the Black 0 moves furthest from the
  sans: xor 0.16, display skeleton 4.87. If review finds it too far from the
  sans, try `BOWL_SHARE` 0.75 at Black only. The pass already supports
  per-glyph shares.
- **Serif short pieces from the thin-stroke pass.** `thin_small` leaves
  1–2 new short pieces in seven non-core glyphs in the opsz 8 Regular or
  Black master: `El.sc`, `Lje.sc`, `ampersand.sc`, `estimated`, `five.cap`,
  `five.lf` and `section`. A fix would let `thin_small` skip an edge whose
  move would shorten a neighbouring piece under the limit, as `spread_short`
  already does.
- **Serif bar.** `|` is thickened by the thin-stroke pass. Excluding it would
  restore `I/|` to r5's 0.66–0.68.
- **Carried over from r5:**
  - the ASCII hyphen-minus before a figure;
  - the serif e and s overlap construction;
  - the serif a's 4-unit step;
  - the serif ff ligature kinks;
  - the sans caption masters' 68 reported glyphs.

## Rebuild

From the repository root:

    .venv/bin/python -I candidates/r6-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r6-type/checks/outlines.py r6-type
    make build  CAND=r6-type SUBSET=core ICONS_DIR=<icon folder>
    make gate   CAND=r6-type ICONS_DIR=<icon folder>
    make render CAND=r6-type OUT=<render folder> MAP=<map file> REFS=0 ICONS_DIR=<icon folder>
    make checks CAND=r6-type ICONS_DIR=<icon folder>
    .venv/bin/python -I candidates/r6-type/checks/figcheck.py build/r6-type
    .venv/bin/python -I candidates/r6-type/checks/skeleton.py build/r6-type
    .venv/bin/python -I candidates/r6-type/checks/widths.py build/r6-type
    .venv/bin/python -I candidates/r6-type/checks/vfkinks.py build/r6-type
