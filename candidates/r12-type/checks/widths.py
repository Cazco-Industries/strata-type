"""Regular/Rounded width table: the same strings shaped with default features
in Strata Sans and Strata Sans Rounded, at several weights and optical sizes.

    .venv/bin/python -I candidates/r12-type/checks/widths.py build/r12-type [--all]

Prints, per string, the total advance in each face and the difference in
percent. Exit 1 if any difference exceeds 1%.
"""
import sys
from pathlib import Path
import uharfbuzz as hb

STRINGS = ['72°', '−3°', '104°F', '18:30', '80%', '30.16', '0123456789', '12:05', '−12°C',
           '3 PM', '12 mph NNW', '30.16 inHg', 'Thu', '½ ¼ ¾', '72℉ 22℃', 'Rain, 40%.']
LOCS = [(14, 400), (32, 400), (14, 100), (14, 700), (14, 900), (32, 900), (20, 500),
        (8, 100), (8, 400), (8, 900)]


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {})
    return sum(p.x_advance for p in buf.glyph_positions)


def main(build, show_all):
    faces = {}
    for name in ('StrataSans', 'StrataSansRounded'):
        path = Path(build) / f'{name}.ttf'
        faces[name] = hb.Face(hb.Blob.from_file_path(str(path)))
    worst = 0.0
    rows = []
    for opsz, wght in LOCS:
        fonts = {}
        for n, face in faces.items():
            f = hb.Font(face)
            f.set_variations({'opsz': opsz, 'wght': wght})
            fonts[n] = f
        for s in STRINGS:
            a = shape(fonts['StrataSans'], s)
            b = shape(fonts['StrataSansRounded'], s)
            d = (b - a) / a * 100
            worst = max(worst, abs(d))
            rows.append((opsz, wght, s, a, b, d))
    print(f'{"opsz":>4} {"wght":>4}  {"string":<11} {"Regular":>8} {"Rounded":>8} {"diff %":>7}')
    for opsz, wght, s, a, b, d in rows:
        if show_all or (opsz, wght) == (14, 400) or abs(d) > 1:
            print(f'{opsz:>4} {wght:>4}  {s:<11} {a:>8} {b:>8} {d:>+7.2f}')
    print(f'largest difference over {len(LOCS)} locations x {len(STRINGS)} strings: {worst:.2f}%')
    return 0 if worst <= 1 else 1


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sys.exit(main(args[0] if args else 'build/r12-type', '--all' in sys.argv))
