"""Interpolation test on the built variable fonts, the way the gate's font
checker runs it: the default location first, then every gvar location in
sorted order, compared at the default em of 1000 units (more sensitive than
these fonts' own 2048).

    .venv/bin/python -I candidates/r9-type/checks/vfkinks.py build/r9-type

Prints each face's findings (kinks, contour order, start points, under- and
overweight contours). Exit 1 if Strata Sans Rounded has any; the other faces
are reported, since the serif carries upstream findings.
"""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.interpolatable import test as interpolation_test
from fontTools.varLib.models import piecewiseLinearMap

FACES = ('StrataSans', 'StrataSerif', 'StrataMono', 'StrataSansRounded')
KINDS = ('kink', 'contour_order', 'wrong_start_point', 'underweight', 'overweight')


def findings(path):
    font = TTFont(path)
    locs = set()
    for variations in font['gvar'].variations.values():
        for var in variations:
            locs.add(tuple((tag, val[1]) for tag, val in sorted(var.axes.items())))
    locations = [{}] + [dict(loc) for loc in sorted(locs, key=lambda v: (len(v), v))]
    maps = {a.axisTag: {-1: a.minValue, 0: a.defaultValue, 1: a.maxValue} for a in font['fvar'].axes}
    glyphsets = [font.getGlyphSet(location=loc, normalized=True) for loc in locations]
    names = [','.join(f"{a.axisTag}={int(piecewiseLinearMap(gs.location.get(a.axisTag, 0), maps[a.axisTag]))}"
                      for a in font['fvar'].axes) for gs in glyphsets]
    results = interpolation_test(glyphsets, names=names)
    return [(glyph, p['type'], p.get('master_1'), p.get('master_2'))
            for glyph, problems in results.items() for p in problems if p['type'] in KINDS]


def main():
    build = Path(sys.argv[1] if len(sys.argv) > 1 else 'build/r9-type')
    bad = False
    for face in FACES:
        found = findings(build / f'{face}.ttf')
        print(f'{face}: {len(found)} finding(s)')
        for glyph, kind, a, b in sorted(found):
            print(f'  {glyph:<16} {kind:<18} {a}  ->  {b}')
        if face == 'StrataSansRounded' and found:
            bad = True
    print('interpolation test (Rounded must be clear):', 'FAIL' if bad else 'PASS')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
