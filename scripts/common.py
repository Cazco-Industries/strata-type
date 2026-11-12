from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / 'sources/upstream'
FACES = {'sans': 'Strata Sans', 'serif': 'Strata Serif', 'mono': 'Strata Mono'}
FORBIDDEN = re.compile(r'inter|source|fira', re.I)
CORE = (set(range(0x20, 0x7f)) | set(range(0xa0, 0x100)) |
        set(range(0x2000, 0x200b)) | set(range(0x2010, 0x2016)) |
        set(range(0x2018, 0x201f)) | {0x2022, 0x2026, 0x202f, 0x2030, 0x2032, 0x2033, 0x2044} |
        set(range(0x2070, 0x207a)) - {0x2072, 0x2073} |
        {0x2103, 0x2109, 0x2212} | set(range(0x2190, 0x219a)) | set(range(0x2150, 0x215f)))
# Unassigned superscripts are not requested. Latin-1 supplies ¹ ² ³ and ¼ ½ ¾.

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


def rename_binary(font, family):
    names = font['name']
    ps_ids = {instance.postscriptNameID for instance in font['fvar'].instances if instance.postscriptNameID != 65535} if 'fvar' in font else set()
    style = names.getDebugName(17) or names.getDebugName(2) or 'Regular'
    style = FORBIDDEN.sub('', style).strip() or 'Regular'
    ps_style = re.sub(r'[^A-Za-z0-9]', '', style)
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
        elif n.nameID in (3, 6, 25):
            value = family.replace(' ', '') + ('-'+ps_style if n.nameID != 25 else '')
        elif n.nameID == 4:
            value = family + ' ' + style
        elif n.nameID == 13:
            value = 'Licensed under the SIL Open Font License, Version 1.1. See accompanying notices.'
        elif n.nameID == 14:
            value = 'https://openfontlicense.org'
        elif n.nameID == 7:
            value = ''
        if n.nameID in ps_ids:
            value = re.sub(r'[^A-Za-z0-9-]', '', value)
        n.string = value.encode(n.getEncoding(), errors='replace')
    assert not any(FORBIDDEN.search(n.toUnicode()) for n in names.names)


def checkpoint():
    from resource_guard import wait_available
    return wait_available()
