#!/usr/bin/env python3
"""Copy a builder's SVGs and optional UFO/designspace tree into a new candidate."""
import argparse
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT, candidate
from icons import parse_svg,validate


def main():
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--icons',type=Path);p.add_argument('--fonts',type=Path);a=p.parse_args()
    import re
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}',a.id) or a.id=='baseline':raise ValueError('Choose a new candidate id; baseline is preserved')
    dest=ROOT/'candidates'/a.id
    if dest.exists():raise ValueError('Candidate exists; do not overwrite concurrent builder work')
    for source in [a.icons,a.fonts]:
        if source:
            source=source.expanduser().resolve()
            if not source.is_dir() or any(p.is_symlink() for p in source.rglob('*')):raise ValueError('Expected source directory without symlinks')
    if a.icons:
        icons=list(a.icons.expanduser().glob('*.svg'))
        if not icons:raise ValueError('No SVGs in external directory')
        for icon in icons:
            errors=validate(parse_svg(icon))
            if errors:raise ValueError(f'{icon}: {errors}')
    shutil.copytree(ROOT/'candidates/baseline',dest)
    if a.icons:
        shutil.rmtree(dest/'icons');(dest/'icons').mkdir()
        for icon in icons:shutil.copyfile(icon,dest/'icons'/icon.name)
    if a.fonts:
        shutil.rmtree(dest/'fonts');shutil.copytree(a.fonts.expanduser(),dest/'fonts')
    (dest/'provenance.json').unlink(missing_ok=True)
    print(dest)

if __name__=='__main__':main()
