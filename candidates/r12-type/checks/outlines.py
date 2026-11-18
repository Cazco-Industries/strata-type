"""Outline hygiene: per glyph point counts and kinks against the upstream
master, so transforms cannot quietly add clusters, notches or extra points.

For every face and master, each glyph's outline (components decomposed) is
compared with the upstream glyph that holds the same drawing in the
baseline master (`com.strata.source` in the glyph lib when a transform moved
a drawing to another name; otherwise the same name). Rounded has no
upstream of its own: it is compared with the finished sans glyph of the same
name, for kinks, fold-backs and degenerate segments only: its fillets add
points by design, and a round pen at Thin makes joins only 5-12 units
long, so for Rounded `short` counts segments under SHORT_ROUNDED em.

Counted per outline:
  points  - every point, on- and off-curve
  kinks   - on-curve joins that are nearly smooth but not quite: a turn of
            KINK_MIN..KINK_MAX degrees where at least one side is a curve, or
            any turn over SMOOTH_TOL on a point flagged smooth
  short   - segments shorter than SHORT em (clusters of points; 12 units
            on the sans's 2048-unit em, 5.9 on the serif's 1000)
  back    - curve segments that fold back on themselves: the control
            polygon turns through more than 180 degrees one way (a loop
            or cusp), or a handle points against its neighbour handle's
            run on a segment that turns less than 90 degrees

A glyph is an outlier in a master when it gains a kink, a short segment or a
backward handle over its upstream, or gains more than POINT_GAIN points and
POINT_SHARE of its upstream count. The default-instance TrueType outlines are
compared the same way for point counts (quadratic conversion can add points
to taut curves). Only glyphs that own contours are measured (composites
repeat their components' counts).

Kinks, fold-backs and point growth fail the check; new short segments
are counted and reported but do not fail it (the serif's stroke gain and
its lowercase remap shorten some serif-bracket pieces below 0.006 em, which
no renderer shows).

The check gates the core set (the characters of U+0020-U+007E and
` deg % minus 1/2 1/4 3/4 degF degC +-`, with their proportional,
tabular, case and figure-context forms) in the text and display masters m00-m05, and every
Rounded master; any outlier there fails it. The full repertoire, the
caption masters (m06-m08, made by emboldening) and the TrueType point
counts (the compiler's quadratic pieces, which grow with squarer rounds)
are counted and reported without gating.

Usage (repository root):
    .venv/bin/python -I candidates/r12-type/checks/outlines.py [CAND] [--json PATH]
"""
import json
import math
import sys
from pathlib import Path

import ufoLib2
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE_KEY = 'com.strata.source'
KINK_MIN, KINK_MAX = 3.0, 25.0
SMOOTH_TOL = 2.0
SHORT = 12.0 / 2048
SHORT_ROUNDED = 4.0 / 2048
POINT_GAIN, POINT_SHARE = 4, 0.15
TT_GAIN, TT_SHARE = 5, 0.15
OUTLIER_FAIL = 1
CORE_CPS = list(range(0x20, 0x7F)) + [0xB0, 0x2212, 0xBD, 0xBC, 0xBE, 0x2109, 0x2103, 0xB1]
GATED_MASTERS = {'m00', 'm01', 'm02', 'm03', 'm04', 'm05'}


def core_names(font):
    cmap = {}
    for g in font:
        for u in g.unicodes:
            cmap[u] = g.name
    base = {cmap[c] for c in CORE_CPS if c in cmap}
    out = set(base)
    for n in font.keys():
        stem = n.split('.')[0]
        if stem in base and any(t in n.split('.')[1:] for t in ('pnum', 'tf', 'case', 'fig')):
            out.add(n)
    return out
FACES = {
    'sans': ('sans', 'StrataSans', 9),
    'serif': ('serif', 'StrataSerif', 9),
    'mono': ('mono', 'StrataMono', 2),
}
# Glyphs whose drawing a transform builds from scratch (no upstream to match).
REBUILT = {
    'sans': {'degree'},
    'mono': {'degree', 'uni2103', 'uni2109', 'plus_plus.liga', 'plus_plus_plus.liga'},
    'serif': set(),
}


def _unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n) if n > 1e-9 else None


def contours(glyphset, name):
    """Decomposed contours as lists of (x, y, kind, smooth) from the UFO points."""
    out = []
    g = glyphset[name]
    stack = [(g, (1, 0, 0, 1, 0, 0))]
    while stack:
        gl, t = stack.pop()
        a, b, c, d, e, f = t
        for con in gl.contours:
            out.append([(a * p.x + c * p.y + e, b * p.x + d * p.y + f, p.type, p.smooth) for p in con.points])
        for comp in gl.components:
            if comp.baseGlyph not in glyphset:
                continue
            ta = comp.transformation
            # compose: outer t after inner ta
            na = a * ta[0] + c * ta[1]
            nb = b * ta[0] + d * ta[1]
            nc = a * ta[2] + c * ta[3]
            nd = b * ta[2] + d * ta[3]
            ne = a * ta[4] + c * ta[5] + e
            nf = b * ta[4] + d * ta[5] + f
            stack.append((glyphset[comp.baseGlyph], (na, nb, nc, nd, ne, nf)))
    return out


def _turn(a, b):
    """Signed angle in degrees from direction a to direction b."""
    return math.degrees(math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]))


def folds(p, h1, h2, q):
    """True when a cubic segment folds back: its control polygon turns more
    than 180 degrees one way, or, on a segment whose ends turn less than 90
    degrees, a handle points backwards along the chord."""
    legs = [(h1[0] - p[0], h1[1] - p[1]), (h2[0] - h1[0], h2[1] - h1[1]), (q[0] - h2[0], q[1] - h2[1])]
    legs = [v for v in legs if math.hypot(*v) > 0.5]
    if len(legs) < 2:
        return False
    total = sum(_turn(a, b) for a, b in zip(legs, legs[1:]))
    if abs(total) > 181:
        return True
    d1 = (h1[0] - p[0], h1[1] - p[1]) if math.hypot(h1[0] - p[0], h1[1] - p[1]) > 0.5 else None
    d2 = (q[0] - h2[0], q[1] - h2[1]) if math.hypot(q[0] - h2[0], q[1] - h2[1]) > 0.5 else None
    if d1 and d2 and abs(_turn(d1, d2)) < 90:
        chord = (q[0] - p[0], q[1] - p[1])
        if d1[0] * chord[0] + d1[1] * chord[1] < -1 or d2[0] * chord[0] + d2[1] * chord[1] < -1:
            return True
    return False


def measure(cons, upm, short=SHORT):
    short_lim = short * upm
    pts = kinks = short = back = 0
    for con in cons:
        n = len(con)
        pts += n
        if n < 2:
            continue
        on = [i for i, p in enumerate(con) if p[2] is not None]
        for i in on:
            p = con[i]
            # incoming: previous distinct point; outgoing: next distinct point
            def nb(step):
                k = i
                for _ in range(n):
                    k = (k + step) % n
                    q = con[k]
                    if math.hypot(q[0] - p[0], q[1] - p[1]) > 0.5:
                        return q
                return None
            prv, nxt = nb(-1), nb(1)
            if prv is None or nxt is None:
                continue
            tin = _unit((p[0] - prv[0], p[1] - prv[1]))
            tout = _unit((nxt[0] - p[0], nxt[1] - p[1]))
            if not tin or not tout:
                continue
            ang = math.degrees(math.acos(max(-1.0, min(1.0, tin[0] * tout[0] + tin[1] * tout[1]))))
            curve_in = con[(i - 1) % n][2] is None
            curve_out = con[(i + 1) % n][2] is None
            if p[3]:
                if ang > SMOOTH_TOL:
                    kinks += 1
            elif (curve_in or curve_out) and KINK_MIN < ang < KINK_MAX:
                kinks += 1
        # segments: on-curve to next on-curve
        for j, i in enumerate(on):
            k = on[(j + 1) % len(on)]
            p, q = con[i], con[k]
            if math.hypot(q[0] - p[0], q[1] - p[1]) < short_lim:
                short += 1
            span = (k - i) % n
            if span == 3 and folds(p, con[(i + 1) % n], con[(i + 2) % n], q):
                back += 1
    return {'points': pts, 'kinks': kinks, 'short': short, 'back': back}


def tt_points(font, name):
    glyf = font['glyf']
    if name not in glyf:
        return None
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[name].draw(pen)
    n = 0
    for op, args in pen.value:
        n += len(args)
    return n


def fallback(name, base):
    """Upstream name for a candidate that does not record its sources:
    proportional figures come from the default figure; drawings that the
    sans swaps with an alternate (G, 4, 3, 6, 9) come from the alternate."""
    n = name.replace('.pnum', '')
    for a, alt in (('G', '.1'), ('four', '.ss01'), ('three', '.1'), ('six', '.ss01'), ('nine', '.ss01')):
        if n == a or n.startswith(a + '.') and not n.startswith(a + alt):
            cand = a + alt + n[len(a):] if n != a else a + alt
            if cand in base:
                return cand
        if n.startswith(a + alt):
            plain = a + n[len(a + alt):]
            if plain in base:
                return plain
    return n


def outlier(c, u, face, name):
    why = []
    for k in ('kinks', 'short', 'back'):
        if c[k] > u[k]:
            why.append(f'{k} {u[k]}->{c[k]}')
    if name not in REBUILT.get(face, ()):
        gain = c['points'] - u['points']
        if gain > POINT_GAIN and gain > POINT_SHARE * max(1, u['points']):
            why.append(f"points {u['points']}->{c['points']}")
    return why


def check_face(cand, face):
    folder, prefix, count = FACES[face]
    cdir = ROOT / 'candidates' / cand / 'fonts' / folder
    bdir = ROOT / 'candidates' / 'baseline' / 'fonts' / folder
    rows = {}
    for i in range(count):
        m = f'm{i:02d}'
        cp, bp = cdir / f'{prefix}-{m}.ufo', bdir / f'{prefix}-{m}.ufo'
        if not cp.exists():
            continue
        # caption masters have no upstream of their own: their text master's upstream
        up_m = {'m06': 'm00', 'm07': 'm02', 'm08': 'm04'}.get(m, m) if not bp.exists() else m
        cf = ufoLib2.Font.open(cp, lazy=False)
        bf = ufoLib2.Font.open(bdir / f'{prefix}-{up_m}.ufo', lazy=False)
        recorded = any(SOURCE_KEY in g.lib for g in cf)
        if m == 'm00' or face == 'mono':
            core = core_names(cf)
        for g in cf:
            if not g.contours:
                continue
            src = g.lib.get(SOURCE_KEY) or (fallback(g.name, bf) if face == 'sans' and not recorded else g.name)
            if src not in bf:
                continue
            c = measure(contours(cf, g.name), cf.info.unitsPerEm)
            u = measure(contours(bf, src), bf.info.unitsPerEm)
            why = outlier(c, u, face, g.name)
            if why:
                rows.setdefault(g.name, {})[m] = why
    return rows, core


def check_rounded(cand):
    cdir = ROOT / 'candidates' / cand / 'fonts'
    rows = {}
    for i in range(9):
        m = f'm{i:02d}'
        rp = cdir / 'sans-rounded' / f'StrataSansRounded-{m}.ufo'
        sp = cdir / 'sans' / f'StrataSans-{m}.ufo'
        if not rp.exists():
            continue
        rf = ufoLib2.Font.open(rp, lazy=False)
        sf = ufoLib2.Font.open(sp, lazy=False)
        for g in rf:
            src = g.lib.get(SOURCE_KEY, g.name)
            if src not in sf or not g.contours:
                continue
            c = measure(contours(rf, g.name), rf.info.unitsPerEm, SHORT_ROUNDED)
            u = measure(contours(sf, src), sf.info.unitsPerEm, SHORT_ROUNDED)
            why = [f'{k} {u[k]}->{c[k]}' for k in ('kinks', 'short', 'back') if c[k] > u[k]]
            if why:
                rows.setdefault(g.name, {})[m] = why
    return rows


def check_tt(cand):
    out = {}
    for face, ttf in (('sans', 'StrataSans.ttf'), ('serif', 'StrataSerif.ttf'), ('mono', 'StrataMono.ttf')):
        cp = ROOT / 'build' / cand / ttf
        bp = ROOT / 'build' / 'baseline' / ttf
        if not cp.exists() or not bp.exists():
            continue
        cf, bf = TTFont(cp), TTFont(bp)
        folder, prefix, _ = FACES[face]
        ufo = ufoLib2.Font.open(ROOT / 'candidates' / cand / 'fonts' / folder / f'{prefix}-m02.ufo'
                                if face != 'mono' else
                                ROOT / 'candidates' / cand / 'fonts' / folder / f'{prefix}-m00.ufo')
        bnames = set(bf.getGlyphOrder())
        recorded = any(SOURCE_KEY in g.lib for g in ufo)
        rows = {}
        for name in cf.getGlyphOrder():
            src = (ufo[name].lib.get(SOURCE_KEY) if name in ufo else None) or (
                fallback(name, bnames) if face == 'sans' and not recorded else name)
            if src not in bnames or name in REBUILT.get(face, ()):
                continue
            c, u = tt_points(cf, name), tt_points(bf, src)
            if c is None or u is None:
                continue
            if c - u > TT_GAIN and c - u > TT_SHARE * max(1, u):
                rows[name] = f'{u}->{c}'
        out[face] = rows
    return out


def main(argv):
    cand = 'r12-type'
    js = None
    args = list(argv)
    if '--json' in args:
        k = args.index('--json'); js = args[k + 1]; del args[k:k + 2]
    if args:
        cand = args[0]
    report, cores = {}, {}
    for f in FACES:
        report[f], cores[f] = check_face(cand, f)
    report['rounded'] = check_rounded(cand)
    tt = check_tt(cand)
    gated = 0
    summary = {}
    for face in ('sans', 'rounded', 'serif', 'mono'):
        rows = report[face]
        core = cores.get(face)
        def is_gated(name, ms):
            if face == 'rounded':
                return True
            return name in core and any(m in GATED_MASTERS for m in ms)
        scope = {n: {m: w for m, w in ms.items() if face == 'rounded' or m in GATED_MASTERS}
                 for n, ms in rows.items() if is_gated(n, ms)}
        # kinks, fold-backs and point growth fail; short segments are reported
        g_rows = {n: {m: [x for x in w if not x.startswith('short')] for m, w in ms.items()} for n, ms in scope.items()}
        g_rows = {n: {m: w for m, w in ms.items() if w} for n, ms in g_rows.items()}
        g_rows = {n: ms for n, ms in g_rows.items() if ms}
        s_rows = {n: ms for n, ms in scope.items() if n not in g_rows}
        full_text = sum(1 for ms in rows.values() if any(m in GATED_MASTERS for m in ms))
        full_cap = sum(1 for ms in rows.values() if any(m not in GATED_MASTERS for m in ms))
        gated += len(g_rows)
        summary[face] = {'core': sorted(g_rows), 'core_short_only': sorted(s_rows),
                         'full_text_display': full_text, 'full_caption': full_cap}
        print(f'{face}: core outliers {len(g_rows)} (kinks, fold-backs, points); core glyphs with only new short '
              f'segments {len(s_rows)} (reported); full repertoire, any reason: {full_text} glyph(s) in text/display '
              f'masters, {full_cap} in caption masters (reported)')
        for name in sorted(g_rows):
            ms = g_rows[name]
            first = next(iter(ms.values()))
            print(f'  {name:24s} {",".join(sorted(ms))}: {"; ".join(first)}')
    for face, rows in tt.items():
        core = cores.get(face, set())
        crow = {n: v for n, v in rows.items() if n in core}
        summary[face + '_tt'] = {'core': sorted(crow), 'full': len(rows)}
        print(f'{face} TrueType default (reported): core {len(crow)} glyph(s) with extra points; full repertoire {len(rows)}')
        for name in sorted(crow):
            print(f'  {name:24s} {crow[name]}')
    if js:
        Path(js).write_text(json.dumps({'ufo': report, 'tt': tt, 'summary': summary}, indent=1, sort_keys=True))
    verdict = 'PASS' if gated < OUTLIER_FAIL else 'FAIL'
    print(f'outline hygiene (core set, text/display masters and Rounded): {gated} outlier(s): {verdict}')
    return 0 if verdict == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
