"""The family's two shared details.

1. The landing diagonal. The 2's spine and the 7's stem leave their top
   along the straight line they had and land on the baseline steeper,
   bowed toward the upper left, as the serif's 7 already does. Every face
   draws the same curve: a straight diagonal becomes one cubic whose top
   handle lies on the old line (so a smooth join into the 2's bowl stays
   smooth) and whose foot handle turns LAND degrees toward the vertical.
   Display masters turn further, so the bow shows at headline sizes.

2. The level cut. Sans and mono strokes end in level (horizontal) cuts.
   The serif's ball terminals (a c f r j y and the f ligatures, the
   figures' balls) take the same cut: the ball's two side points drop or
   rise to the ball's extreme, so the ball becomes a short wedge with a
   flat end on the level, as wide as the ball was.
"""
import math
import lib

# Degrees the foot handle of a landing diagonal turns toward the vertical,
# per master kind.
LAND = {'text': 12.0, 'display': 24.0}
# A diagonal is a line at this many degrees from the level or more (and
# less than STEEP), at least this share of the glyph's height long.
SHALLOW, STEEP = 30.0, 82.0
MIN_SHARE = 0.30


def _on_list(P):
    return [i for i, p in enumerate(P) if p.type is not None]


def diagonals(glyph):
    """(contour, start index, end index) of each long diagonal line."""
    b = lib.bounds(glyph)
    h = b[3] - b[1]
    out = []
    for ci, c in enumerate(glyph.contours):
        P = c.points
        n = len(P)
        for j, q in enumerate(P):
            if q.type != 'line':
                continue
            i = (j - 1) % n
            p = P[i]
            if p.type is None:
                continue
            dx, dy = q.x - p.x, q.y - p.y
            L = math.hypot(dx, dy)
            if L < MIN_SHARE * h:
                continue
            ang = math.degrees(math.atan2(abs(dy), abs(dx)))
            if SHALLOW <= ang <= STEEP and dx * dy > 0:
                # top right to bottom left only (the 2's spine, the 7's stem)
                out.append((ci, i, j))
    return out


def _turn(v, deg):
    """Turn the upward vector v toward the vertical by deg."""
    a = math.radians(deg) * (1 if v[0] > 0 else -1)
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


# Where a diagonal's top meets a straight line at a shallow turn (the mono's
# and the serif's 7: the stem's right edge meets the short upright at the
# bar's end), the bowed curve's top handle turns away from that line until
# the join turns by at least TOP_CORNER degrees, so it stays a real corner
# (the outline check and the tangency pass treat 3-25 degree joins next to
# a curve as kinks to straighten, which would swell the stem under the
# bar). Every diagonal of the glyph takes the same top turn, so the stem's
# two edges stay parallel.
TOP_CORNER = 32.0


def _top_turn(glyph, plan):
    """Degrees every planned diagonal's top handle turns toward the level."""
    need = 0.0
    for ci, i, j in plan:
        P = glyph.contours[ci].points
        n = len(P)
        a, b = P[i], P[j]
        top_i = i if a.y > b.y else j
        other = j if top_i == i else i
        # the neighbour of the top point that is not on this diagonal
        k = (top_i + (1 if (top_i + 1) % n != other else -1)) % n
        q = P[k]
        if q.type is None:
            continue    # a curve continues from the top: keep its tangent
        top, foot = P[top_i], P[other]
        d = (top.x - foot.x, top.y - foot.y)
        e = (q.x - top.x, q.y - top.y)
        if math.hypot(*e) < 0.5:
            continue
        cos = (d[0] * e[0] + d[1] * e[1]) / (math.hypot(*d) * math.hypot(*e))
        turn = math.degrees(math.acos(max(-1.0, min(1.0, cos))))
        if turn < TOP_CORNER:
            need = max(need, TOP_CORNER - turn)
    return need


def land(glyph, plan, deg, top_deg=0.0):
    """Bow the planned diagonals of one master's glyph. plan lists
    (contour, start, end) found on the reference master; indices are taken
    before any insertion, so later segments are handled first. top_deg
    turns each top handle toward the level (see TOP_CORNER)."""
    from ufoLib2.objects import Point
    # the segment closing the contour first (its handles go at the end), then later ones
    for ci, i, j in sorted(plan, key=lambda t: (t[0], t[2] > t[1], -t[2])):
        P = glyph.contours[ci].points
        a, b = P[i], P[j]
        top, foot = (a, b) if a.y > b.y else (b, a)
        d = (top.x - foot.x, top.y - foot.y)
        L = math.hypot(*d)
        v = _turn(d, -top_deg)
        h_top = (top.x - v[0] / 3, top.y - v[1] / 3)
        u = _turn(d, deg)
        h_foot = (foot.x + u[0] / 3, foot.y + u[1] / 3)
        first, second = (h_top, h_foot) if top is a else (h_foot, h_top)
        b.type = 'curve'
        P.insert(j if j > i else len(P), Point(second[0], second[1]))
        P.insert(j if j > i else len(P) - 1, Point(first[0], first[1]))
        assert L > 0


def _is_line(glyph, ci, i, j):
    if ci >= len(glyph.contours):
        return False
    P = glyph.contours[ci].points
    return j < len(P) and P[j].type == 'line' and P[i].type is not None


def landing(masters, bases, ref_name, display, guarded):
    """Bow the diagonals of every glyph whose base name is in bases (the
    2's spine, the 7's stem), found on the reference master, in every
    master. display: master names that take the display turn. Returns
    {glyph: diagonals bowed}."""
    ref = masters[ref_name]
    done = {}
    for g in ref:
        name = g.name
        if name.split('.')[0] not in bases or not g.contours or g.components:
            continue
        plan = diagonals(g)
        if not plan or not all(_is_line(f[name], *t) for f in masters.values() for t in plan):
            continue
        top_deg = _top_turn(g, plan)

        def move(name=name, plan=plan, top_deg=top_deg):
            for m, f in masters.items():
                land(f[name], plan, LAND['display' if m in display else 'text'], top_deg)
        if guarded(masters, name, move):
            done[name] = len(plan)
    return done


# ------------------------------------------------------------------ level cut

def _nb(P, i, step):
    n = len(P)
    k = i
    for _ in range(n):
        k = (k + step) % n
        if P[k].type is not None:
            return k
    return None


def balls(glyph, upm, max_w=0.16, min_drop=0.022):
    """Ball terminals: a smooth extreme with level handles whose two
    neighbouring on-curve points are curve points within max_w em of each
    other and at least min_drop em above (or below) it. Returns
    (contour, left, extreme, right, 'top' | 'bot')."""
    out = []
    for ci, c in enumerate(glyph.contours):
        P = c.points
        n = len(P)
        for e, p in enumerate(P):
            if p.type != 'curve' or not p.smooth:
                continue
            a, b = P[e - 1], P[(e + 1) % n]
            if a.type is not None or b.type is not None or abs(a.y - p.y) > 1 or abs(b.y - p.y) > 1:
                continue
            l, r = _nb(P, e, -1), _nb(P, e, 1)
            L, R = P[l], P[r]
            if R.type != 'curve' or p.type != 'curve':
                continue
            w = abs(R.x - L.x)
            up = min(L.y, R.y) - p.y
            dn = p.y - max(L.y, R.y)
            if w > max_w * upm:
                continue
            if up > min_drop * upm:
                out.append((ci, l, e, r, 'bot'))      # the ball hangs: its foot is the extreme
            elif dn > min_drop * upm:
                out.append((ci, l, e, r, 'top'))
    return out


def level_cut(glyph, plan):
    """Drop the ball's side points to its extreme and draw the end as a
    straight level line through it."""
    for ci, l, e, r, _ in plan:
        P = glyph.contours[ci].points
        n = len(P)
        E = P[e]
        for k in (l, r):
            dy = E.y - P[k].y
            # the side point and the handle on its outer side move together,
            # so the stroke side keeps its run into the cut
            outer = (k - 1) % n if k == l else (k + 1) % n
            P[k].y += dy
            if P[outer].type is None:
                P[outer].y += dy
            P[k].smooth = False
        Lp, Rp = P[l], P[r]
        # the two curves into and out of the extreme become straight thirds
        h = [(e - 2) % n, (e - 1) % n, (e + 1) % n, (e + 2) % n]
        P[h[0]].x, P[h[0]].y = Lp.x + (E.x - Lp.x) / 3, E.y
        P[h[1]].x, P[h[1]].y = Lp.x + 2 * (E.x - Lp.x) / 3, E.y
        P[h[2]].x, P[h[2]].y = E.x + (Rp.x - E.x) / 3, E.y
        P[h[3]].x, P[h[3]].y = E.x + 2 * (Rp.x - E.x) / 3, E.y


# Glyphs whose ball terminals take the level cut (base names, before any
# suffix; superior and inferior figures count as their figure). Dots and
# other round marks are not terminals.
LEVEL = {'a', 'ae', 'aogonek', 'c', 'cent', 'f', 'f_i', 'f_j', 'f_l', 'f_t', 'longs', 'j', 'dotlessj', 'r',
         'y', 'J', 'two', 'three', 'five', 'eng', 'Eng', 'gscript', 'ordfeminine'}
SMALL_NAMES = {'twosuperior': 'two', 'threesuperior': 'three', 'twoinferior': 'two', 'threeinferior': 'three',
               'fivesuperior': 'five', 'fiveinferior': 'five'}


def level_base(name):
    base = name.split('.')[0]
    return SMALL_NAMES.get(base, base) in LEVEL


def level_terminals(masters, ref_name, guarded):
    """Level cuts on every ball terminal of the LEVEL glyphs found on the
    reference master, where the structure matches in all masters."""
    ref = masters[ref_name]
    upm = ref.info.unitsPerEm
    done = {}
    for g in ref:
        if not level_base(g.name) or not g.contours:
            continue
        plan = [t for t in balls(g, upm)
                if (t[2] - t[1]) % len(g.contours[t[0]].points) == 3
                and (t[3] - t[2]) % len(g.contours[t[0]].points) == 3
                and len(_on_list(g.contours[t[0]].points)) >= 6]
        if not plan:
            continue
        if any(len(f[g.name].contours) != len(g.contours)
               or any(len(a.points) != len(b.points) for a, b in zip(f[g.name].contours, g.contours))
               for f in masters.values()):
            continue

        def move(name=g.name, plan=plan):
            for f in masters.values():
                level_cut(f[name], plan)
        if guarded(masters, g.name, move):
            done[g.name] = len(plan)
    return done
