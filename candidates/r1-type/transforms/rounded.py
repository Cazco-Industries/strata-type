"""Strata Sans Rounded: a numeric style made by rounding the sans masters.

Rounded has the same optical-size axis as the sans, so its spacing matches
the regular at every size (open at text sizes, tight at display sizes). Only
the three text masters are rounded. The display masters reuse those outlines
(the display Regular moved a touch toward Thin, as in the sans) and take the
sans's display spacing. Display outlines drawn from the sans display masters
would cut terminals at other points of each curve, and the smooth joins that
rounding makes there would kink between sizes.

Figures are tabular by default, in a cell a little narrower than the sans
cell; each figure is condensed or widened (stems kept) so all ten fill the
cell evenly, and the 1 is the footed tabular 1. `pnum` selects proportional
figures, kerned like the sans. Corners are found once on the Regular master
and filleted in every master with radii proportional to that master's stem;
stroke ends shorter than 1.7 stems become full semicircles. A stroke-end cap
reaches further along its curve in heavier masters, so where a glyph's joins
would kink between weights, every master's curve cuts move part of the way
toward the curve points the Regular uses (the smallest share that clears the
interpolation check).
"""
import math
import shutil
from pathlib import Path
import ufoLib2
from ufoLib2.objects import Font
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
import lib
import identity
import optical

MASTERS = {'m00': (14, 100), 'm01': (32, 100), 'm02': (14, 400),
           'm03': (32, 400), 'm04': (14, 900), 'm05': (32, 900)}
PARTNER = {'m00': 'm02', 'm01': 'm03', 'm02': 'm00', 'm03': 'm01', 'm04': 'm02', 'm05': 'm03'}
REF = 'm02'
TEXT = ('m00', 'm02', 'm04')
# display master -> text master whose rounded outlines it reuses
DISPLAY = {'m01': 'm00', 'm03': 'm02', 'm05': 'm04'}
# The display Regular is a touch finer, as in the sans: moved toward Thin.
FINER = {'m03': ('m00', 0.08)}
FIGS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
# Tabular cell as a share of the sans tabular cell, the smallest side
# bearing as a share of the cell, and the narrowest figure as a share of the
# widest: together they make the tabular figures fill their cells evenly.
CELL = 0.925
SIDE = 0.085
EVEN = 0.95
# Fillet radii in stems: convex corners, and the joins (concave corners).
R_CONVEX = 0.95
R_CONCAVE = 0.48
# Bowls relax toward circular arcs (the sans pushes them squarer): each
# quarter-ish curve's handles shorten to SOFT of a circular arc's for the
# same turn, and never lengthen, so round figures look soft and a ring that
# is already circular (the degree) stays round.
SOFT = 0.97
# name in Rounded -> (source glyph in sans, unicodes)
GLYPHS = {}
for i, n in enumerate(FIGS):
    GLYPHS[n] = ('one.tf' if n == 'one' else n, [0x30 + i])
    GLYPHS[n + '.pnum'] = (n, [])
GLYPHS.update({
    'space': ('space', [0x20]), 'figurespace': ('figurespace', [0x2007]),
    'punctuationspace': ('punctuationspace', [0x2008]), 'thinspace': ('thinspace', [0x2009]),
    'period': ('period.tf', [0x2E]), 'colon': ('colon.tf', [0x3A]), 'comma': ('comma.tf', [0x2C]),
    'period.pnum': ('period', []), 'colon.pnum': ('colon', []), 'comma.pnum': ('comma', []),
    'percent': ('percent', [0x25]), 'degree': ('degree', [0xB0]),
    'degreecentigrade': ('degreecentigrade', [0x2103]), 'degreefarenheit': ('degreefarenheit', [0x2109]),
    'minus': ('minus', [0x2212]), 'plus': ('plus', [0x2B]), 'hyphen': ('hyphen', [0x2D]),
    'plusminus': ('plusminus', [0xB1]), 'slash': ('slash', [0x2F]), 'fraction': ('fraction', [0x2044]),
    'C': ('C', [0x43]), 'F': ('F', [0x46]),
})
PNUM = [n for n in GLYPHS if n.endswith('.pnum')]


def flat(font, name):
    g = font[name].copy()
    lib.decompose(font, g)
    return g


def stem(font):
    g = font['H']
    ux = sorted(set(round(p.x) for c in g.contours for p in c.points))
    return ux[1] - ux[0]


def fit_figures(src, gs_by_name):
    """Tabular figures: scale each figure's width (stems compensated) into
    the band [EVEN * widest, widest] and centre it in the Rounded cell."""
    for m, f in src.items():
        cell = round(CELL * f['zero.tf'].width)
        widest = cell * (1 - 2 * SIDE)
        lo = EVEN * widest
        vm, vp = stem(f), stem(src[PARTNER[m]])
        for n in FIGS:
            g = gs_by_name[n][m]
            p = gs_by_name[n][PARTNER[m]]
            b = lib.bounds(g)
            ink = b[2] - b[0]
            s = min(widest, max(lo, ink)) / ink
            if abs(s - 1) > 1e-3:
                ng = lib.scale_compensated(g, p, s, 1.0, vm, vp)
            else:
                ng = g.copy()
            b = lib.bounds(ng)
            lib.shift_glyph(ng, cell / 2 - (b[0] + b[2]) / 2)
            ng.width = cell
            gs_by_name[n][m] = ng
        gs_by_name['figurespace'][m].width = cell


def round_masters(src):
    ref = src[REF]
    flats = {name: {m: flat(f, s) for m, f in src.items()} for name, (s, _) in GLYPHS.items()}
    fit_figures(src, flats)
    out = {m: {} for m in src}
    st = stem(ref)
    for name, (s, unis) in GLYPHS.items():
        gs = flats[name]
        plan = [identity.tension_plan(c, 0.0) for c in gs[REF].contours]
        for g in gs.values():
            for c, pl in zip(g.contours, plan):
                if pl:
                    relax(c, pl)
        plans = [lib.classify_corners(c, st) for c in gs[REF].contours]
        best = None
        for alpha in TRANSFER:
            done = fillet(src, gs, plans, alpha)
            n = kinks(done, name)
            if best is None or n < best[0]:
                best = (n, alpha, done)
            if n == 0:
                break
        n, alpha, done = best
        if alpha:
            print(f'  {name}: fillet joins moved {alpha:.2f} of the way to the Regular\'s curve points')
        if n:
            print(f'  {name}: {n} kink(s) left')
        for m, g in done.items():
            g.unicodes = unis
            out[m][name] = g
    return out


def relax(contour, plan_segs):
    """Shorten each planned curve's handles to SOFT of a circular arc's
    (handle = 4/3 tan(turn/4) r, as a share of the distance to the tangent
    intersection); handles already shorter are kept."""
    segs = lib.to_segments(contour)
    starts = [segs[i - 1]['end'] for i in range(len(segs))]
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
        turn = math.acos(max(-1, min(1, lib.dot(lib.unit(d0), lib.unit(lib.mul(d3, -1))))))
        target = SOFT * 4 / 3 * math.tan(turn / 4) / math.tan(turn / 2)
        f0, f3 = min(1 / a, target), min(1 / b, target)
        seg['ctrl'] = [lib.add(p0, lib.mul(d0, f0 * a)), lib.add(p3, lib.mul(d3, f3 * b))]
    lib.from_segments(contour, segs)


# Shares of the way each master's fillet joins may move toward the curve
# points the Regular uses; the first share that interpolates without kinks
# is kept, so outlines change no more than they must.
TRANSFER = (0.0, 0.25, 0.5, 0.75, 1.0)


def fillet(src, gs, plans, alpha):
    """Fillet copies of one glyph's masters. Radii scale with each master's
    stem; with alpha > 0, each curve cut moves toward the Regular's."""
    done = {REF: gs[REF].copy()}
    sr = stem(src[REF])
    t_ref = [lib.fillet_contour(c, cs, ts, r_convex=R_CONVEX * sr, r_concave=R_CONCAVE * sr)
             for c, (cs, ts) in zip(done[REF].contours, plans)]
    for m, g in gs.items():
        if m == REF:
            continue
        g = done[m] = g.copy()
        sm = stem(src[m])
        for c, (cs, ts), tr in zip(g.contours, plans, t_ref):
            lib.fillet_contour(c, cs, ts, r_convex=R_CONVEX * sm, r_concave=R_CONCAVE * sm, t_ref=tr, alpha=alpha)
    for g in done.values():
        lib.round_glyph(g)
    return done


def kinks(done, name):
    """Kinks the interpolation check finds between the text masters, in
    weight order (the display masters reuse these outlines)."""
    from fontTools.varLib.interpolatable import test_gen
    order = [m for m in TEXT if m in done]
    gs = [{name: done[m]} for m in order]
    return sum(1 for _, p in test_gen(gs, glyphs=[name], names=order, upem=2048) if p['type'] == 'kink')


def display_masters(src, text_out):
    """Display masters: the text outlines, re-spaced. Tabular glyphs are
    centred in the display cell; every other glyph moves its sidebearings by
    the amounts the sans moves them between the text and display masters."""
    out = {}
    for d, t in DISPLAY.items():
        out[d] = {}
        cell = round(CELL * src[d]['zero.tf'].width)
        for name, (s, _) in GLYPHS.items():
            base = text_out[t][name]
            if d in FINER:
                other, k = FINER[d]
                g = lib.lerp_glyph(base, text_out[other][name], k)
            else:
                g = base.copy()
            if name in FIGS or name == 'figurespace':
                if g.contours:
                    b = lib.bounds(g)
                    lib.shift_glyph(g, cell / 2 - (b[0] + b[2]) / 2)
                g.width = cell
            else:
                gt, gd = flat(src[t], s), flat(src[d], s)
                if gd.contours:
                    bt, bd = lib.bounds(gt), lib.bounds(gd)
                    dl = bd[0] - bt[0]
                    dr = (gd.width - bd[2]) - (gt.width - bt[2])
                    lib.shift_glyph(g, dl)
                    g.width = g.width + dl + dr
                else:
                    g.width = g.width + gd.width - gt.width
            g.unicodes = list(base.unicodes)
            lib.round_glyph(g)
            out[d][name] = g
    return out


def kerning(f):
    """Figure + degree (tabular and proportional) and proportional 1-pairs,
    measured on the rounded outlines."""
    pairs = {}
    pairs.update(optical.degree_kerns(f, FIGS))
    pnums = [n + '.pnum' for n in FIGS]
    pairs.update(optical.degree_kerns(f, pnums, ref='zero.pnum'))
    ones = [('one.pnum', x) for x in pnums] + [(x, 'one.pnum') for x in pnums if x != 'one.pnum']
    pairs.update(optical.pair_kerns(f, ones, ref=('zero.pnum', 'zero.pnum')))
    for k, v in pairs.items():
        f.kerning[k] = v


def features():
    a = ' '.join(n[:-5] for n in PNUM)
    b = ' '.join(PNUM)
    return (f'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n\n'
            f'@TAB = [{a}];\n@PROP = [{b}];\n\n'
            f'feature pnum {{ sub @TAB by @PROP; }} pnum;\n'
            f'feature tnum {{ sub @PROP by @TAB; }} tnum;\n')


def make(sans_dir):
    sans_dir = Path(sans_dir)
    dest = sans_dir.parent / 'sans-rounded'
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir()
    src = {m: ufoLib2.Font.open(sans_dir / f'StrataSans-{m}.ufo') for m in MASTERS}
    rounded = round_masters({m: src[m] for m in TEXT})
    rounded.update(display_masters(src, rounded))
    ds = DesignSpaceDocument()
    op = AxisDescriptor(); op.tag = 'opsz'; op.name = 'Optical size'; op.minimum = 14; op.default = 14; op.maximum = 32
    ds.addAxis(op)
    ax = AxisDescriptor(); ax.tag = 'wght'; ax.name = 'Weight'; ax.minimum = 100; ax.default = 400; ax.maximum = 900
    ax.map = [(100, 100), (400, 400), (500, 490), (600, 580), (700, 670), (800, 780), (900, 900)]
    ds.addAxis(ax)
    order = ['.notdef'] + list(GLYPHS)
    for m, (opsz, w) in MASTERS.items():
        s = src[m]
        f = Font()
        f.info.familyName = 'Strata Sans Rounded'
        style = {100: 'Thin', 400: 'Regular', 900: 'Black'}[w]
        f.info.styleName = style if opsz == 14 else ('Display' if w == 400 else 'Display ' + style)
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
        f.features.text = features()
        kerning(f)
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
