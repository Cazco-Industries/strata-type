"""Outline drift against the incumbent: every glyph whose outline differs
from r6, per face and master in the sources and per table in the built
fonts, checked against the changes this candidate intends (INTENDED).

Sources: each master's glyph records (contour points with their types and
smooth flags, components, advance, Unicode values, anchors) are compared
exactly, coordinates as numbers. Glyphs added or removed count as changes.

Built fonts (TTF and WOFF2): per glyph, the default instance's glyf entry
(coordinates, contour ends, on-curve flags, components), its hmtx entry,
and every gvar tuple, keyed by its region, so a change in one region does
not hide behind another. Each changed tuple is labelled with the masters
its region peaks at. cmap, GSUB, GPOS, fvar, avar, STAT, HVAR and the name
records are compared whole.

INTENDED lists, per face, the masters whose glyphs may change and which
glyphs (None = any glyph in that master), and per built font the glyphs and
gvar regions allowed to change. The check fails when anything changes
outside it, and lists what changed inside it.

Usage (repository root):
    .venv/bin/python -I candidates/r8-type/checks/drift.py [CAND] [--ref r6-type] [--json PATH] [--list PATH]

--list writes every changed glyph name, per face and master and per built
font, table and gvar region, as plain text.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[3]
FACES = {'sans': 'StrataSans', 'sans-rounded': 'StrataSansRounded', 'serif': 'StrataSerif', 'mono': 'StrataMono'}
TEMP = ('uni2103', 'uni2109')

# The serif's small optical size (opsz 8, masters m00-m02) takes r7's
# caption weight, so any glyph there may change; the mono's degree-letter
# signs are redrawn in both masters. Nothing else moves. In the built
# serif, only gvar regions that peak at opsz 8 may change (the default
# instance and the text and display regions keep r6's numbers).
INTENDED = {
    'sources': {
        'serif': {'m00': None, 'm01': None, 'm02': None},
        'mono': {'m00': set(TEMP), 'm01': set(TEMP)},
    },
    'binaries': {
        'StrataSerif': {'glyf': set(), 'hmtx': set(), 'gvar_regions': 'caption'},
        'StrataMono': {'glyf': set(TEMP), 'hmtx': set(TEMP), 'gvar_regions': 'any', 'gvar': set(TEMP)},
    },
}
NUM = {'x', 'y', 'xScale', 'xyScale', 'yxScale', 'yScale', 'xOffset', 'yOffset', 'width', 'height'}
WHOLE = ('cmap', 'GSUB', 'GPOS', 'GDEF', 'fvar', 'avar', 'STAT', 'HVAR', 'MVAR', 'name', 'OS/2', 'hhea', 'post', 'maxp')


def _node(el):
    attrs = tuple(sorted((k, float(v) if k in NUM else v) for k, v in el.attrib.items()))
    return (el.tag, attrs, tuple(_node(c) for c in el))


def _records(ufo):
    out = {}
    for path in sorted((ufo / 'glyphs').glob('*.glif')):
        root = ET.parse(path).getroot()
        outline = root.find('outline')
        out[root.get('name')] = (_node(outline) if outline is not None else None,
                                 tuple(_node(el) for el in root if el.tag in {'advance', 'unicode', 'anchor'}))
    return out


def sources(cand, ref):
    report, bad = {}, []
    for face, prefix in FACES.items():
        a_dir, b_dir = ROOT / 'candidates' / ref / 'fonts' / face, ROOT / 'candidates' / cand / 'fonts' / face
        masters = sorted(p.name[len(prefix) + 1:-4] for p in a_dir.glob(f'{prefix}-m*.ufo'))
        if sorted(p.name[len(prefix) + 1:-4] for p in b_dir.glob(f'{prefix}-m*.ufo')) != masters:
            bad.append(f'{face}: master set differs')
        face_rep = {}
        for m in masters:
            a, b = _records(a_dir / f'{prefix}-{m}.ufo'), _records(b_dir / f'{prefix}-{m}.ufo')
            changed = sorted(n for n in a.keys() | b.keys() if a.get(n) != b.get(n))
            allowed = INTENDED['sources'].get(face, {})
            ok_names = allowed.get(m, set()) if m in allowed else set()
            outside = [n for n in changed if not (m in allowed and (ok_names is None or n in ok_names))]
            face_rep[m] = {'glyphs': len(b), 'changed': len(changed), 'outside_intended': outside,
                           'unchanged': len(b) - len(changed),
                           'changed_names': changed if len(changed) <= 40 else changed[:40] + ['...'],
                           'changed_all': changed}
            if outside:
                bad.append(f'{face} {m}: {len(outside)} unintended ({", ".join(outside[:12])})')
        # non-glyph source files (features, info, designspace)
        other = []
        for p in sorted(a_dir.rglob('*')):
            rel = p.relative_to(a_dir)
            if p.is_dir() or rel.parts[1:2] == ('glyphs',) or p.name == '.DS_Store':
                continue
            q = b_dir / rel
            if not q.exists() or q.read_bytes() != p.read_bytes():
                other.append(str(rel))
        face_rep['other_files_differing'] = other
        report[face] = face_rep
    return report, bad


def _glyf_record(font, name):
    g = font['glyf'][name]
    if g.isComposite():
        return ('composite', tuple((c.glyphName, c.x, c.y, tuple(map(tuple, c.transform)) if hasattr(c, 'transform') else None)
                                   for c in g.components))
    if g.numberOfContours == 0:
        return ('empty',)
    coords, ends, flags = g.getCoordinates(font['glyf'])
    return ('simple', tuple(map(tuple, coords)), tuple(ends), tuple(f & 1 for f in flags))


def _peak_label(axes, tags):
    return ','.join(f'{t}={axes[t][1]:+.3f}' for t in tags if t in axes)


def binaries(cand, ref):
    report, bad = {}, []
    for prefix in FACES.values():
        for ext in ('ttf', 'woff2'):
            pa, pb = ROOT / 'build' / ref / f'{prefix}.{ext}', ROOT / 'build' / cand / f'{prefix}.{ext}'
            if not pa.exists() or not pb.exists():
                bad.append(f'{prefix}.{ext}: missing')
                continue
            a, b = TTFont(pa, lazy=False), TTFont(pb, lazy=False)
            rep = {}
            if a.getGlyphOrder() != b.getGlyphOrder():
                bad.append(f'{prefix}.{ext}: glyph order differs')
            names = [n for n in b.getGlyphOrder() if n in set(a.getGlyphOrder())]
            glyf = sorted(n for n in names if _glyf_record(a, n) != _glyf_record(b, n))
            hmtx = sorted(n for n in names if a['hmtx'][n] != b['hmtx'][n])
            tags = [ax.axisTag for ax in b['fvar'].axes] if 'fvar' in b else []
            gvar, regions = [], {}
            if 'gvar' in b:
                for n in names:
                    va = {tuple(sorted(v.axes.items())): v.coordinates for v in a['gvar'].variations.get(n, [])}
                    vb = {tuple(sorted(v.axes.items())): v.coordinates for v in b['gvar'].variations.get(n, [])}
                    diff = [k for k in va.keys() | vb.keys() if va.get(k) != vb.get(k)]
                    if diff:
                        gvar.append(n)
                        for k in diff:
                            lab = _peak_label(dict(k), tags)
                            regions.setdefault(lab, set()).add(n)
            whole = [t for t in WHOLE if (t in a) != (t in b) or (t in a and a.getTableData(t) != b.getTableData(t))]
            want = INTENDED['binaries'].get(prefix, {'glyf': set(), 'hmtx': set(), 'gvar_regions': 'none'})
            out_glyf = [n for n in glyf if n not in want['glyf']]
            out_hmtx = [n for n in hmtx if n not in want['hmtx']]
            mode = want.get('gvar_regions', 'none')
            out_gvar = []
            for lab, ns in regions.items():
                peaks = dict(p.split('=') for p in lab.split(',')) if lab else {}
                caption = float(peaks.get('opsz', '0')) < 0
                for n in ns:
                    if mode == 'none' or (mode == 'caption' and not caption) or (mode == 'any' and n not in want.get('gvar', set())):
                        out_gvar.append((n, lab))
            out_whole = [t for t in whole if t not in want.get('tables', set())]
            rep = {'glyphs': len(names), 'glyf_changed': glyf, 'hmtx_changed': hmtx,
                   'gvar_changed_glyphs': len(gvar),
                   'gvar_regions_changed': {lab: len(ns) for lab, ns in sorted(regions.items())},
                   'gvar_region_glyphs': {lab: sorted(ns) for lab, ns in sorted(regions.items())},
                   'tables_changed': whole,
                   'outside_intended': {'glyf': out_glyf, 'hmtx': out_hmtx, 'gvar': sorted(out_gvar)[:40],
                                        'gvar_count': len(out_gvar), 'tables': out_whole}}
            for kind, lst in (('glyf', out_glyf), ('hmtx', out_hmtx), ('gvar', out_gvar), ('tables', out_whole)):
                if lst:
                    bad.append(f'{prefix}.{ext} {kind}: {len(lst)} unintended ({", ".join(map(str, sorted(lst)[:8]))})')
            report[f'{prefix}.{ext}'] = rep
    return report, bad


def main(argv):
    cand, ref, out = 'r8-type', 'r6-type', None
    args = list(argv)
    if '--ref' in args:
        i = args.index('--ref'); ref = args[i + 1]; del args[i:i + 2]
    listing = None
    if '--list' in args:
        i = args.index('--list'); listing = Path(args[i + 1]); del args[i:i + 2]
    if '--json' in args:
        i = args.index('--json'); out = Path(args[i + 1]); del args[i:i + 2]
    if args:
        cand = args[0]
    src, bad_s = sources(cand, ref)
    binr, bad_b = binaries(cand, ref)
    result = {'candidate': cand, 'reference': ref, 'status': 'FAIL' if bad_s or bad_b else 'PASS',
              'problems': bad_s + bad_b, 'sources': src, 'binaries': binr}
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=1, default=sorted) + '\n')
    if listing:
        listing.parent.mkdir(parents=True, exist_ok=True)
        lines = [f'Glyphs whose outlines differ from {ref}: {cand}, status {result["status"]}', '']
        for face, rep in src.items():
            for m, r in rep.items():
                if m == 'other_files_differing':
                    lines.append(f'{face} other source files differing: {len(r)}' + (f' ({", ".join(r)})' if r else ''))
                    continue
                lines.append(f'{face} {m} sources: {r["changed"]} of {r["glyphs"]}' + (': ' + ' '.join(r['changed_all']) if r['changed'] else ''))
            lines.append('')
        for font, r in binr.items():
            lines.append(f'{font} default glyf: {len(r["glyf_changed"])}' + (': ' + ' '.join(r['glyf_changed']) if r['glyf_changed'] else ''))
            lines.append(f'{font} hmtx: {len(r["hmtx_changed"])}' + (': ' + ' '.join(r['hmtx_changed']) if r['hmtx_changed'] else ''))
            for lab, ns in r['gvar_region_glyphs'].items():
                lines.append(f'{font} gvar region {lab}: {len(ns)}: ' + ' '.join(ns))
            if not r['gvar_region_glyphs']:
                lines.append(f'{font} gvar: 0')
            lines.append(f'{font} whole tables differing: ' + (', '.join(r['tables_changed']) or 'none'))
            lines.append('')
        listing.write_text('\n'.join(lines) + '\n')
    print(f'drift {cand} vs {ref}: {result["status"]}')
    for face, rep in src.items():
        for m, r in rep.items():
            if m == 'other_files_differing':
                if r:
                    print(f'  {face}: other source files differing: {", ".join(r)}')
                continue
            if r['changed']:
                print(f'  {face} {m}: {r["changed"]}/{r["glyphs"]} glyphs differ'
                      + (f' ({", ".join(r["changed_names"])})' if r['changed'] <= 12 else '')
                      + (f'; outside intended: {r["outside_intended"][:12]}' if r['outside_intended'] else ''))
            else:
                print(f'  {face} {m}: identical ({r["glyphs"]} glyphs)')
    for font, r in binr.items():
        print(f'  {font}: glyf {len(r["glyf_changed"])} {r["glyf_changed"][:8]}, hmtx {len(r["hmtx_changed"])} {r["hmtx_changed"][:8]}, '
              f'gvar glyphs {r["gvar_changed_glyphs"]}, regions {r["gvar_regions_changed"]}, tables {r["tables_changed"]}')
    for p in result['problems']:
        print('  PROBLEM', p)
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
