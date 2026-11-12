"""Strata Sans: identity, weather numerals and optical spacing.

Masters: m00 (opsz 14, Thin), m01 (32, Thin), m02 (14, Regular, default),
m03 (32, Regular), m04 (14, Black), m05 (32, Black).
"""
import re
from fontTools.misc.transform import Transform
from ufoLib2.objects import Component
import lib
from fontTools.pens.statisticsPen import StatisticsPen

TEXT = ['m00', 'm02', 'm04']
DISPLAY = ['m01', 'm03', 'm05']
PARTNER = {'m00': 'm02', 'm01': 'm03', 'm02': 'm00', 'm03': 'm01', 'm04': 'm02', 'm05': 'm03'}
FIGS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
MATH = ['plus', 'minus', 'equal', 'multiply', 'divide', 'plusminus', 'less', 'greater',
        'lessequal', 'greaterequal', 'notequal', 'approxequal', 'logicalnot']
TF_GAIN = 0
# Tabular 1: flag lengthened along its outer edge by this fraction.
ONE_FLAG = 0.35
# Width factors for the figures that read narrow next to the round zero.
WIDEN = {'zero': 1.04, 'six': 1.035, 'nine': 1.035, 'eight': 1.03, 'three': 1.025,
         'five': 1.02, 'two': 1.02}
# Spacing per side: open at text size, tight at display size.
TRACK = {'m00': 6, 'm02': 6, 'm04': 6, 'm01': -10, 'm03': -10, 'm05': -10}
# Punctuation that separates figures keeps its room when display tightens.
NO_TIGHTEN = {'period', 'comma', 'colon', 'semicolon', 'period.tf', 'comma.tf', 'colon.tf', 'semicolon.tf'}
SEQUENTIAL = {'DZ', 'Dz', 'Dzcaron_', 'dz', 'dzcaron', 'IJ', 'ij', 'LJ', 'Lj', 'lj', 'NJ', 'Nj', 'nj',
              'I.double', 'idotless.double', 'feng', 'feng.1', 'degreecentigrade', 'degreefarenheit',
              'afii10045', 'afii10048', 'Ukcyrillic', 'ljecyrillic', 'njecyrillic', 'exclamdbl'}
FIXED_SPACES = {0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2008, 0x2009, 0x200A,
                0x200B, 0x202F, 0x205F, 0x2007}


def stem(font):
    """Vertical stem of H (left stem width at mid height)."""
    g = font['H']
    xs = sorted(p.x for c in g.contours for p in c.points)
    # H is drawn as one contour: the two smallest distinct x values are the left stem
    ux = sorted(set(round(x) for x in xs))
    return ux[1] - ux[0]


def ink(font, g):
    return lib.bounds(g, font)


# ------------------------------------------------------------------ G

def swap_g(masters):
    first = masters['m02']
    pairs = []
    for n in sorted(first.keys()):
        if n.startswith('G') and not n.endswith('.1') and (n + '.1') in first and '.' not in n:
            pairs.append((n, n + '.1'))
    swap = {}
    for a, b in pairs:
        swap[a] = b; swap[b] = a
    for f in masters.values():
        for a, b in pairs:
            ga, gb = f[a], f[b]
            da, db = ga.copy(), gb.copy()
            for dst, src in ((ga, db), (gb, da)):
                dst.clearContours(); dst.clearComponents(); dst.clearAnchors()
                for c in src.contours:
                    dst.contours.append(c)
                for c in src.components:
                    dst.components.append(Component(swap.get(c.baseGlyph, c.baseGlyph), c.transformation))
                for an in src.anchors:
                    dst.anchors.append(an)
                dst.width = src.width
        # Kerning follows the shape.
        for gname, members in list(f.groups.items()):
            f.groups[gname] = [swap.get(m, m) for m in members]
        newk = {}
        for (l, r), v in f.kerning.items():
            newk[(swap.get(l, l), swap.get(r, r))] = v
        f.kerning.clear(); f.kerning.update(newk)
    fea = first.features.text
    fea = fea.replace('name "Capital G with spur";', 'name "Capital G without spur";')
    for f in masters.values():
        if f.features.text:
            f.features.text = f.features.text.replace('name "Capital G with spur";', 'name "Capital G without spur";')
    return [a for a, _ in pairs]


# ------------------------------------------------------------------ t

def slant_t(masters, left=0.35, right=0.08):
    for f in masters.values():
        g = f['_part.t_base']
        c = g.contours[0]
        tops = sorted([p for p in c.points if p.type is not None], key=lambda p: -p.y)[:2]
        tl, tr = sorted(tops, key=lambda p: p.x)
        w = tr.x - tl.x
        tl.y -= left * w
        tr.y += right * w


# ------------------------------------------------------------------ figures

def widen(masters, name, s):
    new = {}
    for m, f in masters.items():
        g, p = f[name], masters[PARTNER[m]][name]
        if not g.contours:
            continue
        b0 = lib.bounds(g)
        vm, vp = stem(f), stem(masters[PARTNER[m]])
        if lib.same_structure(g, p):
            ng = lib.scale_compensated(g, p, s, 1.0, vm, vp)
        else:
            ng = g.copy()
            for c in ng.contours:
                for q in c.points:
                    q.x *= s
        b1 = lib.bounds(ng)
        # keep the left side bearing; grow the advance by the ink growth
        dx = b0[0] - b1[0]
        for c in ng.contours:
            for q in c.points:
                q.x += dx
        new[m] = (ng, (b1[2] - b1[0]) - (b0[2] - b0[0]))
    for m, (ng, grow) in new.items():
        g = masters[m][name]
        g.clearContours()
        for c in ng.contours:
            g.contours.append(c)
        g.width = g.width + grow
    return {m: grow for m, (ng, grow) in new.items()}


def long_flag(g, t):
    """Extend the flag of a one along its own outer edge by fraction t."""
    c = g.contours[0]
    pts = c.points
    xmin = min(p.x for p in pts)
    tips = [i for i, p in enumerate(pts) if p.x == xmin]
    assert len(tips) == 2, 'one outline changed'
    upper = max(tips, key=lambda i: pts[i].y)
    n = len(pts)
    prev = (upper - 1) % n if (upper - 1) % n not in tips else (upper + 1) % n
    dx, dy = pts[upper].x - pts[prev].x, pts[upper].y - pts[prev].y
    for i in tips:
        pts[i].x += t * dx
        pts[i].y += t * dy


def numerals(masters):
    growth = {}
    for n, s in WIDEN.items():
        growth[n] = widen(masters, n, s)
    # zero.tf has its own contour; widen and recentre within the new cell.
    tf_old = {m: f['zero.tf'].width for m, f in masters.items()}
    gz = widen(masters, 'zero.tf', WIDEN['zero'])
    for m, f in masters.items():
        tf = tf_old[m] + TF_GAIN
        # zero.tf: widen() kept the lsb and grew the width; recentre in tf
        g = f['zero.tf']
        b = lib.bounds(g)
        cx_old = (b[0] + b[2]) / 2 - gz[m] / 2  # centre before widening
        target = cx_old + TF_GAIN / 2
        lib.shift_glyph(g, target - (b[0] + b[2]) / 2)
        g.width = tf
        # tabular one: keep the flag and stem, drop the slab foot
        one = f['one.tf']
        if one.contours:
            one.clearContours()
        for n in FIGS:
            gt = f[n + '.tf']
            if n == 'one':
                # footless tabular 1 with a longer flag, so it fills its cell
                # instead of floating in it; centred on its area centroid
                flat = f['one'].copy(); lib.decompose(f, flat)
                long_flag(flat, ONE_FLAG)
                pen = StatisticsPen()
                flat.draw(pen)
                gt.clearComponents()
                lib.copy_contours(flat, gt, Transform(1, 0, 0, 1, round(tf / 2 - pen.meanX), 0))
                gt.width = tf
                continue
            if n not in ('zero',) and gt.components:
                c = gt.components[0]
                if c.baseGlyph == n:
                    grow = growth.get(n, {}).get(m, 0)
                    t = c.transformation
                    off = t[4] + TF_GAIN / 2 - grow / 2
                    if n == 'one':
                        # no foot: centre the 1 on its area centroid
                        pen = StatisticsPen(glyphset=f)
                        f['one'].draw(pen)
                        off = tf / 2 - pen.meanX
                    c.transformation = Transform(1, 0, 0, 1, off, t[5])
            gt.width = tf
        # slashed zeros follow the widened zero
        for zs, base in (('zero.slash', 'zero'), ('zero.tf.slash', 'zero.tf')):
            g = f[zs]
            g.width = f[base].width
            for c in g.components:
                if c.baseGlyph == '_part.zeroslash':
                    bz = lib.bounds(f[base])
                    bs = lib.bounds(f['_part.zeroslash'])
                    t = c.transformation
                    c.transformation = Transform(1, 0, 0, 1, (bz[0] + bz[2]) / 2 - (bs[0] + bs[2]) / 2, t[5])
        # other tabular glyphs keep their offsets and gain the cell growth
        for g in f:
            if g.name.endswith('.tf') and g.width == tf_old[m]:
                for c in g.components:
                    t = c.transformation
                    c.transformation = Transform(t[0], t[1], t[2], t[3], t[4] + TF_GAIN / 2, t[5])
                if g.contours:
                    for cc in g.contours:
                        for q in cc.points:
                            q.x += TF_GAIN / 2
                g.width = tf
        f['figurespace'].width = tf


def math_on_figures(masters):
    for f in masters.values():
        tf = f['zero.tf'].width
        names = [n for n in MATH if n in f]
        moves = {}
        for n in names:
            g = f[n]
            case = f[n + '.case'] if (n + '.case') in f else None
            dy = 0
            if case is not None and case.components and case.components[0].baseGlyph == n:
                dy = case.components[0].transformation[5]
            b = lib.bounds(g, f)
            moves[n] = ((tf - (b[0] + b[2])) / 2, dy)
        for n in names:
            g = f[n]
            dx, dy = moves[n]
            for c in g.contours:
                for q in c.points:
                    q.x += dx; q.y += dy
            for a in g.anchors:
                a.x += dx; a.y += dy
            for c in g.components:
                if c.baseGlyph in moves:
                    bdx, bdy = moves[c.baseGlyph]
                    t = c.transformation
                    c.transformation = Transform(t[0], t[1], t[2], t[3], t[4] + dx - bdx, t[5] + dy - bdy)
                else:
                    t = c.transformation
                    c.transformation = Transform(t[0], t[1], t[2], t[3], t[4] + dx, t[5] + dy)
            g.width = tf
            case = f[n + '.case'] if (n + '.case') in f else None
            if case is not None and case.components and case.components[0].baseGlyph == n:
                case.components[0].transformation = Transform(1, 0, 0, 1, 0, 0)
                case.width = tf
            for alt in (n + '.tf', n + '.case.tf'):
                if alt in f:
                    a = f[alt]
                    for c in a.components:
                        c.transformation = Transform(1, 0, 0, 1, 0, 0)
                    a.width = tf


# ------------------------------------------------------------------ degree

def degree(masters):
    for m, f in masters.items():
        s = stem(f)
        heavy = (s - 46) / (404 - 46)
        disp = m in DISPLAY
        D = 520 + 140 * heavy - (14 if disp else 0)
        tv = max(44, (0.80 - 0.14 * heavy) * s)
        th = tv * 0.92
        top = 1504
        lsb = 56 + 0.10 * s
        rsb = 116 + 0.14 * s
        cx, cy = lsb + D / 2, top - D / 2
        g = f['degree']
        g.clearContours()
        g.contours.append(lib.ellipse(cx, cy, D / 2, D / 2, ccw=True))
        g.contours.append(lib.ellipse(cx, cy, D / 2 - tv, D / 2 - th, ccw=False))
        g.width = lsb + D + rsb
        # composed units: the letter starts close to the ring
        for name, base, gap in (('degreecentigrade', 'C', -40), ('degreefarenheit', 'F', -40)):
            u = f[name]
            u.clearComponents()
            u.components.append(Component('degree', Transform()))
            u.components.append(Component(base, Transform(1, 0, 0, 1, g.width + gap, 0)))
            u.width = g.width + gap + f[base].width


# ------------------------------------------------------------------ optical spacing

def spacing(masters):
    for m, f in masters.items():
        cats = f.lib.get('public.openTypeCategories', {})
        zero_w = {g.name for g in f if g.width < 100 or cats.get(g.name) == 'mark'}
        # how far each glyph's own drawing moves (marks and fixed spaces stay)
        moved = {}
        for g in f:
            if g.name in zero_w or set(g.unicodes) & FIXED_SPACES:
                moved[g.name] = 0
            else:
                moved[g.name] = 0 if (TRACK[m] < 0 and g.name in NO_TIGHTEN) else TRACK[m]
        for g in f:
            d = moved[g.name]
            if g.name in zero_w:
                # marks built from spacing parts: undo the parts' own shift
                for c in g.components:
                    t = c.transformation
                    bd = moved[c.baseGlyph]
                    c.transformation = Transform(t[0], t[1], t[2], t[3], t[4] - t[0] * bd, t[5] - t[1] * bd)
                continue
            if set(g.unicodes) & FIXED_SPACES:
                continue
            if not g.contours and not g.components:
                # word spaces open by half the letter step; tabular spaces keep the cell
                g.width += 2 * d if g.name.endswith('.tf') else d
                continue
            for c in g.contours:
                for q in c.points:
                    q.x += d
            for a in g.anchors:
                a.x += d
            seq = g.name in SEQUENTIAL or re.fullmatch(r'[a-z]+roman', g.name or '')
            spacing_comps = sorted([c for c in g.components if c.baseGlyph not in zero_w],
                                   key=lambda c: c.transformation[4])
            for c in g.components:
                t = c.transformation
                bd = moved[c.baseGlyph]
                # the base already moved by bd in its own space
                ax, ay = d - t[0] * bd, -t[1] * bd
                if seq and c in spacing_comps:
                    ax += 2 * d * spacing_comps.index(c)
                c.transformation = Transform(t[0], t[1], t[2], t[3], t[4] + ax, t[5] + ay)
            n_seq = len(spacing_comps) if seq else 1
            g.width += 2 * d * n_seq
        tfw = f['zero.tf'].width
        for n in ('figurespace',):
            f[n].width = tfw
        for n in ('punctuationspace', 'punctuationspace.tf'):
            if n in f:
                f[n].width = f['period.tf'].width


def display_finer(masters, t=0.05):
    """Display Regular a touch finer: move m03 toward m01."""
    a, b = masters['m03'], masters['m01']
    for g in list(a):
        if g.name in b and lib.same_structure(g, b[g.name]):
            ng = lib.lerp_glyph(g, b[g.name], t)
            g.clearContours()
            for c in ng.contours:
                g.contours.append(c)
            for ca, cn in zip(g.components, ng.components):
                ca.transformation = cn.transformation
            for aa, an in zip(g.anchors, ng.anchors):
                aa.x, aa.y = an.x, an.y
            g.width = ng.width


def soft_hyphen(masters):
    for f in masters.values():
        h = f['hyphen']
        if 0xAD not in h.unicodes:
            h.unicodes = list(h.unicodes) + [0xAD]


def run(masters):
    display_finer(masters)
    swap_g(masters)
    slant_t(masters)
    numerals(masters)
    math_on_figures(masters)
    degree(masters)
    spacing(masters)
    soft_hyphen(masters)
    for f in masters.values():
        for g in f:
            lib.round_glyph(g)
    lib.set_metrics(list(masters.values()), 2048)
