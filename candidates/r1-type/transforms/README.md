These scripts make every outline and metadata change in this candidate. They
start from `candidates/baseline/fonts` each time, so the result can be rebuilt
from the baseline alone. No glyph here was drawn by hand.

Run from the repository root:

    .venv/bin/python -I candidates/r1-type/transforms/apply.py          # all faces
    .venv/bin/python -I candidates/r1-type/transforms/apply.py serif    # one face
    make build CAND=r1-type SUBSET=core ICONS_DIR=<icon folder>

Rounded reads the finished sans masters, so after changing `sans.py` or
`identity.py` run `apply.py sans rounded` (or all faces), never `rounded`
alone.

`apply.py` resets a face folder from the baseline, then runs that face's steps:

| Script | What it does |
| --- | --- |
| `hygiene.py` | Removes upstream product names left in the sans designspace and the serif features. Copyright lines and designer credits are untouched. |
| `identity.py` | The family trait, planned once on the sans Regular text master and applied to every master: axis-cut terminals with apertures opened at text sizes, squarer (slightly superelliptic) rounds, a vertical cut at the end of the y tail, and an R leg that springs from the middle of the bowl's lower bar. A glyph whose rounds would add an interpolation kink keeps its original rounds. |
| `optical.py` | Optical kerning for figures. Each gap is the mean clipped white between two outline profiles, so a pair is kerned to match a reference pair (0 0, or 0 and the degree ring). |
| `sans.py` | Spurred G and open 4 by default, slanted t top, wider round figures, footed tabular 1, math signs centred on the figures, degree ring, figure kerning (figure + degree, 1-pairs, figure–period), opsz-dependent tracking, a finer display Regular, soft hyphen and line metrics. |
| `rounded.py` | Writes `fonts/sans-rounded/`: a numeric style made by filleting the sans Thin, Regular and Black text masters, with an opsz axis (the display masters reuse the text outlines and take the sans display spacing). Tabular figures in a narrower even cell, footed 1, proportional figures under `pnum`, kerning measured on the rounded outlines. |
| `build_rounded.py` | Compiles that designspace through the standard builder (the main build also includes it). |
| `serif.py` | Scales the design by 1.09 to the sans cap height, raises the lowercase and shortens descenders (a smooth vertical remap), applies the family's squarer rounds lightly, adds the missing core glyphs, sets line metrics and the OS/2 block, remaps the weight axis by ink colour and keeps the caption design to larger sizes. |
| `mono.py` | Puts the Bold master's parts in the Light master's order, squares the curves, scales to the sans x-height, remaps the weight axis, opens the triple-bar operators, adds the missing core glyphs and sets line metrics. |
| `lib.py` | Shared geometry: bounds, decomposition, stem measurement, stem-compensated scaling, master mixing, corner fillets (with optional curve-parameter transfer from a reference master), curve tension, ellipses and line metrics. |

Rules the scripts follow:

- Every master is changed by the same plan. Corners, terminals and curves are
  classified once (on the Regular master) and the same edit is applied
  everywhere, so masters stay compatible.
- Where a per-master quantity (a fillet cut, a terminal cut) would land at a
  different point of a curve in each master, the cut moves toward the curve
  parameter the Regular uses, by the smallest share that keeps the
  interpolation check clean.
- A step that could add an interpolation finding checks itself (rounded and
  raw point positions) and leaves the glyph unchanged rather than add one.
- New glyphs that would need a flipped or rotated component are written as
  outlines, so they add no transformed components.
- A step that expects a particular outline (for example the mono triple bar
  or the 14-point serif right arrow) asserts it and stops if the baseline
  changes.
