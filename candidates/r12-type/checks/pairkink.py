"""The gate's interpolation test on one pair of serif locations, in several
builds: outlines drawn from each variable font at the two user locations
(as checks/vfkinks.py does), compared with fontTools' interpolatable test.
Small step (fontTools glyph sets only).
usage: .venv/bin/python -I candidates/r12-type/checks/pairkink.py 'wght=900,opsz=12' 'wght=200,opsz=13' KEY=font.ttf ..."""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.interpolatable import test as interpolation_test

KINDS = ('kink', 'contour_order', 'wrong_start_point', 'underweight', 'overweight')
locs = [{k: float(v) for k, v in (p.split('=') for p in a.split(','))} for a in sys.argv[1:3]]
for spec in sys.argv[3:]:
    key, path = spec.split('=', 1)
    font = TTFont(path)
    gss = [font.getGlyphSet(location=loc, normalized=False) for loc in locs]
    names = [sys.argv[1], sys.argv[2]]
    res = interpolation_test(gss, names=names)
    found = sorted((g, p['type'], p.get('contour'), p.get('value')) for g, ps in res.items() for p in ps if p['type'] in KINDS)
    print(f'{key}: {len(found)} finding(s) between {names[0]} and {names[1]}')
    for g, t, c, v in found:
        print(f'  {g:<16} {t:<12} contour {c} value {v}')
