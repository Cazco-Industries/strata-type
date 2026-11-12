"""Strata Sans Rounded: a numeric style made by rounding the sans text masters.

Corners are found once on the Regular master and filleted in every master
with radii proportional to that master's stem, so the masters stay
compatible. Stroke ends shorter than 1.7 stems become full semicircles.
Figures are tabular by default; `pnum` selects proportional figures.
"""
import shutil
from pathlib import Path
import ufoLib2
from ufoLib2.objects import Font, Glyph, Component
from fontTools.misc.transform import Transform
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
import lib

MASTERS = {'m00': 100, 'm02': 400, 'm04': 900}
REF = 'm02'
FIGS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
# name in Rounded -> (source glyph in sans, unicodes)
GLYPHS = {}
for i, n in enumerate(FIGS):
    GLYPHS[n] = (n + '.tf', [0x30 + i])
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


def round_masters(src):
    ref = src[REF]
    out = {m: {} for m in src}
    for name, (s, unis) in GLYPHS.items():
        gs = {m: flat(f, s) for m, f in src.items()}
        st = stem(ref)
        plans = []
        for c in gs[REF].contours:
            plans.append(lib.classify_corners(c, st))
        for m, g in gs.items():
            sm = stem(src[m])
            for c, (corners, terms) in zip(g.contours, plans):
                lib.fillet_contour(c, corners, terms, r_convex=0.46 * sm, r_concave=0.14 * sm)
            g.unicodes = unis
            lib.round_glyph(g)
            out[m][name] = g
    return out


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
    rounded = round_masters(src)
    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.tag = 'wght'; ax.name = 'Weight'; ax.minimum = 100; ax.default = 400; ax.maximum = 900
    ax.map = [(100, 100), (400, 400), (500, 490), (600, 580), (700, 670), (800, 780), (900, 900)]
    ds.addAxis(ax)
    order = ['.notdef'] + list(GLYPHS)
    for m, w in MASTERS.items():
        s = src[m]
        f = Font()
        f.info.familyName = 'Strata Sans Rounded'
        f.info.styleName = {100: 'Thin', 400: 'Regular', 900: 'Black'}[w]
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
        path = dest / f'StrataSansRounded-{m}.ufo'
        f.save(path, overwrite=True)
        sd = SourceDescriptor(); sd.filename = path.name; sd.location = {'Weight': w}
        sd.familyName = 'Strata Sans Rounded'; sd.styleName = f.info.styleName
        ds.addSource(sd)
    # Same named weights as Strata Sans, placed in user units.
    for w, nm in ((100, 'Thin'), (200, 'ExtraLight'), (300, 'Light'), (400, 'Regular'), (500, 'Medium'),
                  (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')):
        i = InstanceDescriptor(); i.familyName = 'Strata Sans Rounded'; i.styleName = nm
        i.userLocation = {'Weight': w}
        ds.addInstance(i)
    ds.write(dest / 'StrataSansRounded.designspace')
    for n in ('COPYRIGHT.txt', 'OFL.txt'):
        shutil.copyfile(sans_dir / n, dest / n)
