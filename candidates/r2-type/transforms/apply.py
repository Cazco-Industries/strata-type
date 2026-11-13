"""Rebuild this candidate's sources from the baseline, deterministically.

Run from the repository root:
    .venv/bin/python -I candidates/r2-type/transforms/apply.py [faces...]

Faces default to: sans rounded serif mono. Each face folder is reset from
candidates/baseline/fonts before its transforms run, so the result depends
only on the baseline bytes and these scripts.
"""
import shutil
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
CAND = HERE.parent
ROOT = CAND.parents[1]
BASE = ROOT / 'candidates' / 'baseline' / 'fonts'
FONTS = CAND / 'fonts'

import ufoLib2  # noqa: E402
import hygiene  # noqa: E402


def load(face, prefix, count):
    return {f'm{i:02d}': ufoLib2.Font.open(FONTS / face / f'{prefix}-m{i:02d}.ufo') for i in range(count)}


def save(face, prefix, masters):
    for m, f in masters.items():
        f.save(FONTS / face / f'{prefix}-{m}.ufo', overwrite=True)


def reset(face):
    shutil.rmtree(FONTS / face, ignore_errors=True)
    shutil.copytree(BASE / face, FONTS / face)


def main(faces):
    if 'sans' in faces:
        import sans
        reset('sans')
        hygiene.sans(FONTS / 'sans')
        ms = load('sans', 'StrataSans', 6)
        sans.run(ms)
        save('sans', 'StrataSans', ms)
        sans.weight_map(FONTS / 'sans')
        print('sans caption stems', sans.caption(FONTS / 'sans'))
        print('sans done', flush=True)
    if 'rounded' in faces:
        import rounded
        rounded.make(FONTS / 'sans')
        print('rounded done', flush=True)
    if 'serif' in faces:
        import serif
        reset('serif')
        hygiene.serif(FONTS / 'serif')
        ms = load('serif', 'StrataSerif', 9)
        serif.run(ms, FONTS / 'serif')
        save('serif', 'StrataSerif', ms)
        print('serif done', flush=True)
    if 'mono' in faces:
        import mono
        reset('mono')
        ms = load('mono', 'StrataMono', 2)
        ms = mono.run(ms, FONTS / 'mono')
        save('mono', 'StrataMono', ms)
        print('mono done', flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('faces',nargs='*')
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    if not set(args.faces)<={'sans','rounded','serif','mono'}:parser.error('Unknown face')
    if args.output_dir:
        FONTS=args.output_dir.resolve()/'fonts'
        FONTS.mkdir(parents=True,exist_ok=True)
    main(args.faces or ['sans', 'rounded', 'serif', 'mono'])
