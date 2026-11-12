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
import lib

S = 1.09
SANS_BASE = Path(__file__).resolve().parents[2] / 'baseline' / 'fonts' / 'sans'
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
    """Ink area per em squared of the lowercase sample at design weight d,
    interpolating the outlines between the two masters around d."""
    for (d0, s0), (d1, s1) in zip(stops, stops[1:]):
        if d0 <= d <= d1:
            t = (d - d0) / (d1 - d0)
            break
    else:
        raise ValueError(d)
    area = adv = 0.0
    for n in SAMPLE:
        g = lib.lerp_glyph(s0[n], s1[n], t)
        pen = AreaPen()
        g.draw(pen)
        area += abs(pen.value)
        adv += s0[n].width + t * (s1[n].width - s0[n].width)
    return area / (adv * upm)


def align_weights(masters, ds_path):
    """Remap the serif weight axis so each user weight is as dark, relative to
    Strata Sans at the same weight, as Regular is. Darkness is ink colour, not
    stem width: a contrasted serif adds less ink per unit of stem than the
    sans, so matching stems alone leaves its bold weights pale."""
    sans = {m: ufoLib2.Font.open(SANS_BASE / f'StrataSans-{m}.ufo') for m in ('m00', 'm02', 'm04')}
    s_stops = [(100, sample_set(sans['m00'])), (400, sample_set(sans['m02'])), (900, sample_set(sans['m04']))]
    f_stops = [(0, sample_set(masters['m03'])), (394, sample_set(masters['m04'])), (1000, sample_set(masters['m05']))]
    s_upm, f_upm = sans['m02'].info.unitsPerEm, masters['m04'].info.unitsPerEm
    sans_c = lambda w: colour(s_stops, lib.piecewise(w, lib.SANS_WGHT_MAP), s_upm)
    serif_c = lambda d: colour(f_stops, d, f_upm)
    ratio = serif_c(394) / sans_c(400)
    new_map = {200: 0, 400: 394, 900: 1000}
    colours = {}
    for w in (300, 500, 600, 700, 800):
        target = ratio * sans_c(w)
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


def run(masters, folder):
    for f in masters.values():
        scale_font(f, S)
    for f in masters.values():
        add_glyphs(f)
    asc, desc = lib.set_metrics(list(masters.values()), 1000)
    for f in masters.values():
        f.features.text = set_os2(set_hhea(f.features.text, asc, desc), f.info)
    info = align_weights(masters, folder / 'StrataSerif.designspace')
    print('serif weights', info)
