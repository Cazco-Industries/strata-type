These scripts make every outline and metadata change in this candidate. They
start from `candidates/baseline/fonts` each time, so the result can be rebuilt
from the baseline alone. No glyph here was drawn by hand.

Run from the repository root:

    .venv/bin/python -I candidates/lumen-146/transforms/apply.py          # all faces
    .venv/bin/python -I candidates/lumen-146/transforms/apply.py serif    # one face
    .venv/bin/python -I candidates/lumen-146/transforms/build_rounded.py  # Strata Sans Rounded binary
    make build CAND=lumen-146 SUBSET=core ICONS_DIR=<icon folder>

`apply.py` resets a face folder from the baseline, then runs that face's steps:

| Script | What it does |
| --- | --- |
| `hygiene.py` | Removes upstream product names left in the sans designspace and the serif features. Copyright lines and designer credits are untouched. |
| `sans.py` | Default capital G with spur, slanted t top, wider round figures, footless tabular one, math signs centred on the figures, new degree sign, opsz-dependent tracking, soft hyphen, line metrics. |
| `rounded.py` | Writes `fonts/sans-rounded/`: a numeric style made by filleting the sans Thin, Regular and Black masters. |
| `build_rounded.py` | Compiles that designspace, through the standard builder, including all four faces. |
| `serif.py` | Scales the design by 1.09 to the sans cap height, adds the missing core glyphs, sets line metrics and the OS/2 block, and remaps the weight axis to the sans steps. |
| `mono.py` | Puts the Bold master's parts in the Light master's order, squares the curves a little, scales to the sans x-height, remaps the weight axis, adds the missing core glyphs and sets line metrics. |
| `lib.py` | Shared geometry: bounds, decomposition, stem measurement, stem-compensated scaling, master mixing, corner fillets, curve tension, ellipses and line metrics. |

Rules the scripts follow:

- Every master is changed by the same plan. Corners and curves are classified
  once (on the Regular master for Rounded) and the same edit is applied
  everywhere, so masters stay compatible.
- New glyphs that would need a flipped or rotated component are written as
  outlines, so they add no transformed components.
- A step that expects a particular outline (for example the 14-point serif
  right arrow) asserts it and stops if the baseline changes.
