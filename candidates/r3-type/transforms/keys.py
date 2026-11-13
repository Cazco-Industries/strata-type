"""Key letters, figures and the family's level-bar signature.

The serif `&` caps its arm with a level bar. That bar is the family's
signature, and the moves here carry it, with straight strokes and taut
rounds, through the sans (and so into Rounded) and the mono:

- `&` (sans, mono): the arm rises toward the x-height and ends under a
  level bar that overhangs both sides of it (`amp_bar`).
- Figures (sans): the flat-top 3 and the straight-stem 6 and 9 become the
  defaults beside the open 4; the round forms move to the alternates
  (`swap_figures`), and the feature labels follow the drawings
  (`FEATURE_NAMES`). The 7's stem stands steeper (`seven_stem`). The round
  figures and g take an extra squaring pass (`FIG_TAUT`); the a does not
  (on the a it bent the bowl's top).
- t and f (sans): the crossbar leads to the right. Its left side keeps
  `BAR_LEFT` of its length past the stem; the t's right side grows by
  `T_RIGHT` (`crossbars`).
- y (sans, mono): a straight tail on the line of the right stroke, cut
  level at the descender (`y_straight`).
- r (sans): the arm ends on a slanted cut at the t's angle (`r_slant`).
- a (sans): a larger bowl; the bowl's top rises into the hook's counter
  (`a_bowl`).
- g (sans): a level ear on the stem top (`g_ear`).
- G (sans): a longer bar into the counter (`g_bar`).
- k (sans): the leg springs from the stem (`k_leg`); R's leg: `identity.r_leg`.
- Mono (`mono`): a g l and the dots take a stronger squaring pass
  (`MONO_TAUT`); the r loses its beak and takes the slanted cut
  (`r_beakless`); the 1's flag flattens (`one_flag`); `>=` and `<=` take a
  level or-equal bar (`level_or_equal`); slanted stroke ends on the
  operators become level cuts, except on strokes shallower than
  `MIN_ANGLE` (`level_ends`).

Every move is planned on one reference master (point indices, contour
choice) and applied to every master with that master's own measures, so
the point structure stays the same and the masters stay compatible. Moves
that could add an interpolation kink are checked with `identity.kinks` and
undone for that glyph if they would.
"""
import math
from ufoLib2.objects import Contour, Point
import lib
import identity

AMP_TOP = 0.80        # arm top, share of the x-height
AMP_LEFT = 0.45       # bar overhang left of the arm, share of the arm width
AMP_RIGHT = 0.35      # bar overhang right of the arm
AMP_BAR = 0.92        # bar thickness, share of the hyphen's thickness
BAR_LEFT = 0.45       # t and f bars: share of the left overhang kept
T_RIGHT = 1.20        # t bar: right overhang grows by this factor
SEVEN = 0.45          # 7 foot moves right by this many stems
FIG_TAUT = 0.25       # extra squaring of the figure bowls
A_BOWL = 0.28         # a: bowl top rises by this share of the hook counter
EAR = 0.50            # g ear length, stems
G_BAR = 0.60          # G bar grows left by this many stems
K_INTO = 0.10         # k leg top-left point sits this many stems into the stem
R_ANGLE = 0.43        # r cut: horizontal run per unit of cut height (t's angle)

SWAP = (('three', '.1'), ('six', '.ss01'), ('nine', '.ss01'))
FEATURE_NAMES = {
    'name "Open digits";': 'name "Classic digits";',
    'name "Open four";': 'name "Closed four";',
    'name "Open six";': 'name "Curved six";',
    'name "Open nine";': 'name "Curved nine";',
    'name "Flat-top three";': 'name "Round-top three";',
}


# ------------------------------------------------------------------ helpers

def stem(font):
    return identity.stem(font)


def on_points(contour):
    return [i for i, p in enumerate(contour.points) if p.type is not None]


def x_at(p, q, y):
    """x of the line through p and q at height y."""
    if q[1] == p[1]:
        return p[0]
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def hbar(font):
    b = lib.bounds(font['hyphen'], font)
    return b[3] - b[1]


def guarded(masters, name, move):
    """Run move(); undo it for this glyph if it adds an interpolation kink."""
    before = identity._points(masters, name)
    k0 = identity.kinks(masters, name)
    move()
    k1 = identity.kinks(masters, name)
    if any(a > b for a, b in zip(k1, k0)):
        identity._restore(masters, name, before)
        print(f'keys: {name} left unchanged (would kink)', flush=True)
        return False
    return True


def rename_features(masters, table):
    for f in masters.values():
        if f.features.text:
            for a, b in table.items():
                f.features.text = f.features.text.replace(a, b)


# ------------------------------------------------------------------ & bar

def amp_arm(glyph, xh):
    """Indices (contour, outer top, inner top) of the &'s arm top: the
    highest level pair of corner points right of the glyph's middle and
    below the x-height."""
    b = lib.bounds(glyph)
    mid = (b[0] + b[2]) / 2
    best = None
    for ci, c in enumerate(glyph.contours):
        pts = c.points
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            p, q = pts[i], pts[j]
            if p.type is None or q.type is None or p.smooth or q.smooth:
                continue
            if abs(p.y - q.y) > 0.08 * xh or min(p.x, q.x) < mid or min(p.y, q.y) < 0.25 * xh or max(p.y, q.y) > xh:
                continue
            if abs(p.x - q.x) > 0.25 * xh:
                continue
            if best is None or max(p.y, q.y) > best[0]:
                outer, inner = (i, j) if p.x > q.x else (j, i)
                best = (max(p.y, q.y), ci, outer, inner)
    assert best is not None, f'{glyph.name}: no level arm top found'
    return best[1:]


def amp_bar(masters, names, ref_name, top=AMP_TOP):
    """The serif's level bar on the &'s arm. The arm's two top points and
    their handles rise to `top` of the x-height; a bar contour, as thick as
    the font's horizontal strokes, caps the arm and overhangs both sides."""
    ref = masters[ref_name]
    for name in names:
        ci, oi, ii = amp_arm(ref[name], ref.info.xHeight)
        bar_like = None
        for f in masters.values():
            g = f[name]
            c = g.contours[ci]
            po, pi = c.points[oi], c.points[ii]
            y_new = top * f.info.xHeight
            n = len(c.points)
            # the arm's top points rise to one level; the handles that lead
            # into them rise with them
            for k in (oi, ii):
                dy = y_new - c.points[k].y
                for d in (-1, 1):
                    h = c.points[(k + d) % n]
                    if h.type is None:
                        h.y += dy
                c.points[k].y = y_new
            w = abs(po.x - pi.x)
            left = min(po.x, pi.x) - AMP_LEFT * w
            right = max(po.x, pi.x) + AMP_RIGHT * w
            t = AMP_BAR * hbar(f)
            yt = po.y
            pts = [Point(right, yt, 'line'), Point(left, yt, 'line'),
                   Point(left, yt - t, 'line'), Point(right, yt - t, 'line')]
            if bar_like is None:
                bar_like = orientation(c)
            if area(pts) * bar_like < 0:
                pts = [pts[0]] + pts[1:][::-1]
            g.contours.append(Contour(points=pts))


def area(pts):
    s = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        s += a.x * b.y - b.x * a.y
    return s / 2


def orientation(contour):
    pts = [p for p in contour.points if p.type is not None]
    return 1 if area(pts) > 0 else -1


# ------------------------------------------------------------------ figures

def figure_pairs(font):
    pairs = []
    for base, mark in SWAP:
        for n in sorted(font.keys()):
            if not (n == base or n.startswith(base + '.')):
                continue
            if '.ss01' in n or n.startswith(base + '.1'):
                continue
            for alt in (n + '.ss01', n.replace(base, base + mark, 1), n + mark):
                if alt != n and alt in font:
                    pairs.append((n, alt))
                    break
    return pairs


def swap_figures(masters, swap_alternates):
    pairs = figure_pairs(masters['m02'])
    assert ('three', 'three.1') in pairs and ('six', 'six.ss01') in pairs and ('nine', 'nine.ss01') in pairs
    swap_alternates(masters, pairs)
    rename_features(masters, FEATURE_NAMES)
    return [a for a, _ in pairs]


def seven_stem(masters):
    """The 7's foot moves right, so its stem stands steeper."""
    ref = masters['m02']
    name = next(n for n in ('seven', 'seven.pnum') if n in ref and ref[n].contours)

    def move():
        for f in masters.values():
            c = f[name].contours[0]
            feet = sorted(on_points(c), key=lambda i: c.points[i].y)[:2]
            assert all(abs(c.points[i].y) < 2 for i in feet), '7 outline changed'
            for i in feet:
                c.points[i].x += SEVEN * stem(f)
    guarded(masters, name, move)
    return name


# ------------------------------------------------------------------ t and f

def crossings(font, glyph, y, skip):
    """x where the glyph's outline (decomposed, without contour `skip`)
    crosses height y."""
    g = glyph.copy()
    lib.decompose(font, g)
    xs = []
    for ci, c in enumerate(g.contours):
        if ci == skip and len(c.points) == 4:
            continue
        poly = flatten(c)
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if (a[1] - y) * (b[1] - y) < 0:
                xs.append(x_at(a, b, y))
    return sorted(xs)


def flatten(contour, steps=24):
    pts = contour.points
    n = len(pts)
    start = next(i for i, p in enumerate(pts) if p.type is not None)
    out = []
    i = start
    cur = (pts[i].x, pts[i].y)
    while True:
        offs = []
        j = (i + 1) % n
        while pts[j].type is None:
            offs.append((pts[j].x, pts[j].y))
            j = (j + 1) % n
        end = (pts[j].x, pts[j].y)
        if len(offs) == 2:
            for s in range(1, steps + 1):
                t = s / steps
                u = 1 - t
                out.append((u ** 3 * cur[0] + 3 * u * u * t * offs[0][0] + 3 * u * t * t * offs[1][0] + t ** 3 * end[0],
                            u ** 3 * cur[1] + 3 * u * u * t * offs[0][1] + 3 * u * t * t * offs[1][1] + t ** 3 * end[1]))
        else:
            out.append(end)
        cur = end
        i = j
        if i == start:
            break
    return out


def bar_contour(glyph, xh):
    for ci, c in enumerate(glyph.contours):
        if len(c.points) != 4 or any(p.type != 'line' for p in c.points):
            continue
        ys = sorted({round(p.y) for p in c.points})
        xs = sorted({round(p.x) for p in c.points})
        if len(ys) == 2 and len(xs) == 2 and abs(ys[1] - xh) <= 4:
            return ci
    return None


def crossbars(masters):
    """t and f bars lead right: the left overhang keeps BAR_LEFT of its
    length, the t's right overhang grows by T_RIGHT. The stem keeps its
    place, so the letter's rhythm is unchanged; the advance grows by what
    the bar gains on the right, and so do the advances of glyphs built
    from these (accented t, t with stroke, peseta)."""
    ref = masters['m02']
    names = []
    for g in ref:
        if not g.name.startswith(('t', 'f')) or g.name.startswith(('tturn', 'tbar')):
            continue
        if '.sups' in g.name or '.subs' in g.name or '.sc' in g.name:
            continue
        ci = bar_contour(g, ref.info.xHeight)
        if ci is None:
            continue
        names.append((g.name, ci))
    done = []
    growth = {}
    for name, ci in names:
        plan = []
        for m, f in masters.items():
            g = f[name]
            c = g.contours[ci]
            ys = [p.y for p in c.points]
            ymid = (min(ys) + max(ys)) / 2
            bx0, bx1 = min(p.x for p in c.points), max(p.x for p in c.points)
            xs = [x for x in crossings(f, g, ymid, ci) if bx0 < x < bx1]
            if len(xs) < 2:
                plan = None
                break
            plan.append((m, xs[0], xs[-1]))
        if not plan:
            continue
        for m, sl, sr in plan:
            f = masters[m]
            g = f[name]
            c = g.contours[ci]
            b0 = lib.bounds(g, f)
            bx0, bx1 = min(p.x for p in c.points), max(p.x for p in c.points)
            nl = sl - BAR_LEFT * (sl - bx0)
            nr = sr + (T_RIGHT if name.startswith('t') else 1.0) * (bx1 - sr)
            for p in c.points:
                p.x = nl if abs(p.x - bx0) < 1 else nr if abs(p.x - bx1) < 1 else p.x
            b1 = lib.bounds(g, f)
            grow = max(0.0, b1[2] - b0[2])
            g.width += grow
            growth.setdefault(m, {})[name] = grow
        done.append(name)
    for m, f in masters.items():
        for g in f:
            if g.name in done:
                continue
            gains = [growth[m].get(c.baseGlyph, 0.0) for c in g.components]
            if any(gains):
                g.width += max(gains)
    return done


# ------------------------------------------------------------------ y

def y_straight(masters, name, ref_name):
    """The y's tail runs straight on, on the line of the right stroke, and
    ends on a level cut at the descender. The tail's on-curve points slide
    onto the two stroke edges and its handles sit at thirds, so the curves
    become straight lines with the same point structure."""
    ref = masters[ref_name][name]
    c = ref.contours[0]
    n = len(c.points)
    below = sorted([i for i in on_points(c) if c.points[i].y < 0], key=lambda i: c.points[i].x)
    e0, e1 = sorted(below[:2], key=lambda i: c.points[i].y)   # e0 low (outer), e1 high (inner)
    # outer edge: walk forward from e0 to the first line segment
    def walk(i, step):
        seq = [i]
        j = i
        while True:
            j = (j + step) % n
            seq.append(j)
            p = c.points[j]
            if p.type is not None:
                nxt = (j + step) % n
                seg_line = (c.points[nxt].type == 'line') if step == 1 else (p.type == 'line')
                if seg_line and len(seq) > 1:
                    return seq, j, nxt
    outer_seq, o_anchor, o_next = walk(e0, 1)
    inner_seq, i_anchor, i_next = walk(e1, -1)

    def move():
        for f in masters.values():
            cc = f[name].contours[0]
            P = cc.points
            y_end = min(p.y for p in P)
            O = ((P[o_anchor].x, P[o_anchor].y), (P[o_next].x, P[o_next].y))
            for seq, a, b in ((outer_seq, o_anchor, o_next), (inner_seq, i_anchor, i_next)):
                A = (P[a].x, P[a].y)
                B = (P[b].x, P[b].y)
                if seq is inner_seq:
                    # the inner edge runs parallel to the outer one, so the
                    # tail keeps one thickness in every master. A level
                    # junction (mono) starts the line at its end point A;
                    # otherwise it starts at the junction corner B and A
                    # moves onto it.
                    d = (O[1][0] - O[0][0], O[1][1] - O[0][1])
                    if abs(B[1] - A[1]) >= 0.2 * abs(B[0] - A[0]):
                        A = (x_at(B, (B[0] + d[0], B[1] + d[1]), A[1]), A[1])
                        P[a].x = A[0]
                    B = (A[0] + d[0], A[1] + d[1])
                end = (x_at(A, B, y_end), y_end)
                P[seq[0]].x, P[seq[0]].y = end
                # points strictly between end and anchor, by position in the run
                inner = seq[1:-1]
                ons = [k for k in inner if P[k].type is not None]
                nseg = len(ons) + 1
                knots = [end] + [None] * len(ons) + [A]
                for s in range(1, nseg):
                    t = s / nseg
                    knots[s] = (end[0] + (A[0] - end[0]) * t, end[1] + (A[1] - end[1]) * t)
                # assign: walk the run, knots at on-curves, handles at thirds
                run = seq
                kidx = 0
                k = 1
                while k < len(run):
                    offs = []
                    while P[run[k]].type is None:
                        offs.append(run[k])
                        k += 1
                    p0, p1 = knots[kidx], knots[kidx + 1]
                    for h, idx in enumerate(offs):
                        t = (h + 1) / (len(offs) + 1)
                        P[idx].x = p0[0] + (p1[0] - p0[0]) * t
                        P[idx].y = p0[1] + (p1[1] - p0[1]) * t
                    kidx += 1
                    if run[k] != a:
                        P[run[k]].x, P[run[k]].y = knots[kidx]
                    k += 1
    guarded(masters, name, move)


# ------------------------------------------------------------------ r

def r_slant(masters, name='r', ref_name='m02'):
    """The r's arm ends on a slanted cut at the t's angle: the cut's lower
    point moves left by R_ANGLE of the cut height, and the short lower edge
    before it becomes straight."""
    ref = masters[ref_name][name]
    c = ref.contours[0]
    n = len(c.points)
    rx = max(p.x for p in c.points)
    cut = [i for i in on_points(c) if abs(c.points[i].x - rx) < 1]
    assert len(cut) == 2, 'r outline changed'
    lo, hi = sorted(cut, key=lambda i: c.points[i].y)
    # previous on-curve before lo along the lower edge
    j = (lo - 1) % n
    offs = []
    while c.points[j].type is None:
        offs.append(j)
        j = (j - 1) % n
    prev = j
    offs = offs[::-1]
    jj = (prev - 1) % n
    into_prev = jj if c.points[jj].type is None else None

    def move():
        for f in masters.values():
            P = f[name].contours[0].points
            h = P[hi].y - P[lo].y
            x_new = P[hi].x - R_ANGLE * h
            limit = x_new - 0.12 * stem(f)
            if P[prev].x > limit:
                d = P[prev].x - limit
                P[prev].x -= d
                if into_prev is not None:
                    P[into_prev].x -= d
            P[lo].x = x_new
            P[lo].y = P[prev].y
            a, b = (P[prev].x, P[prev].y), (P[lo].x, P[lo].y)
            for k, idx in enumerate(offs):
                t = (k + 1) / (len(offs) + 1)
                P[idx].x = a[0] + (b[0] - a[0]) * t
                P[idx].y = a[1] + (b[1] - a[1]) * t
    guarded(masters, name, move)


# ------------------------------------------------------------------ a

def a_bowl(masters, name='a'):
    """A larger a bowl: the bowl's top (inner and outer edge) and its join
    with the stem rise by A_BOWL of the hook's counter, eased to zero at
    the bowl's middle, so the bowl stroke keeps its thickness."""
    ref = masters['m02'][name]
    assert len(ref.contours) == 2, 'a outline changed'
    outer, inner = ref.contours
    ys_in = [p.y for p in inner.points]
    # the hook's inner top: lowest on-curve of the outer contour that is
    # above the counter's top and left of the stem
    plan = []

    def select(f):
        g = f[name]
        o, i = g.contours
        top_in = max(p.y for p in i.points)
        mid = (min(p.y for p in i.points) + top_in) / 2
        stem_x = max(p.x for p in i.points)
        above = sorted(p.y for p in o.points if p.type is not None and p.y > top_in + 1 and p.x < stem_x - 1)
        # lowest: the bowl stroke's upper edge; next: the hook's lower edge
        return top_in, mid, stem_x, (above[1] if len(above) > 1 else None)
    top_in, mid, stem_x, hook = select(masters['m02'])
    assert hook is not None
    sel_o = [k for k, p in enumerate(outer.points)
             if p.y > mid and p.y < hook - 1 and p.x <= stem_x + 1]
    sel_i = [k for k, p in enumerate(inner.points) if p.y > mid]

    def move():
        for f in masters.values():
            o, i = f[name].contours
            t_in, m_, sx, hk = select(f)
            low = min(p.y for p in o.points if p.type is not None and p.y > t_in + 1 and p.x < sx - 1)
            d = A_BOWL * (hk - low)
            for c, sel in ((o, sel_o), (i, sel_i)):
                P = c.points
                n = len(P)
                ys = [p.y for p in P]

                def owner(k):
                    # a handle moves with the on-curve point it belongs to
                    if P[k].type is not None:
                        return k
                    if P[(k - 1) % n].type is not None:
                        return (k - 1) % n
                    return (k + 1) % n
                for k in sel:
                    w = min(1.0, max(0.0, (ys[owner(k)] - m_) / (t_in - m_)))
                    P[k].y += d * w
    guarded(masters, name, move)
    return len(sel_o), len(sel_i)


# ------------------------------------------------------------------ g

def g_ear(masters, name='g'):
    """A level ear on the g's stem top: the stem's top-right corner becomes
    a short bar to the right, as thick as the horizontal strokes. Two
    points are inserted in every master."""
    ref = masters['m02'][name]
    c = ref.contours[0]
    xh = masters['m02'].info.xHeight
    tops = [i for i in on_points(c) if abs(c.points[i].y - xh) < 2]
    assert len(tops) == 2, 'g outline changed'
    right = max(tops, key=lambda i: c.points[i].x)
    for f in masters.values():
        g = f[name]
        P = g.contours[0].points
        p = P[right]
        L = EAR * stem(f)
        t = AMP_BAR * hbar(f)
        x0, y0 = p.x, p.y
        # contour runs up the stem's right side into `right`, then left along the top
        new = [Point(x0, y0 - t, 'line'), Point(x0 + L, y0 - t, 'line'), Point(x0 + L, y0, 'line')]
        P[right:right + 1] = new
        g.width += 0.5 * L


# ------------------------------------------------------------------ G, k

def g_bar(masters, name='G'):
    for f in masters.values():
        g = f[name]
        c = [c for c in g.contours if len(c.points) == 7]
        assert len(c) == 1, 'G outline changed'
        P = c[0].points
        xl = min(p.x for p in P)
        for p in P:
            if abs(p.x - xl) < 1:
                p.x -= G_BAR * stem(f)


def k_leg(masters, names=('k', 'k.base')):
    """The k's legs spring from the stem (the R's leg: identity.r_leg): the leg's two top points
    move left until the top-left point sits K_INTO stems inside the stem."""
    for name in names:
        for f in masters.values():
            g = f[name]
            quads = [c for c in g.contours if len(c.points) == 4]
            st = [c for c in quads if len({round(p.x) for p in c.points}) == 2]
            leg = [c for c in quads if c not in st]
            assert len(leg) == 1 and len(st) <= 1, f'{name} outline changed'
            if st:
                sr = max(p.x for p in st[0].points)
            else:
                sr = lib.bounds(g)[0] + stem(f)
            tops = sorted(leg[0].points, key=lambda p: -p.y)[:2]
            tl = min(tops, key=lambda p: p.x)
            dx = tl.x - (sr - K_INTO * stem(f))
            for p in tops:
                p.x -= dx


# ------------------------------------------------------------------ mono

ONE_FLAG = 0.55       # mono 1: the flag tip rises by this share of its drop
MONO_TAUT = 0.40      # mono a g l and the dots: extra squaring
MIN_ANGLE = 30       # level cuts only on strokes steeper than this
OPERATORS = ['less', 'greater', '_part.arrowhead', '_part.arrowhead1', '_part.arrowhead2',
             '_part.arrowhead3', '_part.less2', '_part.greater2', 'greater_equal.liga',
             '_part.not_equal', 'exclam_equal_equal.liga']


def level_ends(masters, names, ref_name):
    """Slanted stroke ends on operators become level cuts. A cut is a short
    line between two corners whose neighbouring edges are longer lines; the
    corner farther from the glyph's middle slides along its edge to the
    other corner's height, so the stroke shortens a little and ends level."""
    ref = masters[ref_name]
    st = stem(ref)
    done = []
    for name in names:
        if name not in ref or not ref[name].contours:
            continue
        g = ref[name]
        b = lib.bounds(g)
        ymid = (b[1] + b[3]) / 2
        plan = []
        for ci, c in enumerate(g.contours):
            P = c.points
            n = len(P)
            for i in range(n):
                j = (i + 1) % n
                pi_, pj = P[i], P[j]
                if pi_.type != 'line' and pi_.type != 'curve' or pj.type != 'line':
                    continue
                if pi_.smooth or pj.smooth:
                    continue
                prv, nxt = (i - 1) % n, (j + 1) % n
                if P[prv].type is None or P[nxt].type is None or P[nxt].type != 'line' or pi_.type != 'line':
                    continue
                dx, dy = pj.x - pi_.x, pj.y - pi_.y
                cut = math.hypot(dx, dy)
                if cut > 1.6 * st or abs(dy) < 0.2 * abs(dx) or abs(dx) < 0.2 * abs(dy):
                    continue
                e1 = math.hypot(pi_.x - P[prv].x, pi_.y - P[prv].y)
                e2 = math.hypot(P[nxt].x - pj.x, P[nxt].y - pj.y)
                if min(e1, e2) < 1.2 * cut:
                    continue
                if abs(pi_.y - ymid) > abs(pj.y - ymid):
                    tip, edge, other = i, prv, j
                else:
                    tip, edge, other = j, nxt, i
                ex, ey = P[edge].x - P[tip].x, P[edge].y - P[tip].y
                if math.degrees(math.atan2(abs(ey), abs(ex))) < MIN_ANGLE:
                    continue        # a shallow stroke would end in a spike
                plan.append((ci, tip, edge, other))
        if not plan:
            continue

        def move(name=name, plan=plan):
            for f in masters.values():
                for ci, tip, edge, other in plan:
                    P = f[name].contours[ci].points
                    T, E = (P[tip].x, P[tip].y), (P[edge].x, P[edge].y)
                    y = P[other].y
                    P[tip].x, P[tip].y = x_at(T, E, y), y
        if guarded(masters, name, move):
            done.append((name, len(plan)))
    return done


def level_or_equal(masters, name='greater_equal.liga'):
    """The `>=` and `<=` ligatures (`<=` is `>=` mirrored) take a level
    or-equal bar under the chevron, in place of the bar slanted along the
    chevron's lower arm: the family's level bar. The bar keeps its four
    points; it spans the chevron and sits one equal-sign gap below it, as
    thick as the equal sign's bars."""
    for f in masters.values():
        g = f[name]
        quads = [c for c in g.contours if len(c.points) == 4]
        bar = min(quads, key=lambda c: min(p.y for p in c.points))
        rest = [c for c in g.contours if c is not bar]
        eq = sorted((c for c in f['equal'].contours), key=lambda c: min(p.y for p in c.points))
        assert len(eq) == 2, 'mono equal changed'
        t = max(p.y for p in eq[0].points) - min(p.y for p in eq[0].points)
        gap = min(p.y for p in eq[1].points) - max(p.y for p in eq[0].points)
        low = min(p.y for c in rest for p in c.points)
        x0 = min(p.x for c in rest for p in c.points)
        x1 = max(p.x for c in rest for p in c.points)
        top = low - gap
        sign = 1 if area(bar.points) > 0 else -1
        rect = [(x1, top), (x0, top), (x0, top - t), (x1, top - t)]
        if sign < 0:
            rect = [rect[0]] + rect[1:][::-1]
        for p, (x, y) in zip(bar.points, rect):
            p.x, p.y = x, y


def one_flag(masters, name='one'):
    """The mono 1's flag flattens: its tip (the two leftmost points) rises
    by ONE_FLAG of the flag's drop."""
    for f in masters.values():
        c = f[name].contours[0]
        P = c.points
        top = max(p.y for p in P)
        tip = sorted(on_points(c), key=lambda i: P[i].x)[:2]
        drop = top - max(P[i].y for i in tip)
        for i in tip:
            P[i].y += ONE_FLAG * drop


def r_beakless(masters, name='r'):
    """The mono r loses the drooping beak at its arm's end (a separate
    five-point contour), then takes the sans r's slanted cut."""
    for f in masters.values():
        g = f[name]
        beak = [c for c in g.contours if len(c.points) == 5]
        assert len(g.contours) == 2 and len(beak) == 1, 'mono r outline changed'
        g.contours.remove(beak[0])
    r_slant(masters, name, 'm00')


def mono(masters):
    """The mono's own drawing, after its squaring and terminals."""
    y_straight(masters, 'y', 'm00')
    r_beakless(masters)
    one_flag(masters)
    dots = [n for n in ('i', 'j', '_part.dot', 'period') if n in masters['m00'] and masters['m00'][n].contours]
    print('keys: mono squaring', identity.rounds(masters, alpha=MONO_TAUT, names=['a', 'g', 'l'] + dots,
                                                 ref_name='m00'), flush=True)
    level_or_equal(masters)
    print('keys: operator ends', level_ends(masters, OPERATORS, 'm00'), flush=True)
    amp_bar(masters, ['ampersand'], 'm00')


# ------------------------------------------------------------------ run

def sans(masters, swap_alternates):
    swapped = swap_figures(masters, swap_alternates)
    print('keys: figure defaults swapped:', len(swapped), flush=True)


def sans_shapes(masters):
    """After the family squaring passes, before the figure metrics."""
    print('keys: t/f bars', len(crossbars(masters)), flush=True)
    y_straight(masters, 'y', 'm02')
    r_slant(masters)
    print('keys: a bowl points', a_bowl(masters), flush=True)
    g_ear(masters)
    g_bar(masters)
    k_leg(masters)
    seven_stem(masters)
    figs = [n for n in ('zero', 'two', 'three', 'six', 'nine', 'g')
            if masters['m02'][n].contours]
    print('keys: figure squaring', identity.rounds(masters, alpha=FIG_TAUT, names=figs), flush=True)
    amp_bar(masters, ['ampersand'], 'm02')
