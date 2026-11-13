These scripts make every outline and metadata change in this candidate. They
start from `candidates/baseline/fonts` each time, so the result can be rebuilt
from the baseline alone. No glyph here was drawn by hand.

Run from the repository root:

    .venv/bin/python -I candidates/r3-type/transforms/apply.py          # all faces
    .venv/bin/python -I candidates/r3-type/transforms/apply.py serif    # one face
    make build CAND=r3-type SUBSET=core ICONS_DIR=<icon folder>

Three faces read the finished sans masters:

- Rounded is made from them.
- The serif sets its stroke colour against them.
- The serif and the mono place their weight steps against them.

So after changing `sans.py`, `keys.py`, `identity.py`, `optical.py` or `lib.py`, run all
faces (`apply.py`, or `apply.py sans rounded serif mono`), in that order.
Never run `rounded`, `serif` or `mono` alone on stale sans masters.

`apply.py` resets a face folder from the baseline, then runs that face's steps:

| Script | What it does |
| --- | --- |
| `hygiene.py` | Removes upstream product names left in the sans designspace and the serif features. Copyright lines and designer credits are untouched. |
| `identity.py` | The family trait, planned once on a reference master and carried to the others: axis-cut terminals with apertures opened at text sizes (`terminals`, with the reference master, master groups and text masters as arguments, so the mono can use it), squarer rounds (`rounds`, kink-checked, with the strength as an argument), the y tail and the R leg (the leg starts where the bowl's lower bar leaves the stem). A terminal trim that would leave a curve stub under `STUB` stems turns the cut onto the axis instead. A glyph whose rounds would add an interpolation kink keeps its rounds. |
| `keys.py` | Key letters, figures and the family's level-bar signature, each move planned on one reference master and carried to the others; moves that bend curves are kink-checked. Sans: a (larger bowl), g (level ear), t and f (bar leads right), r (slanted cut), y (straight tail, level cut), k (leg from the stem), G (longer bar), flat-top 3 and straight-stem 6 and 9 as defaults with relabelled alternates, steeper 7, and an extra squaring pass on 0 2 3 6 9 g (not the a, where it bent the bowl's top). `&` (sans, mono): the arm ends under a level bar (`amp_bar`). Mono: squarer a g l and dots, beakless r, straight y, flatter 1, level-cut operators and a level or-equal bar on `>=` and `<=`. |
| `optical.py` | Optical kerning for figures. Each gap is the mean clipped white between two outline profiles, so a pair is kerned to match a reference pair (0 0, or 0 and the degree ring). `pair_kerns` takes a floor: a share of the reference pair's bounding-box gap that no pair may close below. |
| `sans.py` | Display Regular made finer, then display Black re-mixed (`display_black`) so Black carries the same ink relative to Regular at display size as at text size. Then the identity steps: spurred G, open 4, the tailed l as the default l (`tailed_l`; the plain l moves to `cv05`/`salt`), the figure swaps from `keys.py`, the 6's flat step merged into one corner (`six_notch`), slanted t, terminals, y tail, R leg, the first squaring pass, a second taut pass (`TAUT`) and the `keys.py` shape moves. Then the figures: wider round figures, footed tabular 1, math signs centred on the figures, degree ring; the proportional 1 takes the tabular 1's drawing with its foot at `PNUM_FOOT` (`footed_pnum_one`). Spacing by `TRACK`: +6 per side at text size and −6 at display, with figures and figure separators keeping their room (`keeps_room`). `tabular_default` makes the tabular figures the default and moves the proportional figures to `.pnum` glyphs under `pnum`. Figure kerning comes after that, with `ONE_FLOOR`. `weight_map` writes the weight axis map. `caption` adds the opsz 8 caption masters (heavier stems, looser spacing). |
| `rounded.py` | Writes `fonts/sans-rounded/`: the finished sans, glyph for glyph, with a round pen on its corners, joins and stroke ends and nothing else changed (curves are the sans's curves). It covers Basic Latin, the weather extras (° % − ½ ¼ ¾ ℉ ℃ ± ⁄) and the figure, punctuation, thin and no-break spaces; every glyph keeps the advance and kerning the sans gives the same character, including the tabular default, `pnum`, the case forms and the `calt` rules that pick them. Corners are classified once on the Regular (`plan`): radii `R_CONVEX`, `R_CONCAVE` and `TERMINAL` in stems, cuts capped at `MAX_CUT`, micro-notches and cusps (`CUSP`) kept sharp, and no fillet swallows a line up to a corner kept sharp. The three text masters and the three caption masters are rounded, each from the sans master of the same name (the captions from the sans's emboldened caption outlines). The display masters reuse the text outlines, centred on the sans display advances, the display Regular moved `FINER` toward Thin as in the sans. Each master takes the sans's glyph categories (`public.openTypeCategories`), so spacing accents with attaching anchors stay base glyphs. The kink check (`kinks`) tests every master in source order and in the order the font checker walks the variable font (`VF_ORDER`), plus Thin against Black in each group, on the cubic outlines and on their quadratic conversion at the compiler's tolerance (`QUAD_ERR`). Where it finds a kink, or where a master's outline gains a kink over its sans master (`rough`), the curve cuts move part of the way toward the Regular's: the first pair of shares from `TRANSFER` (text masters, then caption masters) that clears both is kept. If no pair clears, the caption masters move part of the way back toward the text masters' rounded outlines (`GAIN`, the largest that clears; only ½ needs it). |
| `serif.py` | Scales the design by 1.09 to the sans cap height. It then raises the lowercase and shortens descenders and ascenders with a smooth vertical remap, applies the family's squarer rounds lightly, and adds the missing core glyphs. `colour_masters` sets each optical size's stroke weight against the sans (`COLOUR`, `BLACK_AT`); small forms take `SMALL` of the gain, and capitals and figures take `CAPFIG_BLACK` more in the Black masters. Finally it sets line metrics and the OS/2 block, remaps the weight axis by ink colour (`STEP_GAMMA`), and keeps the caption design to larger sizes. |
| `mono.py` | Puts the Bold master's parts in the Light master's order, squares the curves, scales to the sans x-height, remaps the weight axis, opens the triple-bar operators and adds the missing core glyphs. `at_amp_defaults` makes the closed-ring @, the conventional & and the dotted 0 the defaults, and moves the old forms to ss05, ss03 and zero. It then applies the family's squaring (`MONO_ROUNDS`) and axis-cut terminals, the mono drawing from `keys.py`, places Medium and SemiBold by ink (`ink_steps`) and sets line metrics. Last come the operator and dot details: minus = the plus's bar and hyphen at half a cell (`dashes`), `++` and `+++` drawn as separate plus signs (`separate_pluses`), and square dots (`square_dots`). |
| `tangency.py` | Runs after the sans, serif and mono steps. Joins that were tangent upstream, and corners a transform flattened into near-tangent joins, are made tangent again by turning handles; in the serif, short leads that the stroke gain turned around get their upstream direction back. A glyph whose realignment would add an interpolation kink between masters keeps its outlines from before this pass (the serif's dagger and double dagger). |
| `lib.py` | Shared geometry: bounds, decomposition, stem measurement, stem-compensated scaling, master mixing, corner fillets (with optional curve-parameter transfer from a reference master), curve tension, ellipses and line metrics. Also horizontal emboldening that keeps smooth points smooth (`embolden`), sample ink (`sample_glyphs`, `ink`) and the stroke gain that reaches a target ink (`solve_bold`), plus the sans weight map. |

Rules the scripts follow:

- Every master is changed by the same plan. Corners, terminals and curves are
  classified once on a reference master, and the same edit is applied
  everywhere, so masters stay compatible.
- Where a per-master quantity (a fillet cut, a terminal cut) would land at a
  different point of a curve in each master, the cut moves toward the curve
  parameter the reference master uses. It moves by the smallest share that
  keeps the interpolation check clean.
- A step that could add an interpolation finding checks itself and leaves the
  glyph unchanged rather than add one. The rounds step checks both rounded
  and raw point positions. The Rounded fillets also check Thin against Black,
  because the gate compares the display Black with the caption Thin.
- New glyphs that would need a flipped or rotated component are written as
  outlines, so they add no transformed components.
- A step must not add kinks, fold-backs or points against the upstream:
  `checks/outlines.py` compares every glyph with the upstream glyph that
  holds its drawing (`com.strata.source` in the glyph lib when a transform
  moved a drawing to another name).
- A step that expects a particular outline or feature block asserts it and
  stops if the baseline changes. Examples are the mono triple bar, the mono
  `&&` and `~@` lookups, the 14-point serif right arrow and the sans figure
  set.
