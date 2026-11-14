# r7-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r6-type, and r6's decisions hold unless a section
below changes them. These are kept as r6 left them and re-checked on the r7
binary:

- the barred default I;
- Rounded width parity (0.00%);
- open 9 px figures;
- the minus kerning in `−3°`;
- the larger figure colon;
- the minus distinct from the hyphen;
- tabular figures by default;
- `zero`;
- `!==` as one ligature;
- r6's ℉/℃ letter (full cap height) and its 1 px ring gap.

Three items were worked. Every other outline is unchanged (section 4).
Before/after images for each item are in `evidence/`, with numbered callouts
explained under each image. Every number in this file is measured on the
built fonts in `build/r7-type` and `build/r6-type`, and the item numbers are
measured on rendered pixels (2x, the specimen themes), unless a line says
otherwise.

## Summary

| Item | Asked | Built r7, measured |
| --- | --- | --- |
| 1. Mono ℉/℃ ring | Letter 1.00 ± 0.02 of F/C, advance kept; ring wall within ±10 % of `°`'s, ring height ≥ 0.90 of `°`; gap ≥ 1 px at 13 px, no contact | Letter height 0.999–1.000; advance 1217 units. Ring 0.92–0.98 of the typed `°`'s height (r6 0.65–0.74); side walls 0.94–0.99 and top walls 0.98–1.07 of its walls (r6 0.55–0.65). Gap ≥ 1.00 px at all 16 sub-pixel positions at 13, 15 and 17 px, Regular and Bold (r6: down to 0.50 px); no contact. Trade-off: a narrower Bold C (0.68–0.71 of the face's C on the render, r6 0.74–0.77), and the letter may overhang into the next cell, so a dash or slash set directly after a Bold unit comes close (below). |
| 2. Serif at text sizes | Find why r6 did not show; 9 px `i` ≥ 1.5 px; hairlines heavier at 9–13 px; ≥ 24 px unchanged; a/e/s open at 9 px / 600 dark | The renderer does use the opsz 8 masters at 9–13 px (the cause was not in `scripts/`). r6's change was below a pixel, and the colour match had thinned the caption stems. 9 px / 400 `i`: 1.57 px with 1 solid pixel → 1.83 px with 2 (light); 1.92 → 2.27 (dark). Hairlines +0.10 to +0.58 px. At 24 and 32 px every measure is identical, with summed ink within 0.05 %; the opsz 20 and 60 masters are byte-identical to r6. a, e, s keep 14, 6 and 5 enclosed counter pixels. |
| 3. Rounded 3 | Round top, softer upper turn, never `ʒ`; exact width parity | Drawn from the sans round-top 3 under the same round pen. Widths +0.00 % at 10 locations × 16 strings. The 3–° gap closes by 1.94 px (`−3°`) and 2.32 px (`23°`) at 96 px, with no kerning change. |
| 4. Everything else | Byte-identical outlines | The UFOs differ from r6 only in the item glyphs. In the binary, glyph order, cmap, hmtx, GSUB, GPOS, GDEF, fvar, avar, STAT, name and HVAR are identical in all four faces. |

## 1. Mono ℉ and ℃: the ring

**What was wrong.** r6 gave the letter its full cap height and kept a 1 px
gap, but its ring was a drawn ellipse with 0.865 of the degree sign's counter
and half its walls. On the rendered sheet it measured about 0.64–0.75 of the
typed `°` and 0.55–0.65 of its wall weight, so a ℉ read lighter and smaller
than a composed `°F` beside it.

**The ring.** The ring is now the face's own degree sign: its two contours,
each scaled about the degree sign's centre, the outer one to `RING_H` 0.93 of
the degree sign's height and `RING_W` of its width, the inner one so that the
walls keep `WALL` 0.97 of the degree sign's side and top walls. Its top stays
on the degree sign's top. The letter is r6's (the face's C or F at full cap
height, condensed in x and emboldened back to its stems), at `GAP` 1.20 px
of nearest ink from the ring at 13 px. Advances are unchanged (one cell, 1217
units).

**Trade-offs.** A ring this size and a 1 px gap leave less of the cell for the
letter. The constructions built and measured (`TEMP_R7` in
`transforms/mono.py`) trade the cell's edges, the ring's width and the
letter's width:

- **hang**: full ring (0.93 × 0.93), its left ink 0.10 cell past the cell's
  left edge, over the left sidebearing; letter ends on the right edge.
- **narrow**: full ring on the cell's left edge, letter narrower. At Bold no
  letter width keeps the 1 px gap inside the cell, so it was dropped.
- **oval**: ring 0.84 wide × 0.93 tall, hanging 0.06 cell; the letter may pass
  the right edge by 0.04 cell (a unit is followed by a space or nothing).
- **graded**: as oval with ring width 0.86, but the hang is per master: the
  Light ring hangs 0.06 cell, the Bold ring sits on the cell's edge, because
  the Bold figure before the unit leaves the least room.
- **graded2**: graded with a narrower Bold ring (0.80 wide, still 0.93 tall
  with 0.97 walls) and the Bold letter up to 0.08 cell past the right edge.
  This was the first r7 build.
- **graded3**: between the two (Bold ring 0.82 wide).
- **inset** (kept): a 1.20 px gap; the Light ring on the cell's left edge
  and the Bold ring 0.03 cell inside it; the ring 0.82 (Light) and 0.77
  (Bold) of the degree sign's width, still 0.93 tall with 0.97 walls; the
  letter up to 0.07 (Light) and 0.10 (Bold) cell past the right edge.

Measured on the built masters and instances (design units converted to px at
13 px; "letter" is the letter's width against the face's F or C; "clear" is
the nearest ink from the ring to a `0` in the previous cell):

| Construction | wght | Ring w × h of `°` | Wall of `°` | Letter F / C | Clear from `0`, px | Ring left / letter right, units |
| --- | ---: | --- | ---: | --- | ---: | --- |
| r6 (hangtuck) | 300 | 0.72 × 0.75 | 0.50 | 0.76 / 0.80 | 1.50 | 0 / 1217 |
|  | 400 | 0.70 × 0.73 | 0.50 | 0.73 / 0.79 | 1.42 | 0 / 1217 |
|  | 700 | 0.66 × 0.69 | 0.50 | 0.67 / 0.76 | 1.24 | 0 / 1217 |
| hang | 300 | 0.93 × 0.93 | 0.97 | 0.74 / 0.75 | 0.55 | −122 / 1217 |
|  | 400 | 0.93 × 0.93 | 0.97 | 0.70 / 0.72 | 0.46 | −122 / 1217 |
|  | 700 | 0.93 × 0.93 | 0.97 | 0.60 / 0.64 | **0.23** | −122 / 1217 |
| narrow | 700 | 0.93 × 0.93 | 0.97 | no fit | – | 0 / 1217 |
| oval | 300 | 0.84 × 0.93 | 0.97 | 0.82 / 0.82 | 0.87 | −73 / 1266 |
|  | 400 | 0.84 × 0.93 | 0.97 | 0.77 / 0.79 | 0.77 | −73 / 1266 |
|  | 700 | 0.84 × 0.93 | 0.97 | 0.67 / 0.71 | **0.54** | −73 / 1266 |
| graded | 300 | 0.86 × 0.93 | 0.97 | 0.82 / 0.82 | 0.87 | −73 / 1278 |
|  | 400 | 0.86 × 0.93 | 0.97 | 0.74 / 0.76 | 0.91 | −52 / 1278 |
|  | 700 | 0.86 × 0.93 | 0.97 | **0.58 / 0.63** | 1.03 | 0 / 1278 |
| graded2 | 300 | 0.86 × 0.93 | 0.97 | 0.82 / 0.82 | 0.87 | −73 / 1278 |
|  | 400 | 0.84 × 0.93 | 0.97 | 0.77 / 0.79 | 0.91 | −52 / 1289 |
|  | 700 | 0.80 × 0.93 | 0.97 | 0.67 / 0.72 | 1.02 | 0 / 1314 |
| graded3 | 400 | 0.85 × 0.93 | 0.97 | 0.76 / 0.79 | 0.91 | −52 / 1289 |
|  | 700 | 0.82 × 0.93 | 0.97 | 0.66 / 0.70 | 1.02 | 0 / 1314 |
| **inset** (kept) | 300 | 0.82 × 0.93 | 0.97 | 0.76 / 0.77 | 1.34 | 0 / 1302 |
|  | 400 | 0.80 × 0.93 | 0.97 | 0.73 / 0.75 | 1.32 | 11 / 1313 |
|  | 700 | 0.77 × 0.93 | 0.97 | 0.66 / 0.70 | 1.26 | 37 / 1339 |

Letter height is 1.000 of the face's F/C in every row. The ring–letter gap
in the outlines is 1.05 px at 13 px in every row except inset (1.20 px). The
cell is 0–1217 units; a negative left is a hang over the left sidebearing, a
positive one an inset, and a right past 1217 an overhang into the space after
the unit.

For comparison, a typed `°` keeps 2.18 px (Light) and 1.92 px (Bold) from a
`0` before it.

Why inset:

- **hang** has the full ring but comes within 0.23 px of a Bold `0` before it
  at 13 px (0.46 px at Regular), so `20℉` reads as a single blob at Bold.
- **oval** keeps the letter widest but still comes within 0.54 px of a Bold
  `0`.
- **graded** clears every figure by at least 0.87 px, but its Bold letter is
  0.58 (F) and 0.63 (C) of the face's F and C. On the 13 px strip the Bold
  ℃'s C read as a parenthesis.
- **graded2** keeps graded's clearance in the outlines and gives the Bold
  letter back r6's width (F 0.67, C 0.72), so it was built first. On the
  render it fell short (table below): its 1.05 px design gap read under 1 px
  at a quarter to three quarters of the sub-pixel positions at 13 px (down
  to 0.50 px), and its hanging Light ring came within 0.50 px of a `0`
  before it, where r6 kept 1.00 px. The renderer's anti-aliasing darkens
  each edge by about half a raster pixel past the outline, so a gap drawn
  at 1.05 px renders as one at about 0.5–1.0 px depending on where the
  glyph falls on the pixel grid.
- **inset** pays for a 1.20 px gap and an un-hung ring with a narrower ring
  (0.82 / 0.77 of the degree sign's width; the height and walls keep their
  values) and a longer overhang (0.10 cell at Bold), and so keeps the Bold
  letter at 0.66 (F) and 0.70 (C), the floor below which the Bold C read as
  a parenthesis. Its gap and its clearance from a `0` before it both hold at
  least 1.00 px at every sub-pixel position at 13 px, in Regular and Bold.

**Sub-pixel positions.** One render puts each glyph at one sub-pixel
position, so a single measurement can land on a lucky or an unlucky phase.
`browser_gap.py` (work tool) renders each unit alone, after a `0` and before
a `0`, at 16 positions (4 × 4, a quarter raster pixel apart, 2x, light
theme) and measures each with the same metric as the strip below (nearest
pixel centres of the two parts' ink at half coverage or more, minus one, in
CSS px). Candidates were built as static fonts from the same masters by the
same code; the graded2 probe reads the same as the built first r7. At 13 px:

| Construction | wght | ℉ gap min / median (share < 1 px) | ℃ gap min / median (share < 1 px) | Ring from `0` before, min | Letter to `0` after, min |
| --- | ---: | --- | --- | ---: | ---: |
| r6 (built) | 400 | 1.00 / 1.00 (0 %) | 0.62 / 0.91 (75 %) | 1.00 | 1.00 |
|  | 700 | 0.50 / 1.00 (25 %) | 0.62 / 0.91 (100 %) | 1.00 | 0.62 |
| graded2 (first r7 build) | 400 | 0.50 / 1.00 (25 %) | 0.50 / 0.91 (75 %) | 0.50 | 0.50 |
|  | 700 | 0.50 / 1.00 (25 %) | 0.62 / 1.00 (50 %) | 0.62 | 0.00 |
| graded2, gap 1.30 px | 400 | 1.00 / 1.00 (0 %) | 1.00 / 1.00 (0 %) | 0.50 | 0.50 |
|  | 700 | 1.00 / 1.00 (0 %) | 1.00 / 1.00 (0 %) | 0.62 | 0.00 |
| inset (probe) | 400 | 1.00 / 1.00 (0 %) | 1.00 / 1.00 (0 %) | 1.00 | 0.50 |
|  | 700 | 1.00 / 1.00 (0 %) | 1.00 / 1.00 (0 %) | 1.00 | 0.00 |
| **inset (built, kept)** | 400 | 1.00 / 1.00 (0 %) | 1.00 / 1.00 (0 %) | 1.00 | 0.50 |
|  | 700 | 1.00 / 1.00 (0 %) | 1.00 / 1.00 (0 %) | 1.00 | 0.00 |

At 15 and 17 px the built r7 also keeps ≥ 1.00 px ring to letter at every position (r6: 0.91 px for ℃ at 15 px), and ≥ 1.00 px from a `0` before it.

"Before" is the ring's distance from a `0` in the previous cell (`20℉`);
"after" is the letter's distance from a `0` in the next cell, a stress case
(a unit is followed by a space or punctuation), and the price of the
overhang: at 13 px the r7 letter comes within 0.50 px (Regular) and 0.00 px (Bold) of a `0` set directly after it, where r6 kept 1.00 px and 0.62 px.

The punctuation that does follow a unit was measured in the outlines instead: the nearest ink between the letter and the next cell's glyph, at 13 px, before the renderer's darkening (about half a raster pixel per edge, so under about 1 px reads as touching). Values are r6 → r7 in px; negative means overlap.

| After the unit | 400 ℉ | 400 ℃ | 700 ℉ | 700 ℃ |
| --- | --- | --- | --- | --- |
| `0` | 1.47 → 0.83 | 1.34 → 0.76 | 1.17 → 0.35 | 1.05 → 0.32 |
| `,` | 4.25 → 3.72 | 2.99 → 2.35 | 3.71 → 2.99 | 2.75 → 1.97 |
| `.` | 4.09 → 3.57 | 2.88 → 2.24 | 3.57 → 2.86 | 2.67 → 1.87 |
| `)` | 2.76 → 2.23 | 2.73 → 2.20 | 2.47 → 1.79 | 2.43 → 1.75 |
| `]` | 2.37 → 1.77 | 2.35 → 1.75 | 2.04 → 1.24 | 2.03 → 1.22 |
| `;` `:` | 3.44 → 2.80 | 2.96 → 2.32 | 3.12 → 2.30 | 2.75 → 1.95 |
| `-` | 2.48 → 1.84 | 3.26 → 2.91 | 2.40 → 1.57 | 2.77 → 2.27 |
| `/` | 3.29 → 2.72 | 1.12 → 0.55 | 2.77 → 1.92 | 0.83 → **0.11** |
| `–` | 0.91 → 0.27 | 2.58 → 2.53 | 0.77 → **−0.05** | 1.89 → 1.81 |

A space, a comma, a full stop or a closing bracket keeps clear room. Two followers do not:

- An en dash after a Bold ℉ meets the F's middle arm (`20℉–25℉`).
- A slash after a Bold ℃ comes within 0.11 px (`20℃/68℉`).

Setting the unit only after the range (`20–25℉`) avoids both. This is the open cost of inset (next steps).

**On the rendered strip** (`mono_units.py`: each glyph rendered alone at 2x
on the light theme; sizes are coverage-weighted extents against the typed `°`,
F and C at the same size; gap is the nearest ink between ring and letter at
half coverage, in CSS px; contact is any 8-connected ink at 15 % coverage
joining ring and letter):

| wght | px | Unit | Letter height (r7) | Letter width r6 → r7 | Ring w × h r6 → r7 | Side / top wall r6 → r7 | Gap px r6 → r7 | Contact r6 / r7 |
| ---: | ---: | --- | ---: | --- | --- | --- | --- | --- |
| 400 | 13 | ℉ | 1.000 | 0.74 → 0.75 | 0.67 × 0.72 → 0.82 × 0.94 | 0.65 / 0.63 → 0.99 / 0.98 | 1.00 → 1.00 | no / no |
| 400 | 13 | ℃ | 1.000 | 0.80 → 0.78 | 0.67 × 0.72 → 0.82 × 0.94 | 0.65 / 0.63 → 0.99 / 0.98 | 0.91 → 1.00 | no / no |
| 400 | 15 | ℉ | 1.000 | 0.73 → 0.70 | 0.67 × 0.74 → 0.80 × 0.96 | 0.60 / 0.63 → 0.98 / 1.03 | 1.00 → 1.50 | no / no |
| 400 | 15 | ℃ | 1.000 | 0.81 → 0.74 | 0.67 × 0.74 → 0.80 × 0.96 | 0.60 / 0.63 → 0.97 / 1.03 | 1.00 → 1.08 | no / no |
| 400 | 17 | ℉ | 1.000 | 0.71 → 0.76 | 0.68 × 0.68 → 0.81 × 0.93 | 0.59 / 0.56 → 0.98 / 1.06 | 1.50 → 1.00 | no / no |
| 400 | 17 | ℃ | 1.000 | 0.77 → 0.74 | 0.68 × 0.68 → 0.81 × 0.93 | 0.59 / 0.56 → 0.98 / 1.06 | 1.00 → 1.08 | no / no |
| 400 | 24 | ℉ | 1.000 | 0.75 → 0.73 | 0.66 × 0.74 → 0.78 × 0.94 | 0.57 / 0.59 → 0.94 / 0.98 | 2.00 → 2.00 | no / no |
| 400 | 24 | ℃ | 1.000 | 0.80 → 0.74 | 0.66 × 0.74 → 0.78 × 0.94 | 0.57 / 0.59 → 0.96 / 0.98 | 1.56 → 2.00 | no / no |
| 700 | 13 | ℉ | 1.000 | 0.66 → 0.67 | 0.65 × 0.72 → 0.82 × 0.98 | 0.58 / 0.61 → 0.97 / 1.07 | 1.00 → 1.00 | no / no |
| 700 | 13 | ℃ | 1.000 | 0.74 → 0.71 | 0.65 × 0.72 → 0.82 × 0.98 | 0.58 / 0.61 → 0.97 / 1.07 | 0.91 → 1.00 | no / no |
| 700 | 15 | ℉ | 1.000 | 0.72 → 0.70 | 0.64 × 0.65 → 0.78 × 0.93 | 0.59 / 0.60 → 0.98 / 1.02 | 1.00 → 1.00 | no / no |
| 700 | 15 | ℃ | 1.000 | 0.77 → 0.71 | 0.64 × 0.65 → 0.78 × 0.93 | 0.59 / 0.60 → 0.98 / 1.02 | 1.00 → 1.00 | no / no |
| 700 | 17 | ℉ | 1.000 | 0.64 → 0.64 | 0.64 × 0.67 → 0.76 × 0.92 | 0.58 / 0.60 → 0.96 / 1.02 | 1.50 → 1.50 | no / no |
| 700 | 17 | ℃ | 1.000 | 0.75 → 0.68 | 0.64 × 0.67 → 0.76 × 0.92 | 0.58 / 0.61 → 0.96 / 1.02 | 1.08 → 1.50 | no / no |
| 700 | 24 | ℉ | 1.000 | 0.68 → 0.67 | 0.65 × 0.69 → 0.73 × 0.93 | 0.55 / 0.56 → 0.97 / 1.00 | 1.50 → 2.00 | no / no |
| 700 | 24 | ℃ | 0.999 | 0.77 → 0.71 | 0.65 × 0.69 → 0.73 × 0.93 | 0.55 / 0.56 → 0.97 / 1.00 | 1.50 → 2.00 | no / no |

- **Letter.** The letter keeps the face's cap height (1.000; 0.999 for the Bold ℃ at 24 px).
- **Ring.** The ring is now 0.92–0.98 of the typed `°`'s height and 0.73–0.82 of its width (r6 0.65–0.74 tall). Its side walls are 0.94–0.99 and its top walls 0.98–1.07 of the `°`'s, against r6's 0.55–0.65. Both are inside the ±10 % asked for.
- **Gap and contact.** The gap is at least 1.00 px at every size and weight on this strip, with no contact at 15 % ink.
- **Cost.** The price is letter width. The Regular ℃'s C is 0.74–0.78 of the face's C (r6 0.77–0.81) and the Bold one 0.68–0.71 (r6 0.74–0.77). ℉ stays within a few hundredths of r6 (0.64–0.76).

`evidence/item1-mono-temperature-units.png` shows `20℉ 20°F  −3℃ −3°C` at
13, 15 and 17 px, 400 and 700, r6 above r7, with the composed `°F` and `°C`
on the same line.

## 2. Serif at text sizes

**Why r6's change did not show.** Three things were checked.

1. *The binary has an opsz axis.* `StrataSerif` has `opsz` 8–60 (avar maps
   user 8 → 8, 12 → 9, 20 → 20) and `wght` 200–900.
2. *The renderer picks the CSS size as opsz.* With
   `font-optical-sizing: auto` (the specimen CSS sets it), the renderer
   resolves opsz to the CSS px size. On the r6 binary, the 9, 11 and 13 px
   rows rendered with `auto` are pixel-identical to the same rows rendered
   with `font-variation-settings: 'opsz' 9`, `11` and `13`, and differ from
   every other opsz tried (8, 9, 11, 13, 18, 20, 26, and `none`, which is
   opsz 20) by 1 470–4 919 changed pixels. The 24 px row differs from both
   opsz 20 and 26, so it too sits at its own size.
3. *The changed outlines are the rendered ones.* 9–13 px resolve to design
   opsz 8.25–9.9, between the opsz 8 (caption) masters r6 changed and the
   opsz 20 masters.

So the cause is in the font, not in the specimen harness. r6's change was too
small to cross a pixel. It touched only the steep thin strokes (v's thin arm
43 → 58 units at opsz 9 / 400: 15 units, 0.27 raster px at 9 px on 2x) and
never the stems. And the caption stems were thinner than drawn: the colour
match (`colour_masters`, which sets each optical size's Regular to a share of
the sans's ink) thinned the caption Regular's stems by 27 units, to 77.5 units
(1.4 raster px at 9 px on 2x). The `i` of "quiet" at 9 px / 400 on light
covered about 1.6 px in total, but only one pixel at half ink or more, which
is the "1 raster px" the review saw.

**The change** (`transforms/serif.py`, opsz 8 masters only):

- `CAPTION_STEM`: after the colour match, every glyph of the caption masters
  gains Thin 5, Regular 16 and Black 16 units of stroke (Black the same units
  as Regular, so the 400 → 600 step keeps most of its size and the 600
  counters lose no more than Regular's). The caption colour match now
  thins by 6.6 / 11.1 / 11.4 units instead of 11.6 / 27.1 / 27.4.
- `HAIR` 8 → 11: the horizontal hairlines (`sturdy_small`) gain 3 more units.
  Thickened in 581 glyphs.
- `THIN_GAIN` Regular 18 → 26, Black 30 → 34: the steep thin strokes
  (`thin_small`) gain more. Thickened in 486 glyphs.
- Short lines keep their direction (`SHORT_LINE`, `SHORT_TURN`). The stroke
  gain moves each point sideways by its own miter, so a line only a few units
  long can turn far. In the caption Black `r`, the 8-unit line inside the
  ball terminal turned from 33° to −12°, the hairline pass left it at 10°,
  and the first r7 build gained a new interpolation finding: a kink at that
  join between the caption Black (900, opsz 8) and display Thin (200, opsz
  60) locations. r6 had the line at 35° and no finding. Now a line under 40
  units with a corner at one end and a smooth point at the other (the only
  kind whose turn can kink a join) that turns more than 15° from its drawn
  direction has its corner end moved sideways back onto that direction, and
  the smooth end's outer handle turned onto the restored line at its own
  length, after the stroke gain and again after the hairline passes. (Moving
  the corner alone left the smooth join itself kinked: the caption Thin `J`
  and caption Regular `r` turned 28° and 26° there, two new outline
  findings.)
  This moves 22 lines
  after the gain and 17 after the hairline passes, all in the caption
  masters (`r`, `r.sups`, `J`, `j`, `f`, `y`, `Eng`, `Ef` and a few others);
  no other master is checked. At the midpoint between those two
  masters the `r` join now turns 4.6° (r6 6.6°, first r7 build 18.3°).
- Advances are unchanged, so text at 9–13 px does not reflow. The text and
  display masters (opsz 20 and 60) are not touched.

**On the render** (`make render`, sheets 05 light and 06 dark, the serif
waterfall "A quiet sky, 0123456789"; effective width is the summed coverage
across the stroke in raster px, median over the middle of the stroke; solid
is the count of pixels at half ink or more; ink is the summed coverage of
the sample line):

| Theme | wght | px | i stem: effective (solid) r6 → r7 | e bar r6 → r7 | y arm r6 → r7 | A leg r6 → r7 | Ink r6 → r7 |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| light | 400 | 9 | 1.57 (1) → 1.83 (2) | 1.56 → 1.66 | 1.36 → 1.74 | 1.23 → 1.59 | 973 → 1078 (+10.8%) |
| light | 400 | 11 | 1.91 (2) → 2.24 (3) | 1.79 → 1.91 | 1.67 → 2.09 | 1.50 → 1.92 | 1390 → 1532 (+10.2%) |
| light | 400 | 13 | 2.30 (2) → 2.61 (3) | 2.07 → 2.18 | 1.92 → 2.34 | 1.69 → 2.10 | 1900 → 2070 (+8.9%) |
| light | 400 | 24 | 4.28 (4) → 4.28 (4) | 2.80 → 2.80 | 2.61 → 2.61 | 2.43 → 2.43 | 5584 → 5583 (-0.0%) |
| light | 400 | 32 | 5.85 (6) → 5.85 (6) | 3.26 → 3.26 | 3.47 → 3.47 | 3.30 → 3.30 | 9584 → 9579 (-0.0%) |
| light | 600 | 9 | 2.55 (3) → 2.91 (3) | 1.58 → 1.68 | 1.47 → 1.77 | 1.74 → 2.10 | 1266 → 1363 (+7.7%) |
| light | 600 | 11 | 3.10 (3) → 3.48 (3) | 1.84 → 1.97 | 1.76 → 2.20 | 2.15 → 2.51 | 1875 → 2011 (+7.3%) |
| light | 600 | 13 | 3.62 (3) → 3.95 (4) | 2.15 → 2.30 | 1.97 → 2.40 | 2.35 → 2.75 | 2560 → 2723 (+6.4%) |
| light | 600 | 24 | 6.46 (7) → 6.46 (7) | 3.00 → 3.00 | 2.48 → 2.48 | 2.84 → 2.84 | 7420 → 7419 (-0.0%) |
| light | 600 | 32 | 8.71 (9) → 8.71 (9) | 3.55 → 3.55 | 3.28 → 3.28 | 3.78 → 3.78 | 12776 → 12772 (-0.0%) |
| dark | 400 | 9 | 1.92 (2) → 2.27 (2) | 1.93 → 2.07 | 1.67 → 2.02 | 1.58 → 1.93 | 1156 → 1258 (+8.8%) |
| dark | 400 | 11 | 2.37 (3) → 2.68 (3) | 2.23 → 2.38 | 1.98 → 2.42 | 1.74 → 2.20 | 1611 → 1748 (+8.5%) |
| dark | 400 | 13 | 2.56 (3) → 2.93 (3) | 2.34 → 2.45 | 2.19 → 2.63 | 2.06 → 2.43 | 2145 → 2320 (+8.2%) |
| dark | 400 | 24 | 4.49 (4) → 4.49 (4) | 2.97 → 2.97 | 2.95 → 2.95 | 2.74 → 2.74 | 6041 → 6041 (-0.0%) |
| dark | 400 | 32 | 5.97 (6) → 5.97 (6) | 3.57 → 3.57 | 3.77 → 3.77 | 3.63 → 3.63 | 10167 → 10163 (-0.0%) |
| dark | 600 | 9 | 2.89 (3) → 2.99 (3) | 1.96 → 2.10 | 1.78 → 2.04 | 1.95 → 2.31 | 1444 → 1540 (+6.6%) |
| dark | 600 | 11 | 3.47 (4) → 3.72 (4) | 2.28 → 2.43 | 2.04 → 2.47 | 2.25 → 2.83 | 2086 → 2225 (+6.6%) |
| dark | 600 | 13 | 4.03 (4) → 4.43 (5) | 2.40 → 2.50 | 2.32 → 2.73 | 2.62 → 3.14 | 2813 → 2983 (+6.0%) |
| dark | 600 | 24 | 6.83 (7) → 6.83 (7) | 3.15 → 3.15 | 2.82 → 2.82 | 3.19 → 3.19 | 7878 → 7878 (-0.0%) |
| dark | 600 | 32 | 8.91 (9) → 8.91 (9) | 3.93 → 3.93 | 3.60 → 3.60 | 4.10 → 4.10 | 13350 → 13346 (-0.0%) |

- **Stems.** At 9 px / 400 the `i` stem goes from 1.57 px, with one pixel at half ink or more, to 1.83 px with two (light), and from 1.92 to 2.27 px (dark). Both themes clear the 1.5 px target.
- **Hairlines.** At 9–13 px the y arm gains 0.26–0.44 px, the e bar 0.10–0.15 px and the A leg 0.35–0.58 px, and the sample line's ink rises 6–11 %.
- **Display sizes.** At 24 and 32 px every stroke measure is the same as r6, and the line's summed ink differs by at most 5 units of coverage (0.05 %).

**Counters at 9 px / 600 on dark** (`serif_counters.py`: "a e s" rendered on
the dark theme at 2x; closed is the count of pixels under half coverage that
are enclosed by ink, such as the a's bowl and the e's eye; white share is the
pixels under half coverage over the ink box):

| Size / wght | a closed, white share | e closed, white share | s closed, white share |
| --- | --- | --- | --- |
| 9 / 600, r6 → r7 | 14 → 14, 0.300 → 0.282 | 6 → 6, 0.355 → 0.336 | 5 → 5, 0.250 → 0.205 |
| 9 / 400, r6 → r7 | 9 → 9, 0.418 → 0.382 | 8 → 8, 0.384 → 0.354 | open, 0.409 → 0.364 |
| 11 / 600, r6 → r7 | 10 → 10, 0.349 → 0.320 | 11 → 11, 0.327 → 0.288 | open, 0.308 → 0.277 |
| 13 / 600, r6 → r7 | 34 → 28, 0.383 → 0.354 | 18 → 18, 0.361 → 0.384 | open, 0.370 → 0.328 |

Every enclosed counter keeps at least one pixel at 0 coverage (full
background). "Open" means the s has no enclosed white at that size; at
9 px / 600 the s's two counters close off into enclosed pockets in r6 and r7
alike, and r7 keeps all 5 of their pixels.

**Display sizes.** The opsz 20 and 60 masters are byte-identical to r6's in
the UFOs (section 4). In the binary their quadratic outlines differ slightly,
because the compatible cubic-to-quadratic conversion runs over all masters
together and the caption masters changed. Bounds do not change; the largest
change in filled area is 0.24% at opsz 20, 0.21% at opsz 24 and 0.45% at
opsz 60; the largest absolute change is 112 units² (`three.sc`, opsz 20). On the render the 24 and 32 px rows measure the same as r6 in stem, bar, arm and leg, on both themes and weights (table above).

`evidence/item2-serif-text-sizes.png` shows the waterfall rows at 9, 11, 13,
24 and 32 px, 400 and 600, light and dark, r6 above r7, cut from the
`make render` sheets, and the counter strip at 9 px / 600 on dark.

## 3. Rounded 3

**What was wrong.** Rounded's 3 was the sans's flat-top 3 under the round
pen. At 48–96 px the flat top bar, the corner and the tight upper turn read
as `ʒ` (ezh).

**The change** (`transforms/rounded.py`). Rounded draws `three` and
`three.pnum` from the sans's round-top 3 (`three.1`, `three.1.pnum`), centred
on the 3's own advance (`DRAWN_FROM`), and then applies the same round pen as
every other Rounded glyph. Both 3s are point-compatible across all nine
masters. The round top makes the upper turn one smooth curve from the top
bowl into the middle join, so the 3 has no concave step left and r6's notch
rule (`merge_notch`) no longer applies to any glyph (`SOFT_NOTCH` is empty).
The sans Regular keeps its flat-top 3. Advances, kerning and `tnum`/`pnum`
stay, so width parity is exact.

`checks/skeleton.py` compares the Rounded 3 with the drawing it is made from
(`DRAWN_FROM`, the same map), so the skeleton check still measures the pen
and nothing else.

Measured on the render (light, 2x, wght 400; gaps are CSS px between the
inks at half coverage):

| Size | Text | Advance: Regular / Rounded r6 / Rounded r7 | Minus–3 gap, Rounded r6 → r7 (Regular) | 3–° gap, Rounded r6 → r7 (Regular) |
| ---: | --- | --- | --- | --- |
| 32 | `−3°` | 53.11 / 53.11 / 53.11 | 6.93 → 6.45 (5.60) | 4.11 → 3.50 (4.03) |
| 32 | `23°` | 54.05 / 54.05 / 54.05 | – | 4.24 → 3.53 (4.11) |
| 32 | `13:30` | 91.41 / 91.41 / 91.41 | – | – |
| 48 | `−3°` | 79.67 / 79.67 / 79.67 | 9.81 → 9.81 (8.51) | 6.46 → 5.52 (6.30) |
| 48 | `23°` | 81.08 / 81.08 / 81.08 | – | 6.46 → 5.52 (6.30) |
| 48 | `13:30` | 137.11 / 137.11 / 137.11 | – | – |
| 96 | `−3°` | 159.33 / 159.33 / 159.33 | 20.31 → 19.50 (17.23) | 13.45 → 11.51 (13.23) |
| 96 | `23°` | 162.14 / 162.14 / 162.14 | – | 13.33 → 11.01 (12.84) |
| 96 | `13:30` | 274.22 / 274.22 / 274.22 | – | – |

**The optional degree gap.** The round top's shoulder sits lower and further
in than the flat bar's corner, so the 3–° gap at 96 px closes by 1.94 px in
`−3°` and 2.32 px in `23°` with no kerning change. That is the "about 2 px"
asked for, so no kerning was added.

`evidence/item3-rounded-three.png` shows `−3°`, `23°` and `13:30` at 32, 48 and
96 px: r6 Regular, r6 Rounded, r7 Regular and r7 Rounded.

## 4. Everything else

Outlines outside the three items are unchanged.

**UFO masters against r6** (every glyph's contours, components and width, plus features and kerning):

| Face | Masters | Glyphs that differ |
| --- | --- | --- |
| Sans | m00–m08 | 0 |
| Rounded | m00–m08 | `three`, `three.pnum` (item 3) |
| Mono | m00–m01 | `uni2103`, `uni2109` (item 1) |
| Serif | m00–m02 (opsz 8) | every drawn glyph (item 2) |
| Serif | m03–m08 (opsz 20 and 60) | 0 |

Features and kerning are the same in every master.

One whole-glyph pass needed a pin to keep that true (`KEEP_DRAWN` in `transforms/serif.py`):

- The tangent-join pass judges a glyph across all masters at once. If restoring a join would add a kink between masters, it leaves the glyph as it was.
- r6 left the `dagger` that way. With r7's caption masters the verdict flipped, and the pass then moved the dagger's handles by 0.4–2.0 units in the text and display masters as well.
- The pin keeps r6's verdict, so the text and display dagger is byte-identical to r6.

**Binary, r6 → r7.** These compare identical in all four faces:

- glyph order;
- cmap;
- advances (hmtx);
- GSUB, GPOS and GDEF;
- fvar, avar and STAT;
- name;
- HVAR.

Left sidebearings change only for Rounded `three` and `three.pnum`. Outlines or variations change in:

| Face | Glyphs with changed outlines or variations |
| --- | --- |
| Sans | 0 |
| Rounded | 2 (`three`, `three.pnum`) |
| Mono | 2 (`uni2103`, `uni2109`) |
| Serif | 392 |

The serif count is every glyph whose opsz 8 masters changed, through gvar. The serif's quadratic outlines are converted compatibly across all masters. So the caption change also moves some quadratic points at the display locations, with these limits:

- no bounds change;
- largest change in filled area 0.24 % at opsz 20, 0.21 % at opsz 24 and 0.45 % at opsz 60;
- largest absolute change 112 units² (`three.sc`, opsz 20).

WOFF2 sizes, r6 → r7:

| Face | Bytes |
| --- | --- |
| Sans | 108 328 → 108 328 |
| Serif | 197 716 → 197 616 |
| Mono | 47 780 → 47 748 |
| Rounded | 74 012 → 73 948 |

## Checks

`make build`, `make gate`, `make render` and `make checks` all exit 0.

**Gate.** Hard failures 0. The quality status is FAIL, from inherited baseline findings with the same counts as r6. Name and reserved-font-name checks pass in every face, and no name record contains Inter, Source or Fira.

| Face | Pass / Warn / Fail / Error, r6 = r7 | Core present | Interpolation glyphs, r6 → r7 |
| --- | --- | ---: | --- |
| Sans | 92 / 4 / 5 / 1 | 258/258 | 0 → 0 |
| Serif | 95 / 5 / 5 / 0 | 258/258 | 3 → 3 |
| Mono | 90 / 6 / 5 / 1 | 258/258 | 0 → 0 |
| Rounded | 98 / 0 / 2 / 1 | 29/29 | 0 → 0 |

**Interpolation.** No new findings:

- The gate's serif findings are r6's: `dagger` (1), `daggerdbl` (2) and `f.ligalong` (1), with the same values.
- `checks/vfkinks.py` lists the same five serif ligatures as r6 (`f_f`, `f_f_i`, `f_f_j`, `f_f_l`, `f_f_t`, 200/8 → 900/8), and Rounded is clear.
- Over 45 instances of the built serif (wght 200–900 × opsz 8–60), the largest turn at a join that is smooth at the default does not grow for `r`, `J`, `y` or `f_j`. `r.sups` peaks at 31.5° (r6 48.4°).

**Line contact.** The headline-collision audit of sheet 05 is clear on light, dark and glass, with 0 contact components. The render made 38 PNGs, and the blind byte scan passes.

**Review checks** (`make checks`): PASS.

| String | Regular | Rounded | Difference |
| --- | ---: | ---: | ---: |
| 104°F | 269.578 px | 269.578 px | +0.000 % |
| 72° | 149.109 px | 149.109 px | +0.000 % |
| 18:30 | 261.891 px | 261.891 px | +0.000 % |
| −3° | 144.094 px | 144.094 px | +0.000 % |

The default cmap and shaped figures are tabular in every face: Sans PASS at 21 locations, Serif INFO at 30 (as r6), Mono PASS at 5 and Rounded PASS at 15.

**Rounded widths** (`checks/widths.py --all`): the largest difference over 10 locations × 16 strings is 0.00 %.

**Tabular default** (`checks/figcheck.py`): PASS.

| Face | Locations | Default advance | All ten equal |
| --- | ---: | ---: | --- |
| Sans | 21 | 1332 | yes |
| Serif | 30 | 579 | yes |
| Mono | 5 | 1217 | yes |
| Rounded | 15 | 1332 | yes |

**Confusables** (`checks/figcheck.py`, xor at wght 400; fail under 0.20): PASS.

| Face | px | 1/l | 1/I | l/I | I/\| | l/\| | 1/\| | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.680 | 0.379 | 0.545 | 0.496 | 0.679 | 0.619 | 0.652 | 0.499 | 0.642 |
| Sans | 11 | 0.713 | 0.376 | 0.577 | 0.550 | 0.726 | 0.649 | 0.658 | 0.467 | 0.643 |
| Sans | 13 | 0.735 | 0.407 | 0.595 | 0.541 | 0.738 | 0.655 | 0.519 | 0.520 | 0.670 |
| Serif | 9 | 0.332 | 0.311 | 0.217 | 0.574 | 0.476 | 0.589 | 0.522 | 0.718 | 0.662 |
| Serif | 11 | 0.293 | 0.270 | 0.278 | 0.583 | 0.445 | 0.577 | 0.531 | 0.683 | 0.650 |
| Serif | 13 | 0.346 | 0.275 | 0.244 | 0.579 | 0.482 | 0.603 | 0.624 | 0.761 | 0.664 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.520 | 0.467 | 0.613 | 0.817 | 0.357 | 0.639 |
| Mono | 11 | 0.436 | 0.373 | 0.439 | 0.564 | 0.436 | 0.640 | 0.909 | 0.386 | 0.624 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.554 | 0.477 | 0.651 | 0.871 | 0.379 | 0.673 |
| Rounded | 9 | 0.680 | 0.369 | 0.548 | 0.485 | 0.676 | 0.613 | 0.654 | 0.500 | 0.632 |
| Rounded | 11 | 0.714 | 0.380 | 0.576 | 0.540 | 0.721 | 0.636 | 0.661 | 0.466 | 0.628 |
| Rounded | 13 | 0.735 | 0.411 | 0.592 | 0.530 | 0.739 | 0.653 | 0.524 | 0.517 | 0.645 |

The heavier serif caption stems bring the serif's stem letters closer together: l/I goes from 0.243 to 0.217 at 9 px, 0.296 to 0.278 at 11 px and 0.265 to 0.244 at 13 px (r6 → r7), and 1/l and 1/I drop by 0.01–0.02. Sans and Mono match r6. In Rounded only 3/7 moves, with the new 3: 0.657 → 0.632 at 9 px, 0.659 → 0.628 at 11 px and 0.691 → 0.645 at 13 px, still far above the line. The closest serif pair, l/I at 9 px, is now 0.017 above the fail line.

**Skeleton** (`checks/skeleton.py`, opsz 14; fail at 4.0 thousandths of an em² or more): PASS, both for the core set and with `--all`.

| Glyph | Region 400 | Region 900 | Overlap 400 | Overlap 900 | IoU 400 | IoU 900 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| G (largest at 400) | 3.68 | 1.80 | 0.979 | 0.991 | 0.955 | 0.974 |
| M (largest at 900) | 0.34 | 3.37 | 0.995 | 0.967 | 0.977 | 0.940 |
| three | 0.09 | 0.52 | 0.997 | 0.993 | 0.980 | 0.978 |
| three.pnum | 0.20 | 0.72 | 0.995 | 0.990 | 0.906 | 0.952 |

Over 135 glyphs the mean region is 0.40 at 400, and the overlap minimum is 0.953.

**Outline hygiene** (`checks/outlines.py`): 0 gated outliers, PASS. Point and kink outliers in the core set:

| Face | Core outliers | Core glyphs with only new short segments (reported) |
| --- | ---: | ---: |
| Sans | 0 | 1 |
| Rounded | 0 | 1 |
| Serif | 0 | 16 |
| Mono | 0 | 0 |

- The serif's short segments are bracket pieces that the stroke gain shortens.
- Default-instance TrueType point growth is reported, not gated, and is unchanged from r6: Sans 2 core glyphs (`zero.pnum`, `zero.pnum.slash`), Serif 0, Mono 13.

## Evidence

Each image puts r6 above r7 and draws its numbered callouts on the r7 rows. The numbers are explained in a legend at the foot of each image and below.

**`evidence/item1-mono-temperature-units.png`** shows `20℉ 20°F  −3℃ −3°C` in mono at 13, 15 and 17 px, 400 and 700, on the light theme at 2x, scaled with nearest neighbour.

1. The ring is the face's own degree sign, 0.93 tall with 0.97 of its walls. It sits beside the typed `°` of the composed `20°F` (r6: a drawn ring, about 0.7 of the `°` with half its walls).
2. The letter is the face's F or C at full cap height, condensed and emboldened back to its stems, as in r6.
3. The ring–letter gap is drawn at 1.20 px at 13 px and renders at 1 px or more at all 16 sub-pixel positions, with no contact.
4. At Bold the ring narrows to 0.77 of the degree sign's width, and the letter may pass the cell's right edge by 0.10 cell, so the Bold C keeps 0.70 of the face's C.
5. The ring starts on the cell's left edge (Light) or 0.03 cell inside it (Bold). That keeps it at least 1 px from the `0` before it, as in r6.

**`evidence/item2-serif-text-sizes.png`** shows the "A quiet sky, 0123456789" waterfall rows, cut from the `make render` sheets 05 (light) and 06 (dark): 9, 11 and 13 px scaled ×4, and 24 and 32 px scaled ×2, at 400 and 600. A strip of `a e s  sea ease` at 9 px / 600 on dark (×6) follows.

1. The 9 px `i` stem, from 1.57 px (1 solid pixel) to 1.83 px (2) on light.
2. Hairlines at 11–13 px: the y arm and e bar gain 0.10–0.44 px.
3. At 24 and 32 px the rows measure the same as r6.
4. The a, e and s counters at 9 px / 600 on dark keep 14, 6 and 5 enclosed pixels.

**`evidence/item3-rounded-three.png`** shows `−3°`, `23°` and `13:30` at 32, 48 and 96 px in r6 Regular, r6 Rounded, r7 Regular and r7 Rounded. It ends with the 3 at 200 px (400 and 900) and an overlay of r6 Rounded (red) on r7 Rounded (blue).

1. The round top, drawn from the sans round-top 3.
2. The upper turn, one smooth curve from the top bowl into the middle join.
3. The minus–3 gap, with the kerning unchanged.
4. The 3–° gap, about 2 px closer at 96 px.

The overlay shows the flat bar and corner giving way to a round shoulder and the middle join moving in, while the lower bowl keeps its place.

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
  - Rounded may take a glyph's drawing from a sans alternate
    (`DRAWN_FROM`: `three` from `three.1`), centred on the default glyph's
    advance. The alternate must be point-compatible in every sans master,
    and `checks/skeleton.py` and `checks/outlines.py` must compare against
    the same drawing (`DRAWN_FROM`, `com.strata.source`).
  - `checks/skeleton.py` must pass at opsz 14: the largest displaced region
    must stay under 4.0 thousandths of an em² at 400 and 900.
- Rounded's display masters (opsz 32) may also carry the hero-bowl pass
  (`HERO` set only; handles toward circular tension; extremes, tangents and
  advances kept; accepted per glyph only if it adds no kink or roughness).
  The display skeleton is reported, not gated.
- A short concave step in a Rounded corner is closed to one join in every
  master (`merge_notch`) before it is filleted, with its fillet reach capped
  (`NOTCH_CUT`). Since r7 no glyph needs it (`SOFT_NOTCH` is empty), but the
  rule stands for any new drawing with a step.
- Rounded widths equal the sans widths (`checks/widths.py`, under 1%), and
  tabular figures stay the default.
- Figure punctuation is fitted by pair kerning and figure-context glyphs,
  never by changing a figure's advance.
- The minus sits from a figure's ink at the median ink gap between tabular
  figures, per master. The nearest-ink limit is a floor, never the target.
- A mono temperature unit keeps one cell's advance and gives up width, never
  height.
  - The letter is the face's own C or F at cap height, condensed in x and
    emboldened back to its stem.
  - The ring is the face's own degree sign, at least 0.90 of its height,
    with walls within ±10% of its walls.
  - Ring and letter keep at least 1 px apart at 13 px on the render at every
    sub-pixel position (`browser_gap.py`, a work-folder script), not only in the outlines: the
    renderer darkens edges by about half a raster pixel, so the outline gap
    must be larger (1.20 px). No contact at any weight.
  - The ring keeps at least 1 px from a `0` in the previous cell at 13 px on
    the render, at every position and weight (r6 kept 1.00 px; a typed `°`
    keeps about 2 px). So the ring does not hang over the left sidebearing.
  - The letter may pass the right edge into the space after it (at most 0.10
    cell). The Bold letter keeps at least 0.65 of the face's F and 0.70 of
    its C across, so a Bold ℃ never reads as a parenthesis.
- Serif caption strength changes only the opsz 8 masters.
  - A caption change counts only if it shows on the 2x render: the 9 px
    serif `i` stem must keep at least 2 pixels at half ink or more at 400 on
    both themes (`CAPTION_STEM` after the colour match).
  - A thin-stroke gain never moves an edge that faces less than 1.5 stems of
    white, so counters keep their room.
  - A caption pass must not turn a short line with one smooth end by more
    than 15° from its drawing (`SHORT_TURN`). When the line is turned back,
    the smooth end's handle turns with it, so the join stays tangent. The
    interpolation check on the built serif may list nothing that r6's does
    not.
  - The a, e and s counters must stay open at 9 px / 600 on dark.
  - The renderer resolves opsz to the CSS px size with
    `font-optical-sizing: auto`, so 9–13 px show the caption masters.
  - A whole-glyph pass whose verdict depends on the caption masters must
    leave the text and display masters as r6 had them. Where a caption
    change flips such a verdict, pin r6's verdict (`KEEP_DRAWN`) and confirm
    with a per-master diff that the opsz 20 and 60 masters are unchanged.
- Every transform that moves points records the upstream drawing it starts
  from (`com.strata.source`). `checks/outlines.py` must report 0 gated
  outliers, and the gated set includes the case, tabular and figure-context
  forms.
- A pass that moves edges keeps smooth line-curve joins tangent. A pass that
  lengthens short pieces is kept only where the filled outline changes by
  less than 1 unit².
- A mono ligature that spans cells must read as one sign, with its own
  strokes (`!==`).
- Any measurement quoted here is taken from the built binary or its render,
  never from a master or a note.

## Next steps

1. **Mono unit followers.** A dash or slash set directly after a Bold unit touches it (`℉–` −0.05 px, `℃/` 0.11 px in the outlines). Options, in order of preference:
   - Set ranges with one unit (`20–25℉`). This is a copy rule and needs no outline change.
   - Shorten the unit F's middle arm by about 70 units at Bold (0.45 px at 13 px). This clears the dash without narrowing the C.
   - Cap the Bold overhang at 0.05 cell and accept a Bold C of about 0.66.

   Measure any of these on the render with `browser_gap.py`, extended to `℉–`, `℃/` and `℉)`.
2. **Mono ℃ width.** The Bold C is 0.70 of the face's C. If reviewers still read it as `(` at 13 px, the next lever is ring width (0.77 now) before the gap or the walls.
3. **Serif 15–20 px.** The caption gain fades from opsz 8 to opsz 20. Check that 15–17 px text (opsz about 11.5–14) gained enough, since only 9, 11 and 13 px were measured here.
4. **Serif `r.sups`.** Its ball-terminal join turns up to 31.5° across instances (r6 48.4°). This is inherited, smaller than r6's, and not flagged by the gate, but it is the largest remaining smooth-join turn found.
5. **Serif `f_f` ligatures.** The five ligature kinks between 200/8 and 900/8 are inherited from r6 and should be fixed in their own round.
6. **`KEEP_DRAWN`.** It pins r6's tangent-join verdict for the dagger only. If the caption masters change again, re-run the per-master diff and add any glyph whose text or display masters move.
7. **Serif l/I at 9 px.** The caption stems took the l/I xor from 0.243 to 0.217, 0.017 above the 0.20 fail line. Any further caption-stem gain should be paired with a clearer l or I difference at opsz 8 (for example the I's serifs, or the l's tail), and the pair re-measured.
8. **Specimen harness.** Nothing in `scripts/` needs to change for item 2. The renderer resolves opsz to the CSS size, and the cause was in the font.

## Rebuild

From the repository root:

    .venv/bin/python -I candidates/r7-type/transforms/apply.py    # sans rounded serif mono, in that order
    .venv/bin/python -I candidates/r7-type/checks/outlines.py r7-type
    make build  CAND=r7-type SUBSET=core ICONS_DIR=<icon folder>
    make gate   CAND=r7-type ICONS_DIR=<icon folder>
    make render CAND=r7-type OUT=<render folder> MAP=<map file> REFS=0 ICONS_DIR=<icon folder>
    make checks CAND=r7-type ICONS_DIR=<icon folder>
    .venv/bin/python -I candidates/r7-type/checks/figcheck.py build/r7-type
    .venv/bin/python -I candidates/r7-type/checks/skeleton.py build/r7-type
    .venv/bin/python -I candidates/r7-type/checks/widths.py build/r7-type --all
    .venv/bin/python -I candidates/r7-type/checks/vfkinks.py build/r7-type
