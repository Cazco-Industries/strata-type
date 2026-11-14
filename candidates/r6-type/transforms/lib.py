"""Shared helpers for the deterministic outline transforms.

Everything here works on ufoLib2 glyphs and keeps point structure identical
across masters unless a caller rebuilds a glyph the same way in every master.
"""
import math
from fontTools.misc.transform import Transform
from ufoLib2.objects import Contour, Point, Component, Anchor


# ---------------------------------------------------------------- basics

def rnd(v):
    return int(round(v))


def bounds(glyph, font=None):
    """Bounds of contours (and decomposed components when font is given)."""
    xs, ys = [], []
    for c in glyph.contours:
        for p in c.points:
            xs.append(p.x); ys.append(p.y)
    if font is not None:
        for comp in glyph.components:
            b = bounds(font[comp.baseGlyph], font)
            if b is None:
                continue
            t = comp.transformation
            for x, y in [(b[0], b[1]), (b[2], b[1]), (b[0], b[3]), (b[2], b[3])]:
                X, Y = t.transformPoint((x, y))
                xs.append(X); ys.append(Y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def copy_contours(src, dst, transform=None, reverse=False):
    for c in src.contours:
        pts = [Point(p.x, p.y, p.type, p.smooth, p.name) for p in c.points]
        if transform is not None:
            for p in pts:
                p.x, p.y = transform.transformPoint((p.x, p.y))
        new = Contour(points=pts)
        if reverse:
            reverse_contour(new)
        dst.contours.append(new)


def reverse_contour(contour):
    """Reverse direction keeping a closed contour's start point."""
    pts = contour.points
    if not pts:
        return
    # Build segments, reverse them, and rebuild.
    segs = to_segments(contour)
    start = segs[-1]['end']
    out = []
    prev_end = start
    rev = []
    ends = [s['end'] for s in segs]
    starts = [start] + ends[:-1]
    for s, st in zip(reversed(segs), reversed(starts)):
        rev.append({'type': s['type'], 'ctrl': list(reversed(s['ctrl'])), 'end': st, 'smooth': False})
    # rev[i] goes from end of segs[n-1-i] to its start; first rev segment starts at start point.
    from_segments(contour, rev)


def decompose(font, glyph):
    """Replace components by their contours (recursively)."""
    comps = list(glyph.components)
    glyph.components.clear()
    for comp in comps:
        base = font[comp.baseGlyph]
        tmp = base.copy()
        decompose(font, tmp)
        t = comp.transformation
        flip = t[0] * t[3] - t[1] * t[2] < 0
        copy_contours(tmp, glyph, Transform(*t), reverse=flip)


def shift_glyph(glyph, dx, dy=0):
    for c in glyph.contours:
        for p in c.points:
            p.x += dx; p.y += dy
    for a in glyph.anchors:
        a.x += dx; a.y += dy
    for comp in glyph.components:
        t = comp.transformation
        comp.transformation = Transform(t[0], t[1], t[2], t[3], t[4] + dx, t[5] + dy)


def round2(glyph):
    """Outline points to two decimals (fillet handles a few units long would
    bend if rounded to whole units; the compiler rounds once at the end)."""
    for c in glyph.contours:
        for p in c.points:
            p.x = round(p.x, 2); p.y = round(p.y, 2)


def round_glyph(glyph):
    for c in glyph.contours:
        for p in c.points:
            p.x = rnd(p.x); p.y = rnd(p.y)
    for a in glyph.anchors:
        a.x = rnd(a.x); a.y = rnd(a.y)
    for comp in glyph.components:
        t = comp.transformation
        comp.transformation = Transform(t[0], t[1], t[2], t[3], rnd(t[4]), rnd(t[5]))
    glyph.width = rnd(glyph.width)


def same_structure(a, b):
    if len(a.contours) != len(b.contours) or len(a.components) != len(b.components):
        return False
    for ca, cb in zip(a.contours, b.contours):
        if len(ca.points) != len(cb.points):
            return False
        if any(pa.type != pb.type for pa, pb in zip(ca.points, cb.points)):
            return False
    return all(x.baseGlyph == y.baseGlyph for x, y in zip(a.components, b.components))


def lerp_glyph(a, b, t, tx=None, ty=None):
    """Return copy of a moved toward b (t=0 -> a, t=1 -> b). Separate x/y factors allowed."""
    tx = t if tx is None else tx
    ty = t if ty is None else ty
    g = a.copy()
    for cg, ca, cb in zip(g.contours, a.contours, b.contours):
        for pg, pa, pb in zip(cg.points, ca.points, cb.points):
            pg.x = pa.x + tx * (pb.x - pa.x)
            pg.y = pa.y + ty * (pb.y - pa.y)
    if len(a.anchors) == len(b.anchors) and all(x.name == y.name for x, y in zip(a.anchors, b.anchors)):
        for ag, aa, ab in zip(g.anchors, a.anchors, b.anchors):
            ag.x = aa.x + tx * (ab.x - aa.x); ag.y = aa.y + ty * (ab.y - aa.y)
    for cg, ca, cb in zip(g.components, a.components, b.components):
        A, B = ca.transformation, cb.transformation
        cg.transformation = Transform(*[A[i] + (tx if i in (0, 2, 4) else ty) * (B[i] - A[i]) for i in range(6)])
    g.width = a.width + tx * (b.width - a.width)
    return g


def stem_comp_factor(s, v_m, v_p):
    """Factor k so that s * (v_m + k (v_p - v_m)) == v_m: move toward partner to undo scaling."""
    if abs(v_p - v_m) < 1e-6:
        return 0.0
    return (v_m / s - v_m) / (v_p - v_m)


def scale_compensated(gm, gp, sx, sy, v_m, v_p, h_m=None, h_p=None, clamp=(-0.6, 1.2)):
    """Scale glyph gm by (sx, sy) about the origin, correcting stems by
    interpolating x and y separately toward partner master gp. v = vertical stem
    (x thickness), h = horizontal stroke (y thickness)."""
    kx = stem_comp_factor(sx, v_m, v_p)
    ky = stem_comp_factor(sy, h_m if h_m else v_m, h_p if h_p else v_p) if sy != 1 else 0.0
    kx = max(clamp[0], min(clamp[1], kx)); ky = max(clamp[0], min(clamp[1], ky))
    g = lerp_glyph(gm, gp, 0, tx=kx, ty=ky)
    for c in g.contours:
        for p in c.points:
            p.x *= sx; p.y *= sy
    return g


# ---------------------------------------------------------------- segments

def to_segments(contour):
    pts = list(contour.points)
    k = next(i for i, p in enumerate(pts) if p.type is not None)
    pts = pts[k:] + pts[:k]
    segs, buf = [], []
    for p in pts[1:] + [pts[0]]:
        if p.type is None:
            buf.append((p.x, p.y))
        else:
            segs.append({'type': p.type, 'ctrl': buf, 'end': (p.x, p.y), 'smooth': p.smooth})
            buf = []
    return segs


def from_segments(contour, segs):
    """Write segments back; the last segment's end is the start point."""
    last = segs[-1]
    pts = [Point(last['end'][0], last['end'][1], last['type'] if last['type'] != 'move' else 'line', last.get('smooth', False))]
    for i, s in enumerate(segs):
        for c in s['ctrl']:
            pts.append(Point(c[0], c[1], None))
        if i < len(segs) - 1:
            pts.append(Point(s['end'][0], s['end'][1], s['type'], s.get('smooth', False)))
    # Move the trailing controls of the last segment: they precede the start point,
    # which UFO allows at the end of a closed contour.
    contour.points[:] = pts


def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def norm(a): return math.hypot(a[0], a[1])
def unit(a):
    n = norm(a)
    return (a[0] / n, a[1] / n) if n > 1e-9 else (0.0, 0.0)
def cross(a, b): return a[0] * b[1] - a[1] * b[0]
def dot(a, b): return a[0] * b[0] + a[1] * b[1]


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


def bez_tangent(p0, p1, p2, p3, t):
    u = 1 - t
    d = (3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
         3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1]))
    if norm(d) < 1e-9:
        d = sub(p3, p0) if t > .5 else sub(p1 if norm(sub(p1, p0)) > 1e-9 else p2, p0)
        if t > .5:
            d = sub(p3, p2 if norm(sub(p3, p2)) > 1e-9 else p1)
    return unit(d)


def split(p0, p1, p2, p3, t):
    a = add(p0, mul(sub(p1, p0), t)); b = add(p1, mul(sub(p2, p1), t)); c = add(p2, mul(sub(p3, p2), t))
    d = add(a, mul(sub(b, a), t)); e = add(b, mul(sub(c, b), t)); f = add(d, mul(sub(e, d), t))
    return (p0, a, d, f), (f, e, c, p3)


def sub_curve(p, t0, t1):
    """Exact sub-curve between parameters t0 < t1."""
    if t0 > 0:
        _, p = split(*p, t0)
        t1 = (t1 - t0) / (1 - t0)
    if t1 < 1:
        p, _ = split(*p, t1)
    return p


def curve_length(p, n=24):
    total, prev = 0.0, p[0]
    for i in range(1, n + 1):
        q = bez(*p, i / n); total += norm(sub(q, prev)); prev = q
    return total


def param_at_chord(p, d, from_end=False):
    """Parameter where the chord distance from the start (or end) equals d."""
    ref = p[3] if from_end else p[0]
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        t = 1 - mid if from_end else mid
        if norm(sub(bez(*p, t), ref)) < d:
            lo = mid
        else:
            hi = mid
    m = (lo + hi) / 2
    return 1 - m if from_end else m


# ---------------------------------------------------------------- fillets

def seg_points(start, seg):
    if seg['type'] == 'curve':
        return (start, seg['ctrl'][0], seg['ctrl'][1], seg['end'])
    if seg['type'] == 'line':
        return None
    raise ValueError('Unsupported segment type ' + seg['type'])


def seg_dirs(start, seg):
    """Unit tangents at the start and the end of a segment."""
    p = seg_points(start, seg)
    if p is None:
        d = unit(sub(seg['end'], start)); return d, d
    return bez_tangent(*p, 0.0), bez_tangent(*p, 1.0)


def seg_len(start, seg):
    p = seg_points(start, seg)
    return norm(sub(seg['end'], start)) if p is None else norm(sub(p[3], p[0]))


def classify_corners(contour, stem, min_turn=28, terminal_ratio=1.7):
    """On a reference master: corners as {index: kind} where index i is the end of
    segment i. kind is 'convex', 'concave'. Also returns the set of segment
    indices that are full round terminals (a short line between two convex corners)."""
    segs = to_segments(contour)
    n = len(segs)
    starts = [segs[i - 1]['end'] for i in range(n)]
    corners = {}
    for i in range(n):
        j = (i + 1) % n
        if segs[i]['smooth']:
            continue
        _, tin = seg_dirs(starts[i], segs[i])
        tout, _ = seg_dirs(starts[j], segs[j])
        ang = math.degrees(math.acos(max(-1, min(1, dot(tin, tout)))))
        if ang < min_turn:
            continue
        corners[i] = 'convex' if cross(tin, tout) > 0 else 'concave'
    terminals = set()
    for j in range(n):
        i = (j - 1) % n
        if segs[j]['type'] == 'line' and corners.get(i) == 'convex' and corners.get(j) == 'convex':
            if seg_len(starts[j], segs[j]) <= terminal_ratio * stem:
                terminals.add(j)
    return corners, terminals


def corner_cuts(contour, corners, terminals, r_convex, r_concave, max_cut=None, meets=(), swallow=None,
                min_chord=0.0):
    """Distances each segment is cut from its start and its end by the
    fillets (before the clamp), and each segment's length."""
    segs = to_segments(contour)
    n = len(segs)
    starts = [segs[i - 1]['end'] for i in range(n)]
    cut_start = [0.0] * n  # distance cut from segment start
    cut_end = [0.0] * n
    for i, kind in corners.items():
        j = (i + 1) % n
        _, tin = seg_dirs(starts[i], segs[i]); tout, _ = seg_dirs(starts[j], segs[j])
        ang = math.acos(max(-1, min(1, dot(tin, tout))))
        r = r_convex if kind == 'convex' else r_concave
        d = r * math.tan(ang / 2)
        if min_chord and ang < math.pi - 1e-3:
            # no fillet shorter than min_chord (a few units at Thin)
            d = max(d, min_chord / (2 * math.cos(ang / 2)))
        if max_cut is not None:
            # acute corners: a smaller radius, so the point keeps its place
            d = min(d, max_cut)
        cut_end[i] = d; cut_start[j] = d
    # Terminals: exactly half of the end line on both sides.
    for j in terminals:
        L = seg_len(starts[j], segs[j])
        cut_start[j] = cut_end[j] = L / 2
        cut_end[(j - 1) % n] = L / 2
        cut_start[(j + 1) % n] = L / 2
    # Lines the fillets would use up: the two fillets meet at the middle,
    # each keeping its own reach on the other side.
    for j in meets:
        L = seg_len(starts[j], segs[j])
        cut_start[j] = cut_end[j] = L / 2
    # Short lines one fillet would leave a sliver of: the fillet takes all of it.
    for j, side in (swallow or {}).items():
        L = seg_len(starts[j], segs[j])
        if side == 'start':
            cut_start[j] = L
        else:
            cut_end[j] = L
    lengths = [seg_len(starts[j], segs[j]) for j in range(n)]
    return segs, starts, cut_start, cut_end, lengths


def fillet_contour(contour, corners, terminals, r_convex, r_concave, t_ref=None, alpha=0.0, max_cut=None,
                   meets=(), swallow=None, min_chord=0.0):
    """Round the listed corners. The same corners/terminals/meets must be
    passed for every master so the resulting structure matches.

    Returns {segment: (t0, t1)}, the parameters at which each curve segment
    was cut. With t_ref (the same dict from the reference master), each cut
    moves that share alpha of the way to the reference parameter, so the
    fillets meet their curves at matching points in every master."""
    swallow = swallow or {}
    segs, starts, cut_start, cut_end, _ = corner_cuts(contour, corners, terminals, r_convex, r_concave,
                                                      max_cut, meets, swallow, min_chord)
    n = len(segs)
    # Clamp cuts to what each segment can give.
    for j in range(n):
        L = seg_len(starts[j], segs[j])
        if j in terminals or j in meets or j in swallow:
            continue
        both = cut_start[j] > 0 and cut_end[j] > 0
        cap = (0.5 if both else 0.62) * L if segs[j]['type'] == 'line' else (0.42 if both else 0.55) * L
        cut_start[j] = min(cut_start[j], cap); cut_end[j] = min(cut_end[j], cap)
    linedir = [unit(sub(segs[j]['end'], starts[j])) if segs[j]['type'] == 'line' else None for j in range(n)]
    # Cut every segment.
    used = {}
    newsegs = []  # list of (start, seg) after cutting
    for j in range(n):
        s0 = starts[j]; seg = segs[j]
        if seg['type'] == 'line':
            d = unit(sub(seg['end'], s0))
            a = add(s0, mul(d, cut_start[j])); b = sub(seg['end'], mul(d, cut_end[j]))
            newsegs.append((a, {'type': 'line', 'ctrl': [], 'end': b, 'smooth': seg['smooth']}))
        else:
            p = seg_points(s0, seg)
            t0 = param_at_chord(p, cut_start[j]) if cut_start[j] > 0 else 0.0
            t1 = param_at_chord(p, cut_end[j], from_end=True) if cut_end[j] > 0 else 1.0
            if t_ref and alpha and j in t_ref:
                r0, r1 = t_ref[j]
                t0 += alpha * (r0 - t0)
                t1 += alpha * (r1 - t1)
            if t1 <= t0:
                t1 = min(1.0, t0 + 1e-3)
            used[j] = (t0, t1)
            q = sub_curve(p, t0, t1)
            newsegs.append((q[0], {'type': 'curve', 'ctrl': [q[1], q[2]], 'end': q[3], 'smooth': seg['smooth']}))
    # Assemble: for each corner after segment i insert a fillet curve.
    out = []
    first_fillet = False
    for j in range(n):
        a, seg = newsegs[j]
        i = (j - 1) % n
        if i in corners:
            # fillet from end of newsegs[i] to a
            pa = newsegs[i][1]['end']
            tin = linedir[i] if segs[i]['type'] == 'line' else seg_dirs(newsegs[i][0], newsegs[i][1])[1]
            tout = linedir[j] if seg['type'] == 'line' else seg_dirs(a, seg)[0]
            if out:
                out[-1]['smooth'] = True   # the fillet leaves this point tangentially
            else:
                first_fillet = True
            out.append(fillet_seg(pa, a, tin, tout))
        if j in terminals or j in meets or j in swallow:
            continue  # zero-length line between two fillets: dropped
        out.append(seg)
    if first_fillet:
        out[-1] = dict(out[-1], smooth=True)
    # The contour start must be an on-curve point: from_segments uses last end.
    from_segments(contour, out)
    return used


def fillet_seg(p, q, tin, tout):
    """A round join from p (leaving along tin) to q (arriving along tout).
    Each handle is the circular-arc share of its own side's distance to the
    corner where the two tangents meet, so an unequal pair of cuts gives an
    even, never reversed, join."""
    chord = norm(sub(q, p))
    ang = math.acos(max(-1, min(1, dot(tin, tout))))
    den = cross(tin, tout)
    if ang < 1e-4 or chord < 1e-6 or abs(den) < 1e-9:
        h1 = h2 = chord / 3
    else:
        d = sub(q, p)
        s1 = cross(d, tout) / den      # p + s1*tin = corner
        s2 = cross(d, tin) / den       # q - s2*tout = corner
        k = 4 / 3 * math.tan(ang / 4) / math.tan(ang / 2) if ang < math.pi - 1e-3 else 4 / 3
        if s1 > 0 and s2 > 0:
            h1, h2 = k * s1, k * s2
        else:
            r = chord / (2 * math.sin(ang / 2))
            h1 = h2 = 4 / 3 * math.tan(ang / 4) * r
    return {'type': 'curve', 'ctrl': [add(p, mul(tin, h1)), sub(q, mul(tout, h2))], 'end': q, 'smooth': True}


# ---------------------------------------------------------------- tension

def tension_contour(contour, alpha, min_len=8):
    """Push cubic handles toward the tangent intersection (squarer curves).
    Only convex arcs whose two handles meet ahead of both ends are changed."""
    segs = to_segments(contour)
    n = len(segs)
    starts = [segs[i - 1]['end'] for i in range(n)]
    for j, seg in enumerate(segs):
        if seg['type'] != 'curve':
            continue
        p0, p1, p2, p3 = starts[j], seg['ctrl'][0], seg['ctrl'][1], seg['end']
        d0 = sub(p1, p0); d3 = sub(p2, p3)
        if norm(d0) < min_len or norm(d3) < min_len:
            continue
        den = cross(d0, d3)
        if abs(den) < 1e-6:
            continue
        w = sub(p3, p0)
        a = cross(w, d3) / den     # p0 + a*d0 is the intersection
        b = cross(w, d0) / den     # p3 + b*d3
        if a <= 1.0 or b <= 1.0:
            continue
        # current fractions toward the intersection, then move them
        f0 = 1 / a; f3 = 1 / b
        nf0 = f0 + alpha * (1 - f0); nf3 = f3 + alpha * (1 - f3)
        nf0 = min(nf0, 0.82); nf3 = min(nf3, 0.82)
        seg['ctrl'] = [add(p0, mul(d0, nf0 * a)), add(p3, mul(d3, nf3 * b))]
    from_segments(contour, segs)


# ---------------------------------------------------------------- shapes

K = 0.5522847498


def ellipse(cx, cy, rx, ry, ccw=True):
    """Four-segment ellipse starting at the bottom point."""
    b, r, t, l = (cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)
    if ccw:
        seq = [b, (cx + K * rx, cy - ry), (cx + rx, cy - K * ry), r, (cx + rx, cy + K * ry), (cx + K * rx, cy + ry), t,
               (cx - K * rx, cy + ry), (cx - rx, cy + K * ry), l, (cx - rx, cy - K * ry), (cx - K * rx, cy - ry)]
    else:
        seq = [b, (cx - K * rx, cy - ry), (cx - rx, cy - K * ry), l, (cx - rx, cy + K * ry), (cx - K * rx, cy + ry), t,
               (cx + K * rx, cy + ry), (cx + rx, cy + K * ry), r, (cx + rx, cy - K * ry), (cx + K * rx, cy - ry)]
    pts = []
    for i, (x, y) in enumerate(seq):
        pts.append(Point(x, y, 'curve' if i % 3 == 0 else None, i % 3 == 0))
    return Contour(points=pts)


# ---------------------------------------------------------------- measuring

def crossings(glyph, y, font=None, steps=48):
    """Sorted x positions where the outline crosses the horizontal line y."""
    g = glyph
    if font is not None and glyph.components:
        g = glyph.copy(); decompose(font, g)
    xs = []
    for c in g.contours:
        segs = to_segments(c)
        start = segs[-1]['end']
        for s in segs:
            if s['type'] == 'curve':
                pts = [bez(start, s['ctrl'][0], s['ctrl'][1], s['end'], i / steps) for i in range(steps + 1)]
            else:
                pts = [start, s['end']]
            for a, b in zip(pts, pts[1:]):
                if (a[1] - y) * (b[1] - y) < 0:
                    xs.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
            start = s['end']
    return sorted(xs)


def stem_width(glyph, y, font=None):
    xs = crossings(glyph, y, font)
    return xs[1] - xs[0] if len(xs) >= 2 else None


def piecewise(x, pts):
    """Linear interpolation through sorted (x, y) pairs."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def inverse_piecewise(y, pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if min(y0, y1) <= y <= max(y0, y1):
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    raise ValueError(y)


# Strata Sans stems (H, opsz 14) by user weight, as a fraction of the em.
# Medium and SemiBold sit a little heavier than upstream (490, 580), so
# 400 -> 600 darkens text by about a third, as in the serif and mono.
SANS_WGHT_MAP = [(100, 100), (400, 400), (500, 495), (600, 590), (700, 670), (800, 780), (900, 900)]
SANS_STEMS = [(100, 46 / 2048), (400, 190 / 2048), (900, 404 / 2048)]


def sans_stem(user_w):
    return piecewise(piecewise(user_w, SANS_WGHT_MAP), SANS_STEMS)


# Shared vertical metrics (fractions of the em), from Strata Sans.
TYPO_ASC, TYPO_DESC = 0.96875, -0.24121


def set_metrics(fonts, upm, extra_margin=0):
    """Same typo/hhea line metrics in every face; win covers every master's bbox."""
    ymax, ymin = 0, 0
    for f in fonts:
        for g in f:
            b = bounds(g, f)
            if b:
                ymax = max(ymax, b[3]); ymin = min(ymin, b[1])
    asc, desc = round(TYPO_ASC * upm), round(TYPO_DESC * upm)
    for f in fonts:
        i = f.info
        i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = asc, desc, 0
        i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = asc, desc, 0
        i.openTypeOS2WinAscent = max(asc, int(math.ceil(ymax)) + extra_margin)
        i.openTypeOS2WinDescent = max(-desc, int(math.ceil(-ymin)) + extra_margin)
        # USE_TYPO_METRICS: lines follow the shared typo values everywhere;
        # win only prevents clipping.
        i.openTypeOS2Selection = sorted(set(i.openTypeOS2Selection or []) | {7})
    return asc, desc


# ---------------------------------------------------------------- weight

def _tangent(pts, i, step):
    n = len(pts)
    p = pts[i]
    for k in range(1, n):
        q = pts[(i + step * k) % n]
        v = (q.x - p.x, q.y - p.y) if step > 0 else (p.x - q.x, p.y - q.y)
        if math.hypot(*v) > 1e-6:
            return unit(v)
    return (1.0, 0.0)


def embolden(glyph, s, miter=3.0):
    """Thicken every stroke of the glyph's own contours by s units across
    vertical stems (thin with s < 0), in place, keeping the advance.

    Each on-curve point moves sideways by half of s times the horizontal part
    of its offset (miter) vector; off-curve points move with the on-curve
    point they belong to. Handles keep their directions, so smooth points stay
    smooth and every master keeps its point structure. Horizontal strokes keep
    their thickness, as in a heavier master of a contrasted design."""
    if not s or not glyph.contours:
        return
    area = 0.0
    for c in glyph.contours:
        pts = c.points
        area += sum(pts[i - 1].x * p.y - p.x * pts[i - 1].y for i, p in enumerate(pts))
    sign = 1.0 if area >= 0 else -1.0  # outer contours counter-clockwise: right-hand normal points out
    h = s / 2.0
    for c in glyph.contours:
        pts = c.points
        n = len(pts)
        on = [i for i, p in enumerate(pts) if p.type is not None]
        if n < 2 or not on:
            continue
        dx = {}
        for i in on:
            tin, tout = _tangent(pts, i, -1), _tangent(pts, i, 1)
            nin = (tin[1] * sign, -tin[0] * sign)
            nout = (tout[1] * sign, -tout[0] * sign)
            k = min(miter, 1.0 / max(1e-6, 1.0 + dot(tin, tout)))
            dx[i] = h * (nin[0] + nout[0]) * k
        new = {i: pts[i].x + dx[i] for i in on}
        for idx, i in enumerate(on):
            j = on[(idx + 1) % len(on)]
            run = []
            k = (i + 1) % n
            while k != j:
                run.append(k)
                k = (k + 1) % n
            for r, kk in enumerate(run):
                new[kk] = pts[kk].x + (dx[i] if r < len(run) / 2 else dx[j])
        for i, x in new.items():
            pts[i].x = x


def sample_glyphs(font, text):
    """Decomposed copies of the glyphs that set `text` (by cmap), with counts."""
    cmap = {}
    for g in font:
        for u in g.unicodes:
            cmap.setdefault(u, g.name)
    counts = {}
    for ch in text:
        name = cmap.get(ord(ch))
        if name:
            counts[name] = counts.get(name, 0) + 1
    out = {}
    for name in counts:
        g = font[name].copy()
        decompose(font, g)
        out[name] = g
    return out, counts


def ink(glyphs, counts, upm, bold=0.0):
    """Outline area of the sample in em squared, after an optional embolden."""
    from fontTools.pens.areaPen import AreaPen
    total = 0.0
    for name, g in glyphs.items():
        if bold:
            g = g.copy()
            embolden(g, bold)
        pen = AreaPen()
        g.draw(pen)
        total += abs(pen.value) * counts[name]
    return total / upm ** 2


def solve_bold(glyphs, counts, upm, target, lo=-120.0, hi=160.0):
    """Embolden amount that brings the sample's ink to target (bisection)."""
    for _ in range(36):
        mid = (lo + hi) / 2
        if ink(glyphs, counts, upm, mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


INK_SAMPLE = ('A quiet afternoon before the rain. Showers arrive near 18:30, mostly light; '
              'winds turn west at 12 mph and the high reaches 72 degrees.')
