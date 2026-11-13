"""Regression check: default figures (no features requested) share one advance.

Usage (from the repository root):
    .venv/bin/python -I candidates/r2-type/checks/figcheck.py build/r2-type

Shapes "0123456789" with no feature overrides, so the font's
default figures are what is measured, at every named instance and at every
combination of axis extremes and defaults. Also checks that `pnum` gives
varied advances (not asked of the mono) and `tnum` keeps the default
advances. Exit 1 on failure.
"""
import itertools
import sys
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont

FACES = ['StrataSans', 'StrataSerif', 'StrataMono', 'StrataSansRounded']


def advances(font, features):
    buf = hb.Buffer()
    buf.add_str('0123456789')
    buf.guess_segment_properties()
    hb.shape(font, buf, features)
    return [p.x_advance for p in buf.glyph_positions]


def locations(tt):
    if 'fvar' not in tt:
        return [{}]
    axes = tt['fvar'].axes
    locs = [dict(inst.coordinates) for inst in tt['fvar'].instances]
    for combo in itertools.product(*[(a.minValue, a.defaultValue, a.maxValue) for a in axes]):
        locs.append({a.axisTag: v for a, v in zip(axes, combo)})
    seen, out = set(), []
    for loc in locs:
        key = tuple(sorted(loc.items()))
        if key not in seen:
            seen.add(key)
            out.append(loc)
    return out


def main(build):
    ok = True
    for face in FACES:
        path = Path(build) / f'{face}.ttf'
        if not path.exists():
            continue
        tt = TTFont(path)
        hbface = hb.Face(hb.Blob.from_file_path(str(path)))
        bad, prop_flat, tnum_diff, sample = [], [], [], None
        locs = locations(tt)
        for loc in locs:
            font = hb.Font(hbface)
            if loc:
                font.set_variations(loc)
            d = advances(font, {})
            t = advances(font, {'tnum': True})
            p = advances(font, {'pnum': True})
            if len(set(d)) != 1:
                bad.append((loc, d))
            if t != d:
                tnum_diff.append((loc, d, t))
            if face != 'StrataMono' and len(set(p)) == 1:
                prop_flat.append(loc)
            if sample is None:
                sample = (d, p)
        status = 'PASS' if not (bad or tnum_diff or prop_flat) else 'FAIL'
        ok &= status == 'PASS'
        print(f'{face}: {status}  locations={len(locs)}  default={sample[0][0]} (all ten equal: {not bad})  '
              f'tnum==default: {not tnum_diff}  '
              f'pnum varied: {"n/a (monospaced)" if face == "StrataMono" else not prop_flat}  pnum@default={sample[1]}')
        for loc, d in bad[:3]:
            print('   unequal default advances at', loc, d)
        for loc, d, t in tnum_diff[:3]:
            print('   tnum differs from default at', loc, d, t)
    print('figure-default check:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'build/r2-type'))
