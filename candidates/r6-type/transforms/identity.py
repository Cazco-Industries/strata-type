"""Strata Sans identity: axis-cut terminals, open apertures, squarer rounds.

Every decision is taken once on the Regular text master (m02) and the same
plan is applied to every master, so the masters stay compatible:

- Terminals. A curved stroke that ends in a straight cut (a short line
  between two corners, where the curves on either side run in opposite
  directions) is re-cut on an axis: horizontally when the stroke ends while
  running up or down (c e s a g, C G S, 2 3 5 6 9), vertically when it ends
  while running sideways (t f r). The cut is then moved back along the
  stroke, which opens the aperture. Text masters open more than display
  masters: open and loose at text sizes, closed and calm at display sizes.
- Rounds. Curve handles are pushed toward their corner, so bowls, shoulders
  and round figures become slightly superelliptic. This is the trait the
  whole family shares (the mono uses the same operation, harder).
"""
import math
import unicodedata
import lib

REF = 'm02'
TEXT = {'m00', 'm02', 'm04'}
# Aperture opening, as a fraction of the master's stem (plus a fixed part).
OPEN_TEXT = (36, 0.40)
OPEN_DISPLAY = (0, 0.08)
# Never use more than this share of the room the curves allow.
ROOM = 0.5
# A trim that would leave a curve piece shorter than this many stems next
# to the cut (a cluster of points) is not made: the cut turns onto the axis
# about its midpoint instead, its neighbouring handles moving with it.
STUB = 0.45
# How far curve handles move toward their corner (0 = unchanged).
TENSION = 0.20
SKIP = {'.notdef', 'ampersand', 'ampersand.1'}


def stem(font):
    g = font['H']
    ux = sorted(set(round(p.x) for c in g.contours for p in c.points))
    return ux[1] - ux[0]


def coord(p, axis):
    return p[1] if axis == 'h' else p[0]


def find_param(p, axis, value, from_end):
    """Parameter where the cubic p crosses coord == value, searching from
    the given end. None when the curve never reaches it."""
    n = 64
    ts = [i / n for i in range(n + 1)]
    if from_end:
        ts = ts[::-1]
    prev_t, prev_v = ts[0], coord(lib.bez(*p, ts[0]), axis) - value
    if abs(prev_v) < 1e-9:
        return prev_t
    for t in ts[1:]:
        v = coord(lib.bez(*p, t), axis) - value
        if prev_v * v <= 0:
            lo, hi = (prev_t, t)
            vlo = prev_v
            for _ in range(50):
                mid = (lo + hi) / 2
                vm = coord(lib.bez(*p, mid), axis) - value
                if vlo * vm <= 0:
                    hi = mid
                else:
                    lo, vlo = mid, vm
            return (lo + hi) / 2
        prev_t, prev_v = t, v
    return None


def terminal_candidates(contour, st):
    """(segment index, axis, sign) for each curved stroke end."""
    segs = lib.to_segments(contour)
    n = len(segs)
    starts = [segs[i - 1]['end'] for i in range(n)]
    out = []
    for j, s in enumerate(segs):
        if s['type'] != 'line':
            continue
        i, k = (j - 1) % n, (j + 1) % n
        if segs[i]['type'] != 'curve' or segs[k]['type'] != 'curve':
            continue
        if segs[i]['smooth'] or s['smooth']:
            continue
        L = lib.seg_len(starts[j], s)
        if not (0.55 * st <= L <= 1.45 * st):
            continue
        _, t_in = lib.seg_dirs(starts[i], segs[i])
        t_out, _ = lib.seg_dirs(starts[k], segs[k])
        if lib.dot(t_in, t_out) > -0.5:
            continue
        u = lib.unit(lib.sub(t_in, t_out))  # the direction the stroke ends in
        axis = 'h' if abs(u[1]) >= abs(u[0]) else 'v'
        sign = (1 if u[1] > 0 else -1) if axis == 'h' else (1 if u[0] > 0 else -1)
        out.append((j, axis, sign))
    return out


def plan(font, names):
    st = stem(font)
    result = {}
    for name in names:
        g = font[name]
        cuts = []
        for ci, c in enumerate(g.contours):
            for j, axis, sign in terminal_candidates(c, st):
                cuts.append((ci, j, axis, sign))
        if cuts:
            result[name] = cuts
    return result


def cut_params(contour, j, axis, sign, extra):
    segs = lib.to_segments(contour)
    n = len(segs)
    i, k = (j - 1) % n, (j + 1) % n
    starts = [segs[x - 1]['end'] for x in range(n)]
    P, Q = starts[j], segs[j]['end']
    # Trim back from the end: both cut points move against the stroke.
    edge = min(coord(P, axis), coord(Q, axis)) if sign > 0 else max(coord(P, axis), coord(Q, axis))
    value = edge - sign * extra
    pi = lib.seg_points(starts[i], segs[i])
    pk = lib.seg_points(starts[k], segs[k])
    ti = find_param(pi, axis, value, from_end=True)
    tk = find_param(pk, axis, value, from_end=False)
    if ti is None or tk is None or ti < 0.2 or tk > 0.8:
        return None
    return segs, i, k, pi, pk, ti, tk, value


def max_extra(contour, j, axis, sign, hi=600.0):
    if cut_params(contour, j, axis, sign, 0.0) is None:
        return None
    lo = 0.0
    if cut_params(contour, j, axis, sign, hi) is not None:
        return hi
    for _ in range(30):
        mid = (lo + hi) / 2
        if cut_params(contour, j, axis, sign, mid) is None:
            hi = mid
        else:
            lo = mid
    return lo


def recut(contour, j, axis, sign, extra):
    """Cut the stroke end at segment j on the axis, `extra` units back from
    the cut's innermost point. Returns False if a curve cannot reach it."""
    r = cut_params(contour, j, axis, sign, extra)
    if r is None:
        return False
    segs, i, k, pi, pk, ti, tk, value = r
    a = list(lib.sub_curve(pi, 0.0, ti))
    b = list(lib.sub_curve(pk, tk, 1.0))
    # Snap the cut exactly onto the axis.
    if axis == 'h':
        a[3] = (a[3][0], value); b[0] = (b[0][0], value)
    else:
        a[3] = (value, a[3][1]); b[0] = (value, b[0][1])
    segs[i] = {**segs[i], 'ctrl': [a[1], a[2]], 'end': a[3]}
    segs[j] = {**segs[j], 'end': b[0]}
    segs[k] = {**segs[k], 'ctrl': [b[1], b[2]]}
    lib.from_segments(contour, segs)
    return True


def stubs(contour, j, axis, sign, extra):
    """Chord lengths of the two curve pieces a trim would leave."""
    r = cut_params(contour, j, axis, sign, extra)
    if r is None:
        return None
    _, i, k, pi, pk, ti, tk, _ = r
    a = lib.norm(lib.sub(lib.bez(*pi, ti), pi[0]))
    b = lib.norm(lib.sub(pk[3], lib.bez(*pk, tk)))
    return a, b


def rotate_cut(contour, j, axis):
    """Turn the cut at segment j onto the axis about its midpoint; each cut
    point's neighbouring handle moves with it."""
    segs = lib.to_segments(contour)
    n = len(segs)
    i, k = (j - 1) % n, (j + 1) % n
    P, Q = segs[i]['end'], segs[j]['end']
    v = (coord(P, axis) + coord(Q, axis)) / 2

    def moved(pt, d):
        return (pt[0], pt[1] + d) if axis == 'h' else (pt[0] + d, pt[1])
    dP, dQ = v - coord(P, axis), v - coord(Q, axis)
    segs[i] = {**segs[i], 'end': moved(P, dP), 'ctrl': [segs[i]['ctrl'][0], moved(segs[i]['ctrl'][1], dP)]}
    segs[j] = {**segs[j], 'end': moved(Q, dQ)}
    segs[k] = {**segs[k], 'ctrl': [moved(segs[k]['ctrl'][0], dQ), segs[k]['ctrl'][1]]}
    lib.from_segments(contour, segs)


def eligible(font):
    """Letters, figures and the question mark: by Unicode category, with
    unencoded alternates following their encoded base name."""
    cmap = {}
    for g in font:
        for u in g.unicodes:
            cmap.setdefault(g.name, u)
    out = []
    for g in font:
        if not g.contours or g.name in SKIP:
            continue
        u = cmap.get(g.name) or cmap.get(g.name.split('.')[0])
        if u is None:
            continue
        cat = unicodedata.category(chr(u))
        if cat[0] == 'L' or cat == 'Nd' or u == 0x3F:
            out.append(g.name)
    return out


# Each optical size is planned on its Regular master; the other weights cut
# their terminals at the same curve parameters, so the cuts correspond and
# interpolate (and the joins Rounded makes there stay smooth between weights).
GROUPS = {'m02': ('m00', 'm02', 'm04'), 'm03': ('m01', 'm03', 'm05')}


def transferred_extra(contour, j, axis, sign, i, k, ti, tk):
    """Trim for `contour` that cuts its curves at parameters ti and tk (the
    reference master's), with the cut on the axis at their mean position."""
    segs = lib.to_segments(contour)
    n = len(segs)
    starts = [segs[x - 1]['end'] for x in range(n)]
    pi = lib.seg_points(starts[i], segs[i])
    pk = lib.seg_points(starts[k], segs[k])
    v = (coord(lib.bez(*pi, ti), axis) + coord(lib.bez(*pk, tk), axis)) / 2
    P, Q = starts[j], segs[j]['end']
    edge = min(coord(P, axis), coord(Q, axis)) if sign > 0 else max(coord(P, axis), coord(Q, axis))
    return sign * (edge - v)


def terminals(masters, names=None, ref_name=REF, groups=None, text=TEXT):
    """Axis-cut terminals. Each group's reference master plans and cuts;
    its members take the same curve parameters. Text-size groups open their
    apertures more than display groups."""
    groups = groups or GROUPS
    ref = masters[ref_name]
    names = names or eligible(ref)
    cuts = plan(ref, names)
    # Validate on every master first, so a glyph is either changed
    # everywhere or nowhere.
    applied = {}
    rotated = []
    st_ref = stem(ref)
    for name, items in sorted(cuts.items()):
        trial = {m: f[name].copy() for m, f in masters.items()}
        ok = True
        for ci, j, axis, sign in items:
            # decided once, on the reference master
            R0 = ref[name].contours[ci]
            room0 = max_extra(R0, j, axis, sign)
            if room0 is not None:
                base0, kk0 = OPEN_TEXT if ref_name in text else OPEN_DISPLAY
                sb = stubs(R0, j, axis, sign, min(base0 + kk0 * st_ref, ROOM * room0))
                if sb is not None and min(sb) < STUB * st_ref:
                    for m in trial:
                        rotate_cut(trial[m].contours[ci], j, axis)
                    rotated.append(name)
                    continue
            for gref, members in groups.items():
                R = trial[gref].contours[ci]
                base, kk = OPEN_TEXT if gref in text else OPEN_DISPLAY
                room = max_extra(R, j, axis, sign)
                if room is None:
                    ok = False
                    break
                # never use more than half the room the curves allow
                extra = min(base + kk * stem(masters[gref]), ROOM * room)
                r = cut_params(R, j, axis, sign, extra)
                if r is None:
                    ok = False
                    break
                _, i, k, _, _, ti, tk, _ = r
                trims = {}
                for m in members:
                    c = trial[m].contours[ci]
                    e = extra if m == gref else transferred_extra(c, j, axis, sign, i, k, ti, tk)
                    if e < 0:
                        ok = False
                        break
                    trims[m] = e
                if not ok:
                    break
                for m, e in trims.items():
                    if not recut(trial[m].contours[ci], j, axis, sign, e):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if not ok:
            continue
        for m, g in trial.items():
            dst = masters[m][name]
            dst.clearContours()
            for c in g.contours:
                dst.contours.append(c)
        applied[name] = items
    if rotated:
        print('terminals turned onto the axis without a trim (short curve left):', ' '.join(sorted(set(rotated))), flush=True)
    return applied


# ------------------------------------------------------------------ rounds

def tension_plan(contour, alpha, min_len=8):
    segs = lib.to_segments(contour)
    n = len(segs)
    starts = [segs[i - 1]['end'] for i in range(n)]
    ok = []
    for j, seg in enumerate(segs):
        if seg['type'] != 'curve':
            continue
        p0, p1, p2, p3 = starts[j], seg['ctrl'][0], seg['ctrl'][1], seg['end']
        d0 = lib.sub(p1, p0); d3 = lib.sub(p2, p3)
        if lib.norm(d0) < min_len or lib.norm(d3) < min_len:
            continue
        den = lib.cross(d0, d3)
        if abs(den) < 1e-6:
            continue
        w = lib.sub(p3, p0)
        a = lib.cross(w, d3) / den
        b = lib.cross(w, d0) / den
        if a <= 1.0 or b <= 1.0:
            continue
        # quarter-ish arcs only: the turn between the end tangents
        ang = math.degrees(math.acos(max(-1, min(1, lib.dot(lib.unit(d0), lib.unit(lib.mul(d3, -1)))))))
        if ang < 45 or ang > 135:
            continue
        ok.append(j)
    return ok


def apply_tension(contour, plan_segs, alpha):
    segs = lib.to_segments(contour)
    n = len(segs)
    starts = [segs[i - 1]['end'] for i in range(n)]
    for j in plan_segs:
        seg = segs[j]
        p0, p1, p2, p3 = starts[j], seg['ctrl'][0], seg['ctrl'][1], seg['end']
        d0 = lib.sub(p1, p0); d3 = lib.sub(p2, p3)
        den = lib.cross(d0, d3)
        if abs(den) < 1e-6:
            continue
        w = lib.sub(p3, p0)
        a = lib.cross(w, d3) / den
        b = lib.cross(w, d0) / den
        if a <= 1.0 or b <= 1.0:
            continue
        f0 = 1 / a; f3 = 1 / b
        nf0 = min(f0 + alpha * (1 - f0), 0.80); nf3 = min(f3 + alpha * (1 - f3), 0.80)
        seg['ctrl'] = [lib.add(p0, lib.mul(d0, nf0 * a)), lib.add(p3, lib.mul(d3, nf3 * b))]
    lib.from_segments(contour, segs)


class _Rounded:
    """A font seen with one glyph's points rounded to integers, as a face
    that rounds will save them (short segments can turn enough in rounding
    to matter); with whole=False the points are kept as they are."""
    def __init__(self, font, name, whole=True):
        self.font, self.name = font, name
        self.glyph = font[name].copy()
        if whole:
            lib.round_glyph(self.glyph)

    def __getitem__(self, key):
        if key == self.name:
            return self.glyph
        return self.font[key] if key in self.font else None

    def __contains__(self, key):
        return key in self.font

    def keys(self):
        return self.font.keys()


def kinks(masters, name):
    """Interpolation kinks in one glyph, with masters compared as a chain in
    source order (m00, m01, ...), the way the gate's check compares them.
    Returns (count with points rounded to integers, count with points as
    they are): some faces round before saving and some do not."""
    from fontTools.varLib.interpolatable import test_gen
    order = sorted(masters)
    upem = masters[order[0]].info.unitsPerEm
    counts = []
    for whole in (True, False):
        gs = [_Rounded(masters[m], name, whole) for m in order]
        counts.append(sum(1 for _, p in test_gen(gs, glyphs=[name], names=order, upem=upem) if p['type'] == 'kink'))
    return tuple(counts)


def _points(masters, name):
    return {m: [[(p.x, p.y) for p in c.points] for c in f[name].contours] for m, f in masters.items()}


def _restore(masters, name, state):
    for m, f in masters.items():
        for c, pts in zip(f[name].contours, state[m]):
            for p, (x, y) in zip(c.points, pts):
                p.x, p.y = x, y


def rounds(masters, alpha=TENSION, names=None, ref_name=REF):
    """Squarer rounds. A glyph whose rounds would add an interpolation kink
    (a smooth point whose handles turn and change length between masters)
    is left as it was."""
    ref = masters[ref_name]
    names = names or [g.name for g in ref if g.contours and g.name not in SKIP]
    count = 0
    kept = []
    for name in names:
        g = ref[name]
        plans = [tension_plan(c, alpha) for c in g.contours]
        if not any(plans):
            continue
        if any(not lib.same_structure(g, f[name]) for f in masters.values()):
            continue
        before = _points(masters, name)
        for f in masters.values():
            for c, p in zip(f[name].contours, plans):
                if p:
                    apply_tension(c, p, alpha)
        k1 = kinks(masters, name)
        if any(k1):
            after = _points(masters, name)
            _restore(masters, name, before)
            k0 = kinks(masters, name)
            if any(a > b for a, b in zip(k1, k0)):
                kept.append(name)
                continue
            _restore(masters, name, after)
        count += 1
    if kept:
        print('rounds left unchanged (would kink):', ' '.join(kept), flush=True)
    return count


# ------------------------------------------------------------------ y

def y_tail(masters, names=('y',)):
    """The y's descender ends in a vertical cut, like the t and f ends:
    the two on-curve points of its tail end (the leftmost below the
    baseline, found on the Regular) move onto their mean x."""
    for name in names:
        g = masters[REF][name]
        idx = []
        for ci, c in enumerate(g.contours):
            for pi, p in enumerate(c.points):
                if p.type is not None and p.y < 0:
                    idx.append((p.x, ci, pi))
        idx.sort()
        pick = [(ci, pi) for _, ci, pi in idx[:2]]
        for f in masters.values():
            pts = [f[name].contours[ci].points[pi] for ci, pi in pick]
            x = sum(p.x for p in pts) / len(pts)
            for p in pts:
                p.x = x


# ------------------------------------------------------------------ R

# The R leg's inner edge meets the stem this many stems inside the stem's
# right edge, at the height of the bar's lower edge.
LEG_INTO = 0.03


def r_leg(masters):
    """R's straight leg springs from the stem where the bowl's lower bar
    leaves it: a wider, steadier stance, and no step or notch between the
    bar and the leg. The leg's inner edge, kept on its bottom point, is aimed
    at the corner of the stem and the bar's lower edge; both top points move
    by the same amount, so the leg keeps its thickness."""
    for f in masters.values():
        st = stem(f)
        g = f['R']
        leg = [c for c in g.contours if len(c.points) == 4]
        bowl = [c for c in g.contours if c not in leg]
        assert len(leg) == 1 and len(bowl) == 1, 'R outline changed'
        P = leg[0].points
        bl = min((p for p in P if p.y < 10), key=lambda p: p.x)
        tops = sorted(P, key=lambda p: -p.y)[:2]
        tl = min(tops, key=lambda p: p.x)
        on = [p for p in bowl[0].points if p.type is not None]
        sr = min(p.x for p in on) + st
        bar = min(p.y for p in on if p.y > 10)
        tx, ty = sr - LEG_INTO * st, bar
        x = bl.x + (tl.y - bl.y) * (tx - bl.x) / (ty - bl.y)
        dx = x - tl.x
        for p in tops:
            p.x += dx
