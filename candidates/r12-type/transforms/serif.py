"""Strata Serif: matched to Strata Sans, plus the missing core glyphs.

The whole design is scaled by 1.09 so its cap height equals the sans cap
height (0.730 vs 0.728 em); the x-height then sits at 0.518 em, a natural
serif proportion under the sans 0.546. The em itself (1000) is unchanged.
"""
import re
import math
from pathlib import Path
import ufoLib2
from fontTools.pens.areaPen import AreaPen
from fontTools.misc.transform import Transform
from ufoLib2.objects import Component, Glyph, Contour, Point
import unicodedata
import lib
import identity

S = 1.09
INFO_SCALE = ['ascender', 'descender', 'xHeight', 'capHeight', 'italicAngle_skip',
              'openTypeHheaAscender', 'openTypeHheaDescender', 'openTypeHheaLineGap', 'openTypeHheaCaretOffset',
              'openTypeOS2TypoAscender', 'openTypeOS2TypoDescender', 'openTypeOS2TypoLineGap',
              'openTypeOS2WinAscent', 'openTypeOS2WinDescent',
              'openTypeOS2SubscriptXSize', 'openTypeOS2SubscriptYSize', 'openTypeOS2SubscriptXOffset',
              'openTypeOS2SubscriptYOffset', 'openTypeOS2SuperscriptXSize', 'openTypeOS2SuperscriptYSize',
              'openTypeOS2SuperscriptXOffset', 'openTypeOS2SuperscriptYOffset', 'openTypeOS2StrikeoutSize',
              'openTypeOS2StrikeoutPosition', 'postscriptUnderlineThickness', 'postscriptUnderlinePosition']
INFO_LISTS = ['postscriptBlueValues', 'postscriptOtherBlues', 'postscriptFamilyBlues', 'postscriptFamilyOtherBlues',
              'postscriptStemSnapH', 'postscriptStemSnapV']
NUM = re.compile(r'(?<![\w.@\-])(-?\d+)(?![\w.])')
# serif masters: weight 0/394/1000 at opsz 8 (m00-02), 20 (m03-05), 60 (m06-08)
TEXT = ['m03', 'm04', 'm05']


def scale_glyph(g, s):
    # Outline points keep two decimals: integer rounding after a scale bends
    # smooth points, and the compiler rounds once at the end anyway.
    for c in g.contours:
        for p in c.points:
            p.x = round(p.x * s, 2); p.y = round(p.y * s, 2)
    for a in g.anchors:
        a.x = round(a.x * s); a.y = round(a.y * s)
    for c in g.components:
        t = c.transformation
        c.transformation = Transform(t[0], t[1], t[2], t[3], round(t[4] * s), round(t[5] * s))
    g.width = round(g.width * s)


def scale_font(f, s):
    for layer in f.layers:
        for g in layer:
            scale_glyph(g, s)
    k = {pair: round(v * s) for pair, v in f.kerning.items()}
    f.kerning.clear(); f.kerning.update(k)
    for key in INFO_SCALE:
        v = getattr(f.info, key, None)
        if isinstance(v, (int, float)):
            setattr(f.info, key, round(v * s))
    for key in INFO_LISTS:
        v = getattr(f.info, key, None)
        if v:
            setattr(f.info, key, [round(x * s) for x in v])
    f.features.text = scale_features(f.features.text, s)


def scale_features(text, s):
    out = []
    in_base = False
    for line in text.split('\n'):
        st = line.strip()
        if st.startswith('table BASE'):
            in_base = True
        if in_base or re.search(r'\bpos\b|\bposition\b|<anchor', st) and not st.startswith('#'):
            code, sep, comment = line.partition('#')
            code = NUM.sub(lambda m: str(round(int(m.group(1)) * s)), code)
            line = code + sep + comment
        if in_base and st.startswith('}'):
            in_base = False
        out.append(line)
    return '\n'.join(out)


def set_hhea(text, asc, desc):
    text = re.sub(r'(?<![A-Za-z])Ascender -?\d+;', f'Ascender {asc};', text)
    text = re.sub(r'(?<![A-Za-z])Descender -?\d+;', f'Descender {desc};', text)
    return text


def set_os2(text, info):
    """The features file carries its own OS/2 block, which wins over the UFO
    info at compile time, so the scaled and matched values are written there."""
    vals = {'TypoAscender': info.openTypeOS2TypoAscender, 'TypoDescender': info.openTypeOS2TypoDescender,
            'TypoLineGap': info.openTypeOS2TypoLineGap, 'winAscent': info.openTypeOS2WinAscent,
            'winDescent': info.openTypeOS2WinDescent, 'XHeight': round(info.xHeight),
            'CapHeight': round(info.capHeight)}
    for k, v in vals.items():
        text, n = re.subn(rf'(?<![A-Za-z]){k} -?\d+;', f'{k} {v};', text)
        assert n == 1, (k, n)
    return text


# ------------------------------------------------------------------ new glyphs

def new_glyph(f, name, unis, width):
    if name in f:
        raise ValueError(f'{name} already exists')
    g = f.newGlyph(name)
    g.unicodes = unis
    g.width = width
    order = f.lib.get('public.glyphOrder')
    if order is not None and name not in order:
        order.append(name)
    return g


def add_glyphs(f):
    em = f.info.unitsPerEm
    new_glyph(f, 'uni2000', [0x2000], em // 2)
    new_glyph(f, 'uni2001', [0x2001], em)
    new_glyph(f, 'uni2008', [0x2008], f['period'].width)
    g = new_glyph(f, 'uni2011', [0x2011], f['hyphen'].width)
    g.components.append(Component('hyphen', Transform()))
    # high reversed-9 quote: the opening quote turned over, drawn as outlines
    ql = f['quoteleft']
    b = lib.bounds(ql, f)
    flat = ql.copy(); lib.decompose(f, flat)
    g = new_glyph(f, 'uni201B', [0x201B], ql.width)
    lib.copy_contours(flat, g, Transform(1, 0, 0, -1, 0, b[1] + b[3]), reverse=True)
    # composed temperature units
    deg = f['degree']
    for name, uni, base, gap in (('uni2103', 0x2103, 'C', -0.012), ('uni2109', 0x2109, 'F', -0.004)):
        off = round(deg.width + gap * em)
        g = new_glyph(f, name, [uni], off + f[base].width)
        g.components.append(Component('degree', Transform()))
        g.components.append(Component(base, Transform(1, 0, 0, 1, off, 0)))
    # vulgar fractions, spaced like the existing ones in this master
    third = f['onethird'].components
    nx, fx, dx = (c.transformation[4] for c in third)
    k7 = f['seveneighths'].components[1].transformation[4] - fx
    k4 = f['onequarter'].components[2].transformation[4] - dx
    names = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    for uni, num, den in ((0x2150, 1, '7'), (0x2151, 1, '9'), (0x2152, 1, '10'), (0x2155, 1, '5'),
                          (0x2156, 2, '5'), (0x2157, 3, '5'), (0x2158, 4, '5'), (0x2159, 1, '6'),
                          (0x215A, 5, '6')):
        shift = k7 if num == 7 else 0
        x = fx + shift
        comps = [Component(names[num] + '.numr', Transform()), Component('fraction', Transform(1, 0, 0, 1, x, 0))]
        x = dx + shift + (k4 if den == '4' else 0)
        for ch in den:
            comps.append(Component(names[int(ch)] + '.dnom', Transform(1, 0, 0, 1, x, 0)))
            x += f[names[int(ch)] + '.dnom'].width
        g = new_glyph(f, f'uni{uni:04X}', [uni], x)
        for c in comps:
            g.components.append(c)
    arrows(f)


def arrows(f):
    """Left-right and up-down arrows from this master's right arrow outline."""
    ar = f['arrowright']
    flat = ar.copy(); lib.decompose(f, flat)
    pts = [(p.x, p.y) for p in flat.contours[0].points]
    assert len(pts) == 14, 'arrowright shape changed'
    head = pts[2:12]
    tail_lo, tail_hi = pts[1], pts[12]
    x0 = pts[0][0]
    tip = max(x for x, _ in head)
    # The two heads must not meet: the arrow holds two full heads (barb end
    # to tip) plus a visible shaft of at least 0.6 of a head between them.
    head_len = tip - min(x for x, _ in head)
    length = max(tip - x0, 2.6 * head_len)
    cx = x0 + length * 0.5
    mir = lambda p: (2 * cx - p[0], p[1])
    # move the right head out so both heads keep their shapes
    shift = (x0 + length) - tip
    right = [(x + shift, y) for x, y in head]
    left = [mir(p) for p in reversed(right)]
    # the shaft keeps the tail's thickness at the middle and thins toward both heads
    poly = right + [(cx, tail_hi[1])] + left + [(cx, tail_lo[1])]
    xs = [p[0] for p in poly]
    dxs = x0 - min(xs)
    poly = [(x + dxs, y) for x, y in poly]
    g = new_glyph(f, 'uni2194', [0x2194], 0)
    g.width = round(max(x for x, _ in poly) + (ar.width - tip))
    g.contours.append(Contour(points=[Point(round(x), round(y), 'line') for x, y in poly]))
    # up-down arrow: the same outline turned a quarter, centred like arrowup
    up = f['arrowup']
    bu = lib.bounds(up, f)
    bb = lib.bounds(g)
    cxu = (bu[0] + bu[2]) / 2
    cyl = (bb[1] + bb[3]) / 2
    cyu = (bu[1] + bu[3]) / 2
    h = new_glyph(f, 'uni2195', [0x2195], up.width)
    # rotate 90 degrees counter-clockwise about the double arrow's centre, then place
    bx = (bb[0] + bb[2]) / 2
    rot = [(cxu - (y - cyl), cyu + (x - bx)) for x, y in poly]
    h.contours.append(Contour(points=[Point(round(x), round(y), 'line') for x, y in rot]))


# ------------------------------------------------------------------ lowercase

# X-height raise per optical size (share of the master's x-height): the
# caption design is already large, text and display gain the most, so the
# serif lowercase sits closer to the sans and mono lowercase.
XH_GAIN = {8: 0.015, 20: 0.04, 60: 0.05}
# Descenders (p q g y j) shortened by this share of their depth, and
# ascenders (b d f h k l) lowered by ASC_CUT units, per optical size. At
# 0.10 and 20 at every size a serif headline set at line-height 1.13 at
# 48 px kept 3.9 px between a descender and the next line's ascender (about
# 3 px once antialiased; 5.6 px with a 0.23 cut read as loose). The
# display master cuts a little more, so a 48 px headline (opsz 48, 0.7 of
# the way from the text to the display master) keeps about 4.6 px.
DEPTH_CUT = {8: 0.10, 20: 0.10, 60: 0.14}
ASC_CUT = {8: 20, 20: 20, 60: 30}
# Squarer rounds, the trait the family shares (the sans uses 0.20).
ROUNDS = 0.16
OPSZ = {'m00': 8, 'm01': 8, 'm02': 8, 'm03': 20, 'm04': 20, 'm05': 20, 'm06': 60, 'm07': 60, 'm08': 60}


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class YMap:
    """A smooth (C1) vertical remap: the x-height rises by gain, ascender
    tops and the baseline stay, descenders shorten by cut. Zero slope change
    at the baseline, x-height and ascender, so serifs keep their thickness."""
    def __init__(self, xh, asc, gain, depth, cut, top=0.0):
        self.xh, self.asc, self.gain, self.depth, self.cut, self.top = xh, asc, gain, depth, cut, top

    def s(self, y):
        if y <= 0:
            return 0.0
        if y <= self.xh:
            return smooth(y / self.xh)
        return 1 - smooth((y - self.xh) / (self.asc - self.xh))

    def lift(self, y):
        """Vertical move at y: x-height gain, minus the ascender cut above it."""
        return self.gain * self.s(y) - (self.top * smooth((y - self.xh) / (self.asc - self.xh)) if y > self.xh else 0.0)

    def __call__(self, y):
        if y < 0:
            d0, d1 = 0.25 * self.depth, 0.7 * self.depth
            return y + self.cut * smooth((-y - d0) / (d1 - d0))
        return y + self.lift(y)


def lowercase_names(f):
    cmap = {}
    for g in f:
        for u in g.unicodes:
            cmap.setdefault(g.name, u)
    inv = {}
    for name, u in cmap.items():
        inv.setdefault(name, u)
    xh = f.info.xHeight
    out = []
    for g in f:
        u = cmap.get(g.name) or cmap.get(g.name.split('.')[0])
        if u is None:
            # ligatures (f_t, f_f_i): lowercase when every part is
            parts = [inv.get(n) for n in g.name.split('.')[0].split('_')]
            if len(parts) < 2 or None in parts or any(unicodedata.category(chr(v)) != 'Ll' for v in parts):
                continue
        elif unicodedata.category(chr(u)) != 'Ll':
            continue
        if any(t in g.name for t in ('.sc', '.sups', '.subs', '.sinf', '.numr', '.dnom', '.ordn')):
            continue
        out.append(g.name)
    return out


def resmooth(contour):
    """Keep smooth points smooth after a non-linear remap: both handles are
    turned onto their mean direction, keeping their lengths."""
    pts = contour.points
    n = len(pts)
    for i, p in enumerate(pts):
        if p.type is None or not p.smooth:
            continue
        a, b = pts[i - 1], pts[(i + 1) % n]
        if a.type is not None and b.type is not None:
            continue
        va = (p.x - a.x, p.y - a.y); vb = (b.x - p.x, b.y - p.y)
        la, lb = lib.norm(va), lib.norm(vb)
        if la < 1e-6 or lb < 1e-6:
            continue
        d = lib.unit(lib.add(lib.unit(va), lib.unit(vb)))
        if a.type is None:
            a.x, a.y = p.x - d[0] * la, p.y - d[1] * la
        if b.type is None:
            b.x, b.y = p.x + d[0] * lb, p.y + d[1] * lb


def lowercase_proportions(masters):
    ref = masters['m04']
    names = set(lowercase_names(ref))
    marks = {g.name for g in ref if any(unicodedata.category(chr(u)) == 'Mn' for u in g.unicodes)
             or g.name.endswith(('cmb', 'cmb.cap', 'comb'))}
    for m, f in masters.items():
        xh = f.info.xHeight
        asc = lib.bounds(f['l'], f)[3]
        depth = -lib.bounds(f['p'], f)[1]
        gain = XH_GAIN[OPSZ[m]] * xh
        ym = YMap(xh, asc, gain, depth, DEPTH_CUT[OPSZ[m]] * depth, ASC_CUT[OPSZ[m]])
        for name in names:
            g = f[name]
            for c in g.contours:
                b = (min(p.y for p in c.points), max(p.y for p in c.points))
                if b[0] > xh * 1.02:
                    # dots and other parts wholly above the x-height move rigidly
                    dy = ym.lift(b[0])
                    for p in c.points:
                        p.y += dy
                    continue
                for p in c.points:
                    p.y = ym(p.y)
                resmooth(c)
            for a in g.anchors:
                a.y = round(ym(a.y))
            for c in g.components:
                if c.baseGlyph in marks:
                    t = c.transformation
                    bb = lib.bounds(f[c.baseGlyph], f)
                    if bb[1] + t[5] > xh * 0.5:
                        c.transformation = Transform(t[0], t[1], t[2], t[3], t[4], t[5] + round(ym.lift(bb[1] + t[5])))
        f.info.xHeight = round(xh + gain)
        f.features.text = shift_mark_bases(f.features.text, names, ym)


def shift_mark_bases(text, names, ym):
    """Above-marks on lowercase bases follow the raised x-height."""
    groups = {}
    for gname, members in re.findall(r'(@bGC_[\w.]+)\s*=\s*\[([^\]]*)\];', text):
        groups[gname] = members.split()

    def fix(mt):
        base, x, y = mt.group(1), int(mt.group(2)), int(mt.group(3))
        members = groups.get(base, [base])
        if members and all(n in names for n in members):
            y = round(ym(y))
        return f'pos base {base} <anchor {x} {y}> mark @MC_above;'
    return re.sub(r'pos base (\S+) <anchor (-?\d+) (-?\d+)> mark @MC_above;', fix, text)


OPSZ_MAP = [(8, 8), (12, 9), (20, 20), (60, 60)]


def opsz_design(user):
    for (u0, d0), (u1, d1) in zip(OPSZ_MAP, OPSZ_MAP[1:]):
        if u0 <= user <= u1:
            return d0 + (user - u0) / (u1 - u0) * (d1 - d0)
    raise ValueError(user)


def optical_map(ds_path):
    """Small sizes use the sturdier caption design for longer: 12 px text
    is drawn almost wholly from the caption masters. Named instances keep
    their user sizes (their design location follows the map), so fvar and
    STAT still agree."""
    text = ds_path.read_text()
    old = '<axis tag="opsz" name="optical" minimum="8" maximum="60" default="20"/>'
    maps = ''.join(f'      <map input="{u}" output="{d}"/>\n' for u, d in OPSZ_MAP)
    new = '<axis tag="opsz" name="optical" minimum="8" maximum="60" default="20">\n' + maps + '    </axis>'
    assert old in text
    text = text.replace(old, new)
    head, sep, tail = text.partition('<instances>')
    assert sep

    def fix(mt):
        v = opsz_design(float(mt.group(1)))
        return f'<dimension name="optical" xvalue="{v:g}"/>'
    tail = re.sub(r'<dimension name="optical" xvalue="([\d.]+)"/>', fix, tail)
    ds_path.write_text(head + sep + tail)


# ------------------------------------------------------------------ weight steps

SAMPLE = ['n', 'o', 'h', 'a', 'e', 's', 'r', 't', 'i', 'l', 'd', 'p', 'c', 'u', 'm']


def sample_set(f):
    out = {}
    for n in SAMPLE:
        g = f[n].copy()
        lib.decompose(f, g)
        out[n] = g
    return out


def colour(stops, d, upm):
    """Ink of the lowercase sample at design weight d in em squared (what the
    sample prints at the same size), interpolating the outlines between the
    two masters around d."""
    for (d0, s0), (d1, s1) in zip(stops, stops[1:]):
        if d0 <= d <= d1:
            t = (d - d0) / (d1 - d0)
            break
    else:
        raise ValueError(d)
    area = 0.0
    for n in SAMPLE:
        g = lib.lerp_glyph(s0[n], s1[n], t)
        pen = AreaPen()
        g.draw(pen)
        area += abs(pen.value)
    return area / upm ** 2


# Medium and SemiBold step further in area than the sans: the serif's added
# ink goes into its stems while hairlines stay thin and print light, so an
# equal area step prints about a tenth smaller. With this exponent on the
# sans's ink ratio, 400 -> 600 prints about a third darker, as in the sans.
STEP_GAMMA = {500: 1.12, 600: 1.12}


def align_weights(masters, ds_path):
    """Remap the serif weight axis so each user weight is as dark, relative to
    Strata Sans at the same weight, as Regular is. Darkness is ink colour, not
    stem width: a contrasted serif adds less ink per unit of stem than the
    sans, so matching stems alone leaves its bold weights pale."""
    sans = {m: ufoLib2.Font.open(ds_path.parent.parent / 'sans' / f'StrataSans-{m}.ufo') for m in ('m00', 'm02', 'm04')}
    s_stops = [(100, sample_set(sans['m00'])), (400, sample_set(sans['m02'])), (900, sample_set(sans['m04']))]
    f_stops = [(0, sample_set(masters['m03'])), (394, sample_set(masters['m04'])), (1000, sample_set(masters['m05']))]
    s_upm, f_upm = sans['m02'].info.unitsPerEm, masters['m04'].info.unitsPerEm
    sans_c = lambda w: colour(s_stops, lib.piecewise(w, lib.SANS_WGHT_MAP), s_upm)
    serif_c = lambda d: colour(f_stops, d, f_upm)
    ratio = serif_c(394) / sans_c(400)
    new_map = {200: 0, 400: 394, 900: 1000}
    colours = {}
    for w in (300, 500, 600, 700, 800):
        target = ratio * sans_c(400) * (sans_c(w) / sans_c(400)) ** STEP_GAMMA.get(w, 1.0)
        lo, hi = 0.0, 1000.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if serif_c(mid) < target:
                lo = mid
            else:
                hi = mid
        new_map[w] = round((lo + hi) / 2)
        colours[w] = (round(target, 4), round(serif_c(new_map[w]), 4))
    seq = [new_map[w] for w in sorted(new_map)]
    assert all(a < b for a, b in zip(seq, seq[1:])), new_map
    text = ds_path.read_text()
    old = {int(o): int(i) for i, o in re.findall(r'<map input="(\d+)" output="(\d+)"/>', text)}
    a = text.index('<axis tag="wght"')
    b = text.index('</axis>', a)
    head = text[a:text.index('>', a) + 1]
    body = '\n'.join(f'      <map input="{w}" output="{d}"/>' for w, d in sorted(new_map.items()))
    text = text[:a] + head + '\n' + body + '\n    ' + text[b:]
    # Named instances keep their user weights: move each design location
    # from the old map to the new one.
    def move(m):
        d = int(m.group(1))
        return f'name="weight" xvalue="{new_map[old[d]]}"'
    text = re.sub(r'name="weight" xvalue="(\d+)"', move, text)
    ds_path.write_text(text)
    return {'colour target/serif': colours, 'map': new_map}


# ------------------------------------------------------------------ colour per optical size

# Serif ink at 400 as a share of Strata Sans ink at 400 for the same text at
# the same CSS size, as outline area, per optical size. The serif sets about
# 8% wider than the sans, so equal total ink reads lighter; caption and text
# aim for a density (ink per em of line) near 0.9 of the sans, which keeps
# the hairlines from going spindly at 13-17 px. Display aims higher because
# this design's figures and rounds are light next to the sans's. Figures take
# the same stroke gain as letters.
COLOUR = {8: 0.96, 20: 0.96, 60: 1.00}
# Black's ink relative to Regular, as a share of the text size's. STEP_GAMMA
# steepens the serif's weight steps so that its hairlines, which antialiasing
# fills in at text sizes, still step like the sans; at display sizes the
# screen prints outline area as drawn, so display Black eases back to keep
# the rendered 400->600 step level with the sans there too.
BLACK_AT = {8: 1.0, 20: 1.0, 60: 0.955}
# (thin, regular, black) masters of each serif optical size, and the sans at
# the CSS size that optical size serves: (sans master, share) pairs. Caption
# serves about 10 px, text 20 px, display 60 px (the sans tops out at 32).
GROUPS = {8: ('m00', 'm01', 'm02'), 20: ('m03', 'm04', 'm05'), 60: ('m06', 'm07', 'm08')}
SANS_AT = {8: (('m07', 2 / 3), ('m02', 1 / 3)), 20: (('m02', 2 / 3), ('m03', 1 / 3)), 60: (('m03', 1.0),)}


def colour_masters(masters, sans_folder, lines=None):
    """Thicken or thin the vertical strokes of each serif master so that the
    Regular of every optical size has COLOUR of the sans ink at its size, and
    Thin and Black keep the text size's ink progression (ink relative to
    Regular). Weights then step alike at every size, and align_weights maps
    them onto the sans's steps."""
    need = {m for pairs in SANS_AT.values() for m, _ in pairs}
    sans = {m: ufoLib2.Font.open(Path(sans_folder) / f'StrataSans-{m}.ufo') for m in need}
    s_ink = {m: lib.ink(*lib.sample_glyphs(f, lib.INK_SAMPLE), f.info.unitsPerEm) for m, f in sans.items()}
    samples = {m: lib.sample_glyphs(f, lib.INK_SAMPLE) for m, f in masters.items()}
    upm = masters['m04'].info.unitsPerEm
    old = {m: lib.ink(*samples[m], upm) for m in masters}
    t, r, b = GROUPS[20]
    prog = {'thin': old[t] / old[r], 'black': old[b] / old[r]}
    bold = {}
    for opsz, (tm, rm, bm) in GROUPS.items():
        target = COLOUR[opsz] * sum(s_ink[m] * k for m, k in SANS_AT[opsz])
        bold[rm] = lib.solve_bold(*samples[rm], upm, target)
        bold[tm] = lib.solve_bold(*samples[tm], upm, target * prog['thin'])
        bold[bm] = lib.solve_bold(*samples[bm], upm, target * prog['black'] * BLACK_AT[opsz])
    for m, v in CAPTION_STEM.items():
        bold[m] += v
    blacks = {grp[2]: CAPFIG_BLACK[opsz] for opsz, grp in GROUPS.items()}
    capfig = capfig_names(masters['m04'])
    lines = caption_lines(masters) if lines is None else lines
    for m, f in masters.items():
        for g in f:
            extra = blacks.get(m, 0.0) if g.name in capfig else 0.0
            lib.embolden(g, bold[m] * (SMALL if is_small(g.name) else 1.0) + extra)
    keep_caption_lines(masters, lines, 'after the stroke gain')
    return {m: round(v, 1) for m, v in sorted(bold.items())}


# Short lines in the caption masters (r7). The stroke gain moves each on-curve
# point sideways by its own miter, so a line only a few units long can turn
# far: in the caption Black r, the 8-unit line inside the ball terminal turned
# from 33 degrees to -12, the hairline passes then left it at 10, and the join
# it meets kinked between the caption Black and display Thin locations of the
# built font (r6: 35 degrees, no kink). A line shorter than SHORT_LINE units
# with a corner at one end and a smooth point at the other (the only kind
# whose turn can kink a join between masters) that has turned more than
# SHORT_TURN degrees from its drawn direction has its corner end, with that
# point's own handles, moved sideways back onto the drawn direction at its
# current height, and the smooth end's outer handle turned onto the restored
# line at its own length (without that the smooth join itself kinks: J and
# r at 25-28 degrees). This runs after the stroke gain and again after the
# hairline passes (steep lines only there, as those passes also move points
# up and down). Only the masters that take CAPTION_STEM are checked, so the
# text and display masters keep their r6 outlines.
SHORT_LINE = 40.0
SHORT_TURN = 15.0
CAPTION_LINES = True


def caption_lines(masters):
    """Short lines with one smooth end, per caption master and glyph, before
    the stroke gain: (contour, start, end, dx, dy)."""
    out = {}
    for m in CAPTION_STEM:
        for g in masters[m]:
            got = []
            for ci, c in enumerate(g.contours):
                pts = c.points
                n = len(pts)
                for i, p in enumerate(pts):
                    q = pts[i - 1]
                    if (p.type == 'line' and q.type is not None and bool(p.smooth) != bool(q.smooth)
                            and math.hypot(p.x - q.x, p.y - q.y) < SHORT_LINE):
                        got.append((ci, (i - 1) % n, i, p.x - q.x, p.y - q.y))
            if got:
                out[(m, g.name)] = got
    return out


def keep_caption_lines(masters, lines, when, steep_only=False):
    if not CAPTION_LINES:
        return
    fixed = {}
    for (m, name), got in sorted(lines.items()):
        g = masters[m][name]
        for ci, a, b, dx0, dy0 in got:
            pts = g.contours[ci].points
            n = len(pts)
            pa, pb = pts[a], pts[b]
            dy = pb.y - pa.y
            if steep_only and (abs(dy0) < abs(dx0) or dy * dy0 <= 0):
                continue
            want = dx0 if abs(dy - dy0) < 1e-9 or abs(dy0) < 1e-9 else dx0 * dy / dy0
            turn = abs((math.degrees(math.atan2(pb.x - pa.x, dy) - math.atan2(want, dy)) + 180.0) % 360.0 - 180.0)
            if turn <= SHORT_TURN:
                continue
            if not pa.smooth:
                k, move = a, (pb.x - want) - pa.x
                s, h = pb, pts[(b + 1) % n]
            else:
                k, move = b, (pa.x + want) - pb.x
                s, h = pa, pts[(a - 1) % n]
            for j in ((k - 1) % n, k, (k + 1) % n):
                if j == k or pts[j].type is None:
                    pts[j].x += move
            if h.type is None:
                # the smooth end's outer handle turns onto the restored line,
                # keeping its length, so the join stays tangent
                o = pa if s is pb else pb
                ux, uy = s.x - o.x, s.y - o.y
                d = math.hypot(ux, uy)
                L = math.hypot(h.x - s.x, h.y - s.y)
                if d > 1e-9 and L > 1e-9:
                    h.x, h.y = s.x + L * ux / d, s.y + L * uy / d
            fixed.setdefault(m, []).append(name)
    for m, names in sorted(fixed.items()):
        print(f'serif {m}: short lines kept in direction {when}: {len(names)} ({", ".join(sorted(set(names))[:16])})', flush=True)


# Glyphs the tangent-join pass leaves as they were (r7). That pass judges a
# glyph across all masters at once and keeps it as it was if restoring would
# add a kink between masters. r6 kept the dagger that way; r7's caption
# masters flipped the verdict, and the restore then moved the dagger's handles
# by 0.4-2.0 units in the text and display masters too. Pinning r6's verdict
# keeps those masters byte-identical to r6, as everything outside the caption
# change must stay.
KEEP_DRAWN = {'dagger'}


# Caption stems (r7). Matching the sans's ink left the caption Regular's
# stems 27 units thinner than drawn (77.5 units, 1.4 px at 9 px on a 2x
# screen): on the built font at 9 px the i's stem covered about 1.6 px but
# only one pixel at half ink or more, so the caption size changed nothing
# visible. CAPTION_STEM units more stroke go on every glyph of the opsz 8
# masters after the colour match (Thin in proportion to its stem; Black the
# same units as Regular, so the 400->600 step keeps most of its size and the
# 600 counters lose no more than Regular's). Advances stay, so text at
# 9-13 px does not reflow. Text and display masters are untouched.
CAPTION_STEM = {'m00': 5.0, 'm01': 16.0, 'm02': 16.0}


# Capitals and figures gain CAPFIG_BLACK more units of stroke (per optical
# size) in the Black masters than the lowercase. With one gain for all glyphs,
# a short capital-and-figure sample ("Age 0123") stepped 4.7-7.7 points less
# from 400 to 600 than running text at the same size. The extra gain is
# largest at caption size, where that gap was widest, and smallest at display
# size, where the paragraph step is already at the top of its range.
CAPFIG_BLACK = {8: 38.0, 20: 20.0, 60: 10.0}
FIGNAMES = {'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'}


def capfig_names(f):
    import unicodedata
    out = set()
    for g in f:
        if not g.contours or is_small(g.name) or '.sc' in g.name:
            continue
        base = g.name.split('.')[0]
        cats = {unicodedata.category(chr(u)) for u in g.unicodes}
        if cats & {'Lu', 'Nd'} or base in FIGNAMES or (len(base) == 1 and base.isupper()):
            out.add(g.name)
    return out


# Superior, inferior and fraction forms are drawn about this size of the
# full forms; their stems take the same share of the stroke gain.
SMALL = 0.6
SMALL_TAGS = ('.sups', '.subs', '.sinf', '.numr', '.dnom', 'superior', 'inferior')


def is_small(name):
    return any(t in name for t in SMALL_TAGS)


# ------------------------------------------------------------------ small sizes

# Caption masters (opsz 8, used up to about 13 px): every inner horizontal
# edge (crossbars, the inside of bowl tops and bottoms, serif tops and
# undersides, arms) moves HAIR units into the white beside it, so hairlines
# and crossbars gain 2 x HAIR of thickness; outer edges on the font's zones
# and at each glyph's own top and bottom stay, so heights, overshoots and
# the baseline do not move. Small forms take SMALL of it. The caption
# masters' sidebearings also close by TIGHT_8 units a side. r7 raised HAIR
# from 8 to 11 and THIN_GAIN below by 8 and 4 units with the caption stems,
# so the hairlines keep their share of the heavier stem.
HAIR = 11
TIGHT_8 = 8
LOW = ('m00', 'm01', 'm02')
# An edge is "on a zone" within ZONE_IN units inside it and ZONE_OUT units
# beyond it (overshoot).
ZONE_IN, ZONE_OUT = 6, 22


def _normals(pts, i, sign):
    tin, tout = lib._tangent(pts, i, -1), lib._tangent(pts, i, 1)
    return tin, tout, (tin[1] * sign, -tin[0] * sign), (tout[1] * sign, -tout[0] * sign)


def embolden_y(glyph, d, tops, bots, miter=3.0):
    """Thicken horizontal strokes by moving each inner edge d units along
    the vertical part of its outward (miter) normal; off-curve points move
    with their on-curve point, so smooth joins stay smooth. Edges facing up
    on a top zone (tops, plus the glyph's own top) and edges facing down on
    a bottom zone (bots, plus its own bottom) stay."""
    if not d or not glyph.contours:
        return 0
    area = 0.0
    for c in glyph.contours:
        pts = c.points
        area += sum(pts[i - 1].x * q.y - q.x * pts[i - 1].y for i, q in enumerate(pts))
    sign = 1.0 if area >= 0 else -1.0
    b = lib.bounds(glyph)
    tops = list(tops) + [b[3]]
    bots = list(bots) + [b[1]]
    moved = 0
    for c in glyph.contours:
        pts = c.points
        n = len(pts)
        on = [i for i, q in enumerate(pts) if q.type is not None]
        if n < 2 or not on:
            continue
        dy = {}
        for i in on:
            tin, tout, nin, nout = _normals(pts, i, sign)
            k = min(miter, 1.0 / max(1e-6, 1.0 + lib.dot(tin, tout)))
            v = d * (nin[1] + nout[1]) * k / 1.0
            v = max(-d, min(d, v))
            y = pts[i].y
            if v > 0 and any(z - ZONE_IN <= y <= z + ZONE_OUT for z in tops):
                v = 0.0
            if v < 0 and any(z - ZONE_OUT <= y <= z + ZONE_IN for z in bots):
                v = 0.0
            dy[i] = v
        new = {i: pts[i].y + dy[i] for i in on}
        for idx, i in enumerate(on):
            j = on[(idx + 1) % len(on)]
            run = []
            k = (i + 1) % n
            while k != j:
                run.append(k)
                k = (k + 1) % n
            for r, kk in enumerate(run):
                new[kk] = pts[kk].y + (dy[i] if r < len(run) / 2 else dy[j])
        for i, y in new.items():
            if abs(y - pts[i].y) > 1e-9:
                moved += 1
            pts[i].y = y
        _retangent(pts, on)
    return moved


def _retangent(pts, on, limit=45.0):
    """A smooth join of a line and a curve keeps its tangent: the handle
    turns to the line's new direction, keeping its length."""
    n = len(pts)
    for i in on:
        p = pts[i]
        if not p.smooth:
            continue
        prv, nxt = pts[(i - 1) % n], pts[(i + 1) % n]
        if p.type == 'line' and prv.type is not None and nxt.type is None:
            line, h = (p.x - prv.x, p.y - prv.y), nxt
        elif nxt.type == 'line' and prv.type is None:
            line, h = (p.x - nxt.x, p.y - nxt.y), prv
            line = (-line[0], -line[1])
        else:
            continue
        d = lib.unit(line)
        v = (h.x - p.x, h.y - p.y)
        L = math.hypot(*v)
        if not d or L < 0.5:
            continue
        sgn = 1 if h is nxt else -1
        cosang = sgn * lib.dot(d, v) / L
        if cosang < math.cos(math.radians(limit)):
            continue
        h.x, h.y = p.x + sgn * d[0] * L, p.y + sgn * d[1] * L


def tighten(f, t):
    """Close every spacing glyph's sidebearings by t units a side (marks,
    zero-width glyphs and spaces keep theirs)."""
    cats = f.lib.get('public.openTypeCategories', {})
    still = {g.name for g in f if g.width < 100 or cats.get(g.name) == 'mark' or not (g.contours or g.components)}
    for g in f:
        if g.name in still:
            continue
        for c in g.contours:
            for q in c.points:
                q.x -= t
        for a in g.anchors:
            a.x -= t
        for c in g.components:
            tr = c.transformation
            bd = 0 if c.baseGlyph in still else -t
            c.transformation = Transform(tr[0], tr[1], tr[2], tr[3], tr[4] - t - tr[0] * bd, tr[5] - tr[1] * bd)
        g.width -= 2 * t


def sturdy_small(masters):
    import keys
    out = {}
    names = [g.name for g in masters[LOW[1]] if g.contours]
    for name in names:
        if not all(name in masters[m] for m in LOW):
            continue

        def move(name=name):
            for m in LOW:
                f = masters[m]
                zt = [f.info.xHeight, f.info.capHeight, f.info.ascender]
                zb = [0, f.info.descender]
                d = HAIR * (SMALL if is_small(name) else 1.0)
                out[name] = embolden_y(f[name], d, zt, zb)
        keys.guarded(masters, name, move)
    for m in LOW:
        tighten(masters[m], TIGHT_8)
    return len([n for n, k in out.items() if k])


# Thin strokes at caption size (r6). The horizontal pass above leaves the
# steep thin strokes alone: the light side of v w x y A K k, the thin
# verticals of N and M, the hairline joins. At Regular they measured about
# 0.55 of the n stem on the built font at 9 px and read as broken at 9-13 px.
# Every steep segment (within STEEP of vertical) whose stroke, measured
# across from its middle, is thinner than THIN_HI of the master's n stem
# moves outward in x, so the stroke gains up to THIN_GAIN units; the gain
# fades from full at THIN_LO of a stem to none at THIN_HI. An edge that faces
# less than THIN_WHITE stems of white (a notch, or a small counter such as the
# a's in the heavier masters) stays, so counters keep their room and a thin
# stroke beside one gains on its open side only. Off-curve points
# move with their on-curve point, so smooth joins stay smooth. Only the
# opsz 8 masters change; text and display sizes keep their hairlines.
THIN_GAIN = {'m00': 0.0, 'm01': 26.0, 'm02': 34.0}
THIN_LO, THIN_HI = 0.60, 0.85
STEEP = 0.5
THIN_MIN_LEN = 10.0
THIN_WHITE = 1.5


def _flat_edges(glyph):
    edges = []
    for c in glyph.contours:
        segs = lib.to_segments(c)
        start = segs[-1]['end']
        for sg in segs:
            pts = [start] + sg['ctrl'] + [sg['end']]
            if len(pts) == 4:
                prev = pts[0]
                for i in range(1, 17):
                    q = lib.bez(*pts, i / 16)
                    edges.append((prev, q)); prev = q
            else:
                edges.append((pts[0], pts[-1]))
            start = sg['end']
    return edges


def _winding(edges, p):
    w = 0
    for (x0, y0), (x1, y1) in edges:
        if y0 <= p[1] < y1 or y1 <= p[1] < y0:
            side = (x1 - x0) * (p[1] - y0) - (p[0] - x0) * (y1 - y0)
            if y0 <= p[1] < y1 and side > 0:
                w += 1
            elif y1 <= p[1] < y0 and side < 0:
                w -= 1
    return w


def _ray(edges, o, d):
    """Distance from o along unit d to where the ray leaves the filled
    shape (nonzero winding), so overlapping contours count as one."""
    ts = []
    for (x0, y0), (x1, y1) in edges:
        ex, ey = x1 - x0, y1 - y0
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        wx, wy = x0 - o[0], y0 - o[1]
        t = (wx * ey - wy * ex) / den
        u = (wx * d[1] - wy * d[0]) / den
        if t > 0.5 and -1e-9 <= u <= 1 + 1e-9:
            ts.append(t)
    ts.sort()
    prev = 0.5
    for t in ts + [None]:
        if t is None:
            return prev if prev > 0.5 else None
        if t - prev > 0.25:
            mid = (prev + t) / 2
            if _winding(edges, (o[0] + d[0] * mid, o[1] + d[1] * mid)) == 0:
                return prev
        prev = t
    return None


def _white(edges, o, d):
    """Distance from o along unit d to the next ink (None: open space)."""
    best = None
    for (x0, y0), (x1, y1) in edges:
        ex, ey = x1 - x0, y1 - y0
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        wx, wy = x0 - o[0], y0 - o[1]
        t = (wx * ey - wy * ex) / den
        u = (wx * d[1] - wy * d[0]) / den
        if t > 1.0 and -1e-9 <= u <= 1 + 1e-9 and (best is None or t < best):
            best = t
    return best


def thin_weights(glyph, stem):
    """Per contour, per segment: the share of THIN_GAIN it takes."""
    area = 0.0
    for c in glyph.contours:
        P = c.points
        area += sum(P[i - 1].x * q.y - q.x * P[i - 1].y for i, q in enumerate(P))
    sign = 1.0 if area >= 0 else -1.0
    edges = _flat_edges(glyph)
    out = []
    for c in glyph.contours:
        segs = lib.to_segments(c)
        start = segs[-1]['end']
        ws = []
        for sg in segs:
            pts = [start] + sg['ctrl'] + [sg['end']]
            chord = (pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1])
            L = math.hypot(*chord)
            w = 0.0
            if L >= THIN_MIN_LEN and abs(chord[1]) / L >= STEEP:
                if len(pts) == 4:
                    m, t = lib.bez(*pts, 0.5), lib.unit(lib.bez_tangent(*pts, 0.5))
                else:
                    m, t = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2), lib.unit(chord)
                if t != (0.0, 0.0):
                    inward = (-t[1] * sign, t[0] * sign)
                    # an edge buried inside another contour is not a side
                    outside = (m[0] - inward[0] * 1.5, m[1] - inward[1] * 1.5)
                    d = _ray(edges, m, inward) if _winding(edges, outside) == 0 else None
                    # the white the edge faces: a notch or a small counter
                    # (under THIN_WHITE stems) keeps its edge
                    white = _white(edges, m, (-inward[0], -inward[1])) if d is not None else None
                    if d is not None and (white is None or white >= THIN_WHITE * stem):
                        r = d / stem
                        w = max(0.0, min(1.0, (THIN_HI - r) / (THIN_HI - THIN_LO)))
            ws.append(w)
            start = sg['end']
        out.append(ws)
    return out


def thicken_thin(glyph, gain, weights):
    """Move the on-curve ends of weighted segments outward in x (see
    THIN_GAIN); off-curve points follow their on-curve point."""
    if not gain:
        return 0
    area = 0.0
    for c in glyph.contours:
        P = c.points
        area += sum(P[i - 1].x * q.y - q.x * P[i - 1].y for i, q in enumerate(P))
    sign = 1.0 if area >= 0 else -1.0
    h = gain / 2.0
    moved = 0
    for c, ws in zip(glyph.contours, weights):
        pts = c.points
        n = len(pts)
        on = [i for i, q in enumerate(pts) if q.type is not None]
        if n < 2 or not on or not any(ws):
            continue
        # segment k of to_segments ends at the k-th on-curve point after the
        # first one, so on-curve point on[j] ends segment j-1 and starts j
        dx = {}
        for idx, i in enumerate(on):
            w_in, w_out = ws[(idx - 1) % len(on)], ws[idx % len(on)]
            if not (w_in or w_out):
                dx[i] = 0.0
                continue
            tin, tout = lib._tangent(pts, i, -1), lib._tangent(pts, i, 1)
            nin = (tin[1] * sign, -tin[0] * sign)
            nout = (tout[1] * sign, -tout[0] * sign)
            if w_in and w_out:
                k = min(3.0, 1.0 / max(1e-6, 1.0 + lib.dot(tin, tout)))
            else:
                k = 1.0
            dx[i] = h * (w_in * nin[0] + w_out * nout[0]) * k
        new = {i: pts[i].x + dx[i] for i in on}
        for idx, i in enumerate(on):
            j = on[(idx + 1) % len(on)]
            run = []
            kk = (i + 1) % n
            while kk != j:
                run.append(kk)
                kk = (kk + 1) % n
            for r, q in enumerate(run):
                new[q] = pts[q].x + (dx[i] if r < len(run) / 2 else dx[j])
        for i, x in new.items():
            if abs(x - pts[i].x) > 1e-9:
                moved += 1
            pts[i].x = x
    return moved


def thin_small(masters):
    """Thicken the steep thin strokes of the opsz 8 masters (THIN_GAIN)."""
    import keys
    stems = {m: lib.stem_width(masters[m]['n'], masters[m].info.xHeight * 0.45) for m in LOW}
    done = []
    for name in [g.name for g in masters[LOW[1]] if g.contours]:
        if not all(name in masters[m] for m in LOW):
            continue
        plan = {m: thin_weights(masters[m][name], stems[m]) for m in LOW}
        if not any(any(ws) for m in LOW for ws in plan[m]):
            continue

        def move(name=name):
            for m in LOW:
                g = masters[m][name]
                thicken_thin(g, THIN_GAIN[m] * (SMALL if is_small(name) else 1.0), plan[m])
        if keys.guarded(masters, name, move):
            done.append(name)
    return done


# ------------------------------------------------------------------ point clusters

# The stroke gain and the vertical remap shorten some pieces of the
# upstream's overlapping serif construction (slab ends buried in a stem,
# steps where a slab meets a bracket) to a unit or two, so pairs of points
# sit almost on top of each other. `spread_short` lengthens every line
# piece shorter than SHORT_EM to SPREAD_TO of it by sliding one of its ends
# along its other segment's own direction (a line keeps its line; a curve
# end moves with its handle), and keeps a move only if the glyph's filled
# shape changes by less than SPREAD_AREA square units (an exact boolean
# comparison), no neighbouring piece becomes short and no join turns into a
# kink. Points are only moved, never added or removed, so the masters stay
# compatible; a piece that cannot be lengthened without a visible change
# stays as it is.
SHORT_EM = 12 / 2048
SPREAD_TO = 1.3
SPREAD_AREA = 1.0
KINK_MIN, KINK_MAX, SMOOTH_TOL = 3.0, 25.0, 2.0


def _fill(contours):
    import pathops
    path = pathops.Path()
    pen = path.getPen()
    for c in contours:
        c.draw(pen)
    return pathops.simplify(path, fix_winding=True, keep_starting_points=False)


def _changed_area(before, contours):
    import pathops
    return pathops.op(before, _fill(contours), pathops.PathOp.XOR).area


def _turn_ok(pts, i):
    """No kink at on-curve point i, by the outline check's rule."""
    n = len(pts)
    p = pts[i]

    def nb(step):
        k = i
        for _ in range(n):
            k = (k + step) % n
            if math.hypot(pts[k].x - p.x, pts[k].y - p.y) > 0.5:
                return pts[k]
        return None
    a, b = nb(-1), nb(1)
    if a is None or b is None:
        return True
    tin, tout = lib.unit((p.x - a.x, p.y - a.y)), lib.unit((b.x - p.x, b.y - p.y))
    ang = math.degrees(math.acos(max(-1.0, min(1.0, lib.dot(tin, tout)))))
    if p.smooth:
        return ang <= SMOOTH_TOL
    curve = pts[(i - 1) % n].type is None or pts[(i + 1) % n].type is None
    return not (curve and KINK_MIN < ang < KINK_MAX)


def _short_pieces(c, lim):
    pts = c.points
    on = [k for k, q in enumerate(pts) if q.type is not None]
    out = []
    for j, k in enumerate(on):
        l = on[(j + 1) % len(on)]
        if pts[l].type == 'line' and math.hypot(pts[l].x - pts[k].x, pts[l].y - pts[k].y) < lim:
            out.append((k, l, on[j - 1], on[(j + 2) % len(on)]))
    return out


def _spread_one(glyph, ci, k, l, o, r, lim, target, before):
    """Try the moves that lengthen piece k->l of contour ci; keep the first
    that leaves the filled shape, the neighbouring pieces and the joins clean."""
    c = glyph.contours[ci]
    pts = c.points
    n = len(pts)
    kinks_before = {i: _turn_ok(pts, i) for i in (o, k, l, r)}
    for end, other, far, handle in ((l, k, r, (l + 1) % n), (k, l, o, (k - 1) % n)):
        e, q = pts[end], pts[other]
        ref = pts[handle] if pts[handle].type is None else pts[far]
        d = lib.unit((e.x - ref.x, e.y - ref.y))
        if not d:
            continue
        w = (e.x - q.x, e.y - q.y)
        bq = lib.dot(d, w)
        disc = bq * bq - lib.dot(w, w) + target * target
        if disc < 0:
            continue
        for lam in sorted((-bq + math.sqrt(disc), -bq - math.sqrt(disc)), key=abs):
            chord = math.hypot(pts[far].x - e.x, pts[far].y - e.y)
            if abs(lam) > 0.25 * chord:
                continue
            moved = [end] + ([handle] if pts[handle].type is None else [])
            old = [(pts[i].x, pts[i].y) for i in moved]
            for i in moved:
                pts[i].x += lam * d[0]
                pts[i].y += lam * d[1]
            good = math.hypot(pts[far].x - pts[end].x, pts[far].y - pts[end].y) >= lim
            good = good and all(_turn_ok(pts, i) or not kinks_before[i] for i in (o, k, l, r))
            good = good and _changed_area(before, glyph.contours) < SPREAD_AREA
            if good:
                return True
            for i, (x, y) in zip(moved, old):
                pts[i].x, pts[i].y = x, y
    return False


def spread_short(masters):
    """Lengthen short line pieces where that changes no filled shape;
    returns (short pieces before, after) over all masters."""
    before_n = after_n = 0
    for f in masters.values():
        lim = SHORT_EM * f.info.unitsPerEm
        target = SPREAD_TO * lim
        for g in f:
            if not g.contours:
                continue
            todo = [(ci, piece) for ci, c in enumerate(g.contours) for piece in _short_pieces(c, lim)]
            before_n += len(todo)
            if not todo:
                continue
            fill = _fill(g.contours)
            for ci, (k, l, o, r) in todo:
                if len({k, l, o, r}) == 4:
                    _spread_one(g, ci, k, l, o, r, lim, target, fill)
            after_n += sum(len(_short_pieces(c, lim)) for c in g.contours)
    return before_n, after_n


# Quadratic splits (r8). The build converts the nine masters' cubic curves to
# quadratic ones together: each curve segment takes the fewest quadratic
# pieces that keep every master within the compiler's tolerance (SPLIT_ERR of
# the em), and each master's compiled points then follow from its own cubic
# and that count. So a change to the caption masters alone can move the
# compiled points of the default and display masters, whose sources did not
# change. r7's caption gain changed the count on 199 curve segments in 135
# glyphs (82 up, 117 down), and the default instance of 64 core glyphs took
# new points. keep_splits holds every segment at the count of r6's masters:
# the reference masters are built again with r6's caption settings
# (R6_CAPTION; text and display masters are the same either way) and
# counted with the compiler's own routine (split_counts). Where the caption
# masters now give another count, the segment's handles in one caption
# master change length along their own directions, so every join stays
# tangent, by the smallest travel (SPLIT_STEP steps up to SPLIT_MAX units)
# that restores r6's count: shorter or longer handles make a curve need
# fewer or more quadratic pieces. A change is kept only if the glyph gains
# no interpolation kink and no other segment's count moves; handles never
# shrink below SPLIT_KEEP of their length or grow past 1 / SPLIT_KEEP. Only
# the caption masters move, and the change in shape stays under a unit or
# two on curves several hundred units long.
SPLIT_ERR = 0.001
SPLIT_STEP = 0.1
SPLIT_MAX = 40.0
SPLIT_KEEP = 0.6
CAPTION = ('m00', 'm01', 'm02')
R6_CAPTION = dict(CAPTION_STEM={'m00': 0.0, 'm01': 0.0, 'm02': 0.0}, HAIR=8,
                  THIN_GAIN={'m00': 0.0, 'm01': 18.0, 'm02': 30.0}, CAPTION_LINES=False)


class caption_profile:
    """Run the caption passes with other settings (R6_CAPTION), then restore."""

    def __init__(self, values):
        self.values = values

    def __enter__(self):
        g = globals()
        self.old = {k: g[k] for k in self.values}
        g.update(self.values)

    def __exit__(self, *exc):
        globals().update(self.old)


def _converted(font, name):
    """name as the compiler converts it: a glyph with contours and components
    is decomposed first (its own contours, then the components')."""
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    g = font[name]
    if not (g.components and len(g.contours)):
        return g
    out = Glyph(name)
    rp = DecomposingRecordingPen(font)
    g.draw(rp)
    rp.replay(out.getPen())
    return out


def _split_needs(masters, name, order):
    from fontTools.cu2qu import curves_to_quadratic
    from fontTools.cu2qu.ufo import _get_segments
    gs = [_converted(masters[m], name) for m in order]
    if not len(gs[0]):
        return None
    errs = [SPLIT_ERR * masters[m].info.unitsPerEm for m in order]
    segs = list(zip(*[_get_segments(g) for g in gs]))
    return [len(curves_to_quadratic([s[1] for s in seg], errs, True)[0]) - 2 if seg[0][0] == 'curve' else 0
            for seg in segs]


def split_counts(masters):
    """{glyph: [quadratic pieces per segment, 0 for a non-curve]} for the
    glyphs every master draws."""
    order = sorted(masters)
    out = {}
    for name in sorted(masters[order[0]].keys()):
        if all(name in masters[m] for m in order):
            got = _split_needs(masters, name, order)
            if got is not None:
                out[name] = got
    return out


def _segment_points(g):
    """For each entry the compiler's segment list holds for g's own contours,
    the curve's point indices (contour, p0, p1, p2, p3), else None."""
    out = []
    for ci, c in enumerate(g.contours):
        pts = c.points
        assert pts[0].type != 'move', f'{g.name}: open contour'
        first = next(i for i, p in enumerate(pts) if p.type is not None)
        order = list(range(first + 1, len(pts))) + list(range(first + 1))
        out.append(None)
        prev, offs = first, []
        for i in order:
            if pts[i].type is None:
                offs.append(i)
                continue
            out.append((ci, prev, offs[0], offs[1], i) if pts[i].type == 'curve' else None)
            prev, offs = i, []
        out.append(None)
    return out


def _need(curve, err):
    from fontTools.cu2qu import curve_to_quadratic
    return len(curve_to_quadratic(curve, err, True)) - 2


def _pin(c, idx, want, err, up):
    """Handle travel that gives this caption curve `want` pieces: fewer or
    equal when up (it needs more), exactly `want` when down; None if none."""
    pts = c.points
    _, a, h1, h2, b = idx
    p0, p1, p2, p3 = pts[a], pts[h1], pts[h2], pts[b]
    l1, l2 = math.hypot(p1.x - p0.x, p1.y - p0.y), math.hypot(p2.x - p3.x, p2.y - p3.y)
    u1 = ((p1.x - p0.x) / l1, (p1.y - p0.y) / l1) if l1 > 1.0 else None
    u2 = ((p2.x - p3.x) / l2, (p2.y - p3.y) / l2) if l2 > 1.0 else None
    dirs = [(s1, s2) for s1, s2 in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
            if (s1 == 0 or u1) and (s2 == 0 or u2)]
    t = SPLIT_STEP
    while t <= SPLIT_MAX + 1e-9:
        for s1, s2 in dirs:
            n1 = l1 + s1 * t if s1 else l1
            n2 = l2 + s2 * t if s2 else l2
            if (s1 and not SPLIT_KEEP * l1 <= n1 <= l1 / SPLIT_KEEP) or (s2 and not SPLIT_KEEP * l2 <= n2 <= l2 / SPLIT_KEEP):
                continue
            q1 = (p0.x + u1[0] * n1, p0.y + u1[1] * n1) if s1 else (p1.x, p1.y)
            q2 = (p3.x + u2[0] * n2, p3.y + u2[1] * n2) if s2 else (p2.x, p2.y)
            got = _need(((p0.x, p0.y), q1, q2, (p3.x, p3.y)), err)
            if (got <= want) if up else (got == want):
                yield t, (h1, q1), (h2, q2)
        t = round(t + SPLIT_STEP, 6)


def keep_splits(masters, ref):
    """Hold every curve segment at the quadratic count `ref` gives (r6's
    masters). Returns ((glyphs, segments) pinned, glyphs left, travel)."""
    order = sorted(masters)
    err = SPLIT_ERR * masters[order[0]].info.unitsPerEm
    now = split_counts(masters)
    pinned, left, travel = [], [], []

    def handles(m, name, idx):
        p = masters[m][name].contours[idx[0]].points
        return [(p[j].x, p[j].y) for j in (idx[2], idx[3])]

    def put(m, name, idx, q):
        p = masters[m][name].contours[idx[0]].points
        (p[idx[2]].x, p[idx[2]].y), (p[idx[3]].x, p[idx[3]].y) = q

    for name in sorted(now):
        if name not in ref or now[name] == ref[name]:
            continue
        assert len(now[name]) == len(ref[name]), f'{name}: segments changed'
        k0 = identity.kinks(masters, name)
        seg = _segment_points(masters[CAPTION[0]][name])
        for i, (n, want) in enumerate(zip(now[name], ref[name])):
            if n == want:
                continue
            idx = seg[i] if i < len(seg) else None
            if idx is None:
                continue
            up = n > want
            curve = {m: tuple((pt.x, pt.y) for pt in (masters[m][name].contours[idx[0]].points[j] for j in idx[1:]))
                     for m in CAPTION}
            # too many pieces: every caption master that needs more than r6's
            # count gives some up; too few: the one caption master that reaches
            # r6's count with the least travel takes it
            groups = [[m for m in CAPTION if _need(curve[m], err) > want]] if up else [[m] for m in CAPTION]
            best = None
            for group in groups:
                saved = {m: handles(m, name, idx) for m in group}
                found = []
                for m in group:
                    hit = None
                    for t, (_, q1), (_, q2) in _pin(masters[m][name].contours[idx[0]], idx, want, err, up):
                        put(m, name, idx, (q1, q2))
                        # the count is the most any master needs, so with
                        # several masters to bring down it is read after the last
                        last = not up or m == group[-1]
                        if not last or _split_needs(masters, name, order)[i] == want:
                            kk = identity.kinks(masters, name)
                            if kk[0] <= k0[0] and kk[1] <= k0[1]:
                                hit = (t, (q1, q2))
                                break
                        put(m, name, idx, saved[m])
                    if hit is None:
                        break
                    found.append((m, hit))
                ok = len(found) == len(group) and _split_needs(masters, name, order)[i] == want
                if ok and (best is None or max(h[0] for _, h in found) < best[0]):
                    best = (max(h[0] for _, h in found), found)
                for m in group:
                    put(m, name, idx, saved[m])
            if best is None:
                continue
            for m, (_, q) in best[1]:
                put(m, name, idx, q)
            travel.append((round(best[0], 2), name, i, '+'.join(m for m, _ in best[1])))
            pinned.append((name, i))
    # read again at the end: a glyph that holds components as well as
    # contours takes its components' pieces once their own glyphs are pinned
    final = split_counts(masters)
    left = sorted(n for n in ref if final.get(n) != ref[n])
    glyphs = sorted({n for n, _ in pinned})
    return (len(glyphs), len(pinned)), left, sorted(travel, reverse=True)


def run(masters, folder):
    for f in masters.values():
        scale_font(f, S)
    for f in masters.values():
        add_glyphs(f)
    lowercase_proportions(masters)
    identity.rounds(masters, alpha=ROUNDS, ref_name='m04')
    lines = caption_lines(masters)
    print('serif stroke gain per master', colour_masters(masters, folder.parent / 'sans', lines))
    print('serif caption hairlines thickened in', sturdy_small(masters), 'glyphs', flush=True)
    print('serif caption thin strokes thickened in', len(thin_small(masters)), 'glyphs', flush=True)
    keep_caption_lines(masters, lines, 'after the hairline passes', steep_only=True)
    asc, desc = lib.set_metrics(list(masters.values()), 1000)
    for f in masters.values():
        f.features.text = set_os2(set_hhea(f.features.text, asc, desc), f.info)
    info = align_weights(masters, folder / 'StrataSerif.designspace')
    print('serif weights', info)
    optical_map(folder / 'StrataSerif.designspace')


# ------------------------------------------------------------------ r11

# r11 item 3: the question mark's hook. Upstream, the inside of the hook is
# a straight line from the terminal's underside (point 9) that runs into the
# bowl stroke and back (points 10 and 11, a spike buried in the stroke), so
# the hook swells to the terminal's full height across the top and then
# drops to the thin right side at a corner, with three points clustered at
# the turn. The two line points go, and one curve runs from the terminal's
# underside to the inside of the right side (point 14, vertical tangent):
# it leaves the terminal at Q_TANGENT degrees above horizontal (the same in
# every master, so instances keep the smooth join), and its handles are
# fitted, per master, so the stroke thins evenly along the hook from the
# terminal's thickness to the right side's (each sample's nearest distance
# to the outer arc against a straight line in arc length). Handles stay
# between Q_HANDLE of the span, so no point cluster comes back. The
# terminal's own incoming handle turns to the new tangent (its length kept).
# `questiondown` (via `questiondown.cap`) and the double marks are
# components of `question`, so they follow.
Q_TANGENT = 15.0
Q_HANDLE = (0.25, 0.75)
Q_STEPS = 50
Q_GLYPHS = ('question', 'questiondown.cap', 'questiondown', 'questiondbl', 'questionexclam', 'exclamquestion')


def _bez(p0, p1, p2, p3, t):
    mt = 1 - t
    return (mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
            mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1])


def _seg_dist(p, poly):
    best = 1e9
    for a, b in zip(poly, poly[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
        best = min(best, math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy))
    return best


def _hook_fit(P):
    """Handles (p1, p2) of the hook's inner curve from P[9] to P[14]."""
    p0, p3 = P[9], P[14]
    arc = [_bez(P[0], P[1], P[2], P[3], i / 32) for i in range(33)]
    t0, t3 = _seg_dist(p0, arc), _seg_dist(p3, arc)
    u = (math.cos(math.radians(Q_TANGENT)), math.sin(math.radians(Q_TANGENT)))
    span = math.hypot(p3[0] - p0[0], p3[1] - p0[1])
    lo, hi = Q_HANDLE
    best = None
    for ia in range(Q_STEPS + 1):
        a = span * (lo + (hi - lo) * ia / Q_STEPS)
        p1 = (p0[0] + a * u[0], p0[1] + a * u[1])
        for ib in range(Q_STEPS + 1):
            b = span * (lo + (hi - lo) * ib / Q_STEPS)
            p2 = (p3[0], p3[1] + b)
            pts = [_bez(p0, p1, p2, p3, i / 20) for i in range(21)]
            L = [0.0]
            for q0, q1 in zip(pts, pts[1:]):
                L.append(L[-1] + math.hypot(q1[0] - q0[0], q1[1] - q0[1]))
            err = sum((_seg_dist(q, arc) - (t0 + (t3 - t0) * l / L[-1])) ** 2 for q, l in zip(pts, L))
            if best is None or err < best[0]:
                best = (err, p1, p2)
    return best[1], best[2], math.sqrt(best[0] / 21)


def question_hook(masters):
    """Redraw the hook's inside (see above) in every master."""
    out = {}
    for m, f in masters.items():
        g = f['question']
        assert not g.components and len(g.contours) == 2, 'question changed'
        c = g.contours[1]
        pts = c.points
        assert len(pts) == 34 and pts[9].type == 'curve' and pts[9].smooth, 'question hook changed'
        assert pts[10].type == 'line' and pts[11].type == 'line', 'question hook changed'
        assert pts[12].type is None and pts[13].type is None and pts[14].type == 'curve', 'question hook changed'
        assert abs(pts[13].x - pts[14].x) < 0.5 and pts[13].y > pts[14].y, 'question hook: right side not vertical'
        P = [(p.x, p.y) for p in pts]
        p1, p2, rms = _hook_fit(P)
        u = (math.cos(math.radians(Q_TANGENT)), math.sin(math.radians(Q_TANGENT)))
        L8 = math.hypot(P[9][0] - P[8][0], P[9][1] - P[8][1])
        pts[8].x, pts[8].y = P[9][0] - L8 * u[0], P[9][1] - L8 * u[1]
        pts[12].x, pts[12].y = p1
        pts[13].x, pts[13].y = p2
        keep = [p for i, p in enumerate(pts) if i not in (10, 11)]
        c.points[:] = keep
        out[m] = round(rms, 1)
    return out


# r11 item 2: caption spacing at 9-12 px. The serif's opsz 8 masters serve
# 8-12 px (the axis maps 12 px to design 9), and with only text masters at
# design 20 above them a spacing change there would show at 80% at 13 px.
# So glyph-only fade layers sit between them: each is the exact
# interpolation of its caption and text masters' glyphs at its size
# (outlines, anchors, advances), made before any spacing change and kept as
# a layer of the caption master. The compiler reads a layer source for its
# glyphs only, so kerning and mark positions still interpolate between the
# masters' own features.fea as in r10. The caption masters' spacing then
# opens, all on the right sidebearing (`caption_open`; the outlines do not
# move, so the features' anchors stay valid). r11 had one layer, at 13 px
# with no opening, so the opening fell linearly in design opsz from the
# caption master to 13 px: 0.895 of the caption opening at 9 px, 0.789 at
# 10, 0.684 at 11, 0.579 at 12 and 0 at 13. The axis maps 12-13 px across
# 1.375 design units against 0.25 for each px below 12, so most of that
# fall came between 12 and 13 px, and 12 px text set wider than 13 px text.
#
# r12 gives each fade layer an opening of its own (FADE_STEPS: user px and
# the opening there, in units per glyph; the last step is 0). The opening is
# then piecewise linear in design opsz between the caption master and the
# steps, and 0 from the last step up. The caption master's own opening
# (CAPTION_TOTAL, all on the right sidebearing) is solved so that 9 px keeps
# r11's opening (O9_R11), and with it every 9 px advance. FADE_STEPS was set
# on rendered PNGs and HarfBuzz widths (see DESIGN-NOTES.md): a step at
# 12 px of 11 units and r11's own 13 px layer (no opening, so from 13 px up
# the font is r11's to the unit). With the 9 px opening fixed, the line from
# the caption master to 12 px gives 80 units at 10 px (the smallest opening
# that keeps every pair of the gap strings 2 device px apart at 10 px is 78;
# r11 kept 2 units over its measured floor too) and 45.5 at 11 px, about
# half of r11's 87.6; every test string gets wider, and no wider per px,
# with each whole px from 9 to 13. A step at 10 px would let 10 px close
# further but costs a third layer set (about 40 KB of WOFF2).
FADE_STEPS = ((12, 11), (13, 0))
FADE_MASTERS = {'m09': ('m00', 'm03'), 'm10': ('m01', 'm04'), 'm11': ('m02', 'm05')}
O9_R11 = 128 * (1 - (opsz_design(9) - 8) / (opsz_design(13) - 8))


def fade_layer(px):
    return f'fade.{px:g}'


def caption_total(steps=None):
    """The caption master's opening (units per glyph) that keeps r11's
    opening at 9 px, given the first fade step."""
    px1, o1 = (FADE_STEPS if steps is None else steps)[0]
    s = (opsz_design(9) - 8) / (opsz_design(px1) - 8)
    assert 0 < s < 1, 'the first fade step must lie above 9 px'
    return round((O9_R11 - o1 * s) / (1 - s))


CAPTION_TOTAL = caption_total()


def _lerp(a, b, t):
    return a + (b - a) * t


# The word spaces (U+0020, U+00A0) open with the letters, so a word space
# keeps its share of the line, and the figure and punctuation spaces (U+2007,
# U+2008) keep their relation to the figures and the period; the em-based
# spaces keep their widths.
OPEN_SPACES = (0x20, 0xA0, 0x2007, 0x2008)


def opened(f):
    """The glyphs of caption master `f` whose spacing opens: every glyph
    except marks, glyphs under 100 units wide and empty glyphs, plus the
    OPEN_SPACES."""
    spaces = [g for g in f if any(u in OPEN_SPACES for u in g.unicodes)]
    covered = {u for g in spaces for u in g.unicodes if u in OPEN_SPACES}
    assert covered == set(OPEN_SPACES) and not any(g.contours or g.components for g in spaces), 'spaces changed'
    cats = f.lib.get('public.openTypeCategories', {})
    names = {g.name for g in f if not (g.width < 100 or cats.get(g.name) == 'mark' or not (g.contours or g.components))}
    return names | {g.name for g in spaces}


def fade_masters(masters, ds_path, steps=None):
    """The fade layers: for each step (px, opening), each caption master's
    glyphs (outlines, components, anchors, advances) interpolated exactly
    with its text master at that size's design location, made before the
    caption spacing opens, with the step's opening added to the advance of
    every glyph `opened` selects; written as the layer fade_layer(px) of the
    caption master. They are sparse (glyph-only) sources: the compiler takes
    their outlines and advances and no features, so kerning and mark
    positions keep interpolating between the caption and text masters' own
    features.fea, exactly as in r10. Returns ({(fade name, px): layer},
    [(px, design opsz)])."""
    steps = FADE_STEPS if steps is None else steps
    out, at = {}, []
    for px, units in steps:
        t = (opsz_design(px) - 8) / (20 - 8)
        for name, (ma, mb) in FADE_MASTERS.items():
            A, B = masters[ma], masters[mb]
            lname = fade_layer(px)
            assert lname not in A.layers, 'fade layer already present'
            wide = opened(A)
            layer = A.layers.newLayer(lname)
            for gname in A.keys():
                ga, gb = A[gname], B[gname]
                g = ga.copy()
                assert [len(c) for c in ga.contours] == [len(c) for c in gb.contours], gname
                assert [c.baseGlyph for c in ga.components] == [c.baseGlyph for c in gb.components], gname
                assert [x.name for x in ga.anchors] == [x.name for x in gb.anchors], gname
                for c, ca, cb in zip(g.contours, ga.contours, gb.contours):
                    for p, pa, pb in zip(c.points, ca.points, cb.points):
                        assert pa.type == pb.type, gname
                        p.x, p.y = _lerp(pa.x, pb.x, t), _lerp(pa.y, pb.y, t)
                for c, ca, cb in zip(g.components, ga.components, gb.components):
                    c.transformation = tuple(_lerp(x, y, t) for x, y in zip(ca.transformation, cb.transformation))
                for x, xa, xb in zip(g.anchors, ga.anchors, gb.anchors):
                    x.x, x.y = _lerp(xa.x, xb.x, t), _lerp(xa.y, xb.y, t)
                g.width = _lerp(ga.width, gb.width, t) + (units if gname in wide else 0)
                g.height = _lerp(ga.height, gb.height, t)
                layer.insertGlyph(g, gname, overwrite=False, copy=False)
            out[(name, px)] = layer
        at.append((px, round(opsz_design(px), 4)))
    return out, at


def add_fade_sources(ds_path, at):
    """Add the fade layers to the designspace as layer sources of their
    caption masters (weight from the caption master, optical at each step's
    design location)."""
    from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor
    ds = DesignSpaceDocument.fromfile(ds_path)
    by = {Path(s.filename).stem.split('-')[-1]: s for s in ds.sources}
    assert not any(s.layerName for s in ds.sources), 'fade sources already present'
    for px, design_opsz in at:
        for name, (ma, _) in FADE_MASTERS.items():
            src = by[ma]
            s = SourceDescriptor()
            s.filename = src.filename
            s.layerName = fade_layer(px)
            s.name = f'fade {px:g} {name}'
            s.familyName = src.familyName
            s.location = dict(src.location, optical=design_opsz)
            ds.addSource(s)
    ds.write(ds_path)


def caption_open(masters, total=None):
    """Open the caption masters' spacing by `total` (CAPTION_TOTAL) units
    per glyph, all of it on the right sidebearing, for every glyph `opened`
    selects. Outlines, anchors and components stay where they are, so each
    master's own mark and kern features (features.fea, written in glyph
    coordinates) stay valid."""
    total = CAPTION_TOTAL if total is None else total
    for m in LOW:
        f = masters[m]
        wide = opened(f)
        for g in f:
            if g.name in wide:
                g.width += total
    return total
