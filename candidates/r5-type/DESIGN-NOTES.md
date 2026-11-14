# r5-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r3-type, which the round 4 review preferred to
r4-type. r3's decisions hold unless a section below changes them, in
particular the footed tabular 1 (r4's spanning 1 crowded the figures), the
flat-top 3, the 2 and 7, and the serif's teardrop terminals (no landing
diagonal and no level cut). From r4 only the five pieces in section 1 are
ported, each as its own transform step. Before/after images for each item
are in `evidence/`, with numbered callouts explained under each sheet.

## Summary

All measurements are from the built fonts in `build/r5-type` and `build/r3-type`.
Unless a row says otherwise, they are at Regular (wght 400).

| Item | Change | r3 → r5 | Target |
| --- | --- | --- | --- |
| 1a Rounded pen and parity | Concentric pen; every master rounded from the sans master of the same name | Ink width at 96 px, largest difference: 0.74% → 0.00%. Mean xor over 0–9 ° % at 96 px: 0.210 → 0.025 | Met |
| 1b Serif opsz 8 | Hairlines and crossbars +16 units, sidebearings −8 a side | e crossbar 58 → 74 units. `nnoonn` 4290 → 4194 | Met |
| 1c Headline clearance | Display master cuts more | Ascender + descender at opsz 60: 1045 → 1024 units | Met |
| 1d `zero` | Slashed 0 under `zero` in sans and Rounded | Plain 0 stays the default | Met |
| 1e Degree ring | 0.44 of the figure height | 0.37 → 0.44. `72°`: ring-to-2 gap 1.68 px against 2-to-7 gap 2.27 px at 13 px | Kept |
| 2a Minus | Pair-kerned so its gap equals the median gap between tabular figures | `−3°` at 96 px: bar to 3, 15.5 → 13.3 px. Median figure gap (72 30 10 18 69) 13.3 px. Rounded 13.6 | Met |
| 2b Colon | `colon.fig` between figures | Dots 1.2× larger. `18:30` gaps at 96 px: 11.3 / 11.1 → 13.4 / 13.2 px | Met |
| 2c Hyphen | `hyphen.fig` between figures | Minus/hyphen length ratio 1.43 → 1.73. Centre difference 0.1 → 10.2 px at 96 px | Met |
| 3 Mono ℉ ℃ | Ring and letter redrawn in one cell | Letter width-for-height ℉ 0.92 → 0.99, ℃ 0.90 → 0.97. Counter 0.55 → 0.86 of the ° counter | ≥ 0.90 / ≥ 0.85: met |
| 4 Mono `!==` | Its own bars and one slash | Bars 2.62 → 2.18 cells. Slash covers about ⅓ → ½ of the bars | One sign: met |
| 5 I and l | Serifed I by default. l kerned to `/` | xor I/\| 0.44–0.45 → 0.50–0.55, 1/I 0.49–0.53 → 0.38–0.41. l to `/` 1.01 → 1.64 px at 13 px | Pass (0.20) |
| 6 Serif density | Short pieces lengthened, no shape change | Short pieces: R 4 → 0, a 8 → 2, e and s 0. Whole serif 2201 → 622 | Outliers 0: met |
| 7 Rounded at 24 px | No radius increase | Skeleton largest region 3.68 (limit 4.0). Per-glyph xor in section 7 | Within limit |

## 1. Pieces ported from r4

Each piece is one step in the transforms, written from r4's script and
checked on its own build before the next one was added.

**(a) Rounded concentric pen and width parity** (`rounded.py`). The pen is
set per weight (`WEIGHT`). In Thin and Regular it is concentric: outer
radius = join radius + one stem, so a stroke keeps its width round a
corner. Black keeps the smaller pen. In stems, outer / join / largest cut:
Thin 1.80 / 0.80 / 1.90, Regular 1.70 / 0.70 / 1.80, Black 0.60 / 0.20 /
0.90. The 7's elbow and the flat-top 3's joins take twice the join radius
(`SOFT_TURNS`, `SOFT_JOIN`).

Every master, display included, is now rounded from the sans master of the
same name. r3 already matched the sans advances (0.00% on the width table),
but its display masters reused the text outlines, centred on the display
advance. So from about 24 px up, r3's Rounded figures did not sit where the
sans puts its figures, and their ink width at 96 px was up to 0.74% off
(`make checks`). In r5 they do: at 96 px, mean xor/union over
`0–9 ° %` against the sans drops from 0.210 to 0.025. Glyphs with no corners
(0, 8, °) are now identical to the sans. `18:30` and `72°` land where the
sans puts them.

**(b) Serif caption strength and 13 px spacing** (`serif.sturdy_small`).
The opsz 8 masters are used up to about 13 px. In them, every inner
horizontal edge moves `HAIR` = 8 units into the white beside it: crossbars,
the inside of bowl tops and bottoms, serif undersides and arms. Hairlines
and crossbars gain 16 units. Outer edges on the zones stay, so heights,
overshoots and the baseline do not move. Small forms take 0.6 of the move.
At Regular the e's crossbar goes from 58 to 74 units, and ink at 9 px rises
8%. Sidebearings close by `TIGHT_8` = 8 units a side, so `nnoonn` goes from
4290 to 4194 units.

New in r5: a smooth join of a line and a curve keeps its tangent through the
move (`_retangent`). Without it, the r's ear gained a 28° kink in the
lightest caption master.

**(c) Headline clearance** (`serif.DEPTH_CUT`, `ASC_CUT`, per optical
size). The display master shortens descenders by 0.14 of their depth and
lowers ascenders by 30 units. The caption and text sizes keep r3's 0.10 and
20. At opsz 60 Regular, ascender plus descender goes from 1045 to 1024 units
(ascender 791 → 781, descender −254 → −243). The render's headline check is
clear on light, dark and glass.

**(d) `zero` in the sans and Rounded.** The plain 0 stays the default.
`zero` gives the slashed 0 (`zero.slash`), in the tabular and proportional
forms.

**(e) Larger degree ring** (`sans.DEG_D` 596 + `DEG_HEAVY` 150 × weight; r3
520). The ring is 0.43–0.44 of the figure height (r3 0.37–0.38). The
figure-to-ring kerning is r3's optical pass (`optical.degree_kerns`), so each
figure keeps the same white to the ring as 0 does.

The brief's condition was that `72°` must still read as one unit. In `72°`
the ring stays closer to the 2 than the 2 is to the 7 at every size measured:
1.68 against 2.27 px at 13 px, 2.81 against 3.90 at 24 px, 10.6 against
15.0 at 96 px (r3 ring gaps 1.74, 2.91, 11.0). So the larger ring is kept.

## 2. Numeral punctuation (sans and Rounded)

All three changes leave the figures' advances alone. Every tabular figure
stays one width, and `tabular_default` and the width parity checks still
pass. Measurements are from the built fonts with `−3°  3:45 PM  18:30  30.16
10-12` shaped at 13, 24 and 96 px (`evidence/item2-numeral-punctuation.png`).

**(a) Minus beside a figure** (`sans.minus_kerns`, `figure_gap`,
`MINUS_PAIRS`, `MINUS_FLOOR` 0.60).

In r3 the minus sat in a full figure-width cell. In `−3°` at 96 px its bar
ended 15.5 px from the 3's leftmost ink, while tabular figures sit a median
13.3 px apart.

The minus and `minus.case` are now kerned to each figure so that the ink
gap equals the median ink gap between tabular figures. The ink gap runs from
the bar's end to the figure's leftmost ink, kerning included. The median is
taken over `72`, `30`, `10`, `18` and `69` in each master, so the rule holds
at every size and weight.

One limit stays, as a floor and never as the target: the figure's nearest
ink, in any direction, never comes closer than 0.60 of the 0 0 gap. This
limit is for the 5's top bar and the 1's flag, which reach over the bar's
end. With the median as the target, the floor does not bind in any master.

An earlier r5 build matched the white area beside the bar to the gap
between two zeros instead. That pulled the bar to 3.0 px from the 3 at
96 px, and in review `−3°` read as nearly fused.

Ink gaps measured on the built fonts at Regular, in px:

| Face, size | r5 figure gaps 72 / 30 / 10 / 18 / 69 | r5 median | r5 `−3` | r5 `−0` to `−9` | r3 `−3` (r3 median) |
| --- | --- | ---: | ---: | --- | --- |
| Sans 96 px | 15.0 / 11.4 / 12.3 / 14.2 / 13.3 | 13.3 | 13.3 | 13.2–13.3 | 15.5 (13.3) |
| Rounded 96 px | 14.0 / 11.4 / 12.3 / 14.2 / 13.3 | 13.3 | 13.6 | 13.2–13.8 | 17.1 (13.9) |
| Sans 24 px | 3.9 / 3.2 / 3.3 / 3.6 / 3.7 | 3.6 | 3.4 | 3.4–3.5 | 3.9 (3.6) |
| Rounded 24 px | 3.6 / 3.2 / 3.3 / 3.6 / 3.7 | 3.6 | 3.6 | 3.4–3.6 | |
| Sans 13 px | 2.3 / 2.0 / 1.9 / 2.0 / 2.3 | 2.0 | 2.0 | 2.0 | 2.2 (2.0) |
| Rounded 13 px | 2.1 / 2.0 / 1.9 / 2.0 / 2.3 | 2.0 | 2.2 | 2.0–2.2 | |

At 96 px Thin the median is 16.6 px and `−3` is 16.5 px; at Black they are
both 6.6 px.

Two small departures:

- At 24 px the optical size falls between the text and display masters.
  The kerns interpolate linearly, but the median is taken per master, so
  the gap lands 0.1–0.2 px under the median.
- Rounded shares the sans kerning, because its widths must equal the sans
  widths. Its 3 and 5 have rounded terminals, so their leftmost ink sits a
  little further right. That leaves `−3` 0.3 px over the median at 96 px.

The white beside the bar of `−3°` at 96 px is now 27 to 41 px (least, mean;
r3 30 to 44). The kerns before tabular figures, in units of 2048, are:

| Master | Range |
| --- | --- |
| Regular | −86 (5) to −20 (4) |
| Display Regular | −69 to +8 (4) |
| Thin | −91 to −25 |
| Black | −110 to −42 |

The caption masters take their text master's values. Where a figure's ink
starts closer than the median, the kern opens the pair. This happens for
the 4 at display Regular and for many proportional figures, up to +88 units
at Display Thin.

These are pair kerns, not width changes, so a column of tabular figures
still aligns. A leading minus moves only its own figure.

**(b) Colon between figures** (`sans.colon_fig`, `COLON_DOT` 1.20,
`COLON_SPREAD` 1.08, `COLON_ROOM` 1.45). Between two figures (`3:45`,
`18:30`) the colon becomes `colon.fig`. Its dots are 1.2× the case colon's,
set 1.08× further apart about the figures' middle, so the pair is centred on
the figure height, not on the x-height. Its sidebearings are 1.45× the case
colon's. At 96 px the colon's centre is 34.9 px against a figure centre of
34.4, and its ink is 13.4 px wide (r3 11.2).

`18:30` gaps either side of the colon:

| Size | r3 | r5 |
| --- | --- | --- |
| 96 px | 11.3 / 11.1 px | 13.4 / 13.2 px |
| 24 px | 3.2 / 3.2 px | 3.9 / 3.8 px |
| 13 px | 2.0 / 2.0 px | 2.5 / 2.5 px |

Elsewhere the colon is unchanged.

**(c) Hyphen and minus** (`sans.hyphen_fig`, `HYPHEN_FIG` 0.58). Between two
figures (`10-12`) the hyphen becomes `hyphen.fig`. Its bar is 0.58 of the
minus's length and is centred on half the x-height, below the minus, which
sits on the figures' middle.

At 96 px the minus-to-hyphen length ratio goes from 1.43 to 1.73, and the
difference in centre height from 0.1 to 10.2 px. For comparison, the serif's
are 1.95 and 10.4 px. At 13 px the hyphen is 3.5 px long and sits 1.2 px
lower than the minus.

Outside figures the hyphen and `hyphen.case` are as in r3. Both
substitutions are one named lookup (`figure_punct`) in `calt`, after the case
rules, so caps and figures both reach it. Rounded measures the same as the
sans (it carries the same glyphs and lookups).

## 3. Mono ℉ and ℃

`mono.py` builds each unit from a ring and the face's own letter in one
cell:

- The ring keeps the degree sign's counter at `TEMP_COUNTER` 0.865 of its
  width and height, with walls at `TEMP_WALL` 0.60 of the degree sign's. Its
  white matches the composed `°` instead of shrinking, and it sits at the top
  of the figures.
- The letter is the face's C or F at `TEMP_LETTER` 0.82 of its height. It is
  narrowed only if the cell is short of room, and its stems are put back to
  the face's stem weight (stem-compensated scaling).
- The ring, a fixed gap and the letter are centred in the cell.

Measured on the built font. The counter is against the composed `°`; the
letter's width-for-height is against the face's own F or C.

| Weight | Counter (r3) | ℉ letter (r3) | ℃ letter (r3) |
| --- | --- | ---: | ---: |
| Light 300 | 0.86 × 0.87 (0.51 × 0.50) | 1.02 (0.97) | 1.00 (0.94) |
| Regular 400 | 0.86 × 0.87 (0.55 × 0.55) | 0.99 (0.92) | 0.97 (0.90) |
| Bold 700 | 0.86 × 0.87 (0.70 × 0.68) | 0.91 (0.82) | 0.90 (0.81) |

Both targets are met at every weight: letter ≥ 0.90, counter ≥ 0.85. One
cell holds both because the letter gives up height, not width. In r3 the
ring took 0.29 to 0.34 of the cell and the letter its full height, so the
ring closed up at 13 to 17 px. In r5 the ring takes 0.40 to 0.41 of the
cell. `evidence/item3-mono-temperature.png` shows 13, 15 and 17 px beside
the composed `°F` and `°C`.

## 4. Mono `!==`

Shaping was already right in r3: `!==` becomes one ligature over three cells
(`exclam.spacer equal.spacer exclam_equal_equal.liga`). `===`, `!=`, `=/=`,
`<=`, `>=`, `->` and `=>` each shape to one ligature or one sequence with no
leftover glyph. I checked this in r3 and r5 at 300, 400 and 700, and it is
unchanged.

The drawing was the problem. r3 drew `!==` as the `===` bars, 2.62 cells
long, with the `!=` slash in the middle. The slash covered about a third of
the bars, so the right-hand end read as a leftover `=`.

`mono.open_triple_bars` now gives `!==` its own three bars:

- Each end is `NOT_INSET` 0.22 of a cell shorter than `===`, so the bars are
  2.18 cells long and never read as `===`.
- One slash crosses them at the centre. It travels `NOT_TRAVEL` one cell and
  rises `NOT_RISE` 1.05 times the bar stack, so it covers about half the
  bars.
- Measured square to the stroke, the slash is as thick as the `!=` slash:
  Light 119.8 against 119.6 units, Bold 221.3 against 221.3.

The ligature is kept rather than dropped, because `!=` and `===` already
ligate and a plain `!==` beside them would look like a missing feature.

## 5. I and l

**Serifed I by default** (`sans.serifed_i`, `short_i_bars`, `I_BAR` 0.62).
In r3 the default I was the bare stem. The I with bars is now the default in
the sans and Rounded at every optical size, including the caption masters,
which are made from the finished text masters. Its bars are 0.62 of the
upstream reach beyond the stem, so a word in capitals stays even. The bare I
is `I.1`, under `ss09` ("Upper-case i without serifs"), `cv08` and `salt`.

**Room after the tailed l** (`sans.l_slash_kerns`, `L_SLASH_EM` 0.085,
`L_SLASH` 0.45). The l is kerned to the slash until their nearest ink, over
the x-height band, is 0.085 em plus 0.45 of a stem apart. At Regular that is
259 units, or 1.64 px at 13 px (r3 159 units, 1.01 px). Thin keeps 194 units
and Black 356. The kern opens the pair: `l/` gains 104 units at Regular.

Confusable xor/union, sans at Regular, default features (fail under 0.20):

| Pair | 9 px r3 → r5 | 11 px r3 → r5 | 13 px r3 → r5 |
| --- | --- | --- | --- |
| I/\| | 0.440 → 0.496 | 0.451 → 0.550 | 0.453 → 0.541 |
| 1/I | 0.487 → 0.379 | 0.494 → 0.376 | 0.528 → 0.407 |
| l/I | 0.530 → 0.545 | 0.580 → 0.577 | 0.608 → 0.595 |
| 1/l | 0.680 → 0.680 | 0.713 → 0.713 | 0.735 → 0.735 |
| l/\| | 0.679 → 0.679 | 0.726 → 0.726 | 0.738 → 0.738 |
| 1/\| | 0.619 → 0.619 | 0.649 → 0.649 | 0.655 → 0.655 |

Rounded is within 0.02 of the sans on every pair (full table under Checks).
1/I gets closer because both now carry bars. At 0.376 it is still well over
the 0.20 limit, and the 1's flag keeps it apart.

## 6. Serif point density

No point is redundant in all nine masters: there are no collinear line
points and no smooth join whose two segments could merge, at 0.75 unit
tolerance. Removing a point in one master would break interpolation, so the
point counts stay as they are (R 63, e 34, a 63, s 48).

What made the outlines look dense was short pieces: on-curve points closer
than 12/2048 em. `serif.spread_short` lengthens each short line piece to 1.3
times that limit. It slides one end along its neighbouring segment's own
direction (along a line, or along a curve's tangent together with its
handle), so no shape moves. A move is kept only if all three hold:

- The filled outline changes by less than 1 unit² (exact boolean XOR area).
- No neighbouring piece becomes short.
- No join gains a kink.

Short pieces over the nine masters, per glyph:

| Glyph | r3 | r5 | Where |
| --- | ---: | ---: | --- |
| R | 4 | 0 | Top serif meeting the stem (m00, m01, m03, m04) |
| a | 8 | 2 | Stem meeting its foot curve. The two left are in the lightest caption masters |
| e | 0 | 0 | |
| s | 0 | 0 | |
| All serif glyphs | 2201 | 622 | Baseline 1686 |

Inside the pipeline the step itself counts 2163 short pieces before and 617
after. The difference from the table is pieces that later steps add or
remove.

The two short pieces left on a are a 4-unit step. Lengthening them would
change the filled area by about 12 unit², over the 1 unit² limit, so they
stay.

e and s look dense in a point view because they are built from overlapping
contours (crossbar and beak), not because of short pieces. That is
construction, not density, and this round leaves it.

Outline outliers on the gated core set are 0 on every face. Serif core
glyphs reported with only new short segments go from 32 to 15. Glyphs in
the full repertoire reported for any reason go from 263 to 135.

## 7. Rounded at 24 px

No radius was pushed past the skeleton limit. The largest displaced region
is 3.68 thousandths of an em² at 400 and 3.37 at 900, against the 4.0 limit.

Per-glyph xor/union of Rounded against the sans, centre-aligned, at
Regular, with opsz equal to the pixel size:

| px | build | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | ° | % | mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | r3 | 0.098 | 0.080 | 0.152 | 0.172 | 0.211 | 0.187 | 0.135 | 0.080 | 0.026 | 0.136 | 0.067 | 0.204 | 0.129 |
| 24 | r5 | 0.000 | 0.030 | 0.020 | 0.067 | 0.036 | 0.083 | 0.009 | 0.115 | 0.000 | 0.014 | 0.000 | 0.013 | 0.032 |
| 48 | r3 | 0.178 | 0.121 | 0.261 | 0.253 | 0.346 | 0.300 | 0.231 | 0.084 | 0.049 | 0.232 | 0.121 | 0.340 | 0.210 |
| 48 | r5 | 0.000 | 0.024 | 0.018 | 0.037 | 0.030 | 0.075 | 0.008 | 0.099 | 0.000 | 0.009 | 0.000 | 0.012 | 0.026 |
| 96 | r3 | 0.179 | 0.120 | 0.260 | 0.253 | 0.349 | 0.299 | 0.232 | 0.082 | 0.047 | 0.232 | 0.120 | 0.341 | 0.210 |
| 96 | r5 | 0.000 | 0.023 | 0.017 | 0.034 | 0.028 | 0.075 | 0.007 | 0.099 | 0.000 | 0.007 | 0.000 | 0.009 | 0.025 |

Read this table as two different effects:

- **r3's numbers are mostly not rounding.** They are the optical-size
  mismatch from section 1a: r3's Rounded drew every size above the text size
  from the text outlines. That is why its 0, 8 and ° differ from the sans
  although they have no corners.
- **r5's numbers are the pen alone.** 0, 8 and ° come out identical to the
  sans. The 7's soft elbow (0.10–0.12), the 5 (0.08) and the 3 (0.03–0.07)
  carry the difference.

At 24 px the Regular stroke is about 2.2 px. Rounding a terminal on it
changes less than a pixel, so Rounded reads as the sans. **Rounded is for
hero numerals at 32 px and up.** Below 32 px, use the sans.

## Checks

Final `make build`, `make gate`, `make render` and `make checks` for
`r5-type` all exit 0. No hard fails.

**Gate** (`build/r5-type/gate.md`). Quality status FAIL with 0 hard failures,
as for r3: the font-checker failures are inherited upstream findings, and
the gate preserves them.

| Face | Pass | Warn | Fail | Error | Core | Interpolation glyphs | WOFF2 bytes (r3) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 92 | 4 | 5 | 1 | 258/258 | 0 | 108328 (107932) |
| Serif | 95 | 5 | 5 | 0 | 258/258 | 3 | 197836 (196676) |
| Mono | 90 | 6 | 5 | 1 | 258/258 | 0 | 47804 (47732) |
| Sans Rounded | 98 | 0 | 2 | 1 | 29/29 | 0 | 73640 (64944) |

Pass, warn, fail and error counts are the same as r3's. Rounded is larger
because its display masters now carry their own outlines.

Name/RFN PASS on all four faces, with no reserved names. Icons PASS (64, one
stroke width). Tabular figures are equal width and the default; `tnum` and
`pnum` are present.

**Interpolation.** The gate reports serif `kink`: 4 in 3 glyphs, the same as
r3. Sans, Mono and Rounded: none. The variable-font kink test
(`checks/vfkinks.py`) finds 5 in the serif, all in the ff ligatures
(`f_f`, `f_f_i`, `f_f_j`, `f_f_l`, `f_f_t`, Thin to Black at opsz 8). They
were present in r3. r3 also had a sixth finding, μ (underweight), which r5
clears. Sans, Mono and Rounded: 0. So there are no new interpolation
findings.

**Render** (`make render`, 38 sheets). Blind byte scan PASS. Headline line
contact: clear on light, dark and glass (0 contacts).

**Confusables** (`checks/figcheck.py`, xor/union, fail under 0.20, Regular,
default features): PASS.

| Face | px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.680 | 0.379 | 0.545 | 0.496 | 0.679 | 0.619 | 0.652 | 0.499 | 0.642 |
| Sans | 11 | 0.713 | 0.376 | 0.577 | 0.550 | 0.726 | 0.649 | 0.658 | 0.467 | 0.643 |
| Sans | 13 | 0.735 | 0.407 | 0.595 | 0.541 | 0.738 | 0.655 | 0.519 | 0.520 | 0.670 |
| Serif | 9 | 0.354 | 0.323 | 0.243 | 0.676 | 0.587 | 0.672 | 0.524 | 0.730 | 0.664 |
| Serif | 11 | 0.305 | 0.277 | 0.296 | 0.671 | 0.551 | 0.667 | 0.551 | 0.693 | 0.654 |
| Serif | 13 | 0.370 | 0.296 | 0.265 | 0.662 | 0.569 | 0.675 | 0.646 | 0.775 | 0.678 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.520 | 0.467 | 0.613 | 0.817 | 0.357 | 0.639 |
| Mono | 11 | 0.436 | 0.373 | 0.439 | 0.564 | 0.436 | 0.640 | 0.909 | 0.386 | 0.624 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.554 | 0.477 | 0.651 | 0.871 | 0.379 | 0.673 |
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.499 | 0.648 |
| Rounded | 11 | 0.714 | 0.380 | 0.576 | 0.540 | 0.721 | 0.636 | 0.661 | 0.467 | 0.652 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.520 | 0.686 |

The lowest value is serif l/I at 9 px, 0.243 (r3 0.227).

**Skeleton** (`checks/skeleton.py`, Rounded against the sans, largest
displaced region beyond 0.012 em in thousandths of an em², fail at 4.0):
PASS. The largest regions are G 3.68, ℉ 3.56, B / E / L 3.51, F 3.43, P / R
3.36 at 400, and M 3.37 at 900. Over 135 glyphs the mean is 0.40, and the
lowest two-way overlap is 0.953.

**Widths** (`checks/widths.py`, Rounded against the sans, 10 locations × 16
strings): largest difference 0.00%. At opsz 14 / 400, in units:

| String | Sans | Rounded | r3 |
| --- | ---: | ---: | ---: |
| 72° | 3558 | 3558 | 3488 |
| −3° | 3505 | 3505 | 3482 |
| 104°F | 6150 | 6150 | 6070 |
| 18:30 | 6165 | 6165 | 5962 |
| 80% | 4703 | 4703 | 4703 |
| 30.16 | 5962 | 5962 | 5962 |
| 0123456789 | 13400 | 13400 | 13400 |
| 12:05 | 6165 | 6165 | 5962 |
| −12°C | 6327 | 6327 | 6313 |
| 3 PM | 5104 | 5104 | 5104 |
| 12 mph NNW | 13279 | 13279 | 13279 |
| 30.16 inHg | 11124 | 11124 | 11124 |
| Thu | 3780 | 3780 | 3780 |
| ½ ¼ ¾ | 6384 | 6384 | 6384 |
| 72℉ 22℃ | 10403 | 10403 | 10243 |
| Rain, 40%. | 10701 | 10701 | 10701 |

The changes from r3 are the larger ring (`72°`, `104°F`), the minus kern
(`−3°`, `−12°C`) and the figure colon (`18:30`, `12:05`).

**`make checks`** (`build/r5-type/checks.md`): PASS. Rounded against the
sans, ink width at 96 px, Regular (limit 1%):

| String | Sans | Rounded | r5 diff | r3 diff |
| --- | ---: | ---: | ---: | ---: |
| 104°F | 269.578 px | 269.578 px | +0.000% | −0.335% |
| 72° | 149.109 px | 149.109 px | +0.000% | +0.740% |
| 18:30 | 261.891 px | 261.891 px | +0.000% | −0.385% |
| −3° | 144.094 px | 144.094 px | +0.000% | +0.362% |

Default shaped figures are tabular at every named instance and at each axis
min, default and max combination. Sans (21 locations), mono (5) and Rounded
(15) PASS. The serif reports INFO with tabular figures true at 30
locations, as in r3.

**Outlines** (`checks/outlines.py`): 0 gated outliers (kinks, fold-backs,
added points) in the core set of sans, Rounded, serif and mono. The gated
set includes the case, tabular and figure-context forms. Reported only:

- Glyphs with only new short segments: sans 1, Rounded 1, serif 15, mono 0.
- Full repertoire, any reason: sans 11 in the text and display masters and
  68 in the caption masters; Rounded 1; serif 135 and 2; mono 0.
- TrueType conversion adds points: sans `zero.pnum` and `zero.pnum.slash`,
  and 13 mono core glyphs (O Q a b colon d nine o p q question six zero).

**Binary** (`build/r5-type/*.ttf`, checked with the shaper):

- Sans GSUB has `calt`, `case`, `cv08`, `ss09`, `zero`, `tnum` and `pnum`
  among its features. Rounded has `calt case cv08 pnum salt ss09 tnum zero`.
- The new glyphs are unencoded: `colon.fig` (805), `hyphen.fig` (843),
  `I.1` (562), `zero.slash` (1340).
- Shaping results:
  - `3:45` → `three colon.fig four five`
  - `10-12` → `… hyphen.fig …`
  - `−3` → `minus.case three` with the minus advance 1340 → 1304
  - `I` → `I` (serifed); `I` with `ss09` or `cv08` → `I.1`
  - `0` with `zero` → `zero.slash`
  - `l/` → l advance 576 → 680
- Mono: `!==` → `exclam.spacer equal.spacer exclam_equal_equal.liga`. ℃ and
  ℉ are encoded at one cell (1217).

## Evidence

Each sheet has numbered callouts explained under it.

- `evidence/item1-r4-ports.png`, r3 and r5:
  - Rounded (red) over the sans (grey) in `18:30  72°  −3°` at 24, 48 and
    96 px.
  - The serif at 9 and 13 px.
  - Two serif lines set solid at 48 px.
  - `zero` off and on at 32 px.
  - `72°` at 13, 16 and 24 px.
- `evidence/item2-numeral-punctuation.png`: `−3°  3:45 PM  18:30  30.16  10-12`
  at 13, 24 and 96 px, r3 and r5, in the sans and Rounded, and `−3` against
  `72  30  10  18  69` at 96 px (callout 4). The serif at 24 px is shown for
  reference.
- `evidence/item3-mono-temperature.png`: `℉ ℃  °F °C  72℉ 72°F` at 13, 15
  and 17 px, Light, Regular and Bold, r3 and r5.
- `evidence/item4-code-ligatures.png`: `a !== b  a === b  a != b  a =/= b
  <= >= -> =>`, r3 and r5, at Regular (13, 15, 24 and 48 px) and Bold
  (24 px).
- `evidence/item5-I-and-l.png`:
  - `I l 1 |  Il1|  ml/h  l/s  AIR` at 9, 11 and 13 px, r3 and r5, in the
    sans and Rounded.
  - The default I and `ss09` at 24 px.
  - The sans caption size at 9 and 13 px.
- `evidence/item6-serif-clusters.png`: point views of R, e, a and s with
  short pieces ringed, at opsz 8 and opsz 20 Regular, r3 and r5.
- `evidence/item7-rounded-sizes.png`: Rounded over the sans in `0–9 ° %` at
  24, 32, 48 and 96 px, r3 and r5, and r5 Rounded alone.

## Rules to keep

- Every outline change is a script in `transforms/`, run from the
  baseline sources by `apply.py`. Masters stay point-compatible.
- Default glyphs must pass the confusable check (`checks/figcheck.py`) at
  9, 11 and 13 px, in the sans and in Rounded. No pair may fall under 0.20
  xor among `1 l I |`, `rn m`, `0 O` and `3 7`.
- Rounded is the sans plus a round pen and nothing else.
  - Every Rounded master, display included, is made from the sans master of
    the same name. A change to a sans glyph changes Rounded through the same
    pen; never draw Rounded by itself.
  - `checks/skeleton.py` must pass: largest displaced region under 4.0
    thousandths of an em² at 400 and 900.
  - Rounded is for hero numerals at 32 px and up. At 24 px and below its
    rounding is close to the pixel and it reads as the sans.
- Rounded widths equal the sans widths (`checks/widths.py`, under 1%), and
  tabular figures stay the default.
- Figure punctuation is fitted by pair kerning and figure-context glyphs,
  never by changing a figure's advance.
- The minus sits from a figure's ink at the median ink gap between tabular
  figures (`72 30 10 18 69`), per master. The nearest-ink limit is a floor,
  never the target. Matching white area instead pulled the bar to 3 px from
  the 3 at 96 px, and it read as fused.
- Every transform that moves points records the upstream drawing it starts
  from (`com.strata.source`). `checks/outlines.py` must report 0 gated
  outliers, and the gated set includes the case, tabular and figure-context
  forms.
- A pass that moves edges (the serif's caption strengthening) keeps smooth
  line-curve joins tangent. A pass that lengthens short pieces is kept only
  where the filled outline changes by less than 1 unit².
- A mono ligature that spans cells must read as one sign. Its strokes are
  its own, not stretched from a neighbour, and are shorter than the forms it
  could be mistaken for (`!==` bars inside `===`'s). A slash or other stroke
  it shares with a smaller ligature keeps that ligature's thickness (`!==`
  against `!=`).
- Any measurement quoted here is taken from the built binary, never from a
  master or a note.

## Next steps

- **ASCII hyphen-minus before a figure.** `-3°` typed with the ASCII
  hyphen-minus is not kerned or replaced; only U+2212 is. A `calt` rule
  turning hyphen-minus into the minus before a figure at the start of a word
  would cover typed temperatures. It needs a rule for ranges and dates
  (`10-12`, `2026-11-13`), which must keep `hyphen.fig`.
- **Serif e and s, and the serifs of R.** These are drawn as overlapping
  contours, so a point view of them looks dense even where no piece is
  short. Removing overlaps master by master would need matching contour
  structure in all nine masters. That is a construction change for its own
  round.
- **Serif a.** Two short pieces remain: a 4-unit step where the stem meets
  its foot curve, in the two lightest caption masters. Redrawing that join
  from upstream would clear them.
- **Serif ff ligatures.** The 5 variable-font kink findings (Thin to Black
  at opsz 8) are inherited from r3. Fixing them needs the ligature parts
  re-planned on one reference master.
- **Reported outline counts.** The sans caption masters report 68 glyphs
  outside the core set. The mono's TrueType conversion adds points on 13
  core glyphs. Neither is gated; both are worth a pass before the full
  repertoire ships.

## Rebuild

From the repository root:

    .venv/bin/python -I candidates/r5-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r5-type/checks/outlines.py r5-type
    make build  CAND=r5-type SUBSET=core ICONS_DIR=<icon folder>
    make gate   CAND=r5-type ICONS_DIR=<icon folder>
    make render CAND=r5-type OUT=<render folder> MAP=<map file> REFS=0 ICONS_DIR=<icon folder>
    make checks CAND=r5-type ICONS_DIR=<icon folder>
    .venv/bin/python -I candidates/r5-type/checks/figcheck.py build/r5-type
    .venv/bin/python -I candidates/r5-type/checks/skeleton.py build/r5-type
    .venv/bin/python -I candidates/r5-type/checks/widths.py build/r5-type
    .venv/bin/python -I candidates/r5-type/checks/vfkinks.py build/r5-type
