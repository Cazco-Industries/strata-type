"""Strata Sans: identity, weather numerals and optical spacing.

Masters: m00 (opsz 14, Thin), m01 (32, Thin), m02 (14, Regular, default),
m03 (32, Regular), m04 (14, Black), m05 (32, Black); caption() adds
m06 (8, Thin), m07 (8, Regular) and m08 (8, Black) after run().
"""
import re
from pathlib import Path
import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor
from fontTools.misc.transform import Transform
from ufoLib2.objects import Component, Anchor
import lib
import identity
import keys
import optical
from fontTools.pens.statisticsPen import StatisticsPen

TEXT = ['m00', 'm02', 'm04']
DISPLAY = ['m01', 'm03', 'm05']
PARTNER = {'m00': 'm02', 'm01': 'm03', 'm02': 'm00', 'm03': 'm01', 'm04': 'm02', 'm05': 'm03'}
FIGS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
MATH = ['plus', 'minus', 'equal', 'multiply', 'divide', 'plusminus', 'less', 'greater',
        'lessequal', 'greaterequal', 'notequal', 'approxequal', 'logicalnot']
TF_GAIN = 0
# Tabular 1: flag lengthened along its outer edge by this fraction, and
# its foot widened by this factor, so it fills the figure cell.
ONE_TF_FLAG = 0.12
FOOT_GROW = 1.10
# Width factors for the figures that read narrow next to the round zero.
WIDEN = {'zero': 1.04, 'six': 1.035, 'nine': 1.035, 'eight': 1.03, 'three': 1.025,
         'five': 1.03, 'two': 1.03, 'seven': 1.05}
# Second squaring pass on every round (kink-checked): taut, slightly
# superelliptic bowls and figures, the trait the mono carries harder.
TAUT = 0.15
# Spacing per side: open at text size, slightly tight at display size.
TRACK = {'m00': 6, 'm02': 6, 'm04': 6, 'm01': -6, 'm03': -6, 'm05': -6}
# Figures, and the punctuation that separates them, keep their text-size room
# when display tightens: 72 px readings (0123, 30.16) stay open.
NO_TIGHTEN = {'period', 'comma', 'colon', 'semicolon', 'period.tf', 'comma.tf', 'colon.tf', 'semicolon.tf'}


def keeps_room(name):
    return name in NO_TIGHTEN or name.split('.')[0] in FIGS
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

def swap_alternates(masters, pairs):
    """Exchange the drawings of each (default, alternate) pair in every master;
    components, kerning and groups follow the drawing."""
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
        for gname, members in list(f.groups.items()):
            f.groups[gname] = [swap.get(m, m) for m in members]
        newk = {}
        for (l, r), v in f.kerning.items():
            newk[(swap.get(l, l), swap.get(r, r))] = v
        f.kerning.clear(); f.kerning.update(newk)


def swap_g(masters):
    first = masters['m02']
    pairs = []
    for n in sorted(first.keys()):
        if n.startswith('G') and not n.endswith('.1') and (n + '.1') in first and '.' not in n:
            pairs.append((n, n + '.1'))
    swap_alternates(masters, pairs)
    for f in masters.values():
        if f.features.text:
            f.features.text = f.features.text.replace('name "Capital G with spur";', 'name "Capital G without spur";')
    return [a for a, _ in pairs]


def open_four(masters):
    """The open-top 4 becomes the default four (every size and style of it);
    the closed 4 moves to the alternate."""
    first = masters['m02']
    pairs = []
    for n in sorted(first.keys()):
        if not n.startswith('four') or 'ss01' in n or n.startswith(('fourdots', 'fourth', 'fourfifths', 'fourroman')):
            continue
        for alt in (n + '.ss01', n.replace('four', 'four.ss01', 1)):
            if alt != n and alt in first:
                pairs.append((n, alt))
                break
    swap_alternates(masters, pairs)
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


def footed_one(f, gt, tf):
    """Tabular 1: flag, stem and a wide foot, so the figure fills its cell.
    The upstream foot is kept (its weight follows the master) and widened;
    the flag is lengthened a little; the whole figure is centred."""
    foot = gt.contours[0]
    off = gt.components[0].transformation[4]
    flat = f['one'].copy(); lib.decompose(f, flat)
    long_flag(flat, ONE_TF_FLAG)
    xs = [p.x for p in foot.points]
    cx = (min(xs) + max(xs)) / 2
    for p in foot.points:
        p.x = cx + (p.x - cx) * FOOT_GROW
    gt.clearComponents()
    lib.copy_contours(flat, gt, Transform(1, 0, 0, 1, off, 0))
    b = lib.bounds(gt)
    lib.shift_glyph(gt, round(tf / 2 - (b[0] + b[2]) / 2))
    gt.width = tf


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
        for n in FIGS:
            gt = f[n + '.tf']
            if n == 'one':
                footed_one(f, gt, tf)
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
        lsb = 72 + 0.12 * s
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
                moved[g.name] = 0 if (TRACK[m] < 0 and keeps_room(g.name)) else TRACK[m]
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


def kern_value(f, a, b):
    """Kerning the font applies to a pair (glyph pairs before group pairs)."""
    ga = [g for g, m in f.groups.items() if g.startswith('public.kern1.') and a in m]
    gb = [g for g, m in f.groups.items() if g.startswith('public.kern2.') and b in m]
    for l, r in [(a, b)] + [(a, y) for y in gb] + [(x, b) for x in ga] + [(x, y) for x in ga for y in gb]:
        if (l, r) in f.kerning:
            return f.kerning[(l, r)]
    return 0


ONE_FLOOR = 1.2


def figure_kerning(masters):
    """Optical kerning around figures, measured per master:
    - figure + degree: the ring sits as far from every figure as from 0
      (the 4's arm no longer runs under the ring), for the default
      (tabular) and the proportional figures;
    - proportional 1 against figures: same white as 0 0, but its stem never
      sits closer to a neighbour than ONE_FLOOR of the 0 0 gap (a lone
      stem matched by area alone jams 012 at display sizes);
    - period and comma between proportional figures never tighten (30.16
      reads as three parts), except after 7 whose arm overhangs. Tabular
      figures do not kern with them at all."""
    for f in masters.values():
        pairs = {}
        prop = [pnum_name(n) for n in FIGS]
        figs = FIGS + [n + '.tf' for n in FIGS]
        pairs.update(optical.degree_kerns(f, figs))
        pairs.update(optical.degree_kerns(f, prop, ref='zero.pnum'))
        one = pnum_name('one')
        ones = [(one, x) for x in prop] + [(x, one) for x in prop if x != one]
        pairs.update(optical.pair_kerns(f, ones, ref=('zero.pnum', 'zero.pnum'), floor=ONE_FLOOR))
        for x in prop:
            for p in ('period', 'comma'):
                if x != pnum_name('seven'):
                    pairs[(x, p)] = max(0, kern_value(f, x, p))
                pairs[(p, x)] = max(0, kern_value(f, p, x))
        for x in FIGS:
            for p in ('period', 'comma'):
                pairs[(x, p)] = 0
                pairs[(p, x)] = 0
        for k, v in pairs.items():
            f.kerning[k] = v


# ------------------------------------------------------------------ tabular default

# Default glyph -> its tabular twin. After tabular_default() the default
# (cmap) glyph holds the tabular drawing, the twin becomes a reference to it,
# and the proportional drawing moves to pnum_name(default).
TAB_PAIRS = [(n, n + '.tf') for n in FIGS] + [
    ('three.1', 'three.1.tf'), ('one.ss01', 'one.tf.ss01'), ('four.ss01', 'four.tf.ss01'),
    ('six.ss01', 'six.tf.ss01'), ('nine.ss01', 'nine.tf.ss01'), ('zero.slash', 'zero.tf.slash')]


def pnum_name(name):
    if name.endswith('.ss01'):
        return name[:-5] + '.pnum.ss01'
    if name == 'zero.slash':
        return 'zero.pnum.slash'
    return name + '.pnum'


def _fill(dst, src, remap):
    dst.clearContours(); dst.clearComponents(); dst.clearAnchors()
    for c in src.contours:
        dst.contours.append(c)
    for c in src.components:
        dst.components.append(Component(remap(c.baseGlyph), c.transformation))
    for a in src.anchors:
        dst.anchors.append(Anchor(a.x, a.y, a.name))
    dst.width = src.width


def tabular_default(masters):
    """Tabular figures become the default (cmap) figures; proportional
    figures move to new `.pnum` glyphs selected by `pnum`.

    Every feature rule that runs after `pnum` in the lookup order and takes a
    default figure gets the same rule for its `.pnum` glyph, so slashed zero,
    the stylistic sets and the character variants work in both spacings.
    Composites elsewhere (circled, squared, letters drawn from figures) keep
    the proportional drawing; kerning and kerning groups of the proportional
    figures move with them; the default figures take the tabular kerning."""
    defaults = {d for d, _ in TAB_PAIRS}
    tabs = {t: d for d, t in TAB_PAIRS}
    pmap = {d: pnum_name(d) for d in defaults}
    for f in masters.values():
        assert all(d in f and t in f for d, t in TAB_PAIRS), 'figure set changed'
        assert not any(p in f for p in pmap.values()), 'pnum glyphs already present'
        old = {n: f[n].copy() for n in list(defaults) + list(tabs)}
        # 1. proportional drawings into the new glyphs
        for d, p in sorted(pmap.items()):
            g = f.newGlyph(p)
            _fill(g, old[d], lambda b: pmap.get(b, b))
        # 2. defaults take the tabular drawings
        for d, t in TAB_PAIRS:
            _fill(f[d], old[t], lambda b: pmap[b] if b in defaults else tabs.get(b, b))
        # 3. tabular twins are references to the defaults
        for d, t in TAB_PAIRS:
            g = f[t]
            g.clearContours(); g.clearComponents(); g.clearAnchors()
            g.components.append(Component(d, Transform()))
            for a in f[d].anchors:
                g.anchors.append(Anchor(a.x, a.y, a.name))
            g.width = f[d].width
        # 4. composites elsewhere keep the proportional figures
        own = defaults | set(tabs) | set(pmap.values())
        for g in f:
            if g.name in own:
                continue
            for c in g.components:
                if c.baseGlyph in defaults:
                    c.baseGlyph = pmap[c.baseGlyph]
        # 5. kerning: proportional pairs move; defaults take the tabular pairs
        for gname, members in list(f.groups.items()):
            f.groups[gname] = [pmap.get(m, m) for m in members]
        newk = {}
        for (l, r), v in f.kerning.items():
            newk[(pmap.get(l, l), pmap.get(r, r))] = v
        for (l, r), v in list(newk.items()):
            if l in tabs or r in tabs:
                newk[(tabs.get(l, l), tabs.get(r, r))] = v
        f.kerning.clear(); f.kerning.update(newk)
        # 6. glyph order, categories, production names
        order = f.lib.get('public.glyphOrder')
        if order is not None:
            for d in sorted(defaults, key=order.index):
                order.insert(order.index(d) + 1, pmap[d])
        cats = f.lib.get('public.openTypeCategories')
        if cats is not None:
            for d, p in pmap.items():
                if d in cats:
                    cats[p] = cats[d]
        ps = f.lib.get('public.postscriptNames')
        if ps is not None:
            for p in pmap.values():
                ps[p] = p
        f.features.text = tabular_features(f.features.text, pmap)


def tabular_features(text, pmap):
    start = text.index('\nfeature pnum {')
    end = text.index('} pnum;', start)
    head, pnum, tail = text[:start], text[start:end], text[end:]
    # pnum: tabular twins and defaults both go to the proportional glyphs
    def prop(mt):
        a, b = mt.group(2), mt.group(3)
        if b in pmap:
            return f'{mt.group(1)}sub {a} by {pmap[b]};\n{mt.group(1)}sub {b} by {pmap[b]};'
        return mt.group(0)
    pnum = re.sub(r'^(\s*)sub (\S+) by (\S+);$', prop, pnum, flags=re.M)
    missing = [b for b in pmap if f'sub {b} by {pmap[b]};' not in pnum]
    # a default with no tabular rule in pnum (none expected) still gets one
    if missing:
        pnum = pnum.rstrip() + '\n' + ''.join(f'    sub {b} by {pmap[b]};\n' for b in sorted(missing))
    # later features: the same rule for the proportional figure
    def later(mt):
        a, b = mt.group(2), mt.group(3)
        if a not in pmap:
            return mt.group(0)
        return f'{mt.group(0)}\n{mt.group(1)}sub {pmap[a]} by {pmap.get(b, b)};'
    tail = re.sub(r'^(\s*)sub (\S+) by (\S+);$', later, tail, flags=re.M)
    figs = '[zero one two three four five six seven eight nine]'
    tail = tail.replace(figs, figs[:-1] + ' ' + ' '.join(pmap[n] for n in FIGS) + ']')
    # contextual classes that list figures also list the proportional ones
    numeral = re.search(r'^@Numeral = \[([^\]]*)\];', head, flags=re.M)
    assert numeral, '@Numeral class changed'
    extra = [pmap[m] for m in numeral.group(1).split() if m in pmap]
    head = head[:numeral.end(1)] + ' ' + ' '.join(extra) + head[numeral.end(1):]
    return head + pnum + tail


def display_finer(masters, t=0.08):
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


def display_black(masters):
    """Display Black re-mixed toward display Regular until Black carries the
    same ink relative to Regular as at text size, so a weight step darkens
    display and text alike (the finer display Regular otherwise made display
    steps about a quarter larger)."""
    upm = masters['m02'].info.unitsPerEm
    ink = {m: lib.ink(*lib.sample_glyphs(masters[m], lib.INK_SAMPLE), upm) for m in ('m02', 'm03', 'm04', 'm05')}
    target = ink['m03'] * ink['m04'] / ink['m02']
    a, b = masters['m05'], masters['m03']
    sample, counts = lib.sample_glyphs(a, lib.INK_SAMPLE)
    other, _ = lib.sample_glyphs(b, lib.INK_SAMPLE)

    def at(k):
        return lib.ink({n: lib.lerp_glyph(g, other[n], k) for n, g in sample.items()}, counts, upm)
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if at(mid) > target:
            lo = mid
        else:
            hi = mid
    k = (lo + hi) / 2
    for g in list(a):
        if g.name in b and lib.same_structure(g, b[g.name]):
            ng = lib.lerp_glyph(g, b[g.name], k)
            g.clearContours()
            for c in ng.contours:
                g.contours.append(c)
            for ca, cn in zip(g.components, ng.components):
                ca.transformation = cn.transformation
            for aa, an in zip(g.anchors, ng.anchors):
                aa.x, aa.y = an.x, an.y
            g.width = ng.width
    return round(k, 3)


def weight_map(folder):
    """Write lib.SANS_WGHT_MAP into the designspace weight axis; named
    instances keep their user weights."""
    path = Path(folder) / 'StrataSans.designspace'
    ds = DesignSpaceDocument.fromfile(path)
    ax = next(a for a in ds.axes if a.tag == 'wght')
    old = sorted((float(i), float(o)) for i, o in ax.map)
    ax.map = list(lib.SANS_WGHT_MAP)
    for inst in ds.instances:
        loc = inst.designLocation
        if 'Weight' in loc:
            user = lib.inverse_piecewise(loc['Weight'], old)
            loc['Weight'] = lib.piecewise(user, lib.SANS_WGHT_MAP)
    ds.write(path)


def soft_hyphen(masters):
    for f in masters.values():
        h = f['hyphen']
        if 0xAD not in h.unicodes:
            h.unicodes = list(h.unicodes) + [0xAD]


def run(masters):
    display_finer(masters)
    print('sans display Black re-mixed toward display Regular by', display_black(masters))
    swap_g(masters)
    open_four(masters)
    keys.sans(masters, swap_alternates)
    slant_t(masters)
    identity.terminals(masters, identity.eligible(masters['m02']) + ['_part.t_base', '_part.f_base'])
    identity.y_tail(masters)
    identity.r_leg(masters)
    identity.rounds(masters)
    print('sans taut rounds', identity.rounds(masters, alpha=TAUT), flush=True)
    keys.sans_shapes(masters)
    numerals(masters)
    math_on_figures(masters)
    degree(masters)
    spacing(masters)
    tabular_default(masters)
    figure_kerning(masters)
    soft_hyphen(masters)
    for f in masters.values():
        for g in f:
            lib.round_glyph(g)
    lib.set_metrics(list(masters.values()), 2048)


# ------------------------------------------------------------------ caption masters

# Caption masters (opsz 8), for 8-13 px text: the finished text masters with
# heavier vertical stems and looser spacing, so small text keeps a dark core
# instead of turning into grey edges. The Regular stem gains CAPTION_STEM
# units; Thin and Black gain what keeps the text masters' ink progression
# (ink of the sample relative to Regular), so weights step evenly at every
# size. Every glyph opens by half its stem gain plus CAPTION_TRACK per side.
CAPTION = {'m06': ('m00', 100), 'm07': ('m02', 400), 'm08': ('m04', 900)}
CAPTION_STEM = 44
CAPTION_TRACK = 24
# Drawn boxes, not strokes: emboldening closes their small counters.
CAPTION_KEEP = {'.notdef'}
CAPTION_OPSZ = 8
CAPTION_STYLE = {100: 'Caption Thin', 400: 'Caption', 900: 'Caption Black'}
# Rounded reads each caption master's stem gain from this lib key.
STEM_KEY = 'com.strata.captionStemGain'


def caption(folder):
    folder = Path(folder)
    src = {t: ufoLib2.Font.open(folder / f'StrataSans-{t}.ufo', lazy=False) for t, _ in CAPTION.values()}
    upm = src['m02'].info.unitsPerEm
    samples = {t: lib.sample_glyphs(f, lib.INK_SAMPLE) for t, f in src.items()}
    ink_text = {t: lib.ink(*samples[t], upm) for t in src}
    reg = lib.ink(*samples['m02'], upm, CAPTION_STEM)
    bold = {}
    for c, (t, _) in CAPTION.items():
        bold[c] = CAPTION_STEM if t == 'm02' else lib.solve_bold(*samples[t], upm, reg * ink_text[t] / ink_text['m02'])
    for c, (t, w) in CAPTION.items():
        f = src[t]
        for g in f:
            if g.name not in CAPTION_KEEP:
                lib.embolden(g, bold[c])
        TRACK[c] = bold[c] / 2 + CAPTION_TRACK
        spacing({c: f})
        for g in f:
            lib.round_glyph(g)
        f.info.styleName = CAPTION_STYLE[w]
        f.info.postscriptFontName = 'StrataSans-' + CAPTION_STYLE[w].replace(' ', '')
        f.lib[STEM_KEY] = round(bold[c], 2)
        f.save(folder / f'StrataSans-{c}.ufo', overwrite=True)
    path = folder / 'StrataSans.designspace'
    ds = DesignSpaceDocument.fromfile(path)
    next(a for a in ds.axes if a.tag == 'opsz').minimum = CAPTION_OPSZ
    for c, (t, w) in CAPTION.items():
        sd = SourceDescriptor()
        sd.filename = f'StrataSans-{c}.ufo'
        sd.path = str(folder / sd.filename)
        sd.name = 'Strata Sans ' + CAPTION_STYLE[w]
        sd.familyName, sd.styleName = 'Strata Sans', CAPTION_STYLE[w]
        sd.location = {'Optical size': CAPTION_OPSZ, 'Weight': w}
        ds.addSource(sd)
    ds.write(path)
    return {c: round(b, 1) for c, b in bold.items()}
