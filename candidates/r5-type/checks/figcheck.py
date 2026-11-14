"""Regression check: default figures (no features requested) share one advance.

Usage (from the repository root):
    .venv/bin/python -I candidates/r5-type/checks/figcheck.py build/r5-type

Shapes "0123456789" with no feature overrides, so the font's
default figures are what is measured, at every named instance and at every
combination of axis extremes and defaults. Also checks that `pnum` gives
varied advances (not asked of the mono) and `tnum` keeps the default
advances.

Confusable shapes: `1 l I |`, `rn m`, `0 O` and `3 7` are rendered with default
features at 9, 11 and 13 px (Regular weight; the optical size follows the
pixel size), each string's ink centred on the same baseline, greyscale and
unhinted. The pairwise pixel xor is sum |a - b| / sum max(a, b): 0 for
identical images, 1 for no shared ink. Every pair must reach XOR_MIN in
every face at every size. Exit 1 on failure.
"""
import itertools
import sys
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont

FACES = ['StrataSans', 'StrataSerif', 'StrataMono', 'StrataSansRounded']
PAIRS = [('1', 'l'), ('1', 'I'), ('l', 'I'), ('I', '|'), ('l', '|'), ('1', '|'), ('rn', 'm'), ('0', 'O'), ('3', '7')]
SIZES = (9, 11, 13)
# The upstream sans's l against I is about 0.05 (same shape); a distinct
# form (tail, serif, foot) moves a pair well past this.
XOR_MIN = 0.20


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


def confusables(build):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import raster
    ok = True
    print(f'confusable xor (fail under {XOR_MIN:.2f}), default features, wght 400:')
    print(f'{"face":<18} {"px":>3}  ' + '  '.join(f'{a + "/" + b:>6}' for a, b in PAIRS))
    table = {}
    for face in FACES:
        path = Path(build) / f'{face}.ttf'
        if not path.exists():
            continue
        f = raster.Face(path)
        have = {chr(c) for c, _ in f.ft.get_chars()}
        for size in SIZES:
            loc = f.location(size, 400)
            row = []
            for a, b in PAIRS:
                if not (set(a + b) <= have):
                    row.append(None)
                    ok = False
                    continue
                W, H = size * 4, size * 3
                v = raster.xor(f.text(a, size, loc, centre=(W, H)), f.text(b, size, loc, centre=(W, H)))
                row.append(v)
                ok &= v >= XOR_MIN
            table[(face, size)] = row
            print(f'{face:<18} {size:>3}  ' + '  '.join(
                '   n/a' if v is None else f'{v:>5.3f}{"!" if v < XOR_MIN else " "}' for v in row))
    print('confusable check:', 'PASS' if ok else 'FAIL')
    return ok


def main(build):
    ok = confusables(build)
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
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'build/r5-type'))
