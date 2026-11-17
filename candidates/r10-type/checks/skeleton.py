"""Skeleton check: Rounded must be the Regular sans skeleton, only rounded.

    .venv/bin/python -I candidates/r10-type/checks/skeleton.py build/r10-type [--all]

Every glyph Rounded draws is rendered from the built Strata Sans Rounded
and the same glyph (same character, or the same name when unencoded) from
the built Strata Sans, at the same pen origin, 256 px per em, unhinted, at
text size (opsz 14) Regular and Black, and thresholded at half coverage.

Each face's ink is dilated by a disc of REACH em. Ink of one face that lies
outside the other face's dilated ink is displaced ink. A round pen of a
fraction of a stem leaves only small separate crumbs of displaced ink, one
at each corner it rounds; a changed construction (a figure drawn to another
shape, a bowl or stroke moved, a corner rounded with a radius of several
stems) leaves one large connected region. The gate is the area of the
largest 4-connected region of displaced ink, in both directions, in
thousandths of an em squared: it must stay under BLOB_MAX at both
locations for every glyph. 4.0 is the area of a square 0.063 em on a side
(about two thirds of a Regular stem). Exit 1 on failure.

Two reference columns are printed and not gated: the two-way dilation
overlap (the smaller of the shares of each face's ink lying within REACH of
the other's), and the intersection over union of both masks after a BLUR em
blur. On small marks (quotes, accents, the hyphen) round ends alone take a
large share of the area, so neither share separates rounding from redrawing.
"""
import sys
from pathlib import Path

import freetype
from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raster  # noqa: E402

PPEM = 256
REACH = 0.012
BLOB_MAX = 4.0
BLUR = 0.025
LOCS = [(14, 400), (14, 900)]
# Rounded builds that drew ':' and '-' from the sans case forms under the
# plain names are compared with those forms.
CASE_NAMES = {'colon': 'colon.case', 'hyphen': 'hyphen.case'}
R = REACH * PPEM
DISC = [(dx, dy) for dx in range(-int(R), int(R) + 1) for dy in range(-int(R), int(R) + 1)
        if dx * dx + dy * dy <= R * R]


def grey(face, gid, loc, w, h, base):
    face._set(PPEM, loc)
    img = Image.new('L', (w, h), 0)
    face.draw(img, [(gid, 0.0, 0.0)], PPEM, loc, PPEM * 0.25, base)
    return img


def binary(img):
    return img.point(lambda v: 255 if v >= 128 else 0)


def count(img):
    return img.histogram()[255]


def dilate(img):
    """Binary dilation by a disc of radius REACH em (shifted copies, OR)."""
    bb = img.getbbox()
    if not bb:
        return img
    m = int(R) + 1
    box = (max(0, bb[0] - m), max(0, bb[1] - m), min(img.width, bb[2] + m), min(img.height, bb[3] + m))
    crop = img.crop(box)
    out = Image.new('L', crop.size, 0)
    for dx, dy in DISC:
        out = ImageChops.lighter(out, ImageChops.offset(crop, dx, dy))
    full = Image.new('L', img.size, 0)
    full.paste(out, box[:2])
    return full


def largest(img):
    """Pixels in the largest 4-connected region of a 0/255 image."""
    bb = img.getbbox()
    if not bb:
        return 0
    img = img.crop(bb)
    w, h = img.size
    data = img.tobytes()
    seen = bytearray(w * h)
    best = 0
    for i in range(w * h):
        if data[i] and not seen[i]:
            stack, n = [i], 0
            seen[i] = 1
            while stack:
                j = stack.pop()
                n += 1
                x = j % w
                for k in (j - 1 if x else -1, j + 1 if x < w - 1 else -1, j - w, j + w):
                    if 0 <= k < w * h and data[k] and not seen[k]:
                        seen[k] = 1
                        stack.append(k)
            best = max(best, n)
    return best


def inside(a, b_dilated):
    n = count(a)
    return count(ImageChops.darker(a, b_dilated)) / n if n else 1.0


def iou(a, b):
    a = binary(a.filter(ImageFilter.GaussianBlur(BLUR * PPEM)))
    b = binary(b.filter(ImageFilter.GaussianBlur(BLUR * PPEM)))
    u = count(ImageChops.lighter(a, b))
    return count(ImageChops.darker(a, b)) / u if u else 1.0


def glyph_names(face):
    names = []
    for i in range(face.ft.num_glyphs):
        try:
            nm = face.ft.get_glyph_name(i).decode()
        except (freetype.FT_Exception, ValueError):
            break
        names.append(nm)
    return names


def main(build, show_all):
    sans = raster.Face(Path(build) / 'StrataSans.ttf')
    rnd = raster.Face(Path(build) / 'StrataSansRounded.ttf')
    names = glyph_names(rnd)
    has_case = 'colon.case' in names
    # encoded glyphs are matched by character (the sans may use production names)
    by_gid = {gid: cp for cp, gid in rnd.ft.get_chars()}
    w, h = int(PPEM * 2.2), int(PPEM * 1.6)
    base = int(PPEM * 1.15)
    rows, missing = [], []
    for nm in names:
        if nm == '.notdef' or not nm:
            continue
        src = nm if has_case else CASE_NAMES.get(nm, nm)
        gr = rnd.ft.get_name_index(nm.encode())
        cp = by_gid.get(gr)
        if cp is not None and src == nm:
            gs = sans.ft.get_char_index(cp)
        else:
            gs = sans.ft.get_name_index(src.encode())
        if not gs:
            missing.append(nm)
            continue
        blobs, cov, ious = [], [], []
        for opsz, wght in LOCS:
            ls, lr = sans.location(opsz, wght), rnd.location(opsz, wght)
            ls['opsz'] = lr['opsz'] = opsz
            ga, gb = grey(sans, gs, ls, w, h, base), grey(rnd, gr, lr, w, h, base)
            a, b = binary(ga), binary(gb)
            if not count(ImageChops.lighter(a, b)):
                blobs.append(None)
                cov.append(None)
                ious.append(None)
                continue
            da, db = dilate(a), dilate(b)
            off = max(largest(ImageChops.subtract(a, db)), largest(ImageChops.subtract(b, da)))
            blobs.append(off / (PPEM * PPEM) * 1000)
            cov.append(min(inside(a, db), inside(b, da)))
            ious.append(iou(ga, gb))
        if any(v is not None for v in blobs):
            rows.append((nm, blobs, cov, ious))
    fails = [r for r in rows if any(v is not None and v >= BLOB_MAX for v in r[1])]
    print(f'skeleton overlap, Rounded vs Regular: largest displaced region beyond {REACH} em, '
          f'1/1000 em^2 (fail at {BLOB_MAX} or more); two-way overlap within {REACH} em and '
          f'blurred IoU ({BLUR} em) for reference')
    print(f'{"glyph":<22} {"region 400":>10} {"region 900":>10} {"overlap 400":>11} {"overlap 900":>11} {"IoU 400":>8} {"IoU 900":>8}')

    def hi(r):
        return max(v for v in r[1] if v is not None)
    worst = sorted(rows, key=hi, reverse=True)
    for nm, blobs, cov, ious in (rows if show_all else worst[:12]):
        f = lambda v, n, d=3: ' ' * (n - 3) + 'n/a' if v is None else f'{v:{n}.{d}f}'
        flag = '  FAIL' if any(v is not None and v >= BLOB_MAX for v in blobs) else ''
        print(f'{nm:<22} {f(blobs[0], 10, 2)} {f(blobs[1], 10, 2)} {f(cov[0], 11)} {f(cov[1], 11)} '
              f'{f(ious[0], 8)} {f(ious[1], 8)}{flag}')
    if rows:
        b4 = [r[1][0] for r in rows if r[1][0] is not None]
        b9 = [r[1][1] for r in rows if r[1][1] is not None]
        c4 = [r[2][0] for r in rows if r[2][0] is not None]
        print(f'{len(rows)} glyphs; largest region {max(b4):.2f} (400) / {max(b9):.2f} (900), '
              f'mean {sum(b4) / len(b4):.2f} (400); overlap minimum {min(c4):.3f} (400)')
    for nm in missing:
        print('no sans glyph for', nm)
    ok = not fails and not missing
    print(f'skeleton check: {len(fails)} glyph(s) at or over {BLOB_MAX}:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sys.exit(main(args[0] if args else 'build/r10-type', '--all' in sys.argv))
