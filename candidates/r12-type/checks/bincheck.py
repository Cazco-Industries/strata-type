"""Round 12 binary checks on build/<cand> against build/<ref> (default r12-type, r11-type).
- Sans, Rounded, Mono (TTF and WOFF2): file sha256 and every table's bytes equal the reference.
- Serif: table set, and which tables differ (expected: gvar, HVAR and tables that carry region lists).
- Serif default-instance advances (hmtx) equal the reference.
- Mono: default shaping of the operator string gives one glyph per character; shaped
  72℉–75℉ 20℃/h equals typed 72°F–75°F 20°C/h (glyphs and positions, wght 300-700,
  default, ligatures off and opt-in).
usage: .venv/bin/python -I candidates/r12-type/checks/bincheck.py [CAND] [REF]   (small step: fontTools + HarfBuzz)"""
import hashlib, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from pathlib import Path
B = str(Path(__file__).resolve().parents[3] / 'build')
cand = sys.argv[1] if len(sys.argv) > 1 else 'r12-type'
ref = sys.argv[2] if len(sys.argv) > 2 else 'r11-type'
FEATS = {'default': {}, 'off': {'calt': False, 'liga': False}, 'optin': {'calt': True, 'liga': True, 'dlig': True, 'ss11': True}}
ok = True


def check(label, cond, detail=''):
    global ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + label + (f'  {detail}' if detail else ''))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def tables(p):
    t = TTFont(p)
    return {tag: t.reader[tag] for tag in t.reader.keys()}  # raw (decompressed) table bytes


for face in ('StrataSans', 'StrataSansRounded', 'StrataMono'):
    for ext in ('ttf', 'woff2'):
        a, b = f'{B}/{ref}/{face}.{ext}', f'{B}/{cand}/{face}.{ext}'
        ta, tb = tables(a), tables(b)
        diff = sorted(k for k in ta.keys() | tb.keys() if ta.get(k) != tb.get(k))
        check(f'{face}.{ext} identical to {ref}', sha(a) == sha(b) and not diff, f'sha256 equal {sha(a) == sha(b)}, {len(ta)} tables, differing {diff}')
for ext in ('ttf', 'woff2'):
    a, b = f'{B}/{ref}/StrataSerif.{ext}', f'{B}/{cand}/StrataSerif.{ext}'
    ta, tb = tables(a), tables(b)
    diff = sorted(k for k in ta.keys() | tb.keys() if ta.get(k) != tb.get(k))
    print(f'INFO StrataSerif.{ext} tables differing from {ref}: {diff} (same table set: {set(ta) == set(tb)})')
s_new, s_ref = TTFont(f'{B}/{cand}/StrataSerif.ttf'), TTFont(f'{B}/{ref}/StrataSerif.ttf')
check('serif glyph order equal', s_new.getGlyphOrder() == s_ref.getGlyphOrder())
dif = [g for g in s_ref.getGlyphOrder() if s_ref['hmtx'][g] != s_new['hmtx'][g]]
check(f'serif default-instance hmtx equal to {ref}', not dif, str(dif[:8]))


def shape(path, text, feats, var=None):
    face = hb.Face(hb.Blob.from_file_path(path)); f = hb.Font(face)
    if var: f.set_variations(var)
    b = hb.Buffer(); b.add_str(text); b.guess_segment_properties(); hb.shape(f, b, feats)
    return [f.glyph_to_string(i.codepoint) for i in b.glyph_infos], [(p.x_advance, p.x_offset, p.y_offset) for p in b.glyph_positions]


mono = f'{B}/{cand}/StrataMono.ttf'
A, Bs = '72℉–75℉ 20℃/h', '72°F–75°F 20°C/h'
for fk, fv in FEATS.items():
    bad = [w for w in (300, 400, 500, 600, 700) if shape(mono, A, fv, {'wght': w}) != shape(mono, Bs, fv, {'wght': w})]
    check(f'mono shaping parity {fk} (wght 300-700): glyphs and positions equal', not bad, ' '.join(shape(mono, A, fv)[0]) if not bad else f'differs at {bad}')
ops = 'a === b !== c => d <= e >= f != g -> h'
n, _ = shape(mono, ops, {})
check('mono default shaping: one glyph per character', len(n) == len(ops), f'{len(n)} glyphs / {len(ops)} chars')
print('ALL PASS' if ok else 'SOME FAIL')
sys.exit(0 if ok else 1)
