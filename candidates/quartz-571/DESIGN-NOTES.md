# Family design notes

This candidate makes the interface face quieter and more specific, gives weather
figures a deliberate rhythm, and brings the answer and data faces onto the same
vertical system. The editable masters remain the source of truth. All geometry
is derived from the workshop baseline and the candidate's own existing icons.
No proprietary outlines or font files are used.

## Sans

The text cut is slightly narrower through the body but has added side space and
a larger x-height. At the text master, horizontal scale is 0.978 with 11 units
added on either side, and vertical scale is 1.014. At display, horizontal scale
is 0.965, the side space is reduced by one unit, and vertical scale is 1.005.
This makes text more open without making headlines broad or blunt. Both axes
and all six master locations are retained.

The lower counter of a is enlarged, its shoulder exit opens, r has a shorter
arm, t extends its crossbar to the right, G has a shorter and lower crossbar,
and R has a slightly stronger outward leg. The shoulders of o, O, 0, 6 and 9
are fuller. The 1 is redrawn with a firm foot and angled flag; 4 has a more
open top. These are local changes to the licensed baseline, not substitutions
from another face. Text and display have their own spacing and pair adjustments.

Default lining figures are tabular through their Unicode mappings. The pnum
feature restores the proportional figures. The minus has exactly one figure's
advance and is vertically centred on lining figures. Degree is a newly drawn
ring, smaller than the baseline, with weight-dependent thickness and a compact
advance. Celsius and Fahrenheit are actual composed glyphs. The soft hyphen
gap is closed.

## Rounded

The supplemental designspace lives in fonts/sans-rounded/. It inherits the
completed Sans masters, spacing and axes. Figures, their tabular forms, degree,
the composed units, minus, percent, colon, period, and the C/F component shapes
are decomposed locally and rounded. The rest of the alphabet is the Sans design;
this is a numeric cut, not a claim that the whole alphabet is rounded.

One fixed corner mask is derived from the Regular master. Each selected corner
is shortened on both adjacent cubic segments, then joined with a tangent cubic
fillet whose radius tracks the actual minus thickness. Adjacent smooth handles
are paired symmetrically, so intermediate locations retain tangent continuity.
Axis-aligned joins retain their natural handle lengths. Fillet handles are
bounded by the trimmed segments, and paired handles use the shorter available
length; this prevents loops on short terminal segments. The open 4 is a simple
diagonal-and-crossbar polygon beside its separate upright, without a tiny bridge.
All masters receive identical segment structures. Circle extrema, counters,
advances and axis locations remain deliberate rather than being raster effects.

The standard builder accepts three faces only. The supplemental build script
therefore emits Rounded separately under build/quartz-571/rounded/, with its own
name and core TTF/WOFF2 files. The extra review sheets render that actual binary.

## Serif

Caps and lining figures rise to the Sans system. Lowercase uses a separate
scale: x-height targets are 0.562 em at optical 8, 0.542 at 20, and 0.518 at
60. Cap targets are 0.738 em in text and 0.731 in display. This retains a
crisper display cut while making answer text mix more naturally with Sans.
Widths and side space are adjusted modestly; the existing optical contrast and
kerning design are retained. Explicit legacy metric declarations are removed so
the new master metrics actually reach the binary.

Missing spaces, the nonbreaking hyphen, reversed quotation mark, fractions,
double arrows and temperature-unit glyphs are supplied. Four non-core diagnostic
glyphs retain baseline geometry to preserve the existing interpolation findings:
be.srb, dagger, daggerdbl, and f.ligalong. They need a separate drawing pass.

## Mono

The cell stays 1200 units. The x-height is 0.554 em and cap height is 0.738 em.
Body width is slightly reduced within the cell, and the bowl shoulders are
fuller, giving o/O/0 a more squared technical character without losing their
counters. Existing contextual and programming ligature rules are retained.

Five inherited bar-ligature component-order errors are repaired by reversing
the two bar components in the bold master. A compatible interpolated Regular
master at the existing weight mapping makes 400 the default; the 300–700 range
is retained. Missing core spaces, hyphens, primes, superscript i, fractions and
temperature units are supplied. Temperature units fit one cell. Unicode spaces
retain their typographic widths; ordinary text and figures retain their cells.
New reversed quotes mirror the right quotation mark; new primes slant their
strokes, so the coverage additions carry the intended punctuation shapes.

## Shared rules

Typographic and horizontal-header ascenders/descenders are 1.14/-0.36 em,
with zero line gap, and clipping reserves are 1.20/0.40 em. Keep these shared.
Keep figure-height relationships, tabular advances, the figure-width minus,
degree counter openness, and the optical separation when changing weights.
Keep component transforms consistent with each glyph's map; do not scale a
composite and its base twice. Do not add or remove points in only one master.

The 28 existing candidate icons use one 1.875-unit stroke with round caps and
joins. This gives a little more presence beside 13–17 px text than the earlier
1.75-unit set. Group order is preserved. Unsupported layer attributes are
removed for the workshop SVG contract; icon-layers.json in the work directory
records those groups for future tone application. The candidate contains its
own copy, and all builds use the same external icons directory.

Keep the bundled license and copyright notices verbatim. Renaming metadata
never replaces the notices. Do not add contributor identity to review artifacts.

## Reproduction and boundaries

Use the repository's isolated interpreter. Run the resource guard around
transforms/design.py; it reconstructs the font sources from baseline. Optional
face arguments allow a bounded repeat. Run transforms/stages.py build for the
standard make build, the supplemental Rounded build, make gate and the design
audit. Run transforms/stages.py render with an empty renders-self directory for
make render and the extra detail sheets. MAP.json stays outside that directory.

The candidate-owned workshop adapter changes only the standard builder's cache
destination to build/quartz-571/compile-cache. The root Makefile and all workshop
scripts stay unchanged. The resource guard remains enabled. No app integration,
upstream modification, network upload, or commit is part of this candidate.

## Remaining work

Review combining-mark placement and less common non-core scripts after the
height changes. A core build and the current review phrases cannot establish
full-script quality. Resolve the preserved Serif diagnostic glyphs deliberately.
Finish inherited font metadata and hinting quality work before a release build.
Assess the larger core payloads before choosing delivery budgets. The icon input
is the existing 28-symbol set, not the baseline's 272-symbol inventory; this round
does not establish coverage of the whole application's icon library. Recognition
of today/places and frozen precipitation still needs testing with ordinary users.

Small-size review on this machine is useful evidence, but it does not establish
Windows hinting, low-density Android rendering, or the final weather-app pairing.
The family weight match remains an optical judgment rather than a user study.

## Final gate and timing evidence

All three standard make stages completed with exit code 0. The shared
resource guard stayed enabled. The universal quality status is still FAIL;
the remaining failures and errors are visible rather than waived.

| Face | Core baseline → candidate | Interpolation glyphs baseline → candidate | Quality fails/errors baseline → candidate |
| --- | --- | --- | --- |
| Sans | 257 → 258 / 258 | 0 → 0 | 6/1 → 3/1 |
| Serif | 240 → 258 / 258 | 4 → 4 | 6/0 → 5/0 |
| Mono | 237 → 258 / 258 | 5 → 0 | 6/1 → 3/1 |

Hard failures: 0. All four binaries cover 258/258 core codepoints,
have tabular default figures and a figure-width minus, and pass reserved-name checks.
Proportional figures remain available in Sans, Serif and Rounded. Mono stays fixed.
Rounded interpolation findings: 0.
No interpolation findings were added beyond baseline. Coding ligatures activate
without changing the total cell advance. Icons and generated components pass.

Final face timings are wall times, including any mid-compile guard pause:

- Sans: 19.147 s; compile-cache hit false.
- Serif: 5.287 s; compile-cache hit true.
- Mono: 2.048 s; compile-cache hit true.
- Three-face build total: 26.569 s.
- Supplemental Rounded build: 18.081 s.
- Standard gate report: 62.255 s wall time; see gate-stage.log for guard pauses.
- Standard render: 26.094 s wall time; 26 sheets before extra details.
- Extra detail render: 3.183 s; final set 36 PNGs.

The first three-face cold build took 83.194 s wall time, including about 25 s
of memory-pressure waits; the face times summed to 58.053 s. The recorded
baseline build was cached (11.529 s), so it is not a cold-build speed comparison.
The final gate/render wall times include the scheduled forecast pause where logged.

Self-review output is in the work directory under renders-self/. MAP.json is
outside that folder. Its anonymous index identifies each sheet. Additional
sheets cover the actual Rounded binary, baseline/Sans comparison, outline
details, optical/weight extremes, family height relationships and icon pairing.
The final PNG byte/metadata audit passes.

Guard timings separate suspension from elapsed time:

| Stage | Elapsed seconds | Unpaused seconds | Suspended seconds |
| --- | ---: | ---: | ---: |
| build | 27.27 | 27.27 | 0.00 |
| rounded | 19.18 | 19.18 | 0.00 |
| gate | 62.62 | 62.62 | 0.00 |
| audit | 18.14 | 18.14 | 0.00 |
| render | 27.26 | 27.26 | 0.00 |
| details | 6.06 | 6.06 | 0.00 |

## Self-review decision

The final 36 PNGs were decoded and visually surveyed in four contact sheets.
Close review covered the text-size waterfalls on all four surfaces, weather
figures and tables, the answer card, coding ligatures, all 28 icons, outline
zooms, punctuation, family fit, small icon/text settings, and weight extremes.
The final numeral and Rounded outline sheets were reopened individually.

Review corrected pinched Rounded terminals, short-segment overshoot, the tiny
bridge at the top of 4, and a flag on 1 that was too heavy in Thin. The flag now
tracks stem weight. The chosen geometry is ready for blind comparison. The
remaining release and coverage limits above still apply; the universal quality
profile has not been made clean.

The self-review map is MAP.json in the work directory, outside renders-self/.
Sheets 27–28 show standard/Rounded numerals; 30–31 show clean outline zooms;
32 shows family fit; 33–34 show icon/text pairing; 35 shows optical/weight
extremes; 36 shows core punctuation. Earlier renders-iteration-* folders are
superseded review evidence and must not be substituted for renders-self/.

## Round 0 pipeline handoff

Rounded now lives at `fonts/sans-rounded/` and the standard build, gate and
render commands include it. Earlier supplemental paths and timing tables above
describe designer self-review only. The review set uses the unchanged finished
icon input, preserved in `review-icons/`; the external work folder remains
read-only. Generated font masters are ignored and rebuilt from baseline by
the transforms. No outline design was changed during pipeline integration.

Rebuild from the repo root with the isolated interpreter and resource guard:

    .venv/bin/python -I scripts/resource_guard.py -- .venv/bin/python -I candidates/quartz-571/transforms/design.py

    make build CAND=quartz-571 SUBSET=core ICONS_DIR=candidates/quartz-571/review-icons
    make gate CAND=quartz-571 ICONS_DIR=candidates/quartz-571/review-icons

Both transform entry points accept `--output-dir` for reproduction in a temporary
directory. The baseline always comes from this checkout.
