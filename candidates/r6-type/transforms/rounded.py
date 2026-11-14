"""Strata Sans Rounded: the Regular sans skeleton, only rounded.

Rounded is the finished sans, glyph for glyph, with round ends, corners and
joins and nothing else changed: the same construction, figure shapes,
key-letter transforms (tailed l, flat-top 3, open 4, straight-stem 6 and 9,
footed 1, axis-cut terminals), advances and kerning. It covers Basic Latin
(U+0020-U+007E) and ` deg % minus 1/2 1/4 3/4 degF degC +- fraction`
plus the figure, punctuation, thin and no-break spaces; the sans's
proportional figures (`pnum`), its case forms (`case`, and the `calt` rules
that pick them between figures and capitals, so "18:30" takes the raised
colon in both faces), and the sans's kerning groups and pairs for these
glyphs. Any string in this set sets the same width in both faces.

The rounding is a round pen: on the Regular master, every corner that
turns by 28 degrees or more is found once, and every master fillets the
same corners with radii in its own stems: R_CONVEX on outer corners,
R_CONCAVE on joins (inner corners), and a stroke end shorter than TERMINAL
stems becomes a full semicircle. A fillet never reaches more than MAX_CUT
stems along either side, so acute points (A, V, W, the 4's apex) keep their
place, and a corner that turns back by more than CUSP degrees (the crotch
where the 6's and 9's straight stems leave the bowl) keeps its point.
Curves are not touched: a round figure such as 0 is the sans's 0.

Every master (text, display and caption) is rounded from the sans master
of the same name (the caption masters from the sans's emboldened caption
outlines, so a small figure's short strokes keep their direction), so
Rounded's ink and spacing follow the sans display drawings at 40-96 px.
The pen's radii are set per weight (WEIGHT, R_CONVEX, R_CONCAVE, MAX_CUT)
in each master's own stems; a glyph whose fillets would kink at the full
pen takes the first smaller pen in PEN_STEPS that clears.
Where a glyph's fillets would kink between masters (on the cubic outlines
or on their quadratic conversion in the built font), or would leave a kink
in one master's outline that its sans master lacks, the curve cuts move
part of the way toward the curve points the Regular uses (the smallest
shares, text masters first, that clear both). Each master takes the
sans's glyph categories, so spacing accents with attaching anchors stay
base glyphs.
"""
import math
import re
import shutil
from pathlib import Path
import ufoLib2
from ufoLib2.objects import Font
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
import lib
import sans

MASTERS = {'m00': (14, 100), 'm01': (32, 100), 'm02': (14, 400),
           'm03': (32, 400), 'm04': (14, 900), 'm05': (32, 900),
           'm06': (8, 100), 'm07': (8, 400), 'm08': (8, 900)}
REF = 'm02'
TEXT = ('m00', 'm02', 'm04')
# display masters -> the text master of the same weight
DISPLAY = {'m01': 'm00', 'm03': 'm02', 'm05': 'm04'}
# Caption masters are rounded from the sans caption masters (Thin, Regular, Black).
CAPTION = ('m06', 'm07', 'm08')
FIGS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
# Round pen, in stems of each master, per weight: outer corners
# (R_CONVEX), joins (R_CONCAVE), the longest reach of a fillet along either
# side (MAX_CUT); a stroke end under TERMINAL stems becomes a semicircle.
# Thin and Regular take a concentric pen: the outer radius is the inner
# radius plus one stem, so a stroke keeps its width round a corner and an
# outer corner reads as a quarter circle at 24 px Regular (r3's pen, 0.60
# outside and 0.20 inside at every weight, thinned corners and read only as
# a softening). Black keeps r3's pen: its corners already read round, and
# its skeleton gate has the least room. With these radii the largest
# displaced region of the skeleton check is 3.68 at 400 (the G) and 3.37 at
# 900 (the M), under the 4.0 limit: the Regular pen cannot grow much more.
WEIGHT = {'m00': 'thin', 'm01': 'thin', 'm06': 'thin', 'm02': 'regular', 'm03': 'regular', 'm07': 'regular',
          'm04': 'black', 'm05': 'black', 'm08': 'black'}
R_CONVEX = {'thin': 1.80, 'regular': 1.70, 'black': 0.60}
R_CONCAVE = {'thin': 0.80, 'regular': 0.70, 'black': 0.20}
MAX_CUT = {'thin': 1.90, 'regular': 1.80, 'black': 0.90}
TERMINAL = 1.60
# Glyphs whose inner turns (the 7's elbow, the joins of the flat-top 3)
# take a softer join: R_CONCAVE times this.
SOFT_TURNS = {'seven', 'seven.pnum', 'three', 'three.pnum'}
SOFT_JOIN = 2.0
# The flat-top 3's upper turn: the sans ends the bar's underside in a step
# a few units long before the diagonal leaves it, so the notch under the
# bar fell under the MICRO rule and kept its point (a sharp V of white under
# the bar at hero sizes); filleting the step's two corners separately folds
# the curve into the bar. In these glyphs the step is first closed to the
# one corner where the underside and the diagonal meet (`merge_notch`, the
# same point in every master), which then takes the soft join like any
# other join.
SOFT_NOTCH = {'three', 'three.pnum'}
# The notch is acute (about 44 degrees of white), so its fillet is set by
# how far it may reach along the underside and the diagonal: NOTCH_CUT
# stems (every other corner of these glyphs is a stroke end, which reaches
# less). At the full MAX_CUT the filled notch read as a dark spot under the
# bar at 96 px.
NOTCH_CUT = 1.0

# Hero figures. The sans draws its bowls as squarish curves (handle
# tension 0.70-0.80 of the way to the corner of the tangents; a circle is
# 0.552), and a round pen does not touch curves, so at 32 px Rounded read as
# the sans. In the display masters only (opsz 32, the size Rounded is for),
# every quarter turn of a hero glyph (turning BOWL_TURN degrees, legs of at
# least BOWL_LEG stems) moves BOWL_SHARE of the way to circular tension:
# bowls, counters, the dots of . : and the rings of % become round. On-curve
# points and handle directions stay, so extremes, advances, stems at the
# extremes and interpolation structure are the sans's; only the shoulders
# move in. The text and caption masters keep the sans skeleton (the skeleton
# check runs at opsz 14), and the change fades in from opsz 14 to 32.
HERO = (set(FIGS) | {sans.pnum_name(f) for f in FIGS}
        | {'zero.slash', 'zero.pnum.slash', 'degree', 'percent', 'period', 'colon', 'colon.case', sans.FIG_COLON})
BOWL_K = 0.5523
BOWL_SHARE = 1.0
BOWL_SHARES = (1.0, 0.75, 0.5, 0.25)
BOWL_TURN = (80.0, 100.0)
BOWL_LEG = 0.5


# A glyph whose fillets kink at every share with the full pen takes the
# first smaller pen in PEN_STEPS (a share of every radius) that clears.
PEN_STEPS = (1.0, 0.85, 0.7, 0.55)
_pen = [1.0]


def radii(m, sm, name=None):
    """(convex, concave, max cut) in units for master m with stem sm."""
    w = WEIGHT[m]
    k = _pen[0]
    concave = R_CONCAVE[w] * (SOFT_JOIN if name in SOFT_TURNS else 1.0)
    cut = min(MAX_CUT[w], NOTCH_CUT) if name in SOFT_NOTCH else MAX_CUT[w]
    return R_CONVEX[w] * sm * k, concave * sm * k, cut * sm * k
# Characters Rounded covers: Basic Latin and the weather extras.
CODEPOINTS = list(range(0x20, 0x7F)) + [
    0xA0, 0xB0, 0xB1, 0xBC, 0xBD, 0xBE, 0x2007, 0x2008, 0x2009, 0x2044, 0x2103, 0x2109, 0x2212]
SPACES = {0x20, 0xA0, 0x2007, 0x2008, 0x2009}


def classes(text):
    """Every glyph class the sans features define, expanded."""
    raw = {m.group(1): m.group(2).split() for m in re.finditer(r'(@\w+) = \[([^\]]*)\];', text)}
    out = {}

    def expand(name, seen=()):
        if name in out:
            return out[name]
        items = []
        for t in raw.get(name, []):
            if t.startswith('@'):
                if t not in seen:
                    items += expand(t, seen + (name,))
            else:
                items.append(t)
        out[name] = items
        return items
    for n in raw:
        expand(n)
    return out


def glyph_set(sans_ref):
    """name -> unicodes for the glyphs Rounded draws (sans names)."""
    cmap = {}
    for g in sans_ref:
        for u in g.unicodes:
            cmap[u] = g.name
    want = set(CODEPOINTS)
    names = {}
    for u in CODEPOINTS:
        n = cmap[u]
        names.setdefault(n, [])
        names[n].append(u)
    for n in list(names):
        names[n] = sorted(u for u in sans_ref[n].unicodes if u in want)
    cl = classes(sans_ref.features.text)
    for a, b in zip(cl['@CASE_L'], cl['@CASE_R']):
        if a in names and b in sans_ref:
            names[b] = []
    for n in FIGS:
        names[sans.pnum_name(n)] = []
    # the sans's marked (slashed) zero, under `zero`; the plain 0 stays default
    for n in ZERO:
        names[n] = []
    # the bare I (ss09, cv08, salt) and the colon between figures
    for n in EXTRA:
        names[n] = []
    return names


ZERO = ('zero.slash', 'zero.pnum.slash')
EXTRA = ('I.1', sans.FIG_COLON, sans.FIG_HYPHEN)


def flat(font, name):
    g = font[name].copy()
    lib.decompose(font, g)
    return g


def stem(font):
    g = font['H']
    ux = sorted(set(round(p.x) for c in g.contours for p in c.points))
    return ux[1] - ux[0]


def round_masters(src, glyphs):
    ref = src[REF]
    out = {m: {} for m in src}
    st = stem(ref)
    report, bowls, notches = [], [], []
    for name, unis in glyphs.items():
        gs = {m: flat(f, name) for m, f in src.items()}
        if name in SOFT_NOTCH:
            merged = merge_notch(src, gs)
            notches.append(f'{name} {merged}')
        base = {m: rough(g) for m, g in gs.items()}
        first = None
        for pen in PEN_STEPS:
            _pen[0] = pen
            plans = plan(src, gs, name)
            best = None
            for alpha, alpha_cap in ((a, b) for a in TRANSFER for b in TRANSFER):
                done = fillet(src, gs, plans, alpha, alpha_cap, name)
                n = kinks(done, name) + sum(max(0, rough(g) - base[m]) for m, g in done.items())
                if best is None or n < best[0]:
                    best = (n, alpha, alpha_cap, done)
                if n == 0:
                    break
            n, alpha, alpha_cap, done = best
            gain = None
            if n:
                for k in GAIN:
                    trial = caption_gain(done, k)
                    if kinks(trial, name) + sum(max(0, rough(g) - base[m]) for m, g in trial.items()) == 0:
                        done, n, gain = trial, 0, k
                        break
            if first is None:
                first = (n, alpha, alpha_cap, done, gain, pen)
            if n == 0:
                break
        if n:
            n, alpha, alpha_cap, done, gain, pen = first
        _pen[0] = 1.0
        if name in HERO:
            done, bowl = hero_bowls(src, done, name)
            if bowl is not None:
                bowls.append(f'{name} {bowl:.2f}')
        if alpha or alpha_cap or n or gain is not None or pen != 1.0:
            share = f'share {alpha:.2f}' + (f', caption {alpha_cap:.2f}' if alpha_cap != alpha else '')
            if gain is not None:
                share += f', caption outlines {gain:.2f} of the way from the text masters'
            if pen != 1.0:
                share += f', pen {pen:.2f}'
            report.append(f'{name} ({share}, kinks left {n})')
        for m, g in done.items():
            g.unicodes = unis
            g.lib[sans.SOURCE_KEY] = name
            out[m][name] = g
    if report:
        print('  rounded fillet joins moved toward the Regular\'s curve points:', ', '.join(report))
    print('  rounded hero bowls (display masters, share of the way to circular):', ', '.join(bowls) or 'none')
    print('  rounded notch steps closed to one join (glyph, steps):', ', '.join(notches) or 'none')
    return out


def merge_notch(src, gs):
    """Close each short step between two lines that together turn a concave
    corner of more than 90 degrees (the step a few units long where the
    flat-top 3's bar underside meets its diagonal): its two points become the
    one point where the two lines meet, in every master. Returns the number
    of steps closed."""
    ref = gs[REF]
    found = []
    for ci, c in enumerate(ref.contours):
        P = c.points
        n = len(P)
        area = sum(P[i - 1].x * p.y - p.x * P[i - 1].y for i, p in enumerate(P))
        for i in range(n):
            a, b, q, d = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
            if not all(p.type == 'line' for p in (b, q, d)) or a.type is None:
                continue
            if not all(math.hypot(g.contours[ci].points[(i + 1) % n].x - g.contours[ci].points[i].x,
                                  g.contours[ci].points[(i + 1) % n].y - g.contours[ci].points[i].y)
                       < MICRO * stem(src[m]) for m, g in gs.items()):
                continue
            u, v = lib.unit((b.x - a.x, b.y - a.y)), lib.unit((d.x - q.x, d.y - q.y))
            turn = math.degrees(math.acos(max(-1.0, min(1.0, lib.dot(u, v)))))
            if turn > 90 and lib.cross(u, v) * area < 0:
                found.append((ci, i))
    for ci, i in sorted(found, reverse=True):
        for g in gs.values():
            P = g.contours[ci].points
            n = len(P)
            a, b, q, d = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
            u, v = (b.x - a.x, b.y - a.y), (d.x - q.x, d.y - q.y)
            s = lib.cross((q.x - a.x, q.y - a.y), v) / lib.cross(u, v)
            b.x, b.y = a.x + u[0] * s, a.y + u[1] * s
            del P[(i + 1) % n]
    return len(found)


def round_bowls(g, share, min_leg):
    """Quarter-turn curves of one outline move `share` of the way from their
    handle tension to circular tension (BOWL_K); points and handle
    directions stay. Returns the number of curves changed."""
    k = 0
    for c in g.contours:
        P = c.points
        for i, p in enumerate(P):
            if p.type != 'curve':
                continue
            h2, h1, p0 = P[i - 1], P[i - 2], P[i - 3]
            if h1.type is not None or h2.type is not None or p0.type is None:
                continue
            d1, d2 = (h1.x - p0.x, h1.y - p0.y), (p.x - h2.x, p.y - h2.y)
            n1, n2 = lib.norm(d1), lib.norm(d2)
            if n1 < 0.5 or n2 < 0.5:
                continue
            u1, u2 = (d1[0] / n1, d1[1] / n1), (d2[0] / n2, d2[1] / n2)
            turn = math.degrees(math.acos(max(-1.0, min(1.0, lib.dot(u1, u2)))))
            if not BOWL_TURN[0] <= turn <= BOWL_TURN[1]:
                continue
            den = lib.cross(u1, u2)
            chord = (p.x - p0.x, p.y - p0.y)
            s1, s2 = lib.cross(chord, u2) / den, lib.cross(u1, chord) / den
            if s1 < min_leg or s2 < min_leg:
                continue
            t1, t2 = n1 / s1, n2 / s2
            if max(t1, t2) < BOWL_K + 0.01:
                continue
            t1 -= share * max(0.0, t1 - BOWL_K)
            t2 -= share * max(0.0, t2 - BOWL_K)
            h1.x, h1.y = p0.x + u1[0] * t1 * s1, p0.y + u1[1] * t1 * s1
            h2.x, h2.y = p.x - u2[0] * t2 * s2, p.y - u2[1] * t2 * s2
            k += 1
    return k


def hero_bowls(src, done, name):
    """Rounder bowls for a hero glyph in the display masters: the largest
    share in BOWL_SHARES (from BOWL_SHARE down) that adds no interpolation
    kink and no outline kink. Returns (outlines, share or None)."""
    base = kinks(done, name)
    rough0 = {m: rough(g) for m, g in done.items()}
    for share in (s for s in BOWL_SHARES if s <= BOWL_SHARE):
        trial = dict(done)
        changed = 0
        for m in DISPLAY:
            if m not in done:
                continue
            g = done[m].copy()
            changed += round_bowls(g, share, BOWL_LEG * stem(src[m]))
            lib.round2(g)
            trial[m] = g
        if not changed:
            return done, None
        if kinks(trial, name) <= base and all(rough(trial[m]) <= rough0[m] for m in DISPLAY if m in trial):
            return trial, share
    return done, None


# Shares of the way each master's fillet joins may move toward the curve
# points the Regular uses, one share for the text masters and one for the
# caption masters; the first pair (text share first) that interpolates
# without kinks and leaves no master with a corner its sans master lacks is
# kept, so outlines change no more than they must.
TRANSFER = (0.0, 0.25, 0.5, 0.75, 1.0)
# A glyph whose caption masters kink at every pair of shares (the small 2
# of the 1/2, which the sans's caption stem gain folds at Black) takes only
# part of its caption outlines: each caption master moves from its text
# master's rounded outline, centred on the caption glyph, toward its own by
# the largest of these shares that clears the check (0 is the text outline).
GAIN = (0.75, 0.5, 0.25, 0.0)


def caption_gain(done, k):
    out = dict(done)
    for c, (t, _) in sans.CAPTION.items():
        if c not in done or t not in done or not done[c].contours:
            continue
        a, b = done[t].getBounds(), done[c].getBounds()
        base = done[t].copy()
        dx = (b.xMin + b.xMax - a.xMin - a.xMax) / 2
        for con in base.contours:
            for pt in con.points:
                pt.x += dx
        g = lib.lerp_glyph(base, done[c], k)
        resmooth(g)
        unfold(g)
        lib.round2(g)
        g.width = done[c].width
        out[c] = g
    return out


# A smooth point whose two sides turn by more than this, or a corner next to
# a curve that turns by KINK degrees, is a kink in one master's outline.
SMOOTH_TOL = 2.0
KINK = (3.0, 25.0)


def rough(g):
    """Kinks in one master's outline: smooth points whose incoming and
    outgoing directions (to the nearest points more than half a unit away)
    differ by more than SMOOTH_TOL, and corners next to a curve that turn by
    a small angle within KINK."""
    n_k = 0
    for c in g.contours:
        P = c.points
        n = len(P)
        for i, p in enumerate(P):
            if p.type is None:
                continue

            def nb(step):
                k = i
                for _ in range(n):
                    k = (k + step) % n
                    q = P[k]
                    if math.hypot(q.x - p.x, q.y - p.y) > 0.5:
                        return q
                return None
            a, b = nb(-1), nb(1)
            if a is None or b is None:
                continue
            u = (p.x - a.x, p.y - a.y)
            v = (b.x - p.x, b.y - p.y)
            nu, nv = math.hypot(*u), math.hypot(*v)
            if nu < 1e-9 or nv < 1e-9:
                continue
            ang = math.degrees(math.acos(max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (nu * nv)))))
            if p.smooth:
                n_k += ang > SMOOTH_TOL
            elif (P[i - 1].type is None or P[(i + 1) % n].type is None) and KINK[0] < ang < KINK[1]:
                n_k += 1
    return n_k


# A line some master's fillets would use up, or leave shorter than this
# (in units), is ended by two fillets that meet at its middle in every
# master; a line with one fillet that would leave a sliver is taken whole.
MIN_LINE = 16
# No fillet chord under this many units (Thin's joins are a few units).
MIN_CHORD = 14
# Lines shorter than this share of the stem in every master keep sharp ends.
MICRO = 0.20
# Corners that turn back by more than this in any master (a crotch or spike
# a few degrees wide, such as where the 6's and 9's straight stems leave the
# bowl) keep their point: a fillet there cannot show and folds over.
CUSP = 160.0


def _corner_turn(contour, i):
    segs = lib.to_segments(contour)
    n = len(segs)
    j = (i + 1) % n
    _, tin = lib.seg_dirs(segs[i - 1]['end'], segs[i])
    tout, _ = lib.seg_dirs(segs[i]['end'], segs[j])
    return math.degrees(math.acos(max(-1, min(1, lib.dot(tin, tout)))))


def plan(src, gs, name=None):
    """Corners, terminals and meeting lines of each contour, decided once
    for every master. Of two neighbouring terminal candidates only the
    shorter is a stroke end (the other is a stem side)."""
    st = stem(src[REF])
    out = []
    for ci, c in enumerate(gs[REF].contours):
        corners, terms = lib.classify_corners(c, st, terminal_ratio=TERMINAL)
        segs = lib.to_segments(c)
        n = len(segs)
        starts = [segs[i - 1]['end'] for i in range(n)]
        length = lambda j: lib.seg_len(starts[j], segs[j])
        # Notches a fraction of a stem across in every master (the inner
        # point of < and >) stay as the sans draws them.
        sharp = set()
        for j in range(n):
            if j in terms or segs[j]['type'] != 'line':
                continue
            if all(lib.seg_len(lib.to_segments(g.contours[ci])[j - 1]['end'], lib.to_segments(g.contours[ci])[j])
                   < MICRO * stem(src[m]) for m, g in gs.items()):
                for i in ((j - 1) % n, j):
                    if corners.pop(i, None):
                        sharp.add(i)
        cusps = set()
        for i in list(corners):
            if i in corners and max(_corner_turn(g.contours[ci], i) for g in gs.values()) > CUSP:
                corners.pop(i)
                cusps.add(i)
                terms.discard(i)
                terms.discard((i + 1) % n)
        for j in sorted(terms, key=length, reverse=True):
            if j in terms and ((j - 1) % n in terms or (j + 1) % n in terms):
                terms.discard(j)
        meets, swallow = set(), {}
        for j in range(n):
            if segs[j]['type'] != 'line' or j in terms:
                continue
            at_start, at_end = (j - 1) % n in corners or (j - 1) % n in terms, j in corners or (j + 1) % n in terms
            if not (at_start or at_end):
                continue
            # a fillet never takes a line whole up to a cusp or a notch corner
            # it keeps sharp (it would end tangent to the far side of it: the
            # g's flag would slope into its bowl)
            kept = cusps | sharp
            if (at_start and not at_end and j in kept) or (at_end and not at_start and (j - 1) % n in kept):
                continue
            for m, g in gs.items():
                rv, rc, mc = radii(m, stem(src[m]), name)
                _, _, cs, ce, L = lib.corner_cuts(g.contours[ci], corners, terms, rv, rc, mc, min_chord=MIN_CHORD)
                if L[j] - cs[j] - ce[j] < MIN_LINE:
                    if at_start and at_end:
                        meets.add(j)
                    else:
                        swallow[j] = 'start' if at_start else 'end'
                    break
        out.append((corners, terms, meets, swallow))
    return out


def fillet(src, gs, plans, alpha, alpha_cap=None, name=None):
    """Fillet copies of one glyph's masters. Radii scale with each master's
    stem (per weight, `radii`); with alpha > 0, each curve cut moves toward
    the Regular's (by alpha_cap in the caption masters, alpha elsewhere)."""
    done = {REF: gs[REF].copy()}
    rv, rc, mc = radii(REF, stem(src[REF]), name)
    t_ref = [lib.fillet_contour(c, cs, ts, r_convex=rv, r_concave=rc, max_cut=mc,
                                meets=ms, swallow=sw, min_chord=MIN_CHORD)
             for c, (cs, ts, ms, sw) in zip(done[REF].contours, plans)]
    for m, g in gs.items():
        if m == REF:
            continue
        g = done[m] = g.copy()
        rv, rc, mc = radii(m, stem(src[m]), name)
        for c, (cs, ts, ms, sw), tr in zip(g.contours, plans, t_ref):
            lib.fillet_contour(c, cs, ts, r_convex=rv, r_concave=rc, t_ref=tr,
                               alpha=alpha if m not in CAPTION or alpha_cap is None else alpha_cap,
                               max_cut=mc, meets=ms, swallow=sw, min_chord=MIN_CHORD)
    for g in done.values():
        resmooth(g)
        unfold(g)
        lib.round2(g)
    return done


# The font checker runs the kink test with its default em of 1000 units on
# this 2048-unit font, which makes it about twice as sensitive; the fillet
# search uses the same setting (at 2048 the Rounded g passed here and showed
# one kink, Black against the caption Thin, in the built font).
KINK_UPEM = 1000


def kinks(done, name):
    """Kinks the interpolation check finds in one glyph, over every master
    as the font holds it: along the source order, along the
    order the font checker walks the variable font's masters (VF_ORDER),
    and between each group's Thin and Black directly."""
    from fontTools.varLib.interpolatable import test_gen
    outlines = dict(done)
    chains = [[m for m in MASTERS if m in outlines], [m for m in VF_ORDER if m in outlines]]
    for group in (TEXT, CAPTION):
        if group[0] in outlines and group[-1] in outlines:
            chains.append([group[-1], group[0]])
    n = 0
    for shapes in (outlines, quadratic(outlines)):
        for chain in chains:
            gs = [{name: shapes[m]} for m in chain]
            n += sum(1 for _, p in test_gen(gs, glyphs=[name], names=chain, upem=KINK_UPEM) if p['type'] == 'kink')
    return n


# The build's cubic-to-quadratic tolerance (the compiler's default, a
# thousandth of the em) for the TrueType outlines the font checker reads.
QUAD_ERR = 2048 * 0.001


def quadratic(outlines):
    """The masters' outlines as the TrueType font holds them: converted to
    quadratic curves together, with the compiler's tolerance and direction,
    and rounded to whole units."""
    from fontTools.cu2qu.ufo import glyphs_to_quadratic
    ms = list(outlines)
    qs = [outlines[m].copy() for m in ms]
    glyphs_to_quadratic(qs, max_err=[QUAD_ERR] * len(qs), reverse_direction=True)
    for q in qs:
        for c in q.contours:
            for pt in c.points:
                pt.x, pt.y = round(pt.x), round(pt.y)
    return dict(zip(ms, qs))


def _vf_order():
    """Masters in the order the font checker meets them in the variable
    font: the default, then masters off the default on one axis, then on
    both, each sorted by axis tag and normalised position."""
    d_op, d_w = MASTERS[REF]
    side = lambda v, d: (v > d) - (v < d)
    key = {}
    for m, (op, w) in MASTERS.items():
        peak = tuple((tag, v) for tag, v in (('opsz', side(op, d_op)), ('wght', side(w, d_w))) if v)
        key[m] = (len(peak), peak)
    return sorted(MASTERS, key=lambda m: key[m])


VF_ORDER = _vf_order()


def resmooth(g):
    """Points flagged smooth get collinear handles again after a blend of
    two masters (each handle keeps its length; a line's direction wins)."""
    for c in g.contours:
        P = c.points
        n = len(P)
        for i, p in enumerate(P):
            if p.type is None or not p.smooth:
                continue
            a, b = P[i - 1], P[(i + 1) % n]
            la, lb = (p.x - a.x, p.y - a.y), (b.x - p.x, b.y - p.y)
            na, nb = lib.norm(la), lib.norm(lb)
            if na < 1e-6 or nb < 1e-6:
                continue
            if a.type is None and b.type is None:
                u = lib.unit((la[0] / na + lb[0] / nb, la[1] / na + lb[1] / nb))
                a.x, a.y = p.x - u[0] * na, p.y - u[1] * na
                b.x, b.y = p.x + u[0] * nb, p.y + u[1] * nb
            elif a.type is None:
                u = lib.unit(lb)
                a.x, a.y = p.x - u[0] * na, p.y - u[1] * na
            elif b.type is None:
                u = lib.unit(la)
                b.x, b.y = p.x + u[0] * nb, p.y + u[1] * nb


def _ang(a, b):
    return math.degrees(math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]))


def unfold(g):
    """A tiny fillet that folds back on itself (Thin, a blended or
    emboldened master) keeps its handle directions but shortens them to the
    point where the two tangents meet, so the curve stays inside its
    corner; one whose tangents meet behind its ends (inverted) becomes a
    straight bevel."""
    k = 0
    for c in g.contours:
        P = c.points
        n = len(P)
        for i, p in enumerate(P):
            if p.type is None:
                continue
            h1, h2, q = P[(i + 1) % n], P[(i + 2) % n], P[(i + 3) % n]
            if h1.type is not None or h2.type is not None or q.type != 'curve':
                continue
            legs = [(h1.x - p.x, h1.y - p.y), (h2.x - h1.x, h2.y - h1.y), (q.x - h2.x, q.y - h2.y)]
            legs = [v for v in legs if lib.norm(v) > 0.5]
            if len(legs) < 2:
                continue
            fold = abs(sum(_ang(a, b) for a, b in zip(legs, legs[1:]))) > 180
            d1, d2 = (h1.x - p.x, h1.y - p.y), (q.x - h2.x, q.y - h2.y)
            chord = (q.x - p.x, q.y - p.y)
            if not fold and lib.norm(d1) > 0.5 and lib.norm(d2) > 0.5 and abs(_ang(d1, d2)) < 90:
                fold = lib.dot(d1, chord) < -1 or lib.dot(d2, chord) < -1
            if not fold:
                continue
            u1, u2 = lib.unit(d1), lib.unit(d2)
            den = lib.cross(u1, u2)
            s1 = s2 = None
            if abs(den) > 1e-9:
                s1 = lib.cross(chord, u2) / den
                s2 = lib.cross(u1, chord) / den
            if s1 is None or s1 <= 0 or s2 <= 0:
                # an inverted fillet (a caption master's stem gain is wider
                # than a small join's radius): a straight bevel
                h1.x, h1.y = p.x + chord[0] / 3, p.y + chord[1] / 3
                h2.x, h2.y = q.x - chord[0] / 3, q.y - chord[1] / 3
                p.smooth = q.smooth = False
                k += 1
                continue
            l1, l2 = min(lib.norm(d1), s1), min(lib.norm(d2), s2)
            h1.x, h1.y = p.x + u1[0] * l1, p.y + u1[1] * l1
            h2.x, h2.y = q.x - u2[0] * l2, q.y - u2[1] * l2
            k += 1
    return k


def kerning(f, sans_font):
    """The sans's kerning groups and pairs, restricted to Rounded's glyphs
    (same names), so strings keep the sans's widths."""
    have = set(f.keys())
    groups = {}
    for gname, members in sans_font.groups.items():
        if gname.startswith(('public.kern1.', 'public.kern2.')):
            keep = [m for m in members if m in have]
            if keep:
                groups[gname] = keep
    f.groups.update(groups)
    for (l, r), v in sans_font.kerning.items():
        if (l in have or l in groups) and (r in have or r in groups):
            f.kerning[(l, r)] = v


TOKEN = re.compile(r"\[[^\]]*\]'?|\S+")


def features(sans_text, have):
    """pnum/tnum, case and the sans's case-context calt rules, every class
    and rule kept only as far as Rounded has its glyphs."""
    cl = classes(sans_text)
    case = [(a, b) for a, b in zip(cl['@CASE_L'], cl['@CASE_R']) if a in have and b in have]
    defs = {'@CASE_L': [a for a, _ in case], '@CASE_R': [b for _, b in case]}
    for k, v in cl.items():
        if k not in defs:
            defs[k] = [x for x in v if x in have]
    calt = re.search(r'\nfeature calt \{(.*?)\n\} calt;', sans_text, re.S).group(1)
    lines = [ln.strip() for ln in calt.split('\n')]
    first = next(i for i, ln in enumerate(lines) if ln.startswith("sub colon'"))
    used, rules = set(), []
    # a named lookup in the sans's calt (figure_punct) stays its own lookup,
    # after the case rules, so it sees what they substituted
    named, block = {}, None
    for ln in lines[first:]:
        m = re.match(r'lookup (\w+) \{$', ln)
        if m:
            block = m.group(1)
            named[block] = []
            continue
        if block and ln == '} %s;' % block:
            block = None
            continue
        if not ln or ln.startswith('#') or not ln.endswith(';'):
            continue
        body = ln[:-1]
        out, ok = [], True
        for tok in TOKEN.findall(body):
            mark = "'" if tok.endswith("'") else ''
            t = tok[:-1] if mark else tok
            if t in ('sub', 'ignore', 'by'):
                out.append(t)
            elif t.startswith('['):
                items = []
                for x in t[1:-1].split():
                    items += defs.get(x, []) if x.startswith('@') else ([x] if x in have else [])
                if not items:
                    ok = False
                    break
                out.append('[' + ' '.join(items) + ']' + mark)
            elif t.startswith('@'):
                if not defs.get(t):
                    ok = False
                    break
                used.add(t)
                out.append(t + mark)
            else:
                if t not in have:
                    ok = False
                    break
                out.append(t + mark)
        if ok:
            (named[block] if block else rules).append('    ' + ' '.join(out) + ';')
    tab = ' '.join(FIGS)
    prop = ' '.join(sans.pnum_name(n) for n in FIGS)
    head = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n\n'
    head += f'@TAB = [{tab}];\n@PROP = [{prop}];\n'
    for k in sorted(used | {'@CASE_L', '@CASE_R'}):
        head += f'{k} = [{" ".join(defs[k])}];\n'
    case_rules = ''.join(f'    sub {a} by {b};\n' for a, b in case)
    lookups = ''.join(f'    lookup {k} {{\n' + '\n'.join('    ' + r for r in v) + f'\n    }} {k};\n'
                      for k, v in named.items() if v)
    bare = ''
    if 'I.1' in have:
        bare = ('feature salt { sub I by I.1; } salt;\n'
                + f'feature {sans.SS_BARE_I} {{\n    featureNames {{\n        name "Upper-case i without serifs";\n    }};\n'
                + f'    sub I by I.1;\n}} {sans.SS_BARE_I};\n'
                + 'feature cv08 { sub I by I.1; } cv08;\n')
    return (head + '\nfeature case {\n' + case_rules + '} case;\n\n'
            + 'feature calt {\n' + '\n'.join(rules) + '\n' + lookups + '} calt;\n\n'
            + bare
            + 'feature pnum { sub @TAB by @PROP; } pnum;\n'
            + 'feature tnum { sub @PROP by @TAB; sub zero.pnum.slash by zero.slash; } tnum;\n'
            + 'feature zero { sub zero by zero.slash; sub zero.pnum by zero.pnum.slash; } zero;\n')


def make(sans_dir):
    sans_dir = Path(sans_dir)
    dest = sans_dir.parent / 'sans-rounded'
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir()
    src = {m: ufoLib2.Font.open(sans_dir / f'StrataSans-{m}.ufo') for m in MASTERS}
    glyphs = glyph_set(src[REF])
    print(f'  rounded glyphs: {len(glyphs)}', flush=True)
    # Every master, display included, is rounded from the sans master of the
    # same name, so Rounded's ink follows the sans display drawings at
    # 40-96 px (r3 reused the text outlines there: "80%" set 1% wider).
    rounded = round_masters({m: src[m] for m in TEXT + tuple(DISPLAY) + CAPTION}, glyphs)
    fea = features(src[REF].features.text, set(glyphs))
    ds = DesignSpaceDocument()
    op = AxisDescriptor(); op.tag = 'opsz'; op.name = 'Optical size'; op.minimum = 8; op.default = 14; op.maximum = 32
    ds.addAxis(op)
    ax = AxisDescriptor(); ax.tag = 'wght'; ax.name = 'Weight'; ax.minimum = 100; ax.default = 400; ax.maximum = 900
    ax.map = list(lib.SANS_WGHT_MAP)
    ds.addAxis(ax)
    order = ['.notdef'] + [n for n in src[REF].glyphOrder if n in glyphs]
    for m, (opsz, w) in MASTERS.items():
        s = src[m]
        f = Font()
        f.info.familyName = 'Strata Sans Rounded'
        style = {100: 'Thin', 400: 'Regular', 900: 'Black'}[w]
        if opsz == 14:
            f.info.styleName = style
        elif opsz == 8:
            f.info.styleName = sans.CAPTION_STYLE[w]
        else:
            f.info.styleName = 'Display' if w == 400 else 'Display ' + style
        f.info.copyright = s.info.copyright
        for k in ('unitsPerEm', 'ascender', 'descender', 'xHeight', 'capHeight', 'versionMajor', 'versionMinor',
                  'openTypeHheaAscender', 'openTypeHheaDescender', 'openTypeHheaLineGap', 'openTypeOS2TypoAscender',
                  'openTypeOS2TypoDescender', 'openTypeOS2TypoLineGap', 'openTypeOS2WinAscent', 'openTypeOS2WinDescent',
                  'openTypeOS2Selection'):
            setattr(f.info, k, getattr(s.info, k))
        f.info.openTypeOS2WeightClass = w
        f.info.openTypeNameLicense = s.info.openTypeNameLicense
        f.info.openTypeNameLicenseURL = s.info.openTypeNameLicenseURL
        nd = s['.notdef'].copy(); lib.decompose(s, nd)
        f.layers.defaultLayer.insertGlyph(nd, '.notdef')
        for n, g in rounded[m].items():
            f.layers.defaultLayer.insertGlyph(g, n)
        f.lib['public.glyphOrder'] = order
        cats = s.lib.get('public.openTypeCategories', {})
        f.lib['public.openTypeCategories'] = {n: cats[n] for n in order if n in cats}
        f.features.text = fea
        kerning(f, s)
        path = dest / f'StrataSansRounded-{m}.ufo'
        f.save(path, overwrite=True)
        sd = SourceDescriptor(); sd.filename = path.name
        sd.location = {'Optical size': opsz, 'Weight': w}
        sd.familyName = 'Strata Sans Rounded'; sd.styleName = f.info.styleName
        ds.addSource(sd)
    # Same named weights as Strata Sans, placed in user units (text size).
    for w, nm in ((100, 'Thin'), (200, 'ExtraLight'), (300, 'Light'), (400, 'Regular'), (500, 'Medium'),
                  (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')):
        i = InstanceDescriptor(); i.familyName = 'Strata Sans Rounded'; i.styleName = nm
        i.userLocation = {'Optical size': 14, 'Weight': w}
        ds.addInstance(i)
    ds.write(dest / 'StrataSansRounded.designspace')
    for n in ('COPYRIGHT.txt', 'OFL.txt'):
        shutil.copyfile(sans_dir / n, dest / n)
