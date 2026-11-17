"""Strata Mono: matched to Strata Sans, squarer curves, missing core glyphs.

Masters: m00 Light (default), m01 Bold. Ligature and contextual features
are kept as they are, except that the closed-ring @, the conventional & and
the dotted 0 are the defaults; the old forms (open @, Et-style & with its &&
ligature, the ~@ ligature, the slashed 0) move to ss05, ss03 and zero.

Its own drawing, shared with Strata Sans: rounds squared harder than the
sans's (MONO_ROUNDS on top of the first squaring pass), and the family's
axis-cut terminals (identity.terminals), so C G J Q S, a c e f g j l r s t y
and 2 5 end flat on a horizontal or vertical cut (3 6 9 cannot be cut
compatibly in both masters and keep their ends). A third squaring pass
(MONO_SQUARE) on the round letters and figures, the mono drawing from
keys.py, and the operator and dot details: the minus is the plus's bar
(as wide, on the math axis) and the hyphen half a cell (`dashes`); `++`
and `+++` are separate plus signs (`separate_pluses`); dots are squared
(`square_dots`); the temperature units pair the degree sign's own ring, round, at 0.705-0.74
of its height and 0.95 of its walls, with a condensed full-height letter at
least 0.66 of the face's F or C, fitted to what follows (`add_glyphs`, TEMP_R7, TEMP_MODE). Operator ligatures are
opt-in (dlig and ss11; `opt_in_ligatures`).
"""
import math
import re
from pathlib import Path
from fontTools.misc.transform import Transform
from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2.objects import Component, Contour, Point
import lib
import identity
import keys
from serif import scale_font, new_glyph

# x-height 0.53846 em -> 0.5459 em (Strata Sans)
S = 0.5459 / 0.53846
TENSION = 0.2
# Second, kink-checked squaring pass (identity.rounds), harder than the sans.
MONO_ROUNDS = 0.30
# Same left/right order in both masters (the Bold master listed these parts right to left).
REORDER = ['bar_bar_equal_end.seq.cv30', 'bar_bar_equal_middle.seq.cv30', 'bar_bar_equal_start.seq.cv30',
           'bar_bar_hyphen_end.seq.cv30', 'bar_bar_hyphen_middle.seq.cv30']
USER_W = [300, 400, 500, 600, 700]
# The upstream glyph that holds a glyph's drawing (outline checks).
SOURCE_KEY = 'com.strata.source'


def reorder_components(masters):
    for f in masters.values():
        for n in REORDER:
            g = f[n]
            comps = sorted(g.components, key=lambda c: (c.baseGlyph, c.transformation[4]))
            g.clearComponents()
            for c in comps:
                g.components.append(c)


def square_curves(masters):
    for f in masters.values():
        for g in f:
            for c in g.contours:
                lib.tension_contour(c, TENSION)


def h_stem(f):
    return lib.stem_width(f['H'], f.info.capHeight * 0.25) / f.info.unitsPerEm


def align_weights(masters):
    """Light stays put; Bold is re-mixed so each user weight matches Strata
    Sans at the same Light-to-Sans ratio, and the axis map follows."""
    light, bold = h_stem(masters['m00']), h_stem(masters['m01'])
    ratio = light / lib.sans_stem(300)
    target_bold = ratio * lib.sans_stem(700)
    t = (target_bold - light) / (bold - light)
    t = max(0.0, min(1.0, t))
    a, b = masters['m00'], masters['m01']
    for g in list(b):
        ga = a[g.name]
        if not lib.same_structure(ga, g):
            continue
        ng = lib.lerp_glyph(ga, g, t)
        g.clearContours()
        for c in ng.contours:
            g.contours.append(c)
        for cb, cn in zip(g.components, ng.components):
            cb.transformation = cn.transformation
        for ab, an in zip(g.anchors, ng.anchors):
            ab.x, ab.y = an.x, an.y
        g.width = ng.width
        lib.round_glyph(g)
    d_light, d_bold = 62, 62 + t * (158 - 62)
    stems = [(d_light, light), (d_bold, light + t * (bold - light))]
    mp = {}
    for w in USER_W:
        target = min(max(ratio * lib.sans_stem(w), stems[0][1]), stems[1][1])
        mp[w] = round(lib.inverse_piecewise(target, stems), 1)
    mp[300], mp[700] = d_light, round(d_bold, 1)
    return mp


def ink_steps(masters, mp, sans_folder):
    """Medium and SemiBold placed by ink: their ink relative to Regular
    matches Strata Sans text (opsz 14) at the same weights, so 400 -> 600
    darkens by the same share in both faces. Light, Regular and Bold keep
    their stem-matched places."""
    import ufoLib2
    sans = {m: ufoLib2.Font.open(Path(sans_folder) / f'StrataSans-{m}.ufo') for m in ('m00', 'm02', 'm04')}
    upm = sans['m02'].info.unitsPerEm
    stops = [(100, 'm00'), (400, 'm02'), (900, 'm04')]
    s_ink = {d: lib.ink(*lib.sample_glyphs(sans[m], lib.INK_SAMPLE), upm) for d, m in stops}

    def sans_ink(w):
        d = lib.piecewise(w, lib.SANS_WGHT_MAP)
        return lib.piecewise(d, sorted(s_ink.items()))
    mupm = masters['m00'].info.unitsPerEm
    m_ink = [(mp[300], lib.ink(*lib.sample_glyphs(masters['m00'], lib.INK_SAMPLE), mupm)),
             (mp[700], lib.ink(*lib.sample_glyphs(masters['m01'], lib.INK_SAMPLE), mupm))]
    i400 = lib.piecewise(mp[400], m_ink)
    for w in (500, 600):
        target = i400 * sans_ink(w) / sans_ink(400)
        target = min(max(target, m_ink[0][1]), m_ink[1][1])
        mp[w] = round(lib.inverse_piecewise(target, m_ink), 1)
    seq = [mp[w] for w in USER_W]
    assert all(a < b for a, b in zip(seq, seq[1:])), mp
    return mp


def write_designspace(path, mp):
    ds = DesignSpaceDocument.fromfile(path)
    ax = ds.axes[0]
    ax.map = sorted(mp.items())
    names = {'Light': 300, 'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700}
    for s in ds.sources:
        if s.styleName == 'Bold':
            s.location = {'Weight': mp[700]}
    for i in ds.instances:
        i.designLocation = {'Weight': mp[names[i.styleName]]}
    ds.write(path)


# ------------------------------------------------------------------ operators

# The === and !== ligatures draw three long bars. At 13-17 px (and in Bold,
# where the gaps were narrower than the bars) they ran together, so the outer
# bars move out by SPREAD bar heights.
# The !== ligature read as a not-equal sign followed by a spare "=": its
# slash crossed only the middle third of three cells of bars. It is now one
# sign across the three cells: its own bars, inset NOT_INSET of a cell at
# each end so the sign has ends like a single symbol, and a slash that
# travels NOT_TRAVEL cells across and NOT_RISE times the stretched height,
# keeping its stroke thickness (measured square to the stroke).
SPREAD = 0.5
NOT_INSET = 0.22
NOT_TRAVEL = 1.0
NOT_RISE = 1.05
TRIPLE = 'equal_equal_equal.liga'
NOT_TRIPLE = 'exclam_equal_equal.liga'
SLASH = '_part.not_equal'


def open_triple_bars(masters):
    for f in masters.values():
        bars = sorted(f[TRIPLE].contours, key=lambda c: min(p.y for p in c.points))
        assert len(bars) == 3 and all(len(c.points) == 4 for c in bars), 'triple bar outline changed'
        t = max(p.y for p in bars[0].points) - min(p.y for p in bars[0].points)
        d = SPREAD * t
        for p in bars[0].points:
            p.y -= d
        for p in bars[2].points:
            p.y += d
        g = f[NOT_TRIPLE]
        comps = list(g.components)
        slash = [c for c in comps if c.baseGlyph == SLASH]
        assert len(slash) == 1, 'not-identical ligature changed'
        assert [c.baseGlyph for c in comps if c.baseGlyph != SLASH] == [TRIPLE], 'not-identical ligature changed'
        g.clearComponents()
        inset = NOT_INSET * f['zero'].width
        x_lo = min(p.x for p in bars[0].points)
        for bar in bars:
            pts = [Point(p.x + inset if p.x == x_lo else p.x - inset, p.y, p.type) for p in bar.points]
            g.contours.append(Contour(points=pts))
        tmp = f[SLASH].copy()
        tmp.clearContours()
        lib.copy_contours(f[SLASH], tmp, Transform(*slash[0].transformation))
        (c,) = tmp.contours
        pts = sorted(c.points, key=lambda p: p.y)
        lo = ((pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2)
        hi = ((pts[2].x + pts[3].x) / 2, (pts[2].y + pts[3].y) / 2)
        ax = lib.sub(hi, lo)
        u = lib.unit(ax)
        k = 1 + 2 * d / ax[1]
        mid = lib.mul(lib.add(lo, hi), 0.5)
        for p in c.points:
            v = lib.sub((p.x, p.y), mid)
            q = lib.add(mid, lib.add(v, lib.mul(u, (k - 1) * lib.dot(v, u))))
            p.x, p.y = q
        # one sign across the three cells: longer travel, same thickness
        # (measured square to the stretched stroke)
        ends = sorted(c.points, key=lambda p: p.y)
        bl, br = sorted(ends[:2], key=lambda p: p.x)
        tl, tr = sorted(ends[2:], key=lambda p: p.x)
        edge = lib.unit((tl.x - bl.x, tl.y - bl.y))
        t = abs(lib.cross((br.x - bl.x, br.y - bl.y), edge))
        y0, y1 = (bl.y + br.y) / 2, (tl.y + tr.y) / 2
        my = (y0 + y1) / 2
        travel, rise = NOT_TRAVEL * f['zero'].width, NOT_RISE * (y1 - y0)
        w = t / math.sin(math.atan2(rise, travel))
        yb, yt = my - rise / 2, my + rise / 2
        xb, xt = mid[0] - travel / 2, mid[0] + travel / 2
        for pair, y, x in ((ends[:2], yb, xb), (ends[2:], yt, xt)):
            left, right = sorted(pair, key=lambda p: p.x)
            left.x, left.y = x - w / 2, y
            right.x, right.y = x + w / 2, y
        g.contours.append(c)
        lib.round_glyph(g)
        lib.round_glyph(f[TRIPLE])


# ------------------------------------------------------------------ new glyphs

def cell(f):
    return f['zero'].width


def ring(cx, top, D, tv, th):
    cy = top - D / 2
    return [lib.ellipse(cx, cy, D / 2, D / 2, True), lib.ellipse(cx, cy, D / 2 - tv, D / 2 - th, False)]


def condensed(fm, fp, name, target_w, stem_m, stem_p):
    """Glyph `name` narrowed to an ink width, stems held by moving toward the
    partner master (clamped, so Bold ends a little lighter)."""
    gm, gp = fm[name].copy(), fp[name].copy()
    lib.decompose(fm, gm); lib.decompose(fp, gp)
    b = lib.bounds(gm)
    sx = min(1.0, target_w / (b[2] - b[0]))
    g = lib.scale_compensated(gm, gp, sx, 1.0, stem_m, stem_p, clamp=(-0.3, 1.0))
    return g


# Temperature units in one cell. One mono cell cannot hold the mono's own
# degree sign and a full-size letter side by side, so the letter gives up
# width, never height: it is the face's finished C or F at full cap height,
# condensed in x and emboldened back to its own stem (`temp_letter`), so its
# stems and bars keep the face's weight in every master.
# The ring keeps the degree sign's counter (TEMP_COUNTER of its width and
# height) with thinner walls (TEMP_WALL of the degree sign's side and top
# walls). Ring and letter keep TEMP_GAP_PX of nearest ink between them at
# TEMP_PX (Euclidean, so a round letter may tuck under the ring).
# Placements built and measured (DESIGN-NOTES, section 1), as
# (edges, ring top, wall share) in TEMP_MODES:
#   'side'      ring at the top left, pair inside TEMP_MARGIN of the cell
#               each side, ring top on the figures' top, walls TEMP_WALL;
#   'hang'      ring on the cell's left edge (over the letter's left
#               sidebearing), letter flush with the right edge;
#   'tuck'      ring raised to the degree sign's own top so a round letter
#               tucks under it, walls TEMP_WALL_TUCK, pair inside TEMP_MARGIN;
#   'hangtuck'  'hang' edges with the 'tuck' ring.
# TEMP_MODE is the one kept.
TEMP_MODE = 'round3'
TEMP_MARGIN = 0.02
TEMP_COUNTER = 0.865
TEMP_WALL = 0.60
TEMP_WALL_TUCK = 0.50
TEMP_GAP_PX = 1.05
TEMP_PX = 13
TEMP_STEP = 4.0
TEMP_MODES = {'side': ('margin', 'figure', TEMP_WALL), 'hang': ('cell', 'figure', TEMP_WALL),
              'tuck': ('margin', 'degree', TEMP_WALL_TUCK), 'hangtuck': ('cell', 'degree', TEMP_WALL_TUCK)}


def temp_letter(f, name, sx, square=False):
    """The finished glyph `name`, condensed to sx in x about its left ink
    and emboldened back by the stem it lost, so its stems keep their
    thickness; heights and horizontal strokes are untouched.
    square (r9): the face's vertical terminal cuts stay vertical. The
    embolden's miter limit moves a cut's inner corner (a sharp turn) less
    than its outer one, so a condensed C's cuts leaned out into spurs that
    overhung the cut by up to 70 units at Bold; the outer corner (with its
    handle) goes back over the inner one."""
    g = f[name].copy()
    lib.decompose(f, g)
    b = lib.bounds(g)
    y = f.info.capHeight * (0.25 if name == 'F' else 0.5)
    stem = lib.stem_width(g, y)
    cuts = _vertical_cuts(g) if square else []
    for c in g.contours:
        for p in c.points:
            p.x = b[0] + (p.x - b[0]) * sx
    lib.embolden(g, stem * (1 - sx))
    for ci, i, j in cuts:
        pts = g.contours[ci].points
        a, z = pts[i], pts[j]
        inner, outer = (i, j) if a.x <= z.x else (j, i)
        d = pts[inner].x - pts[outer].x
        n = len(pts)
        step = 1 if (outer - inner) % n == 1 else -1
        handle = (outer + step) % n
        pts[outer].x += d
        if pts[handle].type is None:
            pts[handle].x += d
    nb = lib.bounds(g)
    lib.shift_glyph(g, b[0] - nb[0], 0)
    return g


def _vertical_cuts(g):
    """(contour, i, j) for each straight vertical segment between on-curve
    points i -> j on the glyph's right half (the letter's terminal cuts)."""
    b = lib.bounds(g)
    out = []
    for ci, c in enumerate(g.contours):
        pts = c.points
        n = len(pts)
        for i, p in enumerate(pts):
            q = pts[(i + 1) % n]
            if p.type and q.type == 'line' and abs(p.x - q.x) < 0.5 and abs(p.y - q.y) > 1 \
                    and p.x > (b[0] + b[2]) / 2:
                out.append((ci, i, (i + 1) % n))
    return out


def _jaw_shift(g, d):
    """Shift the C's lower right (below its middle, right of its middle)
    left by d at the terminal cut, ramping to 0 at the letter's middle, so
    the lower terminal ends d short; heights and strokes are unchanged."""
    b = lib.bounds(g)
    ym, xa, xb = (b[1] + b[3]) / 2, (b[0] + b[2]) / 2, b[2]
    for c in g.contours:
        for p in c.points:
            if p.y < ym and p.x > xa:
                p.x -= d * min(1.0, (p.x - xa) / (xb - xa))


def shorten_jaw(g, dx, fpts, fit):
    """The C's lower terminal gives way to what follows (a slash's foot):
    the smallest _jaw_shift, in 2-unit steps, that keeps `fit` from the
    follower points (letter at +dx). Returns the shift."""
    base = g.copy()
    d = 0.0
    while True:
        h = base.copy()
        _jaw_shift(h, d)
        if nearest([(x + dx, y) for x, y in ink_points(h)], fpts) >= fit:
            break
        d += 2.0
        assert d < 300, 'jaw does not clear'
    for c, hc in zip(g.contours, h.contours):
        for p, q in zip(c.points, hc.points):
            p.x = q.x
    return d


def _part(g, ci):
    h = g.copy(); h.clearContours(); h.contours.append(g.contours[ci]); return h


def ink_points(glyph, step=TEMP_STEP):
    """Points along every contour, about `step` units apart."""
    out = []
    for c in glyph.contours:
        segs = lib.to_segments(c)
        start = segs[-1]['end']
        for s in segs:
            pts = [start] + s['ctrl'] + [s['end']]
            if len(pts) == 4:
                n = max(2, int(lib.curve_length(pts) / step))
                out += [lib.bez(*pts, i / n) for i in range(n)]
            else:
                a, b = pts[0], pts[-1]
                n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
                out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
            start = s['end']
    return out


def clear_shift(left_pts, right_pts, gap):
    """Smallest x shift of right_pts that leaves every point at least `gap`
    from left_pts and to its right."""
    need = -1e9
    for rx, ry in left_pts:
        for px, py in right_pts:
            dy = abs(py - ry)
            if dy < gap:
                need = max(need, rx - px + math.sqrt(gap * gap - dy * dy))
    return need


def nearest(a_pts, b_pts):
    return min(math.hypot(ax - bx, ay - by) for ax, ay in a_pts for bx, by in b_pts)


def temp_unit(f, base, mode='hangtuck'):
    """Contours of ℃ (base C) or ℉ (base F) in one cell, and the letter's
    condensing factor."""
    W = cell(f)
    em = f.info.unitsPerEm
    gap = TEMP_GAP_PX * em / TEMP_PX
    cw, ch, wv, wh = degree_parts(f)
    edges, ring_top, wall = TEMP_MODES[mode]
    tv, th = wall * wv, wall * wh
    ow, oh = TEMP_COUNTER * cw + 2 * tv, TEMP_COUNTER * ch + 2 * th
    if ring_top == 'degree':
        top = lib.bounds(f['degree'], f)[3]
    else:
        top = f.info.capHeight + 0.012 * em
    lo_edge, hi_edge = (0.0, W) if edges == 'cell' else (TEMP_MARGIN * W, W - TEMP_MARGIN * W)
    ring = oval_ring(lo_edge + ow / 2, top, ow, oh, tv, th)
    tmp = f['degree'].copy(); tmp.clearContours(); tmp.clearComponents()
    for c in ring:
        tmp.contours.append(c)
    rpts = [p for p in ink_points(tmp) if p[0] > lo_edge + ow / 2]

    def place(sx):
        lt = temp_letter(f, base, sx)
        lpts = ink_points(lt)
        dx = clear_shift(rpts, [p for p in lpts if p[0] < lib.bounds(lt)[0] + 0.6 * (lib.bounds(lt)[2] - lib.bounds(lt)[0])], gap)
        return lt, dx, lib.bounds(lt)[2] + dx

    lo, hi = 0.3, 1.0
    if place(hi)[2] > hi_edge:
        for _ in range(24):
            mid = (lo + hi) / 2
            if place(mid)[2] <= hi_edge:
                lo = mid
            else:
                hi = mid
        sx = lo
    else:
        sx = hi
    lt, dx, right = place(sx)
    shift = 0.0 if edges == 'cell' else (hi_edge - right) / 2
    out = f['degree'].copy(); out.clearContours(); out.clearComponents()
    for c in oval_ring(lo_edge + shift + ow / 2, top, ow, oh, tv, th):
        out.contours.append(c)
    lib.copy_contours(lt, out, Transform(1, 0, 0, 1, dx + shift, 0))
    return out, sx


# r7: the ring is the face's own degree sign. r6's ring was a drawn ellipse
# with 0.865 of the degree sign's counter and half its walls; on the rendered
# sheet it measured about 0.75 of the typed degree sign across and half its
# wall weight, so it read light and cramped beside a composed °F. Here the
# ring is the degree sign's own two contours, each scaled about the degree
# sign's centre: the outer contour to RING_H of its height and RING_W of its
# width, the inner one so that the walls keep WALL of the degree sign's side
# and top walls. Its top stays at the degree sign's top. The letter is r6's
# (the face's C or F at full cap height, condensed in x and emboldened back
# to its stem), at TEMP_GAP_PX of nearest ink from the ring at TEMP_PX.
# A full ring and a 1 px gap leave too little of the cell for the letter, so
# the constructions trade the cell's edges and the ring's width:
#   hang    the ring's left ink HANG of a cell left of the cell's edge, over
#           the left sidebearing; the letter ends on the right edge;
#   narrow  the ring on the cell's left edge (as r6), the letter narrower;
#   oval    a ring a little narrower than the degree sign (RING_W < RING_H),
#           hanging HANG of a cell; the letter may pass the right edge by
#           OVER of a cell (a unit is followed by a space or nothing);
#   graded  'oval' with the hang per master: the Light ring hangs, the Bold
#           ring sits on the cell's edge, because the Bold figure before the
#           unit leaves the least room. A ring hanging a whole cell-share at
#           Bold came within a quarter pixel of a 0 or 7 at 13 px. Its Bold
#           letter kept 0.58 (F) and 0.63 (C) of the face's F and C across,
#           and at 13 px the Bold C read as a parenthesis;
#   graded2 'graded' with a narrower Bold ring (RING_W 0.80, still RING_H tall
#           with WALL walls) and the Bold letter OVER 0.08 of a cell past the
#           right edge, which gives the Bold letter back r6's width (F 0.67,
#           C 0.72 of the face's F and C);
#   graded3 between the two (Bold RING_W 0.82): Bold F 0.66, C 0.70.
#   inset   (kept) measured in the renderer at 16 sub-pixel positions (2x),
#           graded2's 1.05 px design gap read under 1 px at 25-75 % of the
#           positions at 13 px (down to 0.50 px; r6's ring, 0.62), because
#           the renderer's anti-aliasing darkens edges past the outline; and
#           its hanging Light ring came within 0.50 px of a 0 before it (r6:
#           1.00). 'inset' takes GAP 1.20 px, puts the Light ring on the
#           cell's edge and the Bold ring 0.03 of a cell inside it, narrows
#           the ring to 0.82 (Light) and 0.77 (Bold) of the degree sign's
#           width (still RING_H tall, WALL walls) and lets the letter pass
#           the right edge by 0.07 / 0.10 of a cell. Rendered at 13 px: gap
#           at least 1.00 px and at least 1.00 px from a 0 before it at every
#           position and weight; letter F 0.73 / 0.66, C 0.75 / 0.70 of the
#           face's F and C (Regular / Bold).
# Values may be per master ({master: value}; `temp_at`). GAP (px at TEMP_PX)
# defaults to TEMP_GAP_PX, the gap the earlier constructions were built at.
# TEMP_MODE names the construction kept; TEMP_MODES above are r6's.
TEMP_R7 = {
    'hang': dict(RING_H=0.93, RING_W=0.93, WALL=0.97, HANG=0.10, OVER=0.0),
    'narrow': dict(RING_H=0.93, RING_W=0.93, WALL=0.97, HANG=0.0, OVER=0.0),
    'oval': dict(RING_H=0.93, RING_W=0.84, WALL=0.97, HANG=0.06, OVER=0.04),
    'graded': dict(RING_H=0.93, RING_W=0.86, WALL=0.97, HANG={'m00': 0.06, 'm01': 0.0}, OVER=0.05),
    'graded2': dict(RING_H=0.93, RING_W={'m00': 0.86, 'm01': 0.80}, WALL=0.97, HANG={'m00': 0.06, 'm01': 0.0}, OVER={'m00': 0.05, 'm01': 0.08}),
    'graded3': dict(RING_H=0.93, RING_W={'m00': 0.86, 'm01': 0.82}, WALL=0.97, HANG={'m00': 0.06, 'm01': 0.0}, OVER={'m00': 0.05, 'm01': 0.08}),
    'inset': dict(RING_H=0.93, RING_W={'m00': 0.82, 'm01': 0.77}, WALL=0.97, HANG={'m00': 0.0, 'm01': -0.03}, OVER={'m00': 0.07, 'm01': 0.10}, GAP=1.20),
    # r8 letter-width trials (DESIGN-NOTES, item 3). Both keep the advance,
    # place the ring as 'inset' does, and fit the letter to what follows a
    # unit: the letter grows until it reaches OVER of a cell past the right
    # edge or comes within FIT px (at TEMP_PX) of an en dash or slash in the
    # next cell (the F; TEMP_FOLLOW). ARM: the F's middle arm alone gives way to the dash (it
    # shortens to keep FIT), so the top bar sets the letter's width.
    #   fit    'inset''s ring, OVER 0.12;
    #   small  a smaller ring (0.82 of the degree sign's height; 0.72 / 0.68
    #          of its width, Light / Bold; walls 0.95) and the same letter.
    'fit': dict(RING_H=0.93, RING_W={'m00': 0.82, 'm01': 0.77}, WALL=0.97, HANG={'m00': 0.0, 'm01': -0.03}, OVER=0.12, GAP=1.20, FIT=1.20, ARM=True),
    'small': dict(RING_H=0.82, RING_W={'m00': 0.72, 'm01': 0.68}, WALL=0.95, HANG={'m00': 0.0, 'm01': -0.03}, OVER=0.12, GAP=1.20, FIT=1.20, ARM=True),
    # r9 (kept). A round ring with air, and a letter fitted to what follows.
    #   ring    RING_W 'round': as wide as it is tall (RING_H of the degree
    #           sign's height: 0.80 Light, 0.77 Bold), walls WALL 0.95 of
    #           the degree sign's; Light on the cell's edge, Bold 0.01 of a
    #           cell inside it (a figure before it keeps >= 1 px).
    #   gap     GAP 1.65 px at 13 px: the renderer reads 3 blank pixels at
    #           2x (1.50 px) at every phase for the F's straight stem and
    #           at least 1.30 px for the C's round shoulder.
    #   letter  fitted to an en dash and a slash in the next cell (FIT, px
    #           at 13 px, per master and follower) and to OVER of a cell
    #           past the right edge (F 0.12, C 0.10). The F's middle arm
    #           gives way to the dash (ARM) but keeps ARM_MIN 0.55 of the
    #           top bar; where it cannot (Bold), the F's fit to the dash
    #           drops to 0.75 px, so Bold `℉–` keeps clear space without
    #           the 1 px. The C is fitted whole (its lower terminal meets a
    #           slash's foot), and its terminal cuts stay vertical (SQUARE).
    'round': dict(RING_H={'m00': 0.80, 'm01': 0.77}, RING_W='round', WALL=0.95, HANG={'m00': 0.0, 'm01': -0.01},
                  OVER={'F': 0.12, 'C': 0.10}, GAP=1.65,
                  FIT={'m00': {'endash': 1.40, 'slash': 1.50}, 'm01': {'endash': 0.75, 'slash': 1.35}},
                  ARM=True, ARM_MIN=0.55, SQUARE=True, FOLLOW={'F': ('endash', 'slash'), 'C': ('endash', 'slash')}),
    # r9 revision (kept). 'round' left the C at 0.47-0.58 of the mono C, its
    # arms closing up so it read as "(", and the Bold F at 0.55. Width now
    # comes first: each letter is at least 0.66 of the mono letter at every
    # weight, and the C's opening stays at least 0.85 of the mono C's.
    # Width was taken from the gap and the ring, in that order:
    #   gap     GAP 1.40 px Light, 1.35 px Bold (was 1.65);
    #   ring    RING_H 0.74 Light, 0.705 Bold of the degree sign's height
    #           (was 0.80 / 0.77), still round; walls 0.95 of the degree
    #           sign's, the Bold top wall 0.87 (WALL side/top) because a
    #           smaller ring renders its top wall heavier at 13-15 px;
    #   fits    per letter (FIT {'F': .., 'C': ..}): Light 1.40 px for the
    #           F, 1.45 px for the C; Bold 1.00 / 1.10 px (dash / slash) for
    #           the F and 0.85 px for the C. The Bold F's arm keeps
    #           ARM_MIN 0.50 of the top bar so the dash fit can be 1.00 px
    #           (worst phase rendered: 0.50 px at 13 px, 1.00 px elsewhere).
    # OVER is unchanged. The C's cuts stay vertical (SQUARE); at 0.66 or
    # more of the mono C the arms keep their opening, so no terminal redraw
    # was needed.
    'round2': dict(RING_H={'m00': 0.74, 'm01': 0.705}, RING_W='round',
                   WALL={'m00': 0.95, 'm01': {'side': 0.95, 'top': 0.87}}, HANG={'m00': 0.0, 'm01': -0.01},
                   OVER={'F': 0.12, 'C': 0.10}, GAP={'m00': 1.40, 'm01': 1.35},
                   FIT={'m00': {'F': {'endash': 1.40, 'slash': 1.40}, 'C': {'endash': 1.45, 'slash': 1.45}},
                        'm01': {'F': {'endash': 1.00, 'slash': 1.10}, 'C': {'endash': 0.85, 'slash': 0.85}}},
                   ARM=True, ARM_MIN={'m00': 0.55, 'm01': 0.50}, SQUARE=True,
                   FOLLOW={'F': ('endash', 'slash'), 'C': ('endash', 'slash')}),
    # r10 (kept): see temp_unit8 and the DESIGN-NOTES.
    # WALL 0.39 in both masters: at 400 the side wall is about 57 units, 1.46
    # px at 50 px/em. The browser renders it about 0.48 raster px heavier, so
    # the soft wall stays under 1.99 px and no sub-pixel phase gives a 3 px
    # run on the sheet-09 middle scanline (gray < 140).
    'round3': dict(RING_H={'m00': 0.74, 'm01': 0.705}, RING_W='round', WALL=0.39,
                   HANG={'m00': 0.0, 'm01': -0.01}, GAP={'m00': 1.30, 'm01': 1.25}, WIDTH=0.80, SQUARE=True,
                   ARM=1.20, SHIFT={'m00': {'endash': 60, 'slash': 80}, 'm01': {'endash': 120, 'slash': 160}}),
}
# Followers the letter is fitted to, per letter. The C keeps OVER only: its
# open lower right meets a following slash's foot below the baseline at any
# useful width (Bold, 'inset' ring: 153 units, under 1.2 px, even at 0.3 of
# its width), so a C fitted to the slash would shrink to nothing.
TEMP_FOLLOW = {'F': ('endash', 'slash'), 'C': ()}


def temp_at(k, m):
    """Construction k with per-master values (dicts keyed by master) read for m."""
    def at(v):
        if isinstance(v, dict) and v and all(re.fullmatch(r'm\d\d', x) for x in v):
            return at(v[m])
        if isinstance(v, dict):
            return {x: at(y) for x, y in v.items()}
        return v
    return {key: at(v) for key, v in k.items()}


def degree_ring(f, k):
    """The degree sign's two contours scaled to construction k, its top at
    the degree sign's top; returns (contours, bounds)."""
    g = f['degree'].copy()
    lib.decompose(f, g)
    assert len(g.contours) == 2, 'degree changed'
    pairs = sorted(((_cbounds(c), c) for c in g.contours), key=lambda b: b[0][0] - b[0][2])
    (o, oc), (i, ic) = pairs
    cx, cy = (o[0] + o[2]) / 2, (o[1] + o[3]) / 2
    A, B = (o[2] - o[0]) / 2, (o[3] - o[1]) / 2
    tv = ((i[0] - o[0]) + (o[2] - i[2])) / 2
    th = ((i[1] - o[1]) + (o[3] - i[3])) / 2
    icx, icy = (i[0] + i[2]) / 2, (i[1] + i[3]) / 2
    ia, ib = (i[2] - i[0]) / 2, (i[3] - i[1]) / 2
    rw, rh, wall = k['RING_W'], k['RING_H'], k['WALL']
    # WALL: one share for both walls, or {'side': .., 'top': ..} (r9 revision).
    wall_s, wall_t = (wall['side'], wall['top']) if isinstance(wall, dict) else (wall, wall)
    if rw == 'round':
        rw = rh * B / A
    kia, kib = (rw * A - wall_s * tv) / ia, (rh * B - wall_t * th) / ib
    dy = o[3] - (cy + rh * B)
    for p in oc.points:
        p.x, p.y = cx + (p.x - cx) * rw, cy + (p.y - cy) * rh + dy
    for p in ic.points:
        p.x = cx + (icx - cx) * rw + (p.x - icx) * kia
        p.y = cy + (icy - cy) * rh + (p.y - icy) * kib + dy
    return [oc, ic], _cbounds(oc)


def temp_unit7(f, base, k):
    """Contours of ℃ (base C) or ℉ (base F) for an r7 construction, and the
    letter's condensing factor."""
    W = cell(f)
    em = f.info.unitsPerEm
    gap = k.get('GAP', TEMP_GAP_PX) * em / TEMP_PX
    ring, rb = degree_ring(f, k)
    rx = -k['HANG'] * W - rb[0]
    tmp = f['degree'].copy(); tmp.clearContours(); tmp.clearComponents()
    for c in ring:
        tmp.contours.append(c)
    lib.shift_glyph(tmp, rx, 0)
    mid = rb[0] + rx + (rb[2] - rb[0]) / 2
    rpts = [p for p in ink_points(tmp) if p[0] > mid]
    over = k['OVER'][base] if isinstance(k['OVER'], dict) else k['OVER']
    hi_edge = W + over * W
    follow = k.get('FOLLOW', TEMP_FOLLOW)[base]
    fit = k.get('FIT') if follow else None
    # FIT may be given per letter ({'F': .., 'C': ..}, r9 revision).
    if isinstance(fit, dict) and base in fit:
        fit = fit[base]
    arm = bool(k.get('ARM')) and base == 'F'
    jaw = tuple(k.get('JAW', ())) if base == 'C' else ()
    square = bool(k.get('SQUARE'))
    # FIT: px at TEMP_PX, one value or one per follower glyph.
    fit_of = (lambda n: (fit[n] if isinstance(fit, dict) else fit) * em / TEMP_PX)
    groups, jpts = [], []
    if fit:
        for n in follow:
            g = f[n].copy()
            lib.decompose(f, g)
            pts = [(x + W, y) for x, y in ink_points(g)]
            if n in jaw:
                jpts += pts
            else:
                groups.append((fit_of(n), pts))
    fpts = [p for _, pts in groups for p in pts]

    def place(sx):
        lt = temp_letter(f, base, sx, square)
        lb = lib.bounds(lt)
        lpts = ink_points(lt)
        dx = clear_shift(rpts, [p for p in lpts if p[0] < lb[0] + 0.6 * (lb[2] - lb[0])], gap)
        return lt, dx, lb[2] + dx

    def clears(sx):
        lt, dx, right = place(sx)
        keep = f_without_arm(lt) if arm else lt
        pts = [(x + dx, y) for x, y in ink_points(keep)]
        return [nearest(pts, gp) for _, gp in groups]

    # The letter grows until it comes nearer a follower than its FIT, or
    # than its narrowest form already is (the stem's place is set by the
    # ring and the gap, not by the letter's width).
    need = [min(ft, c - 0.5) for (ft, _), c in zip(groups, clears(0.3))] if groups else []

    arm_min = k.get('ARM_MIN')

    def fits(sx):
        lt, dx, right = place(sx)
        if right > hi_edge:
            return False
        if not all(c >= n for c, n in zip(clears(sx), need)):
            return False
        if arm and arm_min and groups:
            # the shortened middle arm keeps ARM_MIN of the top bar
            h = lt.copy()
            shorten_arm(h, dx, fpts, min(ft for ft, _ in groups))
            return arm_share(h) >= arm_min
        return True

    lo, hi = 0.3, 1.0
    if not fits(hi):
        for _ in range(24):
            m = (lo + hi) / 2
            if fits(m):
                lo = m
            else:
                hi = m
        sx = lo
    else:
        sx = hi
    lt, dx, right = place(sx)
    if arm and fit:
        shorten_arm(lt, dx, fpts, min(ft for ft, _ in groups))
    if jaw and fit:
        shorten_jaw(lt, dx, jpts, fit_of(jaw[0]))
    out = f['degree'].copy(); out.clearContours(); out.clearComponents()
    for c in tmp.contours:
        out.contours.append(c)
    lib.copy_contours(lt, out, Transform(1, 0, 0, 1, dx, 0))
    return out, sx


def temp_unit8(f, base, k):
    """Contours of ℃ (base C) or ℉ (base F) for an r10 construction (one
    width rule for both letters), and the letter's condensing factor. The
    ring is `degree_ring`'s; the letter is `temp_letter` at the condensing
    that gives its ink WIDTH of the face's own letter, GAP px (at TEMP_PX)
    of nearest ink right of the ring. What follows a unit is cleared by the
    contextual followers (`unit_followers`), not by narrowing the letter."""
    W = cell(f)
    em = f.info.unitsPerEm
    gap = k['GAP'] * em / TEMP_PX
    ring, rb = degree_ring(f, k)
    rx = -k['HANG'] * W - rb[0]
    tmp = f['degree'].copy(); tmp.clearContours(); tmp.clearComponents()
    for c in ring:
        tmp.contours.append(c)
    lib.shift_glyph(tmp, rx, 0)
    mid = rb[0] + rx + (rb[2] - rb[0]) / 2
    rpts = [p for p in ink_points(tmp) if p[0] > mid]
    ref = f[base].copy()
    lib.decompose(f, ref)
    rb0 = lib.bounds(ref)
    target = k['WIDTH'] * (rb0[2] - rb0[0])
    square = bool(k.get('SQUARE'))

    def place(sx):
        lt = temp_letter(f, base, sx, square)
        lb = lib.bounds(lt)
        lpts = ink_points(lt)
        dx = clear_shift(rpts, [p for p in lpts if p[0] < lb[0] + 0.6 * (lb[2] - lb[0])], gap)
        return lt, dx, lb[2] - lb[0]

    lo, hi = 0.3, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        if place(m)[2] >= target:
            hi = m
        else:
            lo = m
    sx = hi
    lt, dx, _ = place(sx)
    if base == 'F' and k.get('ARM'):
        # the F's middle arm keeps ARM px (at TEMP_PX) from the contextual
        # en dash in the next cell; its top bar sets the letter's width
        fol = unit_follower(f, 'endash', k['SHIFT']['endash'])
        shorten_arm(lt, dx, [(x + W, y) for x, y in ink_points(fol)], k['ARM'] * em / TEMP_PX)
    out = f['degree'].copy(); out.clearContours(); out.clearComponents()
    for c in tmp.contours:
        out.contours.append(c)
    lib.copy_contours(lt, out, Transform(1, 0, 0, 1, dx, 0))
    return out, sx


# r10: what follows a unit. The wider r10 letters reach further into the
# next cell, so an en dash or slash right after ℃ or ℉ takes a contextual
# form (calt, on by default, one glyph for one character) that starts
# later in its cell: the en dash's left end and the slash's foot move
# right by UNIT_FOLLOW_SHIFT units (per master); their right ends stay, so
# what comes after them keeps its space. Comma and period sit mid-cell and
# keep 2.5 px or more, so they have no contextual form.
UNIT_FOLLOWERS = ('endash', 'slash')
UNIT_FOLLOW_LOOKUP = 'unit_follow'


def unit_follower(f, name, shift):
    """The follower `name` starting `shift` units later in its cell: the en
    dash's left end, or the slash's lower end (its foot), moves right."""
    g = f[name].copy()
    lib.decompose(f, g)
    b = lib.bounds(g)
    for c in g.contours:
        for p in c.points:
            if name == 'slash':
                # the foot moves the most, the top not at all
                p.x += shift * max(0.0, min(1.0, (b[3] - p.y) / (b[3] - b[1])))
            elif p.x < (b[0] + b[2]) / 2:
                p.x += shift
    return g


def unit_followers(masters, mode=TEMP_MODE):
    """Add `<follower>.unit` glyphs (the construction's SHIFT, per master and
    follower) and the calt lookup that uses them."""
    shift = {}
    for m, f in masters.items():
        shift[m] = temp_at(TEMP_R7[mode], m)['SHIFT']
        for n in UNIT_FOLLOWERS:
            src = unit_follower(f, n, shift[m][n])
            g = new_glyph(f, f'{n}.unit', [], cell(f))
            lib.copy_contours(src, g)
            lib.round_glyph(g)
        fea = f.features.text
        assert UNIT_FOLLOW_LOOKUP not in fea
        rules = '\n'.join(f'    sub [uni2103 uni2109] {n}\' by {n}.unit;' for n in UNIT_FOLLOWERS)
        f.features.text = (fea.rstrip('\n') + f'\n\nlookup {UNIT_FOLLOW_LOOKUP} {{\n{rules}\n}} {UNIT_FOLLOW_LOOKUP};\n'
                           f'\nfeature calt {{\n    lookup {UNIT_FOLLOW_LOOKUP};\n}} calt;\n')
    return shift


def _arm_points(g):
    """The F's middle arm: its two right-hand corners (contour, index),
    the on-curve points right of the stem between the baseline and the top
    bar."""
    assert len(g.contours) == 1, 'F changed'
    pts = g.contours[0].points
    b = lib.bounds(g)
    stem_r = min(p.x for p in pts if p.type and b[1] + 1 < p.y < b[3] - 1)
    out = [i for i, p in enumerate(pts) if p.type and p.x > stem_r + 1 and 0.2 * b[3] < p.y < 0.7 * b[3]]
    assert len(out) == 2, f'F arm: {out}'
    return out


def arm_share(g):
    """The F's middle arm over its top bar, each measured from the stem."""
    pts = g.contours[0].points
    idx = _arm_points(g)
    b = lib.bounds(g)
    stem_r = min(p.x for i, p in enumerate(pts) if p.type and i not in idx and p.x > b[0] + 1)
    top = max(p.x for p in pts if p.y > b[3] - 1)
    return (pts[idx[0]].x - stem_r) / (top - stem_r)


def f_without_arm(g):
    """The F with its middle arm cut back to the stem (for the follower test)."""
    h = g.copy()
    pts = h.contours[0].points
    idx = _arm_points(h)
    stem_r = min(p.x for i, p in enumerate(pts) if p.type and i not in idx and p.x > lib.bounds(h)[0] + 1)
    for i in idx:
        pts[i].x = stem_r
    return h


def shorten_arm(g, dx, fpts, fit):
    """Move the F's middle arm's right end left until it keeps `fit` from
    the follower points (letter at +dx)."""
    pts = g.contours[0].points
    idx = _arm_points(g)
    x0 = pts[idx[0]].x
    while True:
        arm = [(pts[i].x + dx, pts[i].y) for i in idx]
        a, b = arm
        seg = [(a[0], a[1] + (b[1] - a[1]) * t / 8) for t in range(9)]
        if nearest(seg, fpts) >= fit:
            break
        for i in idx:
            pts[i].x -= 2.0
    return x0 - pts[idx[0]].x


def temp_units(masters, mode=TEMP_MODE):
    """Draw ℃ and ℉ (created empty by add_glyphs, so the glyph order stays)
    from the finished C and F of each master."""
    info = {}
    for m, f in masters.items():
        for name, base in (('uni2103', 'C'), ('uni2109', 'F')):
            if mode in TEMP_R7 and 'WIDTH' in TEMP_R7[mode]:
                src, sx = temp_unit8(f, base, temp_at(TEMP_R7[mode], m))
            elif mode in TEMP_R7:
                src, sx = temp_unit7(f, base, temp_at(TEMP_R7[mode], m))
            else:
                src, sx = temp_unit(f, base, mode)
            g = f[name]
            g.clearContours()
            lib.copy_contours(src, g)
            lib.round_glyph(g)
            info[(m, name)] = round(sx, 3)
    return info


def degree_parts(f):
    """Counter width and height and the side and top walls of the degree sign."""
    g = f['degree'].copy()
    lib.decompose(f, g)
    boxes = sorted((_cbounds(c) for c in g.contours), key=lambda b: b[0] - b[2])
    assert len(boxes) == 2, 'degree changed'
    o, i = boxes
    return i[2] - i[0], i[3] - i[1], ((i[0] - o[0]) + (o[2] - i[2])) / 2, ((i[1] - o[1]) + (o[3] - i[3])) / 2


def oval_ring(cx, top, ow, oh, tv, th):
    cy = top - oh / 2
    return [lib.ellipse(cx, cy, ow / 2, oh / 2, True), lib.ellipse(cx, cy, ow / 2 - tv, oh / 2 - th, False)]


def add_glyphs(masters):
    pairs = {'m00': 'm01', 'm01': 'm00'}
    stems = {m: h_stem(f) * f.info.unitsPerEm for m, f in masters.items()}
    for m, f in masters.items():
        p = masters[pairs[m]]
        W = cell(f)
        st = stems[m]
        for u in (0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2009, 0x200A, 0x202F):
            new_glyph(f, f'uni{u:04X}', [u], W)
        h = f['hyphen']
        if 0x2010 not in h.unicodes:
            h.unicodes = list(h.unicodes) + [0x2010]
        g = new_glyph(f, 'uni2011', [0x2011], W)
        g.components.append(Component('hyphen', Transform()))
        # reversed high quote
        ql = f['quoteleft']; flat = ql.copy(); lib.decompose(f, flat); b = lib.bounds(flat)
        g = new_glyph(f, 'uni201B', [0x201B], W)
        lib.copy_contours(flat, g, Transform(1, 0, 0, -1, 0, b[1] + b[3]), reverse=True)
        # primes: the straight quote leaned like a slash
        q = f['quotesingle']; bq = lib.bounds(q)
        lean = Transform(1, 0, 0.3, 1, -0.3 * bq[1], 0)
        def prime(dx):
            tmp = q.copy(); tmp.clearContours(); lib.copy_contours(q, tmp, lean)
            bb = lib.bounds(tmp)
            lib.shift_glyph(tmp, W / 2 - (bb[0] + bb[2]) / 2 + dx, 0)
            return tmp
        g = new_glyph(f, 'uni2032', [0x2032], W)
        lib.copy_contours(prime(0), g)
        g = new_glyph(f, 'uni2033', [0x2033], W)
        lib.copy_contours(prime(-0.14 * W), g)
        lib.copy_contours(prime(0.14 * W), g)
        # superscript i, sized like the superior figures
        one, sup = f['one'], f['onesuperior']
        bo, bs = lib.bounds(one, f), lib.bounds(sup, f)
        k = (bs[3] - bs[1]) / (bo[3] - bo[1])
        xh = f.info.xHeight
        vm = lib.stem_width(f['i'], xh * 0.5); vp = lib.stem_width(p['i'], p.info.xHeight * 0.5)
        gi = lib.scale_compensated(f['i'], p['i'], k, k, vm, vp, clamp=(-0.6, 1.0))
        bi = lib.bounds(gi)
        g = new_glyph(f, 'uni2071', [0x2071], W)
        lib.copy_contours(gi, g, Transform(1, 0, 0, 1, W / 2 - (bi[0] + bi[2]) / 2, bs[1] - bi[1]))
        # temperature units: created here so the glyph order stays, drawn by
        # temp_units from the finished C and F
        for name, uni in (('uni2103', 0x2103), ('uni2109', 0x2109)):
            new_glyph(f, name, [uni], W)
        # vulgar fractions from the one-third construction
        third = {c.baseGlyph: c.transformation[4] for c in f['onethird'].components}
        nx, fx, dx = third['one.numr'], third['_part.fraction'], third['three.dnom']
        for uni, den in ((0x2150, ['seven']), (0x2151, ['nine'])):
            g = new_glyph(f, f'uni{uni:04X}', [uni], W)
            g.components.append(Component('one.numr', Transform(1, 0, 0, 1, nx, 0)))
            g.components.append(Component('_part.fraction', Transform(1, 0, 0, 1, fx, 0)))
            g.components.append(Component(den[0] + '.dnom', Transform(1, 0, 0, 1, dx, 0)))
        # one-tenth: a narrowed "10" denominator, drawn as outlines
        g = new_glyph(f, 'uni2152', [0x2152], W)
        g.components.append(Component('one.numr', Transform(1, 0, 0, 1, nx - 0.03 * W, 0)))
        g.components.append(Component('_part.fraction', Transform(1, 0, 0, 1, fx - 0.03 * W, 0)))
        b3 = lib.bounds(f['three.dnom'], f)
        right = b3[2] + dx + 0.02 * W
        z = condensed(f, p, 'zero.dnom', 0.8 * (lib.bounds(f['zero.dnom'], f)[2] - lib.bounds(f['zero.dnom'], f)[0]),
                      st * 0.75, stems[pairs[m]] * 0.75)
        o = condensed(f, p, 'one.dnom', 0.8 * (lib.bounds(f['one.dnom'], f)[2] - lib.bounds(f['one.dnom'], f)[0]),
                      st * 0.75, stems[pairs[m]] * 0.75)
        bz, bo1 = lib.bounds(z), lib.bounds(o)
        zx = right - bz[2]
        lib.copy_contours(z, g, Transform(1, 0, 0, 1, zx, 0))
        ox = zx + bz[0] - 0.05 * W - bo1[2]
        lib.copy_contours(o, g, Transform(1, 0, 0, 1, ox, 0))
        for gg in f:
            if gg.name.startswith('uni2') and gg.name[3:7] in ('2032', '2033', '2071', '2152', '201B'):
                lib.round_glyph(gg)


# ------------------------------------------------------------------ @ and & defaults

# (default, alternate): the alternate's drawing becomes the default and the
# old default moves to the alternate name, which its stylistic set selects.
SWAP = [('at', 'at.ss05'), ('ampersand', 'ampersand.ss03'),
        ('zero', 'zero.zero'), ('zero.tosf', 'zero.tosf.zero')]
# Composites drawn from an old default keep it: glyph -> (old base, new base).
OLD_USERS = {'ampersand_ampersand.liga': ('ampersand', 'ampersand.ss03'),
             'ampersand_ampersand_ampersand.rem': ('ampersand', 'ampersand.ss03'),
             'zero.cv12': ('zero', 'zero.zero'), 'zero.tosf.cv12': ('zero.tosf', 'zero.tosf.zero')}
CALT_AMP = """lookup ampersand_ampersand {
  sub ampersand' ampersand by ampersand.before.ss03;
} ampersand_ampersand;"""
SS03 = """feature ss03 {
featureNames {
  name "Et ampersand";
};
lookup ampersand_et_pair {
  ignore sub ampersand.before.ss03' ampersand.before.ss03;
  ignore sub ampersand.before.ss03 ampersand.before.ss03' ampersand;
  sub ampersand.before.ss03' ampersand by ampersand.spacer;
} ampersand_et_pair;
lookup ampersand_et_liga {
  sub ampersand.spacer ampersand' by ampersand_ampersand.liga;
} ampersand_et_liga;
lookup ampersand_et {
  sub [ampersand ampersand.before.ss03] by ampersand.ss03;
} ampersand_et;
} ss03;"""
SS05 = """feature ss05 {
featureNames {
  name "Open at sign";
};
%s
lookup at_open {
  sub at by at.ss05;
} at_open;
} ss05;"""


def one(pattern, text):
    found = list(re.finditer(pattern, text, re.S))
    assert len(found) == 1, (pattern, len(found))
    return found[0]


def at_amp_defaults(masters):
    """Closed-ring @, conventional & and dotted 0 by default; old forms in
    ss05, ss03 and zero. In the default, && sets as two conventional &
    (the first one the upstream pair form); ~@ sets as ~ and @."""
    for f in masters.values():
        for a, b in SWAP:
            ga, gb = f[a], f[b]
            assert ga.width == gb.width and not ga.components and not gb.components
            ga.contours, gb.contours = list(gb.contours), list(ga.contours)
            ga.anchors, gb.anchors = list(gb.anchors), list(ga.anchors)
            sa, sb = ga.lib.get(SOURCE_KEY, a), gb.lib.get(SOURCE_KEY, b)
            ga.lib[SOURCE_KEY], gb.lib[SOURCE_KEY] = sb, sa
        for n, (old, new) in OLD_USERS.items():
            for c in f[n].components:
                if c.baseGlyph == old:
                    c.baseGlyph = new
        fea = f.features.text
        amp = one(r'lookup ampersand_ampersand \{.*?\} ampersand_ampersand;', fea)
        fea = fea[:amp.start()] + CALT_AMP + fea[amp.end():]
        at = one(r'\n[ \t]*lookup asciitilde_at \{.*?\} asciitilde_at;', fea)
        at_lookup = at.group(0).strip()
        fea = fea[:at.start()] + fea[at.end():]
        ss03 = one(r'feature ss03 \{.*?\} ss03;', fea)
        fea = fea[:ss03.start()] + SS03 + fea[ss03.end():]
        ss05 = one(r'feature ss05 \{.*?\} ss05;', fea)
        fea = fea[:ss05.start()] + SS05 % at_lookup + fea[ss05.end():]
        f.features.text = fea


# ------------------------------------------------------------------ operators and dots

# Hyphen width in cells; the minus is the plus without its upright.
HYPHEN_W = 0.50
# `++` and `+++`: separate plus signs, each pulled toward the group's middle
# by up to PLUS_PULL cells, never closer than PLUS_GAP bar thicknesses.
PLUS_PULL = 0.04
PLUS_GAP = 1.5
PLUS_LIGS = (('plus_plus.liga', 2), ('plus_plus_plus.liga', 3))


def plus_bar(f):
    """(left, bottom, right, top) of the plus sign's horizontal bar."""
    P = f['plus'].contours[0].points
    left = min(p.x for p in P)
    ys = [p.y for p in P if abs(p.x - left) < 1]
    return left, min(ys), max(p.x for p in P), max(ys)


def set_rect(contour, x0, y0, x1, y1):
    """A four-point rectangle moved to new edges, order and direction kept."""
    P = contour.points
    assert len(P) == 4 and all(p.type == 'line' for p in P), 'not a rectangle'
    cx = sum(p.x for p in P) / 4
    cy = sum(p.y for p in P) / 4
    for p in P:
        p.x = x0 if p.x < cx else x1
        p.y = y0 if p.y < cy else y1


def dashes(masters):
    """Minus = the plus's bar: as wide as the plus and on its axis, at its
    thickness. Hyphen = HYPHEN_W of the cell, centred, at its own height
    (its .lc and .case forms are components and follow)."""
    for f in masters.values():
        W = cell(f)
        x0, y0, x1, y1 = plus_bar(f)
        set_rect(f['minus'].contours[0], x0, y0, x1, y1)
        h = f['hyphen']
        b = lib.bounds(h)
        set_rect(h.contours[0], (W - HYPHEN_W * W) / 2, b[1], (W + HYPHEN_W * W) / 2, b[3])


def separate_pluses(masters):
    """`++` and `+++` were one joined outline whose bars ran into each other
    (read as H). Each is now separate copies of the plus, one per cell."""
    out = {}
    for m, f in masters.items():
        W = cell(f)
        x0, y0, x1, y1 = plus_bar(f)
        gap = W - (x1 - x0)
        pull = max(0.0, min(PLUS_PULL * W, (gap - PLUS_GAP * (y1 - y0)) / 2))
        out[m] = round(pull)
        for name, k in PLUS_LIGS:
            g = f[name]
            g.clearContours()
            centres = [W / 2 - (k - 1 - i) * W for i in range(k)]
            mid = sum(centres) / k
            for c in centres:
                dx = c - W / 2 + (pull if c < mid - 1 else -pull if c > mid + 1 else 0.0)
                lib.copy_contours(f['plus'], g, Transform(1, 0, 0, 1, dx, 0))
            g.lib[SOURCE_KEY] = 'plus'
    return out


# A second, stronger squaring of the round letters and figures (on top of
# MONO_ROUNDS): flat-sided, engineered rounds, the plain coding-face
# character judged from rendered images only. Kink-checked like the first.
MONO_SQUARE = 0.25
SQUARE_SET = ('o', 'c', 'e', 'b', 'd', 'p', 'q', 'n', 'h', 'm', 'u', 'O', 'C', 'D', 'G', 'Q', 'U',
              'zero', 'two', 'three', 'five', 'six', 'eight', 'nine')


# Dots: share of the way from each side's middle to the corner that the
# curve handles sit (a squarer dot, as on the mono's 0).
DOT_SQUARE = 0.90


def _cbounds(c):
    xs = [p.x for p in c.points]
    ys = [p.y for p in c.points]
    return min(xs), min(ys), max(xs), max(ys)


def _area(c):
    P = c.points
    return sum(P[i - 1].x * P[i].y - P[i].x * P[i - 1].y for i in range(len(P))) / 2


def _dot_contours(f):
    """(glyph, contour index) of every filled dot: a four-curve, twelve-point
    contour, about square, smaller than DOT_MAX of the cap height, wound
    like the glyph's largest contour, with no other contour inside it."""
    cap = f.info.capHeight
    out = []
    for g in f:
        cs = list(g.contours)
        if not cs:
            continue
        big = max(cs, key=lambda c: abs(_area(c)))
        sign = _area(big) > 0
        for i, c in enumerate(cs):
            P = c.points
            if len(P) != 12 or sum(p.type == 'curve' for p in P) != 4 or any(p.type == 'line' for p in P):
                continue
            x0, y0, x1, y1 = _cbounds(c)
            w, h = x1 - x0, y1 - y0
            if not h or not 0.8 <= w / h <= 1.25 or max(w, h) > 0.32 * cap or (_area(c) > 0) != sign:
                continue
            if any(j != i and _cbounds(o)[0] >= x0 and _cbounds(o)[2] <= x1 and _cbounds(o)[1] >= y0
                   and _cbounds(o)[3] <= y1 for j, o in enumerate(cs)):
                continue
            out.append((g.name, i))
    return out


def square_dots(masters, ref_name='m00'):
    picks = _dot_contours(masters[ref_name])
    done = []
    for name, i in picks:
        ok = True
        for f in masters.values():
            P = f[name].contours[i].points
            n = len(P)
            k = next(j for j in range(n) if P[j].type == 'curve')
            seg = [[P[(k + 3 * s + t) % n] for t in range(4)] for s in range(4)]
            for a, h1, h2, b in seg:
                if not ((abs(h1.y - a.y) < 2 and abs(h2.x - b.x) < 2) or (abs(h1.x - a.x) < 2 and abs(h2.y - b.y) < 2)):
                    ok = False
        if not ok:
            continue
        for f in masters.values():
            P = f[name].contours[i].points
            n = len(P)
            k = next(j for j in range(n) if P[j].type == 'curve')
            for s in range(4):
                a, h1, h2, b = [P[(k + 3 * s + t) % n] for t in range(4)]
                if abs(h1.y - a.y) < 2:   # leaves a horizontally, arrives vertically
                    cx, cy = b.x, a.y
                else:
                    cx, cy = a.x, b.y
                h1.x, h1.y = a.x + DOT_SQUARE * (cx - a.x), a.y + DOT_SQUARE * (cy - a.y)
                h2.x, h2.y = b.x + DOT_SQUARE * (cx - b.x), b.y + DOT_SQUARE * (cy - b.y)
        done.append(name)
    return done


# ------------------------------------------------------------------ ligatures opt-in

# r9: the operator ligatures are off by default. Every lookup of the `calt`
# ligature family moves to `dlig` and to stylistic set LIG_SET (the same
# lookups, in the same order, so either feature gives the r8 ligatures):
# the two- to four-character ligatures (rules that set `.spacer` and `.liga`
# glyphs: === !== == != <= >= ++ && :: ... www and the rest) and the
# arbitrary-length sequences (LIG_SEQ: => ==> <== and -> --> <-- arrows,
# ### and ___). `calt` keeps only the contextual forms that leave one glyph
# per character (CALT_KEEP: the && pair form ss03 needs, colons centred
# between < and >, the x in 0xFF, lowered operators between lowercase, the
# raised colon between capitals, the Greek capitals, the dotless i/j and
# l forms after f and capitals, and the two- and three-em dashes). Every
# lookup is defined once, at the place the calt block stood, so the lookup
# list and its order are r8's; only the features that reference them change.
LIG_SET = 'ss11'
LIG_SET_NAME = 'Operator ligatures'
LIG_SEQ = ('equal_arrows', 'hyphen_arrows', 'numbersigns', 'underscores')
CALT_KEEP = ('ampersand_ampersand', 'center', 'hexadecimal_x', 'calt_long_dashes', 'calt_salt_low',
             'caltGreekUCdiph', 'caltGreekUC', 'lowercase_hyphen', 'lowercase_plus', 'lowercase_asterisk',
             'lowercase_asteriskmath', 'uppercase_colon')
# Loose rules in the calt block become named lookups (same rules, same place).
CALT_LOOSE = {'twoemdash': 'calt_long_dashes', 'salt_low': 'calt_salt_low'}


def _calt_items(body):
    """Top-level items of the calt block: ('lookup', name, text) for each
    lookup block, ('rules', name, text) for each run of loose rules (named by
    CALT_LOOSE) and ('note', None, text) for comments and blank lines."""
    items, cur, loose = [], None, []

    def flush():
        if loose:
            text = '\n'.join(loose)
            names = {v for k, v in CALT_LOOSE.items() if k in text}
            assert len(names) == 1, ('unexpected loose calt rules', text)
            items.append(('rules', names.pop(), text))
            loose.clear()
    for ln in body.split('\n'):
        s = ln.strip()
        if cur is not None:
            cur[2].append(ln)
            if s == '} %s;' % cur[1]:
                items.append(('lookup', cur[1], '\n'.join(cur[2])))
                cur = None
            continue
        m = re.match(r'lookup (\w+) \{$', s)
        if m:
            flush()
            cur = ['lookup', m.group(1), [ln]]
        elif s and not s.startswith('#'):
            loose.append(ln)
        else:
            flush()
            items.append(('note', None, ln))
    assert cur is None, 'unterminated calt lookup'
    flush()
    return items


def _is_ligature(kind, name, text):
    if kind != 'lookup':
        return False
    outs = re.findall(r'\bby\s+([^;]+);', text)
    if any(re.search(r'\.(liga|spacer)\b', o) for o in outs):
        return True
    return name in LIG_SEQ


def opt_in_ligatures(masters):
    """Operator ligatures off by default, on under dlig and LIG_SET."""
    done = None
    for f in masters.values():
        fea = f.features.text
        block = one(r'\nfeature calt \{\n(.*?)\n\} calt;', fea)
        items = _calt_items(block.group(1))
        lig = [n for k, n, t in items if _is_ligature(k, n, t)]
        keep = [n for k, n, t in items if k != 'note' and not _is_ligature(k, n, t)]
        assert tuple(keep) == CALT_KEEP, keep
        assert all(n in lig for n in LIG_SEQ) and len(set(lig)) == len(lig)
        out = []
        for k, n, t in items:
            if k == 'rules':
                out.append(f'lookup {n} {{\n{t}\n}} {n};')
            else:
                out.append(t)
        refs = lambda names: '\n'.join(f'    lookup {n};' for n in names)
        out.append('\nfeature calt {\n' + refs(keep) + '\n} calt;')
        out.append('\nfeature dlig {\n' + refs(lig) + '\n} dlig;')
        out.append(f'\nfeature {LIG_SET} {{\nfeatureNames {{\n  name "{LIG_SET_NAME}";\n}};\n' + refs(lig) + f'\n}} {LIG_SET};')
        assert f'feature {LIG_SET} ' not in fea and 'feature dlig ' not in fea
        fea = fea[:block.start()] + '\n' + '\n'.join(out) + fea[block.end():]
        # aalt keeps collecting the moved lookups right where calt stood, so
        # its alternates (and the lookup list) stay r8's.
        aalt = one(r'\nfeature aalt \{.*?\n\} aalt;', fea)
        ref = one(r'\nfeature calt;', aalt.group(0))
        a = aalt.group(0)
        a = a[:ref.end()] + '\nfeature dlig;' + a[ref.end():]
        f.features.text = fea[:aalt.start()] + a + fea[aalt.end():]
        done = (len(lig), len(keep))
    return done


def run(masters, folder):
    reorder_components(masters)
    square_curves(masters)
    for f in masters.values():
        scale_font(f, S)
    mp = align_weights(masters)
    open_triple_bars(masters)
    add_glyphs(masters)
    at_amp_defaults(masters)
    print('mono ligatures moved to dlig and %s (lookups moved, kept in calt)' % LIG_SET, opt_in_ligatures(masters))
    print('mono squarer rounds', identity.rounds(masters, alpha=MONO_ROUNDS, ref_name='m00'))
    cut = identity.terminals(masters, identity.eligible(masters['m00']), ref_name='m00',
                             groups={'m00': ('m00', 'm01')}, text={'m00'})
    print('mono axis-cut terminals', len(cut), ' '.join(n for n in sorted(cut) if len(n) == 1 or n.isascii() and '.' not in n)[:400])
    keys.mono(masters)
    dashes(masters)
    print('mono ++ pull', separate_pluses(masters))
    names = [n for n in SQUARE_SET if n in masters['m00']]
    print('mono squarer round letters and figures', identity.rounds(masters, alpha=MONO_SQUARE, names=names, ref_name='m00'))
    dots = square_dots(masters)
    print('mono square dots', len(dots), ' '.join(sorted(set(n for n in dots if len(n) < 12)))[:300])
    print('mono temperature units', TEMP_MODE, temp_units(masters, TEMP_MODE))
    print('mono unit followers (calt)', unit_followers(masters, TEMP_MODE))
    mp = ink_steps(masters, mp, folder.parent / 'sans')
    lib.set_metrics(list(masters.values()), masters['m00'].info.unitsPerEm)
    write_designspace(folder / 'StrataMono.designspace', mp)
    print('mono weights', mp)
    return masters
