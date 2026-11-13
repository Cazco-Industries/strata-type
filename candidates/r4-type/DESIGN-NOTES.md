# r4-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r3-type, and its decisions hold unless a section below
changes them: the shared line metrics, the tailed l, tabular figures by
default with `pnum` proportional, Rounded as the sans plus a round pen over
full Basic Latin, minus vs hyphen and separated `++` in the mono, the caption
masters. Before/after images for each item are in `evidence/` (before =
r3-type, after = r4-type, numbered callouts explained under each image).

The round was started twice before and stopped partway. Its partial work
(the signature module, the Rounded pen per weight, the mono unit glyphs, the
display spacing and 1, the serif small-size and 0 changes, the 3/7 check, the
Rounded display masters and `zero`) was diffed against r3-type and kept: it
was sound and built cleanly. On top of it this round
fixed the landing diagonal where a stem meets a short upright (the 7 in the
mono and serif swelled under the bar), enlarged the Rounded Regular pen,
rebuilt the mono ℉/℃ proportions, enlarged the sans degree ring, cut the
serif display extenders, widened the serif 0 further, added a smaller-pen
fallback to Rounded, and made Rounded's kink test match the gate's (which
cleared a kink in the Rounded g). Nothing was reset from r3-type.

## Summary against the review

| Priority | Item | State |
| --- | --- | --- |
| 1 | Identity: owned details across sans, serif, mono; display 2/7 | Done: the landing diagonal (2 and 7 bow onto the baseline, in all three faces) and the level cut (the serif's ball terminals end flat and level, as sans and mono strokes do) |
| 2 | Rounded plainly round at 24 px Regular; softer 7/3 turns | Done: concentric pen, Regular outer radius 1.70 stems (r3 0.60), joins 0.70 (r3 0.20); 7 and 3 joins twice that. Skeleton check PASS (3.68 / 3.37, limit 4.0) |
| 3 | Mono ℉/℃: larger open ring, less compressed letter; serif ring = ° | Done: ring 0.375 of the cell (r3 0.29), counter about 0.70 of the mono °'s (r3 0.50); letters at 0.84 of their height, as wide for their height as the face's own F and C in the Light (0.92-0.93 in the Bold; r3 0.81-0.82). Serif ℉/℃ are the serif ° plus F/C |
| 4 | Display spacing via opsz; tabular 1 hole | Done: display masters −18 units a side (figures −10); the tabular 1 spans 0.92-0.94 of its cell (r3 0.76); tabular stays default |
| 5 | Serif small sizes: hairlines, crossbars, 13 px spacing | Done: opsz 8 masters gain 8 units on each inner horizontal edge and close 8 units a side; 9 px e crossbar peak 0.555 → 0.714 |
| 6 | Watch items a-f | (a) 3/7 in the check, 0.62-0.69, flat-top 3 kept; (b) cause reported, gap 3.9 → 4.6 px; (c) ° 0.385 → 0.44 of the figure height; (d) Rounded = sans ink at 96 px; (e) serif 0 wider, mono g link opened; (f) `zero` in sans and Rounded, plain 0 default |

## 1. Identity: the landing diagonal and the level cut

Two details, each drawn by one function in `transforms/signature.py` and
applied to all three faces, planned once on a reference master and checked
for interpolation kinks.

**The landing diagonal.** A long straight diagonal running from the top right
to the bottom left (the 2's spine, the 7's stem; at least 0.30 of the glyph's
height, 30-82° from the level) becomes one cubic. Its top handle lies on the
old line, so the 2's spine still leaves the bowl smoothly; its foot handle
turns `LAND` degrees toward the vertical, 12° in the text and caption masters
and 24° in the display masters. The stroke leaves the top as before and lands
on the baseline steeper, bowed toward the upper left. That is the gesture the
serif's 7 had upstream, now the family's: in the build it is on the sans 2
and 7 (and their `pnum`, superior and denominator forms), the serif 7 (lining,
cap, small-cap and superior forms) and superior 2 (the full-size serif 2 is
curved upstream and is left), and the mono 7 (with its denominator and
tabular old-style forms). The display masters bow twice as far, so the 2 and
7 at 40-96 px are the family's own, while at 9-13 px the bow is under a pixel
and the skeleton reads as before.

Where the top of the diagonal meets a short straight line at a shallow turn
(the mono's and the serif's 7, whose stem meets a short upright at the bar's
end with a 23° turn), the top handle also turns away from that line until the
join turns by at least `TOP_CORNER` (32°). Without this, the tangent pass
read the join as a near-tangent kink and straightened it, which swelled the
stem under the bar (the inherited build's mono 7, and an S-bend in the
serif's 7 that read bold at 13 px).

**The level cut.** Sans and mono strokes end in level cuts. The serif's ball
terminals now take the same cut: the ball's two side points move to the
ball's extreme and the end becomes a straight level line, so a ball becomes a
short wedge as wide as the ball was, with a flat end on the level. 41
glyphs take it: a c f j r y and their superior forms, ae, aogonek, the cent
sign, the script g, dotless j, the f ligatures and long s, the balls of 2 3 5
(lining, cap, small-cap and superior forms, and the old-style 2), eng and
Eng, and J with its small-cap and superior forms. The serif keeps its
bracketed serifs and contrast; the ends of its strokes now follow the sans's
logic.

Evidence: `evidence/1-identity.png` (150 px detail, 72, 24 and 13 px for each
face, before and after).

## 2. Rounded at 24 px Regular

r3's pen was 0.60 stems outside and 0.20 inside at every weight. At Regular
that made a 1.3 px outer radius at 24 px on a 2.2 px stroke, and the inner
fillet barely moved, so corners thinned and read as softened, not round.

This round's pen is concentric for Thin and Regular: outer radius = inner
radius + one stem, so a stroke keeps its width round a corner. Black keeps
r3's pen: its corners already read round and its skeleton check had the
least room. Radii (`rounded.R_CONVEX`, `R_CONCAVE`, `MAX_CUT`, in each
master's own H stem; `TERMINAL` 1.60 stems, under which a stroke end becomes
a semicircle, as in r3):

| Master | opsz / wght | H stem | Outer radius | Join radius | Largest cut | 7 and 3 joins |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| m00 | 14 / 100 | 46 | 83 (0.97 px) | 37 (0.43 px) | 87 | 74 (0.86 px) |
| m01 | 32 / 100 | 46 | 83 | 37 | 87 | 74 |
| m02 | 14 / 400 | 190 | 323 (3.79 px) | 133 (1.56 px) | 342 | 266 (3.12 px) |
| m03 | 32 / 400 | 169 | 287 (3.37 px) | 118 (1.39 px) | 304 | 237 |
| m04 | 14 / 900 | 404 | 242 (2.84 px) | 81 (0.95 px) | 364 | 162 |
| m05 | 32 / 900 | 364 | 218 | 73 | 328 | 146 |
| m06 | 8 / 100 | 58 | 104 | 46 | 110 | 93 |
| m07 | 8 / 400 | 234 | 398 | 164 | 421 | 328 |
| m08 | 8 / 900 | 493 | 296 | 99 | 444 | 197 |

Units of the 2048 em; px at 24 px in brackets. In stems: Thin
1.80 / 0.80 / 1.90, Regular 1.70 / 0.70 / 1.80, Black 0.60 / 0.20 / 0.90
(outer / join / largest cut). r3's Regular was 0.60 / 0.20, a 114-unit
(1.34 px) outer radius.

The 7's elbow and the flat-top 3's joins (`SOFT_TURNS`) take `SOFT_JOIN` = 2
times the join radius: 1.40 stems in the Regular, so the interior turns of
the 7 and 3 read soft at text sizes. Every master, display included, is now
rounded from the sans master of the same name (r3 reused the text outlines
in the display masters), so Rounded's ink and spacing follow the sans
drawings at display sizes.

A glyph whose fillets would kink at every curve-cut share with the full pen
takes the first smaller pen in `PEN_STEPS` (0.85, 0.7, 0.55 of every radius)
that clears. In the build only the e needs it (0.55: the e's crossbar joins
kinked in the display Thin at the full pen). The kink test that picks the
pen and the fillet joins runs at an em of 1000 units (`rounded.KINK_UPEM`),
as the gate's font checker does on the built font; at the font's own 2048 a
g passed here and then showed one kink (Black against the caption Thin) in
the built font. `checks/vfkinks.py` reruns the checker's test, in its
location order, on the built fonts.

Measured (Rounded against the sans at 24 px, wght 400, same origin, opsz 14
so both builds compare the same masters; px² of ink the pen removes):

| Measure | r3 | r4 |
| --- | ---: | ---: |
| Ink removed from E F L T H N 7 3 4 1 (opsz 14) | 21.1 px² (2.8% of the ink) | 32.2 px² (4.2%) |
| Ink removed from the E alone (opsz 14) | 2.27 px² | 7.73 px² |
| Ink removed from E F L T H N 7 3 4 1 at the browser's opsz for 24 px | — | 29.2 px² |

The stems' ends of H, N, T, 1 and 4 were already full semicircles in r3 and
are unchanged; the gain is on corners and joins. The E loses over three
times r3's ink at its corners, and in the 24 px row the corners of E, F, L
and the 7's elbow read as round, not as softened.

Skeleton check (largest displaced region beyond 0.012 em, limit 4.0
thousandths of an em²): largest 3.68 at 400 (G) and 3.37 at 900 (M), against
r3's 0.49 and 3.37; mean 0.40 over 132 glyphs; PASS. The glyphs nearest the
limit:

| Glyph | Region 400 | Region 900 | Overlap 400 | Overlap 900 |
| --- | ---: | ---: | ---: | ---: |
| G | 3.68 | 1.80 | 0.979 | 0.991 |
| ℉ | 3.56 | 1.60 | 0.978 | 0.982 |
| B | 3.51 | 1.60 | 0.965 | 0.991 |
| E | 3.51 | 1.60 | 0.953 | 0.978 |
| L | 3.51 | 1.60 | 0.962 | 0.975 |
| F | 3.43 | 1.51 | 0.969 | 0.976 |
| M | 0.34 | 3.37 | 0.995 | 0.967 |
| P | 3.36 | 1.51 | 0.977 | 0.988 |
| R | 3.36 | 1.65 | 0.979 | 0.984 |

Evidence: `evidence/2-rounded.png` (24 px rows, 24 px at 5×, 120 px).

## 3. Mono ℉ and ℃

One mono cell (1217 units) cannot hold the mono's own degree sign and a
full-size letter. r3 filled the cell with a small ring (counter half the
degree sign's) and a full-height letter narrowed to fit, ring and letter
touching the cell's edges, which read as cramped.

Now (`mono.TEMP_*`): the ring is 0.375 of the cell at every weight, with a
wall of min(0.72 stem, 0.20 ring diameter), its top on the figures' top. The
letter is set at 0.84 of its height and narrowed only where the cell runs
out, with its stems held at the font's weight. Ring and letter are 0.025 of
the cell apart, and the pair is centred with at least 0.025 of the cell each
side.

| Measure | r3 | r4 |
| --- | --- | --- |
| ℉ ring counter, Light (units) | 195 × 208 | 274 × 288 |
| ℉ counter over the mono °'s counter (386 × 416), Light | 0.51 × 0.50 | 0.71 × 0.69 |
| ℉ counter at 15 px, Light | 1.50 × 1.62 px | 2.12 × 2.25 px (° 2.88 × 3.25) |
| ℉ counter at 15 px, Bold | 1.62 × 1.75 px | 2.12 × 2.25 px (° 2.38 × 2.62) |
| F, C width per height against the plain letter, Light | 0.97, 0.95 | 1.02, 0.99 |
| F, C width per height against the plain letter, Bold | 0.82, 0.81 | 0.93, 0.92 |

The letter is now as wide for its height as the face's own F and C in the
Light, and within 8% in the Bold, where the cell runs out first.

Serif ℉ and ℃ are the serif `°` plus F or C as components (unchanged from
r3), so the ring is the serif's own `°`: at 15 px the counters of °, ℉ and ℃
measure the same 3.25 × 2.88 px.

Evidence: `evidence/3-temperature-units.png` (13, 15, 17 px at 4×, 96 px, the
serif at 64 px).

## 4. Display spacing and the tabular 1

The sans display masters (opsz 32) now track letters −18 units a side (r3
−6) and figures and the math signs set on them −10 a side (`FIG_TRACK`, r3
0: figures kept their text room), with the figure separators (period, comma,
colon) keeping their text room. The optical size axis carries it, so 40-72 px
settings close up with no CSS tracking while text sizes keep their spacing.
Every figure moves by the same amount, so the tabular cell stays one width.

The footed tabular 1 takes a flag of 0.30 of the figure height (r3 0.12) and
a foot 1.34 times as wide (r3 1.10), so its ink spans most of its cell and the
hole beside it closes. The advance is unchanged (all ten default figures are
one width at every location; `checks/figcheck.py` PASS).

| Measure (sans, wght 400) | r3 | r4 |
| --- | --- | --- |
| Tabular 1 ink over its cell, opsz 14 | 0.756 | 0.922 |
| Tabular 1 ink over its cell, opsz 32 | 0.761 | 0.941 |
| Ink area of 1 over 0 at 72 px | 0.708 | 0.779 |
| "104°F" at 72 px: gap 1 → 0 | 9.2 px | 4.7 px |
| "12 mph" at 72 px: gap 1 → 2 | 11.2 px | 6.6 px |
| "30.16" at 72 px: gaps . → 1, 1 → 6 | 9.2, 10.8 px | 5.0, 6.3 px |
| "104°F" ink width at 72 px | 199.4 px | 203.0 px |

The 104°F string is 2% wider in ink because the 1's foot and flag now fill
the cell the tighter display spacing gives back; the gaps beside the 1 are
about half of r3's.

Evidence: `evidence/4-display.png`.

## 5. Serif at small sizes

The opsz 8 masters (used up to about 13 px) gain `HAIR` = 8 units on every
inner horizontal edge (crossbars, the insides of bowl tops and bottoms, serif
tops and undersides, arms), so hairlines and crossbars gain 16 units of
thickness, while edges on the font's zones and at each glyph's own top and
bottom stay put (heights, overshoots and the baseline do not move). Their
sidebearings close by `TIGHT_8` = 8 units a side.

| Measure (serif, wght 400, opsz = size) | r3 | r4 |
| --- | --- | --- |
| e crossbar at 9 px: peak coverage, ink thickness | 0.555, 0.81 px | 0.714, 1.02 px |
| e crossbar at 11 px: peak coverage, ink thickness | 0.582, 0.80 px | 0.665, 0.94 px |
| Test sentence ink width at 13 px | 285.7 px | 280.0 px (−2.0%) |

Peak coverage is the darkest pixel of the crossbar in the e's centre column
(three pixels wide, averaged over four sub-pixel positions; 1.0 = solid ink);
thickness is that column's coverage summed across the crossbar band.

Evidence: `evidence/5-serif-small.png`.

## 6. Watch items

**(a) 3 against 7.** `checks/figcheck.py` now checks `3 7` with the other
pairs at 9, 11 and 13 px (pixel xor, default features, threshold 0.20). The
flat-top 3 clears it in every face (lowest 0.619, the sans at 9 px), so it
stays. Table in "Gate and checks".

**(b) Headline clearance.** The cause is in the serif's vertical extents.
With the harness CSS fixed, one headline baseline sits 54.24 px below the
last (48 px × line-height 1.13) whatever the font's ascent and descent
lines, so the gap between lines is that pitch less the tallest ascender
above the baseline and the deepest descender below it. At 48 px (opsz 48,
wght 400) r3's b, h and l reach 37.92 px up and its f 38.45 px; its q
reaches 11.90 px down and its y 12.1 px. A q's foot and an f below it kept
54.24 − 11.90 − 38.45 = 3.89 px, about 3 px once antialiased.

This round the display master (opsz 60) cuts descenders by 0.14 of their
depth (0.10 in the text masters) and ascenders by 30 units (20 in text). A
48 px headline lies 0.7 of the way from the text to the display master: its
ascenders reach 37.58 px (f 38.11), its descenders 11.57 px (y 11.71), and
the q-to-f gap is 4.56 px. The harness CSS is unchanged. The cut is smaller
than r2's 0.23, whose 5.6 px gap read as loose.

**(c) Degree sign size.** The sans ring diameter starts at 596 units before
its weight term (r3 520). At 400 and 16 px the ring is 0.439 of the figure
height (r3 0.385), 654 units or 5.11 px across (r3 574 units, 4.48 px), its
top 14 units above the figures' top as before; Rounded's ring is the sans's.

**(d) Rounded against the sans at 96 px.** Rounded now rounds each display
master from the sans display master of the same name, so its ink follows the
sans: at 96 px "80%" is 189.09 px of ink in both (r3: Rounded 193.17
against the sans's 191.06), and the gap from ° to F in "104°F" is 11.9 px in
both (r3: 13.5 against 13.0).

**(e) Serif 0 and mono g.** The serif's lining 0 widens by 0.10 of its ink
inside the same tabular cell (`serif.ZERO_WIDE`; r3 0): ink width per unit
of height at 72 px is 0.662 (r3 0.602; the sans 0 is 0.723, the mono 0.633),
so the serif 0 no longer reads as a narrow ellipse beside the sans. The mono
g's link (`mono.G_LINK`) is thinned: in the centre column the link is 93
units of ink (r3 122) and the white above it 219 units (r3 190), in the
Light.

**(f) `zero`.** The sans already had a slashed zero under `zero`; Rounded now
carries it too (`zero.slash`, `zero.pnum.slash`; also kept under `tnum` and
`pnum`). With default features both faces shape the plain `zero`; with
`zero` on they shape `zero.slash` (and `zero.pnum.slash` with `pnum`), same
advance.

Evidence: `evidence/6-watch-items.png`.

## Gate and checks

`make gate`: hard failures 0; names PASS in every face (no reserved name in
any name record); no missing required glyphs (core 258/258 in the sans,
serif and mono, 29/29 in Rounded); icons PASS. The quality status is FAIL
as in r3: the same inherited checker FAILs and ERRORs, which only
`--strict` rejects.

| Face | Build | Pass | Warn | Fail | Error | Interpolation check | WOFF2 bytes |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| Sans | r3-type | 92 | 4 | 5 | 1 | none | 107,932 |
| Sans | r4-type | 92 | 4 | 5 | 1 | none | 108,328 |
| Serif | r3-type | 95 | 5 | 5 | 0 | 4 kinks (dagger, daggerdbl ×2, f.ligalong) | 196,676 |
| Serif | r4-type | 95 | 5 | 5 | 0 | 3 kinks (dagger, daggerdbl, f.ligalong) | 197,416 |
| Mono | r3-type | 90 | 6 | 5 | 1 | none | 47,732 |
| Mono | r4-type | 90 | 6 | 5 | 1 | none | 47,684 |
| Rounded | r3-type | 98 | 0 | 2 | 1 | none | 64,944 |
| Rounded | r4-type | 98 | 0 | 2 | 1 | none | 72,648 |

Rounded's WOFF2 grows by 7.7 KB, mostly because every master is now rounded
from its own sans master (r3's display masters reused the text outlines).

Checker interpolation test on the built fonts (`checks/vfkinks.py`, same
test and location order): sans, mono and Rounded 0; serif 5, one kink in
each ff ligature (ff, ffi, ffj, ffl, fft) between 200 and 900 at opsz 8.
r3 had the same five and an underweight μ (6).

`make render` (38 sheets): the headline line-contact report is clear on the
light, dark and glass surfaces (0 contact regions each).

`make checks`: PASS. Rounded ink width against the sans Regular at 96 px is
+0.000% for "104°F", "72°", "18:30" and "−3°" (limit 1%). Default shaped
figures are tabular at every named instance and axis corner (sans, mono and
Rounded PASS; serif INFO, as in r3).

Confusable check (`checks/figcheck.py`, pixel xor, default features, wght
400; PASS, every pair at or over 0.20):

| Face | px | 1/l | 1/I | l/I | rn/m | 0/O | 3/7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | 0.701 | 0.525 | 0.530 | 0.652 | 0.499 | 0.619 |
| Sans | 11 | 0.732 | 0.534 | 0.580 | 0.658 | 0.467 | 0.626 |
| Sans | 13 | 0.754 | 0.566 | 0.608 | 0.519 | 0.520 | 0.654 |
| Serif | 9 | 0.354 | 0.323 | 0.243 | 0.530 | 0.593 | 0.664 |
| Serif | 11 | 0.305 | 0.270 | 0.301 | 0.557 | 0.627 | 0.642 |
| Serif | 13 | 0.370 | 0.291 | 0.270 | 0.646 | 0.654 | 0.689 |
| Mono | 9 | 0.468 | 0.382 | 0.366 | 0.817 | 0.357 | 0.655 |
| Mono | 11 | 0.436 | 0.373 | 0.439 | 0.909 | 0.386 | 0.643 |
| Mono | 13 | 0.511 | 0.374 | 0.453 | 0.871 | 0.379 | 0.679 |
| Rounded | 9 | 0.702 | 0.531 | 0.544 | 0.654 | 0.499 | 0.629 |
| Rounded | 11 | 0.734 | 0.539 | 0.593 | 0.661 | 0.467 | 0.650 |
| Rounded | 13 | 0.753 | 0.570 | 0.618 | 0.524 | 0.520 | 0.674 |

Figure-default check: PASS in every face (ten default figures one width at
21 sans, 30 serif, 5 mono and 15 Rounded locations; `tnum` = default).

Skeleton check: PASS, largest 3.68 (400) and 3.37 (900); table in section 2.

Widths (`checks/widths.py`, 16 strings at 10 locations): Rounded equals the
sans to 0.00% everywhere.

Outline hygiene (`checks/outlines.py`): 0 outliers in the core set of the
sans, serif, mono and Rounded text and display masters (no new kink, no
fold-back, no glyph more than 4 points over upstream). Reported, not gated:
glyphs whose only change is new short segments (sans 1, Rounded 1, serif 33,
mono 0) and TrueType extra points at the default (sans 8 core glyphs, serif
1, mono 13).

## Rules to keep

- Every outline change is a script in `transforms/`, run from the baseline
  sources by `apply.py`; masters stay point-compatible.
- The two family details live in `signature.py` and nowhere else: a face
  takes the landing diagonal or the level cut by calling it, so the gesture
  stays one curve across the faces. A diagonal whose top meets a straight
  line must keep a real corner there (`TOP_CORNER`), or the tangent pass will
  straighten it into a swelling.
- Default glyphs must pass the confusable check (`checks/figcheck.py`) at 9,
  11 and 13 px: no pair of `1 l I`, `rn m`, `0 O`, `3 7` under 0.20 xor.
- Rounded is the sans plus a round pen, nothing else, and every master is
  rounded from the sans master of the same name. `checks/skeleton.py` must
  pass (under 4.0). The Regular pen is near that limit (3.68): a larger pen
  needs a different measure, not a bigger radius.
- Tabular figures stay the default and one width at every location; display
  tightening moves every figure by the same amount.
- `checks/outlines.py` must report 0 gated outliers; per-master passes that
  turn handles must not add an interpolation kink.
- Rounded widths equal the sans widths (`checks/widths.py`, under 1%).
- Kink tests run at an em of 1000 units, as the gate's checker does; a test
  at the font's own em misses kinks the gate reports. `checks/vfkinks.py`
  must show 0 for Rounded.
- ℉ and ℃ in the serif are the serif's `°` plus a letter, never a separate ring.

## Next steps

1. Serif interpolation: the three source kinks (dagger, daggerdbl,
   f.ligalong) and the five ff-ligature kinks at opsz 8 are inherited from
   upstream. They are the family's last interpolation findings; find their
   cause in the serif sources, fix it in the serif transform and check with
   `checks/vfkinks.py`.
2. Rounded is at 3.68 of the 4.0 skeleton limit at Regular (G, ℉, B, E, L
   all over 3.4). A rounder Regular needs a measure that tells corner
   rounding (intended) from a moved stroke, not a larger radius.
3. The landing diagonal is under a pixel at 9–13 px, so at text sizes the
   family's own detail is the level cut, the tailed l and the flat-top 3.
   If the review wants a detail that reads at 13 px, try one at stroke ends
   in the sans and mono, held to the confusable check.
4. Mono Bold ℉ and ℃: the letters are 0.93 and 0.92 as wide for their
   height as the face's own F and C, because the cell runs out. A thinner
   Bold ring wall is the next lever; measure at 13–17 px.
5. Headline clearance is 4.56 px at 48 px with the harness's 1.13
   line-height. Recheck if the headline size or line-height changes; the
   opsz 60 cut can go to about 0.16 with a look at display descenders.
6. The inherited checker FAILs and ERRORs (5 + 1 in the sans and mono, 5 in
   the serif, 2 + 1 in Rounded) are the same as in r3; they block only
   `--strict`.

## Rebuild

From the repository root:

```
.venv/bin/python -I scripts/resource_guard.py -- .venv/bin/python -I candidates/r4-type/transforms/apply.py
make build CAND=r4-type SUBSET=core ICONS_DIR=<icons>
make gate CAND=r4-type ICONS_DIR=<icons>
make render CAND=r4-type OUT=<empty dir> MAP=<map file outside OUT> REFS=0 ICONS_DIR=<icons>
make checks CAND=r4-type ICONS_DIR=<icons>
.venv/bin/python -I candidates/r4-type/checks/figcheck.py build/r4-type
.venv/bin/python -I candidates/r4-type/checks/skeleton.py build/r4-type
.venv/bin/python -I candidates/r4-type/checks/widths.py build/r4-type
.venv/bin/python -I candidates/r4-type/checks/outlines.py r4-type
.venv/bin/python -I candidates/r4-type/checks/vfkinks.py build/r4-type
```
