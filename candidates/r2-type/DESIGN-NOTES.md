# r2-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font. Reference fonts were only looked at as rendered images.

This round starts from the r1 candidate. Its decisions still hold unless a
section below changes them. These include the shared line metrics, the
footed tabular 1, the optical figure kerning, the degree ring, the open 4,
the spurred G, the slanted t and the core coverage of 258/258. The
key-letter moves below build on the G, t, y and R and on the mono
operators.

## Summary against the review

| Priority | Item | State |
| --- | --- | --- |
| 1 | Tabular figures by default, `pnum` proportional, regression check | Done |
| 2 | Bold moves on a g t f r y R G k and 0 2 3 4 6 7 9 | Done (`keys.py`); see "Key letters and figures" |
| 2 | Serif `&` level-bar terminal carried into sans, Rounded and mono | Done (`amp_bar`); Rounded now draws `&` |
| 2 | Mono as its own drawing | Done for a g r y, 1 l i and the comparison operators. I and `\|\|` are unchanged. |
| 3 | Rounded: colon centred, widths within 1%, visible rounding, same 1 | Done |
| 4 | Serif colour 0.88–0.95, 400→600 step 30–35%, headline ≥ 4 px | Mostly. The "Age 0123" step is 30.3–34.0% at every size, after a separate cap/figure gain. The paragraph step is 31.7–35.5%. Paragraph density is 0.935–0.955 at 9–48 px and 0.970–0.971 at 64–96 px. Headline clearance is 5.0 px. |
| 5 | Small-size weight and open display tracking | Done |
| 6 | Mono closed-ring `@` and conventional `&` by default, old forms in a set | Done |

## Figures: tabular by default

Before this round, the sans mapped 0–9 to proportional figures, and
tabular figures needed `tnum`. r1's sans fails the check below: at Thin text
size, for example, its default 0 and 1 are 1197 and 614 units wide (of
2048), and `tnum` changes them. r1's Rounded already set tabular figures by
default, but in its own narrower cell (1232 units against the sans's 1332).

- **Sans** (`sans.tabular_default`). The default (encoded) figures now hold
  the tabular drawings. The proportional drawings move to new `.pnum` glyphs,
  which `pnum` selects.
  - The `.tf` twins become references to the defaults, so `tnum` changes
    nothing.
  - Every later feature rule that takes a default figure (slashed zero,
    stylistic sets, character variants) gets the same rule for its `.pnum`
    glyph, so the alternates work in both spacings.
  - Composites made from figures elsewhere (circled figures, letters drawn
    from figures) keep the proportional drawing.
  - Kerning moves with the drawings. The proportional pairs go to `.pnum`,
    and the defaults take the tabular kerning.
- **Rounded** follows the sans (below), so it has the same default and `pnum`.
- **Serif and mono** already set equal-width figures by default.
- **Regression check.** `checks/figcheck.py` shapes "0123456789" with no
  features requested. It runs at every named instance and at every
  combination of axis minimum, default and maximum. It fails unless all ten
  default advances are equal, `tnum` equals the default, and `pnum` varies
  (the mono is exempt from `pnum`).

      .venv/bin/python -I candidates/r2-type/checks/figcheck.py build/r2-type

## Strata Sans

- **Taut rounds** (`TAUT = 0.15`). A second squaring pass runs on top of
  r1's, with the same kink check: 484 glyphs changed. Bowls, shoulders and
  round figures are tauter and more superelliptic. Rounded inherits this
  before its own softening.
- **Caption masters** (`caption`, opsz 8). Three new masters serve
  8–13 px text: Caption Thin, Caption and Caption Black. They are the
  finished text masters with heavier vertical stems and looser spacing, so
  small text keeps a dark core instead of turning to grey edges.
  - The Regular stem gains 44 units (of 2048).
  - Thin and Black gain what keeps the text masters' ink progression:
    11.9 and 88.5 units. Weights therefore step evenly at every size.
  - Each glyph opens by half its stem gain plus 24 units per side.
  - `.notdef` is not emboldened, because its drawn box would close up in
    Caption Black.
  - The opsz axis now runs 8–32.
- **Display tracking.** Display masters close by 6 units per side, where r1
  used 10. Figures, and the period, comma, colon and semicolon between them,
  keep their text-size room at display sizes (`keeps_room`), so 72 px
  readings such as 0123 and 30.16 stay open.
- **Proportional 1-pairs.** The floor for 1-pairs rose from 0.8 to 1.2 of
  the 0 0 bounding gap (`ONE_FLOOR`). At display sizes, a lone stem matched
  by area alone jammed 012.
- **Weight map.** Medium and SemiBold sit at 495 and 590 (r1: 490 and 580),
  so 400 → 600 darkens text by about a third.
- **Display Black.** Display Black is re-mixed 21% toward display Regular
  (`display_black`). Black then carries the same ink relative to Regular at
  display size as at text size. The finer display Regular had made display
  weight steps larger than text steps. The rendered 400→600 step at 64–96 px
  was +41.5–42.4% against +29.8% at 15 px. It is now +34.6–35.4% against
  +31.0%.

## Key letters and figures

`transforms/keys.py` makes one move per letter or figure. Each move is
planned on the Regular text master (m02): which contour, which points.
It is then applied to every master with that master's own stem and
x-height, so the point structure does not change. The moves that bend
curves (7, y, r, a and the mono operator cuts) run under a kink check that
would undo the move for that glyph; none was undone. The other moves shift
straight corners or add bars. The gate's interpolation check covers all of
them, with 0 findings in sans, Rounded and mono. The aim is qualities seen in
rendered reference images: straight strokes, level cuts, taut rounds and
large counters. No reference outline was used.

Sans moves (Rounded is made from the sans, so it carries all of them):

| Glyph | Move | Setting |
| --- | --- | --- |
| a | The bowl's top rises into the hook's counter, so the bowl is larger and the hook's counter smaller | 0.28 of the gap (`A_BOWL`) |
| g | A level ear on the stem top. The advance grows by half the ear's length. | ear 0.5 stem long, 0.92 hyphen thick (`EAR`, `AMP_BAR`) |
| t, f | The crossbar leads right. Its left overhang is cut to 0.45 of its length. The t's right overhang grows by 1.2×. The stem keeps its place. The t's advance grows by its right-side gain (682 → 728 of 2048 at Regular text), and composites built on t or f gain the same width. | `BAR_LEFT`, `T_RIGHT`; 7 glyphs |
| r | The arm ends on a slanted cut at the t's angle | 0.43 run per unit of cut height (`R_ANGLE`) |
| y | The tail runs straight on the line of the right stroke. Both edges are straight and parallel, and the tail is cut level at the descender. | `y_straight` |
| k, R | The leg springs from the stem: its top-left point sits inside the stem | 0.10 stem (`K_INTO`) |
| G | The bar reaches further into the counter | 0.6 stem longer (`G_BAR`) |
| 3, 6, 9 | The flat-top 3 and the straight-stem 6 and 9 become the defaults, beside r1's open 4. The drawings swap in every size and form: 24 pairs, covering tabular, `pnum`, circled, squared, numerator, denominator, superior and inferior forms. | `swap_figures` |
| 7 | The foot moves right, so the stem stands steeper | 0.45 stem (`SEVEN`) |
| 0 2 3 6 9 a g | One more squaring pass, on top of the family's two. It changed 6 of these 7 glyphs. | 0.25 (`FIG_TAUT`) |

0 and 2 take only the extra squaring, and the 4 keeps r1's open form.

**Alternates.** The round forms remain available:

- `ss01` "Classic digits" gives the round-top 3, closed 4, curved 6 and
  curved 9;
- `cv02` "Closed four", `cv03` "Curved six", `cv04` "Curved nine" and
  `cv09` "Round-top three" give each figure on its own.

The labels were renamed to match the swapped drawings (`FEATURE_NAMES`).
This also corrects `cv02`, which still read "Open four" after r2 made the
open 4 the default.

## The `&` signature

The serif's `&` ends its arm under a level bar. That bar is now the family's
signature in all four faces (`amp_bar`):

- **Sans and mono.** The arm's two top points rise to 0.80 of the x-height
  and are levelled. A level bar is added across the arm top. It overhangs
  0.45 of the arm's width on the left and 0.35 on the right, and it is 0.92
  of the hyphen's thickness. The mono's arm cut was slanted; it is
  levelled first.
- **Rounded** now draws `&`, from the sans `&` through the same rounding.
  Like every other Rounded glyph, it keeps the sans advance and kerning. It
  is extra coverage; the gate's required Rounded set is unchanged (29/29).
- **Mono `&&`.** By default the first `&` of the pair is the upstream
  armless pair form, so only the second `&` shows the bar.

## Strata Sans Rounded

r1's Rounded had its own narrower tabular cell and its own figure widths. A
reading set in it did not match the same reading in the sans (up to 16.09%
wider or narrower). r2 builds it on the sans skeleton instead.

- **Advances and kerning copied.** Every glyph keeps the advance the sans
  gives the same character in figure context, in every master. This covers
  the tabular default, `pnum`, degree, percent and minus. The sans's kerning
  between those glyphs is copied too.
  - The display and caption masters reuse the rounded text outlines. Each
    outline is centred where the sans master centres the same glyph, on the
    sans advance.
  - The caption masters take the sans caption stem gain.
- **Colon.** The colon is the sans's raised colon (`colon.case`), the one
  that sits between figures. Its dots centre on the figures (dot centre at
  744.5 units, figure centre at 745.0) and in the advance (166 units each
  side). r1's Rounded used the baseline colon, centred at 526.5 units, with
  150 and 142 units of side room.
- **Widths.** The largest Regular/Rounded difference is 0.00%, over 9
  strings at 10 locations (r1: 16.09%). The strings are 72°, −3°, 104°F,
  18:30, 80%, 30.16, 0123456789, 12:05 and −12°C. The locations are:
  - opsz 14 at weights 100, 400, 700 and 900;
  - opsz 32 at 400 and 900;
  - opsz 20 at 500;
  - opsz 8 at 100, 400 and 900.

  Check:

      .venv/bin/python -I candidates/r2-type/checks/widths.py build/r2-type

- **Same 1.** The default 1 is the sans's footed tabular 1, and the `pnum` 1
  is the sans's proportional 1, both rounded.
- **Key moves and `&`.** Rounded is made from the finished sans masters, so
  it has the sans's key-letter and figure moves (flat-top 3, straight-stem 6
  and 9, steeper 7) and its level-bar `&`. The `&` is new in Rounded.
- **Rounding plainly visible.** The radii are two to three times r1's:

  | Setting | r1 | r2 |
  | --- | --- | --- |
  | Convex corner radius | 0.95 stem | 2.0 stems |
  | Concave join radius | 0.48 stem | 1.4 stems |
  | Stroke ends that become semicircles | under 1.7 stems | under 2.2 stems |
  | Bowl handles, share of a circular arc's | 0.97 | 0.86 |

  The bowls therefore read soft against the sans's taut ones, and the
  degree ring stays round.
- **Compatible joins.** The kink check now also compares Thin with Black
  directly. The gate compares the display Black with the caption Thin, and
  the earlier chain-only check missed joins in 3 and 5 there. Interpolation
  findings: 0.

## Strata Serif

Colour is measured as **density**: rendered ink divided by the line's
length, relative to the sans at 400 at the same CSS size. The serif sets
about 8% wider than the sans, so equal total ink reads lighter. Density is
the measure used here.

- **Stroke colour per optical size** (`colour_masters`). The vertical
  strokes of each master are thickened or thinned by a solved gain until:
  - each optical size's Regular holds a set share of the sans's outline ink
    at the CSS size it serves: 0.96 at caption and text, 1.00 at display
    (`COLOUR`);
  - Thin and Black keep the text size's ink progression;
  - display Black eases to 0.955 of it (`BLACK_AT`). At display size the
    screen prints outline area as drawn, so the steeper step that text needs
    would overshoot there.

  Gains in units per master, m00–m08: −11.4, −26.6, −26.4, −6.7, −16.4,
  −29.6, 7.3, 21.5, 12.1.
- **Small forms** (superiors, inferiors, numerators, denominators) take 0.6
  of the gain (`SMALL`). They are drawn at about that size, and the full
  gain gave `u.sups` a wrong-start-point interpolation finding.
- **Capitals and figures** (new, `CAPFIG_BLACK`). In the three Black
  masters, capitals and figures take extra stroke on top of the solved
  gain:
  - 38 units at caption size (opsz 8);
  - 20 at text size (opsz 20);
  - 10 at display size (opsz 60).

  With one gain for every glyph, "Age 0123" stepped 4.7–7.7 points less
  from 400 to 600 than running text did at the same size. Its step is now
  30.3–34.0% at every size, and the paragraph step stays within 0.2 points
  of r2's. Capitals and figures are the glyphs with an uppercase or digit
  code point, plus the unencoded alternates of A–Z and 0–9. Small forms
  and small capitals are excluded. A
  single value of 20 at all sizes left 9 px at 27.2% and took 96 px to
  36.1%, which is why the value varies with optical size.
- **Weight steps** (new). Medium and SemiBold target the sans's ink ratio
  to the power 1.12 (`STEP_GAMMA`). The serif's added ink goes into stems
  while hairlines print light, so an equal outline-area step prints smaller.
  The weight map is 200→0, 300→239, 400→394, 500→533, 600→672, 700→736,
  800→869, 900→1000.
- **Headline clearance.** Descenders (p q g y j) shorten by 23% of their
  depth (r1: 14%), and ascenders (b d f h k l) drop 20 units. The shared
  line metrics and the harness line height are unchanged. The closest ink
  between headline lines went from 3.0 px to 5.0 px on light, dark and
  glass.

## Strata Mono

- **Defaults** (`at_amp_defaults`). Three upstream alternates become the
  defaults: the closed-ring `@`, the conventional `&` and the dotted 0. The
  old forms move to stylistic sets:
  - the open `@` and the `~@` ligature go to `ss05` ("Open at sign");
  - the Et-style `&` and its `&&` ligature go to `ss03` ("Et ampersand");
  - the slashed 0 goes to `zero`.

  By default, `&&` sets as two conventional `&`, using the upstream pair
  form for the first. Composites that drew the old forms (the `&&` and
  `&&&` ligatures, the `cv12` zeros) keep them.
- **Family squaring and terminals.**
  - Rounds are squared harder than the sans's (`MONO_ROUNDS = 0.30`, on top
    of the earlier squaring): 444 glyphs changed.
  - The family's axis-cut terminals (`identity.terminals`, planned on Light
    and carried to Bold) were cut on 126 glyphs. Among basic Latin letters
    and figures these are C G J Q S, a c e f g j l r s t y, and 2 5. The cuts
    planned for 3 6 9 could not be made compatibly in both masters, so those
    keep their upstream ends.
- **Own drawing** (`keys.mono`, planned on Light and carried to Bold). The
  aim is the plain, engineered character of the coding faces named in the
  brief, judged by eye from rendered images only.
  - **a g l, the dots of i and j, the period and the dot part**: one more squaring pass,
    stronger than the sans's (`MONO_TAUT = 0.40`; 7 glyphs changed).
  - **r**: the drooping beak at the arm's end (a separate contour) is
    removed. The arm then ends on the sans r's slanted cut.
  - **y**: the sans y's straight tail, cut level at the descender.
  - **1**: the flag flattens. Its tip rises by 0.55 of its drop
    (`ONE_FLAG`). This separates it further from l and I.
  - **Operators.** Slanted stroke ends on `<` `>`, the arrowhead parts of
    the `->` `<-` `>>=` family of ligatures, the slash of `!=` and the
    `!==` ligature become level cuts (`level_ends`). Strokes shallower than 30° keep their ends
    (`MIN_ANGLE`), because a level cut there leaves a long spike. `>=` and
    `<=` take a level or-equal bar under the chevron, in place of the bar
    that ran parallel to the lower arm (`level_or_equal`). It spans the
    chevron, sits one equal-sign gap below it, and is as thick as the
    equal sign's bars.
  - **`&`**: the level-bar signature (see "The `&` signature").
  - **Unchanged**: I (already serifed, which keeps it apart from l and 1),
    and `||`, which is two plain bars.
- **Weight steps** (`ink_steps`). Medium and SemiBold are placed by ink so
  that 400 → 600 darkens by the same share as the sans text. The map is
  300→62, 400→82.5, 500→100.5, 600→118.5, 700→131.9.

## Measurements

Rendered ink is measured on the specimen paragraph and on "Age 0123", in a
browser at 2×. Each cell shows total ink, then density, then the 400→600
step. The first two are relative to the sans at 400.

| Size | Serif paragraph | Serif "Age 0123" | Sans step (para / Age) | Mono paragraph |
| --- | --- | --- | --- | --- |
| 9 px | 1.010 / 0.955 / +31.7% | 0.870 / 0.937 / +30.3% | +31.6% / +31.8% | 0.900 / 0.727 / +39.3% |
| 13 px | 1.025 / 0.937 / +32.8% | 0.877 / 0.919 / +34.0% | +30.8% / +31.5% | 0.979 / 0.748 / +30.9% |
| 15 px | 1.022 / 0.940 / +32.7% | 0.868 / 0.919 / +33.5% | +31.0% / +31.4% | 1.009 / 0.754 / +30.9% |
| 17 px | 1.002 / 0.935 / +32.7% | 0.846 / 0.912 / +33.1% | +31.1% / +31.4% | 1.021 / 0.754 / +30.8% |
| 32 px | 1.063 / 0.941 / +34.1% | 0.833 / 0.910 / +31.7% | +32.5% / +30.3% | 1.142 / 0.770 / +32.0% |
| 48 px | 1.040 / 0.954 / +34.7% | 0.814 / 0.918 / +32.5% | +33.8% / +31.7% | 1.145 / 0.772 / +33.1% |
| 64 px | 1.029 / 0.971 / +34.6% | 0.805 / 0.930 / +32.7% | +34.6% / +32.5% | 1.145 / 0.772 / +33.9% |
| 96 px | 1.027 / 0.970 / +35.5% | 0.801 / 0.926 / +33.7% | +35.4% / +33.2% | 1.148 / 0.774 / +34.6% |

Before the identity moves and the cap/figure gain, the serif "Age 0123"
step was +23.8% (9 px), +27.8–28.1% (13–32 px), +29.7% (48 px), +30.4%
(64 px) and +31.3% (96 px).

Before and after, for the serif and the sans:

- **r1 serif density** ran from 1.148 at 9 px to 0.805 at 96 px in the
  paragraph, against 0.93–0.97 now. Its paragraph steps were +21.2% (9 px),
  +24.0% (15 px), +32.9% (48 px) and +37.3% (96 px).
- **Sans step.** In r1 the sans step was +29.8% at text size and
  +41.5–42.4% at 64–96 px. In r2 it is +30.3% to +35.4% at every size, after
  the display Black re-mix.
- **Outline area** (drawn ink of a mixed sentence at the same CSS size, from
  the compiled fonts) gives serif/sans 0.94, 1.01, 0.96 and 1.01 at opsz 9,
  15, 20 and 48. The density ratios are 0.89, 0.94, 0.93 and 0.96. In r1 the
  ink ratios were 1.29, 1.21, 1.12 and 0.95.

What the table shows:

- **Serif density** in the paragraph is 0.935–0.955 at 9–48 px and
  0.970–0.971 at 64–96 px. The aim is 0.95, so 9 and 48 px are just above
  it and 64–96 px are 0.02 above. In "Age 0123" it is 0.910–0.937 at every
  size. Against the pre-identity build, paragraph density rose by
  0.003–0.007. Density is measured against the sans, whose key letters
  changed; the serif's Regular stroke gains moved by 0.2 units or less.
- **Serif paragraph step** is +31.7% to +35.5%. The 96 px value is 0.5
  points over the aim, as before.
- **Serif "Age 0123" step** is +30.3% to +34.0% at every size, inside the
  30–35% aim, after the capitals and figures gain (see Strata Serif).
- **Mono.** Its paragraph density is lower (0.73–0.77): the monospaced cell
  gives narrow letters a full advance. Its 9 px paragraph step (+39.3%) is
  the one outlier, and its cause has not been traced.

## Gate versus starting point

Universal-profile counts are pass / warn / fail / error.

| Face | r1 | r2 | Interpolation findings |
| --- | --- | --- | --- |
| Sans | 91 / 5 / 5 / 1 | 92 / 4 / 5 / 1 | 0 → 0 |
| Serif | 95 / 5 / 5 / 0 | 95 / 5 / 5 / 0 | 4 kinks → 4 kinks |
| Mono | 90 / 6 / 5 / 1 | 90 / 6 / 5 / 1 | 0 → 0 |
| Sans Rounded | 90 / 1 / 4 / 1 | 91 / 0 / 4 / 1 | 0 → 0 |

The r2 column is the final build, after the key-letter, `&`, mono and
cap/figure moves. Its counts are the same as the build before those moves.

The serif's 4 kinks are the same upstream ones as in r1: dagger, daggerdbl
(×2) and f.ligalong. The warning drops on the sans (5 → 4) and Rounded
(1 → 0) are the profile's own interpolation warning clearing. Every other
warning, fail and error is the same check as in r1.

- **Clean results:**
  - no hard failures and no reserved names;
  - Name/RFN passes on all four faces;
  - core coverage is 258/258 for each text face and 29/29 for Rounded
    (Rounded also draws `&`, outside the required set);
  - icons pass (37);
  - the gate's figure checks show equal tabular widths in all four faces,
    and varied `pnum` widths in sans, serif and Rounded (the mono has no
    proportional figures).
- **Render.** 35 sheets, blind byte scan PASS. The headline collision check
  reports clear (0 components) on light, dark and glass. The closest ink
  between serif headline lines is 5.0 px on all three.
- **Quality status is FAIL**, the same as at the starting point, with the
  same failing checks (see next steps).

## Rules to keep

- Make every outline change as a transform from the baseline. Re-run
  `apply.py`; never patch a built UFO. Run the faces in the order sans,
  rounded, serif, mono, because the other three read the finished sans
  masters.
- Plan once on a reference master and apply to every master. Where a
  per-master cut lands at different curve points, transfer it by curve
  parameter, using the smallest share that clears the interpolation check.
- A rounds or fillet step must not add a kink. Check the pairs the gate
  compares, including Thin against Black for Rounded.
- Emboldening steps leave drawn boxes (`.notdef`) alone, and scale the gain
  for small forms.
- The default figures are tabular in every face, and `pnum` gives
  proportional figures. Run `checks/figcheck.py` after any figure or feature
  change.
- Rounded keeps the sans's advances and kerning for every glyph it draws.
  Run `checks/widths.py`; it fails above 1%.
- Rounded display and caption masters reuse the rounded text outlines and
  change only spacing (and, for caption, stem weight).
- Rounded bowls relax toward circular arcs and are never lengthened.
- Figures and figure separators never tighten at display sizes.
  Figure–period and figure–comma kerns never tighten, except after 7.
- Figure + degree and 1-pairs are kerned from outline profiles per master,
  not by hand values.
- Serif colour is judged by rendered density against the sans, at each
  optical size, on more than one sample.
- Serif line clearance comes from glyph depth and height, not from the
  harness or the line metrics, which stay shared across faces.
- The instance opsz keeps user sizes; only the design mapping moves.
- A key-letter move is its own function in `keys.py`, planned on one
  reference master. A move that bends curves runs under the kink check.
- When a default and its alternate swap drawings, the feature labels are
  renamed to describe what the feature now gives.
- Capitals and figures get their extra Black stroke per optical size. Judge
  it on "Age 0123" and on the paragraph together.

## Next steps

1. **Judge the identity moves by eye.** Compare them at text and display
   sizes against rendered reference images only. The settings are
   constants at the top of `keys.py`. 0 and 2 took only the extra squaring.
2. **Mono I and `||`** are unchanged. Some operator strokes keep their
   slanted ends:
   - the `>=` and `<=` chevrons, because a level cut on so shallow a stroke
     leaves a spike;
   - the chevron parts of `<*` `<+` `*>` `+>`, which the cut rule does not
     match.
3. **Mono 9 px step** (+39.3%) is still untraced.
4. **Serif display density** is 0.970–0.971 at 64–96 px against a 0.95 aim,
   and the 96 px paragraph step is +35.5%.
5. **Rounded at 400 / 24 px.** The rounding is clear at display sizes and in
   heavy weights. At Regular around 24 px it is subtler, because the radii
   scale with a thinner stem. Judge whether the text Regular needs a larger
   radius share.
6. **Mono alternates** (`ss03`, `ss05`, `zero`) are listed under Strata
   Mono. The sans alternates are listed under "Key letters and figures".
7. **Upstream structure.** These need build-pipeline or point-structure
   fixes, not outline work:
   - the remaining serif kinks (dagger, daggerdbl ×2, f.ligalong);
   - y.sups (sans) and j.sups (serif), which keep their original rounds;
   - the quality fails and errors, all unchanged from r1: nested and
     transformed components, smart dropout, fvar/STAT consistency, name
     lengths, duplicate instance names (sans), font version and default
     instance name IDs (serif), script tags (mono), and case mapping and
     whitespace glyphs (Rounded).

## Icons

No icon changes; icons belong to another designer. Builds, gates and renders
used the icon folder named in the brief, read-only. All 37 icons pass.

## Rebuild

    .venv/bin/python -I scripts/resource_guard.py -- .venv/bin/python -I candidates/r2-type/transforms/apply.py sans rounded serif mono
    make build CAND=r2-type SUBSET=core ICONS_DIR=<icon folder>
    make gate CAND=r2-type ICONS_DIR=<icon folder>
    make render CAND=r2-type OUT=<empty folder> MAP=<file outside OUT> ICONS_DIR=<icon folder>
    .venv/bin/python -I candidates/r2-type/checks/figcheck.py build/r2-type
    .venv/bin/python -I candidates/r2-type/checks/widths.py build/r2-type
