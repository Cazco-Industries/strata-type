"""Restore tangent joins and short leads that a transform bent.

Scaling, squaring (identity.rounds), the serif's lowercase remap and stroke
gain move handles master by master; where the upstream drawing joins two
pieces tangentially, those moves can leave a small break (a kink of a few
degrees that the interpolation check and the outline check both see).

For every glyph that still has the upstream's point structure (same
contours, same point types; the upstream is the glyph named by
`com.strata.source`, or the same name):

1. Short leads (the serif only). A line shorter than LEAD em next to a
   curve whose direction now differs from its upstream direction by more
   than FLIP degrees (the serif's stroke gain can turn a lead of a few
   units around) is redrawn
   in its upstream direction, at its current length. When one end of it
   joined its curve tangentially upstream, the line takes that curve's
   handle direction and its other end moves (sliding along the line before
   it when that line ends in a curve, so that join keeps its angle); when
   both ends join curves, it turns about its middle.
2. Tangent joins. Every on-curve point next to a curve whose join now
   turns by more than FLAT degrees and under BREAK gets its handles
   realigned, when its upstream join turned by less than TANGENT degrees
   (the outline check's kink floor) or by BREAK or more (a corner a
   transform flattened into a near-tangent join, such as an inner corner of
   an axis-cut terminal): a handle next to a line takes the line's
   direction; two handles take their mean direction (a retracted handle
   keeps its place and the other side follows the nearest distinct point).
   Handle lengths and on-curve points do not move.

A glyph a transform redrew (another point structure) is straightened as in
step 2 at every near-tangent join next to a curve, but only when its
upstream has no such join at all.

Each master is realigned on its own, so a glyph whose realignment would add
an interpolation kink between masters (the gate's check, masters in source
order) is left as it was before this pass.
"""
import math
from pathlib import Path
import ufoLib2

SOURCE_KEY = 'com.strata.source'
TANGENT = 3.0
FLAT = 0.3
BREAK = 25.0
LEAD = 0.03
FLIP = 20.0


def _unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n) if n > 0.5 else None


def _distinct(P, i, step):
    n = len(P)
    p = P[i]
    k = i
    for _ in range(n):
        k = (k + step) % n
        if math.hypot(P[k].x - p.x, P[k].y - p.y) > 0.5:
            return P[k]
    return None


def _turn(P, i):
    """Turn at on-curve point i, between the nearest distinct points (as the
    outline check measures it)."""
    p, a, b = P[i], _distinct(P, i, -1), _distinct(P, i, 1)
    if a is None or b is None:
        return None
    tin = _unit((p.x - a.x, p.y - a.y))
    tout = _unit((b.x - p.x, b.y - p.y))
    if not tin or not tout:
        return None
    return math.degrees(math.acos(max(-1.0, min(1.0, tin[0] * tout[0] + tin[1] * tout[1]))))


def _kinks(P):
    n = len(P)
    out = 0
    for i, p in enumerate(P):
        if p.type is None:
            continue
        t = _turn(P, i)
        near_curve = P[i - 1].type is None or P[(i + 1) % n].type is None
        if t is not None and ((p.smooth and t > 2.0) or (near_curve and TANGENT <= t < BREAK)):
            out += 1
    return out


def _align(P, i):
    """Make the join at on-curve point i tangent by turning its handles."""
    n = len(P)
    p = P[i]
    a, b = P[i - 1], P[(i + 1) % n]
    da, db = _distinct(P, i, -1), _distinct(P, i, 1)
    la = (p.x - da.x, p.y - da.y)
    lb = (db.x - p.x, db.y - p.y)
    na, nb = math.hypot(*la), math.hypot(*lb)
    free_a = a.type is None and math.hypot(p.x - a.x, p.y - a.y) > 0.5
    free_b = b.type is None and math.hypot(b.x - p.x, b.y - p.y) > 0.5
    if free_a and free_b:
        d = _unit((la[0] / na + lb[0] / nb, la[1] / na + lb[1] / nb))
    elif free_a:
        d = _unit(lb)
    elif free_b:
        d = _unit(la)
    else:
        return False
    if free_a:
        ra = math.hypot(p.x - a.x, p.y - a.y)
        a.x, a.y = round(p.x - d[0] * ra, 2), round(p.y - d[1] * ra, 2)
    if free_b:
        rb = math.hypot(b.x - p.x, b.y - p.y)
        b.x, b.y = round(p.x + d[0] * rb, 2), round(p.y + d[1] * rb, 2)
    return True


def _same(c, u):
    return len(c.points) == len(u.points) and all((p.type is None) == (q.type is None) for p, q in zip(c.points, u.points))


def _angle(u, v):
    return math.degrees(math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))))


def _meet(p, d, q, e):
    """Intersection of the lines p + s d and q + t e (None when parallel)."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    s = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + s * d[0], p[1] + s * d[1])


def _relead(P, Q, upm):
    """Step 1: short leads turned around by a transform get their upstream
    direction back."""
    n = len(P)
    fixed = 0
    for i in range(n):
        b, a = P[i], P[i - 1]
        if b.type != 'line' or a.type is None:
            continue
        L = (b.x - a.x, b.y - a.y)
        U = (Q[i].x - Q[i - 1].x, Q[i].y - Q[i - 1].y)
        l = math.hypot(*L)
        ul, uu = _unit(L), _unit(U)
        if not ul or not uu or l > LEAD * upm or _angle(ul, uu) <= FLIP:
            continue
        curve_b = P[(i + 1) % n].type is None
        curve_a = P[i - 2].type is None
        if not (curve_a or curve_b):
            continue
        tan_b = curve_b and (_turn(Q, i) or 0.0) < TANGENT
        tan_a = curve_a and (_turn(Q, (i - 1) % n) or 0.0) < TANGENT
        if curve_a and curve_b and not (tan_a ^ tan_b):
            m = ((a.x + b.x) / 2, (a.y + b.y) / 2)
            a.x, a.y = round(m[0] - uu[0] * l / 2, 2), round(m[1] - uu[1] * l / 2, 2)
            b.x, b.y = round(m[0] + uu[0] * l / 2, 2), round(m[1] + uu[1] * l / 2, 2)
            fixed += 1
            continue
        # one end joins its curve tangentially upstream: that end stays
        if tan_b or (curve_b and not curve_a):
            fix, move, h, before, before2 = b, a, P[(i + 1) % n], P[i - 2], P[i - 3]
            d = _unit((h.x - fix.x, h.y - fix.y)) if tan_b else uu
            d = (-d[0], -d[1]) if d else None
        else:
            fix, move, h, before, before2 = a, b, P[i - 2], P[(i + 1) % n], P[(i + 2) % n]
            d = _unit((fix.x - h.x, fix.y - h.y)) if tan_a else uu
        if not d:
            continue
        target = (fix.x + d[0] * l, fix.y + d[1] * l)
        if before.type is not None and before2.type is None:
            # the line before the moving end ends in a curve: slide along it
            e = _unit((move.x - before.x, move.y - before.y))
            x = _meet((fix.x, fix.y), d, (before.x, before.y), e) if e else None
            if x and math.hypot(x[0] - move.x, x[1] - move.y) <= LEAD * upm:
                target = x
        move.x, move.y = round(target[0], 2), round(target[1], 2)
        fixed += 1
    return fixed


def restore_glyph(g, up, upm=1000, relead=False):
    """Short leads get their upstream direction back; joins that were
    tangent upstream, or corners a transform flattened into near-tangent
    joins, are made tangent. A glyph a transform redrew (other point
    structure) whose upstream has no kink at all gets every near-tangent
    join next to a curve straightened."""
    fixed = 0
    same = len(g.contours) == len(up.contours) and all(_same(c, u) for c, u in zip(g.contours, up.contours))
    clean = sum(_kinks(u.points) for u in up.contours) == 0
    if not same and not clean:
        return 0
    if same and relead:
        for c, u in zip(g.contours, up.contours):
            fixed += _relead(c.points, u.points, upm)
    for ci, c in enumerate(g.contours):
        P = c.points
        n = len(P)
        Q = up.contours[ci].points if same else None
        for i, p in enumerate(P):
            if p.type is None:
                continue
            if not (P[i - 1].type is None or P[(i + 1) % n].type is None):
                continue
            tc = _turn(P, i)
            if tc is None or not FLAT < tc < BREAK:
                continue
            if same:
                tu = _turn(Q, i)
                if tu is None or TANGENT <= tu < BREAK:
                    continue
            if _align(P, i):
                if same and Q[i].smooth:
                    p.smooth = True
                fixed += 1
    return fixed


def restore(masters, base_folder, prefix, relead=False, keep=()):
    """masters: {mXX: Font}; the upstream masters are read from base_folder.
    relead: also run step 1 (the serif; key-letter transforms in the sans and
    mono redraw short lines on purpose). keep: glyphs left as they were in
    every master, whatever the kink test says."""
    import identity
    before = {m: {g.name: [[(p.x, p.y, p.smooth) for p in c.points] for c in g.contours] for g in f if g.contours}
              for m, f in masters.items()}
    total, glyphs = 0, set()
    for m, f in masters.items():
        path = Path(base_folder) / f'{prefix}-{m}.ufo'
        if not path.exists():
            continue
        base = ufoLib2.Font.open(path)
        for g in f:
            if not g.contours:
                continue
            src = g.lib.get(SOURCE_KEY, g.name)
            if src not in base:
                continue
            k = restore_glyph(g, base[src], f.info.unitsPerEm, relead)
            if k:
                total += k
                glyphs.add(g.name)
    kept = []
    for name in sorted(glyphs):
        if not all(name in f for f in masters.values()):
            continue
        if name in keep:
            _set(masters, name, before)
            kept.append(name)
            continue
        after = {m: [[(p.x, p.y, p.smooth) for p in c.points] for c in f[name].contours] for m, f in masters.items()}
        k1 = identity.kinks(masters, name)
        _set(masters, name, before)
        k0 = identity.kinks(masters, name)
        if any(x > y for x, y in zip(k1, k0)):
            kept.append(name)
        else:
            _set(masters, name, after, flat=True)
    if kept:
        print('tangent joins left as they were (would kink between masters):', ' '.join(kept), flush=True)
    return total, len(glyphs) - len(kept)


def _set(masters, name, state, flat=False):
    for m, f in masters.items():
        pts = state[m] if flat else state[m].get(name)
        if pts is None:
            continue
        for c, cp in zip(f[name].contours, pts):
            for p, (x, y, sm) in zip(c.points, cp):
                p.x, p.y, p.smooth = x, y, sm
