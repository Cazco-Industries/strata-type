from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / 'sources/upstream'
FACES = {'sans': 'Strata Sans', 'serif': 'Strata Serif', 'mono': 'Strata Mono'}
ALL_FACES = {**FACES, 'sans-rounded': 'Strata Sans Rounded'}
ROUNDED_CORE = set(map(ord, ' 0123456789.,:%°−+±-/CF℃℉')) | {0x2007, 0x2008, 0x2009, 0x2044}
FORBIDDEN = re.compile(r'inter|source|fira', re.I)
CORE = (set(range(0x20, 0x7f)) | set(range(0xa0, 0x100)) |
        set(range(0x2000, 0x200b)) | set(range(0x2010, 0x2016)) |
        set(range(0x2018, 0x201f)) | {0x2022, 0x2026, 0x202f, 0x2030, 0x2032, 0x2033, 0x2044} |
        set(range(0x2070, 0x207a)) - {0x2072, 0x2073} |
        {0x2103, 0x2109, 0x2212} | set(range(0x2190, 0x219a)) | set(range(0x2150, 0x215f)))
# Unassigned superscripts are not requested. Latin-1 supplies ¹ ² ³ and ¼ ½ ¾.

def candidate_faces(path):
    faces = dict(FACES)
    if (path / 'fonts/sans-rounded').is_dir():
        faces['sans-rounded'] = ALL_FACES['sans-rounded']
    return faces

def candidate(value):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', value):
        raise ValueError('Candidate id must be lowercase letters, digits, hyphens, underscores')
    p = ROOT / 'candidates' / value
    if not p.is_dir() or p.is_symlink():
        raise ValueError(f'Unknown candidate: {value}')
    return p


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(path):
    p = Path(path)
    h = hashlib.sha256()
    for f in sorted(p.rglob('*')) if p.is_dir() else [p]:
        if f.is_file():
            if f.is_symlink():
                raise ValueError(f'Symlink rejected: {f}')
            h.update(str(f.relative_to(p) if p.is_dir() else f.name).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def release_version():
    path = ROOT / 'VERSION'
    return path.read_text().strip() if path.is_file() else '27.0.0.0'


def opentype_revision(version=None):
    """Map annual YY.minor.patch.build (e.g. 27.0.0.0) to OpenType 16.16 major.mmm."""
    ver = (version or release_version()).split('+')[0]
    parts = [int(p) for p in ver.split('.')]
    major = parts[0]
    minor = parts[1] if len(parts) > 1 else 0
    patch = parts[2] if len(parts) > 2 else 0
    if not (0 <= minor <= 99 and 0 <= patch <= 9):
        raise ValueError(f'Annual version out of OpenType 16.16 range: {ver}')
    rev_str = f'{major}.{minor:02d}{patch}'
    return float(rev_str), rev_str


def ensure_stat(font):
    if 'fvar' not in font:
        return
    names = font['name']
    if 'STAT' in font and font['STAT'].table.AxisValueArray and font['STAT'].table.AxisValueArray.AxisValue:
        # Align Serif STAT optical band naming with fvar ("SmText") to stay <= 31 chars.
        stat_name_ids = {av.ValueNameID for av in font['STAT'].table.AxisValueArray.AxisValue}
        for n in names.names:
            if n.nameID in stat_name_ids and n.toUnicode() == 'SmallText':
                n.string = 'SmText'.encode(n.getEncoding(), errors='replace')
        return
    from fontTools.otlLib.builder import buildStatTable
    weight_labels = {
        100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular',
        500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black',
    }
    inst_coords = [inst.coordinates for inst in font['fvar'].instances]
    stat_axes = []
    for axis in font['fvar'].axes:
        tag = axis.axisTag
        axis_name = names.getDebugName(axis.axisNameID) or tag
        if tag == 'wght':
            vals = sorted({int(round(c['wght'])) for c in inst_coords if 'wght' in c})
            has_bold = 700 in vals
            entries = []
            for v in vals:
                label = weight_labels.get(v, str(v))
                if v == 400:
                    entry = dict(value=400, name=label, flags=0x2)
                    if has_bold:
                        entry['linkedValue'] = 700
                    entries.append(entry)
                else:
                    entries.append(dict(value=v, name=label))
            stat_axes.append(dict(tag='wght', name=axis_name, values=entries))
        elif tag == 'opsz':
            vals = sorted({float(c['opsz']) for c in inst_coords if 'opsz' in c})
            if 32.0 in vals:
                entries = [
                    dict(nominalValue=14, rangeMinValue=axis.minValue, rangeMaxValue=24, name='Text', flags=0x2),
                    dict(nominalValue=32, rangeMinValue=24, rangeMaxValue=axis.maxValue, name='Display'),
                ]
            else:
                entries = [
                    dict(nominalValue=axis.defaultValue, rangeMinValue=axis.minValue, rangeMaxValue=axis.maxValue, name='Text', flags=0x2),
                ]
            stat_axes.append(dict(tag='opsz', name=axis_name, values=entries))
    if stat_axes:
        buildStatTable(font, stat_axes, elidedFallbackName='Regular', macNames=False)


def rename_binary(font, family):
    names = font['name']
    ver = release_version()
    rev_val, rev_str = opentype_revision(ver)
    if 'head' in font:
        font['head'].fontRevision = rev_val
    ps_ids = {instance.postscriptNameID for instance in font['fvar'].instances if instance.postscriptNameID != 65535} if 'fvar' in font else set()
    default_style = None
    if 'fvar' in font:
        dflt = {a.axisTag: a.defaultValue for a in font['fvar'].axes}
        for inst in font['fvar'].instances:
            if dict(inst.coordinates) == dflt:
                default_style = names.getDebugName(inst.subfamilyNameID)
                break
    style = default_style or names.getDebugName(17) or names.getDebugName(2) or 'Regular'
    style = FORBIDDEN.sub('', style).strip() or 'Regular'
    ps_style = re.sub(r'[^A-Za-z0-9]', '', style)
    ps_name = family.replace(' ', '') + '-' + ps_style
    has_id5 = False
    for n in names.names:
        value = n.toUnicode()
        value = re.sub(r'Inter(?: Variable)?', family, value, flags=re.I)
        value = re.sub(r'Source\s*Serif\s*(?:4|Pro)?', family, value, flags=re.I)
        value = re.sub(r'Fira\s*Code', family, value, flags=re.I)
        value = FORBIDDEN.sub('', value)
        if n.nameID == 0:
            value = 'Copyright notices retained verbatim in the accompanying licenses directory.'
        elif n.nameID in (1, 16, 21):
            value = family
        elif n.nameID == 3:
            value = f'{ps_name};{ver}'
        elif n.nameID == 4 or n.nameID == 18:
            value = family + ' ' + style
        elif n.nameID == 5:
            value = f'Version {rev_str};{ver}'
            has_id5 = True
        elif n.nameID == 6:
            value = ps_name
        elif n.nameID == 17:
            value = style
        elif n.nameID == 25:
            value = family.replace(' ', '')
        elif n.nameID == 13:
            value = 'Licensed under the SIL Open Font License, Version 1.1. See accompanying notices.'
        elif n.nameID == 14:
            value = 'https://openfontlicense.org'
        elif n.nameID == 7:
            value = ''
        if n.nameID in ps_ids:
            value = re.sub(r'[^A-Za-z0-9-]', '', value)
        n.string = value.encode(n.getEncoding(), errors='replace')
    if not has_id5:
        names.setName(f'Version {rev_str};{ver}', 5, 3, 1, 0x409)
    ensure_stat(font)
    assert not any(FORBIDDEN.search(n.toUnicode()) for n in names.names)


def checkpoint():
    from resource_guard import wait_available
    return wait_available()
