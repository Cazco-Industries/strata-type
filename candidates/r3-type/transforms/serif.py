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
# ascenders (b d f h k l) lowered by ASC_CUT units: a serif headline set at
# line-height 1.13 at 48 px keeps about 3.9 px between a descender and the
# next line's ascender (5.6 px with the earlier 0.23 cut read as loose).
DEPTH_CUT = 0.10
ASC_CUT = 20
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
        ym = YMap(xh, asc, gain, depth, DEPTH_CUT * depth, ASC_CUT)
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


def colour_masters(masters, sans_folder):
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
    blacks = {grp[2]: CAPFIG_BLACK[opsz] for opsz, grp in GROUPS.items()}
    capfig = capfig_names(masters['m04'])
    for m, f in masters.items():
        for g in f:
            extra = blacks.get(m, 0.0) if g.name in capfig else 0.0
            lib.embolden(g, bold[m] * (SMALL if is_small(g.name) else 1.0) + extra)
    return {m: round(v, 1) for m, v in sorted(bold.items())}


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


def run(masters, folder):
    for f in masters.values():
        scale_font(f, S)
    for f in masters.values():
        add_glyphs(f)
    lowercase_proportions(masters)
    identity.rounds(masters, alpha=ROUNDS, ref_name='m04')
    print('serif stroke gain per master', colour_masters(masters, folder.parent / 'sans'))
    asc, desc = lib.set_metrics(list(masters.values()), 1000)
    for f in masters.values():
        f.features.text = set_os2(set_hhea(f.features.text, asc, desc), f.info)
    info = align_weights(masters, folder / 'StrataSerif.designspace')
    print('serif weights', info)
    optical_map(folder / 'StrataSerif.designspace')
