# r1-type design notes

Every change below is made by the scripts in `transforms/`, run from the
baseline sources (see `transforms/README.md`). Nothing was edited by hand in
the UFOs. Upstream copyright lines and designer credits are unchanged, and the
fonts stay under OFL 1.1. No outline was copied, traced or imported from any
reference font. Reference fonts were only looked at as rendered images.

This round starts from the previous round's candidate. Its decisions still
hold unless a section below changes them, in particular the shared line
metrics, the colour-matched weight maps, the mono interpolation fix, the
math signs centred on figures and the core coverage of 258/258. The notes
cover what changed and why.

## Strata Sans: identity

The aim is a calm grotesque: firm, quiet and engineered, with figures that
carry weather data. The outlines are the upstream sans's, re-cut. They do not
follow any reference outline.

- **Axis-cut terminals** (`identity.py`). Curved strokes that end in a
  straight cut are re-cut on an axis:
  - horizontal on c e s a g, C G S, 2 3 5 6 9;
  - vertical on t f r, which end while running sideways.

  The cut then moves back along the stroke to open the aperture. The opening
  is 36 units plus 0.40 stem in the text masters, and 0.08 stem in the
  display masters. Text sizes stay open and legible, and headlines stay
  closed and calm. The plan is made once on the Regular text master and
  carried to the other masters by curve parameter.
- **Squarer rounds.** Curve handles are pushed 20% toward their corners, so
  bowls, shoulders and round figures become slightly superelliptic. This is
  the trait the three faces share:
  - the serif uses the same operation at 10%;
  - the mono's earlier squaring (20%) is the same idea.

  If a glyph's rounds would add an interpolation kink, it keeps its original
  rounds. This applies to y.sups only.
- **y tail and R leg.**
  - The y's descender ends in a vertical cut, like t and f.
  - R's straight leg starts at the middle of the bowl's lower bar instead of
    its inner corner, which gives a wider, steadier stance (0.9 stem shift).
- **Open 4 by default.** The open-top 4 is the default in every size and
  style; `ss01` gives the closed 4. The open form separates 4 from 9 and A at
  small sizes and suits the calm, open figure set.
- **The display Regular is finer**: it moves 8% toward Thin (was 5%).

## Strata Sans: figures

- **Footed tabular 1.** The footless tabular 1 drew only about 62% of the
  zero's ink width (2.9 px against 4.7 px at 9 px) and left a hole in
  columns. The tabular 1 now:
  - keeps the upstream foot, widened 10% (its weight follows the master);
  - has its flag lengthened 12% along the outer edge;
  - is centred in the cell.

  Its ink is now 94% of the zero's (4.5 px against 4.7 px at 9 px).
  Tabular figures remain the default.
- **Proportional figures under `pnum`** for standalone numbers (hero
  temperatures). They are kerned optically (below).
- **Wider 2, 5 and 7.** Two and five widen 3% (was 2%), and seven widens
  5%. They read narrow next to the round figures once the 1 got its foot.
- **Optical figure kerning** (`optical.py`), measured per master on outline
  profiles:
  - **Figure + degree.** Every figure sits as far from the ring as 0 does,
    and never closer at its widest point. This covers the tabular and the
    proportional figures. The 4's arm no longer runs under the ring.
  - **Proportional 1-pairs.** 1 0, 0 1, 1 1, 1 4 and the rest get the same
    mean white as 0 0, clamped to −150…+40 units, and are never closer than
    0.8 of the 0 0 bounding gap.
  - **Period and comma between figures never tighten**, so "30.16" reads as
    30 . 16. Any negative kern between a figure and a period or comma is
    clamped to 0. The one exception is after 7, whose arm overhangs.
- **Degree sign opened.** Its left sidebearing grows from 56 + 0.10 stem to
  72 + 0.12 stem, and the figure + degree kerns hold that gap for every
  figure. In "104°F" the 4–ring gap on the weather sheet went from 0.5 px to
  7.0 px.

## Strata Sans Rounded (numeric style)

The goal was a face that reads as rounded at 24–32 px and on the card, and
that spaces like the regular.

- **Larger radii.**
  - Convex corners: 0.95 stem (was 0.46).
  - Concave joins: 0.48 stem (was 0.14).
  - Stroke ends shorter than 1.7 stems: full semicircles, as before.

  The joins on 1 4 7 % F C are now visibly soft at 24 px.
- **Softer bowls.** Each curve's handles shorten to 0.97 of a circular arc's
  handles for the same turn, and never lengthen. This undoes the squareness
  the sans adds. A ring that is already circular, such as the degree, stays
  round.
- **Spacing matches the regular.** Rounded now has the sans's opsz axis.
  - The display masters reuse the rounded text outlines, with the display
    Regular moved 8% toward Thin, and take the sans's display spacing.
  - Display outlines drawn from the sans display masters would cut terminals
    at other curve points, and the joins would kink between sizes.
  - At Regular, the proportional 7–2 gap is the same in em as the sans's.
- **Even tabular figures.**
  - The tabular cell is 0.925 of the sans cell, with 0.085 side room.
  - Every figure is condensed or widened, with stems kept, to between 0.95
    and 1.0 of the widest, so all ten fill the cell evenly.
  - The tabular 1 is the footed 1. Its ink is 98% of the zero's.
- **Kerning on the rounded outlines.** Figure + degree pairs for the tabular
  and proportional figures, plus proportional 1-pairs. At 96 px, the gaps in
  "104°F" (1–0, 0–4, 4–°, °–F) went from 29 / 12 / 9.5 / 15.5 px to
  8 / 7.5 / 7.5 / 12 px.
- **Compatible joins.** A stroke-end cap reaches further along its curve in
  heavier masters. The starting point already had 4 kinks, and the larger
  radii raised that to 10, at the inner joins of 3 5 6 9 between Thin and
  Regular.
  - Each master's fillet cuts now move part of the way toward the curve
    parameters the Regular uses.
  - The share is the smallest of 0, 0.25, 0.5, 0.75 and 1 that clears the
    check, which is 0.25.
  - Interpolation findings went from 4 to 0.

## Strata Serif

- **Bigger lowercase.** A smooth vertical remap raises the x-height of
  lowercase letters by 1.5% at caption, 4% at text and 5% at display. Ascender
  tops and the baseline stay put. The slope is unchanged at the baseline,
  x-height and ascender, so serifs keep their thickness.
  - Smooth points are re-smoothed after the remap.
  - Marks above lowercase bases follow the new x-height.
  - Default x-height: 0.518 → 0.539 em.
  - At 72 px (2× render), the headline e grew from 74.7 to 78.2 px. The mono
    e is 82.2 px.
- **Headline line clearance, fixed by glyph depth.**
  - Descenders (p q g y j) shorten by 14% of their depth, with a smooth taper.
  - The harness, line height and line gap are unchanged.
  - The closest ink between headline lines 1 and 2 (the q over the next f)
    went from 0.5 px to 2.5 px on light, dark and glass.
- **Sturdier small sizes.** The opsz axis maps 12 to design size 9 (8→8,
  12→9, 20→20, 60→60). Text at 9–12 px is drawn almost entirely from the
  caption masters, with their heavier hairlines and serifs.
  - Named instances keep their user sizes, so fvar and STAT agree.
- **Family trait.** The squarer rounds operation runs at 10%, planned on the
  text Regular. j.sups would gain a kink, so it is left unchanged.

## Strata Mono

- **Operators.** The === and !== ligatures drew three bars with gaps
  narrower than the bars in Bold, and they ran together at 13–17 px.
  - The outer bars move out by half a bar height.
  - The !== slash is stretched along its own axis to cover the taller stack,
    keeping its angle, thickness and overhang.
  - On a 2× render, the white between bars went from 3–4 px to 5 px.
  - => <= && || were already clear and are unchanged.
- **Unchanged:**
  - The zero is slashed and differs from O.
  - The 1 has a flag and a foot and differs from l and I.
  - The ligatures turn on and off cleanly (checked with `liga`/`calt` off on
    the code sheet).

## Icons

There are no icon changes here; icons belong to another designer. The
primary icon folder fails the icon contract (a custom `data-layer`
attribute), so builds, gates and renders use the fallback icon folder named
in the brief, read-only. All 28 icons pass.

## Gate versus starting point

Universal-profile counts are pass / warn / fail / error.

| Face | Starting point | This candidate | Interpolation findings |
| --- | --- | --- | --- |
| Sans | 91 / 5 / 5 / 1 | 91 / 5 / 5 / 1 | 0 → 0 |
| Serif | 95 / 5 / 5 / 0 | 95 / 5 / 5 / 0 | 5 kinks → 4 (be.srb cleared; dagger, daggerdbl ×2, f.ligalong are upstream) |
| Mono | 90 / 6 / 5 / 1 | 90 / 6 / 5 / 1 | 0 → 0 |
| Sans Rounded | 89 / 2 / 4 / 1 | 90 / 1 / 4 / 1 | 4 kinks → 0 |

- There are no hard failures and no reserved names. Name/RFN passes on all
  four faces.
- Core coverage is 258/258 for each text face and 29/29 for Rounded.
- The headline collision check reports 0 components on light, dark and glass.
- The quality status is FAIL, the same as at the starting point. The
  remaining failures are upstream structure (see next steps).

## Rules to keep

- Make every outline change as a transform from the baseline. Re-run
  `apply.py`; never patch a built UFO. Regenerate the sans before Rounded,
  because Rounded reads the sans masters.
- Plan once on the Regular and apply to every master. Where a per-master cut
  lands at different curve points, transfer it by curve parameter, using the
  smallest share that clears the interpolation check.
- A rounds step must not add a kink. Check both the rounded and the raw point
  positions, and leave the glyph unchanged if either count rises.
- Rounded display masters reuse the rounded text outlines and change only
  spacing.
- Rounded bowls relax toward circular arcs and are never lengthened.
- Figure–period and figure–comma kerns never tighten, except after 7.
  Separators are never tracked tighter at display sizes.
- Figure + degree and 1-pairs are kerned from outline profiles per master,
  not by hand values.
- Serif line clearance comes from glyph depth, not from the harness or the
  line metrics, which stay shared across faces.
- The instance opsz keeps user sizes; only the design mapping moves.

## Next steps

1. Hero numbers should request proportional figures (`font-variant-numeric:
   proportional-nums`). The card sheet renders Rounded with the default
   tabular figures, so its "72°" 7–2 gap is 9.5 px against 5.0 px for the
   regular. Down from 17.5 px, but not equal. In the font, proportional
   Rounded matches the sans.
2. Serif headline clearance is now 2.5 px at the harness line height. If the
   headline line height drops further, cut the descenders more rather than
   change the shared metrics.
3. The primary icon folder needs its `data-layer` attributes removed (or
   moved to the layer manifest) before it can replace the fallback icons.
4. y.sups (sans) and j.sups (serif) kept their original rounds. Fixing them
   needs a point-structure change upstream.
5. `ss01` now gives the closed 4. Document it with the other alternates.
6. Remaining interpolation kinks (serif dagger, daggerdbl ×2 and f.ligalong)
   and the quality FAILs are upstream:
   - nested and transformed components;
   - smart dropout;
   - fvar/STAT consistency;
   - name lengths;
   - mono script tags.

   They need build-pipeline fixes, not outline work.

## Rebuild

    .venv/bin/python -I scripts/resource_guard.py -- .venv/bin/python -I candidates/r1-type/transforms/apply.py
    make build CAND=r1-type SUBSET=core ICONS_DIR=<icon folder>
    make gate CAND=r1-type ICONS_DIR=<icon folder>
    make render CAND=r1-type OUT=<empty folder> ICONS_DIR=<icon folder>
