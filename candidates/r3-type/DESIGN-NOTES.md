# r3-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font; reference fonts were only looked at as rendered images.

This round starts from r2-type. Its decisions hold unless a section below
changes them: the shared line metrics, tabular figures by default with
`pnum` proportional, the footed tabular 1, the optical figure kerning, the
caption masters, the key-letter moves (with the exceptions below), the
level-bar `&`, and the mono defaults (closed-ring `@`, conventional `&`,
dotted 0). Before/after images for each item are in `evidence/`.

## Summary against the review

| Priority | Item | State |
| --- | --- | --- |
| 1 | l and I distinct by default (sans, Rounded); confusable xor check | Done: tailed l by default; check gates 1/l, 1/I, l/I, rn/m, 0/O at 9, 11, 13 px, threshold 0.20 |
| 2 | Rounded = Regular skeleton, only rounded; skeleton check | Done: round pen on corners, joins and ends only; curves are the sans's. Check: largest displaced region under 4.0 thousandths of an em squared (build: 0.49 at 400, 3.37 at 900). Plainly round at 24 px at Bold; a softening at Regular |
| 3 | Rounded covers text | Done: Basic Latin (95 of 95) plus ° − ½ ¼ ¾ ℉ ℃ ± ⁄ and four spaces (108 encoded characters) |
| 4 | Outline hygiene; point/kink check against upstream | Done for a, t, 9, R, S; check `checks/outlines.py` |
| 5 | Mono minus/hyphen, ℉ ℃, `++` | Done |
| 6 | Mono and serif identity | Partly: squared dots, flatter bowls and separated operators in the mono; squarer rounds in the serif. The measured change is small: 0.7% of the mono code sheet's ink and 1.6% of the serif text sheet's ink against r2 |
| 7 | Flat-top 3, pnum 1, headline leading | Done: 3 kept, pnum 1 footed, headline gap 5.6 → 3.9 px |

## 1. l, I and 1 differ by default

**Choice: a tailed l.** The default `l` is the sans's tailed l (upstream
drawing; `sans.tailed_l` swaps it with the plain l in every master, with
every accented and styled l that has a tailed twin). The capital I stays
plain.

Why the tail rather than a barred I:

- The tail sits at the baseline and turns right, so at 9 px the l ends in
  a hook that the I's flat foot and the 1's footed base do not have. The
  three letters then differ at the bottom (l), the top (1's flag) and not
  at all for I, which is the plainest of the three.
- A barred I would change every all-caps reading the app sets ("NNW",
  "THU", "IN"), and bars widen the I's footprint in capitals-and-figures
  strings. The tail changes only lowercase words.
- It is an upstream drawing, so it needs no new outline, interpolates in
  every master, and Rounded inherits it with the same rounding as every
  other glyph.

The plain l moves to the alternate: `cv05` (relabelled "Lower-case L
without tail") and `salt` give it. `ss02` and `ss04` ("Disambiguation")
keep the serifed I and the slashed zero but no longer swap the l, which
would remove the tail. Rounded has the same default (the tailed l, plain
I, footed 1). It carries no stylistic alternates, so `cv05`, `salt`,
`ss02` and `ss04` change nothing there; the plain l is a sans-only option.

**Confusable check** (`checks/figcheck.py`, runs first). `1 l I`, `rn m`
and `0 O` are rendered with default features at 9, 11 and 13 px (Regular;
optical size follows the pixel size), each string's ink centred on one
baseline, greyscale and unhinted. Pairwise pixel xor = sum |a − b| / sum
max(a, b): 0 for identical images, 1 for no shared ink. Every pair must
reach **0.20** in every face at every size. The upstream sans's l against
I scores about 0.05 (the same shape); a tail, serif or foot moves a pair
well past 0.20.

## 2. Rounded is the Regular skeleton, only rounded

r2's Rounded was not the sans's skeleton. Its round pen was two stems wide
on corners (1.4 on joins, semicircle ends under 2.2 stems), and it relaxed
every bowl toward a circular arc (0.86 of the arc's handle). That pen
turned the flat top of the 3 into a round top, and the relaxed bowls
pointed the 0 into a lemon. r2's notes said Rounded inherited the
key-letter transforms; in the build, the large pen and the relaxed bowls
had redrawn them (the r2 skeleton result under Gate and checks).

`rounded.py` now does one thing to the finished sans: a round pen on
corners, joins and stroke ends, planned once on the Regular and applied to
the three text masters and the three caption masters, each rounded from the
sans master of the same name, with radii in that master's own stems. The
display masters reuse the text outlines, as the sans's do.

| Setting | r2 | r3 |
| --- | --- | --- |
| Convex corner radius (`R_CONVEX`) | 2.0 stems | 0.60 stem |
| Concave join radius (`R_CONCAVE`) | 1.4 stems | 0.20 stem |
| Stroke ends that become semicircles (`TERMINAL`) | under 2.2 stems | under 1.6 stems |
| Fillet reach along either side (`MAX_CUT`) | no cap | 0.90 stem |
| Bowl relaxation toward a circular arc | 0.86 | none (curves are the sans's) |

- Acute points (A, V, W, the 4's apex) keep their place, because no
  fillet reaches past 0.90 stem. Notches narrower than 0.20 stem in every
  master (the inner points of `<` and `>`) and corners that turn back by
  more than 160° (the crotch where the 6's and 9's straight stems leave
  the bowl) keep their points.
- A line that a master's fillets would use up is ended by two fillets that
  meet at its middle in every master; a line with one fillet that would
  leave a sliver under 16 units is taken whole, except up to a cusp or a
  notch corner that stays sharp (otherwise the fillet would end tangent to
  the far side of it: at Black the g's flag would slope down into its
  bowl). No fillet chord is shorter than 14 units (Thin's joins are a few
  units).
- Tiny fillets that fold back (at Thin, or in the blended display Regular)
  keep their handle directions with handles shortened to where the
  tangents meet; one whose tangents meet behind its ends becomes a
  straight bevel.
- Interpolation: each glyph's fillets are tested with the interpolation
  check's kink test over every master, in source order and in the order
  the font checker walks the variable font, on the cubic outlines and on
  their quadratic conversion at the compiler's tolerance. Where it finds a
  kink, or where one master's outline gains a kink its sans master lacks,
  the curve cuts move part of the way toward the curve points the Regular
  uses: the smallest shares (0.25 steps, text masters first, then caption
  masters) that clear both. In the build, 23 of the 135 Rounded glyphs
  needed a share; the S and the $ take the full share (1.00) in their text
  masters.
- The ½ is the one glyph no share clears: the sans's caption stem gain
  folds the counter of its small 2 at Black. Its Rounded caption masters
  take 0.75 of the caption outlines, moving from the text masters' rounded
  outlines centred on the caption glyph (the largest share that clears
  the test).
- Rounding at 24 px: at Regular text size the sans stem is 190 of 2048
  units, so a stroke end is a semicircle about 2.2 px across and a corner
  has a radius of about 1.3 px. At Bold and Black the round ends and
  corners show plainly at 24 px. At Regular they read as a softening of
  every end and corner rather than as an obviously round face: the stroke
  ends are already full semicircles, the most a round pen can do on a
  2.2 px stem. Evidence sheet 2 shows both weights at 24 px.

**Skeleton check** (`checks/skeleton.py`). Every glyph Rounded draws is
rendered from the built Rounded and the same glyph of the built sans, at
the same pen origin, 256 px per em, unhinted, at opsz 14 Regular and
Black, thresholded at half coverage. Each face's ink is dilated by a disc
of 0.012 em; ink of one face outside the other's dilated ink is displaced.
A round pen of a fraction of a stem leaves small separate crumbs, one per
corner; a changed construction (a figure redrawn, a bowl moved, a corner
rounded by several stems) leaves one large region. The gate is the largest
4-connected displaced region in either direction, in thousandths of an em
squared: under **4.0** at both weights for every glyph (4.0 is a square
0.063 em on a side, about two thirds of a Regular stem).

## 3. Rounded covers text

Rounded draws every character of U+0020–U+007E (A–Z, a–z, figures,
punctuation and symbols) plus ° % − ½ ¼ ¾ ℉ ℃ ± ⁄ and the figure,
punctuation, thin and no-break spaces, all by the same rounding from the
finished sans glyph of the same character. It also takes the sans's
proportional figures (`pnum`), case forms (`case`) and the `calt` rules
that pick them, and the sans's kerning groups and pairs for these glyphs,
so "3 PM", "12 mph NNW", "30.16 inHg" and "Thu" set entirely in Rounded at
the sans's widths.

## 4. Outline hygiene

**Outline check** (`checks/outlines.py`, runs after the transforms). Each
glyph is compared with the upstream glyph that holds its drawing (the
`com.strata.source` key the transforms record, otherwise the same name),
master by master:

- points: every point, on- and off-curve (components decomposed);
- kinks: on-curve joins that are nearly smooth but not quite (a turn of
  3–25° with a curve on at least one side), or any turn over 2° at a point
  flagged smooth;
- back: curve segments that fold back on themselves (a loop or cusp in the
  control polygon, or a handle pointing back along the chord);
- short: segments under 12/2048 em (4/2048 em in Rounded, whose fillets are
  short by design), reported only.

Rounded is compared with the finished sans glyph of the same name, for
kinks and fold-backs only (its fillets add points by design). A glyph is an
outlier when it gains a kink or a fold-back over its upstream, or gains more
than 4 points and more than 15% of its upstream count. The gate covers the
core set (U+0020–U+007E, ° % − ½ ¼ ¾ ℉ ℃ ±, with their proportional,
tabular and case forms) in the text and display masters m00–m05 and every
Rounded master; the full repertoire, the caption masters and the
TrueType point counts are reported without gating. Exit 1 on any gated
outlier.

The five glyphs the review named:

- **a bowl top.** The extra figure squaring (`FIG_TAUT`) no longer applies
  to the a: on its bowl it bent the top join. `a_bowl` now moves each
  handle by the weight of the on-curve point it belongs to, so a handle and
  its point rise together and the join stays tangent.
- **t foot.** An axis-cut terminal trim that would leave a curve piece
  shorter than 0.45 stem beside the cut (`identity.STUB`) is not made; the
  cut turns onto the axis about its midpoint instead, its neighbouring
  handles moving with it. The t's foot is now one cut between two curves,
  with no cluster of short pieces.
- **9 notch.** The straight-stem 6 that the default 9 is drawn from met its
  diagonal through a flat step about a tenth of a stem long (two corners,
  upstream). `sans.six_notch` merges the step into one corner, in every
  master, before the 9 is made from the 6.
- **R leg junction.** `identity.r_leg` replaces the shared k/R leg move:
  the leg's inner edge, kept on its bottom point, is aimed at the corner of
  the stem and the bowl's lower bar, so there is no step or notch between
  bar and leg, and the leg keeps its thickness.
- **Dense S.** The S's density was turned joins: the squarer rounds and the
  axis cuts turned smooth joins next to its spine. `transforms/tangency.py`
  (run last on every face) realigns any join that was tangent upstream, or a
  corner that a transform flattened to a near-tangent, by turning its
  handles about the on-curve point; handle lengths and point counts are
  unchanged.

Before and after, per glyph (text masters m00, m02, m04; points / kinks
against upstream):

| Glyph (drawing it starts from) | Master | Upstream | r2-type | r3-type |
| --- | --- | --- | --- | --- |
| a | m00, m02, m04 | 43 / 0 | 43 / 0 | 43 / 0 |
| t | m00 | 20 / 0 | 20 / 1 | 20 / 0 |
| t | m02, m04 | 20 / 0 | 20 / 0 | 20 / 0 |
| 9 (`nine.ss01`) | m00, m02, m04 | 31 / 0 | 31 / 0 | 30 / 0 |
| 6 (`six.ss01`) | m00, m02, m04 | 31 / 0 | 31 / 0 | 30 / 0 |
| R | m00, m02, m04 | 24 / 0 | 24 / 0 | 24 / 0 |
| S | m00, m02, m04 | 40 / 0 | 40 / 0 | 40 / 0 |

TrueType points in the default instance, r2 → r3: a 58 → 58, t 22 → 23,
9 44 → 43, 6 44 → 43, R 28 → 28, S 53 → 53. The 9 and the 6 lose the
point of the flat step (`six_notch`), and their one short segment at m00
is gone. The a, R and S faults were visual (a bent bowl-top join, a notch
at the leg, crowded turned joins) and did not register in the point and
kink counts; evidence sheet 4 shows each outline before and after.

All gated outliers, r2-type against r3-type:

| Face | r2-type gated outliers | r3-type |
| --- | --- | --- |
| Sans | 6: e, g, s (m04), t (m00), two.pnum (m04), x (m05); each a new kink | 0 |
| Rounded | 16: C, ampersand, comma, degreecentigrade, five, five.pnum, nine, nine.pnum, one.pnum, six, six.pnum, slash, three, three.pnum, two, two.pnum; each 1–3 new kinks | 0 |
| Serif | 15: G, J, a, asterisk, braceleft, comma, dollar, exclam, f, g, j, p, question, r, y; each new kinks | 0 |
| Mono | 5: a and two (a new kink); ampersand 44 → 58, at 52 → 64 and zero 28 → 36 points | 0 |
| Total | 42 (FAIL) | 0 (PASS) |

Reported, not gated: TrueType points grow in the sans's zero.pnum
(34 → 42) and zero.pnum.slash (38 → 46), and in 13 core mono glyphs where
the squarer rounds meet the quadratic conversion (the largest are zero
42 → 59, O 30 → 42, Q 39 → 51 and a 44 → 54).

## 5. Mono details

- **Minus and hyphen.** The minus is now the plus sign's bar: as wide as
  the plus, on the plus's axis and at its thickness (`dashes`). The hyphen
  is half a cell wide, centred, at its own height. In the build (Light,
  the default) the minus spans 913 of the cell's 1,217 units, exactly the
  plus bar, centred 2 units from the plus's axis; the hyphen spans 609
  (0.50 of the cell). In r2 the hyphen (793 units) was wider than the
  minus (710).
- **℉ and ℃.** Choice: one cell, letter first. The letter is the mono's
  own F or C, condensed to fill the cell after a small open ring at the top
  left, at full cap height. In r2 the ring took 0.31 of the cell with a
  0.06-cell margin, which pinched the letter. Now the ring is 0.29 of the
  cell (about 0.34 at Bold), the margin 0.025 and the gap 0.03, so the
  letter has 0.63 of the cell in ℉ and 0.65 in ℃ (0.55 and 0.56 in r2). At
  13–17 px the F's arms and the C's aperture stay open (evidence sheet 5).
- **`++` and `+++`.** The ligatures were one joined outline whose bars ran
  into each other, which read as H. They are now separate plus signs, one
  per cell, each pulled toward the group's middle by at most 0.04 cell and
  never closer than 1.5 bar thicknesses (`separate_pluses`). In the build
  `++` is two contours with 207 units between the bars at Light and 181 at
  Bold (r2: one contour, bars joined).

## 6. Identity

**Mono.** Three changes give the mono more of its own drawing, all judged
from rendered images and none copied:

- a further squaring pass on the round letters and figures
  (`MONO_SQUARE` = 0.25, on o c e b d p q n h m u, O C D G Q U and
  0 2 3 5 6 8 9), on top of the mono's earlier squaring, so bowls are flat
  sided; any glyph it would kink is left as it was (all 24 took it);
- squared dots: the dots on i j : ; ! ? and the period put their handles
  0.90 of the way from each side's middle to the corner (`square_dots`);
- the operator details above.

Measured on a seven-line code sheet set at 15 and 30 px (unhinted
greyscale), the mono differs from r2-type in 0.7% of its ink pixels (0.06%
of all sheet pixels; coverage xor 0.010). That is a visible but small
step. The concern that the mono is still close to its predecessor stands,
and a larger change of construction, not only of detail, is listed under
next steps.

**Serif.** The family's signature is the squarer round. The serif's rounds
now take 0.16 of the way toward the corner (`serif.ROUNDS`, 0.10 in r2), so
its bowls share the sans's superelliptic shape more plainly. The serif's
text sheet differs from r2's in 1.6% of its ink pixels at 17 px (0.16%
of all pixels; coverage xor 0.026), mostly from the rounds and the longer
descenders. This is also a small step.

Kept because reviewers praised them: the footed tabular 1 by default, the
Rounded widths and centred colon, the sans's open apertures and axis cuts,
and the figure shapes.

## 7. Watch items

- **Flat-top 3.** Kept. Judged from the built sans at 9, 11 and 13 px
  (evidence sheet 7), alone and in "23°", "13:30" and "3 PM": the open
  lower bowl and the short diagonal read as a 3 at every size. No check
  measures the 3 against similar shapes; this is a visual judgement.
- **pnum 1.** The proportional 1 now has the tabular 1's foot
  (`sans.footed_pnum_one`): the foot is 0.80 of the tabular foot's width,
  so the proportional figure stays narrower, and its sidebearings are the
  proportional 2's. Rounded inherits it.
- **Headline leading.** The serif's descenders were shortened by 0.23 of
  their depth in r2; now by 0.10 (`serif.DEPTH_CUT`), so the line box does
  not grow and a 48 px serif headline at line-height 1.13 keeps
  3.9 px between a descender and the next line's ascender (q to b, f
  and h; 5.6 px in r2), measured on the built fonts.

## Gate and checks

`make gate` (fontbakery counts; interpolation = the interpolation check's
findings; hard failures 0, names PASS and no missing required glyphs in
every face):

| Face | Build | Pass | Warn | Fail | Error | Interpolation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Sans | r2-type | 92 | 4 | 5 | 1 | none |
| Sans | r3-type | 92 | 4 | 5 | 1 | none |
| Serif | r2-type | 95 | 5 | 5 | 0 | 4 kinks (dagger, daggerdbl ×2, f.ligalong) |
| Serif | r3-type | 95 | 5 | 5 | 0 | the same 4 kinks |
| Mono | r2-type | 90 | 6 | 5 | 1 | none |
| Mono | r3-type | 90 | 6 | 5 | 1 | none |
| Rounded | r2-type | 91 | 0 | 4 | 1 | none |
| Rounded | r3-type | 98 | 0 | 2 | 1 | none |

Rounded's remaining findings are the fvar/STAT consistency and
smart-dropout FAILs and the family-and-style name length ERROR; the r2
case-mapping and whitespace-glyph FAILs are cleared by the full Basic
Latin. Core coverage is 258/258 in the sans, serif and mono, 29/29 in
Rounded. WOFF2 sizes: sans 107,932 bytes, serif 196,676, mono 47,732,
Rounded 64,944.

Run on the built variable fonts at every master location, the
interpolation check's kink test finds 0 problems in the sans, mono and
Rounded (as in r2) and 6 in the serif (10 in r2): one kink in each of the
ff ligatures (ff, ffi, ffl, fft, ffj) between the lightest and the Black at
opsz 8, and one underweight μ, all present in r2 at about the same size.

`make checks`: PASS. Rounded ink width against the sans Regular at 96 px
is within 0.74% for "104°F", "72°", "18:30" and "−3°" (limit 1%), and the
default shaped figures are tabular at every named instance and axis
corner (sans, mono and Rounded PASS; serif INFO, as in r2). `make render`
writes 38 sheets; the headline line-contact report is clear (0 contact
regions) on the light, dark and glass surfaces.

Confusable check (pixel xor, default features; every pair ≥ 0.20, PASS):

| Face | px | 1/l | 1/I | l/I | rn/m | 0/O |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans | 9 | .680 | .487 | .530 | .652 | .499 |
| Sans | 11 | .713 | .494 | .580 | .658 | .467 |
| Sans | 13 | .735 | .528 | .608 | .519 | .520 |
| Serif | 9 | .346 | .316 | .227 | .597 | .741 |
| Serif | 11 | .297 | .282 | .294 | .587 | .701 |
| Serif | 13 | .351 | .277 | .254 | .679 | .786 |
| Mono | 9 | .468 | .382 | .366 | .817 | .357 |
| Mono | 11 | .436 | .373 | .439 | .909 | .386 |
| Mono | 13 | .511 | .374 | .453 | .871 | .379 |
| Rounded | 9 | .680 | .492 | .544 | .653 | .499 |
| Rounded | 11 | .714 | .499 | .593 | .665 | .467 |
| Rounded | 13 | .735 | .531 | .618 | .528 | .520 |

In r2-type the sans's l against I scored 0.048, 0.055 and 0.050 (FAIL).

Skeleton check: PASS over 130 glyphs; largest displaced region 0.49 at 400
and 3.37 at 900 (M), mean 0.13; r2-type FAILED with 18 of its 36 glyphs at
or over 4.0 (largest 8.77 at 400 in zero.pnum, 14.72 at 900 in ℉).

Widths (`checks/widths.py`, 16 strings at 10 locations): Rounded equals
the sans to 0.00% everywhere ("3 PM" 5104 = 5104, "Thu" 3780 = 3780 units
at opsz 14 Regular). In r2-type the largest difference was 24.5% ("½ ¼ ¾"
−18.1%, "Rain, 40%." +11.3%, "3 PM" −9.2%), because letters were missing.

## Rules to keep

- Every outline change is a script in `transforms/`, run from the
  baseline sources by `apply.py`; masters stay point-compatible.
- Default glyphs must pass the confusable check (`checks/figcheck.py`) at
  9, 11 and 13 px: no pair of `1 l I`, `rn m`, `0 O` under 0.20 xor, in the
  sans and in Rounded.
- Rounded is the sans plus a round pen, nothing else. A change to a sans
  glyph changes Rounded through the same pen; never draw Rounded by itself.
  `checks/skeleton.py` must pass (largest displaced region under 4.0
  thousandths of an em squared at 400 and 900).
- Every transform that moves points records the upstream drawing it starts
  from (`com.strata.source`), and `checks/outlines.py` must report 0 gated
  outliers: no glyph gains a kink, a fold-back or more than 4 points and
  15% over its upstream.
- A per-master pass that turns handles must not add an interpolation kink.
  `identity.rounds` and `tangency.restore` check each glyph with the
  interpolation check's kink test and keep the earlier outline where it
  would kink; `rounded.round_masters` moves its curve cuts (and, for ½,
  its caption gain) until the test clears over every master, in source
  and variable-font order, on the cubic and the quadratic outlines.
- Rounded widths equal the sans widths (`checks/widths.py`, under 1%), and
  tabular figures stay the default.

## Next steps

- The sans's caption stem gain folds the counters of the small fraction
  figures at Black (the 2 of ½: `checks/outlines.py` reports the sans
  caption masters without gating). A gain that grows those counters'
  sides less would clean the sans and let Rounded take the full caption
  outlines for ½.
- The serif's family detail is still limited to squarer rounds. Axis-cut
  terminals on the serif's c, e, s and r would carry the sans's sharpest
  trait, but need their own kink-checked plan for the bracketed terminals.
- The mono's identity needs a larger step than this round's details (0.7%
  of its code-sheet ink): its own construction of the rounds, terminals
  and figure widths, judged against rendered references only.
- At Regular text size Rounded reads as softened rather than round. A
  larger convex radius on stroke ends is not possible (they are already
  semicircles), so a plainer Regular needs larger corner radii, held
  under the skeleton gate.
- The mono's TrueType outlines gain points where the squarer rounds meet
  the quadratic conversion (`checks/outlines.py` reports them); a tighter
  conversion tolerance for the mono would bring them down.
- The serif's dagger, double dagger and long f ligature keep the upstream
  interpolation kinks between the opsz 8 Black and the opsz 20 lightest
  masters (4 findings in 3 glyphs, as in r2-type; the baseline had 5 in 4).

## Rebuild

From the repository root:

```
.venv/bin/python -I scripts/resource_guard.py -- .venv/bin/python -I candidates/r3-type/transforms/apply.py
.venv/bin/python -I candidates/r3-type/checks/outlines.py r3-type
make build CAND=r3-type SUBSET=core ICONS_DIR=<icons>
make gate CAND=r3-type ICONS_DIR=<icons>
make render CAND=r3-type OUT=<empty dir> MAP=<map file outside OUT> REFS=0 ICONS_DIR=<icons>
make checks CAND=r3-type ICONS_DIR=<icons>
.venv/bin/python -I candidates/r3-type/checks/figcheck.py build/r3-type
.venv/bin/python -I candidates/r3-type/checks/skeleton.py build/r3-type
.venv/bin/python -I candidates/r3-type/checks/widths.py build/r3-type
```
