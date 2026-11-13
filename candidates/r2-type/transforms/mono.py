"""Strata Mono: matched to Strata Sans, squarer curves, missing core glyphs.

Masters: m00 Light (default), m01 Bold. Ligature and contextual features
are kept as they are, except that the closed-ring @, the conventional & and
the dotted 0 are the defaults; the old forms (open @, Et-style & with its &&
ligature, the ~@ ligature, the slashed 0) move to ss05, ss03 and zero.

Its own drawing, shared with Strata Sans: rounds squared harder than the
sans's (MONO_ROUNDS on top of the first squaring pass), and the family's
axis-cut terminals (identity.terminals), so C G J Q S, a c e f g j l r s t y
and 2 5 end flat on a horizontal or vertical cut (3 6 9 cannot be cut
compatibly in both masters and keep their ends).
"""
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
# bars move out by SPREAD bar heights. The !== slash is decomposed and
# stretched along its own axis, keeping its angle, thickness and overhang.
SPREAD = 0.5
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
        g.clearComponents()
        for c in comps:
            if c.baseGlyph != SLASH:
                g.components.append(c)
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
        # temperature units in one cell: a small ring and a narrowed letter
        margin = 0.06 * W
        heavy = max(0.0, (st - 125) / 170)
        D = 0.31 * W + 0.07 * W * heavy
        wall = min(0.75 * st, 0.27 * D)
        top = f.info.capHeight + 0.012 * f.info.unitsPerEm
        gap = 0.035 * W
        for name, uni, base in (('uni2103', 0x2103, 'C'), ('uni2109', 0x2109, 'F')):
            g = new_glyph(f, name, [uni], W)
            for c in ring(margin + D / 2, top, D, wall, wall * 0.92):
                g.contours.append(c)
            room = W - 2 * margin - D - gap
            lt = condensed(f, p, base, room, st, stems[pairs[m]])
            bl = lib.bounds(lt)
            lib.copy_contours(lt, g, Transform(1, 0, 0, 1, margin + D + gap - bl[0], 0))
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
            if gg.name.startswith('uni2') and gg.name[3:7] in ('2032', '2033', '2071', '2103', '2109', '2152', '201B'):
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


def run(masters, folder):
    reorder_components(masters)
    square_curves(masters)
    for f in masters.values():
        scale_font(f, S)
    mp = align_weights(masters)
    open_triple_bars(masters)
    add_glyphs(masters)
    at_amp_defaults(masters)
    print('mono squarer rounds', identity.rounds(masters, alpha=MONO_ROUNDS, ref_name='m00'))
    cut = identity.terminals(masters, identity.eligible(masters['m00']), ref_name='m00',
                             groups={'m00': ('m00', 'm01')}, text={'m00'})
    print('mono axis-cut terminals', len(cut), ' '.join(n for n in sorted(cut) if len(n) == 1 or n.isascii() and '.' not in n)[:400])
    keys.mono(masters)
    mp = ink_steps(masters, mp, folder.parent / 'sans')
    lib.set_metrics(list(masters.values()), masters['m00'].info.unitsPerEm)
    write_designspace(folder / 'StrataMono.designspace', mp)
    print('mono weights', mp)
    return masters
