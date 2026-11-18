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

Since r11 it also takes masters added to a face (`added_masters`) and
layers added to a master (`added_layers`; either must hold the same glyph
set as the master), glyphs appended to or
retired from the glyph order (`appended`; maxp must move by the same count),
and a per-font `advance` list: the glyphs whose default-instance advance may
change (an empty set means no advance in the font may change). A gvar
region set to 'caption' allows changes only in regions that peak below the
default optical size.

Since r12 a master may take several added layers (`added_layers` maps it to
a set of layer names), a layer of that set which the reference already has is
compared glyph by glyph like a master (`layers` lists the glyphs that may
change in it; none by default), and a layer the reference has but the
candidate lacks is a problem unless listed in `removed_layers`.

Usage (repository root):
    .venv/bin/python -I candidates/r12-type/checks/drift.py [CAND] [--ref r6-type] [--json PATH] [--list PATH]

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
# r9 item 3: the Rounded glyphs whose outer corners are not stroke ends, so
# the larger pen reaches them (every other corner in Rounded is a stroke end,
# already a full semicircle in r6).
ROUNDED = ('B', 'E', 'F', 'G', 'K', 'L', 'P', 'R', 'bracketleft', 'bracketleft.case', 'bracketright',
           'bracketright.case', 'degreefarenheit', 'e', 'five', 'five.pnum', 'g', 'k', 'onequarter',
           'seven', 'seven.pnum', 'three', 'three.pnum', 'threequarters')
RMASTERS = ('m00', 'm01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08')
# r10 item 1: the mono's ℃/℉ are redrawn again (TEMP) and two contextual
# follower forms are appended (calt after a unit: the en dash and slash
# start later in their cells). Appended glyphs extend the glyph order at its
# end only; post and maxp may change by exactly those names (checked).
UNIT_FOLLOW = ('endash.unit', 'slash.unit')
# r10 item 2: the Rounded glyphs whose concave turns, corner notches or
# text/caption bowls changed (display turns back to a 0.85-stem fillet with
# an outer corner concentric to it, the flat-top 3's notch capped to keep
# both lines, and the hero bowls a share of the way to circular in the text
# and caption masters). Item 3 changes no glyph (one 3 already), item 4 is
# skipped (the serif question mark is a component of four other glyphs).
ROUNDED_R10 = ('B', 'E', 'F', 'G', 'L', 'P', 'R', 'bracketleft', 'bracketleft.case', 'bracketright',
               'bracketright.case', 'colon', 'colon.case', 'colon.fig', 'degree', 'degreefarenheit', 'eight',
               'eight.pnum', 'five', 'five.pnum', 'nine', 'nine.pnum', 'percent', 'period', 'six', 'six.pnum',
               'three', 'three.pnum', 'two', 'two.pnum', 'zero', 'zero.pnum', 'zero.pnum.slash', 'zero.slash')
ROUNDED_ALL = tuple(sorted(set(ROUNDED) | set(ROUNDED_R10)))
# r11 item 1: the mono's ℃/℉ decompose in ccmp to the typed degree +
# letter pair (GSUB), and the standalone signs are redrawn to fit the cell
# (TEMP again). The r10 followers are retired: once ccmp decomposes the sign
# no calt context can reach them, so the r11 fonts no longer have them
# (against r6 nothing changes there; against r10 they are the only glyphs
# removed, at the end of the glyph order).
# r11 item 2: the serif's 9-10 px spacing opens in the caption masters
# (m00-m02, already free; right sidebearings only) and fades out by 13 px
# through three glyph-only layers at that optical size (layer fade.13 of
# m00-m02, the exact r10 interpolation of the glyphs there), so the built
# serif gains caption-side gvar regions peaking between opsz 8 and the text
# masters and its HVAR store is re-modelled; GPOS keeps interpolating
# between the masters' own features. No advance changes at the default
# instance.
# r11 item 3: the serif question mark's hook is redrawn in every master; the
# inverted and double marks are components of it, so they follow.
# r11 item 4: no glyph changes (r10's hyphens already clear their
# neighbours by 2 px; measured in the browser).
# r12: the serif caption spacing fades out in steps instead of one ramp to
# 13 px: the caption masters' opening changes (m00-m02, already free) and
# each caption master takes one more glyph-only layer below 13 px (FADE_LAYERS;
# the exact interpolation of its glyphs there plus that step's opening).
# fade.13 is kept as r11 made it, so against r11 it must not change. The
# built serif's new regions all peak below the default optical size
# ('caption') and its HVAR store is re-modelled (already allowed); nothing
# else in any face moves.
QUESTION = ('question', 'questiondown.cap', 'questiondown', 'questiondbl', 'questionexclam', 'exclamquestion')
FADE_ON = ('m00', 'm01', 'm02')
FADE_LAYERS = ('fade.12', 'fade.13')
SMASTERS = ('m00', 'm01', 'm02', 'm03', 'm04', 'm05', 'm06', 'm07', 'm08')
MONO_ALL = TEMP + UNIT_FOLLOW

# The serif's small optical size (opsz 8, masters m00-m02) takes r7's
# caption weight (r8), so any glyph there may change; the mono's
# degree-letter signs are redrawn in both masters (r8 and r9 item 1); the
# Rounded glyphs above take r9's larger pen in every master (item 3, any
# region: the default instance is the Regular text master). Nothing else
# moves. In the built serif, only gvar regions that peak at opsz 8 may change
# (the default instance and the text and display regions keep r6's
# numbers). In the built mono, GSUB changes (r9 item 4: the operator
# ligatures move from calt to dlig and ss11) and the name table gains the
# ss11 feature name; no other table changes.
INTENDED = {
    'added_layers': {'serif': {m: set(FADE_LAYERS) for m in FADE_ON}},
    'sources': {
        'serif': {**{m: set(QUESTION) for m in SMASTERS}, 'm00': None, 'm01': None, 'm02': None},
        'mono': {'m00': set(MONO_ALL), 'm01': set(MONO_ALL)},
        'sans-rounded': {m: set(ROUNDED_ALL) for m in RMASTERS},
    },
    'binaries': {
        'StrataSerif': {'glyf': set(QUESTION), 'hmtx': set(QUESTION), 'gvar_regions': 'caption', 'gvar': set(QUESTION),
                        'tables': {'HVAR', 'GPOS', 'GDEF', 'MVAR'}, 'advance': set()},
        'StrataMono': {'glyf': set(TEMP), 'hmtx': set(TEMP), 'gvar_regions': 'any', 'gvar': set(TEMP),
                       'tables': {'GSUB', 'name'}, 'appended': UNIT_FOLLOW, 'advance': set()},
        'StrataSansRounded': {'glyf': set(ROUNDED_ALL), 'hmtx': set(ROUNDED_ALL), 'gvar_regions': 'any',
                              'gvar': set(ROUNDED_ALL)},
    },
}
NUM = {'x', 'y', 'xScale', 'xyScale', 'yxScale', 'yScale', 'xOffset', 'yOffset', 'width', 'height'}
WHOLE = ('cmap', 'GSUB', 'GPOS', 'GDEF', 'fvar', 'avar', 'STAT', 'HVAR', 'MVAR', 'name', 'OS/2', 'hhea', 'post', 'maxp')


def _node(el):
    attrs = tuple(sorted((k, float(v) if k in NUM else v) for k, v in el.attrib.items()))
    return (el.tag, attrs, tuple(_node(c) for c in el))


def _records(ufo, sub='glyphs'):
    out = {}
    for path in sorted((ufo / sub).glob('*.glif')):
        root = ET.parse(path).getroot()
        outline = root.find('outline')
        out[root.get('name')] = (_node(outline) if outline is not None else None,
                                 tuple(_node(el) for el in root if el.tag in {'advance', 'unicode', 'anchor'}))
    return out


def _layers(ufo):
    """{layer name: directory} from layercontents.plist."""
    import plistlib
    p = ufo / 'layercontents.plist'
    return {n: d for n, d in plistlib.loads(p.read_bytes())} if p.exists() else {'public.default': 'glyphs'}


def sources(cand, ref):
    report, bad = {}, []
    for face, prefix in FACES.items():
        a_dir, b_dir = ROOT / 'candidates' / ref / 'fonts' / face, ROOT / 'candidates' / cand / 'fonts' / face
        masters = sorted(p.name[len(prefix) + 1:-4] for p in a_dir.glob(f'{prefix}-m*.ufo'))
        b_masters = sorted(p.name[len(prefix) + 1:-4] for p in b_dir.glob(f'{prefix}-m*.ufo'))
        added_ok = set(INTENDED.get('added_masters', {}).get(face, ()))
        added = [m for m in b_masters if m not in masters]
        if [m for m in masters if m not in b_masters] or [m for m in added if m not in added_ok]:
            bad.append(f'{face}: master set differs')
        face_rep = {}
        layers_ok = {m: {v} if isinstance(v, str) else set(v) for m, v in INTENDED.get('added_layers', {}).get(face, {}).items()}
        layer_changes_ok = INTENDED.get('layers', {}).get(face, {})
        removed_ok = INTENDED.get('removed_layers', {}).get(face, {})
        skip = set()
        for m in [m for m in masters if m in b_masters]:
            la, lb = _layers(a_dir / f'{prefix}-{m}.ufo'), _layers(b_dir / f'{prefix}-{m}.ufo')
            for name in la:
                if name not in lb and name not in removed_ok.get(m, ()):
                    bad.append(f'{face} {m}: layer {name} removed')
            for name, sub in lb.items():
                if name in la:
                    if name in layers_ok.get(m, ()):
                        # an intended layer the reference already has: compare it like a master
                        skip.add(f'{prefix}-{m}.ufo/{sub}')
                        a = _records(a_dir / f'{prefix}-{m}.ufo', la[name])
                        b = _records(b_dir / f'{prefix}-{m}.ufo', sub)
                        changed = sorted(n for n in a.keys() | b.keys() if a.get(n) != b.get(n))
                        ok_names = layer_changes_ok.get((m, name), set())
                        outside = [n for n in changed if not (ok_names is None or n in ok_names)]
                        face_rep[f'{m}/{name}'] = {'glyphs': len(b), 'changed': len(changed), 'outside_intended': outside,
                                                   'unchanged': len(b) - len(changed),
                                                   'changed_names': changed if len(changed) <= 40 else changed[:40] + ['...'],
                                                   'changed_all': changed}
                        if outside:
                            bad.append(f'{face} {m} layer {name}: {len(outside)} unintended ({", ".join(outside[:12])})')
                    continue
                skip.add(f'{prefix}-{m}.ufo/{sub}')
                if name not in layers_ok.get(m, ()):
                    bad.append(f'{face} {m}: unintended layer {name}')
                    continue
                names = {ET.parse(p).getroot().get('name') for p in (b_dir / f'{prefix}-{m}.ufo' / sub).glob('*.glif')}
                same = names == set(_records(b_dir / f'{prefix}-{m}.ufo'))
                face_rep[f'{m}/{name}'] = {'added_layer': True, 'glyphs': len(names), 'same_glyph_set': same}
                if not same:
                    bad.append(f'{face} {m}: layer {name} glyph set differs from the master')
        for m in added:
            if m in added_ok:
                names = set(_records(b_dir / f'{prefix}-{m}.ufo'))
                same = names == set(_records(b_dir / f'{prefix}-{b_masters[0]}.ufo'))
                face_rep[m] = {'added': True, 'glyphs': len(names), 'same_glyph_set': same}
                if not same:
                    bad.append(f'{face} {m}: added master glyph set differs')
        for m in [m for m in masters if m in b_masters]:
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
            if p.is_dir() or rel.parts[1:2] == ('glyphs',) or p.name == '.DS_Store' or '/'.join(rel.parts[:2]) in skip:
                continue
            q = b_dir / rel
            if not q.exists() or q.read_bytes() != p.read_bytes():
                other.append(str(rel))
        for p in sorted(b_dir.rglob('*')):
            rel = p.relative_to(b_dir)
            if p.is_dir() or p.name == '.DS_Store' or (a_dir / rel).exists():
                continue
            if '/'.join(rel.parts[:2]) in skip or rel.parts[1:2] == ('glyphs',):
                continue
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
            want = INTENDED['binaries'].get(prefix, {'glyf': set(), 'hmtx': set(), 'gvar_regions': 'none'})
            appended = tuple(want.get('appended', ()))
            oa, ob = a.getGlyphOrder(), b.getGlyphOrder()
            # names in `appended` may be added at the end (r10) or retired from it (r11 against r10)
            core_a, core_b = [n for n in oa if n not in appended], [n for n in ob if n not in appended]
            only_appended = bool(appended) and oa != ob and core_a == core_b and oa[:len(core_a)] == core_a and ob[:len(core_b)] == core_b
            if oa != ob and not only_appended:
                bad.append(f'{prefix}.{ext}: glyph order differs')
            appended_ok = set()
            if only_appended:
                # post and maxp may differ by exactly the appended names
                pa_, pb_ = a['post'], b['post']
                post_ok = (pb_.formatType == pa_.formatType and pa_.formatType == 2.0
                           and all(getattr(pa_, k) == getattr(pb_, k) for k in ('italicAngle', 'underlinePosition',
                                                                              'underlineThickness', 'isFixedPitch')))
                ma, mb = a['maxp'], b['maxp']
                maxp_ok = mb.numGlyphs - ma.numGlyphs == len(ob) - len(oa) and all(
                    getattr(ma, k, None) == getattr(mb, k, None) for k in ('maxPoints', 'maxContours', 'maxCompositePoints',
                                                                          'maxCompositeContours', 'maxComponentElements',
                                                                          'maxComponentDepth', 'maxZones'))
                if post_ok:
                    appended_ok.add('post')
                if maxp_ok:
                    appended_ok.add('maxp')
                rep_appended = {'appended': [n for n in ob if n not in oa], 'retired': [n for n in oa if n not in ob],
                                'post_only_names': post_ok, 'maxp_only_count': maxp_ok}
            else:
                rep_appended = {}
            names = [n for n in b.getGlyphOrder() if n in set(a.getGlyphOrder())]
            glyf = sorted(n for n in names if _glyf_record(a, n) != _glyf_record(b, n))
            hmtx = sorted(n for n in names if a['hmtx'][n] != b['hmtx'][n])
            advance = sorted(n for n in names if a['hmtx'][n][0] != b['hmtx'][n][0])
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
            out_glyf = [n for n in glyf if n not in want['glyf']]
            out_hmtx = [n for n in hmtx if n not in want['hmtx']]
            mode = want.get('gvar_regions', 'none')
            out_gvar = []
            for lab, ns in regions.items():
                peaks = dict(p.split('=') for p in lab.split(',')) if lab else {}
                caption = float(peaks.get('opsz', '0')) < 0
                for n in ns:
                    if not (n in want.get('gvar', set()) or (mode == 'caption' and caption)):
                        out_gvar.append((n, lab))
            out_whole = [t for t in whole if t not in want.get('tables', set()) and t not in appended_ok]
            out_adv = [n for n in advance if 'advance' in want and n not in want['advance']]
            rep = {'glyphs': len(names), 'glyf_changed': glyf, 'hmtx_changed': hmtx,
                   'gvar_changed_glyphs': len(gvar),
                   'gvar_regions_changed': {lab: len(ns) for lab, ns in sorted(regions.items())},
                   'gvar_region_glyphs': {lab: sorted(ns) for lab, ns in sorted(regions.items())},
                   'advance_changed': advance, 'tables_changed': whole, **rep_appended,
                   'outside_intended': {'glyf': out_glyf, 'hmtx': out_hmtx, 'advance': out_adv, 'gvar': sorted(out_gvar)[:40],
                                        'gvar_count': len(out_gvar), 'tables': out_whole}}
            for kind, lst in (('glyf', out_glyf), ('hmtx', out_hmtx), ('advance', out_adv), ('gvar', out_gvar), ('tables', out_whole)):
                if lst:
                    bad.append(f'{prefix}.{ext} {kind}: {len(lst)} unintended ({", ".join(map(str, sorted(lst)[:8]))})')
            report[f'{prefix}.{ext}'] = rep
    return report, bad


def main(argv):
    cand, ref, out = 'r12-type', 'r6-type', None
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
                if r.get('added'):
                    lines.append(f'{face} {m} sources: added master, {r["glyphs"]} glyphs (all new)')
                    continue
                if r.get('added_layer'):
                    lines.append(f'{face} {m} sources: added layer, {r["glyphs"]} glyphs (all new, same glyph set as the master: {r["same_glyph_set"]})')
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
            lines.append(f'{font} advances changed: {len(r["advance_changed"])}' + (': ' + ' '.join(r['advance_changed']) if r['advance_changed'] else ''))
            if r.get('appended') or r.get('retired'):
                lines.append(f'{font} glyph order: appended {r.get("appended", [])}, retired {r.get("retired", [])}')
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
            if r.get('added'):
                print(f'  {face} {m}: added master ({r["glyphs"]} glyphs, same glyph set: {r["same_glyph_set"]})')
                continue
            if r.get('added_layer'):
                print(f'  {face} {m}: added layer ({r["glyphs"]} glyphs, same glyph set as the master: {r["same_glyph_set"]})')
                continue
            if r['changed']:
                print(f'  {face} {m}: {r["changed"]}/{r["glyphs"]} glyphs differ'
                      + (f' ({", ".join(r["changed_names"])})' if r['changed'] <= 12 else '')
                      + (f'; outside intended: {r["outside_intended"][:12]}' if r['outside_intended'] else ''))
            else:
                print(f'  {face} {m}: identical ({r["glyphs"]} glyphs)')
    for font, r in binr.items():
        print(f'  {font}: glyf {len(r["glyf_changed"])} {r["glyf_changed"][:8]}, hmtx {len(r["hmtx_changed"])} {r["hmtx_changed"][:8]}, '
              f'advances {len(r["advance_changed"])}, gvar glyphs {r["gvar_changed_glyphs"]}, regions {r["gvar_regions_changed"]}, tables {r["tables_changed"]}'
              + (f', appended {r["appended"]}, retired {r["retired"]}' if r.get('appended') or r.get('retired') else ''))
    for p in result['problems']:
        print('  PROBLEM', p)
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
