"""Generate the owner's always-current specimen site in site/.

Reads our own builds only (build/r<N>-type plus older entries, and the icon
sets in ~/strata-ml/type-climb-work), copies the WOFF2 and SVG files into
site/ subfolders and writes everything the page needs into site/data.js, so
site/index.html opens straight from disk with no server and no network.

Stdlib + fontTools only. Run with the isolated interpreter:

    .venv/bin/python -I scripts/site.py              # regenerate if sources changed
    .venv/bin/python -I scripts/site.py --force      # regenerate regardless
    .venv/bin/python -I scripts/site.py --scheduled  # LaunchAgent mode (guarded)
    .venv/bin/python -I scripts/site.py agent-install | agent-uninstall | agent-status

Sources are opened read-only. Change detection hashes the content of every
font and SVG (a touched-but-identical file does not rebuild; an edit in place
does). A build or icon set that is mid-write (a required face missing, ANY
file or the directory itself touched in the last SETTLE seconds, or a file
that will not parse) keeps its previous generated copy until it has been quiet
for SETTLE seconds. In --scheduled mode a run that starts inside a quiet UTC
window waits for the window to end instead of skipping the whole interval.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import html
import io
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import signal
import struct
import subprocess
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / 'scripts' / 'site_page.html'
DEFAULT_TYPE_ROOT = REPO / 'build'
DEFAULT_ICON_ROOT = Path.home() / 'strata-ml' / 'type-climb-work'
DEFAULT_OUT = REPO / 'site'
LABEL = 'com.strata-type.site'
PLIST = Path.home() / 'Library' / 'LaunchAgents' / f'{LABEL}.plist'
LOG = Path.home() / 'Library' / 'Logs' / 'strata-type-site.log'
HEAVY_PAUSE = Path.home() / 'strata-ml' / 'ops' / 'HEAVY_PAUSE'
FLOOR = 14 * 1024**3
SETTLE = 180            # seconds a whole build / icon set must be untouched before we copy it
ACTIVE_BUILD = 30 * 60  # a build touched this recently may still be gaining faces
INTERVAL = 600
STATE_VERSION = 4

# (key, file, display name, required)
FACES = [
    ('sans', 'StrataSans.woff2', 'Strata Sans', True),
    ('rounded', 'StrataSansRounded.woff2', 'Strata Sans Rounded', False),
    ('serif', 'StrataSerif.woff2', 'Strata Serif', True),
    ('mono', 'StrataMono.woff2', 'Strata Mono', True),
]
OLDER_TYPE = ['lumen-146', 'quartz-571', 'baseline']
OLDER_ICONS = ['quartz-571', 'lumen-146']
SVG_NS = 'http://www.w3.org/2000/svg'
SVG_ELEMENTS = {
    'svg', 'g', 'path', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'rect',
    'defs', 'clipPath', 'mask', 'use', 'title', 'desc', 'linearGradient',
    'radialGradient', 'stop', 'symbol',
}
DROP_ROOT_ATTRS = {'width', 'height', 'class', 'id', 'style'}


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def log(msg: str) -> None:
    print(f"{utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')} {msg}", flush=True)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_sig(paths: list[Path], base: Path) -> str:
    """Hash names and bytes, so an in-place edit is noticed whatever its mtime or size."""
    parts = []
    for p in sorted(paths):
        parts.append(f'{p.relative_to(base)}|{sha(p.read_bytes())}')
    return sha('\n'.join(parts).encode())


def newest_touch(directory: Path, subdirs: tuple[str, ...] = ()) -> tuple[float, str]:
    """Newest mtime of the directory itself and everything directly inside it.

    Descends into the named subdirectories one level. This is the build's heartbeat:
    a builder rewriting any file (fonts, build.json, gate output) or replacing one
    atomically (which bumps the directory mtime) keeps the build "active".
    """
    best, who = directory.stat().st_mtime, '.'
    for p in directory.iterdir():
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if m > best:
            best, who = m, p.name
        if p.is_dir() and p.name in subdirs:
            for q in p.iterdir():
                try:
                    mq = q.stat().st_mtime
                except OSError:
                    continue
                if mq > best:
                    best, who = mq, f'{p.name}/{q.name}'
    return best, who


# ---------------------------------------------------------------- guard

def quiet_wait() -> float:
    """Seconds until the current quiet UTC window (:00-:05, :15-:20, ...) ends; 0 outside one."""
    now = utcnow()
    if now.minute % 15 > 5:
        return 0.0
    end = now.replace(minute=now.minute - now.minute % 15 + 6, second=2, microsecond=0)
    return max(0.0, (end - now).total_seconds())


def guard_reason() -> str | None:
    now = utcnow()
    if now.minute % 15 <= 5:
        return f'quiet window (:{now.minute:02d} UTC)'
    free = shutil.disk_usage('/').free
    if free < FLOOR:
        return f'/ has {free / 1024**3:.1f} GiB free (floor 14 GiB)'
    if HEAVY_PAUSE.exists():
        return 'shared HEAVY_PAUSE flag'
    return None


# ---------------------------------------------------------------- discovery

def numbered(root: Path, pattern: str) -> list[Path]:
    found = []
    if root.is_dir():
        for p in root.iterdir():
            m = re.fullmatch(pattern, p.name)
            if m and p.is_dir():
                found.append((int(m.group(1)), p))
    return [p for _, p in sorted(found, key=lambda t: -t[0])]


def type_dirs(root: Path) -> list[Path]:
    return numbered(root, r'r(\d+)-type') + [root / n for n in OLDER_TYPE if (root / n).is_dir()]


def icon_dirs(root: Path) -> list[Path]:
    dirs = [p for p in numbered(root, r'r(\d+)-icons') if (p / 'icons').is_dir()]
    return dirs + [root / n for n in OLDER_ICONS if (root / n / 'icons').is_dir()]


def scan_type(path: Path, now: float) -> dict | None:
    files = {k: path / fn for k, fn, _, _ in FACES if (path / fn).is_file()}
    if not files:
        return None
    stats = {k: f.stat() for k, f in files.items()}
    newest = max(s.st_mtime for s in stats.values())
    problems, recent = [], False
    missing = [name for k, _, name, req in FACES if req and k not in files]
    if missing:
        problems.append('missing ' + ', '.join(missing))
    touched, who = newest_touch(path)
    if now - touched < SETTLE:
        problems.append(f'build directory touched {int(now - touched)} s ago ({who}); waiting for {SETTLE} s of quiet')
        recent = True
    return {
        'id': path.name, 'path': path, 'files': files, 'sig': content_sig(list(files.values()), path),
        'newest': newest, 'problems': problems, 'recent': recent,
    }


def scan_icons(path: Path, now: float) -> dict | None:
    d = path / 'icons'
    svgs = sorted(d.glob('*.svg'))
    if not svgs:
        return None
    layer_file = path / 'icon-layers.json'
    inputs = svgs + ([layer_file] if layer_file.is_file() else [])
    touched, who = newest_touch(path, ('icons',))
    problems, recent = [], False
    if now - touched < SETTLE:
        problems.append(f'icon set touched {int(now - touched)} s ago ({who}); waiting for {SETTLE} s of quiet')
        recent = True
    return {
        'id': path.name, 'path': path, 'svgs': svgs, 'layer_file': layer_file if layer_file.is_file() else None,
        'sig': content_sig(inputs, path), 'newest': max(p.stat().st_mtime for p in svgs),
        'problems': problems, 'recent': recent,
    }


FACES_BY_KEY = {k: (k, fn, name, req) for k, fn, name, req in FACES}


# ---------------------------------------------------------------- fonts

def single_subs(gsub, tag: str) -> dict:
    idxs = set()
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag == tag:
            idxs.update(fr.Feature.LookupListIndex)
    mapping = {}
    for i in sorted(idxs):
        lk = gsub.LookupList.Lookup[i]
        for st in lk.SubTable:
            kind = lk.LookupType
            if kind == 7:
                kind, st = st.ExtensionLookupType, st.ExtSubTable
            if kind == 1:
                for k, v in st.mapping.items():
                    mapping.setdefault(k, v)
    return mapping


def feature_list(font: TTFont, table: str) -> list[dict]:
    if table not in font:
        return []
    out, seen = [], {}
    name = font['name']
    for fr in font[table].table.FeatureList.FeatureRecord:
        tag = fr.FeatureTag
        label = None
        params = getattr(fr.Feature, 'FeatureParams', None)
        if params is not None:
            nid = getattr(params, 'UINameID', None) or getattr(params, 'FeatUILabelNameID', None)
            if nid:
                label = name.getDebugName(nid)
        if tag in seen:
            if label and not out[seen[tag]].get('label'):
                out[seen[tag]]['label'] = label
            continue
        seen[tag] = len(out)
        out.append({'tag': tag, 'label': label})
    return sorted(out, key=lambda f: f['tag'])


def figure_advances(font: TTFont) -> dict | None:
    cmap = font.getBestCmap()
    digits = [cmap.get(0x30 + i) for i in range(10)]
    if None in digits:
        return None
    hmtx = font['hmtx']
    res = {'glyphs': digits, 'default': [hmtx[g][0] for g in digits]}
    if 'GSUB' in font:
        gsub = font['GSUB'].table
        for tag in ('tnum', 'pnum'):
            m = single_subs(gsub, tag)
            if any(g in m for g in digits):
                res[tag] = [hmtx[m.get(g, g)][0] for g in digits]
                res[tag + 'Glyphs'] = [m.get(g, g) for g in digits]
    return res


def face_meta(data: bytes, rel: str) -> dict:
    font = TTFont(io.BytesIO(data))
    name = font['name']
    cmap = font.getBestCmap() or {}
    axes, instances = [], []
    if 'fvar' in font:
        for a in font['fvar'].axes:
            axes.append({'tag': a.axisTag, 'min': a.minValue, 'default': a.defaultValue,
                         'max': a.maxValue, 'name': name.getDebugName(a.axisNameID) or a.axisTag})
        for inst in font['fvar'].instances:
            instances.append({'name': name.getDebugName(inst.subfamilyNameID) or '',
                              'coords': {k: round(v, 2) for k, v in inst.coordinates.items()}})
    os2 = font['OS/2']
    weight = None
    if not any(a['tag'] == 'wght' for a in axes):
        weight = os2.usWeightClass
    return {
        'file': rel,
        'bytes': len(data),
        'family': name.getBestFamilyName(),
        'style': name.getBestSubFamilyName(),
        'fullName': name.getBestFullName(),
        'version': name.getDebugName(5),
        'upm': font['head'].unitsPerEm,
        'glyphCount': len(font.getGlyphOrder()),
        'axes': axes,
        'instances': instances,
        'staticWeight': weight,
        'gsub': feature_list(font, 'GSUB'),
        'gpos': [f['tag'] for f in feature_list(font, 'GPOS')],
        'cmap': [[cp, g] for cp, g in sorted(cmap.items())],
        'figures': figure_advances(font),
        'metrics': {
            'xHeight': getattr(os2, 'sxHeight', None), 'capHeight': getattr(os2, 'sCapHeight', None),
            'ascender': os2.sTypoAscender, 'descender': os2.sTypoDescender,
        },
    }


def read_stable(path: Path) -> bytes:
    """Read a source file and fail if it changed while we read it."""
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size) or len(data) != after.st_size:
        raise OSError(f'{path.name} changed while reading')
    return data


def build_type_entry(scan: dict, out: Path) -> dict:
    """Parse and copy one type build into a fresh fonts/<id>.new directory."""
    tmp = out / 'fonts' / f".{scan['id']}.new"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    faces = {}
    for key, path in scan['files'].items():
        data = read_stable(path)
        stem = path.stem
        fname = f'{stem}.{sha(data)[:10]}.woff2'
        meta = face_meta(data, f"fonts/{scan['id']}/{fname}")
        meta['source'] = str(path)
        meta['modified'] = iso(path.stat().st_mtime)
        (tmp / fname).write_bytes(data)
        faces[key] = meta
    return {'faces': faces, 'tmp': tmp}


# ---------------------------------------------------------------- icons

def local(tag: str) -> str:
    return tag.split('}', 1)[-1]


def attr_name(name: str) -> str:
    if name.startswith('{'):
        ns, n = name[1:].split('}', 1)
        return ('xlink:' if 'xlink' in ns else '') + n
    return name


def clean_svg(el: ET.Element, root: bool = False) -> str | None:
    tag = local(el.tag)
    if tag not in SVG_ELEMENTS:
        return None
    attrs = []
    for k, v in el.attrib.items():
        n = attr_name(k)
        low = n.lower()
        if low.startswith('on') or (root and low in DROP_ROOT_ATTRS):
            continue
        if low in ('href', 'xlink:href') and not v.startswith('#'):
            continue
        if low == 'style' and re.search(r'url\(|expression|javascript', v, re.I):
            continue
        if low.startswith('xmlns'):
            continue
        attrs.append(f'{n}="{html.escape(v, quote=True)}"')
    if root:
        attrs.insert(0, f'xmlns="{SVG_NS}"')
        attrs += ['aria-hidden="true"', 'focusable="false"']
    kids = ''.join(filter(None, (clean_svg(c) for c in el)))
    text = html.escape(el.text.strip()) if tag in ('title', 'desc') and el.text else ''
    return f"<{tag}{(' ' + ' '.join(attrs)) if attrs else ''}>{text}{kids}</{tag}>"


def apply_layer_map(root: ET.Element, layers: list[str]) -> str:
    """Return 'svg' if the file marks its own layers, 'map' if we applied icon-layers.json."""
    if any('data-layer' in e.attrib for e in root.iter()):
        return 'svg'
    if not layers:
        return 'none'
    kids = [c for c in root if local(c.tag) not in ('title', 'desc', 'defs')]
    groups = [c for c in kids if local(c.tag) == 'g']
    target = groups if len(groups) == len(layers) else (kids if len(kids) == len(layers) else None)
    if target is None:
        return 'mismatch'
    for el, layer in zip(target, layers):
        el.set('data-layer', layer)
    return 'map'


def build_icon_entry(scan: dict, out: Path) -> dict:
    tmp = out / 'icons' / f".{scan['id']}.new"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    layer_map = {}
    if scan['layer_file']:
        raw = json.loads(read_stable(scan['layer_file']))
        layer_map = {k.removesuffix('.svg'): v for k, v in raw.items() if isinstance(v, list)}
    icons = []
    for svg in scan['svgs']:
        data = read_stable(svg)
        root = ET.fromstring(data)
        if local(root.tag) != 'svg':
            raise ValueError(f'{svg.name} is not an SVG')
        name = svg.stem
        source = apply_layer_map(root, layer_map.get(name, []))
        markup = clean_svg(root, root=True)
        layers = sorted({e.get('data-layer') for e in root.iter() if e.get('data-layer')})
        (tmp / svg.name).write_text(markup + '\n', encoding='utf-8')
        icons.append({
            'name': name, 'svg': markup, 'layers': layers, 'layerSource': source,
            'strokeWidth': root.get('stroke-width'), 'viewBox': root.get('viewBox'),
            'modified': iso(svg.stat().st_mtime),
        })
    return {'icons': icons, 'tmp': tmp}


# ---------------------------------------------------------------- tofu

def build_tofu(path: Path) -> None:
    """A tiny utility font that draws a box for every code point.

    It sits last in each specimen font stack, so a character missing from one
    of our builds shows as a box instead of silently borrowing a system font.
    """
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib.tables.DefaultTable import DefaultTable
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'tofu'])
    empty = TTGlyphPen(None).glyph()
    pen = TTGlyphPen(None)
    for x0, y0, x1, y1, cw in ((80, 0, 520, 700, True), (150, 70, 450, 630, False)):
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        if not cw:
            pts.reverse()
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    fb.setupGlyf({'.notdef': empty, 'tofu': pen.glyph()})
    fb.setupCharacterMap({0x25A1: 'tofu'})
    fb.setupHorizontalMetrics({'.notdef': (600, 0), 'tofu': (600, 80)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({'familyName': 'Strata Site Tofu', 'styleName': 'Regular'})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200,
                usWeightClass=400)
    fb.setupPost()
    font = fb.font
    st4 = CmapSubtable.newSubtable(4)
    st4.platformID, st4.platEncID, st4.language = 3, 1, 0
    st4.cmap = {0x25A1: 'tofu'}
    data4 = st4.compile(font)
    groups = [(0x0000, 0xD7FF, 1), (0xE000, 0x10FFFF, 1)]
    data13 = struct.pack('>HHLLL', 13, 0, 16 + 12 * len(groups), 0, len(groups))
    data13 += b''.join(struct.pack('>LLL', *g) for g in groups)
    header = struct.pack('>HH', 0, 2)
    off4 = 4 + 8 * 2
    off13 = off4 + len(data4)
    header += struct.pack('>HHL', 3, 1, off4) + struct.pack('>HHL', 3, 10, off13)
    raw = DefaultTable('cmap')
    raw.data = header + data4 + data13
    font['cmap'] = raw
    buf = io.BytesIO()
    font.save(buf)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buf.getvalue())


# ---------------------------------------------------------------- generate

def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(f'.{path.name}.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)


def swap_dir(tmp: Path, final: Path) -> None:
    old = final.with_name(f'.{final.name}.old')
    shutil.rmtree(old, ignore_errors=True)
    if final.exists():
        os.replace(final, old)
    os.replace(tmp, final)
    shutil.rmtree(old, ignore_errors=True)


def load_state(out: Path) -> dict:
    try:
        state = json.loads((out / '.state.json').read_text())
        if state.get('version') == STATE_VERSION:
            return state
    except (OSError, ValueError):
        pass
    return {'version': STATE_VERSION, 'fingerprint': None, 'type': {}, 'icons': {}}


def resolve(kind: str, scans: list[dict], state: dict, out: Path, builder, built: list, rebuild: bool) -> tuple[list, list]:
    """Decide per entry: reuse, rebuild, keep previous copy, or list as pending."""
    entries, pending = [], []
    now = time.time()
    for scan in scans:
        prev = state[kind].get(scan['id'])
        prev_ok = prev is not None and (out / prev['dir']).is_dir()
        problems = list(scan['problems'])
        if kind == 'type' and prev_ok and not problems:
            lost = [FACES_BY_KEY[k][2] for k in prev['faces'] if k not in scan['files']]
            if lost and now - scan['newest'] < ACTIVE_BUILD:
                problems.append('face no longer present: ' + ', '.join(lost))
        if not problems:
            if prev_ok and prev['sig'] == scan['sig'] and not rebuild:
                entries.append(dict(prev, stale=None))
                continue
            try:
                result = builder(scan, out)
            except Exception as exc:  # unreadable or changing source: keep the old copy
                problems.append(f'unreadable: {exc}')
            else:
                entry = {
                    'id': scan['id'], 'sig': scan['sig'], 'dir': f"{'fonts' if kind == 'type' else 'icons'}/{scan['id']}",
                    'builtAt': iso(scan['newest']), 'stale': None,
                }
                if kind == 'type':
                    entry['faces'] = result['faces']
                else:
                    entry['icons'] = result['icons']
                built.append((result['tmp'], out / entry['dir']))
                entries.append(entry)
                continue
        if prev_ok:
            entries.append(dict(prev, stale='; '.join(problems)))
        else:
            pending.append({'kind': kind, 'id': scan['id'], 'reason': '; '.join(problems)})
    return entries, pending


def unicode_names(type_entries: list[dict]) -> dict:
    names = {}
    for e in type_entries:
        for face in e['faces'].values():
            for cp, _ in face['cmap']:
                if cp not in names:
                    names[cp] = unicodedata.name(chr(cp), '') or f'<{unicodedata.category(chr(cp))}>'
    return {str(k): v for k, v in sorted(names.items())}


def generate(type_root: Path, icon_root: Path, out: Path, force: bool) -> str:
    started = time.monotonic()
    now = time.time()
    out.mkdir(parents=True, exist_ok=True)
    state = load_state(out)
    type_scans = [s for s in (scan_type(p, now) for p in type_dirs(type_root)) if s]
    icon_scans = [s for s in (scan_icons(p, now) for p in icon_dirs(icon_root)) if s]
    code_sig = sha(TEMPLATE.read_bytes() + Path(__file__).read_bytes())
    fingerprint = sha(json.dumps({
        'v': STATE_VERSION, 'code': code_sig,
        'type': [(s['id'], s['sig']) for s in type_scans],
        'icons': [(s['id'], s['sig']) for s in icon_scans],
    }).encode())
    outputs_exist = all((out / n).is_file() for n in ('index.html', 'data.js', 'stamp.js', 'fonts/_tofu/StrataTofu.ttf'))
    if not force and outputs_exist and state.get('fingerprint') == fingerprint:
        return 'unchanged'

    # New generator code re-reads every font and icon; otherwise unchanged entries are reused.
    rebuild = force or state.get('code') != code_sig
    built: list = []
    type_entries, type_pending = resolve('type', type_scans, state, out, build_type_entry, built, rebuild)
    icon_entries, icon_pending = resolve('icons', icon_scans, state, out, build_icon_entry, built, rebuild)
    for tmp, final in built:
        swap_dir(tmp, final)

    tofu = out / 'fonts' / '_tofu' / 'StrataTofu.ttf'
    if not tofu.is_file() or force:
        build_tofu(tofu)

    # Keep only what the current entries need.
    keep = {'fonts': {e['id'] for e in type_entries} | {'_tofu'}, 'icons': {e['id'] for e in icon_entries}}
    for sub, ids in keep.items():
        base = out / sub
        if base.is_dir():
            for child in base.iterdir():
                if child.name not in ids:
                    shutil.rmtree(child, ignore_errors=True) if child.is_dir() else child.unlink()

    generated_at = utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    pending = type_pending + icon_pending
    payload = {
        'generatedAt': generated_at,
        'generator': 'scripts/site.py',
        'intervalSeconds': INTERVAL,
        'type': [{k: v for k, v in e.items() if k not in ('sig', 'dir')} for e in type_entries],
        'icons': [{k: v for k, v in e.items() if k not in ('sig', 'dir')} for e in icon_entries],
        'pending': pending,
        'unicodeNames': unicode_names(type_entries),
        'tofu': 'fonts/_tofu/StrataTofu.ttf',
    }
    atomic_write(out / 'data.js', 'window.STRATA_SITE = ' + json.dumps(payload, ensure_ascii=True, separators=(',', ':')) + ';\n')
    atomic_write(out / 'stamp.js', f'window.__strataStamp && window.__strataStamp({json.dumps(generated_at)});\n')
    atomic_write(out / 'index.html', TEMPLATE.read_text(encoding='utf-8'))

    # A build that is only waiting to settle must be retried on the next run;
    # one that is stuck (missing faces) waits for its files to change.
    any_recent = any(s['recent'] for s in type_scans + icon_scans)
    state = {
        'version': STATE_VERSION,
        'fingerprint': None if any_recent else fingerprint,
        'code': code_sig,
        'generatedAt': generated_at,
        'type': {e['id']: {k: v for k, v in e.items() if k != 'stale'} for e in type_entries},
        'icons': {e['id']: {k: v for k, v in e.items() if k != 'stale'} for e in icon_entries},
    }
    atomic_write(out / '.state.json', json.dumps(state))
    stale = [f"{e['id']} ({e['stale']})" for e in type_entries + icon_entries if e.get('stale')]
    rebuilt = [f'{final.parent.name}/{final.name}' for _, final in built]
    parts = [
        f"generated in {time.monotonic() - started:.1f}s",
        f"type latest {type_entries[0]['id'] if type_entries else 'none'} ({len(type_entries)})",
        f"icons latest {icon_entries[0]['id'] if icon_entries else 'none'} ({len(icon_entries)})",
        'rebuilt ' + (', '.join(rebuilt) if rebuilt else 'none'),
    ]
    if stale:
        parts.append('kept previous copy: ' + '; '.join(stale))
    if pending:
        parts.append('pending: ' + '; '.join(f"{p['id']} ({p['reason']})" for p in pending))
    return ' | '.join(parts)


# ---------------------------------------------------------------- agent

def agent_plist() -> dict:
    return {
        'Label': LABEL,
        'ProgramArguments': [str(REPO / '.venv' / 'bin' / 'python'), '-I', str(REPO / 'scripts' / 'site.py'), '--scheduled'],
        'WorkingDirectory': str(REPO),
        'StartInterval': INTERVAL,
        'RunAtLoad': True,
        'LowPriorityIO': True,
        'Nice': 10,
        'StandardOutPath': str(LOG),
        'StandardErrorPath': str(LOG),
    }


def launchctl(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(['/bin/launchctl', *args], capture_output=True, text=True, check=check)


def agent_install() -> int:
    domain = f'gui/{os.getuid()}'
    PLIST.parent.mkdir(parents=True, exist_ok=True)
    launchctl('bootout', f'{domain}/{LABEL}')
    PLIST.write_bytes(plistlib.dumps(agent_plist()))
    res = launchctl('bootstrap', domain, str(PLIST))
    if res.returncode != 0:
        print(f'launchctl bootstrap failed: {res.stderr.strip()}', file=sys.stderr)
        return 1
    print(f'Installed {PLIST} (every {INTERVAL} s, log {LOG})')
    return 0


def agent_uninstall() -> int:
    launchctl('bootout', f'gui/{os.getuid()}/{LABEL}')
    if PLIST.exists():
        PLIST.unlink()
    print(f'Removed {LABEL}; the site/ folder is left in place')
    return 0


def agent_status() -> int:
    rows = [line for line in launchctl('list').stdout.splitlines() if line.endswith(LABEL)]
    print('loaded: ' + (rows[0] if rows else 'no'))
    print(f'plist: {PLIST} ({"present" if PLIST.exists() else "absent"})')
    if LOG.exists():
        print('last log lines:')
        print(''.join(LOG.read_text(errors='replace').splitlines(keepends=True)[-5:]), end='')
    return 0


# ---------------------------------------------------------------- main

def main() -> int:
    global SETTLE
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('action', nargs='?', default='build',
                    choices=['build', 'agent-install', 'agent-uninstall', 'agent-status'])
    ap.add_argument('--force', action='store_true', help='regenerate even if sources are unchanged')
    ap.add_argument('--scheduled', action='store_true', help='LaunchAgent mode: skip in quiet windows and below the disk floor')
    ap.add_argument('--settle', type=int, default=SETTLE, help='seconds a build must be untouched before it is copied')
    ap.add_argument('--type-root', type=Path, default=DEFAULT_TYPE_ROOT)
    ap.add_argument('--icon-root', type=Path, default=DEFAULT_ICON_ROOT)
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    if args.action == 'agent-install':
        return agent_install()
    if args.action == 'agent-uninstall':
        return agent_uninstall()
    if args.action == 'agent-status':
        return agent_status()

    SETTLE = args.settle
    prefix = 'scheduled: ' if args.scheduled else ''
    if args.scheduled:
        # The interval is fixed (:01, :11, ...), so half the starts land in a quiet window.
        # Sleeping through the window (no CPU) beats skipping a whole interval.
        wait = quiet_wait()
        if wait:
            log(f'{prefix}waiting {wait:.0f} s for the quiet window to end')
            time.sleep(wait)
        signal.alarm(300)  # never let a stuck run block later intervals
        why = guard_reason()
        if why:
            log(f'{prefix}skipped: {why}')
            return 0
    elif shutil.disk_usage('/').free < FLOOR:
        log('refused: / is below the 14 GiB floor')
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / '.lock', 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log(f'{prefix}skipped: another run holds the lock')
            return 0
        try:
            result = generate(args.type_root.resolve(), args.icon_root.resolve(), args.out.resolve(), args.force)
        except Exception as exc:  # report once, readably; the previous site stays in place
            log(f'{prefix}FAILED: {type(exc).__name__}: {exc}')
            return 1
    log(prefix + result)
    if not args.scheduled and result != 'unchanged':
        print(f'Open file://{(args.out / "index.html").resolve()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
